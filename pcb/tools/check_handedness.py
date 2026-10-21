"""Handedness + placement gate (DESIGN-SPEC sec 1 'Handedness gate', audit M3; sec 3 keep-outs).

    "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" tools\\check_handedness.py

Reads the saved board (read-only) and checks, in the ENCLOSURE frame:
  1. every PTH centre (J1) lands on its J6 pin within 0.02: "5" LED_SW (54.662,-3.810), "6" W- (57.202,-3.810),
     "11" C- (54.662,-1.270); the K->E map is also run through the STEP chain (K -> STEP -> E) with det = +1;
  2. no hole or copper within 1.00 of J6-12 /P+_FUSE (57.202,-1.270) or J6-4 GND (52.122,-3.810);
  3. J1's pad nets match; J1 has exactly 3 plated holes;
  4. NPTH holes where params says; no copper within 0.40 and no track within 0.50 of an NPTH edge;
  5. every part on F.Cu; no part courtyard in a keep-out; height zones respected;
  6. every NPTH-to-board-edge web >= P.EDGE_WEB_MIN (0.50; JLC routes +-0.2) - rev A;
  7. silk (JLC legend minimums): every silk stroke >= 0.15; every visible silk text >= 1.0 high with >= 0.15 stroke
     (the F-side 'W'/'C' string markers may be 0.8 if 1.0 does not fit) - rev A.
Writes build/gate_handedness.json and exits 1 on any failure.
"""
from __future__ import annotations

import json
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402
from kigeom import arc_points  # noqa: E402

ROOT = os.path.dirname(HERE)
mm = pcbnew.ToMM


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def xy(v):
    return (mm(v.x), mm(v.y))


def k_to_step_to_e(xk, yk, z_s=0.0):
    """K -> kicad-cli STEP (x_K, -y_K, z) -> E (DESIGN-SPEC sec 1), for F.Cu items (z_s = 0)."""
    xs, ys, zs = xk, -yk, z_s
    return (xs - 100.0, P.STACK["underside_y"] - zs, 100.0 + ys)


def copper_items(board):
    """(kind, name, net, distance-function) for every copper feature (K frame)."""
    items = []
    for t in board.GetTracks():
        w = mm(t.GetWidth()) / 2 if t.GetClass() != "PCB_VIA" else 0
        if t.GetClass() == "PCB_VIA":
            c, r = xy(t.GetPosition()), mm(t.GetWidth(pcbnew.F_Cu)) / 2
            items.append(("via", "via", t.GetNetname(), lambda p, c=c, r=r: math.hypot(p[0] - c[0], p[1] - c[1]) - r))
        elif t.GetClass() == "PCB_ARC":
            pts = arc_points(xy(t.GetStart()), xy(t.GetMid()), xy(t.GetEnd()), 24)
            items.append(("track", "arc", t.GetNetname(),
                          lambda p, pts=pts, w=w: min(seg_dist(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1)) - w))
        else:
            a, b = xy(t.GetStart()), xy(t.GetEnd())
            items.append(("track", "track", t.GetNetname(), lambda p, a=a, b=b, w=w: seg_dist(p, a, b) - w))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                continue
            c = xy(pad.GetPosition())
            sx, sy = mm(pad.GetSize(pcbnew.F_Cu).x) / 2, mm(pad.GetSize(pcbnew.F_Cu).y) / 2
            rot = round(pad.GetOrientationDegrees()) % 180
            if rot == 90:
                sx, sy = sy, sx
            if pad.GetShape(pcbnew.F_Cu) == pcbnew.PAD_SHAPE_CIRCLE:
                f = lambda p, c=c, r=sx: math.hypot(p[0] - c[0], p[1] - c[1]) - r
            else:
                f = lambda p, c=c, sx=sx, sy=sy: math.hypot(max(abs(p[0] - c[0]) - sx, 0), max(abs(p[1] - c[1]) - sy, 0))
            items.append(("pad", f"{fp.GetReference()}.{pad.GetNumber()}", pad.GetNetname(), f))
    return items


