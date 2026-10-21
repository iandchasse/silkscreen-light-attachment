"""Bare-LED page profile for rev B with tools/optics_sim.py (geometry-only model, see its docstring).

120 deg LEDs, emitter centre y 115.90 (the emitter face), z 9.50, no tilt, layout L5-w13.5-s1.9
(pairs at x 3 / 16.5 / 30 / 43.5 / 57, warm/cool at +-1.9), case skin occluders only: the housing
blocks nothing on the way to the page (checked in build.py). Writes out/optics.json.
    python optics_report.py
"""
import importlib.util
import json
import sys

import numpy as np

import params as P

spec = importlib.util.spec_from_file_location('optics_sim', P.OPTICS)
O = importlib.util.module_from_spec(spec)
sys.modules['optics_sim'] = O
spec.loader.exec_module(O)

LAY, Z, Y = 'L5-w13.5-s1.9', 9.50, P.EMIT_Y
res = {'model': f'optics_sim external, 120 deg (m=1), z {Z}, y {Y}, tilt 0, layout {LAY}, case skin occluders', 'pages': {}}
m = O.exponent_for_full_angle(120.0)
for page in ('FT01C', 'T01C', 'PLAIN'):
    zp = O.PANELS[page]
    src = O.sources_external(Z, Y, 0.0, LAY, m)
    r = O.evaluate(src, zp, 'top', O.skin(), False, 0.5, 0.25, keep=True)
    dp, prof = r['_prof']
    D = P.ACTIVE['y1'] - P.ACTIVE['y0']
    mid = float(np.interp(D / 2, dp, prof))
    vs = {str(d): round(float(np.interp(d, dp, prof)) / mid, 2) for d in (2, 10, 20, 40)}
    vs['far'] = round(float(prof[-1]) / mid, 2)
    pub = O.public(r)
    res['pages'][page] = dict(z_page=zp, vs_mid=vs, band_mm=pub['band'], band_worst_col_mm=pub['band_col'],
                              flux_on_page=pub['flux'], near_far=pub['near_far'], nf_10_40=pub['nf_10_40'],
                              minmax_low80=pub['minmax_low80'], ends_mid=pub['ends_mid'], mix=pub['mix'],
                              lux_far_per_lm=pub['lux_far_per_lm'], lux_mid_per_lm=pub['lux_mid_per_lm'])
    print(page, json.dumps(res['pages'][page]))
P.OUT.mkdir(exist_ok=True)
(P.OUT / 'optics.json').write_text(json.dumps(res, indent=1))
