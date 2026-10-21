"""CLIP (lower printed part), E frame, seated. Printed top face (y 118.40) on the bed.

Features are kept as named solids so the checks can attribute every contact and gap.
"""
import math

import params as P
from util import (arc, box, cyl_y, fuse, cut, mirror_x, prism_x, prism_y, prism_z, one_solid)
import cadquery as cq

YT = P.CLIP_TOP
YU = P.CLIP_UNDER
OV = 0.5          # features start 0.5 inside their parent block (y 116.5) so the union is solid


def back_rail():
    x0, x1 = P.CLIP_X
    z0, z1 = P.BACK_RAIL_Z
    nx0, nx1 = P.NOTCH_X
    pts = [(x0, z0), (x1, z0), (x1, z1), (nx1, z1), (nx1, P.NOTCH_Z), (nx0, P.NOTCH_Z), (nx0, z1), (x0, z1)]
    return prism_y(pts, YU, YT)


def _round_crest(h, r=0.3):
    """Bump profile (along, up) with 45-deg flanks and an R0.3 round crest whose top is exactly h (rev A, MINOR-8)."""
    c = h - r
    hb = r * math.sin(math.radians(45)) + (h - r + r * math.cos(math.radians(45)))
    arc_pts = [(r * math.sin(math.radians(a)), c + r * math.cos(math.radians(a))) for a in range(-45, 46, 9)]
    return [(-hb, -0.05), (-hb, 0.0)] + arc_pts + [(hb, 0.0), (hb, -0.05)]


def back_finger(x0, x1):
    """Rev A (MINOR-7): 1.4 at the root (y 116.0) tapering to 1.0 at the tip (y 103.0), R1.5 root fillet."""
    b = P.BF
    zi, r = b['z_in'], b['root_r']
    zo_root, zo_tip = zi - b['t_root'], zi - b['t_tip']
    lead = b['lead']
    cy, cz = YU - r, zi + r                       # R1.5 root fillet into the back rail underside
    fil = [(cy + r * math.sin(math.radians(a)), cz - r * math.cos(math.radians(a))) for a in range(0, 91, 6)]
    pts = [(YU + OV, zo_root), (YU, zo_root), (P.TIP_Y, zo_tip), (P.TIP_Y, zi - lead), (P.TIP_Y + lead, zi)] +         fil + [(YU + OV, cz)]
    return prism_x(pts, x0, x1)


def back_bump(x0, x1):
    b = P.BF
    y, zi = b['bump_y'], b['z_in']
    pts = [(y + a, zi + u) for a, u in _round_crest(b['bump_h'], b['crest_r'])]
    return prism_x(pts, x0, x1)


def leaf_body():
    """Rev A (MINOR-7): 1.4 -> 1.0 taper (inner face fixed at x -4.24), R1.5 root fillet into the left block."""
    l = P.LEAF
    xi, r = l['x_in'], l['root_r']
    xo_root, xo_tip = xi - l['t_root'], xi - l['t_tip']
    lead_x = xo_tip + 0.35                   # 45-deg lead-in from the tip straight into the bump flank
    cx, cy = xi + r, YU - r
    fil = [(cx - r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 91, 6)]
    pts = [(xo_root, YU + OV), (xo_root, YU), (xo_tip, P.TIP_Y), (lead_x, P.TIP_Y), (xi, P.TIP_Y + (xi - lead_x))] +         fil + [(cx, YU + OV)]
    return prism_z(pts, l['z0'], l['z1'])


def leaf_bump():
    l = P.LEAF
    y, xi = l['bump_y'], l['x_in']
    pts = [(xi + u, y + a) for a, u in _round_crest(l['bump_h'], l['crest_r'])]
    return prism_z(pts, l['z0'], l['z1'])


def corner_finger_left(side_z0):
    c = P.CF
    ax, az = c['axis']
    fx0, fx1 = c['front_x']
    zi, t, ri = c['z_in'], c['t'], c['r_in']
    ro = ri + t
    sx_in = c['side_x_in']
    sx_out = sx_in - t
    pts = [(fx1, zi), (fx1, zi + t), (ax, zi + t)] + arc(ax, az, ro, 90, 180)[1:] + \
          [(sx_out, side_z0), (sx_in, side_z0)] + arc(ax, az, ri, 180, 90)[:-1]
    body = prism_y(pts, P.TIP_Y, YU + OV)
    lead = c['lead']
    y1 = P.TIP_Y + lead
    cone = cq.Solid.makeCone(ri + lead + 0.1, ri, lead + 0.1, cq.Vector(ax, P.TIP_Y - 0.1, az), cq.Vector(0, 1, 0))
    wf = prism_x([(y1, zi), (P.TIP_Y - 0.1, zi + lead + 0.1), (P.TIP_Y - 0.1, az), (y1, az)], ax, fx1 + 0.2)
    ws = prism_z([(sx_in, y1), (sx_in - lead - 0.1, P.TIP_Y - 0.1), (ax, P.TIP_Y - 0.1), (ax, y1)], side_z0 - 0.1, az)
    return cut(body, cone, wf, ws)


