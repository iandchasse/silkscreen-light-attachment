"""Generate the silkscreen-light-attachment KiCad 9 project (rev B) from tools/params.py.

Run with KiCad's bundled Python (it needs pcbnew), with KiCad closed:

    "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" tools\\generate.py

Environment: KICAD9_DIR (KiCad install, default C:\\Program Files\\KiCad\\9.0), CQ_PYTHON (a python with
CadQuery for the STEP models; default: the enclosure project's .venv).

Writes, in order:
  lib/<name>.pretty       footprints (Hongli 3014 LED, J1 1x2 / J2 1x1 J6 plug headers, NPTH 4.80, stock R_0805 copy)
  lib/<name>.3dshapes     STEP models (LED + headers built with CadQuery, stock R_0805 copied)
  lib/<name>.kicad_sym    symbols (LED and R from KiCad stock; the two plug headers written here)
  <name>.kicad_sch        schematic
  <name>.kicad_pro, fp-lib-table, sym-lib-table, <name>.kicad_dru
  <name>.kicad_pcb        placed and routed board (built from the schematic's own netlist)
Every write is atomic (temp file + replace); refuses to run while KiCad holds a lock file.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402
from kigeom import uid, q, f  # noqa: E402

ROOT = os.path.dirname(HERE)
NAME = P.PROJECT
LIBNAME = NAME
LIBDIR = os.path.join(ROOT, "lib")
PRETTY = os.path.join(LIBDIR, NAME + ".pretty")
SHAPES = os.path.join(LIBDIR, NAME + ".3dshapes")
SYMLIB = os.path.join(LIBDIR, NAME + ".kicad_sym")
SCH = os.path.join(ROOT, NAME + ".kicad_sch")
PCB = os.path.join(ROOT, NAME + ".kicad_pcb")
PRO = os.path.join(ROOT, NAME + ".kicad_pro")
KICAD = os.environ.get("KICAD9_DIR", r"C:\Program Files\KiCad\9.0")
KICAD_CLI = os.environ.get("KICAD_CLI", os.path.join(KICAD, "bin", "kicad-cli.exe"))
if not os.path.exists(KICAD_CLI):
    KICAD_CLI = shutil.which("kicad-cli") or KICAD_CLI
STOCK_SYM = os.path.join(KICAD, "share", "kicad", "symbols")
STOCK_FP = os.path.join(KICAD, "share", "kicad", "footprints")
STOCK_3D = os.path.join(KICAD, "share", "kicad", "3dmodels")
CQ_PYTHON = os.environ.get("CQ_PYTHON", os.path.normpath(os.path.join(
    ROOT, "..", "..", "silkscreen-enclosure-claude", ".venv", "Scripts", "python.exe")))
TEMPLATE_PRO = os.path.join(HERE, "template.kicad_pro")
MODEL = "${KIPRJMOD}/lib/" + NAME + ".3dshapes/"


def refuse_if_open(root=ROOT):
    locks = glob.glob(os.path.join(root, "~*.lck")) + glob.glob(os.path.join(root, "*.lck"))
    if locks:
        sys.exit(f"KiCad has this project open ({', '.join(os.path.basename(x) for x in locks)}). "
                 "Close it first, or your next save would overwrite the generated files.")


def write_text(path, text):
    """Atomic write with LF line ends."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


# =====================================================================================
# footprints
# =====================================================================================
FP_LED = "LED_3014_HONGLI_HL-A-3014H421W"
FP_HDR = {"J1": "J6_PLUG_1x2_P5_P6", "J2": "J6_PLUG_1x1_P11"}
FP_R = "R_0805_2012Metric"
FP_NPTH = {4.80: "NPTH_4.80mm"}
STEP_LED = "LED_3014_HONGLI_HL-A-3014H421W.step"
STEP_HDR = {"J1": "J6_PLUG_1x2_HC-PZ254-11.5L.step", "J2": "J6_PLUG_1x1_HC-PZ254-11.5L.step"}
STEP_R = "R_0805_2012Metric.step"

L = P.LED
PAD1_W, PAD_H = L["pad1"]
PAD2_W = L["pad2"][0]
LAND = PAD1_W + L["gap"] + PAD2_W            # 3.37 overall
PAD1_X = -LAND / 2 + PAD1_W / 2              # -0.73: pad 1 (cathode) at -x at 0 deg
PAD2_X = LAND / 2 - PAD2_W / 2               # +1.23
LED_CRT = (LAND / 2 + 0.195, 0.95)           # half-extents; 3.8 mm pair pitch leaves 0.04 between courtyards


