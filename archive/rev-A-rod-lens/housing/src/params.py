"""All housing numbers, enclosure frame E (mm).

E: X = main-board KiCad X - 44.24, Y = 148.25 - KiCad Y (+Y = the device's top edge),
Z = 0 at the main-PCB rear face, +Z toward the screen. Source: design/DESIGN-SPEC.md (the
contract), design/mechanical-spec.md (M-spec), design/spec-audit.md, design/optics-final.md Rev 2.
Deviations from the contract are marked DEV and listed in housing/PROGRESS.md.
"""
import math
import sys
from pathlib import Path

HOUSING = Path(__file__).resolve().parents[1]
A = HOUSING.parent
OUT = HOUSING / 'out'
STOCK = A / 'enclosures' / 'silkscreen-enclosure-claude'
STOCK_OUT = STOCK / 'out'
PCB_GEOM = A / 'pcb' / 'build' / 'geometry.json'

# ---------------------------------------------------------------- stock case (rev K, unmodified)
CASE_X0, CASE_X1 = -4.09, 64.09
CASE_TOP = 115.60
CASE_ZF, CASE_ZB = 6.0, -6.7
CORNER_R, CORNER_CY, CORNER_CX0, CORNER_CX1 = 5.0, 110.6, 0.91, 59.09
FRONT_EDGE_R, BACK_EDGE_R = 1.8, 2.0
SEAM_V = (-4.15, -3.35)
J6_OPEN = dict(x0=42.582, x1=58.922, z0=-5.415, z1=0.215)
J6_FACES = {'enclosure model': 113.15, 'B.Fab': 112.93, 'STEP-internal': 112.82,
            'STEP, main board 0.20 down (INFERRED)': 112.62}
J6_FACE_MODEL = 113.15
E_MIN, E_MAX = 3.68, 6.00          # J6 usable engagement window


def stock_params_check():
    """Import the stock case's params read-only (no .pyc written) and compare."""
    sys.dont_write_bytecode = True
    src = str(STOCK / 'src')
    if src not in sys.path:
        sys.path.append(src)          # appended: never shadows this project's modules
    import importlib.util
    spec = importlib.util.spec_from_file_location('stock_params', STOCK / 'src' / 'params.py')
    sp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sp)
    pairs = {'X0': (sp.X0, CASE_X0), 'X1': (sp.X1, CASE_X1), 'Y1': (sp.Y1, CASE_TOP),
             'Z_FRONT': (sp.Z_FRONT, CASE_ZF), 'Z_BACK': (sp.Z_BACK, CASE_ZB),
             'CORNER_R': (sp.CORNER_R, CORNER_R), 'FRONT_EDGE_R': (sp.FRONT_EDGE_R, FRONT_EDGE_R),
             'BACK_EDGE_R': (sp.BACK_EDGE_R, BACK_EDGE_R)}
    return {k: {'stock': round(a, 4), 'housing': b, 'ok': abs(a - b) < 1e-3} for k, (a, b) in pairs.items()}


# ---------------------------------------------------------------- light PCB (DESIGN-SPEC sec 3)
PCB_T = 1.6
PCB_Y_SEAT = 118.61                 # underside, seated (roof pad on the tails)
PCB_Y_REST = 118.40                 # underside, resting on the clip (off the case)
Y_PLAY = PCB_Y_SEAT - PCB_Y_REST    # 0.21
FLOAT = 0.30                        # radial X/Z float on the columns
PCB_X = (-3.50, 63.50)
PCB_Z = (-6.20, 19.60)
PCB_WIDE_X = (-4.20, 64.20)
PCB_WIDE_Z0 = 12.10
COL_HOLE_D = 4.20
COLS = {'C0': (5.00, 0.50), 'C1': (47.00, 2.35), 'C2': (60.90, -2.54)}   # rev A fix: C2 x 61.00 -> 60.90 (shared with the PCB)
DATUM_HOLE_D = 1.60
DATUM_HOLES = [(-2.40, 16.00), (62.40, 16.00)]
STAKE_HOLES = [(15.00, 13.10), (45.00, 13.10), (15.00, 18.30), (45.00, 18.30)]   # rev A fix: +Z pair z 18.40 -> 18.30
LED_Z = 16.00
LED_X_WARM = [1.1, 14.6, 28.1, 41.6, 55.1]
LED_X_COOL = [4.9, 18.4, 31.9, 45.4, 58.9]
LED_L, LED_W, LED_H = 3.00, 1.40, 0.70
# proxy positions for R1/R2 (0805) and D11/D12 (SOT-23) in zone A (DESIGN-SPEC: x 31..41, z -3..3)
PROXY_PARTS = {'R1': (33.0, -1.8, 2.0, 1.25, 0.60), 'R2': (33.0, 1.8, 2.0, 1.25, 0.60),
               'D11': (37.8, -1.8, 2.9, 2.4, 1.10), 'D12': (37.8, 1.8, 2.9, 2.4, 1.10)}

