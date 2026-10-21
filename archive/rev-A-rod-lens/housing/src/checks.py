"""Housing checks, DESIGN-SPEC sec 4 items 1-7, plus springs, engagement stack and insertion order.

Everything is evaluated on tessellated solids (0.01 mm chord) with manifold3d: exact mesh-mesh
intersection volumes and min_gap distances. The stock case is out/tub.stl + out/lid.stl of the
read-only enclosure copy (built 2026-09-25, E frame).
"""
import math
import time

import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial import cKDTree

import carrier
import clip
import cover
import params as P
import pcba_proxy
import util as U

EPS_VOL = 2e-3      # mm3: coincident faces / float32 slivers count as touching
TOUCH = 0.02        # mm: a datum face is "in contact" when its gap is below this
SEARCH = 6.0


def mf(shape):
    return U.manifold_of(U.to_mesh(shape))


def inter(a, b):
    i = a ^ b
    v = U.mvolume(i)
    if v <= 1e-7:
        return 0.0, None
    bb = U.mbbox(i)
    return v, bb


def depth_of(bb):
    return None if bb is None else float(min(np.subtract(bb[1], bb[0])))


class Model:
    def __init__(self, log=print):
        t = time.time()
        self.clip, self.clip_f = clip.build()
        self.cover, self.cover_f = cover.build()
        self.car, self.car_f = carrier.build()
        self.car_rigid = carrier.build_rigid()
        self.rod = carrier.rod()
        self.dowels = carrier.dowels()
        spec, notes = pcba_proxy.load_geometry()
        self.pcba_notes = notes or []
        self.pcba_spec = spec or pcba_proxy.proxy_spec()
        self.pcba_cmp = pcba_proxy.compare(spec) if spec else None
        self.pcba = pcba_proxy.build(self.pcba_spec)
        log(f'  solids built {time.time() - t:.1f}s')
        t = time.time()
        self.fixed = {}            # clip + cover features (never move relative to the case when seated)
        for n, s in self.clip_f.items():
            self.fixed['clip.' + n] = mf(s)
        for n, s in self.cover_f.items():
            self.fixed['cover.' + n] = mf(s)
        self.moving = {}           # float with the PCB
        for n, s in self.pcba.items():
            self.moving['pcba.' + n] = mf(s)
        for n, s in self.car_f.items():
            self.moving['carrier.' + n] = mf(s)
        for i, s in enumerate(self.dowels):
            self.moving[f'carrier.dowel_{i}'] = mf(s)
        self.moving['rod'] = mf(self.rod)
        self.parts = {'clip': mf(self.clip), 'cover': mf(self.cover), 'carrier': mf(self.car), 'rod': mf(self.rod)}
        self.case = {n: U.manifold_of(U.load_stl(P.STOCK_OUT / f'{n}.stl')) for n in ('tub', 'lid')}
        log(f'  meshes/manifolds {time.time() - t:.1f}s')

    def case_hit(self, m):
        vol, bbs = 0.0, []
        for c in self.case.values():
            v, bb = inter(m, c)
            if v > 0:
                vol += v
                bbs.append(bb)
        gap = min(m.min_gap(c, SEARCH) for c in self.case.values())
        bb = None
        if bbs:
            bb = [np.min([b[0] for b in bbs], 0).tolist(), np.max([b[1] for b in bbs], 0).tolist()]
        return vol, gap, bb


# ---------------------------------------------------------------------------- 1. seated vs case
def check_seated(M):
    rows, ok = {}, True
    design = {'back_bump_L': 0.30, 'back_bump_R': 0.30, 'leaf_bump': 0.40}
    for name, m in list(M.fixed.items()) + list(M.moving.items()):
        part, feat = (name.split('.', 1) + [''])[:2] if '.' in name else (name, name)
        vol, gap, bb = M.case_hit(m)
        kind = clip.CONTACT.get(feat) if part == 'clip' else None
        r = {'gap': round(gap, 3), 'interference_mm3': round(vol, 4)}
        if kind == 'datum':
            r['kind'] = 'datum contact'
            r['pass'] = vol <= 0.02 and gap <= TOUCH
        elif kind == 'spring':
            d = depth_of(bb) or 0.0
            r['kind'] = 'spring bump (designed interference)'
            r['depth'] = round(d, 3)
            r['design_depth'] = design[feat]
            r['pass'] = abs(d - design[feat]) <= 0.03
        elif name.startswith('pcba.pin_'):
            r['kind'] = 'pin in the J6 opening'
            r['pass'] = vol <= EPS_VOL and gap >= P.PIN_WALL_MIN - 0.3   # wall clearance proper is check 3
        else:
            r['kind'] = 'clearance'
            r['pass'] = vol <= EPS_VOL and gap > 0.0
            if feat in clip.DESIGN_GAP:
                r['design_gap'] = clip.DESIGN_GAP[feat]
                r['pass'] = r['pass'] and gap >= clip.DESIGN_GAP[feat] - 0.03
        rows[name] = r
        ok &= r['pass']
    total = {n: round(sum(inter(m, c)[0] for c in M.case.values()), 4) for n, m in M.parts.items()}
    return {'pass': bool(ok), 'features': rows, 'part_interference_mm3': total,
            'note': 'datum = P1/P2/P3 on the top face, lip on the front face, ear on the right side; springs = back-finger '
                    'bumps (0.30) and the left-leaf bump (0.40). Every other feature must clear (gap reported).'}


# ---------------------------------------------------------------------------- 2. insertion sweep
def pcba_offset(h, yf=P.J6_FACE_MODEL):
    e0 = yf - P.TIP_SEAT                   # housing height at which the pins would be seated in J6
    if h - P.Y_PLAY >= e0:
        return h - P.Y_PLAY                # hanging 0.21 low, pins above the J6 face
    if h >= e0:
        return e0                          # pins resting on the J6 face while the PCB lifts onto the roof pad
    return h


def probes(M):
    f = M.clip_f
    pr = {}
    for s, (fx, sx, sz) in {'L': ((-2.4, -1.0), (-5.8, -4.1), (P.CF['side_z0_left'] - 0.1, 4.21)),
                            'R': ((61.0, 62.4), (64.1, 65.8), (P.CF['side_z0_right'] - 0.1, 4.21))}.items():
        cf = f['corner_finger_' + s]
        pr[f'corner_finger_{s}.front(Z)'] = (mf(cf.intersect(U.box(*fx, 100, 117, 6.0, 7.7))), 0.15)
        pr[f'corner_finger_{s}.side(X)'] = (mf(cf.intersect(U.box(*sx, 100, 117, *sz))), 0.15)
    for n in ('back_finger_L', 'back_finger_R', 'leaf'):
        pr[n] = (M.fixed['clip.' + n], 0.20)
    for n in ('lip', 'ear', 'P1', 'P2', 'P3'):
        pr[n] = (M.fixed['clip.' + n], TOUCH)
    return pr


