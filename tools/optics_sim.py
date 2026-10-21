"""Illumination model for a light bar on the TOP edge of the Silkscreen page.

Coordinates are the enclosure frame of silkscreen-enclosure-claude:
    X = KiCad X - 44.24,  Y = 148.25 - KiCad Y (+Y = the top edge, the J6 end),
    Z = 0 at the main PCB's rear face, +Z toward the viewer.

Model (geometry only)
---------------------
* Page: the active area (x 2.16..57.84, y 15.10..107.90) in the plane z = z_page, facing +Z.
* LED: a point source at (x, y, z) with an optical axis a (default -Y, i.e. down the page, tilted
  toward -Z by `tilt` degrees) and intensity I = cos^m(angle between the ray and a), zero behind the
  emitter.  m comes from the full half-intensity angle (120 deg -> m = 1, 90 -> 2, 60 -> 4.8).
* Irradiance on the page: E = sum I * cos(incidence) / r^2, optionally times the Fresnel
  transmission of a glossy n = 1.5 film, counted only for rays that pass every occluder.
* Occluders are z-planes.  An Aperture is opaque except inside a rectangle: the front skin is three of
  them - the window at the lip underside (z 4.98, y <= 108.5), the bevel's corner (z 5.40, same
  rectangle) and the front face (z 6.00, 0.6 wider on every side: the 0.6 x 45 deg bevel).  A Plate is
  opaque inside a rectangle: the lip underside seen as a ceiling over y >= 108.5, or a visor.  A plane
  only matters when it lies strictly between the source and the page, so a source UNDER the lip (the
  internal variant) can never be shadowed by it - its rays only descend.  For internal sources the
  constraint is how high the emitter may sit (see internal_fit()), not occlusion.
* Not modelled: the LED body's size, scattering by a matte front film (it makes the far page look
  brighter than this predicts), reflections off the ceiling/visor, refraction down to the ink (<= 1 mm
  lateral shift through the FT01C stack).  The SHAPE of the gradient and the ranking of layouts hold.

Metrics (per string: warm alone; the cool string is its mirror image in every layout here)
---------------------------------------------------------------------------------------------
d = distance from the lit edge of the active area (the top edge: d = 107.90 - y).
  profile      x-mean over the middle 80 % of the width, as a function of d
  near/far     profile(d) / profile(far edge) at d = 2, 5, 10, 20, 40, 80
  nf_10_40     max(profile on 10..40 mm) / profile(far edge)   (the "is the middle washed out" number)
  pk_2         max(profile beyond 2 mm) / profile(far edge)    (brightest visible band vs the bottom)
  lux_*_per_lm lux at the far edge / half way per lumen emitted by each LED of the string
  vs_mid       profile(d) / profile(half way down)
  band         shadowed band at the top: first d where the profile reaches 5 % of its maximum
               (band_col: the same per column, worst column over the full width)
  minmax       min/max over the whole page and over the lower 80 % of it
  scallop      max/min across x at d = 5, 10, 20, between the 2nd and the 2nd-last LED of the string
  ends_mid     both strings on, at d = 10: min(mean of the outer 10 % at each end) / mean of the middle 10 %
  mix          both strings on: max |warm share - 0.5| across x at d = 3, 10, 20
  flux         fraction of the string's emitted flux that lands on the active area

Run with any Python 3 with numpy + matplotlib (system python here):
    python tools/optics_sim.py                 full sweeps -> design/optics/*.json, *.png, tables on stdout
    python tools/optics_sim.py --quick         coarser grids, fewer points
    python tools/optics_sim.py --eval "kind=external,page=FT01C,z=10,y=112,tilt=20,layout=L5"
    python tools/optics_sim.py --eval "kind=internal,page=PLAIN,h=0.8,y=111,layout=L6,angle=90,fresnel=1"
    python tools/optics_sim.py --eval "kind=external,page=T01C,z=16,y=117.44,layout=L5-w12.5-s1.2,pattern=design/optics/rod_pattern_pick.json"
        (a tabulated source, e.g. the PMMA rod lens from tools/rod_lens.py; z, y = the emitter centre)
Import it for other studies: sources_internal(), sources_external(), evaluate(), layout().
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "design", "optics")

# ---- enclosure geometry (research/enclosure.md, research/mechanical-j6.md) -----------------------
ACTIVE = dict(x0=2.16, x1=57.84, y0=15.10, y1=107.90)          # hw.py:29-30
WIN = dict(x0=1.56, x1=58.44, y0=14.5, y1=108.5)               # window at the lip underside, tub.py:18-26
LIP_Z, BEVEL_Z, FACE_Z, BEVEL = 4.98, 5.40, 6.00, 0.60          # params.py:24-28; bevel corner (sect)
CASE = dict(x0=-4.09, x1=64.09, top=115.6)
FACE_FLAT_Y1 = 113.8                                            # flat front face ends, R1.8 round to 115.6
# Page (front) planes.  FT01C: pressed to the lip by the midplate springs.  The springs only take up
# +-0.2 (0.6 travel, 0.35 at nominal): a thinner panel is NOT pushed to the lip in the stock case, so
# PLAIN and T01C need stops like the light-strip copy's PANEL_STOPS, which hold the page at
# DISP_REAR + t (rear on the midplate at 3.0, springs loaded as for a nominal FT01C).
PANELS = {"FT01C": 4.98, "T01C": 3.0 + 1.41, "PLAIN": 3.0 + 0.926}
EMITTER_HALF = 0.40      # half the emitting height of a 0.8 mm tall side-view LED / 0603 top-view
CLEAR = 0.05             # emitter top to the ceiling
MIN_SKIN = 0.40          # 2 layers at 0.2 over a raised ceiling (the light strip left 0.70)


def exponent_for_full_angle(full_deg: float) -> float:
    """cos^m exponent whose half-intensity full angle is full_deg (120 deg -> m = 1)."""
    return math.log(0.5) / math.log(math.cos(math.radians(full_deg / 2.0)))


@dataclass
class Source:
    x: float
    y: float
    z: float
    axis: tuple = (0.0, -1.0, 0.0)
    m: float = 1.0
    colour: str = "W"
    pattern: object = None   # optional callable(ux, uy, uz) -> I / I0 (e.g. TabulatedPattern); overrides axis/m.
                             # Keep m = 1 with a pattern: evaluate() then normalises flux to a bare Lambertian LED.


class TabulatedPattern:
    """Radiant intensity I / I0 tabulated over (theta, s), where theta = atan2(-uz, -uy) in degrees is the
    elevation in the Y-Z plane (0 = -Y, down the page; + = toward the page, -Z, the same sign as `tilt`)
    and s = ux is the lateral direction cosine.  I0 is the on-axis intensity of the bare Lambertian LED
    (phi / pi), so a pattern that includes lens losses keeps evaluate()'s flux and lux-per-lm meaning.
    Written by tools/rod_lens.py (JSON: theta_deg, s, table[theta][s], dy, dz = source offset from the
    emitter centre).  Bilinear interpolation; zero outside the table."""

    def __init__(self, theta_deg, s, table, dy=0.0, dz=0.0, meta=None):
        self.th = np.asarray(theta_deg, float)
        self.s = np.asarray(s, float)
        self.t = np.asarray(table, float)
        self.dy, self.dz, self.meta = dy, dz, meta or {}

    @classmethod
    def load(cls, path):
        with open(path) as f:
            j = json.load(f)
        return cls(j["theta_deg"], j["s"], j["table"], j.get("dy", 0.0), j.get("dz", 0.0), j.get("meta"))

    def __call__(self, ux, uy, uz):
        th = np.degrees(np.arctan2(-uz, -uy))
        fi = np.interp(th, self.th, np.arange(len(self.th)), left=-1, right=-1)
        fj = np.interp(ux, self.s, np.arange(len(self.s)), left=-1, right=-1)
        ok = (fi >= 0) & (fj >= 0)
        i0 = np.clip(np.floor(fi).astype(int), 0, len(self.th) - 2)
        j0 = np.clip(np.floor(fj).astype(int), 0, len(self.s) - 2)
        a, b = fi - i0, fj - j0
        t = self.t
        v = (t[i0, j0] * (1 - a) * (1 - b) + t[i0 + 1, j0] * a * (1 - b)
             + t[i0, j0 + 1] * (1 - a) * b + t[i0 + 1, j0 + 1] * a * b)
        return np.where(ok, v, 0.0)


def axis_from(direction: str, tilt_deg: float) -> tuple:
    """Unit optical axis: 'down' = -Y (top-edge bar), 'right' = +X (left-edge strip), tilted toward -Z."""
    t = math.radians(tilt_deg)
    if direction == "down":
        return (0.0, -math.cos(t), -math.sin(t))
    return (math.cos(t), 0.0, -math.sin(t))


@dataclass
class Aperture:
    """Opaque plane z = const except inside the rectangle."""
    z: float
    x0: float
    x1: float
    y0: float
    y1: float
    keep_inside = True

    def passes(self, s, px, py, zp):
        return _crossing(self, s, px, py, zp)


@dataclass
class Plate(Aperture):
    """Opaque rectangle in the plane z = const (a ceiling, a visor)."""
    keep_inside = False


def _crossing(o, s, px, py, zp):
    dz = zp - s.z
    if dz == 0:
        return np.ones(np.shape(px), bool)
    t = (o.z - s.z) / dz
    if not (0.0 < t < 1.0):                      # plane not between the source and the page
        return np.ones(np.shape(px), bool)
    x = s.x + t * (px - s.x)
    y = s.y + t * (py - s.y)
    inside = (x >= o.x0) & (x <= o.x1) & (y >= o.y0) & (y <= o.y1)
    return inside if o.keep_inside else ~inside


def skin():
    """The front skin's window edge: lip underside, bevel corner, front face (0.6 wider)."""
    w = WIN
    return [Aperture(LIP_Z, w["x0"], w["x1"], w["y0"], w["y1"]),
            Aperture(BEVEL_Z, w["x0"], w["x1"], w["y0"], w["y1"]),
            Aperture(FACE_Z, w["x0"] - BEVEL, w["x1"] + BEVEL, w["y0"] - BEVEL, w["y1"] + BEVEL)]