# header: Samtec TSW-102-14-G-D-004, 3 live pins named by the J6 pin they mate
PINS = {'5': (54.662, -3.810), '6': (57.202, -3.810), '11': (54.662, -1.270)}
NO_PIN = (57.202, -1.270)          # J6-12 /P+_FUSE: must stay empty
PIN_SQ = 0.64
HDR_OAL, HDR_TAIL, HDR_POST, HDR_BODY = 13.46, 2.79, 8.13, 2.54
HDR_BODY_X = (53.392, 58.472)
HDR_BODY_Z = (-5.080, 0.000)

# ---------------------------------------------------------------- engagement stack
CLIP_TOP = 118.40                   # clip top face = PCB seat = print bed
PAD_Y = CASE_TOP                    # datum pads land on the tub top face
ROOF_PAD_Y = 121.40                 # tail pad face (roof underside over the header)
TIP_SEAT = ROOF_PAD_Y - HDR_OAL     # 107.94
STACK_TOL = {'case top': 0.10, 'clip pad->top': 0.10, 'cover seat->pad': 0.10, 'header OAL': 0.13}
SOLDER_MAX, ROOF_DEFL_MAX = 0.10, 0.12

# ---------------------------------------------------------------- CLIP (M-spec 3a/3b + audit)
CLIP_UNDER = 116.0                  # underside of rails / blocks (0.40 above the top face)
CLIP_X = (-5.80, 65.69)
BACK_RAIL_Z = (-8.25, -4.20)        # rev A: outer face -8.05 -> -8.25, flush with the 1.4 finger roots
NOTCH_X = (52.6, 59.2)              # rev A: 59.3 -> 59.2 so the C2 pilot (x 60.90, dia 1.8) keeps a 0.80 wall
NOTCH_Z = -5.80                     # DEV: -5.70 -> -5.80 so the header body keeps 0.40 at full float
FRONT_RAIL_Z = (4.20, 7.60)
PADS = {'P1': (2.0, 8.0, -2.9, 3.9), 'P2': (24.0, 30.0, -2.9, 3.9),
        'P3': (43.0, 58.3, 0.7, 4.1)}   # DEV: P3 z0 0.6 -> 0.7 (header body 0.40 at full float)
BRIDGE_Z = (-4.20, 4.20)            # pad blocks join both rails above y 116.0
LIP = dict(x0=-0.6, x1=60.6, z0=6.00, z1=7.60, y0=110.0, round_r=0.5)   # rev A: R0.5 bottom inner edge (was a 0.3 chamfer)
BOSS = dict(x0=43.0, x1=52.6, z0=-5.10, z1=-0.10, y0=114.20, chamfer=0.3)
LEFT_BLOCK = dict(x0=-5.8, x1=2.0, z0=-6.55, z1=4.6)
RIGHT_BLOCK = dict(x0=59.2, x1=65.69, z0=-6.55, z1=4.6)
EAR = dict(x0=64.09, x1=65.69, z0=-3.0, z1=4.0, y0=107.0, chamfer=0.8)
TIP_Y = 103.0
BACK_FINGERS = [(4.2, 11.8), (44.8, 52.4)]   # rev A: b 10.0 -> 7.6 keeps k ~8.6 N/mm with the 1.4 -> 1.0 taper;
#   the right finger moves out of the header notch (x 52.6..59.2) so its R1.5 root fillet keeps >= 0.40 from J1
BF = dict(z_in=-6.85, t_root=1.4, t_tip=1.0, bump_y=106.0, bump_h=0.45, crest_r=0.3, lead=0.8, root_r=1.5)
#   rev A (MINOR-7/8): taper 1.4 at the root (y 116.0) -> 1.0 at the tip (y 103.0), R1.5 root fillet, R0.3 round crest
LEAF = dict(x_in=-4.24, t_root=1.4, t_tip=1.0, z0=-2.4, z1=1.4,   # rev A: b 5.0 -> 3.8 keeps k ~2.8 N/mm with the taper
            bump_y=104.5, bump_h=0.55, crest_r=0.3, root_r=1.5)  # (DEV 6: M-spec b 6.0; >= 1.1 from the corner-finger side part)
