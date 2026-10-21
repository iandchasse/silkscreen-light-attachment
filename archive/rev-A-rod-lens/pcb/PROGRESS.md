# Light PCBA generated KiCad project - PROGRESS

Status: COMPLETE and PASSING (2026-09-25), including the review round 1 fixes: see "Rev A fixes (review round 1)" at the end, which supersedes the 150 R numbers below. Nothing committed (per brief).

## How to rebuild (close KiCad first; every script refuses to write while a *.lck exists)
KiCad python: "C:\Program Files\KiCad\9.0\bin\python.exe" (pcbnew 9.0.6). CadQuery python (STEP models,
E-frame STEP/STL) via env CQ_PYTHON, default W\silkscreen-enclosure-claude\.venv\Scripts\python.exe.
Env overrides: KICAD9_DIR, KICAD_CLI, CQ_PYTHON.
  1. "<kicad-python>" tools\generate.py       lib/ (footprints, symbols, STEP), .kicad_sch, .kicad_pro/.kicad_dru,
                                              routed .kicad_pcb (board built from the schematic netlist)
  2. "<kicad-python>" tools\make_outputs.py   gates first (ERC, DRC+parity, handedness/placement, string sanity);
                                              then production/, docs/, build/geometry.json via build/stage/
  Optional: tools\check_handedness.py, tools\export_geometry.py, tools\report_design.py [strings]

## Result of the last run
- ERC 0 (no exclusions, no ignored ERC checks); DRC 0 violations / 0 unconnected / 0 parity (--severity-all,
  0 exclusions, 0 ignored DRC checks; custom rule trace_to_npth_0p5 verified live by a 0.6 mm test).
- Handedness/placement gate PASS: J1 "5"/"6"/"11" at E (54.662,-3.810)/(57.202,-3.810)/(54.662,-1.270) error 0.000;
  nets LED_SW/W-/C-; nearest copper to J6-12 1.690, to J6-4 1.290 (>= 1.00); NPTH copper >= 0.575; all parts on F.Cu;
  no courtyard in any keep-out / height zone.
- E-frame PCBA STEP: post tips Y 107.94, tail tips Y 121.40 for all three pins (asserted, docs/reports/eframe_step_check.json).
- Generated sources byte-identical across runs (19 files hashed).

## String-voltage sanity
- N = 5 LEDs per string, Rs = 150 R (CRCW0805150RFKEAHP), BAW56 series diode.
- N x Vf at 13.3 mA: 13.00 / 14.25 / 15.75 V (min / typ / max, 25 C); 16.27 V max at -10 C.
- Rs drop 1.99 V at 13.3 mA (2.09 V at 13.96 mA); Rs dissipation 29 mW.
- LED_SW (V_OUT, incl. BAW56 + R37 sense + FET): 15.94 V min hot, 17.31 V typ, **19.66 V worst (cold, max bin)** vs the 22.0 V ceiling (margin 2.34 V) and OVP min 24.25 V (margin 4.59 V).
- Hold-off at ~14 uA hot: 11.5 V > 6.5 V (boost body-diode rule).
- LED_MONIT lit 1.71..2.11 V; open 2.60..2.73 V.
- Hot-plug peak (C9 at OVP, TPS923610) through 150 R: 52-64 mA < IFP 80 mA (TPS923611: 78-96 mA, over IFP).
- Verdict: PASS.

## Files
- tools/: params.py (single source, E frame), kigeom.py, generate.py, build_pcb.py, make_step_models.py (CadQuery),
  check_handedness.py, export_geometry.py, report_design.py, make_outputs.py, template.kicad_pro
- production/: gerbers/, silkscreen-light-attachment_rev-A_gerbers.zip (8 Gerbers + PTH/NPTH drill only), bom.csv,
  jlc_bom.csv, jlc_cpl.csv, 3d/silkscreen-light-attachment.step, 3d/..._pcba_E.step, 3d/..._pcba_E.stl
