"""COVER (upper printed part), E frame, seated. Printed roof top (y 123.40) on the bed."""
import cadquery as cq

import params as P
from util import box, cyl_y, fuse, cut, prism_x, prism_y, prism_z, one_solid

T = P.TONGUE
EG = P.WALL_GAP
BACK_OUT = {'left': P.PCB_X[0] - EG - P.WALL_T, 'right': P.PCB_X[1] + EG + P.WALL_T,
            'back': P.PCB_Z[0] - EG - P.WALL_T}
BACK_IN = {'left': P.PCB_X[0] - EG, 'right': P.PCB_X[1] + EG, 'back': P.PCB_Z[0] - EG}
FR_IN = (P.PCB_WIDE_X[0] - P.FRONT_WALL_GAP, P.PCB_WIDE_X[1] + P.FRONT_WALL_GAP)
FR_OUT = (FR_IN[0] - P.FRONT_WALL_T, FR_IN[1] + P.FRONT_WALL_T)
SK_IN = P.SKIRT['z_in']
SK_OUT = SK_IN + P.SKIRT['t']
ZS = P.REGION_SPLIT_Z


def _uv(t, u, a):
    """(u = outward offset from the PCB edge, a = along-edge coordinate) -> (x, z)."""
    c = t['edge'] + t['sign'] * u
    return (c, a) if t['axis'] == 'x' else (a, c)


def _poly(t, us, as_):
    """rectangle u in us, along in as_ -> (x,z) polygon."""
    (u0, u1), (a0, a1) = us, as_
    return [_uv(t, u0, a0), _uv(t, u1, a0), _uv(t, u1, a1), _uv(t, u0, a1)]


def tongue_parts(t):
    fo, th, sl = T['face_off'], T['t'], T['slot']
    root, tip = t['root'], t['tip']
    pocket = prism_y(_poly(t, (0.05, fo + th + sl), (root, tip + T['tip_gap'])), P.CLIP_TOP - 0.5, P.ROOF_TOP + 0.5)
    body = prism_y(_poly(t, (fo, fo + th), (root - 1.0, tip)), T['y0'], P.ROOF_TOP)
    h = fo + T['preload']                  # bump height 0.60: crest 0.15 inside the PCB edge
    c = T['crest']
    a1 = tip - 0.05
    a0 = a1 - (2 * h + c)
    prof = [(fo + 0.05, a0), (fo, a0), (fo - h, a0 + h), (fo - h, a0 + h + c), (fo, a1), (fo + 0.05, a1)]
    bump = prism_y([_uv(t, u, a) for u, a in prof], T['y0'], T['bump_y1'])   # never touches the roof
    bump = cut(bump, lead_wedge(t, fo - h, a0 - 0.1, a1 + 0.1))
    return pocket, body, bump


def lead_wedge(t, u_crest, a0, a1):
    """Rev A (MAJOR-2): 45-deg lead-in at the bottom of a bump, T['lead'] deep, so the full crest starts at
    y0 + lead (119.55) and the PCB edge meets a flank, never the flat bump bottom."""
    c, y0 = T['lead'], T['y0']
    tri = [(u_crest + c + 0.1, y0 - 0.1), (u_crest - 0.1, y0 + c + 0.1), (u_crest - 0.1, y0 - 0.1)]
    if t['axis'] == 'x':          # u -> x, along -> z
        return prism_z([(t['edge'] + t['sign'] * u, y) for u, y in tri], a0, a1)
    return prism_x([(y, t['edge'] + t['sign'] * u) for u, y in tri], a0, a1)


def grip_ribs():
    """Rev A (MAJOR-4): 3 horizontal ribs on each cover end face (x -6.25 / 66.25, back region), centred at z -2.5
    over the J6 posts, 0.5 proud, flat underside (the finger catch) and a 45-deg top flank (prints roof-down)."""
    g = P.GRIP
    out = {}
    for side, x_face, sgn in (('L', BACK_OUT['left'], -1), ('R', BACK_OUT['right'], +1)):
        ribs = []
        for y0 in g['ys']:
            prof = [(0.0, y0), (g['h'], y0), (g['h'], y0 + g['flat']), (0.0, y0 + g['flat'] + g['h']),
                    (-0.2, y0 + g['flat'] + g['h']), (-0.2, y0)]
            ribs.append(prism_z([(x_face + sgn * u, y) for u, y in prof], g['z0'], g['z1']))
        out['grip_' + side] = fuse(*ribs)
    return out


def rear_pull_tools():
    """Rev A (MAJOR-4, optional): a 0.6-deep fingernail ledge in the back wall outer face (inside the envelope),
    flat top face (y 121.4) and a 45-deg lower flank; kept clear of the back-tongue pocket (x 19..28.4)."""
    r = P.REAR_PULL
    zb, d = BACK_OUT['back'], r['depth']
    prof = [(r['y0'], zb - 0.1), (r['y0'], zb), (r['y0'] + d, zb + d), (r['y1'], zb + d), (r['y1'], zb - 0.1)]
    return [prism_x(prof, x0, x1) for x0, x1 in r['xs']]