def check_sweep(M, log=print):
    s = P.SWEEP
    hs = [round(s['h0'] - i * s['step'], 3) for i in range(int(round((s['h0'] - s['h1']) / s['step'])) + 1)]
    pr = probes(M)
    first_eng = {k: None for k in pr}
    bump_first, bump_full = {}, {}
    collisions, allowed = [], []
    pin_min_gap = math.inf
    boss_min_gap = math.inf
    springs = {'clip.back_bump_L': 0.30, 'clip.back_bump_R': 0.30, 'clip.leaf_bump': 0.40}
    for h in hs:
        po = pcba_offset(h)
        moved_parts = {'clip': U.mtranslate(M.parts['clip'], (0, h, 0)), 'cover': U.mtranslate(M.parts['cover'], (0, h, 0)),
                       'carrier': U.mtranslate(M.parts['carrier'], (0, po, 0)), 'rod': U.mtranslate(M.parts['rod'], (0, po, 0))}
        for pn, pm in moved_parts.items():
            vol = sum(inter(pm, c)[0] for c in M.case.values())
            if vol <= EPS_VOL:
                continue
            feats = M.fixed if pn in ('clip', 'cover') else {k: v for k, v in M.moving.items() if k.startswith(pn)}
            for fn, fm in feats.items():
                if not fn.startswith(pn):
                    continue
                mm = U.mtranslate(fm, (0, h if pn in ('clip', 'cover') else po, 0))
                v = sum(inter(mm, c)[0] for c in M.case.values())
                if v <= EPS_VOL:
                    continue
                bbs = [inter(mm, c)[1] for c in M.case.values()]
                d = max(depth_of(b) or 0 for b in bbs)
                rec = {'h': h, 'feature': fn, 'mm3': round(v, 4), 'depth': round(d, 3)}
                if fn in springs:
                    allowed.append(rec)
                    bump_first.setdefault(fn, h)
                    if d >= springs[fn] - 0.01:
                        bump_full.setdefault(fn, h)
                else:
                    collisions.append(rec)
        for n, (m, thr) in pr.items():
            if first_eng[n] is None:
                g = min(U.mtranslate(m, (0, h, 0)).min_gap(c, 1.0) for c in M.case.values())
                if g <= thr:
                    first_eng[n] = h
        for k, m in M.moving.items():
            if k.startswith('pcba.pin_'):
                mm = U.mtranslate(m, (0, po, 0))
                pin_min_gap = min(pin_min_gap, min(mm.min_gap(c, SEARCH) for c in M.case.values()))
        bm = U.mtranslate(M.fixed['clip.boss'], (0, h, 0))
        boss_min_gap = min(boss_min_gap, min(bm.min_gap(c, SEARCH) for c in M.case.values()))
    def refine(test, h):          # test(h) True at h (engaged), False at h + step; bisect the boundary
        lo, hi = h, min(h + s['step'], s['h0'])
        if hi <= lo or test(hi):
            return h
        for _ in range(8):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if test(mid) else (lo, mid)
        return round(lo, 3)

    for n, h in list(first_eng.items()):
        if h is not None:
            m, thr = pr[n]
            first_eng[n] = refine(lambda hh: min(U.mtranslate(m, (0, hh, 0)).min_gap(c, 1.0) for c in M.case.values()) <= thr, h)
    for dct, need in ((bump_first, None), (bump_full, True)):
        for n, h in list(dct.items()):
            fm = M.fixed[n]

            def hit(hh, fm=fm, n=n, need=need):
                mm = U.mtranslate(fm, (0, hh, 0))
                rr = [inter(mm, c) for c in M.case.values()]
                v = sum(r[0] for r in rr)
                if need is None:
                    return v > EPS_VOL
                return max(depth_of(r[1]) or 0 for r in rr) >= springs[n] - 0.01
            dct[n] = refine(hit, h)
    tip_rest = P.TIP_SEAT - P.Y_PLAY
    order = []
    for n, h in first_eng.items():
        order.append({'h': h, 'event': f'{n} engages (gap <= {pr[n][1]})'})
    for n, h in bump_first.items():
        order.append({'h': h, 'event': f'{n} starts riding the case (preload builds)'})
    for n, h in bump_full.items():
        order.append({'h': h, 'event': f'{n} reaches full preload (on the flat face)'})
    order.append({'h': round(P.CASE_TOP - tip_rest, 3), 'event': 'pin tips (hanging, 107.73) cross the top-face plane'})
    for lab, yf in P.J6_FACES.items():
        order.append({'h': round(yf - tip_rest, 3), 'event': f'pin tips reach the J6 face y {yf} ({lab})'})
    order.append({'h': round(P.CASE_TOP - P.BOSS['y0'], 3), 'event': 'J6 boss enters the opening'})
    order.append({'h': 0.0, 'event': 'P1/P2/P3 land on the top face; tips at y 107.94'})
    order = sorted([o for o in order if o['h'] is not None], key=lambda o: -o['h'])
    xg = [first_eng[k] for k in first_eng if 'side(X)' in k]
    zg = [first_eng[k] for k in first_eng if 'front(Z)' in k or k.startswith('back_finger')]
    j6 = P.J6_FACE_MODEL - tip_rest
    return {'pass': not collisions, 'heights': hs[0:1] + hs[-1:], 'step': s['step'], 'collisions': collisions[:50],
            'n_collisions': len(collisions), 'designed_spring_contacts': len(allowed),
            'engagement_order': order, 'pin_min_gap_to_case_during_sweep': round(pin_min_gap, 3),
            'boss_min_gap_to_case_during_sweep': round(boss_min_gap, 3),
            'guided_before_J6': {'X_guide_h': max([x for x in xg if x is not None], default=None),
                                 'Z_guide_h': max([z for z in zg if z is not None], default=None),
                                 'pins_touch_J6_h(model face)': round(j6, 3)},
            'm_spec_3c_compare': {'pins cross top face': '7.65 (M-spec) / 7.87 (audit m1)',
                                  'pins reach J6': '5.21..4.68 (M-spec) / 5.42..4.89 (audit m1)',
                                  'X guided': '7.6', 'Z guided': '10.8/10.6 (audit: fingers 10.1..7.6, back 10.6)',
                                  'right ear': '3.6', 'lip': '3.8', 'boss': '1.4', 'left leaf': '6.1'}}


