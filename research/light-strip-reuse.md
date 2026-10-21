# silkscreen-light-strip -> light-attachment reuse analysis

`LS` = `W\silkscreen-light-strip` (READ-ONLY; git repo with **no commits**). W = the workspace folder that holds the sibling repos. Status: DONE 2026-09-25.

**Version drift:** `LS/tools/params.py:85` says `per_string: 6` (6 warm/cool pairs, pitch 15.55, plus a 3.68in hinge). README, DESIGN.md and ASSEMBLY.md still describe the 5-pair rev A (pitch 18.56). The current state is params.py plus `docs/images/optics_summary.json` and `production/*.csv` (D1-D12, D13/D14). Use DESIGN.md for the reasoning.

## Key numbers
| Item | Value | Source |
|---|---|---|
| Drive current | 200 mV / R37 15 ohm = 13.3 mA nominal, 13.9 mA max; one string at a time | LS/docs/DESIGN.md:16 |
| OVP (TPS923610) | 24.25 / 25 / 25.5 V; latches after 3 trips; reset with ADIM low > 2.5 ms | DESIGN.md:17 |
| LED_SW design ceiling | 22 V at -10 C | DESIGN.md:41; params.py:85 |
| Lower limit | string must hold off > ~5.2 V (boost body diode); J6 rule: >= 3 LEDs, Vf > 6 V | DESIGN.md:18; de-link_pcb/docs/HARDWARE.md:1177-1184 |
| LEDs per string | 5 (rev A, 15.5 V typ) or **6 (params, 21.7 V worst case incl. BAV70W)**; 7 hits OVP cold; 3 fails if one LED shorts | DESIGN.md:32-43; params.py:85 |
| LED | XINGLIGHT XL-4008WWC 3000 K (LCSC C5440667) / XL-4008UWC 6000-6500 K (C2843774); side-view, 4.0x1.4x0.8 mm; LCSC-only, JLC Extended | params.py:80-84; leds.md:14-21; README.md:46 |
| LED ratings | IF 20 mA, IFP 80 mA, VR 5 V, Pd 70 mW, ESD 2 kV, 120 deg; Vf 2.7-3.3 V @20 mA (bins N11-8, N11-9, N12-1), ~2.9-3.0 V @13 mA; MSL 3 | leds.md:70, 99-114 |
| LED land pattern | 1.6 x 1.1 pads at +/-1.85 (params trims depth to 1.0); face 1.0 ahead of the pad centreline (EasyEDA-derived) | leds.md:89-96; params.py:88-90 |
| Flip diode | Nexperia BAV70W,115, SOT-323, LCSC C28064, DigiKey stock; drop 0.65-0.95 V | params.py:141; DESIGN.md:41-43; README.md:46 |
| LED_MONIT | LED_SW x 0.1071; lit <= 1.96 V, open >= 2.49 V (first ~0.2 s only) | DESIGN.md:20, 47 |
| Side-strip optics (6 pairs) | pitch 15.55, face gap 1.197, h 0.785; near/far 233 @2, 36.5 @10, 9.9 @20 mm; scallop 1.51 @10 | docs/images/optics_summary.json |
| **Top-edge optics (model, 6 pairs)** | pitch 9.28, gap 1.197, h 0.785; near/far **2017 @2, 196 @10, 46.8 @20, 9.3 @40 mm**; scallop 1.69 @10; ends/mid 0.647 | optics_summary.json case 4; optics_sim.py:212-214 |
| Top border under the bezel | 2.74 - 0.7 = 2.04 mm | LS/docs/research/mechanical-fit.md:182 |
| CPL rotation offsets | `SOT-323_SC-70` +180, `LED_SideView_XINGLIGHT_XL-4008` +0 | make_outputs.py:135 |
| KiCad python | `C:\Program Files\KiCad\9.0\bin\python.exe` (pcbnew 9.0.6) | README.md "Regenerating"; memory kicad-mcp-server-install.md |

## 1. Pipeline architecture
The data flows `params.py` -> `generate.py` (footprints, 3D, symbols, schematic, project) -> kicad-cli netlist -> `build_pcb.py` (the board is built from the netlist, so parity holds) -> `make_outputs.py` (checks, then fab and docs outputs).