CF = dict(front_x=(-2.29, -1.10), z_in=6.10, t=1.5, axis=(-2.29, 4.20), r_in=1.9,
          side_x_in=-4.19, side_z0_left=2.5, side_z0_right=2.0, side_z1=4.20, lead=1.0)
PILOT_D = 1.8                       # rev A (MAJOR-3): 1.6 -> 1.8 (0.8 d) for the ST2.2 thread-former, through the seat block

# ---------------------------------------------------------------- COVER
ROOF_TOP = 123.40
ROOF_UNDER = 121.60                 # roof 1.80; the tail pad is 0.20 proud at 121.40
TAIL_PAD = dict(x0=52.9, x1=59.0, z0=-5.6, z1=0.5)
WALL_GAP = 0.75                     # cover wall inner face to the PCB edge (0.45 at full float)
WALL_T = 2.0                        # back-region walls (1.0 behind the tongue slots)
WALL_BOTTOM = CLIP_TOP + 0.10       # walls stop 0.10 above the clip: the columns carry the load
FRONT_WALL_GAP = 0.75               # front-region end walls to the widened PCB / carrier end walls
FRONT_WALL_T = 1.6
REGION_SPLIT_Z = 11.25              # back-region walls end here, front-region end walls start
SKIRT = dict(z_in=PCB_Z[1] + WALL_GAP, t=2.0, y0=110.0)   # inner 20.35 >= 20.30
COL_D, COL_BORE, COL_BOSS_D = 3.60, 2.50, 5.20   # rev A: bore 2.30 -> 2.50 (screw major 2.2)
COL_BOSS_Y0 = PCB_Y_SEAT + PCB_T + 0.45    # 120.66: boss shoulder 0.45 above the seated PCB top
CBORE_D, CBORE_DEPTH = 4.40, 1.0
COL_RELIEF = dict(col='C2', x1=59.20, y1=PCB_Y_SEAT + 0.30)   # rev A: C2 foot flat, J1 body >= 0.43 at full float
SCREW = dict(name='ST2.2 x 6.5 pan, plastics thread-forming (DIN 7981 form / PT class)', d=2.2, L=6.5, head_d=4.0, head_k=1.6)
SCREW_TIP_CLEAR_MIN = 0.30          # screw tip above the case top face at every column
SCREW_ENGAGE_MIN = 2.40             # thread engaged in the clip pilot
# centering tongues (audit M5, horizontal cantilevers cut into the walls)
TONGUE = dict(L=8.0, t=0.8, slot=0.5, tip_gap=0.4, inner_slit=0.4, face_off=0.45,
              preload=0.15, y0=119.05, crest=0.2, bump_y1=121.20, lead=0.50)   # rev A: 45-deg 0.50 lead-in, full crest from 119.55   # bump stays 0.40 below the roof
#   face_off: tongue face sits 0.45 behind the PCB edge (0.30 float + 0.15), so the bump is
#   0.60 tall and interferes 0.15 (the preload). y0: bottom 0.44 above the seated carrier top.
TONGUES = {  # edge axis, edge value, sign (+1: wall on the + side of the edge), root, tip
    'left':  dict(axis='x', edge=PCB_X[0], sign=-1, along='z', root=-5.0, tip=3.0),
    'right': dict(axis='x', edge=PCB_X[1], sign=+1, along='z', root=2.85, tip=10.85),
    'back':  dict(axis='z', edge=PCB_Z[0], sign=-1, along='x', root=20.0, tip=28.0),
    'front': dict(axis='z', edge=PCB_Z[1], sign=+1, along='x', root=26.0, tip=34.0),
}
TEXT = dict(s='SCREEN', size=3.6, depth=0.4, x=30.0, z=12.6)
ARROW = dict(x=30.0, z0=15.2, z1=19.0, w=4.0, shaft=1.4, head=1.8, depth=0.4)