# ---------------------------------------------------------------------------- 3. pins vs J6
def check_pins(M):
    o = P.J6_OPEN
    pins = M.pcba_spec['pins']
    tips = {n: round(v[2], 3) for n, v in pins.items()}
    a = P.PIN_SQ / 2

    def wall_clear(dx=0.0, dz=0.0):
        best = math.inf
        for n, (x, z, *_r) in pins.items():
            x, z = x + dx, z + dz
            best = min(best, x - a - o['x0'], o['x1'] - (x + a), z - a - o['z0'], o['z1'] - (z + a))
        return best

    nominal = wall_clear()
    centred = min(wall_clear(dx, dz) for dx in (-0.05, 0, 0.05) for dz in (-0.05, 0, 0.05))
    full = min(wall_clear(P.FLOAT * math.cos(t), P.FLOAT * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 33))
    tip = min(tips.values())
    eng = {lab: round(yf - tip, 3) for lab, yf in P.J6_FACES.items()}
    j6 = {}
    try:
        s = cq.Shape.importBrep(str(P.STOCK / 'hardware' / 'cache' / 'J6.brep'))
        bb = s.BoundingBox()
        j6['bbox_y'] = [round(bb.ymin, 3), round(bb.ymax, 3)]
        entries = {}
        for n, (x, z, y0, y1) in pins.items():
            inside = lambda px, py, pz: s.isInside(cq.Vector(px, py, pz), 1e-4)
            depth = None
            for k in range(1, 200):
                if inside(x, bb.ymax - 0.05 * k, z):
                    depth = round(0.05 * k, 2)
                    break
            half = {}
            for ax, (ux, uz) in {'x': (1, 0), 'z': (0, 1)}.items():
                w = None
                for k in range(1, 60):
                    if inside(x + ux * 0.02 * k, bb.ymax - 0.1, z + uz * 0.02 * k):
                        w = round(0.02 * k * 2, 2)
                        break
                half[ax] = w
            pin = U.box(x - a, x + a, y0, y1, z - a, z + a)
            v = pin.intersect(s).Volume()
            entries[n] = {'entry_open_depth': depth, 'entry_width_x': half['x'], 'entry_width_z': half['z'],
                          'pin_vs_J6_model_mm3': round(v, 4), 'engagement_model_face': round(bb.ymax - y0, 3)}
        j6['entries'] = entries
    except Exception as e:
        j6['error'] = repr(e)
    ok = all(abs(t - P.TIP_SEAT) <= 0.02 for t in tips.values()) and nominal >= P.PIN_WALL_MIN and \
        centred >= P.PIN_WALL_MIN and all(P.E_MIN <= e <= P.E_MAX for e in eng.values())
    empty = min(math.hypot(x - P.NO_PIN[0], z - P.NO_PIN[1]) for x, z, *_r in pins.values())
    ok &= empty > 1.0
    return {'pass': bool(ok), 'tips_seated_y': tips, 'engagement_by_J6_face': eng, 'window': [P.E_MIN, P.E_MAX],
            'pin_wall_clearance': {'nominal': round(nominal, 3), 'centred_+-0.05': round(centred, 3),
                                   'full_float_+-0.30 (info; J6 lead-in centres the pins)': round(full, 3),
                                   'required': P.PIN_WALL_MIN},
            'nearest_metal_to_J6-12': round(empty, 3), 'J6_model': j6}


# ---------------------------------------------------------------------------- 4. optics keep-out
def keepout_solid(dz=0.0, dy=0.0):
    pts = [(y + dy, z + dz) for z, y in P.keepout_polygon()]
    return U.prism_x(pts, P.KO_X[0], P.KO_X[1])


def check_keepout(M):
    ko = keepout_solid()
    res, ok = {}, True
    for n, s in (('clip', M.clip), ('cover', M.cover), ('carrier', M.car)):
        v = s.intersect(ko).Volume()
        g = mf(s).min_gap(mf(ko), 5.0)
        res[n] = {'intrusion_mm3': round(v, 5), 'min_gap': round(g, 3)}
        ok &= v <= 1e-3
    # the engine (rod + keep-out) floats with the PCB; the clip/cover do not
    worst = {}
    for n, s in (('clip', M.clip), ('cover', M.cover)):
        ms = mf(s)
        gs = []
        for dy in (0.0, -P.Y_PLAY):
            for t in np.linspace(0, 2 * math.pi, 9)[:-1]:
                ks = mf(keepout_solid(P.FLOAT * math.sin(t), dy))
                gs.append(ms.min_gap(ks, 5.0))
                inter_v = U.mvolume(ms ^ U.manifold_of(U.to_mesh(keepout_solid(P.FLOAT * math.sin(t), dy))))
                ok &= inter_v <= EPS_VOL
        worst[n] = round(min(gs), 3)
    lip_clear = {f'z {z}': round(P.LIP['y0'] - P.y_ko(z), 3) for z in (P.LIP['z0'], P.LIP['z1'])}
    return {'pass': bool(ok), 'parts': res, 'min_gap_with_engine_float': worst, 'lip_bottom_vs_y_ko': lip_clear,
            'rule': 'y_ko(z) = 108.05 + 0.357 (z - 4) for z 3.93..13.70, rod lower half, z 18.10; x -1.0..61.0'}


# ---------------------------------------------------------------------------- 5. float extremes
DESIGNED = [  # (moving prefix, fixed prefix, why)
    ('pcba.board', 'clip.', 'PCB rests on the clip top (Y seat)'),
    ('pcba.board', 'cover.column_', 'float stop: hole on column'),
    ('pcba.board', 'cover.tongue', 'centering tongue (spring)'),
    ('pcba.pin_', 'cover.tail_pad', 'roof pad pushes the tails (seated)'),
    ('pcba.pin_', 'cover.roof', 'roof underside 0.20 above the tail tops, inside the tail-pad footprint'),
]


def designed(mn, fn):
    for a, b, why in DESIGNED:
        if mn.startswith(a) and fn.startswith(b):
            return why
    return None