| Script | Role |
|---|---|
| `params.py` | Every dimension, rule and part, in dicts (PANEL, ACTIVE, J3, FLEX, RULES, LED, BAR, PAIRS, TAIL, DIODE). |
| `kigeom.py` | `uid()` (uuid5), S-expression formatting, `rounded_path` (fillets -> line/arc prims), polygons. |
| `generate.py` | In order (:677-687): `refuse_if_open` (a `*.lck` is present, :51); footprints; symbols; schematic (its own `Sch` writer); project files (lib tables, .kicad_pro from `tools/template.kicad_pro` with rules overwritten, .kicad_dru); `kicad-cli sch export netlist` parsed to pad->net; `build_pcb.build`. |
| `build_pcb.py` | Text skeleton (stackup, layers, title), then `LoadBoard`, `FootprintLoad`, placement, Edge.Cuts, tracks/arcs/vias by net, rule areas, User.1-4, silk, teardrops, `SaveBoard`. |
| `make_outputs.py` | `checks` -> `gerbers` + zip -> `boms` -> `cpl` -> `docs` (PDFs, STEP, VRML, renders). |
| `report_design.py` | Read-only pcbnew dump -> docs/reports/design_summary.md |
| `export_geometry.py` | build/geometry.json: outline polygon, LED ref/colour/x/y, body dimensions, diodes, stiffeners, panel/active, main-board box. It is copied into the enclosure as `hardware/reference/light-strip/strip-geometry.json` (LS/enclosures/silkscreen-enclosure-claude/src/params.py:378). |
| `optics_sim.py` | numpy/matplotlib model -> optics PNGs + JSON. No KiCad needed. |
| `make_step_model.py` | LED STEP body: a dummy 4.0x1.4 board, `kicad-cli pcb export step --board-only` |
| `foldpath.py`, `blender_fold.py` | Flex tail length and fold renders. Flex-only. |

**Commands** (close KiCad first):
```
"C:\Program Files\KiCad\9.0\bin\python.exe" tools\generate.py
"C:\Program Files\KiCad\9.0\bin\python.exe" tools\make_outputs.py
python tools\optics_sim.py        # numpy+matplotlib; env LED_FULL_ANGLE_H/_V (default 120)
"C:\Program Files\KiCad\9.0\bin\python.exe" tools\export_geometry.py
blender -b -P tools/blender_fold.py -- 64
```
Environment variables:
- `KICAD9_DIR` (generate.py:44) locates kicad-cli and the stock libraries.
- `KICAD_CLI` (make_outputs.py:29) overrides the kicad-cli path.
- `make_step_model.py:17` still hard-codes the kicad-cli path.

**Gate** (make_outputs.py:39-61, 172-179):
- `checks()` runs `kicad-cli sch erc --severity-all` and `pcb drc --schematic-parity --severity-all`, writing .rpt and .json. It accepts exit codes 0 and 5.
- It then adds up ERC violations, DRC violations, unconnected items and parity items from the JSON.
- A non-zero total raises `SystemExit` **at the end, after every output has been written**.
- Any other kicad-cli failure aborts at once (`run()`).
- Current result: ERC 0, DRC 0/0/0.
- Coverlay-opening clearances and webs were measured separately, because DRC treats mask-to-copper clearance as 0 (DESIGN.md:264).

## 2. Symbols, footprints, 3D, fields, JLC rotations
- **Project library, regenerated each run** (`lib/<name>.pretty|.kicad_sym|.3dshapes`):
  - LED footprint written from params, with F.Fab K/A labels, an arrow and a silk cathode bar (generate.py:154-199).
  - SOT-323 copied from stock `Package_TO_SOT_SMD/SOT-323_SC-70`, body silk stripped (:234-265).
  - Symbols extracted from stock `Device:LED`, `Diode:BAV70`, `Connector_Generic:Conn_01x06` and `Connector:TestPoint`, then renamed (:348-383).
  - 3D: generated VRML (:281-302) plus a STEP from make_step_model. The footprint references only the `.wrl` (lib LED .kicad_mod:25), so the STEP export needs `--subst-models` (K10, open).
