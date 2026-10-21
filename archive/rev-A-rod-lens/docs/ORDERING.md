# Ordering (rev A)

Rev A has not been built. Order one small batch first, and bench-test one board before fitting it to a reader ([SAFETY-AND-TEST §2](SAFETY-AND-TEST.md#2-bench-test-of-the-bare-pcba)). The board-house details below follow [pcb/docs/jlc-notes.md](../pcb/docs/jlc-notes.md), which is generated with the fab files.

Files, all in `pcb/production/` (regenerate them with `pcb/tools/make_outputs.py`; do not edit them by hand):

| File | Use it for |
|---|---|
| `silkscreen-light-attachment_rev-A_gerbers.zip` | The PCB order. It holds 8 Gerbers plus separate PTH and NPTH drill files, nothing else |
| `jlc_bom.csv` | The PCBA "BOM file": 4 lines, 14 parts |
| `jlc_cpl.csv` | The PCBA "CPL / pick-and-place file": 14 top-side placements, rotations already corrected for JLC |
| `bom.csv` | The full BOM with manufacturer, MPN, DigiKey and LCSC columns, an Assembly column, and `J1` |

## 1. PCB (JLCPCB)

| Field | Value |
|---|---|
| Base material | FR-4 |
| Layers | **2** |
| Dimensions | 68.4 × 25.8 mm (JLC reads it from the zip) |
| PCB qty | 5 |
| Delivery format | Single PCB, no panel |
| PCB thickness | **1.6 mm**. The header stack assumes it |
| Solder mask | **Black**. JLC has no matte black, so gloss black is fine. The board's underside is the ceiling of the LED channel, and the optics assume black |
| Silkscreen | **White** |
| Surface finish | **ENIG preferred**: flat pads keep the LED seat height and tilt that the rod optics depend on. **LF-HASL is acceptable**: the smallest copper gap is 0.43 mm. The job file says ENIG |
| Outer copper weight | 1 oz |
| Remove order number | **Yes** (or pick a location). JLC's number must not land on the board |
| Outline tolerance | Standard. Every unplated hole keeps at least 0.50 mm of FR-4 to the edge, so at least 0.30 mm remains at JLC's ±0.2 mm routing tolerance |
| Gold fingers, castellated holes, edge plating | No |
| Everything else | JLC defaults |

**Remark for the order** (the two inner corners where the board width steps are drawn R0.35): "Inner corners at the two width steps are R0.35; the standard router radius (up to R0.5) is acceptable." That adds at most about 0.06 mm of FR-4 at each corner. Do not pay for a special tool.

Check the Gerber viewer before paying:
- 3 plated holes of 1.02 mm in an L near one end, and **no hole in the fourth corner** of that square;
- 9 unplated holes: 3 × 4.20 mm and 6 × 1.60 mm;
- white text on KiCad's bottom (B) side, which faces up in use: "SILKSCREEN LIGHT ATTACHMENT", "rev A 2026-09-25", a SCREEN arrow, and 5 / 6 / 11 beside the header holes.

## 2. PCBA (JLCPCB)

| Field | Value |
|---|---|
| PCBA type | **Economic** |
| Assembly side | **Top side** only. All SMD parts are on KiCad's top (F) side, which faces the case in use |
| PCBA qty | All 5 (or at least 2 for a first test) |
| Edge rails, fiducials, tooling holes | Not needed by this board. If JLC proposes drilling tooling holes inside the board outline, decline: there is no free area |
| Confirm parts placement | **Yes**. Check the preview as described below before you pay |
| BOM / CPL | `jlc_bom.csv` / `jlc_cpl.csv`. You should see **14 parts and no `J1`** |

Parts (from `jlc_bom.csv`). All four lines are JLC Extended parts, so expect an Extended-part fee per line.

| LCSC | Part | Refs | Notes |
|---|---|---|---|
| **C210340** | HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3, **3000 K** | D1-D5 | warm. 102,969 in stock on 2026-09-25 |
| **C210343** | same MPN, **6000 K** | D6-D10 | cool. The MPN is the same for every colour temperature; the LCSC code picks the colour. 40,519 in stock on 2026-09-25 |
| **C8663** | Nexperia BAW56,215, SOT-23 | D11, D12 | pin 3 is the common anode. 43,296 in stock on 2026-09-25 |
| **C5972814** | Vishay CRCW0805200RFKEAHP, **200 Ω** 1 % 0.5 W pulse-proof, 0805 | R1, R2 | 2,477 in stock on 2026-09-25 |

**`J1` is not in these files.** It is marked DNP in the schematic and on the board, and it stays in `bom.csv` as "DNP at JLC - hand-solder; not placed by JLC". If JLC asks about the three unplaced plated holes, answer: "J1 is DNP, fitted by the customer." See §3.

**Placement preview checks** (from [pcb/docs/jlc-notes.md](../pcb/docs/jlc-notes.md)):
- **LEDs D1-D10, rotation 180.**
  - JLC's library footprints for C210340 and C210343 have their origin about **0.2 mm off the land-pattern centre**, toward the cathode pad. The CPL point is the KiCad body centre, which is the centre of the datasheet land pattern.
  - Confirm that **each LED body sits centred on its two lands**.
  - Confirm that the **cathode mark** (the chamfered corner, or EasyEDA pad 1) sits on the **LARGE pad** (1.91 × 0.92 mm). The "+" marks the anode, the small pad.
  - **Reject operator shifts.** If JLC's engineer proposes moving the LEDs by about 0.2 mm to line up with their library outline, decline and keep the CPL point. A body shifted 0.2 mm toward the cathode leaves the anode electrode covering only about 62 % of its land, which raises the risk of tombstoning or skew.
- **BAW56 D11, D12, rotation 270.** The CPL already includes the +180° EasyEDA offset. Pin 3 (the single pin) points toward R1/R2 and the LED row; pins 1 and 2 face the `J1` edge.
- **R1, R2, rotation 270.** Non-polar; no check needed.

If anything looks mirrored or rotated, stop and ask JLC to correct it before production.

## 3. The header, J1: buy it separately

`J1` is hand-soldered by the builder on every board ([ASSEMBLY §3](ASSEMBLY.md#3-fit-j1)). JLC cannot fit it: the exact part (LCSC C20382277, TSW-102-14-G-D-004) was out of stock on 2026-09-25, and JLC will not modify a stocked part.

| Buy | Where | Then |
|---|---|---|
| **Samtec TSW-102-14-G-D** (2 × 2, all 4 pins) | DigiKey **612-TSW-102-14-G-D-ND** | push out **position 4** (the pin at `J6`-12, P+_FUSE) with pliers before soldering |
| or Samtec **TSW-102-14-G-D-004** (position 4 already omitted) | Samtec direct (or LCSC C20382277 when back in stock) | solder as is |

Check DigiKey or Samtec stock for the header **before** ordering the PCBA: there is no substitute.

- The part: 0.100" pitch, gold, post .320" (8.13 mm), tail .110" (2.79 mm), .100" body. **No substitution.** The post length sets how far the header goes into `J6`, and the tail length sets how it seats against the cover. A standard header (for example TSW-102-07, post .230") would not reach far enough.
- A 4-pin header will not go into the 3-hole footprint until position 4 is out. That is deliberate: there is no hole at `J6`-12.
- Also buy a **2.54 mm 2 × 6 female header** to use as the soldering jig (for example a spare Sullins PPPC062LJBN-RC, `J6`'s own part, which is also handy for measuring the `J6` entry: [SAFETY-AND-TEST §7](SAFETY-AND-TEST.md#7-measure-the-j6-entry)).

## 4. DigiKey and alternatives (for your own stock or a hand build)

| Ref | DigiKey | Alternative |
|---|---|---|
| D1-D10 | n/a (LCSC only) | None. Keep the Hongli pair from LCSC so both strings match |
| R1, R2 | 541-CRCW0805200RFKEAHPCT-ND (cut tape; checked on DigiKey's search page for the MPN, 2026-09-25) | Another **200 Ω 1 % pulse-proof / anti-surge 0805** (for example Panasonic's ERJ-P06 series; not checked in this project). Never a plain 0805: each hot-plug puts a pulse through it. **Do not go below 200 Ω**: with 150 Ω a TPS923611 main board reaches 78-96 mA, over the LED's 80 mA pulse rating |
| D11, D12 | 1727-2916-1-ND | onsemi BAW56LT1G (LCSC C82478, [design/led-choice.md](../design/led-choice.md)), or any BAW56 in SOT-23 with the same pinout (pins 1 and 2 cathodes, pin 3 common anode). The SOT-323 BAW56W does **not** fit the footprint |
| J1 | 612-TSW-102-14-G-D-ND (push out position 4) | None. No substitution |

## 5. Mechanical parts

| Item | Qty | Spec | Where |
|---|---|---|---|
| Rod | 1 | Clear PMMA (acrylic), **Ø4.0 mm**, cast or extruded. Cut to **66.0 mm** with square ends. Not longer than 66.4 mm: the sockets allow 0.2 mm of play per end. **Measure it: use Ø3.90-4.10.** Over 4.15 it will not seat in the bore; under about 3.9 the lips lose most of their 0.16 mm preload | Plastics stockists, for example a 4 mm × 1000 mm extruded rod (<https://www.clearplastictube.co.uk/clear-acrylic-round-rod-extruded-4mm-1000mm>), 4 mm acrylic rod packs on Amazon (<https://www.amazon.ca/Round-Acrylic-Extruded-Length-Diameter/dp/B0GFNLKFPV>), or US stockists such as TAP Plastics, U.S. Plastic Corp. or Acme Plastics (check that they list 4 mm, not only inch sizes). No DigiKey source |
| Dowel pins | 2 | Steel parallel pins, **Ø1.5 × 4 mm, ISO 8734** (hardened). Set in 5-minute epoxy in the carrier | Misumi, McMaster-Carr, Accu, or a small-pin assortment |
| Screws | 3 | **ST2.2 × 6.5 mm pan head, plastics thread-forming (PT / DIN 7981 class)**. The model uses a Ø4.0 × 1.6 head. **Nothing longer**: the tip clears the case by only 0.30 mm | Hardware suppliers, or AliExpress / Amazon "2.2 × 6.5 self-tapping pan head" |
| Glue | a few drops | **5-minute epoxy.** Not CA: CA fumes fog the PMMA rod and haze the LED lenses | any |
| Filament | about 14 g | **Black PETG.** The carrier must be black (matte if you have it): it is part of the optics | any |
| Soldering jig | 1 | 2.54 mm 2 × 6 female header | see §3 |
| Optional | 1 | M2 × 12 screw and the back screw-lock tab | Only if friction retention proves too weak. The tab is described in `design/mechanical-spec.md` §3d but not modelled in rev A |

The optics were optimised for a 4.0 mm rod. Do not use a 3/16" (4.76 mm) or 1/8" (3.175 mm) rod: the carrier's cradle will not hold it, and the beam changes.

## 6. Printing

Print files: `housing/out/print/{clip,cover,carrier}.stl` (or `.step`), already in print orientation with the bed at Z 0, or the plate `housing/out/print/housing-plate.3mf` with all three.

| Setting | Value |
|---|---|
| Material | PETG, black |
| Nozzle / layer | 0.4 mm / 0.20 mm |
| Walls | 3 |
| Infill | 30 % (the columns and pads are thin enough to print solid) |
| Supports | **Off**. None are needed |
| Elephant-foot compensation | On. The model leaves the 0.2 mm bed-edge chamfers to the slicer |
| Orientation | Clip: its top face (the board seat) on the bed. Cover: roof top on the bed. Carrier: flanges (the board face) on the bed. Do not rotate them |

Reference slice ([housing/out/slice/slice-report.json](../housing/out/slice/slice-report.json)): OrcaSlicer, Elegoo Centauri Carbon 2, 0.4 nozzle, "0.20mm Standard" and the Elegoo PETG preset, 3 walls, 30 %, supports off. No warnings.

| Part | Time | Filament | Layers |
|---|---|---|---|
| Clip | 21 min 3 s | 3.95 g | 77 |
| Cover | 24 min 24 s | 7.98 g | 67 |
| Carrier | 10 min 22 s | 1.97 g | 43 |
| **Total** | **55 min 49 s** | **13.90 g** | |

Re-slice for your own printer. Print the clip first and try it on the case before printing the rest (README step 1).

## 7. Before you pay: checklist

- [ ] Gerber preview: the 3-hole L with an empty fourth corner; 9 unplated holes; 2 layers, 1.6 mm, black mask, white silk; ENIG (or LF-HASL); order number removed; the inner-corner remark added.
- [ ] PCBA: Economic, top side, 14 parts, no `J1`. D1-D5 = C210340 (3000 K), D6-D10 = C210343 (6000 K), not swapped. R1/R2 = C5972814 (200 Ω).
- [ ] Placement preview: every LED centred on its lands with the cathode mark on the LARGE pad; no 0.2 mm operator shift; BAW56 pin 3 toward the LED row.
- [ ] `J1` ordered separately: 612-TSW-102-14-G-D-ND (push out position 4) or the -004 from Samtec, plus a 2 × 6 female header for the jig.
- [ ] Rod Ø4.0 × 66.0; 2 dowels Ø1.5 × 4 ISO 8734; 3 screws ST2.2 × 6.5 PT; 5-minute epoxy; black PETG.