def check_float(M):
    states = [(0.0, 0.0)] + [(P.FLOAT * math.cos(t), P.FLOAT * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 17)[:-1]]
    worst, viol, contacts = {}, [], {}
    fixed_parts = {'clip': M.parts['clip'], 'cover': M.parts['cover']}
    for dyn, dy in (('seated', 0.0), ('resting', -P.Y_PLAY)):
        for dx, dz in states:
            for mn, mm in M.moving.items():
                m2 = U.mtranslate(mm, (dx, dy, dz))
                for pn, pm in fixed_parts.items():
                    g = m2.min_gap(pm, 1.0)
                    if g >= P.FLOAT_CLEAR:
                        key = (mn, pn)
                        worst[key] = min(worst.get(key, 9), g)
                        continue
                    for fn, fm in M.fixed.items():
                        if not fn.startswith(pn + '.'):
                            continue
                        gf = m2.min_gap(fm, 1.0)
                        why = designed(mn, fn)
                        if why:
                            v, bb = inter(m2, fm)
                            c = contacts.setdefault((mn, fn), {'why': why, 'min_gap': 9, 'max_pen': 0.0, 'max_vol': 0.0})
                            c['min_gap'] = min(c['min_gap'], gf)
                            c['max_pen'] = max(c['max_pen'], depth_of(bb) or 0.0)
                            c['max_vol'] = max(c['max_vol'], v)
                            continue
                        worst[(mn, fn)] = min(worst.get((mn, fn), 9), gf)
                        if gf < P.FLOAT_CLEAR - 1e-3:
                            viol.append({'state': dyn, 'dx': round(dx, 3), 'dz': round(dz, 3), 'moving': mn, 'fixed': fn,
                                         'gap': round(gf, 3)})
    # designed contacts must not exceed their design: Y seat touch only, float stop touch only, tongue <= 0.45
    bad_contacts = []
    for (mn, fn), c in contacts.items():
        if 'tongue' in fn:       # spring: bump depth <= preload + float, body never touches
            bad = c['max_pen'] > P.TONGUE['preload'] + P.FLOAT + 0.02 or ('bump' not in fn and c['max_vol'] > 0.01)
        else:                    # touch-only contacts (Y seat, float stop, tail pad): no volume
            bad = c['max_vol'] > 0.01
        if bad:
            bad_contacts.append({'moving': mn, 'fixed': fn, 'pen': round(c['max_pen'], 3), 'vol': round(c['max_vol'], 4)})
    carrier_min = min([g for (mn, fn), g in worst.items() if mn.startswith(('carrier', 'rod'))], default=None)
    pcba_min = min([g for (mn, fn), g in worst.items() if mn.startswith('pcba')], default=None)
    lows = sorted(({'moving': k[0], 'fixed': k[1], 'min_gap': round(g, 3)} for k, g in worst.items() if g < 1.0),
                  key=lambda r: r['min_gap'])[:25]
    return {'pass': not viol and not bad_contacts, 'required': P.FLOAT_CLEAR,
            'states': f'{len(states)} X/Z positions (centre + 16 on the 0.30 circle) x seated/resting (0.21 Y)',
            'carrier_rod_min_gap': None if carrier_min is None else round(carrier_min, 3),
            'pcba_min_gap_excl_designed': None if pcba_min is None else round(pcba_min, 3),
            'violations': viol[:40], 'n_violations': len(viol), 'bad_designed_contacts': bad_contacts,
            'designed_contacts': [{'moving': k[0], 'fixed': k[1], **{a: (round(b, 3) if isinstance(b, float) else b)
                                                                       for a, b in v.items()}} for k, v in contacts.items()],
            'lowest_gaps_below_1mm': lows, 'pcba_source': M.pcba_spec['source']}


# ---------------------------------------------------------------------------- 6. printability
def to_print(shape, part):
    """E -> print frame: X' = x, Y' = z, Z' = bed_y - y (proper rotation, bed at Z' = 0)."""
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90).translate(cq.Vector(0, 0, P.PRINT_BED_Y[part]))


def overhangs(mesh):
    n = mesh.face_normals
    lim = math.sin(math.radians(P.OVERHANG_DEG))
    zmin = mesh.triangles[:, :, 2].min(1)
    flag = (n[:, 2] < -lim) & (zmin > 0.05)
    idx = np.where(flag)[0]
    patches = []
    if len(idx):
        adj = mesh.face_adjacency
        keep = flag[adj[:, 0]] & flag[adj[:, 1]]
        comps = trimesh.graph.connected_components(adj[keep], nodes=idx, min_len=1)
        for c in comps:
            c = np.asarray(c)
            area = float(mesh.area_faces[c].sum())
            sub = mesh.submesh([c], append=True)
            per = float(sum(np.linalg.norm(sub.vertices[e[0]] - sub.vertices[e[1]])
                            for e in sub.edges[trimesh.grouping.group_rows(sub.edges_sorted, require_count=1)]))
            width = 2 * area / per if per > 0 else 0
            lo, hi = sub.bounds
            patches.append({'area': round(area, 3), 'width': round(width, 3), 'z': round(float(lo[2]), 2),
                            'bbox_xy': [round(float(lo[0]), 2), round(float(lo[1]), 2), round(float(hi[0]), 2),
                                        round(float(hi[1]), 2)],
                            'ok': width <= P.BRIDGE_OK_W or area <= 1.0})
    return patches


def thin_walls(mesh, s=0.2, rmax=None):
    rmax = rmax or P.MIN_WALL + 0.1
    pts, fi, nrm = U.sample_triangles(mesh.triangles, s)
    pts = np.round(pts, 6)
    tree = cKDTree(pts)
    pairs = tree.query_pairs(rmax, output_type='ndarray')
    thick = np.full(len(pts), np.inf)
    for a in range(0, len(pairs), 2_000_000):
        pr = pairs[a:a + 2_000_000]
        for i, j in ((pr[:, 0], pr[:, 1]), (pr[:, 1], pr[:, 0])):
            ni, nj = nrm[i], nrm[j]
            anti = np.einsum('ij,ij->i', ni, nj) < -0.95
            d = pts[i] - pts[j]
            t = np.einsum('ij,ij->i', d, ni)
            lat = np.linalg.norm(d - t[:, None] * ni, axis=1)
            ok = anti & (t > 0.05) & (lat < 0.75 * s + 0.02)
            np.minimum.at(thick, i[ok], t[ok])
    return pts, thick