- docs/: schematic PDF, layout PDF, images/render_top.png + render_bottom.png, design_summary.md, reports/, sources/
- build/geometry.json (enclosure frame, for housing/)

## Decisions and evidence (docs/sources/)
- LED land pattern verified on the Hongli datasheet B-17-A-1548 rev A/3 p.2 (datasheet.lcsc.com/lcsc/C210340.pdf,
  page image saved): pad 1 1.91x0.92 = cathode, pad 2 0.91x0.92, gap 0.55.
- Rs: CRCW0805150RFKEAHP = LCSC C313835, 12,187 in stock (JLC parts API 2026-09-25) -> first choice, 150 R.
- CPL offsets from EasyEDA footprints: LED C210340 +0, BAW56 C8663 +180, R C313835 +0, J1 0 (no EasyEDA footprint).
- BAW56,215 DigiKey 1727-2916-1-ND (web search).

## Deviations from DESIGN-SPEC
1. Outline step fillets R0.35 (convex) + R0.35 (concave) instead of R0.5: each width step is only 0.70 (x -4.20 -> -3.50 and 63.50 -> 64.20), and two fillets on one 0.70 edge can total at most 0.70 (R0.5 + R0.5 would need 1.00; R1.0 + R0.5 would need 1.50).
2. STEP frame: kicad-cli 9.0.6 does not put F.Cu at z_s = 0 / B.Cu at z_s = -1.6 (sec 1). It writes the bare dielectric slab (1.51) at z 0..1.51 and seats F-side models on the component plane z = 1.595. make_outputs calibrates that plane on the J1 body box and maps Y = 118.61 - (z_s - 1.595), X = x_s - 100, Z = 100 + y_s (still a +90 deg rotation about X, det +1). Header tips land exactly at Y 107.94 / 121.40 (asserted); the PCB slab in the E-frame STEP spans Y 118.695..120.205 (copper + mask not modelled) vs nominal 118.61..120.21. Use build/geometry.json (118.61 / 120.21) for fit checks.
3. LED silk cathode mark = two short bars along the long sides over pad 1, not a bar across the end: inside a warm/cool pair the pads are only 0.43 apart. F.Fab carries K/A letters and the pin-1 body chamfer.
4. LED courtyard is pads + 0.195 (not IPC 0.25) so the 3.8 mm pair pitch leaves 0.04 between courtyards.
5. Part keep-outs are enforced by tools/check_handedness.py (courtyard vs keep-out rectangles, height zones), not by KiCad rule areas: the NPTH column holes are footprints that legitimately sit inside keep-outs.
6. J1 DigiKey field holds the DigiKey product number 1102472 (TSW-102-14-G-D, pull position 4): the -004 is not confirmed at DigiKey. R1/R2 DigiKey 541-150TCT-ND is inferred from the CRCW-HP numbering (unverified).
7. J1 CPL rotation offset 0: EasyEDA has no footprint for C20382277 (API 404); check JLC's placement preview.
8. Fab outputs (Gerber X2 creation date, kicad-cli/CadQuery STEP, PDFs) carry timestamps; the generated KiCad sources, library and models are byte-identical run to run (KIID seed + uuid rewrite + model stamp).

## Left / open
- DigiKey PN for CRCW0805150RFKEAHP (541-150TCT-ND) unverified; J1 -004 availability (out of stock at LCSC).
- J1 CPL rotation: check JLC's preview (THT, likely hand-placed or DNP).

## Rev A fixes (review round 1) - 2026-09-25
This section supersedes the 150 R numbers under "String-voltage sanity", deviations 6-7 and "Left / open" above.
Sources: design/review-electrical.md (F1-F4), review-dfm.md (F1-F6, F9), DESIGN-SPEC sec 7. Every change is in
tools/ (params.py, generate.py, build_pcb.py, check_handedness.py, make_outputs.py, report_design.py). No generated
file was hand-edited. Nothing was committed.

