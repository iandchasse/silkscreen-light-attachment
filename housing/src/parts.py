"""Rev C solids (E frame): BASE, LID and the PCBA (from pcb/build/geometry.json, proxy if missing).

Rev C = rev B + (1) the lid's front wall is an enclosing hood (flat reflector face flared 20 deg, closed ends, lip at y 110.5),
(2) a rounder, print-friendly brow and larger front corners, (3) a rabbet on the base's top outer edge so the lid wall
overlaps it and the seam is a hairline.
"""
import json
import math

import numpy as np

import params as P
import util as U

N = 36  # polygon segments per 90 deg of arc


def arc_pts(c0, c1, r, a0, a1, n=N):
    """(c0 + r cos a, c1 + r sin a) for a from a0 to a1 (deg)."""
    k = max(2, int(abs(a1 - a0) / 90 * n))
    return [(c0 + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             c1 + r * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


def round_poly(pts, radii, n=N):
    """Closed polygon with a tangent arc of radius radii[i] at vertex i (0 = sharp corner)."""
    out, m = [], len(pts)
    for i in range(m):
        p0, p1, p2 = (np.array(pts[(i - 1) % m], float), np.array(pts[i], float), np.array(pts[(i + 1) % m], float))
        r = radii[i]
        if r <= 0:
            out.append(tuple(p1))
            continue
        vin, vout = (p1 - p0) / np.linalg.norm(p1 - p0), (p2 - p1) / np.linalg.norm(p2 - p1)
        cr = vin[0] * vout[1] - vin[1] * vout[0]
        phi = math.acos(max(-1.0, min(1.0, float(vin @ vout))))
        t = r * math.tan(phi / 2)
        t1, t2 = p1 - vin * t, p1 + vout * t
        c = t1 + np.array([-vin[1], vin[0]]) * r * (1 if cr > 0 else -1)
        a1, a2 = math.atan2(*(t1 - c)[::-1]), math.atan2(*(t2 - c)[::-1])
        da = (a2 - a1) % (2 * math.pi) if cr > 0 else -((a1 - a2) % (2 * math.pi))
        k = max(2, int(abs(da) / (math.pi / 2) * n))
        out += [(c[0] + r * math.cos(a1 + da * j / k), c[1] + r * math.sin(a1 + da * j / k)) for j in range(k + 1)]
    return out


# ------------------------------------------------------------------ PCBA data
def pcba_data():
    """Returns (data, source). data: outline_xz, holes, leds, parts, headers, pins, tail_tip."""
    try:
        g = json.loads(P.PCB_GEOM.read_text())
        if g.get('rev') == 'B':
            return g, f"geometry.json rev B ({g.get('date')})"
    except Exception:
        pass
    # proxy from the contract numbers
    leds = [{'ref': f'D{i + 1}', 'x': x, 'body_box': {'x': [x - 1.5, x + 1.5], 'z': [8.8, 10.2], 'y': [115.9, 116.6]}}
            for i, x in enumerate([1.1, 14.6, 28.1, 41.6, 55.1, 4.9, 18.4, 31.9, 45.4, 58.9])]
    pins = [{'x': x, 'z': z, 'square': 0.64, 'y_post_tip': 108.1, 'y_tail_tip': 119.6}
            for x, z in [(54.662, -3.81), (57.202, -3.81), (54.662, -1.27)]]
    g = {'pcb': {'outline_xz': None, 'bbox_xz': [[-2.5, 62.5], [-6.0, 11.0]]},
         'holes': [{'x': x, 'z': z, 'dia': P.HOLE_D} for x, z in P.HOLES], 'leds': leds,
         'parts': [{'ref': 'R1', 'body_box': {'x': [44.5, 46.5], 'z': [-4.2, -3.0], 'y': [115.9, 116.6]}},
                   {'ref': 'R2', 'body_box': {'x': [48.0, 50.0], 'z': [-2.0, -0.8], 'y': [115.9, 116.6]}}],
         'header': {'bodies': [{'ref': 'J1', 'body_box': {'x': [53.392, 58.472], 'z': [-5.08, -2.54], 'y': [114.1, 116.6]}},
                               {'ref': 'J2', 'body_box': {'x': [53.392, 55.932], 'z': [-2.54, 0.0], 'y': [114.1, 116.6]}}],
                    'pins': pins, 'j6_face_y': list(P.J6_FACE)}}
    return g, 'PROXY from the contract numbers'


def outline_xz(g):
    o = g['pcb'].get('outline_xz')
    if o:
        return [tuple(p) for p in o]
    (x0, x1), (z0, z1) = g['pcb']['bbox_xz']
    r = 2.0
    pts = arc_pts(x1 - r, z0 + r, r, -90, 0) + arc_pts(x1 - r, z1 - r, r, 0, 90) + \
        arc_pts(x0 + r, z1 - r, r, 90, 180) + arc_pts(x0 + r, z0 + r, r, 180, 270)
    return pts


def tail_tip(g):
    return max(p['y_tail_tip'] for p in g['header']['pins'])


def lid_top(g):
    return round(max(119.6, tail_tip(g)) + P.TAIL_CLR + P.SKIN, 2)


def bbox_solid(b, grow=0.0):
    return U.box(b['x'][0] - grow, b['x'][1] + grow, b['y'][0] - grow, b['y'][1] + grow, b['z'][0] - grow, b['z'][1] + grow)


def build_pcba(g):
    y0 = g['pcb'].get('underside_y_seated', P.PCB_Y0)
    t = g['pcb'].get('thickness', P.PCB_T)
    pcb = U.prism_y(outline_xz(g), y0, y0 + t)
    pcb = U.cut(pcb, *[U.cyl_y(h['x'], h['z'], h['dia'] / 2, y0 - 1, y0 + t + 1) for h in g['holes']])
    leds = U.fuse(*[bbox_solid(d['body_box']) for d in g['leds']])
    rs = U.fuse(*[bbox_solid(p['body_box']) for p in g['parts']])
    bodies = U.fuse(*[bbox_solid(b['body_box']) for b in g['header']['bodies']])
    pins = U.fuse(*[U.box(p['x'] - p['square'] / 2, p['x'] + p['square'] / 2, p['y_post_tip'], p['y_tail_tip'],
                          p['z'] - p['square'] / 2, p['z'] + p['square'] / 2) for p in g['header']['pins']])
    return {'pcb': pcb, 'leds': leds, 'resistors': rs, 'header_bodies': bodies, 'pins': pins}


# ------------------------------------------------------------------ outlines
def cap_xy(ybot, top, inset=0.0):
    """Cap outline in the X-Y (front) view: sides at XO0/XO1, R6.25 corners, flat top. inset > 0 offsets it inward
    (concentric arcs): the rabbet / lid-skirt boundaries."""
    cy = top - P.XY_R
    ybot = min(ybot, cy - 0.5)          # the arcs start at cy; callers clip the bottom themselves
    r = P.XY_R - inset
    return [(P.XO0 + inset, ybot), (P.XO1 - inset, ybot)] + arc_pts(P.CORNER_X[1], cy, r, 0, 90) + \
        arc_pts(P.CORNER_X[0], cy, r, 90, 180)


def slope():
    return (P.EMIT_Z[0] - P.WIN_EDGE[1]) / (P.EMIT_Y - P.WIN_EDGE[0])


def graze_z(y, margin=P.LIGHT_MARGIN):
    """z of the grazing ray (lowest emitter point -> window top edge), minus a perpendicular margin."""
    s = slope()
    return P.WIN_EDGE[1] + s * (y - P.WIN_EDGE[0]) - margin * math.sqrt(1 + s * s)


def case_cavity():
    """Stock case top region grown by CL on the sides/front/back (top face kept at 115.60)."""
    c, top = P.CL, P.CASE_TOP
    x0, x1, zb, zf = P.CX0 - c, P.CX1 + c, P.CZB - c, P.CZF + c
    r5 = P.CORNER_R + c
    cy = top - r5
    xy = [(x0, 90.0), (x1, 90.0)] + arc_pts(P.CORNER_X[1], cy, r5, 0, 90) + arc_pts(P.CORNER_X[0], cy, r5, 90, 180)
    rb, rf = P.BACK_R + c, P.FRONT_R + c
    yz = [(90.0, zb)] + arc_pts(top - rb, P.BACK_C[1], rb, -90, 0) + arc_pts(top - rf, P.FRONT_C[1], rf, 0, 90) + [(90.0, zf)]
    vb, vf = P.VBACK_R + c, P.VFRONT_R + c
    xz = arc_pts(-2.09, -4.7, vb, 180, 270) + arc_pts(62.09, -4.7, vb, 270, 360) + \
        arc_pts(62.29, 4.2, vf, 0, 90) + arc_pts(-2.29, 4.2, vf, 90, 180)
    s1 = U.prism_z(xy, -12, 14)
    s2 = U.prism_x(yz, -8, 68)
    s3 = U.prism_y(xz, 90.0, top + 0.5)
    return s1.intersect(s2).intersect(s3).clean()


def light_cut():
    """Everything the base may not occupy in front of the case face over the window width."""
    y0 = P.JAW_Y0
    s = slope()
    yl = P.WIN_EDGE[0] + (P.LED_CLR_Z - P.WIN_EDGE[1] + P.LIGHT_MARGIN * math.sqrt(1 + s * s)) / s
    yz = [(100.0, P.CZF + P.CL), (y0, P.CZF + P.CL), (y0, graze_z(y0)), (yl, P.LED_CLR_Z), (118.0, P.LED_CLR_Z),
          (118.0, 20.0), (100.0, 20.0)]
    return U.prism_x(yz, -2.29, 62.29)


def fin_yz():
    """Side-view (Y-Z) region of the skirt incl. the front-corner X guides: everything at y >= Y_BOT, plus z above the
    45 deg line through (Y_BOT, FIN_Z) down to FIN_Y; concave corner filleted FIN_RC, convex tip rounded FIN_RV."""
    from shapely.geometry import Polygon
    y0, z0 = P.Y_BOT, P.FIN_Z
    zt = z0 + (y0 - P.FIN_Y)
    s = Polygon([(y0 + 12, -20), (y0 + 12, 30), (P.FIN_Y, 30), (P.FIN_Y, zt), (y0, z0), (y0, -20)])
    s = s.buffer(P.FIN_RC, quad_segs=16).buffer(-P.FIN_RC, quad_segs=16)
    s = s.buffer(-P.FIN_RV, quad_segs=16).buffer(P.FIN_RV, quad_segs=16)
    return list(s.exterior.coords)[:-1]


def base_xz():
    """Plan (X-Z) outline of the base: back corners, sides, the wraps round the case's front vertical corners and the
    central tongue (z up to 9, trimmed by light_cut) between them."""
    wr = P.WRAP_R
    return arc_pts(-2.09, -4.7, P.XZ_R_BACK, 180, 270) + arc_pts(62.09, -4.7, P.XZ_R_BACK, 270, 360) + \
        arc_pts(62.29, 4.2, wr, 0, 90) + [(62.29, 9.0), (-2.29, 9.0)] + arc_pts(-2.29, 4.2, wr, 90, 180)


def tongue_rect():
    """The base's central front tongue (x between the wraps, z 4..9): never rabbeted, never skirted."""
    from shapely.geometry import box as sbox
    return sbox(-2.29, 4.0, 62.29, 9.0)


def hood_profile(top):
    """Side-view (Y-Z) outer silhouette of the lid: roof y=top, back R2 round, vertical hood front z=Z_FRONT down to the
    lip y=HOOD_LIP_Y (outer edge R_LIP) and the soft brow: vertical front -> R_KNEE -> 45 deg bevel (leg HOOD_CHAMFER) ->
    R_ROOF -> roof. The lid prints roof-down, so the brow never overhangs more than 45 deg (+ the small R_ROOF bed round)."""
    zf, zb, c = P.Z_FRONT, P.ZOB, P.HOOD_CHAMFER
    pts = [(P.HOOD_LIP_Y, zb), (P.HOOD_LIP_Y, zf), (top - c, zf), (top, zf - c), (top, zb)]
    return round_poly(pts, [0, P.HOOD_R_LIP, P.HOOD_R_KNEE, P.HOOD_R_ROOF, P.TOP_R_BACK])


def hood_inner_z(y):
    """z of the flat reflector face at height y (y <= PCB underside): flared HOOD_FLARE deg away from the case."""
    return P.VISOR_Z0 + (P.PCB_Y0 - y) * math.tan(math.radians(P.HOOD_FLARE))


def rabbet_cut(top):
    """Base: everything on the floor's rim (y CASE_TOP .. above the floor) outside the outline inset by RAB, except the
    tongue. Leaves a shoulder at y = CASE_TOP, RAB wide, all round the sides, back and corner wraps."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    keep = unary_union([Polygon(base_xz()).buffer(-P.RAB, join_style='round', quad_segs=16), tongue_rect()])
    keep = max(keep.geoms, key=lambda p: p.area) if hasattr(keep, 'geoms') else keep
    band = U.box(-10, 70, P.CASE_TOP, P.LID_BOT + 1.0, -10, 14)
    inside = U.prism_y(list(keep.exterior.coords)[:-1], P.CASE_TOP - 1, P.LID_BOT + 2).intersect(
        U.prism_z(cap_xy(100, top, P.RAB), -10, 14))
    return band.cut(inside)


# ------------------------------------------------------------------ parts
def build_base(g, top, with_bumps=True):
    xz = base_xz()
    env = U.prism_z(cap_xy(P.FIN_Y, top), P.ZOB - 1, 10).intersect(U.prism_y(xz, P.FIN_Y, P.FLOOR_TOP)).intersect(
        U.prism_x(fin_yz(), -8, 68)).clean()
    j = P.J6_OPEN
    window = U.box(j['x0'], j['x1'], 110.0, 118.0, j['z0'], j['z1'])
    bosses = [U.cyl_y(x, z, P.BOSS_D / 2, P.FLOOR_TOP - 0.5, P.BOSS_TOP) for x, z in P.HOLES]
    b = P.BUMP
    zc = P.CZB - P.CL + b['proud'] - b['r']
    bumps = [U.cyl_x(b['y'], zc, b['r'], xa, xb) for xa, xb in b['xs']] if with_bumps else []
    base = U.cut(env, case_cavity(), light_cut(), window, rabbet_cut(top))
    base = U.fuse(base, *bosses, *bumps)
    base = U.cut(base, *[U.cyl_y(x, z, P.PILOT_D / 2, P.PILOT_BOT, P.BOSS_TOP + 1) for x, z in P.HOLES])   # blind
    return U.one_solid(base), {'bumps': U.fuse(*bumps) if bumps else None}


def build_lid(g, top):
    zf, zb, ylip = P.Z_FRONT, P.ZOB, P.HOOD_LIP_Y
    rl = P.XZ_R_FRONT_LID
    xz = arc_pts(-2.09, -4.7, P.XZ_R_BACK, 180, 270) + arc_pts(62.09, -4.7, P.XZ_R_BACK, 270, 360) + \
        arc_pts(P.XO1 - rl, zf - rl, rl, 0, 90) + arc_pts(P.XO0 + rl, zf - rl, rl, 90, 180)
    env = U.prism_z(cap_xy(ylip, top), zb - 1, zf + 1).intersect(U.prism_x(hood_profile(top), -8, 68)).intersect(
        U.prism_y(xz, ylip - 1, top + 1)).clean()
    from shapely.geometry import Polygon, box as sbox
    from shapely.ops import unary_union
    cav = Polygon(outline_xz(g)).buffer(P.PCB_GAP, join_style='round', quad_segs=16)
    xc0, _, xc1, _ = cav.bounds                                        # the hood's closed ends sit at the cavity's x limits
    # below the rim (z < BROW_Z): only a skirt rides over the base's rabbet: it is the cap outline minus the outline inset
    # by RAB - RAB_CL (so RAB_CL clearance to the rabbet face), and it stops RAB_CL_V above the shoulder
    inner = unary_union([Polygon(base_xz()).buffer(-(P.RAB - P.RAB_CL), join_style='round', quad_segs=16),
                         sbox(xc0, 0.0, xc1, P.BROW_Z + 1.0)])
    inner = max(inner.geoms, key=lambda p: p.area) if hasattr(inner, 'geoms') else inner
    below = U.box(-10, 70, 100, P.CASE_TOP + P.RAB_CL_V, -10, P.BROW_Z)          # nothing below the skirt's lower edge
    ins = U.prism_y(list(inner.exterior.coords)[:-1], 100, P.LID_BOT).intersect(
        U.prism_z(cap_xy(100, top, P.RAB - P.RAB_CL), -10, P.BROW_Z)).intersect(U.box(-10, 70, 99, P.LID_BOT + 1, -10, P.BROW_Z))
    under = U.fuse(below, ins)
    # the hood: flat reflector face from the PCB underside down to the lip, between the closed ends
    hz0, hz1 = hood_inner_z(P.PCB_Y0), hood_inner_z(ylip - 1.0)
    hood_in = U.prism_x([(ylip - 1.0, P.BROW_Z), (ylip - 1.0, hz1), (P.PCB_Y0, hz0), (P.PCB_Y0, P.BROW_Z)], xc0, xc1)
    cavity = U.prism_y(list(cav.exterior.coords)[:-1], P.PCB_Y0, P.PCB_Y1)
    pins = g['header']['pins']
    px = [p['x'] for p in pins]
    pz = [p['z'] for p in pins]
    m = 0.85 + 0.45
    pocket = U.box(min(px) - m, max(px) + m, P.PCB_Y1 - 0.1, tail_tip(g) + P.TAIL_CLR, min(pz) - m, max(pz) + m)
    cb_floor = round(top - P.HEAD_K, 3)      # a k-max M2 pan head sits flush with the top; tip of a 3 mm screw 0.1 above the pilot bottom
    holes = []
    for x, z in P.HOLES:
        holes += [U.cyl_y(x, z, P.RECESS_D / 2, 116.0, P.RECESS_TOP), U.cyl_y(x, z, P.CLR_D / 2, 116.0, cb_floor + 0.01),
                  U.cyl_y(x, z, P.CB_D / 2, cb_floor, top + 1)]
    lid = U.cut(env, under, hood_in, cavity, pocket, *holes)
    return U.one_solid(lid), {'cb_floor': cb_floor, 'hood_x': (round(xc0, 3), round(xc1, 3))}


def build_all():
    g, src = pcba_data()
    top = lid_top(g)
    base, bf = build_base(g, top)
    base_nb, _ = build_base(g, top, with_bumps=False)
    lid, lf = build_lid(g, top)
    return dict(g=g, src=src, top=top, base=base, base_nb=base_nb, lid=lid, pcba=build_pcba(g), bumps=bf['bumps'], cb_floor=lf['cb_floor'],
                hood_x=lf['hood_x'])


if __name__ == '__main__':
    import time
    t = time.time()
    M = build_all()
    for n in ('base', 'lid'):
        bb = M[n].BoundingBox()
        print(n, M[n].isValid(), len(M[n].Solids()), round(M[n].Volume(), 1),
              [round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
    print('lid top', M['top'], 'src', M['src'], f'{time.time() - t:.1f}s')