def check_print(M, declared):
    res, ok = {}, True
    for part, shape in (('clip', M.clip), ('cover', M.cover), ('carrier', M.car)):
        pm = U.to_mesh(to_print(shape, part))
        ov = overhangs(pm)
        pts, th = thin_walls(pm)
        thin = th < P.MIN_WALL - 0.02
        # back to E for the declared-exception boxes
        bed = P.PRINT_BED_Y[part]
        E = np.c_[pts[:, 0], bed - pts[:, 2], pts[:, 1]]
        dec = np.zeros(len(pts), bool)
        for lab, (x0, x1, y0, y1, z0, z1) in declared.get(part, {}).items():
            dec |= (E[:, 0] >= x0) & (E[:, 0] <= x1) & (E[:, 1] >= y0) & (E[:, 1] <= y1) & (E[:, 2] >= z0) & (E[:, 2] <= z1)
        und = thin & ~dec
        clusters = []
        if und.any():
            q = E[und]
            lab = trimesh.graph.connected_components(cKDTree(q).query_pairs(0.5, output_type='ndarray'),
                                                     nodes=np.arange(len(q)), min_len=1)
            for c in lab[:20]:
                c = np.asarray(c)
                clusters.append({'n': int(len(c)), 'min_t': round(float(th[und][c].min()), 3),
                                 'E_bbox': np.round(np.r_[q[c].min(0), q[c].max(0)], 2).tolist()})
        dec_min = {}
        for lab, (x0, x1, y0, y1, z0, z1) in declared.get(part, {}).items():
            sel = thin & (E[:, 0] >= x0) & (E[:, 0] <= x1) & (E[:, 1] >= y0) & (E[:, 1] <= y1) & (E[:, 2] >= z0) & (E[:, 2] <= z1)
            if sel.any():
                dec_min[lab] = round(float(th[sel].min()), 3)
        bad_ov = [p for p in ov if not p['ok']]
        r = {'overhang_patches_flagged': len(ov), 'overhang_area_flagged_mm2': round(sum(p['area'] for p in ov), 2),
             'overhang_patches_failing': bad_ov[:10], 'widest_accepted_patch': max([p['width'] for p in ov if p['ok']], default=0),
             'thin_wall_min_undeclared': round(float(th[~dec].min()), 3) if (~dec).any() else None,
             'thin_clusters_undeclared': clusters, 'declared_thin': dec_min,
             'mesh_watertight': bool(pm.is_watertight), 'print_height': round(float(pm.bounds[1][2]), 2)}
        r['pass'] = (not bad_ov) and (not clusters) and r['mesh_watertight']
        ok &= r['pass']
        res[part] = r
    return {'pass': bool(ok), 'parts': res,
            'rule': f'overhang > {P.OVERHANG_DEG} deg from vertical flagged; patches wider than {P.BRIDGE_OK_W} mm (and > 1 mm2) '
                    f'fail; walls between anti-parallel faces >= {P.MIN_WALL} except declared features'}


def declared_thin():
    d = {'cover': {}, 'clip': {}, 'carrier': {}}
    for n, t in P.TONGUES.items():
        pts = cover._poly(t, (P.TONGUE['face_off'] - 0.7, P.TONGUE['face_off'] + P.TONGUE['t'] + 0.05),
                          (t['root'] - 1.1, t['tip'] + 0.05))
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        d['cover'][f'tongue_{n} (0.8 spring, audit M5)'] = (min(xs), max(xs), P.TONGUE['y0'] - 0.1, P.ROOF_TOP + 0.1,
                                                             min(zs), max(zs))
    for n, (x, z) in P.COLS.items():
        r = P.COL_D / 2 + 0.05
        d['cover'][f'column_{n} wall 0.55 (contract 3.6 column, rev A 2.5 bore; 100% infill, drill 2.4)'] = (x - r, x + r, P.CLIP_TOP - 0.1,
                                                                                       P.COL_BOSS_Y0 + 0.25, z - r, z + r)
    d['cover']['engraved arrow + SCREEN ribs (top 0.4 of the roof)'] = (15.0, 45.0, P.ROOF_TOP - 0.45, P.ROOF_TOP + 0.1, 9.0, 20.0)
    x, z = P.COLS['C1']
    d['clip']['C1 pilot dia 1.8 in the 0.4-tall P3 pad (0.75/0.85)'] = (x - 1.0, x + 1.0, P.PAD_Y - 0.1, P.CLIP_UNDER + 0.3,
                                                              P.PADS['P3'][2] - 0.1, P.PADS['P3'][3] + 0.1)
    x, z = P.COLS['C2']
    d['clip']['C2 pilot dia 1.8 to the notch face x 59.2 (0.80)'] = (P.RIGHT_BLOCK['x0'] - 0.05, x, P.CLIP_UNDER - 0.2,
                                                                    P.CLIP_TOP + 0.1, z - 1.0, z + 1.0)
    d['clip']['boss / back-rail corner artefact (<= 4 samples)'] = (42.8, 43.2, 115.8, 116.2, -5.2, -4.1)
    ez0, ez1 = P.CAR['end_z']
    for lab, (x0, x1) in (('left', (P.CAR['x0'], P.CAR['end_in'][0])), ('right', (P.CAR['end_in'][1], P.CAR['x1']))):
        d['carrier'][f'{lab} cradle end: lip flexures 0.8, outer strip 0.525, dowel hole floor 0.30 over the crown, '
                     f'dowel hole 0.625 to the inner face'] = (x0 - 0.25, x1 + 0.25, P.CAR['end_bottom'] - 0.1,
                                                              P.PCB_Y_SEAT + 0.1, ez0 - 0.1, ez1 + 0.1)
    g = P.GLUE_DAM
    x0, x1 = P.CAR['end_in']
    d['carrier']['-Z glue-dam rebate (flange 1.0 -> 0.7)'] = (x0 - 0.1, x1 + 0.1, P.PCB_Y_SEAT - P.CAR['fl_t'] - 0.1,
                                                              P.PCB_Y_SEAT + 0.1, P.CAR['fl_m'][1] - g['w'] - 0.25,
                                                              P.CAR['fl_m'][1] + 0.1)
    d['carrier']['+Z glue-dam rebate (flange 1.0 -> 0.7)'] = (x0 - 0.1, x1 + 0.1, P.PCB_Y_SEAT - P.CAR['fl_t'] - 0.1,
                                                              P.PCB_Y_SEAT + 0.1, P.CAR['fl_p'][0] - 0.1,
                                                              P.CAR['fl_p'][0] + g['w'] + 0.25)
    return d


# ---------------------------------------------------------------------------- springs + stack
def cantilever(E, L, b, t, d):
    I = b * t ** 3 / 12
    k = 3 * E * I / L ** 3
    return k, k * d, 1.5 * t * d / L ** 2