def ear():
    e = P.EAR
    pts = [(e['x0'], YU + OV), (e['x0'], e['y0'] + e['chamfer']), (e['x0'] + e['chamfer'], e['y0']),
           (e['x1'], e['y0']), (e['x1'], YU + OV)]
    return prism_z(pts, e['z0'], e['z1'])


def lip():
    """Rev A (MINOR-8): R0.5 on the bottom inner edge (the case-face contact edge) instead of the 0.3 chamfer."""
    l = P.LIP
    r = l['round_r']
    arc_pts = [(l['y0'] + r - r * math.sin(math.radians(a)), l['z0'] + r - r * math.cos(math.radians(a)))
               for a in range(0, 91, 6)]
    pts = [(YU + OV, l['z0'])] + arc_pts + [(l['y0'], l['z1']), (YU + OV, l['z1'])]
    return prism_x(pts, l['x0'], l['x1'])


def boss():
    b = P.BOSS
    w = cq.Workplane('XY').box(b['x1'] - b['x0'], YU + OV - b['y0'], b['z1'] - b['z0'], centered=False) \
        .translate((b['x0'], b['y0'], b['z0'])).edges('<Y').chamfer(b['chamfer'])
    return w.val()


def features():
    f = {}
    f['back_rail'] = back_rail()
    x0, x1 = P.CLIP_X
    f['front_rail'] = box(x0, x1, YU, YT, *P.FRONT_RAIL_Z)
    lb, rb = P.LEFT_BLOCK, P.RIGHT_BLOCK
    f['left_block'] = box(lb['x0'], lb['x1'], YU, YT, lb['z0'], lb['z1'])
    f['right_block'] = box(rb['x0'], rb['x1'], YU, YT, rb['z0'], rb['z1'])
    for n, (px0, px1, pz0, pz1) in P.PADS.items():
        f[n] = box(px0, px1, P.PAD_Y, YU, pz0, pz1)
        if n == 'P3':
            f['P3_block'] = box(px0, px1, YU, YT, pz0, P.BRIDGE_Z[1])
        else:
            f[n + '_block'] = box(px0, px1, YU, YT, *P.BRIDGE_Z)
    b = P.BOSS
    f['boss_bridge'] = box(b['x0'], b['x1'], YU, YT, b['z0'], P.BRIDGE_Z[1])
    f['boss'] = boss()
    f['lip'] = lip()
    for i, (bx0, bx1) in enumerate(P.BACK_FINGERS):
        s = 'L' if i == 0 else 'R'
        f['back_finger_' + s] = back_finger(bx0, bx1)
        f['back_bump_' + s] = back_bump(bx0, bx1)
    f['leaf'] = leaf_body()
    f['leaf_bump'] = leaf_bump()
    f['corner_finger_L'] = corner_finger_left(P.CF['side_z0_left'])
    f['corner_finger_R'] = mirror_x(corner_finger_left(P.CF['side_z0_right']))
    f['ear'] = ear()
    return f


def pilots():
    return [cyl_y(x, z, P.PILOT_D / 2, P.PAD_Y - 1.0, YT + 1.0) for x, z in P.COLS.values()]


def build():
    f = features()
    solid = one_solid(cut(fuse(*f.values()), *pilots()))
    return solid, f


# the kind of contact each feature is allowed to make with the stock case when seated
CONTACT = {'P1': 'datum', 'P2': 'datum', 'P3': 'datum', 'lip': 'datum', 'ear': 'datum',
           'back_bump_L': 'spring', 'back_bump_R': 'spring', 'leaf_bump': 'spring'}
DESIGN_GAP = {'corner_finger_L': 0.10, 'corner_finger_R': 0.10, 'back_finger_L': 0.15, 'back_finger_R': 0.15,
              'leaf': 0.15, 'boss': 0.315}
