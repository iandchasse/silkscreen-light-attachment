> **Superseded by [DESIGN-SPEC-revB.md](DESIGN-SPEC-revB.md) (rev A, archived).** This is the rev A (rod lens) contract,
> kept for history. Rev A's files are in `archive/rev-A-rod-lens/`. Do not build from this file.

# Silkscreen light attachment: design spec (implementation contract)

Status: frozen for rev A implementation, 2026-09-25. This file is the single source of truth. Where it disagrees with
another design file, this file wins. Details it does not repeat come from:
- `design/mechanical-spec.md` (M-spec): clip and cover geometry, stack, springs, printing.
- `design/spec-audit.md` (audit): fixes, all adopted below.
- `design/optics-final.md` "Rev 2" (optics): rod geometry and keep-out.
- `design/led-choice.md`: LED, resistor and diode sourcing.
- `research/electrical-j6.md`: electrical limits.

`design/parts.md` and optics-final sections 0-4 are superseded for part numbers and geometry.

## 0. Scope
An **external clip-on** warm/cool reading light for the **unmodified** stock enclosure (silkscreen-enclosure-claude
rev K). It plugs into the main board's J6 through the case's existing top-wall J6 opening and lights the page from the
top edge. The in-case variant is out of scope; the light-strip project covers it.

Deliverables:
- **PCBA:** a generated KiCad project under `pcb/`.
- **Printed parts:** a CadQuery project under `housing/` with three parts: clip, cover and rod carrier.
- **Fit checks:** against the stock case copy in `enclosures/silkscreen-enclosure-claude` (read-only reference).
- **Docs:** README, ordering, assembly, safety/bench test and firmware notes.

## 1. Frames
- **Enclosure frame (E).**
  - X = main-board KiCad X - 44.24.
  - Y = 148.25 - main-board KiCad Y, so +Y is the device's top edge.
  - Z = 0 at the main-PCB rear face, and +Z points toward the screen/reader.
  - All mechanical numbers in this file are in E.
- **Light-PCB KiCad frame (K).** The light PCB lies in E's X-Z plane.
  - **F.Cu faces -Y, toward the case.** It is the component side: LEDs, resistors, diodes and the header body are
    all on F.Cu, so JLC does a normal single-sided top assembly.
  - B.Cu faces +Y, toward the cover roof. It carries no parts; only the header tails stick out of it.
  - Viewed from F (looking +Y from below the board), screen-right = +X and screen-up = +Z.
  - **Mapping:**
    - x_K = X + 100.000
    - y_K = 100.000 - Z
  - Examples:
    - the LED row z 16.00 is at y_K 84.00;
    - the header's far row z -3.81 is at y_K 103.81.
- **STEP from K to E.** kicad-cli STEP uses (x_s, y_s, z_s) = (x_K, -y_K, z), with F.Cu at z_s = 0 and B.Cu at
  z_s = -1.6. With the seated PCB underside at Y 118.61:
  - X = x_s - 100;
  - Y = 118.61 - z_s;
  - Z = 100 + y_s.

  The determinant is +1, so this is a proper rotation. Verify it numerically on the pads.
- **Handedness gate (audit M3), scripted, run in make_outputs, fails the build.**
  - Transform every PTH centre to E and require LED_SW at (54.662, -3.810), W- at (57.202, -3.810) and C- at
    (54.662, -1.270), each within 0.02.
  - Require no hole or copper within 1.00 of (57.202, -1.270) = J6-12 /P+_FUSE or of (52.122, -3.810) = J6-4 GND.
  - Require J1's pad nets to match.

## 2. Electrical
Per colour string: J1-5 LED_SW -> 5 LEDs in series -> Rs -> node N -> BAW56 common anode (pin 3). BAW56 pin 1 (K1)
goes to the string's return contact (the block diode). BAW56 pin 2 (K2) goes back to the LED_SW anode bus (the clamp,
which holds the string's reverse voltage to one diode drop).

