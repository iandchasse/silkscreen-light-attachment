"""Visor reflector study for the rev B cap (enclosure frame E, mm; geometry only).

Compares the page light from the bare LED row with what a reflector on the visor's inner face adds:
  - specular (a strip of mirror / aluminium tape, reflectance R): each LED gets a mirror image across the visor plane,
    and a page point receives the image's light only if the line image -> page crosses the finite mirror;
  - diffuse (a white print, Lambertian, reflectance R): the visor face is split into patches lit by the LEDs, each
    re-emitting R * E / pi.

Run:  python tools/visor_reflector_sim.py            (system python with numpy)
"""
import numpy as np

# ---- geometry (housing/src/params.py, pcb/build/geometry.json, design/optics-sweep.md) ----
LED_X = np.array([1.1, 14.6, 28.1, 41.6, 55.1, 4.9, 18.4, 31.9, 45.4, 58.9])   # warm + cool, both strings lit
LED_Y, LED_Z = 115.90, 9.50                  # emitter face centre
PCB_UNDER = 116.60
VIS_X = (-3.0, 63.0)                         # mirror strip length along X
ACT_X, ACT_Y = (2.16, 57.84), (15.10, 107.90)
PAGES = {"PLAIN": 3.926, "FT01C": 4.98}
# window occluders: a ray must cross each plane z = zo at y <= yo (front face edge, bevel corner, lip underside)
OCC = [(6.00, 109.10), (5.40, 108.50), (4.98, 108.50)]

xs = np.linspace(ACT_X[0] + 0.1 * (ACT_X[1] - ACT_X[0]), ACT_X[1] - 0.1 * (ACT_X[1] - ACT_X[0]), 23)   # middle 80 %
ds = np.arange(0.5, ACT_Y[1] - ACT_Y[0] + 0.01, 1.0)                 # distance below the active top
ys = ACT_Y[1] - ds
PX, PY = np.meshgrid(xs, ys)                                         # (ny, nx)


def clear(ys_, zs_, py, pz):
    """True where the straight ray (ys_, zs_) -> (py, pz) passes every window occluder."""
    ys_, zs_, py = np.asarray(ys_, float), np.asarray(zs_, float), np.asarray(py, float)
    ok = np.ones(np.broadcast(ys_, zs_, py).shape, bool)
    for zo, yo in OCC:
        crosses = np.logical_and(zs_ > zo, pz < zo)
        with np.errstate(divide="ignore", invalid="ignore"):
            yc = ys_ + (py - ys_) * (zs_ - zo) / (zs_ - pz)
        ok &= np.logical_or(~crosses, yc <= yo + 1e-9)
    return ok


def lam_down(dx, dy, dz):
    """Lambertian LED about -Y: intensity per unit flux-ish, 0 behind the emitter."""
    r = np.sqrt(dx * dx + dy * dy + dz * dz)
    return np.clip(-dy / r, 0, None), r


def direct(pz):
    E = np.zeros_like(PX)
    for lx in LED_X:
        dx, dy, dz = PX - lx, PY - LED_Y, pz - LED_Z
        I, r = lam_down(dx, dy, dz)
        E += I * (LED_Z - pz) / r / r ** 2 * clear(LED_Y, LED_Z, PY, pz)
    return E


def mirror_line(y_top, y_bot, tilt_deg, z_top=11.30):
    """Mirror segment in Y-Z: from (y_top, z_top) down to y_bot. tilt > 0 leans the bottom edge toward the LEDs (-Z),
    so the face looks a little downward and throws the reflected light further down the page."""
    t = np.radians(tilt_deg)
    z_bot = z_top - (y_top - y_bot) * np.tan(t)
    return np.array([y_top, z_top]), np.array([y_bot, z_bot])


def specular(pz, y_top, y_bot, tilt, R):
    A, B = mirror_line(y_top, y_bot, tilt)
    u = (B - A) / np.linalg.norm(B - A)              # along the mirror (Y-Z)
    n = np.array([-u[1], u[0]])                      # normal; make it point toward the LEDs (-Z side)
    if n[1] > 0:
        n = -n
    E = np.zeros_like(PX)
    S = np.array([LED_Y, LED_Z])
    Sp = S - 2 * np.dot(S - A, n) * n                # image of the LED row across the mirror plane
    for lx in LED_X:
        # line image -> page point, intersect with the mirror plane
        dyp, dzp = PY - Sp[0], pz - Sp[1]
        denom = dyp * n[0] + dzp * n[1]
        with np.errstate(divide="ignore", invalid="ignore"):
            s = -((Sp[0] - A[0]) * n[0] + (Sp[1] - A[1]) * n[1]) / denom
        Qy, Qz = Sp[0] + s * dyp, Sp[1] + s * dzp
        along = (Qy - A[0]) * u[0] + (Qz - A[1]) * u[1]
        Qx = lx + s * (PX - lx)
        hit = (s > 0) & (s < 1) & (along >= 0) & (along <= np.linalg.norm(B - A)) & (Qx >= VIS_X[0]) & (Qx <= VIS_X[1])
        # the LED's own intensity toward Q (real ray), the image's path length and the page incidence
        I, _ = lam_down(Qx - lx, Qy - LED_Y, Qz - LED_Z)
        dx, dy, dz = PX - lx, PY - Sp[0], pz - Sp[1]
        r = np.sqrt(dx * dx + dy * dy + dz * dz)
        cosi = (Sp[1] - pz) / r
        E += np.where(hit & (Qy < LED_Y), R * I * cosi / r ** 2 * clear(Qy, Qz, PY, pz), 0.0)
    return E