1. **R1/R2 150 R -> 200 R** (elec F3). The part is now CRCW0805200RFKEAHP, Vishay Dale, LCSC C5972814 (JLC Extended,
   2,477 in stock). It was CRCW0805150RFKEAHP / C313835.
   - DigiKey is **541-CRCW0805200RFKEAHPCT-ND**, cut tape, verified on DigiKey's search page for the MPN on
     2026-09-25. The page also lists the ...TR-ND reel and ...DKR-ND Digi-Reel. 541-200TCT-ND is NOT listed for this
     MPN.
   - Value, MPN, Manufacturer, LCSC, Datasheet (crcwhpe3.pdf) and Description ("200 R 1 % 0.5 W ...") all come from
     params.RS.
   - The string gate now computes the hot-plug peaks from the review-electrical model instead of a hard-coded table:
     I = (V_C9 - 5 V0 - 0.8) / (17 + Rs + 5 x 5.3). The gate now fails if the TPS923611 peak or the LED_MONIT
     separation fails. Before and after:

   | Quantity | 150 R (before) | 200 R (after) |
   |---|---|---|
   | V_OUT min / typ / worst | 15.94 / 17.31 / 19.66 V | 16.61 / 17.98 / **20.36 V** |
   | Margin to 22.0 V ceiling | 2.34 V | 1.64 V |
   | Margin to OVP min 24.25 V | 4.59 V | 3.89 V |
   | Rs dissipation | 29 mW | 39 mW |
   | LED_MONIT lit (open 2.60-2.73 V, now gated for separation) | 1.71-2.11 V | 1.78-2.18 V |
   | Hot-plug peak, TPS923610 (C9 25.5 V) | 52-64 mA (research table); 55-62 mA (same model) | 43.7-49.3 mA |
   | Hot-plug peak, TPS923611 (C9 31.4 V) | 78-96 mA (over IFP) | **68.0-73.5 mA < IFP 80 mA** |
   | TPS923611 LED_SW-to-GND misinsertion | ~101 mA | ~79 mA |

   Hold-off is unchanged at 11.5 V (> 6.5 V).
2. **Holes and webs** (DFM F1).
   - C2 moved from E (61.00, -2.54) to **(60.90, -2.54)**, and SC/SD from z 18.40 to **z 18.30**. C0/C1, the datum
     holes and SA/SB are unchanged.
   - NPTH-to-edge webs went from 0.400 to **0.500** (C2, SC, SD). The others are DL/DR 1.000, C0 4.600, SA/SB 5.700
     and C1 6.450.
   - A new gate item in check_handedness.py requires every web to be >= params.EDGE_WEB_MIN = 0.50. It measures
     exact segment and arc distances to Edge.Cuts. An independent parse of the plotted NPTH.drl and Edge_Cuts.gbr
     also gives a minimum of 0.5000.
   - Knock-on 1: at z 18.30, the cool links at y_K 83.10 would have come 0.475 from the stake holes (< 0.50). The
     cool-link lane moved to **y_K 83.15**. Tracks to NPTH are now 0.525 (was 0.575), and the gap to the LED pads is
     0.265.
   - Knock-on 2: J1's body box now sits **0.328** from the C2 hole edge (was 0.428), against the spec's 0.4. The Ø3.60
     column floats 0.30 in the Ø4.20 hole. The gate keeps 0.40 for every other part and allows 0.30 for J1-C2 only
     (params.COLUMN_KEEPOUT_EXCEPT). The 4.2 NPTH courtyard margin went from 0.40 to 0.30 (params.COLUMN_CRTYD), so
     DRC courtyards_overlap stays an error. Both are recorded as deviations.
3. **J1 DNP at JLC** (DFM F5).
   - The schematic symbol is now `(dnp yes)`. The footprint gets the DNP attribute from the netlist, and generate.py
     exits if the netlist flag does not match params. DRC parity is 0.
   - jlc_bom.csv went from 15 parts (5 lines) to **14 parts (4 lines)**, and jlc_cpl.csv from 15 rows to **14 rows**.
     make_outputs asserts that DNP = [J1], 14 JLC parts, 14 CPL rows, and no J1.
   - bom.csv keeps J1 and gains an "Assembly" column. J1 reads "DNP at JLC - hand-solder; not placed by JLC", and the
     other lines read "JLC SMT (top)".
