"""Single source of numbers for the silkscreen-light-attachment PCBA (rev B, "simple").

Mirrors design/DESIGN-SPEC-revB.md (which supersedes DESIGN-SPEC.md).  Every mechanical number here is in the
ENCLOSURE frame E (mm):
    X = main-board KiCad X - 44.24,   Y = 148.25 - main-board KiCad Y (+Y = device top edge),
    Z = 0 at the main-PCB rear face, +Z toward the screen/reader.
The light PCB lies in E's X-Z plane.  Its KiCad frame K:
    x_K = X + 100.000,   y_K = 100.000 - Z
F.Cu faces -Y (toward the case) and carries every part; B.Cu faces +Y (the housing lid).
Rev A (rod lens, carrier, BAW56, 2x2 TSW header) is archived in archive/rev-A-rod-lens/.
"""
from __future__ import annotations

PROJECT = "silkscreen-light-attachment"
REVISION = "B"
DATE = "2026-09-25"
COMPANY = "idc LLC"
TITLE = "Silkscreen light attachment"

# ------------------------------------------------------------------ frames
K_OX = 100.000          # x_K = X + K_OX
K_OY = 100.000          # y_K = K_OY - Z


def to_k(X, Z):
    """Enclosure (X, Z) -> light-PCB KiCad (x_K, y_K)."""
    return (X + K_OX, K_OY - Z)


def to_e(xk, yk):
    """Light-PCB KiCad (x_K, y_K) -> enclosure (X, Z)."""
    return (xk - K_OX, K_OY - yk)


# ------------------------------------------------------------------ headers (hand-soldered by the builder)
# Hong Cheng HC-PZ254-11.5L series (LCSC product attributes, 2026-09-25): insulation (body) height 2.5, mating pin 6.0,
# end-connection (tail) pin 3.0, total 11.5 ("11.5L"), square brass pin, gold, 2.54 pitch.  The pin section is not on
# the product page; 0.64 square is the standard for this header style (assumed).  Body width 2.50 per row (assumed,
# typical); body length = positions x 2.54.
HDR = {
    "body_h": 2.50, "post": 6.00, "tail": 3.00, "post_sq": 0.64, "body_w": 2.50, "pitch": 2.54,
    "drill": 1.02, "pad": 1.70,
    "source": "LCSC/JLC product attributes 2026-09-25 (insulation height 2.5 mm, mating pin 6 mm, end pin 3 mm, "
              "square pin, brass, gold); total 11.5 mm from the MPN; 0.64 mm square pin assumed (not listed)",
    "alt": "Harwin M20-9990246 (DigiKey product 3728226): 1x2, 3 mm tail, 6.1 mm mating (tin); 0.1 mm deeper",
}
HEADERS = {
    # ref: pads {name = mating J6 pin: (X, Z)}, part data
    "J1": {"pads": {"5": (54.662, -3.810), "6": (57.202, -3.810)}, "positions": 2,
           "mpn": "HC-PZ254-11.5L-1x2PZ", "manufacturer": "Hong Cheng", "lcsc": "C27985187", "stock": 24852,
           "digikey": "Harwin M20-9990246 (DigiKey product 3728226) - 6.1 mm post",
           "datasheet": "https://www.lcsc.com/datasheet/lcsc_datasheet_2407101107_Hong-Cheng-HC-PZ254-11-5L-1x2PZ_C27985187.pdf"},
    "J2": {"pads": {"11": (54.662, -1.270)}, "positions": 1,
           "mpn": "HC-PZ254-11.5L-1x1PZ", "manufacturer": "Hong Cheng", "lcsc": "C27985186", "stock": 10775,
           "digikey": "1 pin cut from Harwin M20-9990246 (DigiKey product 3728226)",
           "datasheet": "https://www.lcsc.com/datasheet/lcsc_datasheet_2407101107_Hong-Cheng-HC-PZ254-11-5L-1x1PZ_C27985186.pdf"},
}
HDR_JLC_TYPE = "JLC Extended (no Basic 2.54 mm headers are listed; checked 2026-09-25)"