def fp_header(name, descr, tags, attr, ref_layer="F.SilkS", ref_hide=True):
    hide = " (hide yes)" if ref_hide else ""
    return [f'(footprint {q(name)}', '\t(version 20241229)', f'\t(generator {q(NAME)})',
            '\t(generator_version "9.0")', '\t(layer "F.Cu")', f'\t(descr {q(descr)})', f'\t(tags {q(tags)})',
            f'\t(property "Reference" "REF**" (at 0 -2 0) (layer {q(ref_layer)}){hide} (uuid {q(uid(name, "ref"))}) '
            '(effects (font (size 1 1) (thickness 0.15))))',
            f'\t(property "Value" {q(name)} (at 0 2 0) (layer "F.Fab") (hide yes) (uuid {q(uid(name, "val"))}) '
            '(effects (font (size 0.5 0.5) (thickness 0.08))))',
            f'\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid {q(uid(name, "ds"))}) '
            '(effects (font (size 1 1) (thickness 0.15))))',
            f'\t(property "Description" {q(descr)} (at 0 0 0) (layer "F.Fab") (hide yes) (uuid {q(uid(name, "de"))}) '
            '(effects (font (size 1 1) (thickness 0.15))))',
            f'\t(attr {attr})']


def g_line(a, b, layer, w, name, i):
    return (f'\t(fp_line (start {f(a[0])} {f(a[1])}) (end {f(b[0])} {f(b[1])}) '
            f'(stroke (width {f(w)}) (type solid)) (layer {q(layer)}) (uuid {q(uid(name, layer, i))}))')


def g_rect(a, b, layer, w, name, i, fill=False):
    return (f'\t(fp_rect (start {f(a[0])} {f(a[1])}) (end {f(b[0])} {f(b[1])}) '
            f'(stroke (width {f(w)}) (type solid)) (fill {"yes" if fill else "no"}) (layer {q(layer)}) '
            f'(uuid {q(uid(name, layer, "r", i))}))')


def g_circle(c, r, layer, w, name, i):
    return (f'\t(fp_circle (center {f(c[0])} {f(c[1])}) (end {f(c[0] + r)} {f(c[1])}) '
            f'(stroke (width {f(w)}) (type solid)) (fill no) (layer {q(layer)}) (uuid {q(uid(name, layer, "c", i))}))')


def g_poly(pts, layer, w, name, i):
    xy = " ".join(f"(xy {f(x)} {f(y)})" for x, y in pts)
    return (f'\t(fp_poly (pts {xy}) (stroke (width {f(w)}) (type solid)) (fill no) (layer {q(layer)}) '
            f'(uuid {q(uid(name, layer, "p", i))}))')


def g_text(txt, at, layer, h, name, i, w=None):
    w = w if w is not None else max(0.08, h * 0.15)
    return (f'\t(fp_text user {q(txt)} (at {f(at[0])} {f(at[1])} 0) (layer {q(layer)}) '
            f'(uuid {q(uid(name, "t", i))}) (effects (font (size {f(h)} {f(h)}) (thickness {f(w)}))))')


def model(fname):
    return (f'\t(model {q(MODEL + fname)} (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')


def write_led_fp():
    """Hongli HL-A-3014H421W-S1-08HL-HR3 top-view 3014 LED.

    Land pattern: datasheet B-17-A-1548 rev A/3 p.2 'Recommended Soldering Pattern' - pad 1 1.91 x 0.92,
    pad 2 0.91 x 0.92, gap 0.55 (3.37 overall), centred on the 3.00 x 1.40 body.  Pad 1 = CATHODE.  Pad 1 is at
    -x at 0 deg, the same as the EasyEDA footprint (C210340), so the JLC CPL offset is 0.
    """
    n = FP_LED
    bl, bw = L["body"][0] / 2, L["body"][1] / 2
    cl, cw = L["cavity"][0] / 2, L["cavity"][1] / 2
    out = fp_header(n, "HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3 top-view LED 3.0x1.4x0.7 mm; pad 1 = cathode (large pad); "
                    "land pattern per datasheet B-17-A-1548 p.2 (1.91x0.92 / 0.91x0.92, gap 0.55)",
                    "LED 3014 PLCC-2 top view", "smd")
    out.append(f'\t(pad "1" smd rect (at {f(PAD1_X)} 0) (size {f(PAD1_W)} {f(PAD_H)}) '
               f'(layers "F.Cu" "F.Paste" "F.Mask") (uuid {q(uid(n, "pad", 1))}))')
    out.append(f'\t(pad "2" smd rect (at {f(PAD2_X)} 0) (size {f(PAD2_W)} {f(PAD_H)}) '
               f'(layers "F.Cu" "F.Paste" "F.Mask") (uuid {q(uid(n, "pad", 2))}))')
    ch = 0.30
    out.append(g_poly([(-bl + ch, -bw), (bl, -bw), (bl, bw), (-bl, bw), (-bl, -bw + ch)], "F.Fab", 0.05, n, 0))
    out.append(g_rect((-cl, -cw), (cl, cw), "F.Fab", 0.05, n, 1))
    out.append(g_text("K", (PAD1_X - 0.35, 0), "F.Fab", 0.5, n, 2))
    out.append(g_text("A", (PAD2_X, 0), "F.Fab", 0.5, n, 3))
    out.append(g_text("${REFERENCE}", (0.3, 0), "F.Fab", 0.4, n, 4))
    ys = LED_CRT[1] - 0.10
    x0, x1 = -LAND / 2 + 0.05, PAD1_X + PAD1_W / 2 - 0.35
    out.append(g_line((x0, -ys), (x1, -ys), "F.SilkS", 0.15, n, 5))
    out.append(g_line((x0, ys), (x1, ys), "F.SilkS", 0.15, n, 6))
    out.append(g_rect((-LED_CRT[0], -LED_CRT[1]), (LED_CRT[0], LED_CRT[1]), "F.CrtYd", 0.05, n, 7))
    out.append(model(STEP_LED))
    out.append(')')
    return n, "\n".join(out) + "\n"