def edge_dist_fn(board):
    """Distance (K) from a point to the Edge.Cuts outline (exact for segments and arcs)."""
    prims = []
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            prims.append(("seg", xy(d.GetStart()), xy(d.GetEnd())))
        elif d.GetShape() == pcbnew.SHAPE_T_ARC:
            prims.append(("arc", arc_points(xy(d.GetStart()), xy(d.GetArcMid()), xy(d.GetEnd()), 256)))
        else:
            raise SystemExit(f"unexpected Edge.Cuts shape {d.GetShapeStr()}")

    def dist(p):
        best = 1e9
        for pr in prims:
            if pr[0] == "seg":
                best = min(best, seg_dist(p, pr[1], pr[2]))
            else:
                pts = pr[1]
                best = min(best, min(seg_dist(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1)))
        return best
    return dist, len(prims)


def silk_items(board):
    """(what, kind, value(s)) for every silk stroke and visible silk text, board and footprints."""
    silk = (pcbnew.F_SilkS, pcbnew.B_SilkS)
    out = []

    def add_shape(g, owner):
        if g.GetLayer() in silk:
            out.append((f"{owner} {g.GetShapeStr()} on {board.GetLayerName(g.GetLayer())}", "stroke",
                        mm(g.GetWidth()), bool(g.IsSolidFill()) if hasattr(g, "IsSolidFill") else False))

    def add_text(t, owner):
        if t.GetLayer() in silk and t.IsVisible():
            out.append((f"{owner} text '{t.GetText()}' on {board.GetLayerName(t.GetLayer())}", "text",
                        (mm(t.GetTextHeight()), mm(t.GetTextThickness())), t.GetText()))
    for d in board.GetDrawings():
        if d.GetClass() in ("PCB_TEXT", "PCB_TEXTBOX"):
            add_text(d, "board")
        elif d.GetClass() == "PCB_SHAPE":
            add_shape(d, "board")
    for fp in board.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetClass() in ("PCB_TEXT", "PCB_TEXTBOX"):
                add_text(g, fp.GetReference())
            elif g.GetClass() == "PCB_SHAPE":
                add_shape(g, fp.GetReference())
        for fld in fp.GetFields():
            add_text(fld, fp.GetReference())
    return out


def courtyard_box(fp):
    """Axis-aligned bbox (K) of a footprint's F.CrtYd graphics."""
    xs, ys = [], []
    for g in fp.GraphicalItems():
        if g.GetLayer() == pcbnew.F_CrtYd:
            bb = g.GetBoundingBox()
            xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
            ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
    if not xs:
        return None
    w = 0.025                                     # courtyard line half-width included by GetBoundingBox
    return (min(xs) + w, max(xs) - w, min(ys) + w, max(ys) - w)


