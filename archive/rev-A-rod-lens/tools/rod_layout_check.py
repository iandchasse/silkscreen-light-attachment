"""Final-layout check for the rod pick: near-field Monte Carlo profile + lux, and lateral metrics.
    python tools/rod_layout_check.py  -> design/optics/rod_layout_check.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import optics_sim as O  # noqa: E402
import rod_lens as RL  # noqa: E402

D, G, DZ, ZE = 4.0, 1.75, -0.1, 16.0
FLUX = dict(warm_typ=24.3 * 0.24, warm_min=19.0 * 0.24, cool_typ=26.0 * 0.24)   # DS208 Table 1 x Fig. 3 (13.3 mA)
tr = RL.trace(3_000_000, D, G, DZ, 1.4, seed=77)
out = {}
for lay in ("L5-w12.5-s1.9", "L5-w13.5-s1.9"):
    RL.LAY = lay
    for pg in RL.PAGES:
        E = RL.project(*tr[:3], ZE, O.PANELS[pg], lay=lay, both=True)
        m = RL.strip(RL.metrics(E["W"], E["C"]))
        m["lux_warm_typ"] = {k: round(v * FLUX["warm_typ"]) for k, v in m["lux_per_lm"].items()}
        m["lux_warm_min"] = {k: round(v * FLUX["warm_min"]) for k, v in m["lux_per_lm"].items()}
        # lateral metrics from the smooth tabulated pattern (the MC bins are too noisy for across-x ratios)
        pat = O.TabulatedPattern.load(os.path.join(O.OUT, "rod_pattern_pick.json"))
        r = O.public(O.evaluate(O.sources_tabulated(ZE, RL.Y_EMIT, pat, lay), O.PANELS[pg], "top", O.skin(), False, 0.5, 0.25))
        m["tab_lateral"] = dict(ends_mid=r["ends_mid"], scallop=r["scallop"], mix=r["mix"])
        out[f"{lay} {pg}"] = m
        print(lay, pg, m["pk_2"], m["u2"], m["vs_mid"], m["band"], m["flux"], m["lux_warm_typ"], m["tab_lateral"])
# reference: an ideal Lambertian lateral pattern (120 deg bare LED) for the lateral metrics with the same layout
for lay in ("L5-w12.5-s1.9", "L5-w13.5-s1.9"):
    r = O.public(O.evaluate(O.sources_external(ZE, RL.Y_EMIT, 0, lay, 1.0), O.PANELS["FT01C"], "top", O.skin(), False, 0.5, 0.25))
    out[f"bare120 {lay} FT01C lateral"] = dict(ends_mid=r["ends_mid"], scallop=r["scallop"], mix=r["mix"])
    print("bare120", lay, out[f"bare120 {lay} FT01C lateral"])
out["flux_lm_13mA"] = FLUX
json.dump(out, open(os.path.join(O.OUT, "rod_layout_check.json"), "w"), indent=1, default=float)