- **Fields** (generate.py:506-532): `Value` = MPN, plus `Footprint`, `Datasheet`, `Description`, `MPN`, `Manufacturer`, `LCSC`. Non-parts are `in_bom no`.
  - **There is no DigiKey field.** The strip is LCSC-primary because its LEDs are sold only through LCSC.
  - The new design must be DigiKey-primary: Value/MPN/Manufacturer orderable at DigiKey, plus a `DigiKey` field and a separate `LCSC` field (memory rule).
- **BOM** (make_outputs.py:84-123) comes from the kicadxml netlist, grouped by (Value, Footprint, LCSC).
  - `jlc_bom.csv` columns: `Comment,Designator,Footprint,JLCPCB Part #`.
  - `bom.csv` columns: `Qty,Designators,Value,Manufacturer,MPN,LCSC,Footprint,Description`. The new design should add a DigiKey column.
- **CPL** (make_outputs.py:126-142) runs `kicad-cli pcb export pos --format csv --units mm --side front --exclude-dnp`, then applies `rot = (Rot + offset[Package]) % 360`.
  - `jlc_cpl.csv` columns: `Designator,Mid X,Mid Y,Layer,Rotation`, e.g. `D1,44.2000mm,-50.4500mm,Top,270.0`.
  - Y comes out negative because kicad-cli uses Y-up.
  - The offsets were derived from EasyEDA footprints (`easyeda.com/api/products/<C#>/components?version=6.4.19.5`). Example: C28064 at EasyEDA 0 deg matches KiCad's SOT-323 at 180 deg (DFM-2).
  - Re-derive the offset for every new part.

## 3. LED choice and alternatives for a rigid top-edge bar
- **Chosen:** XL-4008 (see Key numbers). About 110 JLC catalogue queries, the LCSC JSON, the JLC assembly-class API and EasyEDA footprints were used (leds.md:25-37).
- **Runners-up** (leds.md:43-57):
  - XL-2810 pair (C3646946/C5440675): 1.2 mm tall.
  - XL-3806: the "warm" part is really 1800-2000 K.
  - MEIHUA MHS110WDT 1204: the cool part is about 8000 K, specified only at 5 mA, and rated ESD 150 V.

**Polarity lesson** (E1/DFM-1 BLOCKER; electrical.md:21-80, dfm.md:15-32): the first layout was mirrored.
- The datasheet's p.7 views are unlabeled.
- The two EasyEDA libraries number the pads oppositely: WWC pad 1 is the anode, UWC pad 1 is the cathode.
- The fix was three independent derivations: with the lens up, seen from the top, the anode is LEFT and the cathode RIGHT (DESIGN.md:103-116).
- A side-view LED cannot be fixed by rotating it.
- Keep the silk cathode bar, the fab K/A labels and the light arrow, and diode-test one loose LED first (ASSEMBLY.md step 1).

**Two ways to mount the LEDs on a rigid bar:**
- **(a) PCB parallel to the panel**, with side-view LEDs as on the strip. The XL-4008 reuses directly, at 0.8 mm plus the PCB thickness.
- **(b) PCB edge-on**, its underside facing down the screen, with **top-view** LEDs whose axis runs along the page. The emitter height is then about half the package width plus the edge clearance (INFERRED).

Top-emitting warm parts named in leds.md:254-255 were rejected there only because they are not side-view. **None has an LCSC or DigiKey number in LS (UNVERIFIED).**
| Package | Warm part (leds.md) | Note |
|---|---|---|
| 0603 | XINGLIGHT XL-1608WWC-06; TOGIALED TJ-S1608CY6T5ALC3DW-A5 | lowest h when edge-on |
| 0805 | XL-2012WWC | |
| 1206 | XL-3216WWC | |
| 3014 | XL-3014WWC-02 | no cool top-view sibling found; XL-C3014UWC C2843795 is side-view, 7000-7500 K (leds.md:250) |
| 3528 / PLCC-2 | XL-3528WWC | tall |
| 3528-4P dual CCT | TOGIALED TJ-S3527UG2W4TLCDWTW-A5, LCSC C440512 (2700-3300 K + 5500-7000 K) | one package mixes perfectly; taller |