def text_and_arrow():
    tx = P.TEXT
    pl = cq.Plane(origin=(tx['x'], P.ROOF_TOP - tx['depth'], tx['z']), xDir=(1, 0, 0), normal=(0, 1, 0))
    txt = cq.Workplane(pl).text(tx['s'], tx['size'], tx['depth'] + 0.3, combine=False, halign='center',
                                valign='center', font='Arial', kind='bold').val()
    a = P.ARROW
    x, w, s, hd = a['x'], a['w'], a['shaft'], a['head']
    zb = a['z1'] - hd
    pts = [(x - s / 2, a['z0']), (x + s / 2, a['z0']), (x + s / 2, zb), (x + w / 2, zb), (x, a['z1']),
           (x - w / 2, zb), (x - s / 2, zb)]
    arrow = prism_y(pts, P.ROOF_TOP - a['depth'], P.ROOF_TOP + 0.3)
    return txt, arrow


def features():
    f = {}
    yu, yt = P.ROOF_UNDER, P.ROOF_TOP
    lo, ro, bo = BACK_OUT['left'], BACK_OUT['right'], BACK_OUT['back']
    f['roof'] = prism_y([(lo, bo), (ro, bo), (ro, ZS), (FR_OUT[1], ZS), (FR_OUT[1], SK_OUT), (FR_OUT[0], SK_OUT),
                         (FR_OUT[0], ZS), (lo, ZS)], yu, yt)
    yb = P.WALL_BOTTOM
    f['back_wall'] = box(lo, ro, yb, yu + 0.1, bo, BACK_IN['back'])
    f['left_wall'] = box(lo, BACK_IN['left'], yb, yu + 0.1, bo, ZS)
    f['right_wall'] = box(BACK_IN['right'], ro, yb, yu + 0.1, bo, ZS)
    f['left_end_wall'] = box(FR_OUT[0], FR_IN[0], P.SKIRT['y0'], yu + 0.1, ZS, SK_OUT)
    f['right_end_wall'] = box(FR_IN[1], FR_OUT[1], P.SKIRT['y0'], yu + 0.1, ZS, SK_OUT)
    f['skirt'] = box(FR_OUT[0], FR_OUT[1], P.SKIRT['y0'], yu + 0.1, SK_IN, SK_OUT)
    for n, (x, z) in P.COLS.items():
        f['column_' + n] = cyl_y(x, z, P.COL_D / 2, P.CLIP_TOP, P.COL_BOSS_Y0 + 0.01)
        f['col_boss_' + n] = cyl_y(x, z, P.COL_BOSS_D / 2, P.COL_BOSS_Y0, yu + 0.1)
        if n == P.COL_RELIEF['col']:   # rev A: the C2 foot (below the seated PCB underside) keeps 0.43 from the J1 body
            rl = P.COL_RELIEF
            f['column_' + n] = cut(f['column_' + n], box(x - 3.0, rl['x1'], P.CLIP_TOP - 1.0, rl['y1'], z - 3.0, z + 3.0))
    tp = P.TAIL_PAD
    f['tail_pad'] = box(tp['x0'], tp['x1'], P.ROOF_PAD_Y, yu + 0.1, tp['z0'], tp['z1'])
    f.update(grip_ribs())
    return f


def build():
    f = features()
    base = fuse(*f.values())
    tools = []
    for x, z in P.COLS.values():
        tools.append(cyl_y(x, z, P.COL_BORE / 2, P.CLIP_TOP - 1, P.ROOF_TOP + 1))
        tools.append(cyl_y(x, z, P.CBORE_D / 2, P.ROOF_TOP - P.CBORE_DEPTH, P.ROOF_TOP + 1))
    tongues = {}
    for n, t in P.TONGUES.items():
        pocket, body, bump = tongue_parts(t)
        tools.append(pocket)
        tongues[n] = (body, bump)
    tools += list(text_and_arrow())
    tools += rear_pull_tools()
    solid = cut(base, *tools)
    adds = []
    for n, (body, bump) in tongues.items():
        f['tongue_' + n] = body
        f['tongue_bump_' + n] = bump
        adds += [body, bump]
    solid = one_solid(fuse(solid, *adds))
    return solid, f


CONTACT_PCBA = {'tongue_left', 'tongue_right', 'tongue_back', 'tongue_front', 'tongue_bump_left',
                'tongue_bump_right', 'tongue_bump_back', 'tongue_bump_front', 'tail_pad',
                'column_C0', 'column_C1', 'column_C2'}