def ceiling(z: float = LIP_Z):
    """The lip underside as a ceiling over the top border (y >= 108.5)."""
    return Plate(z, CASE["x0"], CASE["x1"], WIN["y1"], 1e3)


def visor(z: float, y_edge: float):
    """A generic visor: an opaque plate at z from y_edge upward (it shades the viewer, not the page,
    unless it reaches below the rays)."""
    return Plate(z, CASE["x0"], CASE["x1"], y_edge, 1e3)


def fresnel_T(cos_i, n=1.5):
    """Unpolarised transmission into a flat n = 1.5 film at incidence acos(cos_i)."""
    ci = np.clip(cos_i, 1e-9, 1.0)
    ct = np.sqrt(1.0 - (1.0 - ci * ci) / (n * n))
    rs = ((ci - n * ct) / (ci + n * ct)) ** 2
    rp = ((ct - n * ci) / (ct + n * ci)) ** 2
    return 1.0 - 0.5 * (rs + rp)


def irradiance(px, py, zp, sources, occluders=(), fresnel=False):
    px, py = np.broadcast_arrays(np.asarray(px, float), np.asarray(py, float))
    e_sum = np.zeros(px.shape)
    for s in sources:
        vx, vy, vz = px - s.x, py - s.y, zp - s.z
        r2 = vx * vx + vy * vy + vz * vz
        r = np.sqrt(r2)
        ci = -vz / r                                          # page normal +Z; source must be above it
        if s.pattern is not None:
            e = np.where(ci > 0, s.pattern(vx / r, vy / r, vz / r) * np.clip(ci, 0, None) / r2, 0.0)
        else:
            ca = (vx * s.axis[0] + vy * s.axis[1] + vz * s.axis[2]) / r
            e = np.where((ca > 0) & (ci > 0), np.clip(ca, 0, None) ** s.m * np.clip(ci, 0, None) / r2, 0.0)
        if fresnel:
            e = e * fresnel_T(ci)
        for o in occluders:
            e = e * o.passes(s, px, py, zp)
        e_sum += e
    return e_sum


# ---- edges: d along the throw, l across it ------------------------------------------------------
EDGES = {"top": dict(D=ACTIVE["y1"] - ACTIVE["y0"], l0=ACTIVE["x0"], l1=ACTIVE["x1"]),
         "left": dict(D=ACTIVE["x1"] - ACTIVE["x0"], l0=ACTIVE["y0"], l1=ACTIVE["y1"])}