def diffuse(pz, y_top, y_bot, tilt, R, dy_patch=0.25, dx_patch=1.0):
    A, B = mirror_line(y_top, y_bot, tilt)
    u = (B - A) / np.linalg.norm(B - A)
    n = np.array([-u[1], u[0]])
    if n[1] > 0:
        n = -n
    L = np.linalg.norm(B - A)
    E = np.zeros_like(PX)
    for a in np.arange(dy_patch / 2, L, dy_patch):
        qy, qz = A + a * u
        for qx in np.arange(VIS_X[0] + dx_patch / 2, VIS_X[1], dx_patch):
            # irradiance on the patch from all LEDs (patch faces -Z-ish, lit by the forward-going light)
            Eq = 0.0
            for lx in LED_X:
                I, r = lam_down(qx - lx, qy - LED_Y, qz - LED_Z)
                cq = ((LED_Y - qy) * n[0] + (LED_Z - qz) * n[1]) / r
                if qy < LED_Y and cq > 0:
                    Eq += I * cq / r ** 2
            if Eq <= 0:
                continue
            Lr = R * Eq / np.pi
            dx, dyy, dz = PX - qx, PY - qy, pz - qz
            r = np.sqrt(dx * dx + dyy * dyy + dz * dz)
            ce = np.clip((dyy * n[0] + dz * n[1]) / r, 0, None)
            ci = (qz - pz) / r
            E += Lr * ce * ci * (dy_patch * dx_patch) / r ** 2 * clear(qy, qz, PY, pz)
    return E


def summary(E, base_mid):
    prof = E.mean(axis=1) / base_mid
    at = lambda d: float(np.interp(d, ds, prof))
    top = float(prof[(ds >= 2) & (ds <= 20)].mean())
    bot = float(prof[ds >= 46.4].mean())
    return dict(d2=at(2), d10=at(10), d20=at(20), mid=at(46.4), d70=at(70), bottom=at(92), top2_20=top, bottom_half=bot,
                ratio=top / bot)


def main():
    import sys
    cases = [("bare LEDs (today)", None)]
    if "--flare" in sys.argv:
        # negative tilt = the bottom edge flares AWAY from the LEDs (+Z): a lampshade-like hood
        for yb in (112.0, 110.5, 109.0):
            for tilt in (-15, -25, -35, -45):
                cases.append((f"mirror R0.85 to y{yb} flare {-tilt}", ("spec", 116.6, yb, tilt, 0.85)))
        cases.append(("white print R0.80 to y110.5 flare 35", ("diff", 116.6, 110.5, -35, 0.80)))
    else:
        for yb in (113.0, 111.0, 109.5):
            for tilt in (0, 10, 20):
                cases.append((f"mirror R0.85 to y{yb} tilt {tilt}", ("spec", 116.6, yb, tilt, 0.85)))
        cases.append(("white print R0.80 to y111 tilt 0", ("diff", 116.6, 111.0, 0, 0.80)))
        cases.append(("white print R0.80 to y111 tilt 20", ("diff", 116.6, 111.0, 20, 0.80)))
    for page, pz in PAGES.items():
        base = direct(pz)
        base_mid = float(np.interp(46.4, ds, base.mean(axis=1)))
        print(f"\n=== {page} page (z {pz}); numbers are page light relative to TODAY's mid-page ===")
        print(f"{'case':38s} {'d2':>6s} {'d10':>6s} {'d20':>6s} {'mid':>6s} {'d70':>6s} {'bot':>6s} | {'top2-20':>7s} {'btmhalf':>7s} {'top/btm':>7s}")
        for name, c in cases:
            E = base.copy()
            if c:
                kind, yt, yb, tilt, R = c
                E = E + (specular(pz, yt, yb, tilt, R) if kind == "spec" else diffuse(pz, yt, yb, tilt, R))
            s = summary(E, base_mid)
            print(f"{name:38s} {s['d2']:6.2f} {s['d10']:6.2f} {s['d20']:6.2f} {s['mid']:6.2f} {s['d70']:6.2f} {s['bottom']:6.2f} | "
                  f"{s['top2_20']:7.2f} {s['bottom_half']:7.2f} {s['ratio']:7.1f}")


if __name__ == "__main__":
    main()
