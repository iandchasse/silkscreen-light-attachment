# Light PCBA (rev B, "simple") - PROGRESS

Rev A notes (rod lens, carrier, BAW56, 2x2 TSW header): archive/rev-A-rod-lens/pcb/PROGRESS.md (+ its production/, docs/).
Contract: design/DESIGN-SPEC-revB.md. Nothing committed (per brief).

## Status (2026-09-25): COMPLETE and PASSING
- [x] Archive rev A production/, docs/, PROGRESS.md -> archive/rev-A-rod-lens/pcb/ (verified identical with diff -rq).
- [x] Generator converted to rev B: params.py, generate.py, build_pcb.py (1.0 mm stack, R2 rounded rectangle, 2 NPTH,
      J1 1x2 + J2 1x1, R1/R2 in the J6-opening zone, rev B silk), make_step_models.py (1x2 / 1x1 header models, E-frame
      transform from STACK), check_handedness.py (J1/J2 pads, INSIDE zones), make_outputs.py (12 SMT parts, headers
      hand-soldered via the Assembly field, pos --smd-only), export_geometry.py ("header" = bbox of both bodies +
      "bodies" + 3 pins + engagement), report_design.py (no diode, engagement()).
- [x] generate.py + make_outputs.py end to end: ALL GATES PASS.
- [x] docs/jlc-notes.md rewritten (short); docs/sources: rev A-only files dropped (kept in the archive), JLC API
      snapshots of the 5 ordered parts added.

## Gate results (last run)
- ERC 0; DRC 0 violations / 0 unconnected / 0 parity (--severity-all, 0 exclusions, 0 ignored checks).
- Handedness: J1 "5"/"6" and J2 "11" at E (54.662,-3.810)/(57.202,-3.810)/(54.662,-1.270), error 0.000; nets
  LED_SW/W-/C-; nearest copper to J6-12 1.690, to J6-4 1.390 (>= 1.0); no hole within 2.03 of either.
- NPTH: copper to hole edge >= 3.965, webs to the edge 2.600 (>= 0.5). Silk: min stroke 0.150, min text 1.000.
- Placement: all 14 parts on F.Cu, LEDs in z 8.0..11.0, R1/R2 inside x 43.5..52.5 z -4.8..-0.4, headers inside
  the J6 opening, nothing else over the case top.
- Field sync: 14 parts, 108 fields, 0 mismatches.
- Strings (200 R, no diode): worst V_OUT 19.41 V (< 22.0, margin 2.59; OVP margin 4.84); LED_MONIT lit
  1.71..2.08 V vs open 2.60..2.73; hold-off 11.5 V > 6.5; hot-plug TPS923610 47.0-52.6 mA, TPS923611
  71.3-76.8 mA (< IFP 80); Rs peak 1.18 W for ~1 ms (CRCW-HP pulse-proof).
- E-frame STEP: post tips Y 108.10, tail tips Y 119.60 at all 3 pins (asserted, docs/reports/eframe_step_check.json).

## Header part (JLC parts API, 2026-09-25)
Hong Cheng HC-PZ254-11.5L-1x2PZ (LCSC C27985187, stock 24852) and -1x1PZ (C27985186, stock 10775), JLC Extended
(no Basic 2.54 headers). Insulation 2.5, mating pin 6.0, end pin 3.0, square brass pin, gold. Pin section not listed
and the LCSC PDF is not machine-readable: 0.64 sq assumed. Tips Y 108.10 -> J6 engagement 4.72..5.05 (limits 3.7..6.0).

## Rebuild (close KiCad first; scripts refuse to write while a *.lck exists)
  "C:\Program Files\KiCad\9.0\bin\python.exe" tools\generate.py
  "C:\Program Files\KiCad\9.0\bin\python.exe" tools\make_outputs.py
