"""STEP models and the enclosure-frame PCBA, built with CadQuery.

Run with the CadQuery python (the enclosure project's venv); generate.py and make_outputs.py call it
through CQ_PYTHON:

    <cq-python> tools/make_step_models.py models <out_dir>
    <cq-python> tools/make_step_models.py eframe <board.step> <board_only.step> <out.step> <out.stl> <report.json>

Model frame (KiCad 3D-model convention): origin = footprint origin, +z away from the board on the
component side, model +y = footprint -y.  Output STEP headers get a fixed timestamp so the files are
byte-stable between runs.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402

import cadquery as cq  # noqa: E402


def _fix_header(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"FILE_NAME\('([^']*)','[^']*'", lambda m: f"FILE_NAME('{os.path.basename(path)}','{P.DATE}T00:00:00'", txt, count=1)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)


def _save(assy, path):
    tmp = path + ".tmp.step"
    try:
        assy.export(tmp)
    except AttributeError:
        assy.save(tmp)
    os.replace(tmp, path)
    _fix_header(path)


def led_model(path):
    L, W, H = P.LED["body"]
    cl, cw, cd = P.LED["cavity"]
    body = cq.Workplane("XY").box(L, W, H, centered=(True, True, False))
    pocket = (cq.Workplane("XY").workplane(offset=H - cd).rect(cl, cw).extrude(cd)
              .edges("|Z").fillet(0.35))
    body = body.cut(pocket)
    lens = (cq.Workplane("XY").workplane(offset=H - cd).rect(cl - 0.02, cw - 0.02).extrude(cd - 0.01)
            .edges("|Z").fillet(0.34))
    # terminals under the body (datasheet p.2 bottom view: pin 1 1.68 long at -x, pin 2 0.78 at +x)
    t1 = cq.Workplane("XY").center(-L / 2 + 1.68 / 2, 0).box(1.68, 0.80, 0.05, centered=(True, True, False))
    t2 = cq.Workplane("XY").center(L / 2 - 0.78 / 2, 0).box(0.78, 0.80, 0.05, centered=(True, True, False))
    assy = cq.Assembly(name="HL-A-3014H421W")
    assy.add(body, name="housing", color=cq.Color(0.95, 0.95, 0.92))
    assy.add(lens, name="lens", color=cq.Color(1.0, 0.86, 0.35))
    assy.add(t1, name="k_terminal", color=cq.Color(0.8, 0.8, 0.82))
    assy.add(t2, name="a_terminal", color=cq.Color(0.8, 0.8, 0.82))
    _save(assy, path)


def header_model(ref, path):
    """Straight 2.54 mm male header (HDR numbers): body on the component plane, square pins from -tail to
    body_h + post.  Origin = body centre (footprint origin); pad K offset (dx, dy) -> model (dx, -dy)."""
    D = P.HDR
    bx0, bx1, bz0, bz1 = P.header_body(ref)
    body = cq.Workplane("XY").box(bx1 - bx0, bz1 - bz0, D["body_h"], centered=(True, True, False))
    assy = cq.Assembly(name=P.HEADERS[ref]["mpn"])
    assy.add(body, name="body", color=cq.Color(0.08, 0.08, 0.08))
    cx, cz = P.header_centre(ref)
    z_lo, z_hi = -D["tail"], D["body_h"] + D["post"]
    for name, (X, Z) in P.HEADERS[ref]["pads"].items():
        post = cq.Workplane("XY").center(X - cx, Z - cz).box(D["post_sq"], D["post_sq"], z_hi - z_lo,
                                                            centered=(True, True, False)).translate((0, 0, z_lo))
        assy.add(post, name=f"pin_{name}", color=cq.Color(0.85, 0.7, 0.2))
    _save(assy, path)


def models(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    led_model(os.path.join(out_dir, "LED_3014_HONGLI_HL-A-3014H421W.step"))
    for ref in P.HEADERS:
        n = P.HEADERS[ref]["positions"]
        header_model(ref, os.path.join(out_dir, f"J6_PLUG_1x{n}_HC-PZ254-11.5L.step"))
    print("models written to", out_dir)


def eframe(board_step, board_only_step, out_step, out_stl, report):
    """Board STEP (kicad-cli, user origin 0,0: x_s = x_K, y_s = -y_K) -> enclosure frame.

    X = x_s - 100, Y = underside_y - (z_s - z_F), Z = 100 + y_s   (a +90 deg rotation about X)
    """
    # kicad-cli puts the bare-board slab (dielectric only) at z 0..t and seats component models on the
    # F surface above it.  Calibrate that component plane (= E Y underside_y, the seated PCB underside) on the J1
    # body box, whose model base is z = 0; the slab is reported separately.
    slab = cq.importers.importStep(board_only_step).val()
    zv = [v.Z for v in slab.Vertices()]
    thick = max(zv) - min(zv)
    full = cq.importers.importStep(board_step).val()
    bx0, bx1, bz0, bz1 = P.header_body("J1")
    cxs = [P.to_k(bx0, 0)[0], P.to_k(bx1, 0)[0]]
    cys = [-P.to_k(0, bz0)[1], -P.to_k(0, bz1)[1]]
    corner_z = sorted({round(v.Z, 5) for v in full.Vertices()
                       if min(abs(v.X - c) for c in cxs) < 1e-3 and min(abs(v.Y - c) for c in cys) < 1e-3})
    if len(corner_z) < 2 or abs(corner_z[-1] - corner_z[0] - P.HDR["body_h"]) > 1e-3:
        print("J1 body corners not found in the board STEP:", corner_z)
        sys.exit(4)
    z_f = corner_z[0]
    shp = cq.importers.importStep(board_step)
    comp = shp.val() if hasattr(shp, "val") else shp
    s = P.STACK
    moved = (comp.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)
             .translate(cq.Vector(-P.K_OX, s["underside_y"] + z_f, P.K_OY)))
    # numeric proof of the rotation on a sample point (a pad centre)
    import math
    X, Z = P.PLUG["pads"]["5"]
    xk, yk = P.to_k(X, Z)
    xs, ys, zs = xk, -yk, z_f
    rx = (xs, ys * math.cos(math.pi / 2) - zs * math.sin(math.pi / 2), ys * math.sin(math.pi / 2) + zs * math.cos(math.pi / 2))
    e_pt = (rx[0] - P.K_OX, rx[1] + s["underside_y"] + z_f, rx[2] + P.K_OY)
    bb = moved.BoundingBox()
    # header posts / tails: vertices near the extreme Y values
    verts = [(v.X, v.Y, v.Z) for v in moved.Vertices()]
    lo = [v for v in verts if v[1] < s["post_tip_y"] + 0.02]
    hi = [v for v in verts if v[1] > s["tail_tip_y"] - 0.02]
    def clusters(vs):
        out = []
        for name, (px, pz) in P.PLUG["pads"].items():
            near = [v for v in vs if abs(v[0] - px) < 0.5 and abs(v[2] - pz) < 0.5]
            out.append({"pad": name, "n": len(near),
                        "x": round(sum(v[0] for v in near) / len(near), 4) if near else None,
                        "z": round(sum(v[2] for v in near) / len(near), 4) if near else None,
                        "y": round(sum(v[1] for v in near) / len(near), 4) if near else None})
        return out
    rep = {"z_F_component_plane": z_f, "board_slab_thickness": round(thick, 4), "slab_z": [round(min(zv), 4), round(max(zv), 4)],
           "slab_top_recess_below_component_plane": round(z_f - max(zv), 4), "bbox": {"xmin": round(bb.xmin, 4), "xmax": round(bb.xmax, 4), "ymin": round(bb.ymin, 4),
                                "ymax": round(bb.ymax, 4), "zmin": round(bb.zmin, 4), "zmax": round(bb.zmax, 4)},
           "pad5_sample_E": [round(c, 4) for c in e_pt],
           "post_tips": clusters(lo), "tail_tips": clusters(hi)}
    errs = []
    if abs((z_f - min(zv)) - s["pcb_t"]) > 0.01:
        errs.append(f"component plane to slab bottom {z_f - min(zv):.4f} != board thickness {s['pcb_t']}")
    vy0, vy1 = min(v[1] for v in verts), max(v[1] for v in verts)
    rep["vertex_y_range"] = [round(vy0, 4), round(vy1, 4)]
    if abs(vy0 - s["post_tip_y"]) > 0.01:
        errs.append(f"lowest vertex Y {vy0:.4f} != post tip {s['post_tip_y']}")
    if abs(vy1 - s["tail_tip_y"]) > 0.01:
        errs.append(f"highest vertex Y {vy1:.4f} != tail tip {s['tail_tip_y']}")
    for grp in (rep["post_tips"], rep["tail_tips"]):
        for c in grp:
            px, pz = P.PLUG["pads"][c["pad"]]
            if not c["n"] or abs(c["x"] - px) > 0.02 or abs(c["z"] - pz) > 0.02:
                errs.append(f"pin {c['pad']} tip not at X {px} Z {pz}: {c}")
    if abs(e_pt[0] - X) > 1e-6 or abs(e_pt[2] - Z) > 1e-6 or abs(e_pt[1] - s["underside_y"]) > 1e-6:
        errs.append(f"sample transform wrong: {e_pt}")
    rep["errors"] = errs
    with open(report, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=2)
    if errs:
        print("\n".join(errs))
        sys.exit(3)
    cq.exporters.export(moved, out_step)
    _fix_header(out_step)
    cq.exporters.export(moved, out_stl, tolerance=0.02, angularTolerance=0.2)
    print("E-frame PCBA:", out_step, out_stl, "tips OK", rep["bbox"])


if __name__ == "__main__":
    if sys.argv[1] == "models":
        models(sys.argv[2])
    elif sys.argv[1] == "eframe":
        eframe(*sys.argv[2:7])
    else:
        sys.exit("usage: models <dir> | eframe <board.step> <board_only.step> <out.step> <out.stl> <report.json>")