| Ref | Qty | Part (Value = MPN) | Mfr | DigiKey | LCSC | Notes |
|---|---|---|---|---|---|---|
| D1-D5 | 5 | HL-A-3014H421W-S1-08HL-HR3 **3000 K** | HONGLITRONIC | none (allowed for the LEDs) | **C210340** | warm string -> W- (J1-6). 3014, 3.00x1.40x0.70. **Pad 1 (large, 1.91x0.92) = cathode** = the chamfered cavity corner (led-choice.md sec 4). The MPN does not encode CCT: the LCSC field is the BOM key and must be in the Value/Description |
| D6-D10 | 5 | same MPN, **6000 K** | HONGLITRONIC | none | **C210343** | cool string -> C- (J1-11) |
| R1, R2 | 2 | **150 R** pulse-proof 0805: CRCW0805150RFKEAHP (Vishay) if LCSC stocks it (>= 1k); else Panasonic ERJ-P06F1500V; else 120 R CRCW0805120RFKEAHP (LCSC C844392, DigiKey 541-120TCT-ND) | | yes | yes | 150 R: hot-plug peak 52-64 mA stays under the LED's 80 mA IFP (120 R gives 60-77 mA). Worst V_OUT 19.7 V, under the 22 V ceiling. Record the final choice and why |
| D11, D12 | 2 | BAW56,215 | Nexperia | yes | **C8663** | SOT-23. Pin 1 = K1, pin 2 = K2, **pin 3 = common anode** (Nexperia Table 2). D11 warm, D12 cool |
| J1 | 1 | **TSW-102-14-G-D-004** | Samtec | TSW-102-14-G-D (1102472); push position 4 out if only this is available | **C20382277** (out of stock 2026-09-25: JLC global sourcing, consign, or DNP + hand solder; **no substitution**) | 2x2, .320 [8.13] gold post, .110 [2.79] tail, .100 body, position 4 omitted |

- **J1 footprint.** A custom `J6_PLUG_3PIN` with three PTH, drill 1.02 and pad 1.70.
  - Pads are **named by the J6 pin they mate:** "5" LED_SW, "6" W-, "11" C-.
  - Pad positions in E:
    - "5" at (54.662, -3.810);
    - "6" at (57.202, -3.810);
    - "11" at (54.662, -1.270).
  - There is **no hole at (57.202, -1.270)**, J6-12.
  - Body courtyard/fab: 5.08 x 5.08, x 53.392..58.472, z -5.080..0.000, on F.
  - Samtec map, for the docs: pos 1 = J6-5, pos 2 = J6-11, pos 3 = J6-6, pos 4 (omitted) = J6-12.
- **Nets.**
  - LED_SW (J1-5, anode bus).
  - W- (J1-6).
  - C- (J1-11).
  - Internal: warm chain nodes, N_W; cool chain nodes, N_C.
  - There is no GND, no 3V3 and no other J6 net anywhere on the board.
- **Rules.**
  - The whole board is SELV, at most 31.4 V. Default 0.2/0.2 rules.
  - Current is 14 mA, so 0.25 mm traces; use 0.4 where convenient.
  - No copper pour; if a pour is used, it must stay floating and far from J1.
  - Black soldermask (matte if JLC offers it): the LED channel's ceiling is the PCB underside, and the optics assume
    black.
  - White silk on B.Cu (the top): name, rev, date, "SCREEN" arrow toward +Z, and the pin labels 5/6/11 by the tails.
- **Firmware notes, docs only** (the firmware repo is not changed): research/electrical-j6.md sec 6.
  - Enable pulse of at least 100 us.
  - LED_MONIT open-load check (open about 2.60-2.73 V; lit about 1.8-2.2 V with 150 R).
  - OVP-latch recovery.
  - Advise "light off before plugging in".

## 3. PCB (generated KiCad project, `pcb/`)
Reuse the silkscreen-light-strip generator architecture: params.py -> generate.py -> netlist -> build_pcb.py ->
make_outputs.py, plus kigeom.py. Apply its 20 review lessons (research/light-strip-reuse.md sec 6):
- clean template: no ERC exclusions and no ignored DRC checks;
- deterministic UUIDs;
- STEP models;
- a gate before any fab output is written;
- fab-only gerber zip;
- env-var KiCad paths;
- DigiKey + LCSC fields;
- per-part CPL rotation offsets derived from the LCSC/EasyEDA footprints;
- a refuse_if_open .lck check.

The project name is `silkscreen-light-attachment`, rev A, 2 layers, 1.6 mm, JLC standard.

**Outline (E, X-Z):**
- main body x -3.50..63.50, z -6.20..**19.60**;
- widened to x **-4.20..64.20** over z **12.10..19.60** for the carrier datum-hole webs;
- all convex corners R1.0, and a small R0.5 where the width steps.