def hdr_pad_offsets(ref):
    """K-frame offsets of a header's pads from its footprint origin (body centre, 0 deg)."""
    cx, cz = P.header_centre(ref)
    return {nm: (round(X - cx, 4), round(-(Z - cz), 4)) for nm, (X, Z) in P.HEADERS[ref]["pads"].items()}


def write_hdr_fp(ref):
    """Standard 2.54 mm straight male header, body on F (the underside), pads NAMED by the J6 pin they mate.

    Origin = body centre.  Courtyard = fab = the modelled body (positions x 2.54 long, 2.50 wide).  No silk here:
    one L-shaped outline around J1 + J2 is drawn on the board (the bodies sit 0.04 apart).
    """
    n = FP_HDR[ref]
    H = P.HEADERS[ref]
    bx0, bx1, bz0, bz1 = P.header_body(ref)
    hx, hz = (bx1 - bx0) / 2, (bz1 - bz0) / 2
    pins = ", ".join(f"{nm} {P.PLUG['nets'][nm]}" for nm in H["pads"])
    out = fp_header(n, f"1x{H['positions']} 2.54 mm straight male header ({H['mpn']}) plugging into main-board J6; pads "
                    f"named by the mating J6 pin: {pins}", "pin header 2.54 J6 plug", "through_hole")
    for nm, (dx, dy) in hdr_pad_offsets(ref).items():
        shape = "rect" if nm == "5" else "circle"
        out.append(f'\t(pad {q(nm)} thru_hole {shape} (at {f(dx)} {f(dy)}) (size {f(P.HDR["pad"])} {f(P.HDR["pad"])}) '
                   f'(drill {f(P.HDR["drill"])}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) '
                   f'(uuid {q(uid(n, "pad", nm))}))')
        out.append(g_text(nm, (dx, dy), "F.Fab", 0.6, n, "lbl" + nm))
    out.append(g_rect((-hx, -hz), (hx, hz), "F.Fab", 0.1, n, 0))
    out.append(g_text("${REFERENCE}", (0, hz - 0.35), "F.Fab", 0.4, n, 1))
    out.append(g_rect((-hx, -hz), (hx, hz), "F.CrtYd", 0.05, n, 2))
    out.append(model(STEP_HDR[ref]))
    out.append(')')
    return n, "\n".join(out) + "\n"


def write_npth_fp(d):
    n = FP_NPTH[d]
    margin = P.COLUMN_CRTYD
    out = fp_header(n, f"Non-plated hole {d:.2f} mm (courtyard = hole + {margin:.2f})", "NPTH hole mechanical",
                    "board_only exclude_from_pos_files exclude_from_bom")
    out.append(f'\t(pad "" np_thru_hole circle (at 0 0) (size {f(d)} {f(d)}) (drill {f(d)}) (layers "*.Cu" "*.Mask") '
               f'(uuid {q(uid(n, "pad"))}))')
    out.append(g_circle((0, 0), d / 2, "F.Fab", 0.05, n, 0))
    out.append(g_circle((0, 0), d / 2 + margin, "F.CrtYd", 0.05, n, 1))
    out.append(')')
    return n, "\n".join(out) + "\n"


def copy_stock_fp(lib, name, model_file, descr_note):
    src = open(os.path.join(STOCK_FP, lib + ".pretty", name + ".kicad_mod"), encoding="utf-8").read()
    src = re.sub(r'\(model "[^"]*"', f'(model {q(MODEL + model_file)}', src, count=1)
    w = P.RULES["silk_line_w"]

    def widen(m):
        blk = m.group(0)
        if '(layer "F.SilkS")' not in blk and '(layer "B.SilkS")' not in blk:
            return blk
        return re.sub(r'\(width ([0-9.]+)\)', lambda n: f'(width {f(max(float(n.group(1)), w))})', blk)
    src = re.sub(r'\(fp_(?:line|poly|arc|circle|rect)\b.*?\(layer "[^"]+"\)', widen, src, flags=re.S)
    src = re.sub(r'\(descr "([^"]*)"\)', lambda m: f'(descr {q(m.group(1) + " " + descr_note)})', src, count=1)
    src = re.sub(r'(\(property "Reference" "REF\*\*"\s*\(at [^)]*\)\s*\(layer "F.SilkS"\))',
                 r'\1\n\t\t(hide yes)', src, count=1)
    return name, src


