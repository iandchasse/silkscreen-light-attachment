# Final completeness + consistency audit (independent)

Auditor: final-audit subagent, 2026-09-25. Scope: request coverage, cross-document consistency,
reproducibility smoke test, residual risks. Nothing other than this file was edited.

## 0. Inventory snapshot (taken at audit start)

- A = silkscreen-light-attachment, git initialised, branch main, no commits; everything untracked (as required: never commit).
- enclosures/ (a local copy of silkscreen-enclosure-claude) is present but not shown by git status (gitignored).
- Outputs present: pcb/production/{bom.csv, jlc_bom.csv, jlc_cpl.csv, silkscreen-light-attachment_rev-A_gerbers.zip, gerbers/*, 3d/*},
  housing/out/{print/*.stl,*.step, housing-plate.3mf, render/*.png, E/*, checks.json, REPORT.md, slice/*}.
- Timestamp note: housing/out/slice/* written 19:49; housing/out/print/*.stl + checks.json + REPORT.md written 19:53 (see sec 3).

## 1. Request coverage

| # | Requirement (BRIEF) | Status | Where |
|---|---|---|---|
| R1 | New folder `silkscreen-light-attachment` | MET | A = W\silkscreen-light-attachment; git initialised, 0 commits, everything untracked |
| R2 | External attachment on the UNMODIFIED stock enclosure (rev K), through the existing top-wall exposure of J6 | MET | README.md:3,41; housing/out/REPORT.md check 1 (seated vs stock case, all datums 0.000, no undesigned interference) and check 2 (insertion sweep, 0 collisions); fit reference = local copy enclosures/silkscreen-enclosure-claude (rev K, gitignored, .gitignore:30) |
| R3 | Internal light out of scope ("already covered by the light strip") | MET | README.md:8 points to ../silkscreen-light-strip; optics-final.md:3 "Scope: the EXTERNAL clip-on only" |
| R4 | PCBA with LEDs that fit the voltage characteristics | MET (numbers below) | pcb/docs/design_summary.md:7-16; pcb/build/reports/gates.json (strings_ok true) |
| R5 | Male header, safe length and positioning | MET (precautions below) | bom.csv:5, ORDERING.md sec 3, ASSEMBLY.md sec 3-4, REPORT.md checks 2/3/5/9, design_summary.md:88-100 |
| R6 | 3D enclosure parts for a completely separate add-on | MET | housing/out/print/{clip,cover,carrier}.{stl,step}, housing-plate.3mf (3 objects: clip, cover, carrier), renders in housing/out/render/ (6 PNG) |
| R7 | LEDs easily available on LCSC | MET (stock not shown in builder docs, see MINOR m7) | C210340 warm 3000 K, 102,969 in stock; C210343 cool 6000 K, 40,519 in stock; both JLC Extended, 2026-09-25 (design/led-choice.md:57-58). Also C8663 BAW56 43,296 (led-choice.md:114), C5972814 200 R 2,477 (jlc-notes.md:18) |
| R8 | Longer-pin header acceptable | MET | Samtec TSW-102-14-G-D(-004): post .320 (8.13), body .100, tail .110 (2.79), OAL 13.46 (design/spec-audit.md:183; ASSEMBLY.md:43,69) |
| R9 | Nothing written into W\de-link_pcb, W\silkscreen-enclosure-claude, W\silkscreen-light-strip | NO WRITES BY THIS PROJECT FOUND | see sec 1c |

### 1a. Voltage fit (N = 5 per string, Rs 200 R, BAW56 series diode, driver 13.3 mA)

- Per-LED Vf at 13.3 mA 2.60 / 2.85 / 3.15 V -> string 13.00 / 14.25 / 15.75 V (25 C), 16.27 V max at -10 C.
- Rs drop 2.66 V at 13.3 mA; Rs dissipation 39 mW (0.5 W part).
- LED_SW (V_OUT) lit: 16.61 V min hot, 17.98 typ, **20.36 V worst** vs 22.0 V design ceiling (margin 1.64 V) and TPS923610 OVP min 24.25 V (margin 3.89 V).
- Hold-off: ~11.5 V needed for 14 uA > 6.5 V boost body-diode rule, so the string stays dark with the driver off (LED_SW <= 5.2 V).
- LED IF 40 mA abs max vs 13.3 mA shared (33 %). LED_MONIT lit 1.78-2.18 V vs open 2.60-2.73 V (separated, gated).
- Hot-plug peak (C9 at OVP, loop 243.5 R): TPS923610 43.7-49.3 mA; TPS923611 68.0-73.5 mA; misinsertion LED_SW->GND ~79 mA; all < IFP 80 mA (but see MAJOR M1 on the IFP pulse-width condition).
- Independent recompute: I = (V_C9 - 0.8 - 5 V0)/243.5 with V0 2.54 (min) / 2.81 (typ): 31.4 V -> 73.5 / 68.0 mA; 25.5 V -> 49.3 / 43.8 mA. Matches. LED_MONIT = V_OUT x 0.1071: 16.61 -> 1.78, 20.36 -> 2.18. Matches.

### 1b. Header safety precautions and where each is enforced

| Precaution | Enforced by | Evidence |
|---|---|---|
| Header choice: exact Samtec TSW-102-14-G-D(-004), no substitutes; 4-pin part cannot enter the 3-hole footprint unless position 4 is pushed out | BOM + docs | bom.csv:5; ORDERING.md:75-93; ASSEMBLY.md:43; spec-audit.md:38 |
| Engagement stack: pad 115.60 + clip 2.80 + tail pad 3.00 = 121.40; tip Y 107.94; engagement 4.68-5.21 nominal, 4.03-5.64 worst vs 3.68-6.00 window (margins 0.35/0.36) | housing/src/checks.py stack + check 3; pcb make_outputs E-frame STEP assertion | REPORT.md:9,167-169; checks.json meta.pcba_E_stl_crosscheck (107.94 / 121.4, tips_match true); pcb/build/reports/eframe_step_check.json |
| Header length QA (13.46 +0.10/-0.13, tails 1.19 proud) and go-gauge after soldering or any forced attempt | Assembly procedure | ASSEMBLY.md:69-81 (gauge holes 1.10, see m5) |
| Keying: one way only; turned 180 deg the posts (x 2.80 / 5.34) land on solid top face; SCREEN arrow engraved | Case outline + off-centre opening; housing geometry | DESIGN.md:105-107; SAFETY-AND-TEST.md:99-101 (height figure, see m1) |
| Lead-in order: Z guided from h 10.27, X from h 7.31, posts reach J6 face at 5.42..4.89 | housing check 2 (insertion sweep, 0 undesigned collisions, 103 designed spring contacts) | REPORT.md:8,103-131 |
| Float: board floats +-0.30 in the housing so J6 centres the posts; flexure tongues with 45 deg lead-ins | housing checks 5 and 9 (17 X/Z states x seated/resting; lead-in) | REPORT.md:11,16; checks.json 5_float_extremes, 9_tongue_lead_in |
| Strain relief: cover pushes on the tails (tail pad 121.40); 3 x ST2.2 x 6.5 PT screws; removal by grip ribs, never the visor | housing geometry + docs | DESIGN-SPEC.md:263-264; README.md:49; REPORT screws row |
| Pin protection: go-gauge; never plug the bare board; clip fingers/leaf stand 4.7 beyond the post tips off the case (envelope y 103.0 vs tips 107.73) | Docs + geometry | README.md:60; SAFETY-AND-TEST.md:104,112+; mechanical-spec.md:253 (not repeated in builder docs, see m11) |
| No metal at J6-4 (GND) / J6-12 (P+_FUSE): exactly 3 PTH, nearest copper 1.290 / 1.690, nearest hole 2.030 / 1.810 (>= 1.0) | pcb/tools/check_handedness.py gate (blocks make_outputs) | design_summary.md:88,99-100; gates.json handedness_gate PASS; checks.json 3_pins_vs_J6 nearest_metal_to_J6-12 2.54 |
| Handedness gate: J1 pads 5/6/11 at J6-5/6/11 E coords, error 0.000 <= 0.02 via both KiCad and STEP chains, nets match, det +1 | check_handedness.py | design_summary.md:89-98 |
| Series 200 R + BAW56 per string (reverse block, reverse clamp, misinsertion limit) | schematic + string gate | README.md:58; design_summary.md:9-16 |

### 1c. Sibling trees (checked 2026-09-25 ~20:15)

- W\silkscreen-enclosure-claude (not a git repo): **0 files modified today** outside `.venv`. The housing build reads A's own gitignored copy under enclosures/.
- W\de-link_pcb: no tracked diffs (`git diff --stat` empty). Today's mtimes: untracked `NOTICE.md` (15:13; content "Charge enable loses 3V3 when the board is trimmed (x3 build)", unrelated to this project, and already present in the session-start git status), `fp-info-cache` + `silkscreen_pcb.kicad_prl` (15:11) and `silkscreen_pcb-backups/...151600.zip` (15:16) = KiCad GUI session artifacts. None references the light attachment.
- W\silkscreen-light-strip: 6 commits today by Ian Chasse (13:37 .. 20:13, e.g. 7933094 "Fabrication Toolkit support..."), all light-strip work (case variants, fab toolkit). No commit message or tracked file references `light-attachment`. Treated as a separate work stream, not a write by this project; reported for completeness.

## 2. Consistency sample (29 values)

Rule applied: DESIGN-SPEC sec 7 and the "Rev A fixes" sections supersede earlier text, so the 150 R numbers in
DESIGN-SPEC.md:63,91 / pcb/PROGRESS.md:25-61 and the rev 0 items in DESIGN-SPEC sec 4-5 are not counted as mismatches
(pcb/PROGRESS.md:3,64 and DESIGN-SPEC.md:237 mark them superseded; docs/DESIGN.md:205 lists them).

| # | Value | Sources checked | Result |
|---|---|---|---|
| 1 | R1/R2 200 R CRCW0805200RFKEAHP, LCSC C5972814 | DESIGN-SPEC:244; bom.csv:6; jlc_bom.csv:5; design_summary:9,20; jlc-notes:16; ORDERING:58; README:58; ASSEMBLY:35 | OK |
| 2 | Warm LED C210340 (3000 K) D1-D5 | bom.csv:2; jlc_bom.csv:2; design_summary:22; jlc-notes:13; ORDERING:54; led-choice:57 | OK |
| 3 | Cool LED C210343 (6000 K) D6-D10 | bom.csv:3; jlc_bom.csv:3; design_summary:22; jlc-notes:14; ORDERING:55; led-choice:58 | OK |
| 4 | BAW56,215 C8663, pin 3 common anode | bom.csv:4; jlc_bom.csv:4; jlc-notes:15,63; ORDERING:56 | OK |
| 5 | J1 TSW-102-14-G-D-004 / buy 612-TSW-102-14-G-D-ND, push out pos 4 | bom.csv:5; design_summary:21,32; jlc-notes:42-44; ORDERING:79-80; README:29; DESIGN-SPEC:245 | OK (MPN/DigiKey mix is deliberate, DESIGN.md:206) |
| 6 | J1 DNP at JLC | gates.json field_sync.dnp [J1]; bom.csv:5 Assembly col; jlc_bom/jlc_cpl have no J1 | OK |
| 7 | 14 JLC SMT parts | README:28; jlc-notes:9,19,72; design_summary:21; jlc_cpl.csv 14 rows | OK |
| 8 | C2 hole (60.90, -2.54) | DESIGN-SPEC:251; design_summary:55,104; NPTH.drl X160.9 Y-102.54 | OK |
| 9 | +Z flange holes z 18.30 | DESIGN-SPEC:252; design_summary:60-61; NPTH.drl Y-81.7 | OK |
| 10 | Datum holes Ø1.6 at (-2.40,16.00)/(62.40,16.00) | DESIGN-SPEC:119; design_summary:56-57; NPTH.drl X97.6/X162.4 Y-84.0 | OK |
| 11 | Post tip Y 107.94 / tail Y 121.40 | DESIGN-SPEC:254; pcb/PROGRESS:21,157; eframe_step_check.json; checks.json meta; REPORT:9,12,167; ASSEMBLY:121 | OK |
| 12 | Engagement 4.68-5.21 nom / 4.03-5.64 worst / window 3.68-6.00 | README:44; REPORT:9,169; housing/PROGRESS:42 | OK |
| 13 | V_OUT worst 20.36 V (ceiling 22.0, OVP 24.25) | design_summary:12; DESIGN.md:68-69; SAFETY:72; FIRMWARE:35; DESIGN-SPEC:244 (20.4) | OK |
| 14 | Hot-plug 43.7-49.3 / 68.0-73.5 mA; misinsertion ~79 mA | design_summary:15; README:53,58; DESIGN.md:72-73; SAFETY:90-91,108,152-153; DESIGN-SPEC:244 | OK (values); wording vs IFP condition = MAJOR M1 |
| 15 | LED_MONIT lit 1.78-2.18 / open 2.60-2.73 V | design_summary:14; DESIGN.md:71; SAFETY:73; FIRMWARE:35,37; DESIGN-SPEC:244 (1.8-2.2) | OK |
| 16 | Screws ST2.2 x 6.5 PT, Ø1.8 pilot, bore Ø2.5, tip 0.30 above case, engaged 2.5/2.5/2.4 | DESIGN-SPEC:263; checks.json stack.screws; REPORT:17; README:34; ORDERING:140; ASSEMBLY:112 | OK |
| 17 | Dowels Ø1.5 x 4 ISO 8734 in Ø1.55 x 2.4 epoxy | DESIGN-SPEC:260; REPORT:92-97; README:33; ASSEMBLY:93-97; ORDERING:140 | OK except housing/PROGRESS.md:78 (rev 0 "1.5 x 3 in Ø1.45 x 1.5", not marked superseded) |
| 18 | Rod Ø4.0 x 66.0, axis y 113.91 z 15.80, gap 2.0, dz -0.20, bore centre 113.835 | optics-final:70; DESIGN-SPEC:182,191,261; REPORT:26-28,66-70; README:32; ORDERING:99 | OK |
| 19 | Print 21m03s/3.95 g + 24m24s/7.98 g + 10m22s/1.97 g = 55m49s/13.90 g | slice-report.json; REPORT OrcaSlicer block; ORDERING:127-130; README:31; housing/PROGRESS:277-279 | OK except housing/PROGRESS.md:18-20 (rev 0 values) |
| 20 | Envelope x -6.75..66.75, y 103.0..123.40, z -8.95..22.35; 7.8 above top face | DESIGN.md:141; REPORT:196; housing/PROGRESS:217 | OK (PROGRESS:113 is rev 0, superseded at :217) |
| 21 | Board 68.4 x 25.8 x 1.6 | README:28; jlc-notes:22; eframe bbox x -4.2..64.2, z -6.2..19.6; design_summary:5 (K bbox incl. 0.05 edge line) | OK |
| 22 | Retention ~7.97 N (J6 4.17 + friction 3.8), insertion ~8.8 N | REPORT springs section; README:47; DESIGN.md:139; SAFETY:61,134 | OK |
| 23 | Guidance before contact: Z h 10.27, X h 7.31, J6 at 5.42 | REPORT:8,107-121; README:46; DESIGN.md:106; SAFETY:62; housing/PROGRESS:259 | OK except housing/PROGRESS.md:37 (rev 0 "10.06") |
| 24 | 180 deg misfit: posts land on the top face at h ... | DESIGN.md:107 and SAFETY-AND-TEST.md:101 say 7.65; REPORT.md:116,133 as-built = 7.87 (hanging tips 107.73) | MISMATCH (m1) |
| 25 | Left leaf width | DESIGN-SPEC.md:267 and REPORT.md:194 (dev 8) say 5.0; REPORT springs table, REPORT.md:198 (dev 12), DESIGN.md:188 (H7) say 3.8 | MISMATCH (m2; already listed DESIGN.md:200) |
| 26 | Flexure stiffness/force | REPORT.md:187 (dev 1, from housing/src/build.py:28) "2.5-2.9 N/mm, ~0.4/1.2 N" vs REPORT springs table 2.92 N/mm, 0.438/1.315 N | MISMATCH (m3; already listed DESIGN.md:201) |
| 27 | Go-gauge hole | DESIGN-SPEC.md:225 Ø0.84 vs ASSEMBLY.md:76-81 Ø1.10 | MISMATCH (m5; already listed DESIGN.md:197) |
| 28 | CPL vs footprint table | jlc_cpl.csv 14 rows = design_summary x_K / -y_K; rotations LED 180 (+0), BAW56 90+180 = 270, R -90 -> 270 | OK |
| 29 | Gerber zip = 8 Gerbers + PTH + NPTH | unzip -l (10 files, 19:12); jlc-notes:7; ORDERING:9 | OK |

Other label mismatch: pcb/docs/design_summary.md:58-61 (from pcb/tools/params.py) still names H6-H9 "carrier stake pin"; since rev A they are epoxy glue points (DESIGN-SPEC.md:260). Also README.md:104 describes the CQ_PYTHON default loosely (m6).

## 3. Reproducibility smoke test (nothing re-run)

| Command (README) | Script exists | Notes |
|---|---|---|
| `tools\generate.py` (in pcb) | yes, pcb/tools/generate.py | refuses on `*.lck` (generate.py:58); CQ_PYTHON default = pcb\..\..\silkscreen-enclosure-claude\.venv\Scripts\python.exe (generate.py:51-52) -> exists |
| `tools\make_outputs.py` (in pcb) | yes | gates ERC/DRC/parity/handedness/field-sync/strings; last run 19:12, all 0 / PASS (gates.json) |
| `src\build.py` (in housing) `--no-sweep` / `--no-render` | yes; flags at build.py:299,320 | paths from `__file__` (params.py:12), so cwd does not matter; inputs present: pcb/build/geometry.json (19:13), enclosures/.../out/tub.stl, out/lid.stl, hardware/cache/J6.brep |
| `src\slice_check.py` | yes | needs OrcaSlicer |
| `python tools/rod_lens.py --rev2` (`--quick`, `--at`, `--name`) | yes; argparse at rod_lens.py:589-594 | |

Outputs present: pcb/production/silkscreen-light-attachment_rev-A_gerbers.zip (13,290 B, 10 files), bom.csv, jlc_bom.csv (4 lines), jlc_cpl.csv (14 rows), 3d/*.step + *_pcba_E.step/.stl, schematic/layout PDFs, pcb/docs/images/render_top/bottom.png; housing/out/print/{clip,cover,carrier}.{stl,step}, housing-plate.3mf (3 objects clip/cover/carrier), 6 renders (every README image link resolves), checks.json (pass true), REPORT.md (Overall PASS).

Caveat: housing/out/slice/* (19:49) predates the final print STLs/checks/REPORT (19:53). Sources last changed 19:42 and the build is documented byte-identical run to run, so the slice most likely matches, but it is not proven (m12).

## 4. Issues (BLOCKER / MAJOR / MINOR) with exact fixes

No BLOCKER found.

**MAJOR**

- **M1. "Under the 80 mA pulse rating" is claimed for a pulse the rating does not cover.** The Hongli IFP 80 mA is specified only at 0.1 ms, 1/10 duty (design/led-choice.md:61; design/review-electrical.md:78). The hot-plug pulse decays with tau about 0.25-1.1 ms (C9 1-4.7 uF effective x 243.5 R; research/electrical-j6.md:24,161), and SAFETY-AND-TEST.md:93 itself says "the pulse lasts about a millisecond". The misinsertion case (79 mA, "just under the 80 mA rating", SAFETY-AND-TEST.md:108) lasts under about 1 ms. The builder docs (README.md:53, SAFETY-AND-TEST.md:88-93,108, DESIGN.md:72,109, design_summary.md:15, DESIGN-SPEC.md:244) never mention the 0.1 ms condition, so the stated margin is not a datasheet guarantee.
  Fix: in docs/SAFETY-AND-TEST.md after line 91 add: "The 80 mA IFP is rated only for 0.1 ms pulses at 1/10 duty (Hongli datasheet p.4). This pulse decays over roughly 0.25-1.1 ms, so 'under 80 mA' is an estimate, not a datasheet guarantee. Treat 'light off, wait 10 s' as mandatory on every main board." Add the same one-sentence caveat to README.md:53 and to DESIGN.md:72 and :109. In pcb/tools/report_design.py, change the hot-plug line so design_summary.md:15 reads "... both < IFP 80 mA (IFP rated at 0.1 ms / 10 %; pulse tau ~0.25-1.1 ms)".

**MINOR**

- **m1.** DESIGN.md:107 and SAFETY-AND-TEST.md:101 give 7.65 mm (M-spec) for where 180-deg-turned posts land on the top face. As built, REPORT.md:116,133 gives 7.87 mm (hanging tips 107.73; 7.66 with the board pushed up, ASSEMBLY.md:121). Fix: change both to "at about 7.9 mm (REPORT engagement order)".
- **m2.** DESIGN-SPEC.md:267 says "left leaf 5.0 wide", and so does REPORT.md:194 (dev 8, from housing/src/build.py:56). The model, the spring table and REPORT.md:198 say 3.8. Fix: DESIGN-SPEC.md:267 -> "left leaf b 3.8 (z -2.4..1.4), taper 1.4 -> 1.0". At housing/src/build.py:56, append "; rev A MINOR-7 narrowed it again to b 3.8 (z -2.4..1.4)", then regenerate REPORT. Once fixed, remove DESIGN.md:200.
- **m3.** REPORT.md:187 (housing/src/build.py:28) says flexure "k = 2.5-2.9 N/mm, about 0.4 N / 1.2 N". The spring table says 2.92 N/mm, 0.438 / 1.315 N. Fix: build.py:28 -> "As built k = 2.92 N/mm: 0.44 N at the 0.15 preload and 1.32 N at full float". Then remove DESIGN.md:201.
- **m4.** housing/PROGRESS.md has stale rev 0 values with no superseded marker: lines 18-20 (slice 4.01/7.99/1.48 g, 24m16s, 9m57s), line 37 (Z guided from h 10.06) and line 78 (dowels 1.5 x 3 pressed into Ø1.45 x 1.5). The note at :281 covers only the "Open" items. Fix: prefix lines 17, 37 and 78 with "(rev 0, superseded by the Rev A fixes section below)", or replace them with the :277-279 / :259 / :230 values.
- **m5.** DESIGN-SPEC.md:225 still asks for Ø0.84 go-gauge holes, which a correct 0.64 mm square post (0.905 mm across the corners) cannot pass. ASSEMBLY.md:76-81 uses Ø1.10. Fix: add a sec 7 row "Go-gauge holes | Ø0.84 | **Ø1.10 drilled** | posts are 0.905 across the corners; 1.10 keeps +-0.10". Then drop the "until the contract is corrected" wording in ASSEMBLY.md:81 and DESIGN.md:197.
- **m6.** README.md:104 reads "`CQ_PYTHON` defaults to `..\silkscreen-enclosure-claude\.venv\Scripts\python.exe` beside this folder", directly after `cd pcb`. The code default is pcb\..\..\silkscreen-enclosure-claude (generate.py:51-52). Fix: "defaults to `..\..\silkscreen-enclosure-claude\.venv\Scripts\python.exe` relative to `pcb\` (the enclosure repo next to this project folder)".
- **m7.** The user asked for LEDs that are easy to get on LCSC, but the builder docs show no LED or diode stock figures (ORDERING.md:54-56; README has none). Fix: add a Notes column to ORDERING.md:54-56 reading "102,969 / 40,519 / 43,296 in stock on 2026-09-25 (JLC Extended)" (source design/led-choice.md:57-58,114). Add one README line: "All SMD parts are LCSC-stocked JLC Extended parts."
- **m8.** ASSEMBLY.md:93 calls for a 1.5 mm drill (dowel slip holes), but the tool lists at README.md:37 and ASSEMBLY.md:15-16 leave it out. Fix: add "1.5 mm drill" to both.
- **m9.** No acceptance band for the rod diameter. ORDERING.md:99 and the ASSEMBLY rod step say only Ø4.0. The cradle (bore Ø4.15, lip interference 0.16, radial play 0.075; REPORT.md:69-89) and the optics were evaluated only at 4.0, and extruded rod is commonly +-0.1-0.2. Fix: in ORDERING.md:99 add "Measure it: use Ø3.90-4.10. Over 4.15 it will not seat in the bore. Under about 3.9 the lips lose most of their 0.16 preload." Also add "measure the rod with calipers" to the ASSEMBLY rod step. Confirm the band with the planned cradle coupon (DESIGN.md:207).
- **m10.** Pin protection off the case (finger and leaf tips stand 4.7 mm beyond the post tips; mechanical-spec.md:253; envelope y 103.0 vs tips 107.73) is not stated in the builder docs. Fix: add to DESIGN.md header-safety section (near :105): "Off the case the clip fingers and leaf stand 4.7 mm beyond the post tips, so the light can be set down on its clip without loading the posts." Add a storage line to ASSEMBLY.md sec 7.
- **m11.** pcb/docs/design_summary.md:58-61 labels H6-H9 "carrier stake pin", but they have been glue points since rev A (DESIGN-SPEC.md:260). Fix: rename the four descriptions in pcb/tools/params.py to "carrier glue point (epoxy), -Z/+Z flange" and regenerate.
- **m12.** housing/out/slice/* (19:49) is older than the final print STLs (19:53), so the slice was not proven to match the shipped STLs. Fix: re-run `housing/src/slice_check.py` then `build.py` (so REPORT folds the new slice in), or have slice_check.py write the SHA-256 of each STL into slice-report.json.
- **m13.** Header sourcing: no DigiKey stock figure is recorded for 612-TSW-102-14-G-D-ND. The LCSC -004 (C20382277) and the 4-pin C3332404 were both out of stock (spec-audit.md:34-35). Fix: in ORDERING.md sec 3 (after :80), add "Check DigiKey or Samtec stock for the header before ordering the PCBA. There is no substitute."

Already self-documented in DESIGN.md sec 10 (no further action beyond the fixes above): go-gauge, J6 entry, pin-to-opening clearance 0.865 < 1.0, leaf width, flexure force, LED_MONIT 150 R, glue, beam width 21/22 deg, stale sections, bom.csv J1 MPN/DigiKey mix.

## 5. Residual risks a builder must know

| Risk | Stated in docs? | Where |
|---|---|---|
| Nothing printed, ordered or powered (Rev A untested) | YES, prominent | README.md:10-16 |
| J6 entry size known only from models (1.40 face / 1.1-1.14 / 1.04) | YES | DESIGN.md:198; SAFETY-AND-TEST.md sec 7; README.md:14 |
| LED IFP margin (73.5 mA on TPS923611; pulse ~10x longer than the 0.1 ms IFP condition) | PARTIAL: numbers and "small margin on 611" stated; the pulse-width condition is not | README.md:53,59; SAFETY-AND-TEST.md:93 (see M1) |
| PETG creep and spring relaxation (back fingers 2.61 N, strain 0.52-0.96 %) | YES | SAFETY-AND-TEST.md:132-141 (7-day check, 5 N floor) |
| Rod lens tolerance (diameter; rod-to-LED dz registration ~10 deg aim per 0.4 mm) | PARTIAL: dz sensitivity in optics-final.md:146 and cradle coupon listed open; no diameter band in builder docs | see m9 |
| Header sourcing (-004 out of stock; hand push-out; no substitutes) | YES, but no DigiKey stock figure | ORDERING.md:75-93; ASSEMBLY.md:43 (m13) |
| Hot-plug pulse never measured on a scope | YES | DESIGN.md:207 |
| TPS923611 main boards: higher OVP, light-off rule mandatory | YES | README.md:59 |
| J3 frontlight present shares the 13.3 mA driver | YES | README.md:61 |
| JLC LED library origin 0.2 mm off: reject operator shifts | YES | jlc-notes.md:48-59; ORDERING.md:67 |
| Pin-to-opening clearance 0.865 at full float (< 1.0 contract) | YES | DESIGN.md:199 |
| Fit on the real case (only CAD fit checks) | YES | README.md:13 (print the clip first) |

## Verdict

The requested scope is covered: a new folder, an external clip-on on the unmodified rev K case, a PCBA with voltage
margins shown, a guarded long-post header, three printed parts, and LCSC-stocked LEDs. The generated outputs agree with
DESIGN-SPEC sec 7 on every key number sampled. No BLOCKER. One MAJOR: M1, the IFP pulse-width caveat, which is
documentation only and changes no hardware. Thirteen MINOR, mostly stale or loosely worded text, and several of them
the docs already disclose.