def tapered(E, L_tot, a, b, t0, t1, d, n=4001):
    """Linear-taper cantilever (t0 at the root -> t1 at L_tot), load at a: k, F, root strain."""
    s = np.linspace(0.0, a, n)
    t = t0 + (t1 - t0) * s / L_tot
    f = (a - s) ** 2 * 12.0 / (E * b * t ** 3)
    k = 1.0 / float(np.sum((f[1:] + f[:-1]) * np.diff(s)) / 2.0)
    F = k * d
    return k, F, 6.0 * F * a / (b * t0 ** 2) / E


def springs(seated):
    out = {}
    bf_d = [seated['features'][f'clip.back_bump_{s}']['depth'] for s in 'LR']
    lf_d = seated['features']['clip.leaf_bump']['depth']
    L_bf = P.CLIP_UNDER - P.BF['bump_y']
    b_bf = P.BACK_FINGERS[0][1] - P.BACK_FINGERS[0][0]
    L_lf = P.CLIP_UNDER - P.LEAF['bump_y']
    b_lf = P.LEAF['z1'] - P.LEAF['z0']
    L_tot = P.CLIP_UNDER - P.TIP_Y
    for lab, L, b, sp, ds, rng, ref in (
            ('back_finger (each)', L_bf, b_bf, P.BF, bf_d, 0.25,
             'rev 0: t 1.2, b 10, k 8.64 N/mm, 2.59 N, strain 0.54 / 0.99 %, root stress 10.8 MPa'),
            ('left_leaf', L_lf, b_lf, P.LEAF, [lf_d], 0.25,
             'rev 0: t 1.2, b 5.0, k 2.84 N/mm, 1.14 N, strain 0.54 / 0.88 %, root stress 10.9 MPa')):
        d = float(np.mean(ds))
        t0, t1 = sp['t_root'], sp['t_tip']
        k, F, e = tapered(P.E_PETG, L_tot, L, b, t0, t1, d)
        _, Fmin, _ = tapered(P.E_PETG, L_tot, L, b, t0, t1, max(d - rng, 0))
        _, Fmax, emax = tapered(P.E_PETG, L_tot, L, b, t0, t1, d + rng)
        _, Fp, _ = tapered(P.E_PLA, L_tot, L, b, t0, t1, d)
        out[lab] = {'L': round(L, 2), 'b': round(b, 2), 't': f'{t0}->{t1}', 'deflection_as_built': round(d, 3),
                    'deflection_range': [round(max(d - rng, 0), 3), round(d + rng, 3)], 'k_N_per_mm': round(k, 2),
                    'force_N': round(F, 2), 'force_range_N': [round(Fmin, 2), round(Fmax, 2)],
                    'strain_nominal_pct': round(100 * e, 2), 'strain_max_pct': round(100 * emax, 2),
                    'root_stress_MPa': round(e * P.E_PETG, 1), 'root_fillet': sp['root_r'],
                    'PLA_force_N': round(Fp, 2), 'm_spec': ref}
    cr = P.CRADLE
    hm = sum(cr['hook_deg']) / 2
    Lc = (P.CRADLE['d'] / 2 + cr['lip_t'] / 2) * math.radians(cr['root_deg'] + hm)
    bc = cr['depth'] - 2 * cr['lip_x_gap']
    kc = 3 * P.E_PETG * (bc * cr['lip_t'] ** 3 / 12) / Lc ** 3
    d_seat = cr['interference'] / math.cos(math.radians(hm))
    hook_chord = 2 * (P.ROD['d'] / 2 - cr['interference']) * math.cos(math.radians(cr['hook_deg'][1]))
    d_snap = (P.ROD['d'] - hook_chord) / 2
    strain = lambda dd: 1.5 * cr['lip_t'] * dd / Lc ** 2
    out['cradle_lip (each of 4)'] = {
        'L': round(Lc, 2), 'b': round(bc, 2), 't': cr['lip_t'], 'deflection_as_built': round(d_seat, 3),
        'deflection_range': [round(0.15 / math.cos(math.radians(hm)), 3), round(d_snap, 3)],
        'k_N_per_mm': round(kc, 2), 'force_N': round(kc * d_seat, 2),
        'force_range_N': [round(kc * 0.15, 2), round(kc * 0.20, 2)],
        'strain_nominal_pct': round(100 * strain(d_seat), 2), 'strain_max_pct': round(100 * strain(d_snap), 2),
        'up_force_per_end_frictionless_N': round(2 * kc * d_seat * math.sin(math.radians(hm)), 2),
        'hold_force_per_end_mu0.3_N': round(2 * kc * d_seat * (math.sin(math.radians(hm)) + P.MU * math.cos(math.radians(hm))), 2),
        'rod_weight_N': 0.0097,
        'm_spec': f'curved lip, straight-cantilever estimate over the arc length; max strain is the snap-through '
                  f'({round(d_snap, 3)} per lip, chord {round(hook_chord, 3)}); one-time assembly, then epoxy dots'}
    T = P.TONGUE
    hbump = T['face_off'] + T['preload']
    for n, t in P.TONGUES.items():
        a1 = t['tip'] - 0.05
        contact = a1 - (2 * hbump + T['crest']) / 2
        L = contact - t['root']
        b = P.ROOF_TOP - T['y0']
        k, F, e = cantilever(P.E_PETG, L, b, T['t'], T['preload'])
        _, Ff, ef = cantilever(P.E_PETG, L, b, T['t'], T['preload'] + P.FLOAT)
        out[f'tongue_{n}'] = {'L_to_bump': round(L, 2), 'height': round(b, 2), 't': T['t'], 'k_N_per_mm': round(k, 2),
                              'preload_N': round(F, 3), 'full_float_N': round(Ff, 3), 'strain_full_float_pct': round(100 * ef, 2),
                              'slot_vs_max_deflection': [T['slot'], T['preload'] + P.FLOAT],
                              'audit_M5': 'k ~0.75 N/mm, 0.11 N preload, 0.34 N full float (1.5-tall floating tongue)'}
    nb = out['back_finger (each)']['force_N']
    nl = out['left_leaf']['force_N']
    j6 = 3 * P.J6_CONTACT_N
    fric = P.MU * (2 * nb * 2) + P.MU * (2 * nl)
    out['retention'] = {'J6_N': round(j6, 2), 'friction_N': round(fric, 2), 'total_N': round(j6 + fric, 2),
                        'insertion_N_approx': round(3 * P.J6_INSERT_N + fric, 2),
                        'm_spec': 'retention ~8 N (5..12), insertion ~10 N'}
    return out