def write_footprints():
    os.makedirs(PRETTY, exist_ok=True)
    os.makedirs(SHAPES, exist_ok=True)
    items = [write_led_fp(), write_hdr_fp("J1"), write_hdr_fp("J2"), write_npth_fp(4.80),
             copy_stock_fp("Resistor_SMD", FP_R, STEP_R, "(KiCad stock, copied into the project)")]
    keep = set()
    for name, text in items:
        write_text(os.path.join(PRETTY, name + ".kicad_mod"), text)
        keep.add(name + ".kicad_mod")
    for fn in os.listdir(PRETTY):                      # rev B: drop rev A leftovers (SOT-23, 3-pin plug, old NPTH)
        if fn not in keep:
            os.remove(os.path.join(PRETTY, fn))
    src = os.path.join(STOCK_3D, "Resistor_SMD.3dshapes", STEP_R)
    if not os.path.exists(src):
        sys.exit("stock 3D model missing: " + src)
    shutil.copyfile(src, os.path.join(SHAPES, STEP_R))
    models = {STEP_LED, STEP_R, "models.stamp"} | set(STEP_HDR.values())
    for fn in os.listdir(SHAPES):
        if fn not in models:
            os.remove(os.path.join(SHAPES, fn))
    # CadQuery/OCC writes assembly colours in a run-dependent order, so the models are rebuilt only when their
    # inputs change (stamp = hash of the model script + the LED/header parameters).
    import hashlib
    src = open(os.path.join(HERE, "make_step_models.py"), encoding="utf-8").read()
    stamp = hashlib.sha256((src + repr(P.LED) + repr(P.HDR) + repr(P.HEADERS) + P.DATE).encode()).hexdigest()
    stamp_file = os.path.join(SHAPES, "models.stamp")
    have = all(os.path.exists(os.path.join(SHAPES, fn)) for fn in [STEP_LED] + list(STEP_HDR.values()))
    if have and os.path.exists(stamp_file) and open(stamp_file).read().strip() == stamp:
        return
    if not os.path.exists(CQ_PYTHON):
        sys.exit("CadQuery python not found (set CQ_PYTHON): " + CQ_PYTHON)
    r = subprocess.run([CQ_PYTHON, os.path.join(HERE, "make_step_models.py"), "models", SHAPES],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("STEP model build failed:\n" + r.stdout + r.stderr)
    write_text(stamp_file, stamp + "\n")


# =====================================================================================
# symbols
# =====================================================================================
def extract_symbol(lib_file, name):
    text = open(os.path.join(STOCK_SYM, lib_file), encoding="utf-8").read()
    m = re.search(r'^\t\(symbol "' + re.escape(name) + r'"\n', text, re.M)
    if not m:
        raise KeyError(name)
    i = m.start()
    depth = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    raise ValueError("unbalanced")


def set_prop(block, prop, value):
    new, n = re.subn(r'(\(property "' + re.escape(prop) + r'" )"[^"]*"', lambda m: m.group(1) + q(value), block, count=1)
    if n != 1:
        raise KeyError(prop)
    return new


def rename_symbol(block, old, new):
    block = block.replace(f'(symbol "{old}"', f'(symbol "{new}"', 1)
    return re.sub(r'\(symbol "' + re.escape(old) + r'_(\d+_\d+)"', lambda m: f'(symbol "{new}_{m.group(1)}"', block)


def _prop(k, v, at=(0, 0), hide=True, justify=None):
    j = f"\n\t\t\t\t(justify {justify})" if justify else ""
    h = "\n\t\t\t\t(hide yes)" if hide else ""
    return (f'\t\t(property {q(k)} {q(v)}\n\t\t\t(at {f(at[0])} {f(at[1])} 0)\n\t\t\t(effects\n\t\t\t\t(font\n'
            f'\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t){j}{h}\n\t\t\t)\n\t\t)')


def _pin(num, name, at, ang, length):
    return (f'\t\t\t(pin passive line\n\t\t\t\t(at {f(at[0])} {f(at[1])} {ang})\n\t\t\t\t(length {f(length)})\n'
            f'\t\t\t\t(name {q(name)}\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n'
            f'\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t\t(number {q(num)}\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n'
            f'\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)')


SYM_HDR = {"J1": "J6_PLUG_1x2", "J2": "J6_PLUG_1x1"}


def plug_symbol(ref):
    """Header symbol: pins numbered by the J6 pin they mate; pin k at (5.08, -2.54 k)."""
    n = SYM_HDR[ref]
    H = P.HEADERS[ref]
    npos = H["positions"]
    y1 = -2.54 * (npos - 1) - 1.27
    rect = (f'\t\t\t(rectangle\n\t\t\t\t(start -5.08 1.27)\n\t\t\t\t(end 2.54 {f(y1)})\n\t\t\t\t(stroke\n'
            '\t\t\t\t\t(width 0.254)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n\t\t\t\t(fill\n\t\t\t\t\t(type background)\n'
            '\t\t\t\t)\n\t\t\t)')
    pins = [_pin(nm, P.PLUG["nets"][nm], (5.08, -2.54 * i), 180, 2.54) for i, nm in enumerate(H["pads"])]
    desc = (f"1x{npos} 2.54 mm male header into the main board J6; pins numbered by the J6 pin they mate ("
            + ", ".join(f"{nm} {P.PLUG['nets'][nm]}" for nm in H["pads"]) + ")")
    props = [_prop("Reference", "J", (-1.27, 3.81), False), _prop("Value", n, (-1.27, y1 - 2.54), False),
             _prop("Footprint", f"{LIBNAME}:{FP_HDR[ref]}"), _prop("Datasheet", H["datasheet"]),
             _prop("Description", desc), _prop("ki_keywords", "connector header J6"), _prop("ki_fp_filters", "J6_PLUG*")]
    return (f'\t(symbol {q(n)}\n\t\t(pin_names\n\t\t\t(offset 0.508)\n\t\t)\n\t\t(exclude_from_sim no)\n'
            f'\t\t(in_bom yes)\n\t\t(on_board yes)\n' + "\n".join(props) + f'\n\t\t(symbol "{n}_0_1"\n' + rect +
            f'\n\t\t)\n\t\t(symbol "{n}_1_1"\n' + "\n".join(pins) + '\n\t\t)\n\t\t(embedded_fonts no)\n\t)')


def build_symbols():
    syms = {}
    led = rename_symbol(extract_symbol("Device.kicad_sym", "LED"), "LED", "LED_3014")
    led = set_prop(led, "Footprint", f"{LIBNAME}:{FP_LED}")
    led = set_prop(led, "Description", "White LED, 3014 top view; pin 1 = K, pin 2 = A")
    syms["LED_3014"] = led
    r = extract_symbol("Device.kicad_sym", "R")
    r = set_prop(r, "Footprint", f"{LIBNAME}:{FP_R}")
    syms["R"] = r
    for ref in ("J1", "J2"):
        syms[SYM_HDR[ref]] = plug_symbol(ref)
    return syms


def write_symbol_lib(syms):
    write_text(SYMLIB, f'(kicad_symbol_lib\n\t(version 20241209)\n\t(generator {q(NAME)})\n\t(generator_version "9.0")\n'
               + "".join(s + "\n" for s in syms.values()) + ")\n")


# =====================================================================================
# schematic
# =====================================================================================
ROOT_UUID = uid("root-sheet")


class Sch:
    def __init__(self, syms):
        self.syms = syms
        self.items = []
        self.symbols = []
        self.n = 0

    def _u(self, *k):
        self.n += 1
        return uid("sch", self.n, *k)

    def wire(self, a, b):
        self.items.append(f'\t(wire (pts (xy {f(a[0])} {f(a[1])}) (xy {f(b[0])} {f(b[1])})) '
                          f'(stroke (width 0) (type default)) (uuid {q(self._u("w"))}))')

    def label(self, name, at, angle=0):
        just = "right bottom" if angle == 180 else "left bottom"
        self.items.append(f'\t(label {q(name)} (at {f(at[0])} {f(at[1])} {angle}) (fields_autoplaced yes) '
                          f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid {q(self._u("l"))}))')

    def text(self, s, at, size=1.27):
        self.items.append(f'\t(text {q(s)} (exclude_from_sim no) (at {f(at[0])} {f(at[1])} 0) '
                          f'(effects (font (size {f(size)} {f(size)})) (justify left top)) (uuid {q(self._u("t"))}))')

    def symbol(self, lib, ref, at, rot=0, fields=None, pins=(), ref_at=None, val_at=None, hide_value=False, fangle=0):
        u = uid("sym", ref)
        fields = dict(fields or {})
        props = [("Reference", ref, ref_at or (at[0], at[1] - 3.81), False),
                 ("Value", fields.pop("Value"), val_at or (at[0], at[1] + 3.81), hide_value)]
        for k, v in fields.items():
            props.append((k, v, at, True))
        lines = [f'\t(symbol (lib_id {q(LIBNAME + ":" + lib)}) (at {f(at[0])} {f(at[1])} {rot}) (unit 1)',
                 f'\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid {q(u)})']
        for k, v, pos, hidden in props:
            ang = fangle if k in ("Reference", "Value") else 0
            lines.append(f'\t\t(property {q(k)} {q(v)} (at {f(pos[0])} {f(pos[1])} {ang}) '
                         f'(effects (font (size 1.27 1.27))' + (' (hide yes)' if hidden else '') + '))')
        for p in pins:
            lines.append(f'\t\t(pin {q(p)} (uuid {q(uid("pin", ref, p))}))')
        lines.append(f'\t\t(instances (project {q(NAME)} (path {q("/" + ROOT_UUID)} (reference {q(ref)}) (unit 1))))')
        lines.append('\t)')
        self.symbols.append("\n".join(lines))
        return u

    def write(self, path):
        head = ['(kicad_sch', '\t(version 20250114)', '\t(generator "eeschema")', '\t(generator_version "9.0")',
                f'\t(uuid {q(ROOT_UUID)})', '\t(paper "A4")',
                '\t(title_block', f'\t\t(title {q(P.TITLE)})', f'\t\t(date {q(P.DATE)})',
                f'\t\t(rev {q(P.REVISION)})', f'\t\t(company {q(P.COMPANY)})',
                '\t\t(comment 1 "Snap-on warm/cool reading light for the Silkscreen reader; plugs into main-board J6")',
                '\t\t(comment 2 "Licensed under CERN-OHL-S-2.0")', '\t\t(comment 3 "(c) 2026 idc LLC")',
                '\t\t(comment 4 "Generated by pcb/tools/generate.py - do not edit")', '\t)', '\t(lib_symbols']
        for name, s in self.syms.items():
            s = s.replace(f'(symbol "{name}"', f'(symbol "{LIBNAME}:{name}"', 1)
            head.append("\t" + s.replace("\n", "\n\t"))
        head.append('\t)')
        body = head + self.items + self.symbols + ['\t(sheet_instances (path "/" (page "1")))',
                                                   '\t(embedded_fonts no)', ')']
        write_text(path, "\n".join(body) + "\n")