4. **Footprint fields = schematic fields** (elec F1).
   - Root cause: generate.schematic_netlist split the netlist on "(comp ". The last block (R2) ran on into
     "(libparts" and picked up the stock R symbol's Datasheet "~" and Description "Resistor".
   - The parse now stops at "(libparts". build_pcb copies EVERY schematic field (except Footprint/Reference/Value)
     and the DNP flag.
   - New field-sync gate in make_outputs: every footprint's fields, Value and DNP must equal the kicadxml netlist.
     Result: 15 parts, 100 fields compared, **0 mismatches**. Before, R2 had 2 mismatches.
5. **DigiKey fields** (elec F2, DFM F4).
   - LEDs: "" -> "n/a - LCSC only (C210340 warm / C210343 cool)".
   - J1: "DK product 1102472 (...)" -> "612-TSW-102-14-G-D-ND (push out position 4 = J6-12)".
   - BAW56: 1727-2916-1-ND (unchanged, confirmed by both reviews).
   - R1/R2: 541-CRCW0805200RFKEAHPCT-ND.
6. **Silk** (DFM F2).
   - Strokes: the generator widens the stock SOT-23 / R_0805 silk from 0.12 to 0.15, and the J1 outline from 0.12 to
     0.15. On the plotted F_Silkscreen, strokes went from 39 x 0.150 + 34 x 0.120 to **73 x 0.150**. B_Silkscreen is
     399 x 0.150 + 3 x 0.200.
   - Text: "rev A 2026-09-25", "SCREEN", "5", "6" and "11" went from 0.8 to **1.0**, with a 0.15 stroke. The "W"/"C"
     markers also went from 0.8 to **1.0**: 1.0 fits, so the 0.8 exception is not used.
   - "SCREEN" moved 0.1 toward the arrow tail, and "11" moved 0.1 left.
   - The hidden generated-footprint reference went from 0.8 to 1.0, and the DRC min_text_height from 0.8 to 1.0.
   - New gate item: 44 silk strokes, min 0.150; 8 visible silk texts, min 1.000 high / 0.150 stroke.
7. **docs/jlc-notes.md** (new) covers:
   - the EasyEDA LED origin about 0.2 mm off the land centre: the CPL point is the body centre, so check that each
     body is centred and the cathode mark is on the LARGE pad, and reject operator shifts;
   - the BAW56 +180 offset (pin 3 toward the LED row);
   - J1 DNP, with the buy / push-out / jig steps;
   - ENIG preferred (LF-HASL acceptable), gloss black mask, white silk, remove the order number;
   - the two inner R0.35 step corners (accept up to R0.5);
   - Economic PCBA, and a checklist.

   The board finish is now "ENIG preferred (LF-HASL acceptable)" in params.BOARD. The stackup copper_finish is ENIG,
   and the title block and fab notes were updated.
8. **Gate results (final run):**
   - ERC 0. DRC 0 violations / 0 unconnected / 0 parity (--severity-all). Exclusions 0/0, ignored checks 0/0.
   - Handedness/placement gate: PASS, 0 failures.
     - J1 5/6/11 error 0.000; det +1.
     - Nearest copper to J6-12 is 1.690, and to J6-4 1.290.
     - NPTH copper min 0.525 (>= 0.40); tracks 0.525 (>= 0.50).
     - Webs min 0.500 (>= 0.50).
     - Every courtyard is clear of the keep-outs; J1-C2 is at 0.328 under the 0.30 exception.
     - Silk: PASS.
   - Field sync: 0 mismatches.
   - String sanity: PASS. Worst V_OUT is 20.36 < 22.0 V; the TPS923611 peak is 73.5 < 80 mA.
   - E-frame STEP header tips land at Y 107.94 / 121.40.
   - The generated sources (18 files) are byte-identical across two generate.py runs.