def stack(M):
    bb = lambda s: s.BoundingBox()
    pad = min(bb(M.clip_f[n]).ymin for n in ('P1', 'P2', 'P3'))
    clip_top = bb(M.clip).ymax
    col_seat = min(bb(M.cover_f['column_' + n]).ymin for n in P.COLS)
    tail_pad = bb(M.cover_f['tail_pad']).ymin
    tip = tail_pad - P.HDR_OAL
    tol = sum(P.STACK_TOL.values())
    E = {lab: round(yf - tip, 3) for lab, yf in P.J6_FACES.items()}
    emax = max(E.values()) + tol
    emin = min(E.values()) - tol - P.SOLDER_MAX - P.ROOF_DEFL_MAX
    rss = math.sqrt(sum(v ** 2 for v in P.STACK_TOL.values()))
    return {'screws': screws(M), 'pad_face_y': round(pad, 3), 'clip_top_y': round(clip_top, 3), 'column_seat_y': round(col_seat, 3),
            'tail_pad_y': round(tail_pad, 3), 'clip_pad_to_top': round(clip_top - pad, 3),
            'cover_seat_to_pad': round(tail_pad - col_seat, 3), 'tip_seated_y': round(tip, 3),
            'tip_off_case_y': round(tip - P.Y_PLAY, 3), 'pcb_underside_seated': round(tail_pad - (P.HDR_TAIL - P.PCB_T) - P.PCB_T, 3),
            'engagement_nominal': E, 'engagement_worst': [round(emin, 3), round(emax, 3)],
            'margins': [round(emin - P.E_MIN, 3), round(P.E_MAX - emax, 3)], 'rss_tol': round(rss, 3),
            'm_spec_2d': 'tip 107.94; E 4.68..5.21 nominal, 4.03..5.64 worst (limits 3.68/6.00)',
            'pass': bool(emin >= P.E_MIN and emax <= P.E_MAX and abs(tip - P.TIP_SEAT) < 0.01)}


def screws(M):
    """Rev A (MAJOR-3): ST2.2 x 6.5 PT screws in dia 1.8 pilots; tips, engagement, walls."""
    seat = P.ROOF_TOP - P.CBORE_DEPTH
    tip = seat - P.SCREW['L']
    rows, ok = {}, True
    for n, (x, z) in P.COLS.items():
        ring = M.clip.intersect(U.cyl_y(x, z, P.PILOT_D / 2 + 0.3, 100.0, 125.0))
        y_bot = ring.BoundingBox().ymin
        eng = P.CLIP_TOP - max(tip, y_bot)
        clr = tip - P.CASE_TOP
        rows[n] = {'x': x, 'z': z, 'pilot_bottom_y': round(y_bot, 3), 'tip_y': round(tip, 3),
                   'tip_above_case_top': round(clr, 3), 'engaged': round(eng, 3),
                   'tip_vs_clip_underside': round(tip - y_bot, 3)}
        ok &= clr >= P.SCREW_TIP_CLEAR_MIN - 1e-6 and eng >= P.SCREW_ENGAGE_MIN - 1e-6
    x2, z2 = P.COLS['C2']
    x1, z1 = P.COLS['C1']
    r = P.PILOT_D / 2
    walls = {'C2 pilot to the header-notch face x %.2f' % P.RIGHT_BLOCK['x0']: round(x2 - r - P.RIGHT_BLOCK['x0'], 3),
             'C2 after thread forming (major 2.2)': round(x2 - P.SCREW['d'] / 2 - P.RIGHT_BLOCK['x0'], 3),
             'C1 pilot in the P3 pad layer (z)': [round(z1 - r - P.PADS['P3'][2], 3), round(P.PADS['P3'][3] - z1 - r, 3)],
             'cover column wall': round((P.COL_D - P.COL_BORE) / 2, 3),
             'screw radial clearance in the column bore': round((P.COL_BORE - P.SCREW['d']) / 2, 3)}
    hdr = M.pcba_spec['boxes'].get('J1_body')
    notch = None
    if hdr:
        notch = {'J1 body x1': hdr[1], 'notch face x': P.RIGHT_BLOCK['x0'],
                 'nominal': round(P.RIGHT_BLOCK['x0'] - hdr[1], 3),
                 'full float': round(P.RIGHT_BLOCK['x0'] - hdr[1] - P.FLOAT, 3)}
        ok &= notch['full float'] >= P.FLOAT_CLEAR - 1e-6
    return {'pass': bool(ok), 'screw': P.SCREW['name'], 'L': P.SCREW['L'], 'head_seat_y': seat, 'pilot_d': P.PILOT_D,
            'column_bore': P.COL_BORE, 'columns': rows, 'walls': walls, 'header_notch_clearance': notch,
            'rule': f"tip >= {P.SCREW_TIP_CLEAR_MIN} above the case top at every column, engaged >= {P.SCREW_ENGAGE_MIN}, "
                    f"J1 body >= {P.FLOAT_CLEAR} from the notch face at full float"}


# ---------------------------------------------------------------------------- 8. rod datum (rev A, MAJOR-1)
def check_rod(M):
    rod = mf(M.rod)
    rig = mf(M.car_rigid)
    vol = lambda dy: U.mvolume(U.mtranslate(rod, (0, dy, 0)) ^ rig)
    lo, hi = -0.30, 0.30
    free_lo, hit_hi = vol(lo) <= 1e-5, vol(hi) > 1e-5
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if vol(mid) > 1e-5 else (mid, hi)
    y_pre = P.ROD['y'] + lo
    R = P.ROD['d'] / 2
    lips = {}
    for n, sld in M.car_f.items():
        if not n.startswith('lip_'):
            continue
        bb = sld.BoundingBox()
        xs = np.linspace(bb.xmin + 0.05, bb.xmax - 0.05, 15)
        pts = np.c_[xs, np.full_like(xs, y_pre), np.full_like(xs, P.ROD['z'])]
        dmin, _, q = U.SurfaceField([U.to_mesh(sld)], s=0.04).exact_min(pts)
        ang = math.degrees(math.atan2(P.ROD['y'] - q[1], abs(q[2] - P.ROD['z'])))
        lips[n] = {'interference': round(R - dmin, 3), 'contact_deg_below_equator': round(ang, 1),
                   'x': [round(bb.xmin, 2), round(bb.xmax, 2)]}
    ends = {}
    for e in 'LR':
        im, ip = lips[f'lip_{e}_mz']['interference'], lips[f'lip_{e}_pz']['interference']
        ends[e] = {'z_preloaded': round(P.ROD['z'] + (im - ip) / 2, 3)}
    leds = [(k, v) for k, v in M.pcba_spec['boxes'].items() if k.startswith('D') and k[1:].isdigit() and int(k[1:]) <= 10]
    face = min(M.pcba_spec['underside_y'] - v[4] for k, v in leds)
    gap = face - (y_pre + R)
    w = carrier.wrap_as_built()
    ok = free_lo and hit_hi and abs(y_pre - P.ROD['y']) <= 0.05 and all(abs(v['z_preloaded'] - P.ROD['z']) <= 0.05
                                                                          for v in ends.values())
    ok &= all(0.15 - 0.005 <= v['interference'] <= 0.20 for v in lips.values()) and abs(gap - 2.0) <= 0.05
    ok &= w['snap_chord_at_hook'] < P.ROD['d']
    return {'pass': bool(ok), 'rod_axis_preloaded': {'y': round(y_pre, 3), 'z': [v['z_preloaded'] for v in ends.values()]},
            'target': {'y': P.ROD['y'], 'z': P.ROD['z'], 'tol': 0.05},
            'method': 'rod moved +Y along z 15.80 against the carrier minus its lips (the crown body) until first contact '
                      '(manifold intersection > 1e-5 mm3, 30-step bisection); lip interference = rod radius - exact distance '
                      'from the rod axis to each lip; z from the L/R interference balance',
            'lips': lips, 'led_face_y_min': round(face, 3), 'n_leds': len(leds), 'gap_led_to_rod': round(gap, 3),
            'dz_led_minus_rod': round(P.LED_Z - P.ROD['z'], 3), 'cradle': w,
            'retained_in_any_orientation': bool(w['snap_chord_at_hook'] < P.ROD['d'])}


