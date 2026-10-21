"""Figures + follow-up numbers for design/optics-final.md (reads design/optics/rod_final.json).

    python tools/rod_report.py        -> design/optics/rod_final.png, rod_report.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import optics_sim as O  # noqa: E402
import rod_lens as RL  # noqa: E402

OUT = O.OUT
fin = json.load(open(os.path.join(OUT, "rod_final.json")))
pk = fin["pick"]
D, G, DZ, ZE = pk["D"], pk["gap"], pk["dz"], pk["z_e"]
rep = {}

# 1. knife-edge baseline with a flux floor (the run in rod_lens.baselines() let the knife block everything)
kn = {}
for ze in (12.0, 14.0, 16.0, 18.0):
    best = None
    for hk in (0.5, 1.0, 1.5, 2.0, 3.0):
        for zk in (-1.0, -0.7, -0.4, 0.0, 0.4):
            t2 = RL.trace(250_000, None, knife=(hk, zk), seed=2)
            rr = {pg: RL.strip(v) for pg, v in RL.run_case(t2, ze, ("FT01C", "PLAIN")).items()}
            if min(rr[p]["flux"] for p in rr) < 0.05:
                continue
            sc = max(rr[p]["u2"] for p in rr) + (100 if max((rr[p]["band"] or 0) for p in rr) > 1.0 else 0)
            if best is None or sc < best[0]:
                best = (sc, hk, zk, rr)
    kn[f"z{ze}"] = dict(hk=best[1], zk=best[2], **{p: {k: best[3][p][k] for k in ("u2", "pk_2", "band", "flux", "vs_mid")}
                                                    for p in best[3]})
rep["bare_knife_flux_floor_0.05"] = kn

# 2. lateral metrics with the tabulated pattern (far-field; fine for across-x ratios): layout w12.5 vs w13.5
pat = O.TabulatedPattern.load(os.path.join(OUT, "rod_pattern_pick.json"))
lay = {}
for L in ("L5-w12.5-s1.2", "L5-w13.5-s1.2"):
    for pg in ("FT01C", "PLAIN"):
        r = O.public(O.evaluate(O.sources_tabulated(ZE, RL.Y_EMIT, pat, L), O.PANELS[pg], "top", O.skin(), False, 0.5, 0.25))
        lay[f"{L} {pg}"] = dict(ends_mid=r["ends_mid"], scallop=r["scallop"], mix=r["mix"], pk_2=r["pk_2"])
rep["layouts_tabulated"] = lay

# 3. far-field toward the reader (theta -89..-72) and elevation cuts for the figure
tr = RL.trace(1_000_000, D, G, DZ, 1.4, seed=21)
ff = RL.farfield(*tr[:3])
th = ff["theta"]
rep["I_toward_reader_max"] = float(ff["I"][(th <= -70) & (th >= -90)].max())
rep["pick_elev_cut"] = dict(peak_deg=ff["peak_deg"], fwhm=ff["fwhm"], lo=ff["lo"], hi=ff["hi"], peak_I=ff["peak_I"])
cuts = {"pick: D 4.0, gap 1.75, dz -0.1": ff}
for lab, (d_, g_, z_) in (("D 3.0, gap 1.5, dz 0", (3.0, 1.5, 0.0)), ("D 5.0, gap 2.0, dz 0", (5.0, 2.0, 0.0))):
    cuts[lab] = RL.farfield(*RL.trace(600_000, d_, g_, z_, 1.4, seed=4)[:3])
json.dump(rep, open(os.path.join(OUT, "rod_report.json"), "w"), indent=1, default=float)
print(json.dumps(rep, indent=1, default=float))

# ---- figure ------------------------------------------------------------------------------------------
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(2, 2, figsize=(15, 11))
# (A) elevation cuts
a = ax[0, 0]
for lab, f in cuts.items():
    a.plot(f["theta"], np.convolve(f["cut"], np.ones(3) / 3, mode="same"), lw=2 if "pick" in lab else 1.2,
           label=f"rod {lab} (FWHM {f['fwhm']:.0f}, aim {f['peak_deg']:+.1f})")
tt = np.linspace(-90, 90, 361)
a.plot(tt, np.cos(np.radians(tt)), "k--", lw=1, label="bare LUXEON 3014 (Lambertian)")
m40 = O.exponent_for_full_angle(40)
a.plot(tt, (m40 + 1) / 2 * np.cos(np.radians(tt)) ** m40, "k:", lw=1, label="ideal 40 deg LED, same lumens")
yc, zc = RL.Y_EMIT - G - D / 2, ZE + DZ
lo = math.degrees(math.atan2(zc - O.PANELS["FT01C"], yc - O.ACTIVE["y0"]))
hi = math.degrees(math.atan2(zc - O.PANELS["FT01C"], yc - O.ACTIVE["y1"]))
a.axvspan(lo, hi, color="0.9", zorder=0, label=f"page seen from the rod centre ({lo:.0f}..{hi:.0f} deg, FT01C)")
a.set_xlim(-60, 80)
a.set_xlabel("elevation theta in Y-Z (deg; + = toward the page)")
a.set_ylabel("I / I0 (I0 = bare LED on-axis)")
a.set_title("Elevation intensity (|s| < 0.15 cut), 3D ray trace, PMMA n 1.491, W 1.4 emitter, black channel")
a.legend(fontsize=7)
a.grid(alpha=0.3)
# (B) page profiles (Monte Carlo)
b = ax[0, 1]
trP = RL.trace(1_000_000, D, G, DZ, 1.4, seed=31)
trB = RL.trace(1_000_000, None, seed=32)
for pg, st in (("FT01C", "-"), ("T01C", "--"), ("PLAIN", ":")):
    m = RL.metrics(RL.project(*trP[:3], ZE, O.PANELS[pg])["W"])
    dc, pr = m["_prof"]
    pr = np.array(pr)
    b.plot(dc, pr / np.interp(46.4, dc, pr), st, color="C0", lw=2, label=f"rod pick, {pg} (peak/far {m['pk_2']})")
mB = RL.metrics(RL.project(*trB[:3], ZE, O.PANELS["FT01C"])["W"])
dc, pr = mB["_prof"]
pr = np.array(pr)
b.plot(dc, pr / np.interp(46.4, dc, pr), color="0.4", lw=1.2, label=f"bare 3014 z16, FT01C (peak/far {mB['pk_2']})")
r40 = O.evaluate(O.sources_external(16, 117.2, 0, RL.LAY, O.exponent_for_full_angle(40)), O.PANELS["FT01C"], "top",
                 O.skin(), False, 0.5, 0.25, keep=True)
dp, pp = r40["_prof"]
b.plot(dp, pp / np.interp(46.4, dp, pp), color="C3", lw=1.2, label=f"ideal 40 deg LED z16, FT01C (peak/far {r40['pk_2']})")
b.set_yscale("log")
b.set_ylim(0.1, 30)
b.set_xlabel("d = distance below the active area's top edge (mm)")
b.set_ylabel("irradiance / value at mid-page")
b.set_title("Page profile (x-mean over the middle 80 %), warm string, near-field Monte Carlo")
b.legend(fontsize=7)
b.grid(alpha=0.3, which="both")
# (C) Y-Z section
c = ax[1, 0]
ang = np.linspace(0, math.pi / 2, 30)
case_z = [6.0, 6.0] + list(4.2 + 1.8 * np.cos(ang)) + [-4.7] + list(-4.7 - 2.0 * np.sin(ang)) + [-6.7]
case_y = [109.1, 113.8] + list(113.8 + 1.8 * np.sin(ang)) + [115.6] + list(113.6 + 2.0 * np.cos(ang)) + [100]
c.plot(case_z, case_y, "k-", lw=1.5)
c.plot([6.0, 5.4, 4.98], [109.1, 108.5, 108.5], "k-", lw=1.5)
c.fill_between([42.582 - 44, 0], 0, 0)  # (keeps the axes simple)
for pg, col in (("FT01C", "C0"), ("T01C", "C1"), ("PLAIN", "C2")):
    c.plot([O.PANELS[pg]] * 2, [100, O.ACTIVE["y1"]], color=col, lw=2, label=f"page {pg} z {O.PANELS[pg]:.2f}")
o, d_, w = trP[:3]
k = np.nonzero((w > 0) & (d_[:, 2] < 0))[0]
oz, oy = ZE + o[k, 2], RL.Y_EMIT + o[k, 1]
t = (O.PANELS["FT01C"] - oz) / d_[k, 2]
yh = oy + t * d_[k, 1]
ok = (yh <= O.ACTIVE["y1"]) & (yh >= O.ACTIVE["y0"])
for ap in O.skin():
    if ap.z > O.PANELS["FT01C"]:
        tk = (ap.z - oz) / d_[k, 2]
        yk = oy + tk * d_[k, 1]
        ok &= (yk >= ap.y0) & (yk <= ap.y1)
sel = np.random.default_rng(0).choice(np.nonzero(ok)[0], 250, replace=False)
for i in sel:
    c.plot([oz[i], O.PANELS["FT01C"]], [oy[i], yh[i]], color="gold", lw=0.4, alpha=0.6)
env = fin["keepout_envelope"]
ez = [z for z, y in zip(env["z"], env["y_max_999"]) if y is not None]
ey = [y for y in env["y_max_999"] if y is not None]
c.plot(ez, np.array(ey) + 0.3, "r-", lw=1.5, label="keep-out top (99.9 % envelope + 0.3)")
c.add_patch(plt.Circle((zc, yc), D / 2, fill=False, color="C0", lw=1.5))
c.add_patch(plt.Rectangle((ZE - 0.7, RL.Y_EMIT), 1.4, 0.7, color="orange"))
c.add_patch(plt.Rectangle((-6.0, RL.Y_PCB_UNDER), 24.5, 1.6, color="green", alpha=0.4))
c.plot([zc - D / 2 - 0.1] * 2, [yc, RL.Y_EMIT], "k-", lw=2)
c.plot([zc + D / 2 + 0.1] * 2, [yc, RL.Y_EMIT], "k-", lw=2)
lip = fin["lip"]
c.add_patch(plt.Rectangle((lip["inner_z"], 110.0), 1.0, RL.Y_PCB_UNDER + 1.6 - 110.0, color="0.2", alpha=0.7))
for ye in (20, 110):
    zz = np.array([zc, 22])
    c.plot(zz, yc - D / 2 + (zz - zc) * (ye - (yc - D / 2)) / (300 - zc), "m--", lw=0.8)
c.text(19.4, 110.2, "front lip\n(bottom y 110.0)", fontsize=7)
c.text(7, 117, "PCB (underside y 118.14)", fontsize=7)
c.text(zc - 1.3, yc - 3.3, f"PMMA rod D {D}", fontsize=7, color="C0")
c.text(19.5, 112.2, "sightlines to eye\n(y 20 / 110, z 300)", fontsize=7, color="m")
c.set_xlim(-8, 23)
c.set_ylim(104, 121)
c.set_aspect("equal")
c.set_xlabel("z (mm, + toward the viewer)")
c.set_ylabel("y (mm, + = top edge)")
c.set_title("Y-Z section: case, pick geometry, page-bound rays to FT01C, keep-out, lip")
c.legend(fontsize=7, loc="lower left")
c.grid(alpha=0.3)
# (D) tolerance
e = ax[1, 1]
for kk, (ddz, dg) in enumerate([(a_, b_) for a_ in (-0.2, 0.0, 0.2) for b_ in (-0.2, 0.0, 0.2)]):
    t2 = RL.trace(600_000, D, G + dg, DZ + ddz, 1.4, seed=40 + kk)
    m = RL.metrics(RL.project(*t2[:3], ZE, O.PANELS["FT01C"])["W"])
    dc, pr = m["_prof"]
    pr = np.array(pr)
    e.plot(dc, pr / np.interp(46.4, dc, pr), lw=2 if (ddz == 0 and dg == 0) else 0.9,
           label=f"dz {DZ + ddz:+.1f}, gap {G + dg:.2f}: peak/far {m['pk_2']}, flux {m['flux']:.3f}")
e.set_yscale("log")
e.set_ylim(0.1, 5)
e.set_xlabel("d (mm)")
e.set_ylabel("irradiance / mid-page")
e.set_title("Tolerance, FT01C: rod centre dz +-0.2, gap +-0.2 (printed holder)")
e.legend(fontsize=7)
e.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "rod_final.png"), dpi=110)
print("figure written")