def header_body(ref):
    """E body box (x0, x1, z0, z1) of a header: pitch x positions long, body_w wide, centred on its pad row."""
    pads = list(HEADERS[ref]["pads"].values())
    xs = [p[0] for p in pads]
    z = pads[0][1]
    h = HDR["pitch"] / 2
    return (round(min(xs) - h, 4), round(max(xs) + h, 4), round(z - HDR["body_w"] / 2, 4), round(z + HDR["body_w"] / 2, 4))


def header_centre(ref):
    b = header_body(ref)
    return (round((b[0] + b[1]) / 2, 4), round((b[2] + b[3]) / 2, 4))


# ------------------------------------------------------------------ stack (E, Y)
STACK = {
    "pcb_t": 1.000,              # rev B: 1.0 mm board
    "underside_y": 116.60,       # F.Cu face: rests on the housing base's 1.0 floor, on the case top (115.60)
    "underside_y_resting": 116.60,
    "top_y": 117.60,             # B.Cu face
}
STACK["body_bottom_y"] = round(STACK["underside_y"] - HDR["body_h"], 4)             # 114.10
STACK["post_tip_y"] = round(STACK["body_bottom_y"] - HDR["post"], 4)                # 108.10
STACK["tail_tip_y"] = round(STACK["underside_y"] + HDR["tail"], 4)                  # 119.60 (2.0 above the top)
J6_FACE_Y = (112.82, 113.15)                 # J6 receptacle face (mechanical-spec sec 1)
ENGAGEMENT_LIMITS = (3.7, 6.0)

# ------------------------------------------------------------------ outline (E): rounded rectangle
OUTLINE = {"x0": -2.50, "x1": 62.50, "z0": -6.00, "z1": 11.00, "r": 2.0}

# ------------------------------------------------------------------ holes (E, all NPTH)
HOLES = [
    # (name, dia, X, Z, purpose)
    ("M1", 4.80, 10.00, -1.00, "housing boss (dia 4.40) + ST2.2 screw"),
    ("M2", 4.80, 38.00, -1.00, "housing boss (dia 4.40) + ST2.2 screw"),
]
HOLE_COPPER_CLEAR = 0.40        # no copper within 0.40 of an NPTH edge
HOLE_TRACE_CLEAR = 0.50         # traces keep 0.50 (kicad_dru rule, kept from rev A)
COLUMN_KEEPOUT = 0.40           # parts keep 0.4 off the boss holes
COLUMN_KEEPOUT_EXCEPT = {}
COLUMN_CRTYD = 0.40             # NPTH courtyard = hole + 0.40
EDGE_WEB_MIN = 0.50             # every NPTH keeps >= 0.50 of FR-4 to the routed outline

# ------------------------------------------------------------------ J6 (E)
J6 = {
    "pitch": 2.54,
    "pins": {4: (52.122, -3.810), 5: (54.662, -3.810), 6: (57.202, -3.810),
             11: (54.662, -1.270), 12: (57.202, -1.270)},
    "net": {4: "GND", 5: "LED_SW", 6: "W-", 11: "C-", 12: "P+_FUSE"},
}
PLUG = {
    "pads": {"5": (54.662, -3.810), "6": (57.202, -3.810), "11": (54.662, -1.270)},
    "nets": {"5": "LED_SW", "6": "W-", "11": "C-"},
    "ref": {"5": "J1", "6": "J1", "11": "J2"},
    "forbidden": [(57.202, -1.270, "J6-12 P+_FUSE"), (52.122, -3.810, "J6-4 GND")],
    "forbid_r": 1.00,
}
HANDEDNESS_TOL = 0.02