ASM_SMT = "JLC SMT (F side)"
ASM_HAND = "hand-solder (builder)"


def part_fields(kind, colour=None, ref=None):
    if kind == "LED":
        c = L[colour]
        return {"Value": L["mpn"], "Footprint": f"{LIBNAME}:{FP_LED}", "Datasheet": L["datasheet"],
                "Description": (f"{colour.capitalize()} white LED {c['cct']} (bin {c['bin']}), LCSC {c['lcsc']}; "
                                "3014 top view 3.0x1.4x0.7; the MPN is shared by every CCT - order by the LCSC code"),
                "Manufacturer": L["manufacturer"], "MPN": L["mpn"], "DigiKey": L["digikey"], "LCSC": c["lcsc"],
                "CCT": c["cct"], "Assembly": ASM_SMT}
    if kind == "R":
        r = P.RS
        return {"Value": r["value"], "Footprint": f"{LIBNAME}:{FP_R}", "Datasheet": r["datasheet"],
                "Description": f"{r['ohms']:.0f} R 1 % 0.5 W pulse-proof thick film 0805 (CRCW-HP); string series resistor",
                "Manufacturer": r["manufacturer"], "MPN": r["mpn"], "DigiKey": r["digikey"], "LCSC": r["lcsc"],
                "Assembly": ASM_SMT}
    if kind == "J":
        h = P.HEADERS[ref]
        d = P.HDR
        return {"Value": h["mpn"], "Footprint": f"{LIBNAME}:{FP_HDR[ref]}", "Datasheet": h["datasheet"],
                "Description": (f"1x{h['positions']} 2.54 mm straight male pin header, body {d['body_h']:.1f}, mating post "
                                f"{d['post']:.1f}, tail {d['tail']:.1f}, {d['post_sq']:.2f} sq; body on the LED side, "
                                "soldered by the builder on the plain side; pins = J6 " + "/".join(h["pads"])),
                "Manufacturer": h["manufacturer"], "MPN": h["mpn"], "DigiKey": h["digikey"], "LCSC": h["lcsc"],
                "Assembly": ASM_HAND}
    raise KeyError(kind)


