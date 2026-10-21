"""ROD CARRIER (PCB-registered, floats with the PCB) + the clear PMMA rod (reference) + dowels.

E frame with the PCB seated (underside y 118.61). Printed flanges-down (the PCB face on the bed).

Rev A (review round 1, MAJOR-1): the rod datums on the bore crown. Bore centre y 113.835, so a rod pushed up onto
the crown sits at axis y 113.91 (2.00 below the LED faces). Below the equator each cradle side is a curved lip
flexure that preloads the rod up onto the crown (0.16 interference); the mouth still faces -Y.
"""
import math

import numpy as np

import params as P
from util import box, cyl_x, cyl_y, fuse, cut, one_solid, prism_x

C = P.CAR
CR = P.CRADLE
YP = P.PCB_Y_SEAT
ZC = P.ROD['z']
YA = P.ROD['y']                  # design rod axis
YB = CR['yc']                    # bore centre (crown datum)
RB = CR['d'] / 2                 # 2.075
RO = RB + CR['lip_t']            # lip outer face
RS = RO + CR['slot']             # slot outer face
RH = P.ROD['d'] / 2 - CR['interference']   # hook radius about the design axis


def ends():
    """(back face x, inner face x) of both sockets."""
    ep = CR['end_play']
    return [(P.ROD['x0'] - ep, C['end_in'][0]), (P.ROD['x1'] + ep, C['end_in'][1])]


def features():
    f = {}
    ez0, ez1 = C['end_z']
    f['mz_wall'] = box(C['x0'], C['x1'], C['wz_bottom'], YP, *C['wz'])
    f['pz_wall'] = box(C['x0'], C['x1'], C['pz_bottom'], YP, *C['pz'])
    f['end_wall_L'] = box(C['x0'], C['end_in'][0], C['end_bottom'], YP, ez0, ez1)
    f['end_wall_R'] = box(C['end_in'][1], C['x1'], C['end_bottom'], YP, ez0, ez1)
    f['flange_m'] = box(C['x0'], C['x1'], YP - C['fl_t'], YP, *C['fl_m'])
    f['flange_p'] = box(C['x0'], C['x1'], YP - C['fl_t'], YP, *C['fl_p'])
    return f


def _mirror(pts):
    return [(2 * ZC - z, y) for z, y in pts]


def _yz(pts_zy):
    return [(y, z) for z, y in pts_zy]


def pocket_zy():
    """Lip + slot + mouth region below the crown (z, y): pie about the bore centre from 56 deg above the equator on
    the left, through the bottom, to 56 deg above the equator on the right."""
    a0 = 180.0 - CR['root_deg']
    a1 = 360.0 + CR['root_deg']
    return [(ZC, YB)] + [(ZC + RS * math.cos(math.radians(a)), YB + RS * math.sin(math.radians(a)))
                         for a in np.linspace(a0, a1, 97)]


def lip_zy():
    """Left lip (z, y). Angles are degrees below the equator, measured on the left side."""
    pts = []
    for a in np.linspace(-(CR['root_deg'] + 2.0), 0.0, 15):            # bore arc: root -> equator (2 deg overlap)
        pts.append((ZC - RB * math.cos(math.radians(a)), YB - RB * math.sin(math.radians(a))))
    h0, h1 = CR['hook_deg']
    for a in np.linspace(h0, h1, 7):                                    # hook: radius 2.0 - i about the rod axis
        pts.append((ZC - RH * math.cos(math.radians(a)), YA - RH * math.sin(math.radians(a))))
    yt = YB - RO * math.sin(math.radians(CR['tip_deg']))
    pts.append((ZC - CR['tip_half'], yt))                               # lead-in to the tip (chord 4.10)
    for a in np.linspace(CR['tip_deg'], -(CR['root_deg'] + 2.0), 25):  # outer face back to the root
        pts.append((ZC - RO * math.cos(math.radians(a)), YB - RO * math.sin(math.radians(a))))
    return pts