**Holes (all NPTH, no copper within 0.40 of the edge):**
| Purpose | Dia | E (X, Z) |
|---|---|---|
| Cover column / float stops (audit m4) | 4.20 | C0 (5.00, 0.50); C1 (47.00, 2.35); C2 (61.00, -2.54) |
| Carrier datum pins | 1.60 | (-2.40, 16.00), (62.40, 16.00) |
| Carrier stake pins, -Z flange | 1.60 | (15.00, 13.10), (45.00, 13.10) |
| Carrier stake pins, +Z flange | 1.60 | (15.00, 18.40), (45.00, 18.40) |

**Placement on F.Cu (E):**
- **LEDs**, centres at z **16.00**, long axis along X, emitting -Y:
  - warm D1..D5 at x **1.1, 14.6, 28.1, 41.6, 55.1**;
  - cool D6..D10 at x **4.9, 18.4, 31.9, 45.4, 58.9**.
  - Orient every cathode (pad 1) the same way along the string's current direction, and keep the silk cathode bar.
- **R1, R2, D11, D12:** in zone A. Suggested: x 31..41, z -3..3; or x 9..23. Height <= 2.0.
- **Underside keep-outs** (no parts; traces are fine):
  - back rail z <= -3.80, and z <= -5.30 over x 52.6..59.3;
  - front rail z 3.80..8.00;
  - P1 x 1.6..8.4 and P2 x 23.6..30.4, both at z -3.3..4.3;
  - boss/P3 block x 42.6..58.7, z 0.2..4.5, and x 42.6..53.0, z -5.5..0.3;
  - left end block x <= 2.4 over z -6.2..5.0 (audit m6);
  - right end block x >= 58.9 over z -6.2..5.0;
  - column holes +0.4.
- **Height zones:**
  - z 8.0..11.8: height <= 2.0;
  - z 11.8..19.6: LEDs only (the carrier channel and flanges; its walls sit at z 12.5..13.7 and 18.1..19.1, and the
    flanges reach z 17.2 on the +Z side);
  - nothing may overlap a carrier flange footprint:
    - -Z flange z 12.0..14.2;
    - +Z flange z 17.2..19.3;
    - x -4.2..64.2 at the end walls, x -4.2..-1.0 and 61.0..64.2.
- **Routing:** both layers. The anode bus runs from J1-5 to D1 and D6, the chains run along the row, and the returns go
  back to R/D11/D12 and on to J1-6 / J1-11. Keep traces 0.5 off the NPTH holes.

**Outputs:**
- ERC/DRC at 0 with parity, plus the handedness gate. Nothing is written if any gate fails.
- Gerbers and a fab-only zip `production/silkscreen-light-attachment_rev-A_gerbers.zip`.
- `production/bom.csv` (Qty, Refs, Value, Mfr, MPN, DigiKey, LCSC, Footprint).
- `jlc_bom.csv` and `jlc_cpl.csv` (F side, rotations verified).
- Schematic and layout PDFs.
- STEP with LED/header/diode/resistor models, **plus an E-frame PCBA STEP** (transform per sec 1) for the housing fit.
- `build/geometry.json` in E: outline, holes, LED body boxes, part boxes, header pins with tips at Y 107.94 seated,
  underside Y 118.61.
- Renders.
- `docs/design_summary.md`.

## 4. Printed parts (CadQuery project, `housing/`, enclosure venv python)
Build clip and cover exactly as M-spec secs 3-4, with these audit changes:
- **Centering (mandatory), audit M4/M5.** Horizontal cantilever tongues cut into the cover walls: 8 long along the edge,
  0.8 thick, 1.5 tall, centred on y 119.4 (on the PCB edge, both seated and resting), with a 0.5 slot behind and a 0.15
  bump. k is about 0.75 N/mm.
  - Left: x -3.50 edge, z 0..3.
  - Right: x 63.50 edge, z 10..11 region (clear of C2).
  - Back: z -6.20 edge, x 20..28.
  - Front: on the **PCB front edge** z 19.60, x 26..34, never on the carrier.
- **Columns (audit m4):** Ø3.60 columns with a Ø2.3 bore in the Ø4.20 PCB holes (float 0.30), 100 % infill; screws
  ST2.2 x 6 plastic thread-forming, Ø1.6 pilots.
- **Cover skirt:** inner face at z >= 20.30 (PCB edge 19.60 + 0.3 float + 0.4), bottom at y 110.0; or omit it if the
  carrier's +Z wall alone looks right. Front-region end walls must clear the widened PCB (x -4.20 / 64.20) and the
  carrier end walls by >= 0.4 at full float.
