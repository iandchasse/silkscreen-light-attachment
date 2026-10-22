# Ordering (rev B)

Rev B is designed and CAD-checked but **not built or tested**. The order files come from `pcb/tools/make_outputs.py`; do not edit them by hand. Short generated version: [pcb/docs/jlc-notes.md](../pcb/docs/jlc-notes.md).

## 1. PCB (JLCPCB)

Upload `pcb/production/silkscreen-light-attachment_rev-B_gerbers.zip`, then set:

| Field | Value |
|---|---|
| Base material | FR-4 |
| Layers | 2 |
| Size | 65.0 × 17.0 mm (read from the Gerbers; corners R2, two 4.80 mm plain holes) |
| Quantity | 5, single boards (no panel) |
| PCB thickness | **1.0 mm** |
| Outer copper | 1 oz |
| Solder mask | any colour (black preferred) |
| Silkscreen | white |
| Surface finish | LF-HASL or ENIG |
| Order number | "Remove order number" |

## 2. Assembly (JLCPCB PCBA)

- Economic PCBA, **top side only**. JLC's "top" is the board's LED side. Nothing goes on the other side.
- Assemble as many of the 5 boards as you want.
- BOM: `pcb/production/jlc_bom.csv` (5 lines). CPL: `pcb/production/jlc_cpl.csv` (14 placements: 12 SMD + the 2 through-hole headers).

| Refs | Part | LCSC | Stock on 2026-09-25 |
|---|---|---|---|
| D1-D5 | Hongli HL-A-3014H421W-S1-08HL-HR3, warm 3000 K | C210340 | 102,969 |
| D6-D10 | same MPN, cool 6000 K | C210343 | 40,519 |
| R1, R2 | Vishay CRCW0805200RFKEAHP, 200 Ω pulse-proof 0805 | C5972814 | 2,477 |

All three are JLC Extended parts. The LED MPN is the same for every colour temperature, so order by the LCSC code.

**Placement preview: check this before you pay.**
- **LEDs D1-D10 (rotation 180):** each body sits centred on its two pads, with the **cathode mark on the large pad** (1.91 × 0.92 mm, toward +X). Decline any "library alignment" shift of about 0.2 mm that the engineer proposes.
- **R1, R2 (rotation 0):** not polarised, nothing to check.
- **J1, J2 (through-hole, rotation 0):** JLC hand-solders them when the order includes through-hole assembly. In the preview, J1's two pins sit in the holes labelled 5 and 6, and J2's pin in 11, bodies on the LED side, flush with the board. To solder them yourself instead, untick J1 and J2 on JLC's BOM page.

## 3. Headers (you solder these)

| Ref | Part | LCSC | Stock on 2026-09-25 |
|---|---|---|---|
| `J1` (for the expansion header's pins 5 and 6) | Hong Cheng HC-PZ254-11.5L-1x2PZ, 1 × 2 | [C27985187](https://www.lcsc.com/product-detail/pin-headers_hong-cheng-hc-pz254-11-5l-1x2pz_C27985187.html) | 24,852 |
| `J2` (for pin 11) | Hong Cheng HC-PZ254-11.5L-1x1PZ, 1 × 1 | [C27985186](https://www.lcsc.com/product-detail/pin-headers_hong-cheng-hc-pz254-11-5l-1x1pz_C27985186.html) | 10,775 |

- Any standard 2.54 mm straight male header with a **2.5 mm body, 6.0 mm post and 3.0 mm tail** works. DigiKey: Harwin M20-9990246 (DigiKey product 3728226), a 1 × 2 with a 6.1 mm post; cut one pin from a second one for the 1 × 1 (`J2`).
- Also get a spare 2.54 mm **2-row female header** (2 × 2 or longer). It is the soldering jig.
- Buy a few spares: they cost almost nothing.

## 4. Screws

2 × **M2 × 3 pan head**: ISO 7045 (cross) or ISO 14583 (Torx). A machine screw or a thread-forming screw for plastics both work; either cuts its own thread in the 1.6 mm printed hole. The head sits in a 4.6 mm counterbore.

**Do not use longer screws.** Up to 3.1 mm seats fully. A 4 mm screw bottoms in the blind hole and its head stands 0.9 mm proud. It still cannot reach the case: 0.2 mm of plastic stays under its tip.

## 5. Printing

- Files: `housing/out/print/base.stl` and `lid.stl` (already turned the right way up for printing), the same as `.step`, and `plate.3mf` with both on one plate.
- PETG, or PLA for a trial fit. **No supports.** Base on its back face, lid top-down (as exported). The base can be any colour. **Print the lid in a light colour (white, light grey, silver silk):** the hood's flared inner face is a diffuse reflector, and a light colour adds about 12 % light in the lower half of the page (+14 % mid, +24 % top); a black lid adds nothing.
- **Optional slicer setting: "Detect thin wall"** (OrcaSlicer) or the Arachne wall generator. It prints the 0.2 mm skin under each screw hole, which stops a too-long screw from reaching the case. Without it the holes are simply open, which is fine as long as you use 3 mm screws.
- Reference slice (Elegoo CC2, 0.4 mm nozzle, 0.20 mm Standard, PETG, 3 walls, 30 % infill): base 20 min 20 s, 3.25 g; lid 15 min 50 s, 5.32 g (rev C hood); no supports, no warnings.
- The lid prints roof-down, so its top gets the bed finish. The first ~1.5 mm of its edge rounds may droop a little.

## 6. Before you pay

- [ ] Thickness 1.0 mm, 2 layers.
- [ ] Assembly on the top (LED) side only: 14 placements, or 12 if you unticked the two headers (J1/J2).
- [ ] Every LED's cathode mark is on its large pad in the preview.
- [ ] Headers, the female-header jig and M2 × 3 screws ordered separately.
- [ ] Screws are 3 mm long (or the parts were printed with "Detect thin wall" on).