2835 is not in leds.md, so it needs a new search. Requirements for whatever is chosen:
- a warm/cool pair in the same footprint;
- IF >= 20 mA and VR >= 5 V;
- **no ESD Zener** (a string would then conduct in reverse; DESIGN.md:56-57);
- a DigiKey-orderable pair, preferably.

## 4. Flip / reverse protection (BAV70W)
**Why the strip has it.** J3 contacts both faces, so a face-down tail mirrors pin k to pin 7-k (DESIGN.md:52-76).
- Each string gets a BAV70W. A1 is a series block rated 100 V, against 25.5 V OVP. A2 clamps the string to about -0.65 V.
- Flipped or open, no current flows and OVP latches.
- There is no TVS on the flex, because it has no ground.

**J6 pin map** (HARDWARE.md:1116-1122):

| Row | Pins |
|---|---|
| 1 | 1 GND, 2 IO46, 3 IO45, 4 GND, 5 LED_SW, 6 W- |
| 2 | 7 3V3, 8 SDA, 9 IO3, 10 SCL, 11 C-, 12 P+ (raw battery, PPTC 0.75 A) |

**Mis-insertions of a 2x6 plug into an unkeyed socket** (INFERRED from the map):
- **Rotated 180 deg.** The bar's LED_SW lands on SDA, its W- on 3V3 and its C- on IO46. At most 3.3 V appears across a string of at least 15 V, so this is benign with or without the diode.
- **Shifted one column toward pin 1.** The bar's W- lands on LED_SW and its LED_SW on GND. The open driver boosts to about 25 V, **reversed across the warm string**: about 4.2 V per LED at N = 6, at the 5 V VR limit. The BAV70W's A1 blocks this and A2 clamps. This is the case the diode is for.
- **Shifted one column the other way.** The bar's C- lands on P+. The BAV70W keeps this benign.

**Recommendation:**
- Keep one BAV70W per string. It is 2 parts, and BAV70W,115 is stocked at DigiKey.
- **Also key the plug mechanically**, with a shroud or housing that prevents offset or rotation.
- Fit only the pins the bar needs, or leave unused pins unconnected. Never route to 12 (P+), 2/3 (strapping pins) or 7/8/10.

**ESD.** D3 SMAJ26A and D8 PESD2IVN-UX sit beside J6 (DESIGN.md:21), so the plug gets better ESD cover than J3 did.

## 5. optics_sim.py and re-targeting
- **Model** (optics_sim.py:1-64): point sources at height h, axis parallel to the page; intensity cos^m x cos^n (120 deg -> m = n = 1); E = I cos(inc)/r^2, cos(inc) = h/r. Geometry only.
- **Inputs:** ACTIVE rectangle, (cool, warm) positions per pair, face_gap, h, m, n, `axis` ("x" left edge, "y" top edge).
- **Outputs:** near/far at 2-40 mm, scallop at 3/6/10/20 mm, ends/mid at 10 mm, mix error, PNGs, JSON.
- **What it favoured for the side strip:**
  - Warm/cool pairs beat alternating W/C: mix error 0.104 vs 0.122 at 10 mm, scallop at 20 mm 1.15 vs 1.49 (DESIGN.md:131-136).
  - The current layout is 6 pairs at 15.55 mm pitch, 6.6 mm LED-to-LED within a pair (params.py:88-104).
  - The faces sit 1.197 mm outside the active area and 0.5 mm behind the aperture.
- **The top edge is already a case** (:212-214, `axis="y"`): 6 pairs over 55.68 mm (pitch 9.28, +/-3.3 within a pair), throwing 92.8 mm. It is 5-10x steeper than the side strip, which is why LS chose the long edge (mechanical-fit.md:177-189).
- **To re-target it:**
  1. Add bar parameters: pair x positions; face gap measured to the ACTIVE top at y 40.35; and h.
  2. Choose h per variant: about 0.4-1.0 mm in-bezel, or the lip height plus a few mm outside the case (INFERRED).
  3. **Add a downward tilt.** Replace the separable cos^m cos^n with the cosine of the angle between the tilted axis and the ray. A raised, tilted source reduces the near-edge hot spot.
  4. Sweep h, tilt, gap and pitch with per_string limited to 5-6.