- **Left end block** (audit m6): x -5.8..2.0, z -6.55..4.6, underside y >= 116.0, >= 0.4 off the R5 corner.
- **Orientation cue** (audit m7): a moulded arrow + "SCREEN" on the cover roof pointing +Z.
- Correct the engagement-order table per audit m1, and the side-flat z range per m10.

**Rod carrier (new part; PCB-registered, floats with the PCB), from optics Rev 2 and audit M6/m3/m8:**
- **-Z wall:** 1.2 thick, z 12.50..13.70, from the PCB underside (118.61) down to y **113.91** (the rod equator).
- **+Z wall = the optical front lip:** 1.0 thick, z 18.10..19.10, from the PCB down to **y 110.0**.
- **End walls:** x -4.20..-1.00 and 61.00..64.20. Each has a **C-cradle** socket opening toward +Y: bore Ø4.10-4.20,
  a 200-220 deg wrap, 2.0 deep, centred at **(y 113.91, z 15.80)**. The rod (clear PMMA Ø4.0 x 66.0, x -3.0..63.0) snaps
  in before the carrier is fitted to the PCB.
- **Top flanges:** along both walls, flat on the PCB underside:
  - -Z flange z 12.00..14.20;
  - +Z flange z 17.20..19.30.
- **Pins:**
  - 2 datum pins Ø1.50 in the end walls, into the PCB Ø1.60 holes at (-2.40, 16.00) / (62.40, 16.00);
  - 4 stake pins Ø1.50 at the flange holes, heat-staked on the PCB top, heads <= 0.6 tall (roof clearance 1.19).
- Matte black PETG. Printed flanges-down (the PCB face on the bed) so the walls grow as prisms.
- The rod-to-LED geometry (gap 2.0, dz -0.20) is held by the carrier + PCB, to +-0.1 target.
- The carrier must keep >= 0.40 from the cover and clip everywhere at full float (+-0.30 X/Z, 0.21 Y).

**Housing checks (scripted, in `housing/`, results to `housing/out/checks.json`; the build fails on any violation):**
1. Seated interference against the stock case (`enclosures/.../out/tub.stl` + `lid.stl`, or the STEPs). Only designed
   contacts are allowed:
   - P1/P2/P3 on the top face;
   - the lip on the front face;
   - the right ear;
   - the back-finger bumps (0.30) and the left-leaf bump (0.40).
   Report every other minimum gap.
2. Insertion sweep along -Y from h 15 to 0 in 0.25 steps: no collision except the designed springs and ramps. Report
   the engagement order heights.
3. Pins against J6: tips at Y 107.94 seated; engagement against J6 face 112.82..113.15. Pins clear the opening walls by
   >= 1.0.
4. Optics keep-out: no clip/cover/carrier solid inside the Rev 2 keep-out polygon over x -1.0..61.0.
5. PCBA fit at float extremes, using the E-frame PCBA STEP or a PCBA proxy built from `pcb/build/geometry.json` (use the
   proxy until the PCB exists).
6. Printability: overhang faces > 50 deg in the print orientation are flagged; minimum wall >= 1.0 except the declared
   1.2 springs.
7. Exports: STL/STEP per part in print orientation, a 3MF plate, and a PNG render set (assembly on the case, section
   through J6, section through the rod).

## 5. Bill of materials: mechanical
- Clip, cover and carrier (PETG, black, matte).
- Clear PMMA rod Ø4.0 x 66.0 (cast or extruded, cut square). No DigiKey source is verified; buy from a plastics
  stockist, and note the McMaster/Amazon class.
- 3 x ST2.2 x 6 PT screws.
- Optional: M2x12 plus the back screw-lock tab (M-spec 3d).

## 6. Documentation to produce
- `README.md`: what it is, a photo/render, a status banner ("rev A, untested"), the safety rules, and links.
- `docs/DESIGN.md`: the why, generated numbers.
- `docs/ORDERING.md`: JLC form fields; header sourcing; rod.
- `docs/ASSEMBLY.md`: coin-cell polarity test of one LED first; tail-length QA; go-gauge (Ø0.84 holes); carrier + rod
  assembly; cover screws snug.
- `docs/SAFETY-AND-TEST.md`:
  - hot-plug advice;
  - a meter check of each string;
  - an LED_MONIT reading;
  - fitting on the case;
  - measuring J6 entry size;
  - a 7-day spring check.
