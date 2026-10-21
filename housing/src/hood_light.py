"""Page light with the rev C hood: a thin wrapper over tools/visor_reflector_sim.py (geometry-only model; the LED row plus a
diffuse Lambertian bounce off the flat inner face of the hood, reflectance R). All numbers are relative to the bare-LED
page light at mid-page (rev B / today = 1.00 at the page middle).

    python hood_light.py        # prints the table
"""
import sys

import numpy as np

import params as P

sys.path.insert(0, str(P.A / 'tools'))
import visor_reflector_sim as V     # noqa: E402  (numpy only)


def hood_light(x_range=(-2.8, 62.8)):
    """Returns {'model': str, 'pages': {page: {case: summary}}}; summary keys: d2, d10, d20, mid, d70, bottom, top2_20,
    bottom_half, ratio (page light / bare-LED mid-page; top2_20 = mean over 2..20 mm below the active top, bottom_half =
    mean over the lower half of the active area)."""
    V.VIS_X = x_range
    y_top, y_lip, tilt = P.PCB_Y0, P.HOOD_LIP_Y, -P.HOOD_FLARE
    cases = [('bare LEDs (rev B, no bounce)', None),
             ('rev B visor, white print', (y_top, 115.2, 0.0, 0.80)),
             ('rev C hood, white print R0.80', (y_top, y_lip, tilt, 0.80)),
             ('rev C hood, light grey R0.50', (y_top, y_lip, tilt, 0.50)),
             ('rev C hood, black R0.05', (y_top, y_lip, tilt, 0.05))]
    out = {'model': (f'tools/visor_reflector_sim.py: 10 LEDs (Lambertian about -Y, z 9.5), flat diffuse reflector from '
                     f'(y {y_top}, z {P.VISOR_Z0}) to the lip y {y_lip}, flared {P.HOOD_FLARE} deg, x {x_range[0]}..{x_range[1]}; '
                     f'case window occluders as in the sim; middle 80 % of the page width'),
           'pages': {}}
    for page, pz in V.PAGES.items():
        base = V.direct(pz)
        base_mid = float(np.interp(46.4, V.ds, base.mean(axis=1)))
        rows = {}
        for name, c in cases:
            E = base if c is None else base + V.diffuse(pz, *c[:3], c[3])
            rows[name] = {k: round(float(v), 3) for k, v in V.summary(E, base_mid).items()}
        out['pages'][page] = rows
    return out


if __name__ == '__main__':
    r = hood_light()
    print(r['model'])
    for page, rows in r['pages'].items():
        print(f'\n{page}')
        print(f"{'case':36s} {'top2-20':>8s} {'d10':>6s} {'d20':>6s} {'mid':>6s} {'btm half':>8s} {'top/btm':>8s}")
        for n, s in rows.items():
            print(f"{n:36s} {s['top2_20']:8.2f} {s['d10']:6.2f} {s['d20']:6.2f} {s['mid']:6.2f} {s['bottom_half']:8.2f} {s['ratio']:8.1f}")