def build_schematic(syms):
    s = Sch(syms)
    # ---------------- J1 / J2 ----------------
    for ref, jy in (("J1", 60.96), ("J2", 76.20)):
        jx = 30.48
        H = P.HEADERS[ref]
        s.symbol(SYM_HDR[ref], ref, (jx, jy), 0, part_fields("J", ref=ref), pins=list(H["pads"]),
                 ref_at=(jx - 1.27, jy - 3.81), val_at=(jx - 1.27, jy + 2.54 * H["positions"] + 1.27))
        for i, nm in enumerate(H["pads"]):
            a = (jx + 5.08, jy + 2.54 * i)
            b = (jx + 12.7, jy + 2.54 * i)
            s.wire(a, b)
            s.label(P.PLUG["nets"][nm], b)

    # ---------------- strings ----------------
    def string(colour, y, r_ref, ret, prefix):
        refs = L[colour]["refs"]
        x0, pitch = 63.5, 20.32
        s.wire((x0 - 3.81 - 5.08, y), (x0 - 3.81, y))
        s.label("LED_SW", (x0 - 3.81 - 5.08, y))
        for i, ref in enumerate(refs):
            x = x0 + i * pitch
            s.symbol("LED_3014", ref, (x, y), 180, part_fields("LED", colour), pins=["1", "2"],
                     ref_at=(x, y - 5.08), val_at=(x, y + 3.81), hide_value=True)
            if i < len(refs) - 1:
                s.wire((x + 3.81, y), (x + pitch - 3.81, y))
                s.label(f"{prefix}_K{i + 1}", (x + 3.81 + 2.54, y))
        c = L[colour]
        s.text(f"{refs[0]}-{refs[-1]}: {L['mpn']} {c['cct']}, LCSC {c['lcsc']} (Value hidden: same MPN for every CCT)",
               (x0 - 5.08, y + 6.35), 1.27)
        xk = x0 + 4 * pitch + 3.81                 # last cathode
        rx = xk + 8.89                             # R centre (rot 90: pin 1 left, pin 2 right)
        s.wire((xk, y), (rx - 3.81, y))
        s.label(f"{prefix}_R", (xk + 1.27, y))
        s.symbol("R", r_ref, (rx, y), 90, part_fields("R"), pins=["1", "2"], ref_at=(rx, y - 3.81),
                 val_at=(rx, y + 3.81), fangle=90)
        s.wire((rx + 3.81, y), (rx + 11.43, y))
        s.label(ret, (rx + 11.43, y))

    string("warm", 50.8, "R1", "W-", "W")
    string("cool", 96.52, "R2", "C-", "C")

    # ---------------- notes ----------------
    import report_design as RD
    sv = RD.string_numbers()
    eg = RD.engagement()
    notes = [
        "HOW IT CONNECTS (rev B, simple)",
        "J1 (1x2) and J2 (1x1) are standard 2.54 mm straight male headers, hand-soldered by the builder (3 joints).",
        "Pins are numbered by the J6 pin they mate: 5 = LED_SW (anode bus), 6 = W- (warm return), 11 = C- (cool return).",
        "Every other J6 position (incl. J6-12 P+_FUSE and J6-4 GND) has NO pin and no hole on this board.",
        f"Header: body {P.HDR['body_h']:.1f} / post {P.HDR['post']:.1f} / tail {P.HDR['tail']:.1f}; post tips at "
        f"Y {P.STACK['post_tip_y']:.2f} -> J6 engagement {eg['min']:.2f}..{eg['max']:.2f} mm.",
        "",
        f"EACH STRING: LED_SW -> 5 LEDs -> Rs {P.RS['ohms']:.0f} R ({P.RS['mpn']}) -> W-/C-. No series diode (rev B):",
        "the housing keys the plug; with 200 R the main board is safe in every misinsertion (research/electrical-j6.md sec 5).",
        f"Driver: constant current {P.DRIVER['i_nom'] * 1e3:.1f} mA ({P.DRIVER['i_max'] * 1e3:.1f} max), one string at a time; "
        f"OVP {P.DRIVER['ovp_min']} V min; design ceiling {P.DRIVER['ceiling']} V.",
        f"String at 13.3 mA: 5 x Vf {sv['n_vf_min']:.1f}..{sv['n_vf_max']:.1f} V + Rs {sv['v_rs']:.2f} V = LED_SW "
        f"{sv['v_min']:.1f}..{sv['v_max']:.1f} V (typ {sv['v_typ']:.1f} V, incl. sense + FET) < {P.DRIVER['ceiling']} V.",
        f"Hot-plug peak through Rs {P.RS['ohms']:.0f} R: TPS923610 {sv['ipk_610'][0] * 1e3:.0f}..{sv['ipk_610'][1] * 1e3:.0f} mA, "
        f"TPS923611 {sv['ipk_611'][0] * 1e3:.0f}..{sv['ipk_611'][1] * 1e3:.0f} mA < IFP {L['ifp'] * 1e3:.0f} mA.",
        "",
        "LEDs: HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3; the MPN does not encode CCT: warm D1-D5 = LCSC C210340 (3000 K),",
        "cool D6-D10 = LCSC C210343 (6000 K). Pad 1 (large) = cathode. Do not plug the bare board into J6 (no housing = no key).",
    ]
    s.text("\n".join(notes), (20.32, 116.84), 1.27)
    s.write(SCH)
    return s


