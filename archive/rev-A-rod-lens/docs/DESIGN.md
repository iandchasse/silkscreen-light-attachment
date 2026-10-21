# Design rationale (rev A)

This is the "why" behind the light attachment. The binding contract is [design/DESIGN-SPEC.md](../design/DESIGN-SPEC.md); its §7 ("As-built changes and review decisions") overrides its earlier sections. Every number here is copied from a generated file or a design note, and the source is named next to it. A few values are worked out here; they are marked **derived**. Where two sources disagree, both are given in [§10](#10-known-inconsistencies-and-open-items).

Status: designed and checked in CAD. **Not built or tested.**

## 1. Frames and words used

- **Enclosure frame (E)**, in mm. X runs along the top edge (screen-right is +X). Y runs up the device, so the top face of the case is at y 115.60. Z = 0 is the main board's rear face, and +Z points toward the reader. X = main-board KiCad X − 44.24; Y = 148.25 − main-board KiCad Y.
- **Light-board KiCad frame (K).** x_K = X + 100, y_K = 100 − Z. KiCad's "top" (F.Cu) faces **down, toward the case**. It is the component side: all LEDs, resistors, diodes and the header body are on it. KiCad's "bottom" (B.Cu) faces up, into the cover, and carries only the header tails and the white text.
- "Seated" means the clip is pushed fully onto the case.

## 2. Why the top edge

- The stock case (silkscreen-enclosure-claude rev K) is closed apart from its openings. The only opening that reaches a light connector is the one in the top wall above `J6` (x 42.582..58.922, z −5.415..0.215; [research/enclosure.md](../research/enclosure.md)).
- `J6` carries the same three frontlight nets as `J3`: LED_SW on pin 5, W− on pin 6 and C− on pin 11 ([research/electrical-j6.md](../research/electrical-j6.md) §1). A light plugged into `J6` therefore uses the stock driver (TPS923610, 13.3 mA regulated, warm/cool selected by the firmware) with no board or firmware change.
- `J6` sits at the top edge of the main board, so the light lives above the top edge of the screen and shines down the page. The in-case, side-lit option is the separate light-strip project.

## 3. Why a rod lens

The LEDs sit 10 mm in front of the case face (row centre z 16.00) and shine straight down the page. A bare 120° LED at that spot lights the top of the page far more than the bottom. The options were ray-traced ([design/optics-final.md](../design/optics-final.md) §1; these are the rev 1 numbers, same layout, PCB 0.47 mm lower):

| Option | Brightest band ÷ bottom edge (FT01C / plain panel) | Verdict |
|---|---|---|
| Bare 3014 LED, 120° | 73.1 / 65.2 | rejected: very top-heavy |
| Bare 3014 + best printed knife-edge | 37.3 / 29.1 | rejected: still top-heavy, and it wastes light |
| Ideal 40° lensed SMD LED | 8.22 / 6.91 | rejected: no warm + cool family could be sourced |
| 30° lensed SMD or 3 mm THT LED | about 4.3 / 3.7 | rejected: dark band at the top and scallops between LEDs |
| **3014 LED + 4.0 mm clear PMMA rod under it** | **4.96 / 3.93** | **picked** |

The rod works as a cylindrical lens. It bends light that would hit the top of the page toward the middle and bottom. It is one piece of stock plastic, cut to length. Its ends sit in black sockets, so they need no polishing. The board stays flat, single-sided and machine-assembled.

The rod-to-LED position matters more than anything else in the optics: about 10° of beam aim per 0.4 mm of rod offset (optics-final R2.3). That is why the rod sits in a carrier pinned to the light board itself, not to the housing, and why the rev A cradle datums the rod on a fixed crown instead of loose mouth edges (§7).

## 4. What the reader sees

Rev 2 numbers, for the Hongli LEDs at the as-built height ([design/optics-final.md](../design/optics-final.md) "Rev 2", R2.1 and R2.2). Warm string at the full 13.3 mA, typical flux 6.5 lm per LED:

| Item | Value |
|---|---|
| Rod | clear PMMA Ø4.0, 66.0 long; axis at y 113.91, z 15.80; 2.0 below the LED faces, 0.20 toward the page |
| Beam | peak 3.75° toward the page, 21° wide at half power |
| Illuminance, glossy frontlit panel (FT01C) | top edge (2 mm down) 250 lux, mid-page 655 lux, bottom 185 lux |
| Illuminance, plain panel | top 183 lux, mid 626 lux, bottom 197 lux |
| Brightest band ÷ bottom edge | 5.54 (FT01C), 4.95 (T01C), 4.58 (plain) |
| Where the brightest band is | 10 to 20 mm below the top of the active area (1.4 to 1.5 × mid-page) |
| Ends of the row vs middle | 0.73 at 10 mm down |
| Shadow band at the top | none |
| Cool string | about 1.08 × the warm numbers (7.0 lm typical) |

Notes:
- The firmware dims from these values. It also switches between warm and cool at 10 kHz, so at 50 % warmth each string is on half the time.
- The top 2 to 5 mm of the page is dimmer than the middle (0.38 to 0.81 × mid on FT01C). It reads as a soft, darker top edge.
- The carrier's front wall (the optical lip, bottom edge at y 110.0) hides the bright rod from the reader's eyes. It may sit anywhere from y 108.01 to 111.07 (optics-final R2.1).
- Tolerance: over a ±0.2 mm box of rod gap and offset, the worst band ratio is 7.13 (FT01C). Moving the whole board ±0.3 mm in Z changes almost nothing (R2.3). The as-built cradle puts the rod axis at (113.910, 15.800), against a target of ±0.05 ([housing/out/REPORT.md](../housing/out/REPORT.md) check 8).

## 5. Electrical window

Each colour is one string: LED_SW (`J6`-5) → 5 LEDs in series → **200 Ω** → BAW56 common anode (pin 3). BAW56 cathode 1 goes to the string's return (W− on `J6`-6, or C− on `J6`-11): this is the **block** diode. BAW56 cathode 2 goes back to LED_SW: this is the **clamp** diode, which holds any reverse voltage across the string to one diode drop.

From [pcb/docs/design_summary.md](../pcb/docs/design_summary.md) (generated by `pcb/tools/report_design.py`, and gated by `make_outputs.py`):

| Item | Value |
|---|---|
| String current (set by the main board's R37) | 13.3 mA nominal, 13.96 mA max |
| 5 × LED forward voltage at 13.3 mA | 13.00 / 14.25 / 15.75 V (min / typ / max, 25 °C); 16.27 V max at −10 °C |
| 200 Ω drop | 2.66 V at 13.3 mA (2.79 V at 13.96 mA); 39 mW |
| Driver output LED_SW when lit | 16.61 V min (hot), 17.98 V typ, **20.36 V worst** (cold, highest LED bin) |
| Design ceiling / over-voltage trip (TPS923610) | 22.0 V (margin 1.64 V) / 24.25 V min (margin 3.89 V) |
| String hold-off at about 14 µA, hot | 11.5 V, above the 6.5 V needed to stay dark while the driver is off (its output then sits at the supply minus a diode drop, up to 5.2 V) |
| LED_MONIT (main-board sense divider, × 0.1071) | lit **1.78..2.18 V**; nothing attached 2.60..2.73 V (separation gated) |
| Hot-plug peak (driver capacitor C9 at over-voltage; loop 243.5 Ω incl. 200 Ω; typ..min LED bin) | TPS923610 (25.5 V): **43.7-49.3 mA**. TPS923611 (31.4 V): **68.0-73.5 mA**. Both under the LED's 80 mA pulse rating (gated). That IFP is specified only for 0.1 ms at 1/10 duty and this pulse lasts about 0.25-1 ms, so the margin is an estimate |
| LED_SW-to-ground misinsertion, TPS923611 | about 79 mA until the over-voltage latch |

The hot-plug model is I = (V_C9 − 5 V0 − 0.8) / (17 + Rs + 5 × 5.3) ([design/review-electrical.md](../design/review-electrical.md); [pcb/PROGRESS.md](../pcb/PROGRESS.md), rev A fixes).

**Why 5 LEDs.** 5 clears both limits for every LED class, and with one LED shorted the other 4 still stay dark while the driver is off (above 6.5 V). 6 does not fit under the 22 V ceiling once a series resistor is added. 5 is also what the stock panel frontlight uses ([research/electrical-j6.md](../research/electrical-j6.md) §3).

**Why 200 Ω (it was 150 Ω).** The contract picked 150 Ω, which keeps a TPS923610 board's hot-plug pulse at 52-64 mA. The independent electrical review ([design/review-electrical.md](../design/review-electrical.md) F3) pointed out that main boards built with the TPS923611 swap part charge C9 to up to 31.4 V, which gives 78-96 mA through 150 Ω: over the 80 mA rating. 200 Ω brings that to 68.0-73.5 mA and the LED_SW-to-ground misinsertion from about 101 to about 79 mA. The cost is small:
- worst LED_SW rises from 19.66 to 20.36 V (margin to the 22 V ceiling 2.34 → 1.64 V);
- resistor power rises from 29 to 39 mW;
- LED_MONIT lit moves from 1.71-2.11 to 1.78-2.18 V, still well apart from the 2.60 V open reading.

The part is Vishay CRCW0805200RFKEAHP (LCSC C5972814), a pulse-proof 0805. It must be pulse-rated: a hot-plug puts about 0.5 to 1.1 W into it for about a millisecond (**derived**: I² × 200 Ω at 49 / 73.5 mA).

**Why diodes on the cathode side.** They block the warm-to-cool cross path in every misinsertion case, with or without Zeners inside the LEDs. These LEDs have no Zener and are rated for only 5 V reverse, so the clamp matters ([design/led-choice.md](../design/led-choice.md) §4).

## 6. Header safety and keying

**Pins.** `J1` is a Samtec 2 × 2 header with a long gold post (.320", 8.13 mm), a short tail (.110", 2.79 mm) and **position 4 removed**: either the TSW-102-14-G-D-004, or the stocked TSW-102-14-G-D (DigiKey 612-TSW-102-14-G-D-ND) with position 4 pushed out. It is **DNP at JLC and hand-soldered by the builder**, with the posts held square in a 2.54 mm female header as a jig ([pcb/docs/jlc-notes.md](../pcb/docs/jlc-notes.md); [ASSEMBLY §3](ASSEMBLY.md#3-fit-j1)). The footprint has three plated holes (drill 1.02, pad 1.70), named after the `J6` pin each one mates with:

| Pad | `J6` pin | Net | Position (E, X / Z) | Samtec position |
|---|---|---|---|---|
| 5 | 5 | LED_SW | 54.662 / −3.810 | 1 |
| 6 | 6 | W− | 57.202 / −3.810 | 3 |
| 11 | 11 | C− | 54.662 / −1.270 | 2 |
| (none) | 12 | P+_FUSE (battery) | 57.202 / −1.270 | 4, removed, **no hole** |

The generated gate checks each pad to within 0.02 mm (all at error 0.000), and requires no copper or hole within 1.00 mm of `J6`-12 or `J6`-4. As built, the nearest copper to `J6`-12 is 1.690 mm and to `J6`-4 (ground) 1.290 mm ([design_summary.md](../pcb/docs/design_summary.md), handedness gate). The electrical review confirmed the pads and nets with its own pcbnew parse ([design/review-electrical.md](../design/review-electrical.md) VERIFIED 1 and 4).

**Why only three pins.** A pin at `J6`-4 would be harmless while it floats, but a solder bridge to pin 5 would short the light supply to ground. That is the worst fault on this connector, because the current is limited only by the battery ([research/electrical-j6.md](../research/electrical-j6.md) §5). A pin at `J6`-12 would put the raw battery on the light. The empty corner also works as a physical check: a 4-pin TSW-102 will not go into the 3-hole footprint until its fourth pin is removed.

**Why the header is hand-soldered.** The -004 (LCSC C20382277) was out of stock on 2026-09-25, JLC will not modify a stocked part, and JLC's hand soldering does not hold the post height and squareness that the tip positions (Y 107.94 / 121.40) rely on ([design/review-dfm.md](../design/review-dfm.md) F5).

**Keying.** The `J6` key boss cannot key: it enters only in the last 1.4 mm, long after the posts. Keying comes from the case outline and the off-centre opening:
- the clip's fingers locate front-to-back from 10.27 mm above seated and sideways from 7.31 mm; the posts meet `J6` at 5.42..4.89 mm ([housing/out/REPORT.md](../housing/out/REPORT.md), engagement order);
- turned 180°, the posts land on the solid top face (at x 2.80 / 5.34) at about 7.9 mm above seated (as-built engagement order in housing/out/REPORT.md), so no contact is possible. Each post then carries the push; its buckling load is about 56 N ([design/mechanical-spec.md](../design/mechanical-spec.md) §3d).

**Pin protection off the case.** The clip's fingers and leaf stand 4.7 mm beyond the post tips, so the light can be set down on its clip without loading the posts.

**Misinsertion without the housing.** Every shift and rotation of a bare plug was enumerated ([research/electrical-j6.md](../research/electrical-j6.md) §5; re-run on the real pads in review-electrical VERIFIED 8). All are inert except the anode on LED_SW with a return on pin 4 (ground). There, the series resistor (at least 68 Ω is enough) lets the driver reach its over-voltage limit and latch off in under about 1 ms; with 200 Ω the pulse is about 79 mA even on a TPS923611 board. So the housing is the key, and the resistor is the backstop.

## 7. Mechanical datum scheme

**Height (Y).** The header body cannot rest on the case: it fits inside the opening and would bottom out in `J6`. So the stack is ([housing/out/REPORT.md](../housing/out/REPORT.md), engagement stack):

| Step | Y |
|---|---|
| Case top face | 115.60 |
| Clip pads P1/P2/P3 on the top face; clip top | 118.40 (+2.80) |
| Cover roof pad pushes the header tail tips | 121.40 (+3.00) |
| Post tips (121.40 − 13.46 overall header length) | 107.94 |
| Board underside when seated / resting on the clip | 118.61 / 118.40 |

The push is on the tails, so each post is in pure axial compression and the solder joints carry no load ([design/spec-audit.md](../design/spec-audit.md) m9). That is why the tail-to-tip length (13.46 +0.10 / −0.13) is checked after soldering and why no solder may sit on the tail tips. Engagement in `J6`: 4.68..5.21 nominal, 4.03..5.64 worst, against a 3.68..6.00 window ([housing/out/checks.json](../housing/out/checks.json)).

**Front-to-back (Z).** Datum: the clip's front lip on the flat bezel band of the front face. Preload: two back spring fingers, 0.30 mm interference, 2.61 N each (0.43..4.78 N over tolerances), k 8.69 N/mm. The fingers taper from 1.4 to 1.0 mm with R1.5 roots, for creep margin.

**Sideways (X).** Datum: an ear on the right side. Preload: a left spring leaf, 0.40 mm interference, 1.11 N (0.42..1.8 N), k 2.77 N/mm.

**The board floats.** Three cover columns pass through Ø4.20 holes in the board, so it can move ±0.30 mm in X and Z. Four full-height flexures in the cover walls centre it lightly (0.44 N preload, 1.32 N at full float, k 2.92 N/mm), so `J6` itself lines up the posts. The flexure bumps have 45° lead-ins, so the cover goes on over the board edge without hanging up. Pin clearance to the opening walls: 1.165 mm nominal, 1.115 mm centred, 0.865 mm at full float.

**Carrier.** The rod carrier is registered to the board, not the housing.
- Two steel dowels, Ø1.5 × 4 mm (ISO 8734), are set in epoxy in Ø1.55 × 2.4 holes in its end walls. They pass through the Ø1.60 board holes at (−2.40, 16.00) and (62.40, 16.00) and finish flush with the board's top.
- Four Ø1.60 holes over the flanges (z 13.10 and 18.30) take epoxy. Glue-dam grooves along the flange edges keep it out of the channel.
- The cradle opens away from the board (−Y). The rod datums on the top of the bore (bore Ø4.15 centred at y 113.835, so the rod axis sits at 113.91, 2.00 below the LED faces). Four curved lips (0.8 thick, 0.16 mm interference, about 2.7 N each) press it up onto that crown in any orientation, and an epoxy dot on each rod end is the long-term retention.
- The carrier floats with the board and keeps at least 0.443 mm from the clip and cover at every float position (REPORT check 5).

**Screws.** Three ST2.2 × 6.5 plastics thread-forming screws (PT / DIN 7981 class) go through the cover columns (bore Ø2.5) into Ø1.8 through-pilots in the clip. They engage 2.5 / 2.5 / 2.4 mm, and each tip stops 0.30 mm above the case top (REPORT, screws).

**Retention.** About 7.97 N to pull off (`J6` contacts 4.17 N + friction 3.8 N), about 8.8 N to push on; the target is 5 to 12 N. There is no snap: the case has no undercut near the top. Grip ribs on both cover end faces and a fingernail ledge on the back wall give a straight pull, because pulling the visor levers the posts ([design/review-mechanical.md](../design/review-mechanical.md) MAJOR-4). If retention proves too low, the mechanical spec has an optional M2 × 12 screw-lock tab ([design/mechanical-spec.md](../design/mechanical-spec.md) §3d).

**Envelope.** x −6.75..66.75, y 103.0..123.40, z −8.95..22.35: the attachment stands 7.8 mm above the top face of the case.

## 8. What was checked, and how

- **PCB** (`pcb/tools/make_outputs.py`, [pcb/docs/reports/](../pcb/docs/reports/)). Nothing is written unless every gate passes:
  - ERC 0 with no exclusions; DRC 0 violations, 0 unconnected, 0 parity errors, with no ignored checks;
  - the header handedness and keep-out gate, including every NPTH-to-edge web ≥ 0.50 mm and the silk minimums (0.15 mm strokes, 1.0 mm text);
  - the string-voltage check, which now fails on the TPS923611 hot-plug peak or on poor LED_MONIT separation;
  - the field-sync check (100 footprint fields against the netlist, 0 mismatches) and the DNP check (J1 only, 14 JLC parts, 14 CPL rows).
- **Housing** (`housing/src/checks.py`, [housing/out/REPORT.md](../housing/out/REPORT.md)), all PASS:
  - seated interference against the stock case meshes;
  - an insertion sweep from 15 mm to 0 in 0.25 mm steps;
  - post engagement in `J6` and the optics keep-out;
  - board and carrier clearance at ±0.30 mm float in 16 directions, seated and resting;
  - printability and exports;
  - the rod datum (check 8), the flexure lead-in (check 9) and the screw stack.
- **Slicing** (OrcaSlicer, Elegoo Centauri Carbon 2, PETG): all three parts slice with no warnings and no supports.
- **Not checked by anything yet:** a real print on a real case, a real `J6` entry, spring force after days of load, the hot-plug pulse on a scope, and the light on a real page.

## 9. As-built deviations from the contract

From [pcb/PROGRESS.md](../pcb/PROGRESS.md) and [pcb/docs/design_summary.md](../pcb/docs/design_summary.md):

| # | Deviation | Why |
|---|---|---|
| P1 | Outline step fillets R0.35 + R0.35, not R0.5 | each width step is only 0.70 mm |
| P2 | kicad-cli puts the board slab at z 0..1.51 and parts at z 1.595, not F.Cu at 0 | kicad-cli 9.0.6 behaviour. The E-frame STEP is calibrated on the header body; post tips land at 107.94 / 121.40 as required. Use `pcb/build/geometry.json` for fit checks |
| P3 | LED cathode mark is two short bars over pad 1, not a bar across the end | pads inside a warm/cool pair are only 0.43 mm apart |
| P4 | LED courtyard is pads + 0.195 mm | the 3.8 mm pair pitch |
| P5 | Keep-outs are checked by script, not by KiCad rule areas | the column holes legitimately sit inside keep-outs |
| P6 | C2 column hole at X 60.90 (was 61.00); +Z flange holes at z 18.30 (was 18.40) | 0.50 mm FR-4 web to the edge (was 0.40). J1's body is then 0.328 mm from the C2 hole edge, under the 0.4 rule; the gate allows 0.30 for that pair only |
| P7 | Cool-string links moved from y_K 83.10 to 83.15 | keep 0.525 mm from the moved +Z holes |
| P8 | `J1` DNP at JLC, left out of `jlc_bom.csv` / `jlc_cpl.csv`; DigiKey field 612-TSW-102-14-G-D-ND | the -004 is out of stock and JLC will not modify parts |
| P9 | R1/R2 200 Ω (was 150 Ω) | TPS923611 hot-plug margin (§5) |
| P10 | Silk strokes widened to 0.15 mm and text raised to 1.0 mm | DFM review F2 (legibility at JLC) |
| P11 | Fab outputs carry timestamps | the KiCad sources themselves are byte-identical run to run |

From [housing/PROGRESS.md](../housing/PROGRESS.md) and [housing/out/REPORT.md](../housing/out/REPORT.md):

| # | Deviation | Why |
|---|---|---|
| H1 | Centering flexures are full height (y 119.05..123.40), cut through the roof with U-slits; k 2.92 N/mm, not about 0.75. 45° lead-in on each bump (full crest from y 119.55) | a 1.5 mm tongue floating mid-wall is an 8 mm unsupported overhang when the cover prints roof-down; the lead-in stops the bump from landing square on the board edge |
| H2 | Flexure face 0.45 behind the board edge, with a 0.60 bump | the rigid root never touches the board at full float |
| H3 | Carrier pins are 2 steel dowels Ø1.5 × 4 in epoxy; the 4 stake holes are glue points with glue dams; no heat-staking | printed pins would point into the print bed; a 1.5 × 3 press fit would split the 0.675 mm wall and is not a stocked length |
| H4 | Rod cradle opens away from the board (−Y); the rod datums on the bore crown, preloaded by curved lips; epoxy dot on each rod end. Carrier end walls widened to z 12.00..19.60 | the material above the rod must carry the dowel; the rod sagged 0.26 mm on the old mouth edges |
| H5 | Rod socket depth 2.2 mm, not 2.0 | 0.20 mm axial play per end for a hand-cut rod |
| H6 | Clip pad P3 edge 0.6 → 0.7; back-rail notch −5.70 → −5.80; notch face x 59.3 → 59.2 | the header body keeps ≥ 0.40 mm at full float |
| H7 | Left leaf narrowed to b 3.8 (z −2.4..1.4); left corner-finger side part at z 2.5..4.2 | the M-spec leaf and finger overlapped; the taper needed a narrower leaf at the same k |
| H8 | Declared thin walls: C1 pilot 0.75 / 0.85; C2 pilot 0.80 (0.60 after thread forming); dowel hole 0.625 wall and 0.30 floor; column wall 0.55; cradle lips 0.8; slot strips 0.525; flange at the glue dams 0.7 | forced by the contract geometry |
| H9 | Roof 1.8 thick, tail pad 0.20 proud at 121.40, column bosses Ø5.2, counterbores Ø4.4 × 1.0 | stack datum and screw heads |
| H10 | Cover walls 0.75 off the board edges; skirt inner face z 20.35; end walls x −4.95 / 64.95; 3 grip ribs on each end face and a fingernail ledge on the back wall | clearance at full float; removal without levering the posts |
| H11 | Screw pilots Ø1.8 through holes; column bore Ø2.5; ST2.2 × 6.5 screws | 2.5 mm thread engagement instead of 2.0; blind holes would leave floors under 1.0 mm |
| H12 | Springs taper 1.4 → 1.0 with R1.5 roots; corner fingers 1.5 thick; bump crests R0.3; lip bottom edge R0.5; text engraved 0.4 deep; elephant-foot chamfers left to the slicer | creep margin, less scuffing, printability |

## 10. Known inconsistencies and open items

- **Go-gauge hole size.** The contract asks for Ø0.84 holes (audit M4, "tips within ±0.10"; the mechanical spec had Ø0.95 for ±0.15). The posts are 0.64 mm square, 0.905 mm across the corners, so they cannot enter a round 0.84 hole. The contract now specifies drilled Ø1.10 holes (DESIGN-SPEC §7), which give the intended ±0.10 on the corners; see [ASSEMBLY §4](ASSEMBLY.md#4-header-qa-length-and-go-gauge). Resolved.
- **`J6` entry size** is known only from models: 1.40 mm square at the face (vendor STEP), 1.1..1.14 mm at 0.15 mm in (research/enclosure.md), 1.04 mm at 0.1 mm in (housing check model). Measure a real one ([SAFETY-AND-TEST §7](SAFETY-AND-TEST.md#7-measure-the-j6-entry)).
- **Pin clearance to the opening wall** at full float is 0.865 mm, under the original 1.0 mm (DESIGN-SPEC §4 check 3); §7 now accepts >= 0.8 at full float (1.165 nominal). The `J6` lead-in centres the posts before the float matters.
- **Left leaf width.** 3.8 mm (z -2.4..1.4) with the 1.4 -> 1.0 taper; DESIGN-SPEC §7 and REPORT now agree. Resolved.
- **Flexure force.** As built k = 2.92 N/mm: 0.44 N at the 0.15 preload and 1.32 N at full float. Resolved.
- **LED_MONIT with 150 Ω.** DESIGN-SPEC §2 says "lit about 1.8-2.2 V with 150 R", but the generated 150 Ω value was 1.71-2.11 V. The as-built 200 Ω value is 1.78-2.18 V, which §7 rounds to 1.8-2.2 V.
- **Glue.** The DFM review allowed a low-bloom CA (Loctite 460) or epoxy, and housing PROGRESS rev 0 said "CA/epoxy". These docs use 5-minute epoxy only, because CA fogs the PMMA rod.
- **Beam width** is 21° in optics-final R2.1 and 22° in its sweep table.
- **Stale sections.** DESIGN-SPEC §2, §4 and §5 still show 150 Ω, printed and heat-staked pins, a +Y cradle mouth, ST2.2 × 6 screws in Ø1.6 pilots and matte mask. pcb/PROGRESS.md still shows the 150 Ω string numbers above its rev A section, and housing PROGRESS still shows rev 0 slice weights and dowels. §7 / the rev A sections supersede them.
- **`bom.csv` J1 row** mixes the -004 MPN and LCSC code with the DigiKey number of the 4-pin part (push out position 4). That is deliberate, but read the Assembly column.
- Open: `J1` -004 stock, a real `J6` entry, the hot-plug pulse on a scope, spring relaxation over 7 days, and a cradle coupon print to check the rod snap and lip preload.