def check_tongue_lead(M):
    """Rev A (MAJOR-2): tongue bumps have a 45-deg lead-in; the PCB edge never lands on a flat bump bottom."""
    T = P.TONGUE
    board = M.pcba['board']
    top = P.PCB_Y_SEAT + P.PCB_T
    res, ok = {}, True
    for n, t in P.TONGUES.items():
        bump = M.cover_f['tongue_bump_' + n]
        m = U.to_mesh(bump)
        v = m.vertices
        c = v[:, 0] if t['axis'] == 'x' else v[:, 2]
        prot = -t['sign'] * (c - t['edge'])           # > 0: inside the PCB edge
        crest_start = float(v[prot >= T['preload'] - 0.005, 1].min())
        bottom_prot = float(prot[v[:, 1] <= T['y0'] + 0.005].max())
        land = board.translate(cq.Vector(0, T['y0'] + 0.02 - top, 0)).intersect(bump).Volume()
        first = T['y0'] + T['lead'] - T['preload']     # where the 45-deg flank crosses the PCB edge line
        res[n] = {'full_crest_from_y': round(crest_start, 3), 'bump_bottom_vs_pcb_edge': round(bottom_prot, 3),
                  'pcb_top_at_bump_bottom_overlap_mm3': round(land, 5), 'edge_contact_starts_y': round(first, 3),
                  'seated_full_crest_band': [round(crest_start, 3), round(top, 3)],
                  'resting_full_crest_band': [round(crest_start, 3), round(top - P.Y_PLAY, 3)]}
        ok &= crest_start >= 119.5 - 1e-3 and bottom_prot < 0 and land <= 1e-6 and top - P.Y_PLAY - crest_start >= 0.4
    rest_top = P.PCB_Y_REST + P.PCB_T
    return {'pass': bool(ok), 'lead': T['lead'], 'tongues': res,
            'cover_insertion': {'columns_enter_the_PCB_holes_at_h': round(rest_top - P.CLIP_TOP, 3),
                                'bumps_touch_the_PCB_edge_at_h (on the 45-deg flank)':
                                    round(rest_top - res['left']['edge_contact_starts_y'], 3),
                                'full_crest_reaches_the_PCB_edge_at_h': round(rest_top - res['left']['full_crest_from_y'], 3)},
            'rule': 'full crest from y >= 119.5; bump bottom outside the PCB edge; no overlap with the PCB top 0.02 above '
                    'the bump bottom; >= 0.4 of full crest on the resting PCB edge'}


# ---------------------------------------------------------------------------- PCB agent's E-frame PCBA STL
def compare_pcba_stl(M):
    """Cross-check pcb/production/3d/*_pcba_E.stl against the geometry used for check 5 (report only)."""
    f = P.A / 'pcb' / 'production' / '3d' / 'silkscreen-light-attachment_pcba_E.stl'
    if not f.exists():
        return {'present': False}
    m = U.load_stl(f)
    lo, hi = m.bounds
    out = {'present': True, 'file': 'pcb/production/3d/' + f.name, 'bbox': [np.round(lo, 3).tolist(), np.round(hi, 3).tolist()],
           'lowest_y (pin tips, expect 107.94)': round(float(lo[1]), 3),
           'highest_y (tail tips, expect 121.40)': round(float(hi[1]), 3)}
    bodies = m.split(only_watertight=False)
    rows = []
    clipm, covm = M.parts['clip'], M.parts['cover']
    for b in bodies:
        blo, bhi = b.bounds
        ext = (bhi - blo)
        kind = 'board' if ext[0] > 30 and ext[2] > 15 else ('header' if bhi[1] > 121.0 or blo[1] < 110 else 'part')
        r = {'kind': kind, 'bbox': [np.round(blo, 2).tolist(), np.round(bhi, 2).tolist()], 'watertight': bool(b.is_watertight)}
        if b.is_watertight and kind == 'part':
            try:
                mb = U.manifold_of(b)
                r['gap_clip'] = round(mb.min_gap(clipm, 2.0), 3)
                r['gap_cover'] = round(mb.min_gap(covm, 2.0), 3)
            except Exception as e:
                r['err'] = repr(e)[:80]
        rows.append(r)
    parts = [r for r in rows if 'gap_clip' in r]
    out['bodies'] = len(rows)
    out['part_bodies_min_gap_clip'] = min([r['gap_clip'] for r in parts], default=None)
    out['part_bodies_min_gap_cover'] = min([r['gap_cover'] for r in parts], default=None)
    out['tips_match'] = bool(abs(lo[1] - 107.94) <= 0.02 and abs(hi[1] - 121.40) <= 0.02)
    out['note'] = ('seated nominal; the STEP board slab is drawn 118.695..120.205 (pcb/PROGRESS.md note 2), so the fit checks '
                   'use geometry.json (118.61..120.21); this is a cross-check only')
    out['bodies_detail'] = rows[:30]
    return out
