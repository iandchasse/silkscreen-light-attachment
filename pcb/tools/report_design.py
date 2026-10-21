"""String-voltage numbers (no KiCad needed) and the as-built summary docs/design_summary.md (needs pcbnew).

    "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" tools\\report_design.py
Read-only on the board; safe while KiCad is open.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402

ROOT = os.path.dirname(HERE)


def string_numbers():
    """LED_SW (boost output) per string at the driver current; research/electrical-j6.md sec 3 method."""
    L, D, R = P.LED, P.DRIVER, P.RS
    n = P.PER_STRING
    vf_min, vf_typ, vf_max = L["vf_13mA"]
    dvf_cold = (D["t_cold"] - 25.0) * D["vf_tc"]                 # +0.105 V per LED at -10 C
    rs = R["ohms"]
    out = {
        "n": n, "rs": rs,
        "n_vf_min": n * vf_min, "n_vf_typ": n * vf_typ, "n_vf_max": n * vf_max,
        "n_vf_max_cold": n * (vf_max + dvf_cold),
        "v_rs": rs * D["i_nom"], "v_rs_max": rs * D["i_max"],
        "v_min": n * vf_min + rs * D["i_nom"] + D["v_sense"] + D["v_fet"],
        "v_typ": n * vf_typ + rs * D["i_nom"] + D["v_sense"] + D["v_fet"],
        "v_max": n * (vf_max + dvf_cold) + rs * D["i_max"] + D["v_sense"] + D["v_fet"],
        "v_hold_uA": n * L["vf_uA"],
        "p_rs": rs * D["i_max"] ** 2,
        "ceiling": D["ceiling"], "ovp_min": D["ovp_min"], "ifp": L["ifp"],
    }
    # hot-plug peak, C9 charged to OVP (review-electrical VERIFIED 7 / F3): (V_C9 - N x V0 - V_D) / R_loop.
    # (typ bin, min bin) -> (low, high) of the range.
    r_loop = D["hp_r_fixed"] + rs + n * D["hp_rd_led"]
    out["r_loop"] = r_loop

    def ipk(vc9):
        return tuple((vc9 - n * v0 - D["hp_vd"]) / r_loop for v0 in (D["hp_v0"][1], D["hp_v0"][0]))
    out["ipk_610"] = ipk(D["hp_vc9"]["TPS923610"])
    out["ipk_611"] = ipk(D["hp_vc9"]["TPS923611"])
    # LED_SW-to-GND misinsertion (review-electrical VERIFIED 8, F3): no R37 in the loop -> (V - N x V0min - V_D) / (Rs + N r_d)
    out["i_mis_611"] = (D["hp_vc9"]["TPS923611"] - n * D["hp_v0"][0] - D["hp_vd"]) / (rs + n * D["hp_rd_led"])
    out["ipk_min"], out["ipk_max"] = out["ipk_610"]
    out["p_rs_peak"] = out["ipk_611"][1] ** 2 * rs          # Rs peak power in the worst hot-plug pulse
    out["monit_lit"] = (out["v_min"] * D["monit_ratio"], out["v_max"] * D["monit_ratio"])
    out["margin_ceiling"] = D["ceiling"] - out["v_max"]
    out["margin_ovp"] = D["ovp_min"] - out["v_max"]
    out["monit_separated"] = out["monit_lit"][1] < D["monit_open"][0]
    out["ok"] = (out["v_max"] < D["ceiling"] and out["v_hold_uA"] > D["open_min"] and out["ipk_610"][1] < L["ifp"]
                 and out["ipk_611"][1] < L["ifp"] and out["monit_separated"])
    return out


def engagement():
    """J6 engagement of the header posts: J6 face Y minus the post tip Y (DESIGN-SPEC-revB, Headers)."""
    tip = P.STACK["post_tip_y"]
    lo, hi = (round(f - tip, 3) for f in P.J6_FACE_Y)
    return {"tip_y": tip, "min": lo, "max": hi, "limits": list(P.ENGAGEMENT_LIMITS),
            "ok": P.ENGAGEMENT_LIMITS[0] <= lo and hi <= P.ENGAGEMENT_LIMITS[1]}


def string_text():
    s = string_numbers()
    return [
        f"- N = {s['n']} LEDs per string, Rs = {s['rs']:.0f} R ({P.RS['mpn']}), no series diode (rev B).",
        f"- N x Vf at 13.3 mA: {s['n_vf_min']:.2f} / {s['n_vf_typ']:.2f} / {s['n_vf_max']:.2f} V (min / typ / max, 25 C); "
        f"{s['n_vf_max_cold']:.2f} V max at -10 C.",
        f"- Rs drop {s['v_rs']:.2f} V at 13.3 mA ({s['v_rs_max']:.2f} V at 13.96 mA); Rs dissipation {s['p_rs'] * 1e3:.0f} mW.",
        f"- LED_SW (V_OUT, incl. R37 sense + FET; no diode): {s['v_min']:.2f} V min hot, {s['v_typ']:.2f} V typ, "
        f"**{s['v_max']:.2f} V worst (cold, max bin)** vs the {s['ceiling']:.1f} V ceiling (margin {s['margin_ceiling']:.2f} V) "
        f"and OVP min {s['ovp_min']} V (margin {s['margin_ovp']:.2f} V).",
        f"- Hold-off at ~14 uA hot: {s['v_hold_uA']:.1f} V > {P.DRIVER['open_min']} V (boost body-diode rule).",
        f"- LED_MONIT lit {s['monit_lit'][0]:.2f}..{s['monit_lit'][1]:.2f} V; open {P.DRIVER['monit_open'][0]:.2f}.."
        f"{P.DRIVER['monit_open'][1]:.2f} V ({'separated' if s['monit_separated'] else 'OVERLAP'}).",
        f"- Hot-plug peak (C9 at OVP, loop {s['r_loop']:.1f} R incl. Rs {s['rs']:.0f} R; typ..min LED bin): TPS923610 "
        f"(25.5 V) {s['ipk_610'][0] * 1e3:.1f}-{s['ipk_610'][1] * 1e3:.1f} mA, TPS923611 (31.4 V) "
        f"{s['ipk_611'][0] * 1e3:.1f}-{s['ipk_611'][1] * 1e3:.1f} mA, both < IFP {s['ifp'] * 1e3:.0f} mA "
        f"(IFP is rated at 0.1 ms, 1/10 duty; this pulse lasts ~0.25-1 ms, so the margin is an estimate) "
        f"(gate). TPS923611 LED_SW-to-GND misinsertion ~{s['i_mis_611'] * 1e3:.0f} mA until the OVP latch. Rs peak power in the "
        f"worst pulse {s['p_rs_peak']:.2f} W for ~1 ms (pulse-proof CRCW-HP 0805).",
        f"- Verdict: {'PASS' if s['ok'] else 'FAIL'}.",
    ]


def main():
    import pcbnew
    mm = pcbnew.ToMM
    b = pcbnew.LoadBoard(os.path.join(ROOT, P.PROJECT + ".kicad_pcb"))
    out = ["# As-built design summary (generated by tools/report_design.py; do not edit)", "",
           f"Project {P.PROJECT} rev {P.REVISION}, {P.DATE}. Frames: KiCad K (x_K = X + 100, y_K = 100 - Z) and "
           "enclosure E (X, Z; Y up the device). All parts on F.Cu (faces -Y, toward the case).", ""]
    bb = b.GetBoardEdgesBoundingBox()
    ds = b.GetDesignSettings()
    out.append(f"Board outline bbox (K): x {mm(bb.GetLeft()):.3f}..{mm(bb.GetRight()):.3f}, "
               f"y {mm(bb.GetTop()):.3f}..{mm(bb.GetBottom()):.3f}; thickness {mm(ds.GetBoardThickness()):.3f} mm; "
               f"{b.GetCopperLayerCount()} copper layers.")
    out += ["", "## String voltage sanity", ""] + string_text()
    out += ["", "## Parts and sourcing", "",
            f"- Rs choice: {P.RS['decision']} (checked {P.RS['lcsc_checked']}). DigiKey {P.RS['digikey']} "
            "(DigiKey search page for the MPN, 2026-09-25).",
            *[f"- {r} {h['manufacturer']} {h['mpn']} (LCSC {h['lcsc']}, {P.HDR_JLC_TYPE}; stock {h['stock']} on "
              f"2026-09-25), pads J6 {'/'.join(h['pads'])}: **hand-soldered by the builder**, in bom.csv, not in "
              f"jlc_bom.csv / jlc_cpl.csv (12 SMT parts). DigiKey alternative: {h['digikey']}."
              for r, h in P.HEADERS.items()],
            f"- Header numbers: body {P.HDR['body_h']} / post {P.HDR['post']} / tail {P.HDR['tail']} / pin "
            f"{P.HDR['post_sq']} sq. Source: {P.HDR['source']}. Alternative: {P.HDR['alt']}.",
            f"- Post tips at Y {P.STACK['post_tip_y']:.2f} (underside {P.STACK['underside_y']:.2f} - body "
            f"{P.HDR['body_h']} - post {P.HDR['post']}); J6 face Y {P.J6_FACE_Y[0]}..{P.J6_FACE_Y[1]} -> engagement "
            f"{P.J6_FACE_Y[0] - P.STACK['post_tip_y']:.2f}..{P.J6_FACE_Y[1] - P.STACK['post_tip_y']:.2f} mm (limits "
            f"{P.ENGAGEMENT_LIMITS[0]}..{P.ENGAGEMENT_LIMITS[1]}). Tails end at Y {P.STACK['tail_tip_y']:.2f} "
            f"({P.STACK['tail_tip_y'] - P.STACK['top_y']:.2f} above the PCB top).",
            f"- LEDs: MPN shared by every CCT; warm = C210340 (3000 K), cool = C210343 (6000 K). DigiKey: {P.LED['digikey']}.",
            "- CPL rotation offsets (EasyEDA footprints, docs/sources/ee_*.json): LED C210340 +0 (pad 1 at -x in both), "
            "R 0805 +0 (non-polar). See docs/jlc-notes.md."]
    out += ["", "## Deviations / notes (DESIGN-SPEC-revB)", ""] + ["- " + d for d in P.DEVIATIONS]
    out += ["", "## Footprints", "", "| Ref | Value | Footprint | x_K | y_K | rot | X (E) | Z (E) | pads (num: net) |",
            "|---|---|---|---|---|---|---|---|---|"]
    def key(fp):
        r = fp.GetReference()
        return (r.rstrip("0123456789"), int("".join(c for c in r if c.isdigit()) or 0))
    for fp in sorted(b.GetFootprints(), key=key):
        pos = fp.GetPosition()
        X, Z = P.to_e(mm(pos.x), mm(pos.y))
        pads = ", ".join(f"{p.GetNumber() or 'npth'}: {p.GetNetname() or '-'}" for p in fp.Pads())
        out.append(f"| {fp.GetReference()} | {fp.GetValue()} | {fp.GetFPIDAsString().split(':')[-1]} | {mm(pos.x):.3f} | "
                   f"{mm(pos.y):.3f} | {fp.GetOrientationDegrees():.0f} | {X:.3f} | {Z:.3f} | {pads} |")
    out += ["", "## Copper by net", "", "| Net | F.Cu mm | B.Cu mm | widths | vias |", "|---|---|---|---|---|"]
    per = defaultdict(lambda: {"len": defaultdict(float), "widths": set(), "vias": []})
    for t in b.GetTracks():
        n = t.GetNetname()
        if t.GetClass() == "PCB_VIA":
            per[n]["vias"].append((round(mm(t.GetPosition().x), 3), round(mm(t.GetPosition().y), 3)))
        else:
            per[n]["len"][b.GetLayerName(t.GetLayer())] += mm(t.GetLength())
            per[n]["widths"].add(round(mm(t.GetWidth()), 3))
    for n in sorted(per):
        d = per[n]
        out.append(f"| {n} | {d['len'].get('F.Cu', 0):.1f} | {d['len'].get('B.Cu', 0):.1f} | {sorted(d['widths'])} | "
                   f"{d['vias']} |")
    gate = os.path.join(ROOT, "build", "gate_handedness.json")
    if os.path.exists(gate):
        g = json.load(open(gate, encoding="utf-8"))
        out += ["", "## Handedness / placement gate (tools/check_handedness.py)", ""]
        out += ["- " + line for line in g.get("lines", [])]
    path = os.path.join(ROOT, "docs", "design_summary.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "strings":
        print("\n".join(string_text()))
    else:
        main()