# ------------------------------------------------------------------ LEDs
LED = {
    "mpn": "HL-A-3014H421W-S1-08HL-HR3", "manufacturer": "HONGLITRONIC",
    "digikey": "n/a - LCSC only (C210340 warm / C210343 cool)",
    "datasheet": "https://www.lcsc.com/datasheet/C210340.pdf",
    "ds_ref": "Hongli B-17-A-1548 rev A/3 (2019-05-24) p.2",
    "body": (3.00, 1.40, 0.70),              # L (X), W (Z), H (-Y)
    "cavity": (2.50, 1.12, 0.40),            # reflector opening L x W, depth
    # datasheet p.2 'Recommended Soldering Pattern': pad 1 (cathode) 1.91 x 0.92, pad 2 0.91 x 0.92, gap 0.55
    "pad1": (1.91, 0.92), "pad2": (0.91, 0.92), "gap": 0.55,
    "z": 9.50,                               # rev B row centre (E)
    "warm": {"refs": ["D1", "D2", "D3", "D4", "D5"], "x": [1.1, 14.6, 28.1, 41.6, 55.1],
             "lcsc": "C210340", "cct": "3000 K", "bin": "WS 2800-3100 K"},
    "cool": {"refs": ["D6", "D7", "D8", "D9", "D10"], "x": [4.9, 18.4, 31.9, 45.4, 58.9],
             "lcsc": "C210343", "cct": "6000 K", "bin": "60-5 5700-6500 K"},
    "vf_13mA": (2.60, 2.85, 3.15),           # min, typ, max at 13.3 mA
    "vf_uA": 2.3,                            # per LED at ~14 uA, hot
    "ifp": 0.080, "if_max": 0.040, "vr": 5.0,
}
PER_STRING = 5

# ------------------------------------------------------------------ resistor
RS = {
    "value": "CRCW0805200RFKEAHP", "ohms": 200.0, "manufacturer": "Vishay Dale",
    "mpn": "CRCW0805200RFKEAHP", "lcsc": "C5972814",
    "digikey": "541-CRCW0805200RFKEAHPCT-ND",
    "datasheet": "https://www.vishay.com/docs/20043/crcwhpe3.pdf",
    "lcsc_stock": 2477, "lcsc_checked": "2026-09-25 (JLC parts API, JLC Extended)",
    "decision": "CRCW0805200RFKEAHP (LCSC C5972814, JLC Extended): pulse-proof 0805, kept from rev A; no JLC Basic "
                "200 R with a documented ~1 W / 1 ms pulse rating was substituted",
}

# ------------------------------------------------------------------ driver (research/electrical-j6.md)
DRIVER = {"i_nom": 0.0133, "i_max": 0.01396, "ovp_min": 24.25, "ceiling": 22.0, "open_min": 6.5,
          "v_sense": 0.206, "v_fet": 0.14,          # R37 sense + Q5/Q6 drop at 13.96 mA (electrical-j6.md sec 3b)
          "monit_ratio": 0.1071, "monit_open": (2.60, 2.73),
          "t_cold": -10.0, "vf_tc": -0.003,
          # hot-plug peak with C9 charged to OVP into the string (review-electrical model):
          #   I = (V_C9 - N x V0 - V_D) / (R37 15 + 2 + Rs + N x 5.3 R); rev B has no series diode -> V_D = 0
          "hp_vc9": {"TPS923610": 25.5, "TPS923611": 31.4}, "hp_r_fixed": 15.0 + 2.0, "hp_rd_led": 5.3,
          "hp_v0": (2.54, 2.81), "hp_vd": 0.0}

# ------------------------------------------------------------------ placement (E)
R_ZONE = (43.50, 52.50, -4.80, -0.40)        # R1/R2 sit in the J6 opening, below the floor window
J6_OPENING = (42.582, 58.922, -5.415, 0.215)
LED_BAND = (-9.0, 99.0, 8.00, 11.00)
PARTS_E = {
    # ref: (X, Z, KiCad rotation); rot 0 = pad 1 at -X
    "R1": (45.50, -3.60, 0),     # warm return (pad 1 <- D5, pad 2 -> W- / J1-6)
    "R2": (49.00, -1.40, 0),     # cool return (pad 1 <- D10, pad 2 -> C- / J2-11)
}
PART_HEIGHT = {"LED": 0.70, "R": 0.60, "HDR": HDR["body_h"]}
INSIDE = {"LED": ("LED band z 8.0..11.0", LED_BAND), "R": ("J6-opening R zone", R_ZONE),
          "HDR": ("J6 opening", J6_OPENING)}