# =====================================================================================
# project files
# =====================================================================================
def write_project_files():
    write_text(os.path.join(ROOT, "fp-lib-table"),
               f'(fp_lib_table\n\t(version 7)\n\t(lib (name {q(LIBNAME)})(type "KiCad")'
               f'(uri "${{KIPRJMOD}}/lib/{NAME}.pretty")(options "")(descr "Light attachment footprints (generated)"))\n)\n')
    write_text(os.path.join(ROOT, "sym-lib-table"),
               f'(sym_lib_table\n\t(version 7)\n\t(lib (name {q(LIBNAME)})(type "KiCad")'
               f'(uri "${{KIPRJMOD}}/lib/{NAME}.kicad_sym")(options "")(descr "Light attachment symbols (generated)"))\n)\n')
    pro = json.load(open(TEMPLATE_PRO, encoding="utf-8"))
    ds = pro["board"]["design_settings"]
    ds["drc_exclusions"] = []
    R = P.RULES
    ds["rules"].update({
        "min_clearance": R["clearance"], "min_copper_edge_clearance": R["edge_clearance"],
        "min_track_width": R["track_min"], "min_via_diameter": R["via_pad"],
        "min_through_hole_diameter": R["via_drill"], "min_via_annular_width": R["min_annular"],
        "min_hole_clearance": R["hole_clearance"], "min_hole_to_hole": R["hole_to_hole"],
        "min_text_height": R["silk_text_h"], "min_text_thickness": R["silk_line_w"], "min_silk_clearance": 0.0,
        "solder_mask_to_copper_clearance": 0.0,
    })
    ds["track_widths"] = [0.0, P.ROUTE["w_row"], P.ROUTE["w_bus"]]
    ds["via_dimensions"] = [{"diameter": 0.0, "drill": 0.0}, {"diameter": R["via_pad"], "drill": R["via_drill"]}]
    ds["defaults"]["board_outline_line_width"] = 0.05
    ds["defaults"]["silk_line_width"] = R["silk_line_w"]
    ds["defaults"]["silk_text_size_h"] = 1.0
    ds["defaults"]["silk_text_size_v"] = 1.0
    ds["defaults"]["silk_text_thickness"] = R["silk_line_w"]
    sev = ds.setdefault("rule_severities", {})
    for k, v in list(sev.items()):          # nothing ignored
        if v == "ignore":
            sev[k] = "warning"
    sev.update({"courtyards_overlap": "error", "copper_edge_clearance": "error", "solder_mask_bridge": "error",
                "missing_courtyard": "error", "hole_clearance": "error", "hole_to_hole": "error",
                "silk_over_copper": "warning", "npth_inside_courtyard": "error", "pth_inside_courtyard": "error"})
    erc = pro.setdefault("erc", {})
    erc["erc_exclusions"] = []
    for k, v in list(erc.get("rule_severities", {}).items()):
        if v == "ignore":
            erc["rule_severities"][k] = "warning"
    ns = pro["net_settings"]
    base = ns["classes"][0]
    base.update({"clearance": R["clearance"], "track_width": P.ROUTE["w_row"], "via_diameter": R["via_pad"],
                 "via_drill": R["via_drill"]})
    ns["classes"] = [base]
    ns["netclass_assignments"] = None
    ns["netclass_patterns"] = []
    pro["meta"]["filename"] = NAME + ".kicad_pro"
    pro["sheets"] = [[ROOT_UUID, "Root"]]
    pro["text_variables"] = {}
    pro["boards"] = []
    pro["libraries"] = {"pinned_footprint_libs": [], "pinned_symbol_libs": []}
    pro["pcbnew"] = {"last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "production/gerbers/",
                                    "pos_files": "production/", "specctra_dsn": "", "step": "production/3d/",
                                    "svg": "", "vrml": ""}, "page_layout_descr_file": ""}
    write_text(PRO, json.dumps(pro, indent=2) + "\n")
    dru = """(version 1)

# Keep traces 0.5 mm off the NPTH boss holes (all other copper keeps the board-wide 0.40 hole clearance).
(rule "trace_to_npth_0p5"
    (constraint hole_clearance (min 0.5mm))
    (condition "A.Type == 'Track' && B.Pad_Type == 'NPTH, mechanical'"))
"""
    write_text(os.path.join(ROOT, NAME + ".kicad_dru"), dru)