# ---------------------------------------------------------------- ROD CARRIER (DESIGN-SPEC sec 4)
CAR = dict(x0=-4.20, x1=64.20,
           wz=(12.00, 13.70), wz_bottom=113.91,          # -Z wall to the rod equator (rev A: outer face 12.50 -> 12.00)
           pz=(18.10, 19.60), pz_bottom=110.0,           # +Z wall = optical front lip (rev A: outer face 19.10 -> 19.60)
           end_bottom=110.0, end_in=(-1.00, 61.00),
           fl_m=(12.00, 14.20), fl_p=(17.20, 19.30), fl_t=1.0,
           end_z=(12.00, 19.60))                           # rev A: end walls widened (z 12.50..19.10) for the lip flexures
ROD = dict(d=4.0, x0=-3.0, x1=63.0, y=113.91, z=15.80)
CRADLE = dict(d=4.15, yc=113.835, depth=2.2, end_play=0.20,   # DEV: mouth toward -Y, 2.2 deep (see PROGRESS)
              lip_t=0.8, slot=0.4, root_deg=56.0, tip_deg=22.0, hook_deg=(4.0, 12.0), interference=0.16,
              lip_x_gap=0.4, tip_half=2.05, mouth_half=2.6)
#   rev A (MAJOR-1): bore centre y 113.91 -> 113.835, so the rod datums on the crown (y 115.91 = LED face - 2.00).
#   Below the equator each side is a curved lip flexure (0.8 thick, rooted 56 deg above the equator, behind a 0.4
#   slot, free 0.4 from both socket x faces) with a hook of radius 2.0 - 0.16 about the rod axis at 4..12 deg below
#   the equator: 0.16 interference preloads the rod up onto the crown; the mouth still faces -Y.
DOWEL = dict(d=1.50, L=4.0, hole_d=1.55, hole_depth=2.4)   # DEV: ISO 8734 1.5 x 4 dowels in epoxy, slip holes, flush with the PCB top
GLUE_DAM = dict(w=0.30, d=0.30)     # rev A (MINOR-6): rebate along both flange inner edges, x -1.0..61.0
GRIP = dict(z0=-6.5, z1=1.5, h=0.5, flat=0.4, ys=(119.1, 120.5, 121.9))   # rev A (MAJOR-4): 3 ribs per cover end face
REAR_PULL = dict(xs=((3.0, 18.0), (30.0, 57.0)), depth=0.6, y0=120.4, y1=121.4)   # fingernail ledge in the back wall

# ---------------------------------------------------------------- optics keep-out (Rev 2)
KO_X = (-1.0, 61.0)


def y_ko(z):
    return 108.05 + 0.357 * (z - 4.00)


def keepout_polygon(n_arc=48):
    """Rev 2 keep-out in (z, y), closed polygon (optics-final R2.1)."""
    pts = [(3.93, 100.0), (3.93, y_ko(3.93))]
    for z in (6.00, 7.60, 10.00):
        pts.append((z, y_ko(z)))
    pts += [(13.70, y_ko(13.70)), (13.70, ROD['y'])]
    r = ROD['d'] / 2
    for i in range(n_arc + 1):          # rod lower half, from -Z to +Z through the bottom
        a = math.pi + math.pi * i / n_arc
        pts.append((ROD['z'] + r * math.cos(a), ROD['y'] + r * math.sin(a)))
    pts += [(18.10, ROD['y']), (18.10, 100.0)]
    return pts


# ---------------------------------------------------------------- material / springs
E_PETG, E_PLA = 2000.0, 3500.0      # MPa
MU = 0.3
J6_CONTACT_N = 1.39                 # per contact, retention (Samtec SSW analogue)
J6_INSERT_N = 1.67

# ---------------------------------------------------------------- checks
MIN_WALL = 1.0
OVERHANG_DEG = 50.0
BRIDGE_OK_W = 3.0                   # overhang patches narrower than this are bridges/holes: flagged, accepted
FLOAT_CLEAR = 0.40
SWEEP = dict(h0=15.0, h1=0.0, step=0.25)
PIN_WALL_MIN = 1.0

# print transforms: E -> print frame (proper rotation, bed at Z = 0, growth +Z)
PRINT_BED_Y = {'clip': CLIP_TOP, 'cover': ROOF_TOP, 'carrier': PCB_Y_SEAT}
