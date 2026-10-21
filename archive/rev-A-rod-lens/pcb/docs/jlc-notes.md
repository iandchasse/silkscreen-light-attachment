# JLC order notes (rev A light PCBA)

These notes are for the builder placing the JLCPCB order for the light attachment board. The files come from
`tools/make_outputs.py`. Regenerate them rather than editing them by hand.

## Files to upload
- Gerbers: `production/silkscreen-light-attachment_rev-A_gerbers.zip`. It holds 8 Gerbers plus separate PTH and NPTH
  drill files.
- BOM: `production/jlc_bom.csv`. It has 4 lines and 14 parts, all JLC Extended:

  | LCSC | Part | Refs |
  |---|---|---|
  | C210340 | 3000 K LED | D1-D5 |
  | C210343 | 6000 K LED | D6-D10 |
  | C8663 | BAW56,215 | D11, D12 |
  | C5972814 | CRCW0805200RFKEAHP, 200 R | R1, R2 |

  C5972814 had 2,477 in stock on 2026-09-25.
- CPL: `production/jlc_cpl.csv`. It has 14 top-side placements, and the rotations are already corrected for JLC.

## PCB form
- 2 layers, FR-4, 1.6 mm, 1 oz. The board is 68.4 x 25.8 mm. Order 5 as single boards, with no panel.
- Surface finish: **ENIG preferred**, because flat pads help the LED seat height and tilt that the rod optics depend
  on. **LF-HASL is acceptable**, since the smallest copper gap is 0.43 mm.
- Solder mask: **black**. JLC offers no matte black, so gloss black is fine. Silkscreen: white.
- Set "Remove order number" (or pick a location) so JLC's number does not land on the board.
- Leave the outline tolerance at standard. Every NPTH keeps at least 0.50 mm of FR-4 to the edge (the gate checks
  this). Even at JLC's +-0.2 mm routing tolerance, at least 0.30 mm remains.
- **Inner corners:** the two concave corners where the board width steps (E x -3.50 / 63.50 at z 12.10) are drawn
  R0.35, which needs a 0.7 mm router. If JLC's standard bit leaves up to R0.5 there, accept it: that adds at most
  about 0.06 mm of FR-4 at the corner. Suggested remark: "Inner corners at the two width steps are R0.35; the standard
  router radius (up to R0.5) is acceptable." Do not pay for a special tool.

## PCBA form
- Economic PCBA, top side only, assemble all 5 boards. The board does not need edge rails, fiducials or tooling holes.
- Set "Confirm parts placement" to yes, then check the placement preview as described below before you pay.

## J1 is DNP at JLC
- J1 is not in `jlc_bom.csv` or `jlc_cpl.csv`. It is marked DNP in the schematic and on the board, and it stays in
  `production/bom.csv` with the note "hand-solder; not placed by JLC".
- If JLC asks about the three unplaced plated holes, answer: "J1 is DNP, fitted by the customer."
- Buy **TSW-102-14-G-D** (DigiKey **612-TSW-102-14-G-D-ND**). The -004 variant (LCSC C20382277) was out of stock on
  2026-09-25, and JLC will not modify parts.
- Push out **position 4**, the pin at J6-12 (P+_FUSE), with pliers. The board has no hole there.
- Hand-solder J1 with its posts plugged into a 2.54 mm 2x6 female header, used as a jig to keep the posts square.
  Then check it with the go-gauge.

## Placement preview checks
**LEDs (D1-D10), CPL rotation 180.**
- JLC's EasyEDA library footprints for C210340 (LED-SMD_L3.0-W1.4-RD) and C210343 (LED3014-RD) have their origin
  about **0.2 mm off the land-pattern centre**, toward the cathode pad.
- The CPL point is the **KiCad body centre**. That is the centre of the datasheet land pattern: 1.91 / 0.55 / 0.91
  mm, symmetric about +-1.685 mm.
- In JLC's preview, confirm that **each LED body is centred on its two lands**. Also confirm that the **cathode mark
  (the chamfered corner, or EasyEDA pad 1) sits on the LARGE pad** (1.91 x 0.92). The "+" marks the anode, which is
  the small pad.
- **Reject operator shifts.** If JLC's engineer proposes moving the LED coordinates by about 0.2 mm to line up their
  library outline, decline and keep the CPL point. A body shifted 0.2 mm toward the cathode leaves the anode electrode
  covering only about 62 % of its land, which raises the risk of tombstoning or skew.

**BAW56 (D11, D12), CPL rotation 270.**
- The CPL already includes the **+180 deg** EasyEDA offset (KiCad 90 + 180).
- In the preview, the single pin 3 (common anode) points toward R1/R2 and the LED row. Pins 1 and 2 face the J1 edge
  of the board.

**R1, R2 (0805, 200 R), CPL rotation 270.**
- These are non-polar, so no check is needed.

## Quick checklist
1. Upload the Gerber zip, then choose 1.6 mm, black mask, white silk and ENIG (or LF-HASL), and remove the order
   number.
2. Choose Economic PCBA, top side, and upload `jlc_bom.csv` and `jlc_cpl.csv`. You should see 14 parts and no J1.
3. In the preview, check that the LEDs are centred on their lands with the cathode on the large pad, and reject any
   0.2 mm shift. Check that each BAW56 has pin 3 toward the LED row.
4. Order J1 separately (612-TSW-102-14-G-D-ND), push out position 4, and hand-solder it in the jig.
