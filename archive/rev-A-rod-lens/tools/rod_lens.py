"""Cylindrical-lens (clear PMMA rod) optics for the EXTERNAL top-edge light bar.

Frame: the enclosure frame of optics_sim.py (X = KiCad X - 44.24, Y = 148.25 - KiCad Y, +Y = top edge,
Z = 0 at the main-PCB rear, +Z toward the viewer).  Page = the active area in the plane z = z_page.

Geometry (per LED, local frame: emitter-face centre at the origin, emission into -Y):
* Emitter: a top-view LED on the UNDERSIDE of a flat PCB.  Rev 2 (2026-09-25): PCB underside y 118.61 seated
  (mechanical-spec.md sec 2d/3f; rev 1 used 118.14), LED = HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3 (LCSC
  C210340 warm / C210343 cool), 0.70 tall -> emitting face y 117.91.  Extended Lambertian emitter W across Z
  (EMIT_W 1.15 = the 3014 cavity, ~1.12 scaled from the Hongli p.2 top view; 1.4 = package width, a variant)
  x L along X (EMIT_L 2.50, Hongli p.2).  Rev 1 (LUXEON 3014, DS208) used W 1.4, L 2.5, y 117.44.
* Rod: an infinite cylinder along X, diameter D, refractive index n (PMMA 1.491), its top `gap` below the
  emitter face, its centre offset `dz` in Z from the emitter centre (dz < 0 = toward the page = aims the
  beam UP the page... no: the chief ray runs emitter -> rod centre, so dz < 0 aims the beam toward the
  page (+tilt), dz > 0 away from it).
* Full 3D trace (skew rays included): vector Snell at both surfaces, unpolarised Fresnel transmission at
  both (the reflected parts are counted as lost: a matte-black holder absorbs them), no TIR possible on
  a circular section but checked.  Rays that miss the rod go straight on (baffle=False) or are absorbed
  by a matte-black channel whose walls are tangent to the rod at its equator (baffle=True).
* Bare LED (D=None): optional knife-edge `knife=(hk, zk)`: an opaque plate hk below the emitter face that
  blocks rays crossing it at z < zk (a printed cut-off toward the page).
* Page: rays are projected straight to z = z_page through the case's front skin (optics_sim.skin()),
  5 LEDs per string at the layout's warm (or cool) x positions; irradiance is binned on the active area.
  This is a near-field Monte Carlo, so no far-field approximation near the top edge.
* The same rays also give a far-field table I/I0(theta, s) that optics_sim.TabulatedPattern reads.

Units: E in optics_sim's units (I0 = 1, i.e. phi = pi per LED); lux per lumen per LED = E * 1e6 / pi.

Run:  python tools/rod_lens.py            (screening sweep -> design/optics/rod_sweep.json)
      python tools/rod_lens.py --quick    (fewer rays)
      python tools/rod_lens.py --final    (rev 1 fine sweep)   --pick D,gap,dz,z_e   (rev 1 pick report)
      python tools/rod_lens.py --rev2 [--quick] [--at D,gap,dz] [--name rev2_alt]
                                          (rev 2: fine sweep at z_e 16 with the Hongli 3014 at y 117.91,
                                           robust pick, lux, tolerance -> design/optics/rod_rev2.json)
      NOTE: the module constants are now the rev 2 values; re-running --final/--pick uses them.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import optics_sim as O  # noqa: E402

OUT = O.OUT
N_PMMA = 1.491                       # cast PMMA at ~550 nm (1.4914 @ 589 nm)
Y_PCB_UNDER = 118.61                 # rev 2: seated PCB underside (mechanical-spec 2d); rev 1 had 118.14
LED_H = 0.70                         # Hongli HL-A-3014H421W package height (DS p.2); LUXEON 3014 is also 0.70
Y_EMIT = Y_PCB_UNDER - LED_H         # 117.91 (rev 1: 117.44)
EMIT_W = 1.15                        # emitter (cavity) width across Z; rev 1 used 1.4
EMIT_L = 2.50                        # emitter (cavity) length along X (Hongli p.2 "2.50")
LAY = "L5-w13.5-s1.9"                # buildable 3.0-long pairs (rev 1 sweeps used L5-w12.5-s1.2)
D_THROW = O.ACTIVE["y1"] - O.ACTIVE["y0"]   # 92.8
XA0, XA1 = O.ACTIVE["x0"], O.ACTIVE["x1"]
XM0, XM1 = XA0 + 0.1 * (XA1 - XA0), XA1 - 0.1 * (XA1 - XA0)   # middle 80 %
# d bins: 0.5 mm to 20, 1 mm to the far edge
D_EDGES = np.unique(np.concatenate([np.arange(0, 20, 0.5), np.arange(20, D_THROW, 1.0), [D_THROW]]))
X_EDGES = np.linspace(XA0, XA1, 113)


def fresnel(ci, ct, n1, n2):
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    return 1.0 - 0.5 * (rs + rp)


def refract(d, nrm, eta):
    """d: unit directions (N,3); nrm: unit normals facing the incident side (d . nrm < 0)."""
    ci = -np.einsum("ij,ij->i", d, nrm)
    k = 1.0 - eta * eta * (1.0 - ci * ci)
    ok = k > 0
    ct = np.sqrt(np.clip(k, 0, None))
    t = eta * d + (eta * ci - ct)[:, None] * nrm
    t /= np.linalg.norm(t, axis=1)[:, None]
    return t, ci, ct, ok


def trace(N, D=None, gap=0.6, dz=0.0, W=None, L=None, n=N_PMMA, baffle=True, knife=None, seed=1):
    """Return origins (N,3), directions (N,3), weights (N) in the LED-local frame, plus a flux ledger."""
    W = EMIT_W if W is None else W
    L = EMIT_L if L is None else L
    rng = np.random.default_rng(seed)
    o = np.zeros((N, 3))
    o[:, 0] = (rng.random(N) - 0.5) * L
    o[:, 2] = (rng.random(N) - 0.5) * W
    u = rng.random(N)
    ct, st, ph = np.sqrt(u), np.sqrt(1 - u), 2 * np.pi * rng.random(N)
    d = np.stack([st * np.cos(ph), -ct, st * np.sin(ph)], axis=1)
    w = np.ones(N)
    led = dict(N=N)
    if D is None:
        if knife is not None:
            hk, zk = knife
            t = hk / -d[:, 1]
            zc = o[:, 2] + t * d[:, 2]
            w[zc < zk] = 0.0
            led["knife_blocked"] = float(1 - w.mean())
        return o, d, w, led
    R = D / 2.0
    yc, zc = -(gap + R), dz
    py, pz = o[:, 1] - yc, o[:, 2] - zc
    a = d[:, 1] ** 2 + d[:, 2] ** 2
    b = 2 * (py * d[:, 1] + pz * d[:, 2])
    c = py * py + pz * pz - R * R
    disc = b * b - 4 * a * c
    hit = disc > 0
    t1 = np.where(hit, (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * a), -1)
    hit &= t1 > 0
    led["hit_rod"] = float(hit.mean())
    h = np.nonzero(hit)[0]
    P1 = o[h] + t1[h, None] * d[h]
    n1 = np.stack([np.zeros(len(h)), (P1[:, 1] - yc) / R, (P1[:, 2] - zc) / R], axis=1)
    din, ci1, ct1, ok1 = refract(d[h], n1, 1.0 / n)
    T1 = fresnel(ci1, ct1, 1.0, n)
    qy, qz = P1[:, 1] - yc, P1[:, 2] - zc
    a2 = din[:, 1] ** 2 + din[:, 2] ** 2
    t2 = -2 * (qy * din[:, 1] + qz * din[:, 2]) / a2
    P2 = P1 + t2[:, None] * din
    n2 = np.stack([np.zeros(len(h)), (P2[:, 1] - yc) / R, (P2[:, 2] - zc) / R], axis=1)
    dout, ci2, ct2, ok2 = refract(din, -n2, n)
    T2 = np.where(ok2, fresnel(ci2, ct2, n, 1.0), 0.0)
    led["fresnel_loss"] = float((1 - T1 * T2).sum() / N)
    led["tir"] = float((~ok2).sum() / N)
    o2, d2, w2 = o.copy(), d.copy(), w.copy()
    o2[h], d2[h], w2[h] = P2, dout, T1 * T2
    if baffle:
        w2[~hit] = 0.0
    w2[d2[:, 1] >= 0] = 0.0            # going back up into the PCB / holder
    led["stray"] = float(w2[~hit].sum() / N)
    led["through_rod"] = float(w2[hit].sum() / N)
    return o2, d2, w2, led


def project(o, d, w, z_e, z_page, y_e=Y_EMIT, lay=LAY, fres=False, both=False):
    """Irradiance histograms (d, x) on the active area for the warm string (and the cool one if both)."""
    N = len(w)
    keep = (w > 0) & (d[:, 2] < 0)
    oo, dd, ww = o[keep], d[keep], w[keep] * (math.pi / N)
    oz = z_e + oo[:, 2]
    oy = y_e + oo[:, 1]
    t = (z_page - oz) / dd[:, 2]
    y = oy + t * dd[:, 1]
    xr = oo[:, 0] + t * dd[:, 0]
    if fres:
        ww = ww * O.fresnel_T(-dd[:, 2])
    dist = O.ACTIVE["y1"] - y
    inY = (dist >= 0) & (dist <= D_THROW)
    apert = []                               # (x_rel at the plane, y-ok mask, x0, x1)
    for ap in O.skin():
        if ap.z <= z_page:
            continue
        tk = (ap.z - oz) / dd[:, 2]
        yk = oy + tk * dd[:, 1]
        apert.append((oo[:, 0] + tk * dd[:, 0], (yk >= ap.y0) & (yk <= ap.y1), ap.x0, ap.x1))
    out = {}
    lx = O.layout(lay)
    for col in (("W", "C") if both else ("W",)):
        H = np.zeros((len(D_EDGES) - 1, len(X_EDGES) - 1))
        for xl, c in lx:
            if c != col:
                continue
            x = xl + xr
            m = inY & (x >= XA0) & (x <= XA1)
            for xk, yok, x0, x1 in apert:
                xa = xl + xk
                m &= yok & (xa >= x0) & (xa <= x1)
            Hk, _, _ = np.histogram2d(dist[m], x[m], bins=[D_EDGES, X_EDGES], weights=ww[m])
            H += Hk
        area = np.diff(D_EDGES)[:, None] * np.diff(X_EDGES)[None, :]
        out[col] = H / area
    return out


def metrics(E, Ec=None):
    """Profile metrics comparable with optics_sim.evaluate() (x-mean over the middle 80 %)."""
    dc = 0.5 * (D_EDGES[1:] + D_EDGES[:-1])
    xc = 0.5 * (X_EDGES[1:] + X_EDGES[:-1])
    mid = (xc >= XM0) & (xc <= XM1)
    prof = E[:, mid].mean(axis=1) + 1e-30      # 1e-30: a beam that misses the page gives huge ratios, not errors
    sm = np.convolve(np.pad(prof, 1, mode="edge"), np.ones(3) / 3, mode="valid")
    at = lambda v, hw=0.75: float(prof[(dc >= v - hw) & (dc <= v + hw)].mean())
    far = float(prof[dc >= D_THROW - 2.0].mean())
    midv = at(D_THROW / 2, 1.0)
    s2, s5 = dc >= 2, dc >= 5
    band_i = np.nonzero(prof >= 0.05 * sm.max())[0]
    dA = np.diff(D_EDGES)[:, None] * np.diff(X_EDGES)[None, :]
    r = dict(
        vs_mid={f"{v}": round(at(v) / midv, 3) for v in (2, 5, 10, 20, 40)} | {"far": round(far / midv, 3)},
        near_far={f"{v}": round(at(v) / far, 2) for v in (2, 5, 10, 20, 40, 80)},
        pk_2=round(float(sm[s2].max() / far), 2),
        u2=round(float(sm[s2].max() / sm[s2].min()), 2),
        u5=round(float(sm[s5].max() / sm[s5].min()), 2),
        peak_d=round(float(dc[s2][np.argmax(sm[s2])]), 1),
        band=round(float(D_EDGES[band_i[0]]), 2) if len(band_i) else None,
        flux=round(float((E * dA).sum() / (5 * math.pi)), 4),
        lux_per_lm={k: round(v * 1e6 / math.pi, 1) for k, v in
                    dict(d2=at(2), d5=at(5), d10=at(10), d20=at(20), mid=midv, far=far).items()},
    )
    if Ec is not None:            # both strings: ends/mid and mix at d 10, scallop at 5/10/20 (warm)
        sel = lambda v: (dc >= v - 1) & (dc <= v + 1)
        both = (E + Ec)[sel(10)].mean(axis=0)
        q = len(xc) // 10
        c0 = len(xc) // 2
        r["ends_mid"] = round(float(min(both[:q].mean(), both[-q:].mean()) / both[c0 - q // 2:c0 + q // 2].mean()), 3)
        wl = sorted(x for x, c in O.layout(LAY) if c == "W")
        inner = (xc >= wl[1]) & (xc <= wl[-2])
        r["scallop"] = {f"{v}": round(float(E[sel(v)][:, inner].mean(0).max() / E[sel(v)][:, inner].mean(0).min()), 3)
                        for v in (5, 10, 20)}
        wv, cv = E[sel(10)].mean(0), Ec[sel(10)].mean(0)
        r["mix10"] = round(float(np.max(np.abs(wv / (wv + cv) - 0.5))), 3)
    r["_prof"] = (dc.tolist(), prof.tolist())
    return r


def farfield(o, d, w, dth=0.5, ds=0.05):
    """I/I0 table over theta (deg, elevation in Y-Z, + toward the page) and s = ux; symmetrised in s."""
    N = len(w)
    th = np.degrees(np.arctan2(-d[:, 2], -d[:, 1]))
    th_e = np.arange(-90, 90 + dth / 2, dth)
    s_e = np.arange(-1, 1 + ds / 2, ds)
    H, _, _ = np.histogram2d(th, d[:, 0], bins=[th_e, s_e], weights=w)
    H = 0.5 * (H + H[:, ::-1])
    I = math.pi * H / (N * math.radians(dth) * ds)
    thc, sc = 0.5 * (th_e[1:] + th_e[:-1]), 0.5 * (s_e[1:] + s_e[:-1])
    # elevation cut (|s| < 0.15) and its FWHM / peak
    cut = I[:, np.abs(sc) < 0.15].mean(axis=1)
    cs = np.convolve(cut, np.ones(5) / 5, mode="same")
    pk = int(np.argmax(cs))
    above = np.nonzero(cs >= 0.5 * cs[pk])[0]
    return dict(theta=thc, s=sc, I=I, cut=cut, peak_deg=float(thc[pk]), peak_I=float(cs[pk]),
                fwhm=float(thc[above[-1]] - thc[above[0]] + dth), lo=float(thc[above[0]]), hi=float(thc[above[-1]]))


def save_pattern(path, ff, dy, dz, meta):
    with open(path, "w") as f:
        json.dump(dict(theta_deg=ff["theta"].round(3).tolist(), s=ff["s"].round(4).tolist(),
                       table=np.round(ff["I"], 5).tolist(), dy=dy, dz=dz, meta=meta), f)


PAGES = ("FT01C", "T01C", "PLAIN")


def run_case(tr, z_e, pages=PAGES, both=False, fres=False):
    o, d, w, led = tr
    res = {}
    for pg in pages:
        E = project(o, d, w, z_e, O.PANELS[pg], both=both, fres=fres)
        res[pg] = metrics(E["W"], E.get("C"))
    return res


def strip(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def main(quick=False):
    """Screening sweep (the default mode). Arguments are parsed in cli()."""
    t0 = time.time()
    P = lambda *s: print(*s, flush=True)
    Ns = 60_000 if quick else 150_000
    Nf = 400_000 if quick else 2_000_000
    out = dict(frame="enclosure frame (optics_sim)", y_emit=Y_EMIT, n_pmma=N_PMMA, layout=LAY)

    # ---- 1. screening sweep: D x gap x dz x z_e, W 1.4, ideal baffle -------------------------------
    DS, GAPS, DZS, ZES = (2.0, 3.0, 4.0, 5.0), (0.0, 0.3, 0.6, 1.0, 1.5), (-1.2, -0.8, -0.4, 0.0, 0.4, 0.8), (12.0, 14.0, 16.0, 18.0)
    rows = []
    for D in DS:
        for g in GAPS:
            for dz in DZS:
                tr = trace(Ns, D, g, dz, EMIT_W, baffle=True, seed=7)
                ff = farfield(*tr[:3])
                for ze in ZES:
                    rr = run_case(tr, ze, ("FT01C", "PLAIN"))
                    rows.append(dict(D=D, gap=g, dz=dz, z_e=ze, through=round(tr[3]["through_rod"], 3),
                                     peak_deg=ff["peak_deg"], fwhm=ff["fwhm"],
                                     **{pg: strip(v) for pg, v in rr.items()}))
        P(f"# D {D} done {time.time() - t0:.0f}s")
    out["sweep"] = rows

    def score(r):   # worst panel's uniformity, penalise a band > 1 mm and low flux
        u = max(r[p]["u2"] for p in ("FT01C", "PLAIN"))
        band = max((r[p]["band"] or 0) for p in ("FT01C", "PLAIN"))
        return u + (100 if band > 1.0 else 0) + (100 if r["FT01C"]["flux"] < 0.12 else 0)

    rows.sort(key=score)
    P("\n## Screening: best 25 (score = worst u2 over FT01C/PLAIN; band <= 1, flux >= 0.12)")
    P("| D | gap | dz | z_e | through | aim | FWHM | FT01C u2 / pk / band / flux | PLAIN u2 / pk / band / flux |")
    P("|---|---|---|---|---|---|---|---|---|")
    for r in rows[:25]:
        f, p = r["FT01C"], r["PLAIN"]
        P(f"| {r['D']} | {r['gap']} | {r['dz']} | {r['z_e']} | {r['through']} | {r['peak_deg']:+.1f} | {r['fwhm']:.0f} | "
          f"{f['u2']} / {f['pk_2']} / {f['band']} / {f['flux']} | {p['u2']} / {p['pk_2']} / {p['band']} / {p['flux']} |")
    P("\n## Best per (D, z_e)")
    best = {}
    for r in rows:
        k = (r["D"], r["z_e"])
        if k not in best:
            best[k] = r
    for k in sorted(best):
        r = best[k]
        P(f"D {k[0]} z_e {k[1]}: gap {r['gap']} dz {r['dz']} aim {r['peak_deg']:+.1f} FWHM {r['fwhm']:.0f} | "
          f"FT01C u2 {r['FT01C']['u2']} pk {r['FT01C']['pk_2']} band {r['FT01C']['band']} flux {r['FT01C']['flux']} | "
          f"PLAIN u2 {r['PLAIN']['u2']} pk {r['PLAIN']['pk_2']} band {r['PLAIN']['band']} flux {r['PLAIN']['flux']}")
    out["best_per_D_z"] = {f"D{k[0]}_z{k[1]}": v for k, v in best.items()}
    with open(os.path.join(OUT, "rod_sweep.json"), "w") as fh:
        json.dump(out, fh, separators=(",", ":"), default=float)
    P(f"# screening written {time.time() - t0:.0f}s")


def fine_sweep(Ns=150_000):
    """Tolerance-aware sweep near the screening optimum: worst u2 over the panels and over dz +-0.2, gap +-0.25."""
    DS = (3.0, 3.175, 4.0, 4.76, 5.0)
    GAPS = (0.75, 1.0, 1.25, 1.5, 1.75, 2.0)
    DZS = tuple(round(float(v), 2) for v in np.arange(-1.0, 0.21, 0.1))
    ZES = (14.0, 16.0, 18.0)
    grid = {}
    for D in DS:
        for g in GAPS:
            for dz in DZS:
                tr = trace(Ns, D, g, dz, EMIT_W, baffle=True, seed=11)
                ff = farfield(*tr[:3])
                for ze in ZES:
                    rr = run_case(tr, ze, ("FT01C", "PLAIN"))
                    grid[(D, g, dz, ze)] = dict(aim=ff["peak_deg"], fwhm=ff["fwhm"], through=tr[3]["through_rod"],
                                                **{pg: strip(v) for pg, v in rr.items()})
    wu = lambda q: max(q[p]["u2"] for p in ("FT01C", "PLAIN"))
    rob = []
    for (D, g, dz, ze), r in grid.items():
        nb = [grid.get((D, gg, round(dz + e, 2), ze)) for gg in GAPS if abs(gg - g) <= 0.26 for e in (-0.2, 0.0, 0.2)]
        if any(q is None for q in nb):
            continue
        rob.append(dict(D=D, gap=g, dz=dz, z_e=ze, aim=r["aim"], fwhm=r["fwhm"], through=round(r["through"], 3),
                        u2_nom=wu(r), u2_rob=max(wu(q) for q in nb),
                        band=max((r[p]["band"] or 0) for p in ("FT01C", "PLAIN")),
                        flux=r["FT01C"]["flux"], pk_ft=r["FT01C"]["pk_2"], pk_pl=r["PLAIN"]["pk_2"]))
    rob.sort(key=lambda r: r["u2_rob"] + (100 if r["band"] > 1.0 else 0))
    return grid, rob


def final(pick, Nf=2_000_000, tag="pick", tol_ze=(-1.0, 1.0)):
    D, g, dz, ze = pick["D"], pick["gap"], pick["dz"], pick["z_e"]
    res = dict(pick=pick)
    tr = trace(Nf, D, g, dz, EMIT_W, baffle=True, seed=3)
    res["ledger"] = tr[3]
    ff = farfield(*tr[:3])
    res["farfield"] = {k: ff[k] for k in ("peak_deg", "peak_I", "fwhm", "lo", "hi")}
    save_pattern(os.path.join(OUT, f"rod_pattern_{tag}.json"), ff, -(g + D / 2), dz,
                 dict(D=D, gap=g, dz=dz, W=EMIT_W, L=EMIT_L, n=N_PMMA, baffle=True, note="source point = rod centre"))
    res["pages"] = {pg: run_case(tr, ze, (pg,), both=True)[pg] for pg in PAGES}
    res["pages_glossy"] = {pg: strip(run_case(tr, ze, (pg,), fres=True)[pg]) for pg in PAGES}
    var = {}
    for name, kw in (("W1.4 (package width)" if EMIT_W != 1.4 else "W1.15 (cavity)", dict(W=1.4 if EMIT_W != 1.4 else 1.15)),
                     ("no baffle", dict(baffle=False)),
                     ("n 1.586 (PC rod)", dict(n=1.586))):
        a = dict(W=EMIT_W, baffle=True, n=N_PMMA)
        a.update(kw)
        t2 = trace(Nf // 2, D, g, dz, a["W"], n=a["n"], baffle=a["baffle"], seed=5)
        var[name] = dict(ledger=t2[3], aim=farfield(*t2[:3])["peak_deg"],
                         **{pg: strip(v) for pg, v in run_case(t2, ze, PAGES).items()})
    res["variants"] = var
    tol = {}
    for ddz, dg in [(p, q) for p in (-0.2, 0.0, 0.2) for q in (-0.2, 0.0, 0.2)] + [(-0.3, 0.0), (0.3, 0.0)]:
        if True:
            t2 = trace(Nf // 2, D, g + dg, dz + ddz, EMIT_W, seed=9)
            tol[f"dz{ddz:+.1f}_gap{dg:+.1f}"] = dict(aim=farfield(*t2[:3])["peak_deg"],
                                                    **{pg: run_case(t2, ze, (pg,))[pg] for pg in PAGES})
    for dze in tol_ze:               # the whole LED row (and the PCB-registered rod) moved in z
        tol[f"z_e{dze:+.1f}"] = dict(aim=None, **{pg: run_case(tr, ze + dze, (pg,))[pg] for pg in PAGES})
    res["tolerance"] = tol
    pat = O.TabulatedPattern.load(os.path.join(OUT, f"rod_pattern_{tag}.json"))
    ev = {}
    for pg in PAGES:
        r = O.public(O.evaluate(O.sources_tabulated(ze, Y_EMIT, pat, LAY), O.PANELS[pg], "top", O.skin(), False, 0.5, 0.25))
        ev[pg] = dict(vs_mid=r["vs_mid"], pk_2=r["pk_2"], flux=r["flux"], band=r["band"], ends_mid=r["ends_mid"],
                      scallop=r["scallop"], lux_far_per_lm=r["lux_far_per_lm"], lux_mid_per_lm=r["lux_mid_per_lm"])
    res["tabulated_in_optics_sim"] = ev
    # keep-out: upper envelope (99.9 %) of page-bound rays in Y-Z, all three panels
    o, d, w = tr[:3]
    zs = np.arange(4.0, ze + dz + D / 2 + 0.01, 0.25)
    ymax = np.full(len(zs), -np.inf)
    for pg in PAGES:
        zp = O.PANELS[pg]
        k = (w > 0) & (d[:, 2] < 0)
        oo, dd = o[k], d[k]
        oz, oy = ze + oo[:, 2], Y_EMIT + oo[:, 1]
        t = (zp - oz) / dd[:, 2]
        y = oy + t * dd[:, 1]
        ok = (y <= O.ACTIVE["y1"]) & (y >= O.ACTIVE["y0"])
        for ap in O.skin():
            if ap.z > zp:
                tk = (ap.z - oz) / dd[:, 2]
                yk = oy + tk * dd[:, 1]
                ok &= (yk >= ap.y0) & (yk <= ap.y1)
        oz, oy, dd = oz[ok], oy[ok], dd[ok]
        for i, zz in enumerate(zs):
            span = (zz >= zp) & (zz <= oz)
            if span.sum() < 50:
                continue
            yy = oy[span] + (zz - oz[span]) * dd[span, 1] / dd[span, 2]
            ymax[i] = max(ymax[i], float(np.quantile(yy, 0.999)))
    res["keepout_envelope"] = dict(z=zs.round(2).tolist(),
                                   y_max_999=[None if not np.isfinite(v) else round(float(v), 2) for v in ymax])
    # the front lip that hides the rod from an eye at z 300, y 20..110
    R = D / 2
    yc, zc = Y_EMIT - g - R, ze + dz
    z_li = zc + R + 0.3
    ang = np.radians(np.linspace(0, 360, 721))
    py, pz = yc + R * np.sin(ang), zc + R * np.cos(ang)
    need = np.inf
    for ye in np.linspace(20, 110, 19):
        yl = py + (z_li - pz) * (ye - py) / (300 - pz)
        need = min(need, float(yl[pz <= z_li].min()))
    vis = [max(107.9 + (z_li + 1.0 - zp) * (ye - 107.9) / (300 - zp) for zp in O.PANELS.values())
           for ye in np.linspace(20, 110, 19)]
    res["lip"] = dict(inner_z=round(z_li, 2), bottom_y_max=round(need, 2), page_view_line_max_y=round(max(vis), 2),
                      rod_centre=(round(yc, 3), round(zc, 3)), rod_bottom_y=round(yc - R, 3))
    return res, tr, ff


def baselines(N=1_000_000):
    out = {}
    for ze in (12.0, 14.0, 16.0, 18.0):
        tr = trace(N, None)
        out[f"bare z{ze}"] = {pg: strip(v) for pg, v in run_case(tr, ze, PAGES).items()}
        best = None
        for hk in (0.5, 1.0, 1.5, 2.0, 3.0):
            for zk in (-1.0, -0.7, -0.4, 0.0, 0.4):
                t2 = trace(N // 4, None, knife=(hk, zk), seed=2)
                rr = {pg: strip(v) for pg, v in run_case(t2, ze, ("FT01C", "PLAIN")).items()}
                sc = max(rr[p]["u2"] for p in rr) + (100 if max((rr[p]["band"] or 0) for p in rr) > 1.0 else 0)
                if best is None or sc < best[0]:
                    best = (sc, hk, zk, rr, t2[3].get("knife_blocked"))
        out[f"bare+knife z{ze}"] = dict(hk=best[1], zk=best[2], blocked=best[4], **best[3])
    refs = {}
    for name, ang, y, zz in (("(a) 40 deg SMD z16 y117.2", 40, 117.2, 16), ("(a) 30 deg SMD z16 y117.2", 30, 117.2, 16),
                             ("(a) 60 deg SMD z16 y117.2", 60, 117.2, 16), ("(b) 3mm 30 deg THT z16 y116.1", 30, 116.1, 16),
                             ("(b) 3mm 40 deg THT z16 y116.1", 40, 116.1, 16), ("(a) 40 deg SMD z14 y117.2", 40, 117.2, 14)):
        m = O.exponent_for_full_angle(ang)
        refs[name] = {}
        for pg in PAGES:
            r = O.public(O.evaluate(O.sources_external(zz, y, 0.0, LAY, m), O.PANELS[pg], "top", O.skin(), False, 0.5, 0.25))
            refs[name][pg] = dict(vs_mid=r["vs_mid"], pk_2=r["pk_2"], flux=r["flux"], band=r["band"], ends_mid=r["ends_mid"],
                                  scallop=r["scallop"], lux_far_per_lm=r["lux_far_per_lm"], lux_mid_per_lm=r["lux_mid_per_lm"],
                                  I0_over_lambertian=round((m + 1) / 2, 2))
    out["refs_cos_m"] = refs
    return out


# ---- rev 2: LCSC LED (Hongli HL-A-3014H421W), PCB underside 118.61 -----------------------------------------------
# Flux per LED at 13.3 mA = datasheet flux at 30 mA x 0.50 (Hongli p.5 "Forward Current vs Relative Intensity":
# ~0.40 at 10 mA, ~0.72 at 20 mA, 1.0 at 30 mA).  3000 K: 12 min / 13 typ lm; 6000 K: 13 min / 14 typ lm (p.3).
FLUX_13MA = dict(warm_typ=13.0 * 0.50, warm_min=12.0 * 0.50, cool_typ=14.0 * 0.50, cool_min=13.0 * 0.50)


def keepout_rule(env, z_hi, margin=0.3):
    """Linear upper bound y = a + b (z - 4) of the 99.9 % envelope over z 4..z_hi, plus margin."""
    z = np.array(env["z"])
    y = np.array([np.nan if v is None else v for v in env["y_max_999"]], dtype=float)
    k = np.isfinite(y) & (z <= z_hi + 1e-9)
    b, a = np.polyfit(z[k] - 4.0, y[k], 1)
    a = a + float(np.max(y[k] - (a + b * (z[k] - 4.0))))
    return dict(a=round(float(a + margin), 2), b=round(float(b), 3), z_hi=round(float(z_hi), 2),
                env={f"{zz:.2f}": round(float(yy), 2) for zz, yy in zip(z[k], y[k])})


def rev2(quick=False, at=None, ze=16.0, name="rev2"):
    t0 = time.time()
    P = lambda *s: print(*s, flush=True)
    Ns = 50_000 if quick else 150_000
    DS = (3.0, 3.175, 4.0, 4.76, 5.0)
    GAPS = (1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5)
    DZS = tuple(round(float(v), 2) for v in np.arange(-0.7, 0.31, 0.1))
    out = dict(frame="enclosure frame (optics_sim)", y_pcb_under=Y_PCB_UNDER, y_emit=Y_EMIT, emit_w=EMIT_W,
               emit_l=EMIT_L, n_pmma=N_PMMA, layout=LAY, z_e=ze, flux_13mA=FLUX_13MA)
    grid = {}
    if at is None:
        for D in DS:
            for g in GAPS:
                for dz in DZS:
                    tr = trace(Ns, D, g, dz, EMIT_W, baffle=True, seed=11)
                    ff = farfield(*tr[:3])
                    rr = run_case(tr, ze, ("FT01C", "PLAIN"))
                    grid[(D, g, dz)] = dict(aim=ff["peak_deg"], fwhm=ff["fwhm"], through=tr[3]["through_rod"],
                                            **{pg: strip(v) for pg, v in rr.items()})
            P(f"# rev2 sweep D {D} {time.time() - t0:.0f}s")
        wu = lambda q: max(q[p]["u2"] for p in ("FT01C", "PLAIN"))
        rob = []
        for (D, g, dz), r in grid.items():
            # full neighbourhood only (gap -0.25/0/+0.25 and dz -0.2/0/+0.2): grid-edge points are not ranked
            nb = [grid.get((D, round(g + eg, 2), round(dz + e, 2))) for eg in (-0.25, 0.0, 0.25) for e in (-0.2, 0.0, 0.2)]
            if any(q is None for q in nb):
                continue
            fl = [q["FT01C"]["flux"] for q in nb]
            rob.append(dict(D=D, gap=g, dz=dz, aim=r["aim"], fwhm=r["fwhm"], through=round(r["through"], 3),
                            flux_swing=round(max(fl) / max(min(fl), 1e-9), 2),
                            u2_nom=wu(r), u2_rob=max(wu(q) for q in nb),
                            band=max((r[p]["band"] or 0) for p in ("FT01C", "PLAIN")),
                            flux=r["FT01C"]["flux"], pk_ft=r["FT01C"]["pk_2"], pk_pl=r["PLAIN"]["pk_2"]))
        # a page-flux swing > 2.2x over the +-0.2 neighbourhood (unit-to-unit brightness) is penalised like a band
        rob.sort(key=lambda r: r["u2_rob"] + (100 if r["band"] > 1.0 else 0) + (100 if r["flux_swing"] > 2.2 else 0))
        best = {}
        for r in rob:
            best.setdefault(r["D"], r)
        P("| D | gap | dz | aim | FWHM | u2 nom | u2 robust | band | flux | pk FT01C / PLAIN |")
        for r in rob[:25]:
            P(f"| {r['D']} | {r['gap']} | {r['dz']} | {r['aim']:+.1f} | {r['fwhm']:.0f} | {r['u2_nom']} | {r['u2_rob']} | "
              f"{r['band']} | {r['flux']} (swing {r['flux_swing']}) | {r['pk_ft']} / {r['pk_pl']} |")
        P("## robust best per D")
        for D in sorted(best):
            r = best[D]
            P(f"D {D}: gap {r['gap']} dz {r['dz']} aim {r['aim']:+.1f} FWHM {r['fwhm']:.0f} u2 {r['u2_nom']} "
              f"rob {r['u2_rob']} band {r['band']} flux {r['flux']} pk {r['pk_ft']}/{r['pk_pl']}")
        # pick: within 5 % of the best robust u2 (band <= 1), take the highest page flux
        ok = [r for r in rob if r["band"] <= 1.0 and r["flux_swing"] <= 2.2]
        lim = 1.05 * ok[0]["u2_rob"]
        pick = max((r for r in ok if r["u2_rob"] <= lim), key=lambda r: r["flux"])
        out["sweep_top"] = rob[:40]
        out["best_per_D"] = {str(k): v for k, v in best.items()}
        at = (pick["D"], pick["gap"], pick["dz"])
        P(f"# pick {at}")
    D, g, dz = at
    res, tr, ff = final(dict(D=D, gap=g, dz=dz, z_e=ze), Nf=1_000_000 if quick else 2_000_000, tag=name,
                        tol_ze=(-1.0, -0.3, 0.3, 1.0))
    for pg in PAGES:
        res["pages"][pg].pop("_prof", None)
    for v in res["tolerance"].values():
        for pg in PAGES:
            v[pg] = strip(v[pg])
    # lux with the Hongli flux at 13.3 mA, a larger ray count, both strings
    t3 = trace(600_000 if quick else 3_000_000, D, g, dz, EMIT_W, seed=77)
    lux = {}
    for pg in PAGES:
        E = project(*t3[:3], ze, O.PANELS[pg], both=True)
        m = strip(metrics(E["W"], E["C"]))
        m["lux_warm_typ"] = {k: round(v * FLUX_13MA["warm_typ"]) for k, v in m["lux_per_lm"].items()}
        m["lux_warm_min"] = {k: round(v * FLUX_13MA["warm_min"]) for k, v in m["lux_per_lm"].items()}
        m["lux_cool_typ"] = {k: round(v * FLUX_13MA["cool_typ"]) for k, v in m["lux_per_lm"].items()}
        lux[pg] = m
        P(pg, "pk", m["pk_2"], "u2", m["u2"], "vs_mid", m["vs_mid"], "band", m["band"], "flux", m["flux"],
          "ends", m.get("ends_mid"), "scallop", m.get("scallop"), "lux", m["lux_warm_typ"])
    res["mc3M"] = lux
    R_ = D / 2
    yc, zc = Y_EMIT - g - R_, ze + dz
    res["geometry"] = dict(y_pcb_under=Y_PCB_UNDER, y_emit=Y_EMIT, z_e=ze, rod_D=D, rod_axis_y=round(yc, 3),
                           rod_axis_z=round(zc, 3), rod_top_y=round(yc + R_, 3), rod_bottom_y=round(yc - R_, 3),
                           wall_mz_inner=round(zc - R_ - 0.1, 2), wall_mz_lower_y=round(yc, 2),
                           wall_pz_inner=round(zc + R_ + 0.2, 2), led_x=[round(x, 3) for x, _ in O.layout(LAY)])
    res["keepout_rule"] = keepout_rule(res["keepout_envelope"], zc - R_ - 0.1)
    out["final"] = res
    with open(os.path.join(OUT, f"rod_{name}.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    P(json.dumps(dict(geometry=res["geometry"], keepout=res["keepout_rule"], lip=res["lip"], ff=res["farfield"],
                      ledger=res["ledger"]), default=float))
    for k, v in res["tolerance"].items():
        P("tol", k, "aim", v["aim"], {pg: (v[pg]["u2"], v[pg]["pk_2"], v[pg]["band"], v[pg]["flux"]) for pg in PAGES})
    for k, v in res["variants"].items():
        P("var", k, v.get("aim"), {pg: (v[pg]["u2"], v[pg]["pk_2"], v[pg]["flux"]) for pg in PAGES})
    for pg in PAGES:
        P("pages", pg, {k: res["pages"][pg].get(k) for k in ("vs_mid", "pk_2", "u2", "band", "flux", "ends_mid")})
    P(f"# rev2 done {time.time() - t0:.0f}s")


def _floats(text, n, flag, ap):
    """Parse 'a,b,c' into n floats, or stop with a usage error naming the flag."""
    try:
        vals = tuple(float(v) for v in text.split(","))
    except ValueError:
        vals = ()
    if len(vals) != n:
        ap.error(f"{flag} expects {n} comma-separated numbers, got {text!r}")
    return vals


def cli():
    ap = argparse.ArgumentParser(
        description="Clear-PMMA rod-lens ray trace for the external top-edge light (modes: see the module docstring).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--final", action="store_true",
                      help="rev 1 tolerance-aware fine sweep -> design/optics/rod_fine.json")
    mode.add_argument("--pick", metavar="D,gap,dz,z_e",
                      help="rev 1 pick report for one geometry -> design/optics/rod_final.json")
    mode.add_argument("--rev2", action="store_true",
                      help="rev 2: fine sweep at z_e 16, robust pick, lux, tolerance -> design/optics/rod_<name>.json")
    ap.add_argument("--quick", action="store_true", help="fewer rays (default screening sweep and --rev2)")
    ap.add_argument("--at", metavar="D,gap,dz",
                    help="with --rev2: skip the sweep and evaluate this rod geometry (e.g. 4.0,2.0,-0.2)")
    ap.add_argument("--name", default="rev2", help="with --rev2: output tag, writes rod_<name>.json (default rev2)")
    a = ap.parse_args()
    if not a.rev2 and (a.at is not None or a.name != "rev2"):
        ap.error("--at and --name only apply with --rev2")
    if a.final:
        t0 = time.time()
        grid, rob = fine_sweep()
        print(f"# fine sweep {time.time() - t0:.0f}s")
        print("| D | gap | dz | z_e | aim | FWHM | through | u2 nominal | u2 robust | band | flux | pk FT01C / PLAIN |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in rob[:30]:
            print(f"| {r['D']} | {r['gap']} | {r['dz']} | {r['z_e']} | {r['aim']:+.1f} | {r['fwhm']:.0f} | {r['through']} | "
                  f"{r['u2_nom']} | {r['u2_rob']} | {r['band']} | {r['flux']} | {r['pk_ft']} / {r['pk_pl']} |")
        bestz = {}
        for r in rob:
            bestz.setdefault((r["D"], r["z_e"]), r)
        print("\n## robust best per (D, z_e)")
        for k in sorted(bestz):
            r = bestz[k]
            print(f"D {k[0]} z_e {k[1]}: gap {r['gap']} dz {r['dz']} aim {r['aim']:+.1f} FWHM {r['fwhm']:.0f} "
                  f"u2 {r['u2_nom']} rob {r['u2_rob']} band {r['band']} flux {r['flux']} pk {r['pk_ft']}/{r['pk_pl']}")
        with open(os.path.join(OUT, "rod_fine.json"), "w") as fh:
            json.dump(dict(robust=rob, best_per_D_z={f"D{k[0]}_z{k[1]}": v for k, v in bestz.items()}), fh,
                      separators=(",", ":"), default=float)
        print(f"# written {time.time() - t0:.0f}s")
    elif a.pick is not None:
        D, g, dz, ze = _floats(a.pick, 4, "--pick", ap)
        t0 = time.time()
        res, tr, ff = final(dict(D=D, gap=g, dz=dz, z_e=ze))
        res["baselines"] = baselines()
        for pg in PAGES:
            res["pages"][pg].pop("_prof", None)
        for v in res["tolerance"].values():
            for pg in PAGES:
                v[pg] = strip(v[pg])
        with open(os.path.join(OUT, "rod_final.json"), "w") as fh:
            json.dump(res, fh, indent=1, default=float)
        print(f"# final {time.time() - t0:.0f}s")
    elif a.rev2:
        at = _floats(a.at, 3, "--at", ap) if a.at is not None else None
        rev2(quick=a.quick, at=at, name=a.name)
    else:
        main(quick=a.quick)


if __name__ == "__main__":
    cli()