def socket_tools():
    t = []
    for xb, xin in ends():
        a, b = min(xb, xin), max(xb, xin)
        t.append(cyl_x(YB, ZC, RB, a - (0.01 if xin < xb else 0), b + (0.01 if xin > xb else 0)))   # bore
        t.append(prism_x(_yz(pocket_zy()), a, b))                                                       # lips/slots
        mh = CR['mouth_half']
        t.append(box(a, b, C['end_bottom'] - 0.1, YB, ZC - mh, ZC + mh))                                # mouth
        rc = RO + CR['slot'] / 2
        for deg in (180.0 - CR['root_deg'], CR['root_deg']):                                            # slot ends
            ang = math.radians(deg)
            t.append(cyl_x(YB + rc * math.sin(ang), ZC + rc * math.cos(ang), CR['slot'] / 2, a, b))
    for x, z in P.DATUM_HOLES:
        t.append(cyl_y(x, z, P.DOWEL['hole_d'] / 2, YP - P.DOWEL['hole_depth'], YP + 0.1))
    g = P.GLUE_DAM
    x0, x1 = C['end_in']
    t.append(box(x0, x1, YP - g['d'], YP + 0.1, C['fl_m'][1] - g['w'], C['fl_m'][1] + 0.01))
    t.append(box(x0, x1, YP - g['d'], YP + 0.1, C['fl_p'][0] - 0.01, C['fl_p'][0] + g['w']))
    return t


def lips():
    """The four lip flexures {name: solid}, each free 0.4 from both socket x faces."""
    out = {}
    g = CR['lip_x_gap']
    for (xb, xin), e in zip(ends(), 'LR'):
        a, b = min(xb, xin) + g, max(xb, xin) - g
        out[f'lip_{e}_mz'] = prism_x(_yz(lip_zy()), a, b)
        out[f'lip_{e}_pz'] = prism_x(_yz(_mirror(lip_zy())), a, b)
    return out


def dowels(y_under=YP):
    d = P.DOWEL
    y1 = y_under + P.PCB_T                         # flush with the PCB top
    return [cyl_y(x, z, d['d'] / 2, y1 - d['L'], y1) for x, z in P.DATUM_HOLES]


def rod():
    r = P.ROD
    return cyl_x(r['y'], r['z'], r['d'] / 2, r['x0'], r['x1'])


def build_rigid():
    """Carrier without the lip flexures (the crown datum body)."""
    return one_solid(cut(fuse(*features().values()), *socket_tools()))


def build():
    f = features()
    rigid = one_solid(cut(fuse(*f.values()), *socket_tools()))
    lp = lips()
    solid = one_solid(fuse(rigid, *lp.values()))
    f.update(lp)
    return solid, f


def wrap_as_built():
    hook_chord = 2 * RH * math.cos(math.radians(CR['hook_deg'][1]))
    return {'bore_d': CR['d'], 'bore_centre_y': YB, 'crown_y': round(YB + RB, 3),
            'rod_axis_on_crown_y': round(YB + RB - P.ROD['d'] / 2, 3),
            'lip': {'t': CR['lip_t'], 'slot': CR['slot'], 'root_deg_above_equator': CR['root_deg'],
                    'hook_deg_below_equator': list(CR['hook_deg']), 'hook_radius_about_axis': round(RH, 3),
                    'interference_radial': CR['interference'], 'x_length': round(CR['depth'] - 2 * CR['lip_x_gap'], 2),
                    'tip_deg': CR['tip_deg'], 'tip_chord': round(2 * CR['tip_half'], 3)},
            'snap_chord_at_hook': round(hook_chord, 3), 'snap_deflection_each_lip': round((P.ROD['d'] - hook_chord) / 2, 3),
            'radial_play_at_equator': round(RB - P.ROD['d'] / 2, 3), 'axial_play_each_end': CR['end_play'],
            'end_wall_behind_socket': round(P.ROD['x0'] - CR['end_play'] - C['x0'], 3),
            'dowel': dict(P.DOWEL), 'dowel_hole_floor_over_crown': round(YP - P.DOWEL['hole_depth'] - (YB + RB), 3)}