- `docs/FIRMWARE-NOTES.md`.

## 7. As-built changes and review decisions (rev A, 2026-09-25)
These supersede the matching lines above. The reasons are in `pcb/PROGRESS.md`, `housing/PROGRESS.md` and
`design/review-*.md`.

**Electrical**

| Item | Was | Now | Why |
|---|---|---|---|
| R1, R2 | 150 R CRCW0805150RFKEAHP (C313835) | **200 R CRCW0805200RFKEAHP, LCSC C5972814** | Keeps the hot-plug peak (about 73 mA) and the LED_SW-to-GND misinsertion current (about 79 mA) under the LED's 80 mA IFP on TPS923611 main boards too. On TPS923610 boards the peak is about 49 mA. Worst V_OUT is 20.4 V, under the 22 V ceiling. LED_MONIT lit reads 1.8-2.2 V against 2.60 V open. |
| J1 at JLC | placed from C20382277 | **DNP at JLC; hand-soldered by the builder** | C20382277 is out of stock and JLC will not modify parts. Buy TSW-102-14-G-D (DigiKey 612-TSW-102-14-G-D-ND), push out position 4 (J6-12), and solder it with the posts plugged into a 2.54 mm female header as a jig. Check with the go-gauge. |

**PCB**

| Item | Was | Now | Why |
|---|---|---|---|
| C2 column hole | (61.00, -2.54) | **(60.90, -2.54)** | 0.40 web to the edge, raised to 0.50. |
| +Z-flange carrier holes | z 18.40 | **z 18.30** | Same web reason. |
| Width-step fillets | R0.5 | **R0.35** (both convex and concave) | The step is only 0.70 wide. |
| Enclosure-frame STEP | F.Cu at z_s 0 | kicad-cli puts the slab at z 0..1.51 and seats F models at z 1.595 | make_outputs calibrates on the J1 body. Tips land at Y 107.94 and 121.40. |

**Printed parts**

| Item | Was | Now | Why |
|---|---|---|---|
| Carrier pins | printed pins, heat-staked | **2 steel dowels Ø1.5 x 4 (ISO 8734) set in epoxy in Ø1.55 holes, plus epoxy at the 4 flange holes** | Printed pins cannot exist with the carrier printed flanges-down. Heat-staking is dropped. |
| Rod cradle | mouth toward +Y | **mouth toward -Y; bore crown is the datum (bore centre y 113.835); compliant lips preload the rod onto the crown; epoxy dot at each rod end** | The datum dowel sits above the rod end. The rod sagged 0.26 mm on the old mouth edges. |
| Centering | floating 1.5 mm tongues | **full-height U-slit flexures in the cover walls, with 45 deg lead-ins on the bumps** | Support-free printing. They take the PCB edge without hanging up. |
| Screws | M2 / ST2.2 x 6 in Ø1.6 pilots | **ST2.2 x 6.5 PT (DIN 7981 class) in Ø1.8 pilots; column bore Ø2.5** | Thread engagement goes from 2.0 to 2.5. The tip stays 0.30 above the case top. |
| Grip | none | **grip ribs on both cover end faces** | Remove the light by its ends, never by the visor, which levers the posts in J6. |
| Springs | as M-spec | **R1.5 roots, 1.4 -> 1.0 taper** | Creep and delamination margin. |
| Bumps and lip | as M-spec | **R0.3 on the bump crests, R0.5 on the lip bottom edge** | Scuffing. |
| Other | | left leaf 3.8 wide (z -2.4..1.4, 1.4 -> 1.0 taper); corner fingers 1.5 thick; P3 pad z0 0.7; back-rail notch z -5.80 | as recorded in housing/PROGRESS.md |
| Go-gauge holes | Ø0.84 | **Ø1.10, drilled** | The posts are 0.64 mm square, 0.905 mm across the corners. Ø1.10 keeps ±0.10 on the corners. |
| Post-to-opening clearance (check 3) | >= 1.0 | **>= 0.8 at full float** (1.165 nominal, 0.865 at full float) | Posts never touch the plastic walls; the J6 lead-in centres them. |

**Ordering**
- ENIG preferred; LF-HASL acceptable.
- Black mask. JLC has no matte black; gloss black is fine.
- Economic PCBA, top side, no rails.
- In JLC's placement preview, check that every LED body sits centred on its lands and that its cathode mark is on the
  LARGE pad. The EasyEDA footprint origin is about 0.2 mm off the land centre.
