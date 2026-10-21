"""Export the as-built PCBA geometry in the ENCLOSURE frame to build/geometry.json (for housing/ checks).

    "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" tools\\export_geometry.py [out.json]

Units mm.  E frame: X across the device, Y up the device (+Y = top edge; the PCB underside = F.Cu faces -Y),
Z toward the screen.  Boxes are [min, max] per axis.  Read-only on the board.
"""
from __future__ import annotations

import json
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402
from kigeom import prims_to_polygon  # noqa: E402

ROOT = os.path.dirname(HERE)
mm = pcbnew.ToMM
S = P.STACK
R3 = lambda v: round(v, 4)

BODY = {  # package body (X along the footprint x at 0 deg, Z along footprint y, H) - datasheets / KiCad models
    "LED": P.LED["body"], "R": (2.00, 1.25, 0.60)}


def outline_e():
    import build_pcb   # noqa: E402  (same primitives the board was built from)
    poly = prims_to_polygon(build_pcb.outline_prims(), 12)
    return [[R3(c) for c in P.to_e(x, y)] for x, y in poly]


def main(out=None):
    out = out or os.path.join(ROOT, "build", "geometry.json")
    b = pcbnew.LoadBoard(os.path.join(ROOT, P.PROJECT + ".kicad_pcb"))
    bb = b.GetBoardEdgesBoundingBox()
    X0, Z1 = P.to_e(mm(bb.GetLeft()), mm(bb.GetTop()))
    X1, Z0 = P.to_e(mm(bb.GetRight()), mm(bb.GetBottom()))
    outline = outline_e()
    xs = [p[0] for p in outline]
    zs = [p[1] for p in outline]
    assert abs(min(xs) - X0) < 0.03 and abs(max(xs) - X1) < 0.03 and abs(min(zs) - Z0) < 0.03 and abs(max(zs) - Z1) < 0.03, \
        "outline polygon disagrees with the board's Edge.Cuts"
    g = {
        "generator": "pcb/tools/export_geometry.py", "project": P.PROJECT, "rev": P.REVISION, "date": P.DATE,
        "frame": "enclosure E (mm): X = main-board KiCad X - 44.24; Y = 148.25 - main-board KiCad Y; Z = 0 at the main-PCB "
                 "rear face, +Z toward the screen. Light-PCB KiCad: x_K = X + 100, y_K = 100 - Z. F.Cu (all parts) faces -Y.",
        "pcb": {"thickness": S["pcb_t"], "underside_y_seated": S["underside_y"], "underside_y_resting": S["underside_y_resting"],
                "top_y_seated": S["top_y"], "bbox_xz": [[R3(min(xs)), R3(max(xs))], [R3(min(zs)), R3(max(zs))]],
                "outline_xz": outline},
        "holes": [], "leds": [], "parts": [], "header": {}, "keepouts_xz": [], "j6_pins": {},
    }
    uy = S["underside_y"]
    pins, bodies = [], []
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        pos = fp.GetPosition()
        X, Z = P.to_e(mm(pos.x), mm(pos.y))
        rot = round(fp.GetOrientationDegrees()) % 180
        if ref.startswith("H"):
            for pad in fp.Pads():
                g["holes"].append({"ref": ref, "name": fp.GetValue().split()[0], "purpose": fp.GetValue(),
                                   "dia": R3(mm(pad.GetDrillSize().x)), "x": R3(X), "z": R3(Z), "plated": False})
            continue
        if ref in P.HEADERS:
            D, H = P.HDR, P.HEADERS[ref]
            bx0, bx1, bz0, bz1 = P.header_body(ref)
            for pad in fp.Pads():
                pX, pZ = P.to_e(mm(pad.GetPosition().x), mm(pad.GetPosition().y))
                pins.append({"pad": pad.GetNumber(), "ref": ref, "net": pad.GetNetname().lstrip("/"), "x": R3(pX),
                             "z": R3(pZ), "square": D["post_sq"], "y_post_tip": S["post_tip_y"],
                             "y_tail_tip": S["tail_tip_y"], "segment_y": [S["post_tip_y"], S["tail_tip_y"]]})
            bodies.append({"ref": ref, "mpn": H["mpn"], "lcsc": H["lcsc"], "positions": H["positions"],
                           "body_box": {"x": [bx0, bx1], "z": [bz0, bz1], "y": [R3(uy - D["body_h"]), uy]}})
            continue
        kind = "LED" if ref in P.LED["warm"]["refs"] + P.LED["cool"]["refs"] else "R"
        L, W, H = BODY[kind]
        if rot == 90:
            L, W = W, L
        box = {"x": [R3(X - L / 2), R3(X + L / 2)], "z": [R3(Z - W / 2), R3(Z + W / 2)], "y": [R3(uy - H), uy]}
        if kind == "LED":
            colour = "warm" if ref in P.LED["warm"]["refs"] else "cool"
            cl, cw, _ = P.LED["cavity"]
            g["leds"].append({"ref": ref, "colour": colour, "cct": P.LED[colour]["cct"], "lcsc": P.LED[colour]["lcsc"],
                              "x": R3(X), "z": R3(Z), "body_box": box,
                              "emitter": {"x": [R3(X - cl / 2), R3(X + cl / 2)], "z": [R3(Z - cw / 2), R3(Z + cw / 2)],
                                          "y": R3(uy - H), "normal": [0, -1, 0]},
                              "cathode_side": "+X" if round(fp.GetOrientationDegrees()) % 360 == 180 else "-X"})
        else:
            g["parts"].append({"ref": ref, "kind": kind, "value": fp.GetValue(), "x": R3(X), "z": R3(Z), "body_box": box})
    g["leds"].sort(key=lambda d: int(d["ref"][1:]))
    bodies.sort(key=lambda d: d["ref"])
    D = P.HDR
    eng = [round(f - S["post_tip_y"], 3) for f in P.J6_FACE_Y]
    g["header"] = {  # rev A schema kept: body_box = bounding box of both bodies; "bodies" gives each one
        "ref": "J1+J2", "refs": [d["ref"] for d in bodies], "mpn": " + ".join(d["mpn"] for d in bodies),
        "body_box": {"x": [min(d["body_box"]["x"][0] for d in bodies), max(d["body_box"]["x"][1] for d in bodies)],
                     "z": [min(d["body_box"]["z"][0] for d in bodies), max(d["body_box"]["z"][1] for d in bodies)],
                     "y": [R3(uy - D["body_h"]), uy]},
        "bodies": bodies, "drill": D["drill"], "pad": D["pad"],
        "part_data": {"body_h": D["body_h"], "post": D["post"], "tail": D["tail"], "post_sq": D["post_sq"],
                      "source": D["source"]},
        "pins": sorted(pins, key=lambda p: int(p["pad"])),
        "j6_face_y": list(P.J6_FACE_Y), "engagement": eng, "engagement_limits": list(P.ENGAGEMENT_LIMITS),
        "no_pin_at": {"J6-12": list(P.J6["pins"][12]), "J6-4": list(P.J6["pins"][4])},
        "no_pin_at_j6_12": list(P.J6["pins"][12])}
    if len(pins) != 3 or sorted(p["pad"] for p in pins) != ["11", "5", "6"]:
        raise SystemExit(f"geometry: header pins {pins}")
    g["parts"].sort(key=lambda d: d["ref"])
    g["holes"].sort(key=lambda d: int(d["ref"][1:]))
    g["keepouts_xz"] = [{"name": n, "x": [x0, x1], "z": [z0, z1]} for n, x0, x1, z0, z1 in P.KEEPOUTS]
    g["j6_pins"] = {str(k): {"x": v[0], "z": v[1], "net": P.J6["net"][k]} for k, v in P.J6["pins"].items()}
    g["checks"] = {"lowest_y": S["post_tip_y"], "highest_y": S["tail_tip_y"]}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(g, fh, indent=1)
    print("geometry:", out)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