# =====================================================================================
# netlist from the schematic (so the PCB matches it exactly)
# =====================================================================================
def schematic_netlist():
    out = os.path.join(ROOT, "build", NAME + ".net")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, SCH],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("netlist export failed:\n" + r.stdout + r.stderr)
    text = open(out, encoding="utf-8").read()
    padnet = {}
    for blk in re.split(r'\n\s*\(net ', text)[1:]:
        nm = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', blk).group(1)
        for ref, pad in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk):
            padnet[(ref, pad)] = nm
    comps = {}
    comp_text = text.split("(libparts", 1)[0]
    for blk in re.split(r'\n\s*\(comp ', comp_text)[1:]:
        ref = re.search(r'\(ref "([^"]+)"\)', blk).group(1)
        val = re.search(r'\(value "((?:[^"\\]|\\.)*)"\)', blk).group(1)
        fpn = re.search(r'\(footprint "([^"]+)"\)', blk)
        fields = dict(re.findall(r'\(field \(name "([^"]+)"\) "((?:[^"\\]|\\.)*)"\)', blk))
        dnp = bool(re.search(r'\(property \(name "dnp"\)', blk))
        comps[ref] = {"value": val, "footprint": fpn.group(1) if fpn else "", "fields": fields, "dnp": dnp}
    want = sorted(L["warm"]["refs"] + L["cool"]["refs"] + list(P.PARTS_E) + list(P.HEADERS))
    if sorted(comps) != want or any(c["dnp"] for c in comps.values()):
        sys.exit(f"netlist parts {sorted(comps)} (want {want}, none DNP)")
    return padnet, comps


def main():
    refuse_if_open()
    write_footprints()
    syms = build_symbols()
    write_symbol_lib(syms)
    build_schematic(syms)
    write_project_files()
    padnet, comps = schematic_netlist()
    import build_pcb   # noqa: E402  (needs pcbnew)
    build_pcb.build(padnet, comps)
    write_project_files()          # again: nothing pcbnew saved may override the rules/severities
    prl = os.path.join(ROOT, NAME + ".kicad_prl")
    if os.path.exists(prl):
        os.remove(prl)
    print("generated", PCB)


if __name__ == "__main__":
    main()