## 6. Review lessons (do not repeat)
1. Mirrored LED polarity from an unlabeled datasheet view (E1/DFM-1): 3 independent sources, silk/fab marks, diode test before ordering.
2. BAV70W CPL 180 deg off (DFM-2/E2): per-footprint offset table; check JLC's placement preview.
3. DRC can't see mask openings/webs (DFM-3/4/5): measure separately.
4. Template carried 44 ERC exclusions + 7 ignored DRC checks (K1/K4), so "0 violations" was hollow. Start clean; per-footprint `allow_soldermask_bridges`. LS still ignores npth/pth_inside_courtyard.
5. Generator tied to `../de-link_pcb`, non-atomic writes (K2): validate inputs, write to temp then move, own template.
6. Hard-coded KiCad paths (K12; `make_step_model.py:17` still): env var, then `shutil.which`.
7. LED 3D model .wrl only (K10, open): point models at STEP so enclosure CAD sees parts.
8. Random board KIIDs -> ~3,700-line diffs (K9): hash with `uid()`.
9. MCP: fab graphics outside courtyard -> false positives; `run_drc` writes beside the board. Never aim it at the repo; `KICAD_BACKEND=swig` (K7/K11).
10. Doc Gerber (Bend_Zones) + .gbrjob in the upload zip (DFM-7): zip fab layers only.
11. Order settings missing; User.Comments never plotted (DFM-6): ORDERING.md with exact form fields and remark.
12. No panel/fiducials for PCBA (DFM-8): plan panelisation or order bare.
13. Part 0.06 mm under the bezel ceiling (M2); LED faces visible off-axis (M1): check against the real enclosure; black mask; visor.
14. Enclosure clash found only at the final check (DESIGN.md:169-176): export geometry.json into the enclosure build and check there (LS: STRIP_GEOMETRY, STRIP_CEIL, STRIP_HOLD, strip_check -> out/light-strip.json).
15. Docs drifted from params (5 vs 6 LEDs): generate numbers; one source of truth.
16. make_outputs writes production files even when checks fail: gate them.
17. Bench test missed an S-C/S-W short (~0.3 A through R37): add a meter check (DESIGN.md:289).
18. Open string reads high only ~0.2 s before the latch decays (DESIGN.md:47, 290).
19. Silk on creases, schematic text overlaps (DFM-11/K3): silk >= 1.0/0.15.
20. No commits/.gitignore (K5; LS still none).

## 7. Reuse plan
**Copy and adapt:**

| File | Change |
|---|---|
| `params.py` | Add J6 (2.54 mm pitch, pin map, position) and a rigid stackup. Keep LED, DIODE, RULES, ACTIVE and PANEL, and add DigiKey fields. |
| `kigeom.py` | As is. |
| `generate.py` | Keep refuse_if_open, the stock-symbol extraction, the Sch writer, write_project_files (with rigid rules), the netlist step, the LED/SOT footprint writers and the VRML/STEP. Replace the tail with a male header from KiCad stock `Connector_PinHeader_2.54mm` (right-angle or straight). |
| `build_pcb.py` | Keep Builder, the skeleton writer with a rigid stackup, and the teardrops. |
| `make_outputs.py` | Gate before writing; filter the zip; add a DigiKey column; set new CPL offsets. |
| `optics_sim.py` | Add tilt and the bar parameters. |
| `export_geometry.py` | Export for both enclosure variants. |
| Also keep | `report_design.py`, a clean `template.kicad_pro`, and the `.kicad_dru` pattern. |

**Drop** (flex-only):
- foldpath.py and blender_fold.py
- the J3 gold-finger tail
- coverlay, stiffener, 3M tape and bend zones
- the PANEL_368/HINGE/FOOT/NECK/TAIL/FLEX parameters

**Keep these outputs:**
- ERC and DRC with parity (.rpt + .json)
- Gerbers, drill and `<name>_rev-X_gerbers.zip`
- bom.csv, jlc_bom.csv and jlc_cpl.csv
- schematic PDF and multipage layout PDF
- STEP (`--subst-models`) and VRML
- `pcb render` PNGs
- build/geometry.json and design_summary.md
- optics PNG and JSON