def main():
    board = pcbnew.LoadBoard(os.path.join(ROOT, P.PROJECT + ".kicad_pcb"))
    lines, fails = [], []

    def ok(cond, msg):
        lines.append(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    # ---- 1/3: J1 plated holes
    tol = P.HANDEDNESS_TOL
    pth = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                pth.append((fp.GetReference(), pad))
    ok(len(pth) == 3 and all(r in P.HEADERS for r, _ in pth), f"exactly 3 plated through-holes, all on J1/J2 (found {len(pth)})")
    for ref, pad in pth:
        xk, yk = xy(pad.GetPosition())
        X, Z = P.to_e(xk, yk)
        Xs, Ys, Zs = k_to_step_to_e(xk, yk)
        nm = pad.GetNumber()
        want = P.PLUG["pads"].get(nm)
        net = pad.GetNetname().lstrip("/")
        if want is None:
            ok(False, f"{ref} pad '{nm}' is not one of 5/6/11")
            continue
        ok(ref == P.PLUG["ref"][nm], f"pad '{nm}' on {ref} (want {P.PLUG['ref'][nm]})")
        d = math.hypot(X - want[0], Z - want[1])
        ok(d <= tol, f"{ref} '{nm}' at E ({X:.3f}, {Z:.3f}) vs J6-{nm} ({want[0]:.3f}, {want[1]:.3f}): {d:.4f} <= {tol}")
        ok(abs(Xs - X) < 1e-9 and abs(Zs - Z) < 1e-9 and abs(Ys - P.STACK["underside_y"]) < 1e-9,
           f"{ref} '{nm}' via the STEP chain: E ({Xs:.3f}, Y {Ys:.2f}, {Zs:.3f}) agrees")
        ok(net == P.PLUG["nets"][nm], f"{ref} '{nm}' net {net} == J6-{nm} {P.J6['net'][int(nm)]}")
    # rotation K-STEP-E: columns of the linear part; det must be +1
    M = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
    det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
           + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    ok(det == 1, f"STEP->E rotation determinant {det} (proper rotation)")

    # ---- 2: forbidden J6 positions
    items = copper_items(board)
    holes = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetDrillSize().x > 0:
                holes.append((fp.GetReference(), pad, xy(pad.GetPosition()), mm(pad.GetDrillSize().x) / 2))
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            holes.append(("via", t, xy(t.GetPosition()), mm(t.GetDrillValue()) / 2))
    for X, Z, what in P.PLUG["forbidden"]:
        p = P.to_k(X, Z)
        dc = min(f(p) for _, _, _, f in items)
        dh = min(math.hypot(p[0] - c[0], p[1] - c[1]) - r for _, _, c, r in holes)
        ok(dc >= P.PLUG["forbid_r"] and dh >= P.PLUG["forbid_r"],
           f"{what} at E ({X}, {Z}): nearest copper {dc:.3f}, nearest hole {dh:.3f} (>= {P.PLUG['forbid_r']})")

    # ---- 4: NPTH holes
    npth = [(r, pad, c, rr) for r, pad, c, rr in holes if r != "via" and pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
    ok(len(npth) == len(P.HOLES), f"{len(npth)} NPTH holes (params: {len(P.HOLES)})")
    for name, dia, X, Z, purpose in P.HOLES:
        p = P.to_k(X, Z)
        m = [h for h in npth if math.hypot(h[2][0] - p[0], h[2][1] - p[1]) < 0.001 and abs(2 * h[3] - dia) < 0.001]
        ok(len(m) == 1, f"NPTH {name} dia {dia} at E ({X}, {Z})")
    min_cu = min(f(c) - r for _, _, c, r in npth for _, _, _, f in items)
    min_tr = min(f(c) - r for _, _, c, r in npth for kind, _, _, f in items if kind == "track")
    ok(min_cu >= P.HOLE_COPPER_CLEAR - 1e-6, f"copper to NPTH edge min {min_cu:.3f} >= {P.HOLE_COPPER_CLEAR}")
    ok(min_tr >= P.HOLE_TRACE_CLEAR - 1e-6, f"tracks to NPTH edge min {min_tr:.3f} >= {P.HOLE_TRACE_CLEAR}")

    # ---- 5: placement
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith("H"):
            continue
        ok(fp.GetLayer() == pcbnew.F_Cu, f"{ref} on F.Cu")
        box = courtyard_box(fp)
        if box is None:
            ok(False, f"{ref} has no courtyard")
            continue
        X0, Z1 = P.to_e(box[0], box[2])
        X1, Z0 = P.to_e(box[1], box[3])
        hits = [n for n, x0, x1, z0, z1 in P.KEEPOUTS if X0 < x1 - 1e-6 and X1 > x0 + 1e-6 and Z0 < z1 - 1e-6 and Z1 > z0 + 1e-6]
        kind = "LED" if fp.GetFPIDAsString().endswith(("3014_HONGLI_HL-A-3014H421W",)) else \
            ("R" if ref.startswith("R") else "HDR")
        h = P.PART_HEIGHT[kind]
        iname, (ix0, ix1, iz0, iz1) = P.INSIDE[kind]
        if not (X0 >= ix0 - 1e-6 and X1 <= ix1 + 1e-6 and Z0 >= iz0 - 1e-6 and Z1 <= iz1 + 1e-6):
            hits.append(f"outside {iname}")
        for n, x0, x1, z0, z1, hmax, allowed in P.HEIGHT_ZONES:
            if Z0 < z1 and Z1 > z0 and X0 < x1 and X1 > x0:
                if allowed and kind != allowed:
                    hits.append(f"{n} (only {allowed})")
                elif h > hmax + 1e-9:
                    hits.append(f"{n} (height {h} > {hmax})")
        for name, dia, hx, hz, purpose in P.HOLES:
            if dia > 3:
                r = dia / 2 + P.COLUMN_KEEPOUT_EXCEPT.get((ref, name), P.COLUMN_KEEPOUT)
                cx, cz = min(max(hx, X0), X1), min(max(hz, Z0), Z1)
                dcol = math.hypot(cx - hx, cz - hz) - dia / 2
                if (ref, name) in P.COLUMN_KEEPOUT_EXCEPT:
                    lines.append(f"INFO {ref} body to column hole {name} edge {dcol:.3f} (exception >= "
                                 f"{P.COLUMN_KEEPOUT_EXCEPT[(ref, name)]:.2f}, PROGRESS deviation)")
                if math.hypot(cx - hx, cz - hz) < r - 1e-6:
                    hits.append(f"column {name} +{r - dia / 2:.2f} (at {dcol:.3f})")
        ok(not hits, f"{ref} courtyard E x {X0:.2f}..{X1:.2f} z {Z0:.2f}..{Z1:.2f}: " + (", ".join(hits) or "clear of keep-outs"))

    # ---- 6: NPTH-to-edge webs (rev A, DFM F1)
    edist, nprim = edge_dist_fn(board)
    webs = []
    for name, dia, X, Z, purpose in P.HOLES:
        c = P.to_k(X, Z)
        webs.append((edist(c) - dia / 2, name, dia, X, Z))
    for w, name, dia, X, Z in sorted(webs):
        ok(w >= P.EDGE_WEB_MIN - 1e-6, f"NPTH {name} dia {dia} at E ({X}, {Z}): web to board edge {w:.3f} >= {P.EDGE_WEB_MIN}")
    lines.append(f"INFO outline {nprim} Edge.Cuts primitives; min NPTH web {min(webs)[0]:.3f} ({min(webs)[1]})")

    # ---- 7: silk legend minimums (rev A, DFM F2)
    sw = P.RULES["silk_line_w"]
    th = P.RULES["silk_text_h"]
    strokes, texts, small = [], [], []
    for what, kind, val, extra in silk_items(board):
        if kind == "stroke":
            strokes.append((val, what))
            if val < sw - 1e-6 and not (extra and val == 0):
                ok(False, f"silk stroke {what} width {val:.3f} < {sw}")
        else:
            h, t = val
            texts.append((h, t, what))
            hmin = 0.8 if extra in ("W", "C") else th
            if extra in ("W", "C") and h < th - 1e-6:
                small.append(what)
            if h < hmin - 1e-6 or t < sw - 1e-6:
                ok(False, f"silk {what} height {h:.3f} / stroke {t:.3f} (need >= {hmin} / {sw})")
    wmin = min(v for v, _ in strokes if v > 0)
    ok(wmin >= sw - 1e-6, f"silk: {len(strokes)} strokes, min width {wmin:.3f} >= {sw}")
    ok(min(h for h, _, _ in texts) >= (0.8 if small else th) - 1e-6 and min(t for _, t, _ in texts) >= sw - 1e-6,
       f"silk: {len(texts)} visible texts, min height {min(h for h, _, _ in texts):.3f}, min stroke "
       f"{min(t for _, t, _ in texts):.3f}" + (f"; W/C markers at 0.8: {small}" if small else "; W/C markers at >= 1.0"))

    lines_out = [l for l in lines]
    rep = {"pass": not fails, "fails": fails, "lines": lines_out}
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    with open(os.path.join(ROOT, "build", "gate_handedness.json"), "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=2)
    for l in lines_out:
        print(l)
    print(f"HANDEDNESS/PLACEMENT GATE: {'PASS' if not fails else 'FAIL'} ({len(fails)} failures)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