# ------------------------------------------------------------------ keep-outs for parts (E rectangles x0,x1,z0,z1)
# "no parts anywhere over the case top (x 0.5..59.5, z -5.2..5.2) except inside the J6 opening"
KEEPOUTS = [
    ("case top, -X of the J6 opening", 0.5, 42.582, -5.2, 5.2),
    ("case top, +X of the J6 opening", 58.922, 59.5, -5.2, 5.2),
    ("case top, +Z of the J6 opening", 42.582, 58.922, 0.215, 5.2),
]
HEIGHT_ZONES = [
    # (name, x0, x1, z0, z1, max height, only this part kind or None)
    ("R zone (floor window)", 43.5, 52.5, -4.8, -0.4, 0.70, None),
]

# ------------------------------------------------------------------ routing (K frame)
ROUTE = {
    "w_row": 0.25,               # links along the LED row
    "w_bus": 0.40,               # everything else
    "y_warm_link": 91.75,        # z 8.25: warm links below the row
    "y_cool_link": 89.55,        # z 10.45: cool links (and the D1-D6 anode bridge) above the row
    "y_sw_via": 92.60,           # z 7.40: LED_SW via under D1's anode; B.Cu bus along this line
    "x_sw_down": 152.122,        # X 52.122: B.Cu bus turns toward J1-5 here (2.54 above J6-4)
    "y_sw_turn": 101.27,         # z -1.27: then 45 deg into J1-5 between J2-11 and J6-4
    "y_w_ret": 93.50,            # z 6.50: warm return D5 -> R1 (F.Cu)
    "y_c_ret": 94.50,            # z 5.50: cool return D10 -> R2 (F.Cu)
    "y_wminus": 105.40,          # z -5.40: W- R1 -> J1-6 from below (F.Cu)
}

# ------------------------------------------------------------------ rules (JLC standard 2-layer)
RULES = {
    "clearance": 0.20, "track_min": 0.20, "via_pad": 0.60, "via_drill": 0.30, "edge_clearance": 0.30,
    "hole_clearance": 0.40, "hole_to_hole": 0.50, "silk_text_h": 1.00, "silk_line_w": 0.15,
    "mask_expansion": 0.05, "min_annular": 0.13,
}
BOARD = {"layers": 2, "thickness": 1.0, "mask": "Black (any colour is fine)", "silk": "White",
         "finish": "LF-HASL or ENIG", "copper_oz": 1}

# ------------------------------------------------------------------ deviations (reported in docs)
DEVIATIONS = [
    "STEP frame: kicad-cli 9.0.6 writes the bare dielectric slab (0.91) at z_s 0..0.91 and seats F-side models on the "
    "component plane z_F (~0.995). make_outputs calibrates z_F on the J1 body box and maps Y = 116.60 - (z_s - z_F), "
    "X = x_s - 100, Z = 100 + y_s (+90 deg about X, det +1). Header tips are asserted at the geometry.json values; the "
    "slab in the E-frame STEP is ~0.09 thinner than 1.0 (copper + mask not modelled). Use build/geometry.json for fit.",
    "LED silk cathode mark = two short bars along the long sides over pad 1 (a bar across the end would sit in the "
    "0.43 gap of a warm/cool pair). LED courtyard = pads + 0.195 so the 3.8 mm pair pitch leaves 0.04.",
    "Header courtyards = the modelled bodies (2.50 wide per row), so J1 and J2 sit 0.04 apart; the F-side silk is one "
    "L-shaped outline around both bodies drawn on the board, not in the footprints.",
    "Part keep-outs (case top except the J6 opening, LED band, R zone, boss holes +0.4) are enforced by "
    "tools/check_handedness.py (courtyard boxes), not by KiCad rule areas.",
    "Header pin section 0.64 square and body width 2.50 are assumed (standard for the HC-PZ254 style; the LCSC page "
    "lists body 2.5 / post 6 / tail 3 but no drawing numbers were readable).",
    "Fab outputs (Gerber X2 dates, STEP, PDFs) carry timestamps; the generated KiCad sources are deterministic.",
]