def to_xy(edge, d, l):
    if edge == "top":
        return l, ACTIVE["y1"] - d
    return ACTIVE["x0"] + d, l


# ---- LED layouts across the top edge -------------------------------------------------------------
LAYOUTS = {   # name: (pairs, pair pitch or None = width/pairs, half separation warm-cool, alternate)
    "L5": (5, None, 2.2, False),          # 5 pairs spread evenly, 4.4 mm LED-to-LED (fits a 4.0 XL-4008)
    "L5-s3.3": (5, None, 3.3, False),     # the light strip's 6.6 mm pair spacing
    "L5-s1.2": (5, None, 1.2, False),     # tight pairs (2.4 mm; top-view 0603/0805 on an edge-on PCB)
    "L5-wide": (5, 12.5, 2.2, False),     # end pairs pushed out toward the corners
    "L5-w12.5-s1.2": (5, 12.5, 1.2, False),   # wide pitch AND tight pairs (top-view LEDs, edge-on PCB)
    "L5-w13.5-s1.2": (5, 13.5, 1.2, False),   # end pairs over the active area's side edges
    "L5-w13.5-s1.9": (5, 13.5, 1.9, False),   # the same with 3.8 mm pairs: two 3.0-long LUXEON 3014s side by side
    "L5-w12.5-s1.9": (5, 12.5, 1.9, False),
    "ALT10": (5, None, None, True),       # 10 LEDs at equal pitch, W C W C ...
    "L6": (6, None, 2.2, False),          # 6 pairs (what-if: 6 LEDs per string)
    "L6-s3.3": (6, None, 3.3, False),     # the light strip's own top-edge case
}


def layout(name="L5"):
    """[(x, colour)] across the active width, centred on it."""
    pairs, pitch, half, alt = LAYOUTS[name]
    x0, x1 = ACTIVE["x0"], ACTIVE["x1"]
    cx, w = (x0 + x1) / 2, x1 - x0
    if alt:
        n = 2 * pairs
        return [(x0 + w * (i + 0.5) / n, "W" if i % 2 == 0 else "C") for i in range(n)]
    p = pitch or w / pairs
    out = []
    for k in range(pairs):
        c = cx + p * (k - (pairs - 1) / 2)
        out += [(c - half, "W"), (c + half, "C")]
    return out


def sources_internal(z_page, h, y_face, lay="L5", tilt=0.0, m=1.0):
    return [Source(x, y_face, z_page + h, axis_from("down", tilt), m, c) for x, c in layout(lay)]


def sources_external(z_src, y_src, tilt, lay="L5", m=1.0):
    return [Source(x, y_src, z_src, axis_from("down", tilt), m, c) for x, c in layout(lay)]


def sources_tabulated(z_emit, y_emit, pattern, lay="L5"):
    """LEDs with a tabulated (e.g. rod-lens) pattern; the point source sits at the emitter + (dy, dz)."""
    return [Source(x, y_emit + pattern.dy, z_emit + pattern.dz, (0.0, -1.0, 0.0), 1.0, c, pattern)
            for x, c in layout(lay)]


def internal_occluders(z_page, h):
    """Under the brow the skin's underside is raised to the emitter's ceiling (z_page + h + half + clearance,
    never below the lip), so the lip/bevel planes below that ceiling are gone over the LEDs; what is left
    is the ceiling plate and any skin plane above it.  All of them lie above the source, so none can block
    a ray to the page (they are kept so the geometry is explicit)."""
    c = max(LIP_Z, z_page + h + EMITTER_HALF + CLEAR)
    return [ceiling(c)] + [o for o in skin() if o.z > c]


def internal_fit(z_page, h):
    """Ceiling the emitter needs (its top + clearance) and what that leaves of the 6.0 front skin."""
    ceil = z_page + h + EMITTER_HALF + CLEAR
    skin_left = FACE_Z - ceil
    if ceil <= LIP_Z:
        cls = "stock lip"
    elif skin_left >= 0.6:
        cls = "raised ceiling"
    elif skin_left >= MIN_SKIN:
        cls = "thin skin"
    else:
        cls = f"Z_FRONT +{MIN_SKIN - skin_left:.2f}"
    return dict(ceiling=round(ceil, 3), skin_left=round(skin_left, 3), fit=cls)


# ---- the evaluator --------------------------------------------------------------------------------
def evaluate(sources, z_page, edge="top", occluders=(), fresnel=False, res=1.0, fine_l=0.5, keep=False):
    g = EDGES[edge]
    D, l0, l1 = g["D"], g["l0"], g["l1"]
    W = [s for s in sources if s.colour == "W"]
    C = [s for s in sources if s.colour == "C"]
    m = W[0].m
    irr = lambda d, l, src: irradiance(*to_xy(edge, d, l), z_page, src, occluders, fresnel)

    # coarse grid (cell centres) and a fine band over the first 20 mm
    d = np.arange(res / 2, D, res)
    l = np.arange(l0 + res / 2, l1, res)
    dd, ll = np.meshgrid(d, l, indexing="ij")
    Ew = irr(dd, ll, W)
    fd = 0.05
    dF = np.arange(fd / 2, min(20.0, D), fd)
    lF = np.arange(l0 + fine_l / 2, l1, fine_l)
    ddF, llF = np.meshgrid(dF, lF, indexing="ij")
    EwF = irr(ddF, llF, W)

    # flux on the active area
    rows = (d - res / 2) >= 20.0 - 1e-9
    flux = EwF.sum() * fd * fine_l + Ew[rows].sum() * res * res
    emitted = len(W) * 2 * math.pi / (m + 1)

    # profile over the middle 80 %
    lm0, lm1 = l0 + 0.1 * (l1 - l0), l1 - 0.1 * (l1 - l0)
    lp = np.linspace(lm0, lm1, 161)
    keyd = [2, 5, 10, 20, 40, 80]
    dp = np.unique(np.concatenate([np.linspace(0.05, D, 300), np.arange(10, 40.01, 0.5),
                                   [x for x in keyd if x < D], [D / 2, D]]))
    Dp, Lp = np.meshgrid(dp, lp, indexing="ij")
    Ep = irr(Dp, Lp, W)
    prof = Ep.mean(axis=1)
    at = lambda v: float(prof[int(np.argmin(np.abs(dp - v)))])
    far, mid = at(D), at(D / 2)
    sel = (dp >= 10) & (dp <= 40)
    line = lambda v, src, lat=lp: irr(np.full_like(lat, v), lat, src)

    # shadowed band at the top
    midcols = (lF >= lm0) & (lF <= lm1)
    PF = EwF[:, midcols].mean(axis=1)
    pmax = max(PF.max(), prof.max())
    hit = np.nonzero(PF >= 0.05 * pmax)[0]
    band = float(dF[hit[0]] - fd / 2) if len(hit) else float(dp[np.nonzero(prof >= 0.05 * pmax)[0][0]])
    colmax = np.maximum(EwF.max(axis=0), np.array([Ew[:, int(np.argmin(np.abs(l - v)))].max() for v in lF]))
    col_band = []
    for j in range(len(lF)):
        k = np.nonzero(EwF[:, j] >= 0.05 * colmax[j])[0]
        col_band.append(dF[k[0]] - fd / 2 if len(k) else 20.0)
    band_col = float(max(col_band))

    # min/max
    allE = np.concatenate([Ew.ravel(), EwF.ravel()])
    low = Ew[d >= 0.2 * D]
    minmax_all = float(allE.min() / allE.max()) if allE.max() > 0 else 0.0
    minmax_low = float(low.min() / low.max()) if low.max() > 0 else 0.0

    # ripple between the LEDs: across the interior (2nd to 2nd-last warm LED), so the ends' falloff
    # (reported as ends_mid) does not count as scalloping
    wl = sorted((s.x if edge == "top" else s.y) for s in W)
    li = np.linspace(wl[1], wl[-2], 241) if len(wl) >= 4 else lp
    scallop = {}
    for v in (5, 10, 20):
        ln = line(v, W, li)
        scallop[f"{v}"] = round(float(ln.max() / ln.min()), 3) if ln.min() > 0 else None
    lfull = np.linspace(l0, l1, 401)
    both10 = line(10, W, lfull) + line(10, C, lfull)
    q = len(lfull) // 10
    c0 = len(lfull) // 2
    ends_mid = float(min(both10[:q].mean(), both10[-q:].mean()) / both10[c0 - q // 2:c0 + q // 2].mean())
    mix = {}
    for v in (3, 10, 20):
        w_, c_ = line(v, W), line(v, C)
        tot = w_ + c_
        mix[f"{v}"] = round(float(np.max(np.abs(w_[tot > 0] / tot[tot > 0] - 0.5))), 3) if (tot > 0).any() else None

    r = dict(
        near_far={f"{v}": (round(at(v) / far, 2) if far > 0 else None) for v in keyd if v < D},
        nf_10_40=round(float(prof[sel].max() / far), 2) if far > 0 else None,
        vs_mid={f"{v}": (round(at(v) / mid, 2) if mid > 0 else None) for v in (2, 5, 10, 20)}
        | {"far": round(far / mid, 3) if mid > 0 else None},
        band=round(band, 2), band_col=round(band_col, 2),
        minmax_all=round(minmax_all, 5), minmax_low80=round(minmax_low, 4),
        scallop=scallop, ends_mid=round(ends_mid, 3), mix=mix,
        pk_2=round(float(prof[dp >= 2].max() / far), 2) if far > 0 else None,
        flux=round(float(flux / emitted), 4),
        far_abs=float(far),
        # lux at the far edge / half way per lumen emitted by EACH LED of the string (I0 = phi (m+1) / 2 pi)
        lux_far_per_lm=round(float(far * 1e6 * (m + 1) / (2 * math.pi)), 2),
        lux_mid_per_lm=round(float(mid * 1e6 * (m + 1) / (2 * math.pi)), 2),
    )
    if keep:
        r["_prof"] = (dp, prof)
        r["_grid"] = (d, l, Ew)
        r["_src"] = [(s.x, s.y, s.colour) for s in sources]
        r["_edge"] = edge
    return r


def public(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


# ---- reference: the light strip's left-edge bar (silkscreen-light-strip tools/params.py) ----------
LS_PAIRS_KICAD = [(43.85, 50.45), (60.85, 67.45), (76.4, 83.0), (91.95, 98.55), (107.5, 114.1), (123.05, 129.65)]
LS_FACE_X = 45.2 - 44.24          # 0.96: 1.197 left of the active area
LS_H = 0.785                      # tape + PI + flex + half the 0.8 LED, on the PLAIN page


def sources_side_strip(m=1.0):
    z = PANELS["PLAIN"] + LS_H
    out = []
    for cool, warm in LS_PAIRS_KICAD:
        out.append(Source(LS_FACE_X, 148.25 - warm, z, axis_from("right", 0), m, "W"))
        out.append(Source(LS_FACE_X, 148.25 - cool, z, axis_from("right", 0), m, "C"))
    return out


# ---- sweeps ---------------------------------------------------------------------------------------
H_LIST = [0.3, 0.45, 0.6, 0.8, 1.0, 1.2]
YF_LIST = [108.6, 109.5, 110.5, 111.5, 113.0, 115.0]
ZS_LIST = [6.5, 7.0, 8.0, 10.0, 12.0, 14.0, 16.0]
YS_LIST = [109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 116.0, 118.0]
TILT_LIST = [0, 5, 10, 15, 20, 25, 30, 35]
BEAM_Z = (8.0, 10.0, 12.0, 14.0, 16.0)
BEAM_TILT = (-30, -25, -20, -15, -10, -5, 0, 5, 10, 20, 30)
HOUSING_MIN_Y = 109.8     # emitter centre >= face-bevel edge 109.1 + ~0.7 so the housing stays off the window
BAND_OK = 0.5             # a band this short hides under the 0.6 margin between the active top and the lip


def run_internal(res, fine_l, m):
    rows = []
    for page, zp in PANELS.items():
        for h in H_LIST:
            for yf in YF_LIST:
                src = sources_internal(zp, h, yf, "L5", 0.0, m)
                occ = internal_occluders(zp, h)
                r = public(evaluate(src, zp, "top", occ, False, res, fine_l))
                rows.append(dict(page=page, z_page=zp, h=h, y_face=yf, gap=round(yf - ACTIVE["y1"], 2),
                                 **internal_fit(zp, h), **r))
    return rows


def run_external(res, fine_l, m, pages=("FT01C", "PLAIN")):
    rows = []
    for page in pages:
        zp = PANELS[page]
        for zs in ZS_LIST:
            for ys in YS_LIST:
                for t in TILT_LIST:
                    src = sources_external(zs, ys, t, "L5", m)
                    r = public(evaluate(src, zp, "top", skin(), False, res, fine_l))
                    rows.append(dict(page=page, z_page=zp, z_src=zs, y_src=ys, tilt=t,
                                     housing_ok=ys >= HOUSING_MIN_Y, **r))
    return rows


def pareto(rows):
    """Non-dominated rows for (band min, nf_10_40 min, flux max)."""
    pts = np.array([[r["band"], r["nf_10_40"] if r["nf_10_40"] is not None else 1e9, -r["flux"]] for r in rows])
    keep = []
    for i, p in enumerate(pts):
        dom = np.all(pts <= p, axis=1) & np.any(pts < p, axis=1)
        if not dom.any():
            keep.append(i)
    return [rows[i] for i in keep]


def best(rows, band_max=BAND_OK, need_housing=True):
    ok = [r for r in rows if r["band"] <= band_max and r["nf_10_40"] is not None
          and (r.get("housing_ok", True) or not need_housing)]
    return min(ok, key=lambda r: (r["nf_10_40"], -r["flux"])) if ok else None


# ---- plots ----------------------------------------------------------------------------------------
def _plt():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("matplotlib missing: no PNGs", file=sys.stderr)
        return None


def plot_profiles(cases, path):
    plt = _plt()
    if not plt:
        return
    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    colours = ["#b45309", "#1d4ed8", "#047857", "#7c3aed", "#6b7280", "#9ca3af"]
    for (name, r), c in zip(cases, colours):
        dp, prof = r["_prof"]
        mid = prof[int(np.argmin(np.abs(dp - dp[-1] / 2)))]
        ls = "--" if r["_edge"] == "left" else "-"
        ax.semilogy(dp, np.maximum(prof / mid, 1e-3), ls, color=c, lw=1.6, label=name)
    ax.set_xlim(0, 93)
    ax.set_ylim(0.2, 300)
    ax.set_xlabel("distance from the lit edge of the active area (mm)")
    ax.set_ylabel("irradiance / half-way value (log)")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=7.5)
    ax.set_title("Profile down the page (x-mean over the middle 80 %), one string lit", fontsize=9)
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_heatmaps(cases, path):
    plt = _plt()
    if not plt:
        return
    from matplotlib.colors import LogNorm
    fig, axes = plt.subplots(1, len(cases), figsize=(2.3 * len(cases) + 1.0, 4.3), constrained_layout=True)
    im = None
    for ax, (name, r) in zip(axes, cases):
        d, l, E = r["_grid"]
        e = E / max(np.median(E), 1e-30)
        x0, x1, y0, y1 = ACTIVE["x0"], ACTIVE["x1"], ACTIVE["y0"], ACTIVE["y1"]
        img = e if r["_edge"] == "top" else np.flipud(e.T)     # rows = y from the top, columns = x
        im = ax.imshow(np.maximum(img, 1e-3), origin="upper", extent=(x0, x1, y0, y1),
                       norm=LogNorm(vmin=0.1, vmax=30), cmap="magma", aspect="equal")
        for x, y, c in r["_src"]:
            if c == "W":
                ax.plot(min(max(x, x0 - 1.5), x1), min(y, y1 + 1.5), "o", ms=3, color="#ffb347", clip_on=False)
        ax.set_title(name, fontsize=7)
        ax.tick_params(labelsize=6)
    fig.colorbar(im, ax=axes, shrink=0.7, label="E / page median (log), warm string")
    fig.savefig(path, dpi=85)
    plt.close(fig)


def plot_external_map(rows, path):
    plt = _plt()
    if not plt:
        return
    pages = sorted({r["page"] for r in rows})
    fig, axes = plt.subplots(2, len(pages), figsize=(3.3 * len(pages), 5.6), constrained_layout=True)
    for j, page in enumerate(pages):
        nf = np.full((len(ZS_LIST), len(YS_LIST)), np.nan)
        tb = np.full_like(nf, np.nan)
        for a, zs in enumerate(ZS_LIST):
            for b, ys in enumerate(YS_LIST):
                r = next(r for r in rows if r["page"] == page and r["z_src"] == zs and r["y_src"] == ys
                         and r["tilt"] == 0 and "angle" not in r)
                tb[a, b] = r["band"]
                if r["band"] <= BAND_OK:
                    nf[a, b] = r["nf_10_40"]
        for i, (arr, lab, cmap) in enumerate(((nf, "nf_10_40, tilt 0 (blank: band > 0.5)", "viridis_r"),
                                              (tb, "shadow band mm, tilt 0", "cividis"))):
            ax = axes[i, j]
            im = ax.imshow(arr, origin="lower", cmap=cmap, aspect="auto")
            ax.set_xticks(range(len(YS_LIST)), [f"{v:g}" for v in YS_LIST], fontsize=6)
            ax.set_yticks(range(len(ZS_LIST)), [f"{v:g}" for v in ZS_LIST], fontsize=6)
            ax.set_xlabel("source y", fontsize=7)
            ax.set_ylabel("source z", fontsize=7)
            ax.set_title(f"{page}: {lab}", fontsize=7.5)
            for a in range(arr.shape[0]):
                for b in range(arr.shape[1]):
                    if not np.isnan(arr[a, b]):
                        ax.text(b, a, f"{arr[a, b]:.0f}" if i == 0 else f"{arr[a, b]:.1f}", ha="center", va="center", fontsize=5.5, color="w")
            fig.colorbar(im, ax=ax, shrink=0.8)
    fig.savefig(path, dpi=85)
    plt.close(fig)


# ---- tables ---------------------------------------------------------------------------------------
def fmt_nf(r):
    nf = r["near_far"]
    return " / ".join(f"{nf[k]:.3g}" if nf.get(k) is not None else "-" for k in ("2", "5", "10", "20", "40", "80"))


def row_line(r, extra=""):
    return (f"| {extra}{fmt_nf(r)} | {r['nf_10_40']} | {r['pk_2']} | {r['band']} / {r['band_col']} | {r['vs_mid']['10']} / "
            f"{r['vs_mid']['20']} / {r['vs_mid']['far']} | {r['minmax_low80']:.3f} | {r['scallop']['5']} / "
            f"{r['scallop']['10']} / {r['scallop']['20']} | {r['ends_mid']} | {r['mix']['10']} | {r['flux']:.3f} | "
            f"{r['lux_far_per_lm']} / {r['lux_mid_per_lm']} |")


HDR = ("| near/far @2/5/10/20/40/80 | nf 10-40 | peak/far >2mm | band / worst col (mm) | vs mid @10/@20/far | min/max low 80% "
       "| scallop @5/10/20 | ends/mid @10 | mix @10 | flux | lux far/mid per lm |")


def parse_eval(spec):
    kv = dict(p.split("=") for p in spec.split(","))
    m = exponent_for_full_angle(float(kv.get("angle", 120)))
    page = kv.get("page", "FT01C")
    zp = PANELS[page] if page in PANELS else float(page)
    lay = kv.get("layout", "L5")
    fres = kv.get("fresnel", "0") == "1"
    if kv.get("kind", "external") == "internal":
        h, yf = float(kv["h"]), float(kv["y"])
        src = sources_internal(zp, h, yf, lay, float(kv.get("tilt", 0)), m)
        occ = internal_occluders(zp, h)
        r = public(evaluate(src, zp, "top", occ, fres, 0.5, 0.25))
        r.update(internal_fit(zp, h))
    else:
        if "pattern" in kv:      # z, y = the EMITTER centre; the table carries the lens offset
            src = sources_tabulated(float(kv["z"]), float(kv["y"]), TabulatedPattern.load(kv["pattern"]), lay)
        else:
            src = sources_external(float(kv["z"]), float(kv["y"]), float(kv.get("tilt", 0)), lay, m)
        occ = skin()
        if "visor_z" in kv:
            occ.append(visor(float(kv["visor_z"]), float(kv.get("visor_y", 109.1))))
        r = public(evaluate(src, zp, "top", occ, fres, 0.5, 0.25))
    print(json.dumps(dict(spec=kv, z_page=zp, **r), indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true", help="coarser grids")
    ap.add_argument("--angle", type=float, default=120.0, help="LED full half-intensity angle (deg)")
    ap.add_argument("--eval", help="evaluate one geometry, e.g. kind=external,page=FT01C,z=10,y=112,tilt=20")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    if a.eval:
        return parse_eval(a.eval)
    os.makedirs(a.out, exist_ok=True)
    res, fine_l = (1.0, 1.0) if a.quick else (1.0, 0.5)
    m = exponent_for_full_angle(a.angle)
    t0 = time.time()
    P = lambda *s: print(*s, flush=True)

    # 0. cross-check against the light strip's own top-edge case (6 pairs +-3.3, gap 1.197, h 0.785)
    ls_top = evaluate(sources_internal(PANELS["PLAIN"], LS_H, ACTIVE["y1"] + 1.197, "L6-s3.3", 0, m),
                      PANELS["PLAIN"], "top", internal_occluders(PANELS["PLAIN"], LS_H), False, 0.5, 0.25, keep=True)
    side = evaluate(sources_side_strip(m), PANELS["PLAIN"], "left", (), False, 0.5, 0.25, keep=True)

    # 1. internal
    internal = run_internal(res, fine_l, m)
    P(f"# internal sweep done {time.time() - t0:.0f}s")
    # 2. external
    external = run_external(res, fine_l, m)
    P(f"# external sweep done {time.time() - t0:.0f}s")

    summary = dict(model=__doc__.split("Metrics")[0].strip(), full_angle=a.angle, m=round(m, 3),
                   panels=PANELS, band_ok=BAND_OK, housing_min_y=HOUSING_MIN_Y)
    summary["reference"] = {"light-strip top edge (L6-s3.3, gap 1.197, h 0.785, PLAIN)": public(ls_top),
                            "light-strip side edge (6 pairs, pitch 15.55, h 0.785, PLAIN; d from the LEFT edge, throw 55.7)": public(side)}

    # internal picks: best feasible per page (skin >= MIN_SKIN), and the table nf_10_40 by (h, y_face)
    P("\n## Internal sweep (L5, tilt 0): nf_10_40 [near/far@10] by h (rows) and LED face y (columns)")
    ipicks = {}
    for page in PANELS:
        P(f"\n**{page}** (page z {PANELS[page]}) - cells: nf_10_40 [nf@10] (fit)")
        P("| h \\ y_face | " + " | ".join(f"{v:g} (gap {v - ACTIVE['y1']:.1f})" for v in YF_LIST) + " |")
        P("|---" * (len(YF_LIST) + 1) + "|")
        for h in H_LIST:
            cells = []
            for yf in YF_LIST:
                r = next(x for x in internal if x["page"] == page and x["h"] == h and x["y_face"] == yf)
                cells.append(f"{r['nf_10_40']:.0f} [{r['near_far']['10']:.0f}]")
            fit = next(x for x in internal if x["page"] == page and x["h"] == h)
            P(f"| {h} ({fit['fit']}, ceil {fit['ceiling']}) | " + " | ".join(cells) + " |")
        feas = [x for x in internal if x["page"] == page and x["skin_left"] >= MIN_SKIN]
        ipicks[page] = min(feas, key=lambda r: (r["nf_10_40"], -r["flux"])) if feas else None
    summary["internal_picks"] = ipicks

    # external: Pareto sets, the best per source height, picks
    P("\n## External sweep (L5): best (y_src, tilt) per source z with band <= 0.5 and y_src >= 109.8")
    epicks, pareto_out = {}, {}
    for page in ("FT01C", "PLAIN"):
        rows = [r for r in external if r["page"] == page]
        par = pareto([r for r in rows if r["housing_ok"]])
        pareto_out[page] = dict(size=len(par),
                                least_band=min(par, key=lambda r: (r["band"], r["nf_10_40"])),
                                best_nf=min(par, key=lambda r: r["nf_10_40"]),
                                most_flux=max(par, key=lambda r: r["flux"]))
        P(f"\n**{page}** (page z {PANELS[page]}); Pareto set (housing-ok): {len(par)} of {len(rows)} geometries")
        P("| z_src | y_src | tilt " + HDR.replace("| near", "| near", 1))
        P("|---" * 14 + "|")
        per_z = []
        for zs in ZS_LIST:
            b = best([r for r in rows if r["z_src"] == zs])
            if b:
                per_z.append(b)
                P(f"| {zs:g} | {b['y_src']:g} | {b['tilt']} " + row_line(b))
            else:
                P(f"| {zs:g} | - | - | no geometry with band <= {BAND_OK} |" + " |" * 8)
        epicks[page] = dict(per_z=per_z, best=best(rows))
    summary["external_pareto"] = pareto_out
    summary["external_best_per_z"] = {k: v["per_z"] for k, v in epicks.items()}

    # shadow band vs source height at tilt 20, y_src 111 (plain words: what a low visor costs)
    P("\n## External: shadowed band at the top (mm) vs source z, tilt 20, by y_src")
    for page in ("FT01C", "PLAIN"):
        P(f"\n**{page}**\n| z_src | " + " | ".join(f"y {v:g}" for v in YS_LIST) + " |")
        P("|---" * (len(YS_LIST) + 1) + "|")
        for zs in ZS_LIST:
            cells = [next(r for r in external if r["page"] == page and r["z_src"] == zs and r["y_src"] == ys
                          and r["tilt"] == 20)["band"] for ys in YS_LIST]
            P(f"| {zs:g} | " + " | ".join(f"{c:.2f}" for c in cells) + " |")

    P("\n## Internal: flux fraction on the active area (PLAIN; the ratios above do not depend on h)")
    P("| h \\ y_face | " + " | ".join(f"{v:g}" for v in YF_LIST) + " |")
    P("|---" * (len(YF_LIST) + 1) + "|")
    for h in H_LIST:
        P(f"| {h} | " + " | ".join(f"{next(x for x in internal if x['page'] == 'PLAIN' and x['h'] == h and x['y_face'] == yf)['flux']:.3f}"
                                  for yf in YF_LIST) + " |")

    P("\n## External Pareto sets (band, nf_10_40, flux; housing-ok), sorted by nf_10_40")
    for page in ("FT01C", "PLAIN"):
        par = sorted(pareto([r for r in external if r["page"] == page and r["housing_ok"]]), key=lambda r: r["nf_10_40"])
        P(f"\n**{page}**: " + "; ".join(f"z{r['z_src']:g} y{r['y_src']:g} t{r['tilt']}: band {r['band']}, nf {r['nf_10_40']:.0f}, "
                                         f"flux {r['flux']:.2f}" for r in par))

    # beam what-if: narrower LEDs and tilts both ways (negative = axis tilted AWAY from the page)
    beam = []
    for page in ("FT01C", "PLAIN"):
        zp = PANELS[page]
        for ang in (120, 90, 60, 40, 30):
            mm = exponent_for_full_angle(ang)
            for zs in BEAM_Z:
                for ys in (110.0, 112.0, 114.0, 116.0, 118.0):
                    for t in BEAM_TILT:
                        r = public(evaluate(sources_external(zs, ys, t, "L5", mm), zp, "top", skin(), False, res, fine_l))
                        beam.append(dict(page=page, angle=ang, z_src=zs, y_src=ys, tilt=t, housing_ok=True, **r))
    P(f"\n# beam sweep done {time.time() - t0:.0f}s")
    P("\n## Beam what-if (external, L5): best (y_src, tilt) by peak/far beyond 2 mm, band <= 0.5")
    P("| page | full angle | z_src | y_src | tilt " + HDR)
    P("|---" * 16 + "|")
    beam_best = {}
    for page in ("FT01C", "PLAIN"):
        for ang in (120, 90, 60, 40, 30):
            for zs in BEAM_Z:
                ok = [r for r in beam if r["page"] == page and r["angle"] == ang and r["z_src"] == zs
                      and r["band"] <= BAND_OK and r["pk_2"] is not None]
                if not ok:
                    continue
                b = min(ok, key=lambda r: (r["pk_2"], -r["flux"]))
                beam_best[f"{page} {ang} z{zs:g}"] = b
                P(f"| {page} | {ang} | {zs:g} | {b['y_src']:g} | {b['tilt']} " + row_line(b))
    summary["beam_best"] = beam_best

    # 3. layouts, 6 pairs, view angle, Fresnel, T01C at the picks
    def geo_int(page, h, yf, lay="L5", tilt=0.0, mm=m, fres=False, keep=False):
        zp = PANELS[page]
        return evaluate(sources_internal(zp, h, yf, lay, tilt, mm), zp, "top",
                        internal_occluders(zp, h), fres, 0.5, 0.25, keep)

    def geo_ext(page, zs, ys, tilt, lay="L5", mm=m, fres=False, keep=False):
        zp = PANELS[page]
        return evaluate(sources_external(zs, ys, tilt, lay, mm), zp, "top", skin(), fres, 0.5, 0.25, keep)

    ip = ipicks["PLAIN"]
    ep = epicks["FT01C"]["best"]
    # a practical external geometry: visor 4 mm proud of the face (z 10), best y/tilt there
    ep10 = {pg: next(r for r in epicks[pg]["per_z"] if r["z_src"] == 10.0) for pg in ("FT01C", "PLAIN")}
    whatif = {}
    P("\n## Layouts at the picks (0.5 mm grid)")
    P("| geometry | layout " + HDR)
    P("|---" * 13 + "|")
    for lay in LAYOUTS:
        for tag, fn in ((f"internal PLAIN h {ip['h']} y {ip['y_face']}", lambda L: geo_int("PLAIN", ip["h"], ip["y_face"], L)),
                        (f"external FT01C z 10 y {ep10['FT01C']['y_src']:g} t {ep10['FT01C']['tilt']}",
                         lambda L: geo_ext("FT01C", 10.0, ep10["FT01C"]["y_src"], ep10["FT01C"]["tilt"], L))):
            r = public(fn(lay))
            whatif[f"{tag} | {lay}"] = r
            P(f"| {tag} | {lay} " + row_line(r))

    P("\n## LED view angle (external FT01C z 10, y as picked, tilt re-optimised; internal PLAIN pick, tilt 0)")
    P("| case | full angle | best tilt " + HDR)
    P("|---" * 14 + "|")
    for ang in (120, 90, 60):
        mm = exponent_for_full_angle(ang)
        cand = [(t, public(geo_ext("FT01C", 10.0, ep10["FT01C"]["y_src"], t, "L5", mm))) for t in range(0, 50, 5)]
        cand = [c for c in cand if c[1]["band"] <= BAND_OK] or cand
        t_best, r = min(cand, key=lambda c: c[1]["nf_10_40"])
        whatif[f"external FT01C z10 angle {ang}"] = dict(tilt=t_best, **r)
        P(f"| external FT01C z 10 | {ang} | {t_best} " + row_line(r))
        ri = public(geo_int("PLAIN", ip["h"], ip["y_face"], "L5", 0.0, mm))
        whatif[f"internal PLAIN angle {ang}"] = ri
        P(f"| internal PLAIN pick | {ang} | 0 " + row_line(ri))
        cand = [(t, public(geo_int("PLAIN", ip["h"], ip["y_face"], "L5", -t, mm))) for t in (5, 10, 20)]
        t_best, r = min(cand, key=lambda c: c[1]["nf_10_40"])
        whatif[f"internal PLAIN angle {ang} tilted up"] = dict(tilt=-t_best, **r)
        P(f"| internal PLAIN pick, tilted AWAY from the page | {ang} | -{t_best} " + row_line(r))

    P("\n## Fresnel (glossy n = 1.5 film) at the picks, and T01C")
    P("| case | fresnel " + HDR)
    P("|---" * 13 + "|")
    fcases = [("internal PLAIN pick", lambda f: geo_int("PLAIN", ip["h"], ip["y_face"], fres=f)),
              ("external FT01C z10 pick", lambda f: geo_ext("FT01C", 10.0, ep10["FT01C"]["y_src"], ep10["FT01C"]["tilt"], fres=f)),
              ("external PLAIN z10 pick", lambda f: geo_ext("PLAIN", 10.0, ep10["PLAIN"]["y_src"], ep10["PLAIN"]["tilt"], fres=f))]
    for name, fn in fcases:
        for f in (False, True):
            r = public(fn(f))
            whatif[f"{name} fresnel {f}"] = r
            P(f"| {name} | {f} " + row_line(r))
    it = ipicks["T01C"]
    for name, r in ((f"internal T01C pick h {it['h']} y {it['y_face']}", public(geo_int("T01C", it["h"], it["y_face"]))),
                    (f"external T01C z 10 y {ep10['FT01C']['y_src']:g} t {ep10['FT01C']['tilt']}",
                     public(geo_ext("T01C", 10.0, ep10["FT01C"]["y_src"], ep10["FT01C"]["tilt"])))):
        whatif[name] = r
        P(f"| {name} | False " + row_line(r))
    summary["whatif"] = whatif
    summary["picks"] = dict(internal_plain=ip, internal_ft01c=ipicks["FT01C"], internal_t01c=it,
                            external_ft01c_best=ep, external_plain_best=epicks["PLAIN"]["best"],
                            external_z10=ep10)

    P("\n## Recommended geometries (0.5 mm grid): beam-sweep winners with the layouts that fix the ends and the colour mix")
    P("| case | layout | fresnel " + HDR)
    P("|---" * 15 + "|")
    rec = {}
    for page in ("FT01C", "PLAIN"):
        for ang, zs in ((60, 12.0), (40, 12.0), (60, 16.0), (40, 16.0)):
            b = beam_best.get(f"{page} {ang} z{zs:g}")
            if not b:
                continue
            mm = exponent_for_full_angle(ang)
            for lay in ("L5", "L5-w12.5-s1.2", "L5-w13.5-s1.2"):
                for f in ((False, True) if lay == "L5-w12.5-s1.2" else (False,)):
                    r = public(geo_ext(page, zs, b["y_src"], b["tilt"], lay, mm, f))
                    name = f"external {page} {ang} deg z{zs:g} y{b['y_src']:g} t{b['tilt']}"
                    rec[f"{name} | {lay} | fresnel {f}"] = r
                    P(f"| {name} | {lay} | {f} " + row_line(r))
    for page, h in (("PLAIN", 1.2), ("T01C", 0.6), ("FT01C", 0.3)):
        for yf in (113.0, 115.0):
            for lay in ("L5", "L5-w12.5-s1.2"):
                r = public(geo_int(page, h, yf, lay))
                name = f"internal {page} h{h} y{yf:g} ({internal_fit(PANELS[page], h)['fit']})"
                rec[f"{name} | {lay}"] = r
                P(f"| {name} | {lay} | False " + row_line(r))
    summary["recommended"] = rec

    P("\n## References (0.5 mm grid)")
    P("| case " + HDR)
    P("|---" * 12 + "|")
    for k, r in summary["reference"].items():
        P(f"| {k} " + row_line(r))

    # headline plots
    fin = ipicks["FT01C"]
    heads = [(f"internal PLAIN h{ip['h']} y{ip['y_face']:g}", geo_int("PLAIN", ip["h"], ip["y_face"], keep=True))]
    if fin:
        heads.append((f"internal FT01C h{fin['h']} y{fin['y_face']:g} ({fin['fit']})",
                      geo_int("FT01C", fin["h"], fin["y_face"], keep=True)))
    for pg in ("FT01C", "PLAIN"):
        e = ep10[pg]
        heads.append((f"external {pg} z10 y{e['y_src']:g} t{e['tilt']}", geo_ext(pg, 10.0, e["y_src"], e["tilt"], keep=True)))
    nb = beam_best.get("FT01C 40 z12") or beam_best.get("FT01C 60 z12")
    if nb:
        heads.append((f"external FT01C z12 y{nb['y_src']:g} t{nb['tilt']}, {nb['angle']} deg LEDs",
                      geo_ext("FT01C", 12.0, nb["y_src"], nb["tilt"], "L5", exponent_for_full_angle(nb["angle"]), keep=True)))
    heads.append(("light-strip top-edge case (LS model)", ls_top))
    heads.append(("light-strip SIDE strip (d from the left edge)", side))
    plot_profiles(heads, os.path.join(a.out, "optics_profiles.png"))
    pick = lambda key: next(c for c in heads if c[0].startswith(key))
    plot_heatmaps([pick("internal PLAIN"), pick("external FT01C z10"), pick("external FT01C z12") if nb else pick("external PLAIN"),
                   pick("light-strip SIDE")], os.path.join(a.out, "optics_heatmaps.png"))
    plot_external_map(external, os.path.join(a.out, "optics_external_map.png"))

    with open(os.path.join(a.out, "optics_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=float)
    with open(os.path.join(a.out, "optics_internal.json"), "w") as f:
        json.dump(internal, f, separators=(",", ":"), default=float)
    with open(os.path.join(a.out, "optics_external.json"), "w") as f:
        json.dump(external + beam, f, separators=(",", ":"), default=float)
    P(f"\n# done in {time.time() - t0:.0f}s -> {a.out}")


if __name__ == "__main__":
    main()
