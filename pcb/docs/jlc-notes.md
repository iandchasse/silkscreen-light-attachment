# JLC order notes (rev B light PCBA)

Files come from `tools/make_outputs.py`; do not edit them by hand.

## PCB
- Upload `production/silkscreen-light-attachment_rev-B_gerbers.zip`.
- 2 layers, FR-4, **1.0 mm**, 1 oz. Board 65.0 x 17.0 mm, corners R2, 2 x 4.80 mm NPTH. Qty 5, single boards.
- Any mask colour (black preferred), white silk, LF-HASL or ENIG. Set "Remove order number".

## Assembly (Economic PCBA, top side)
- BOM `production/jlc_bom.csv` (5 lines) and CPL `production/jlc_cpl.csv` (14 placements: 12 SMD + J1/J2 THT). All JLC Extended
  (checked 2026-09-25): LEDs C210340 warm x5 (stock 102969), C210343 cool x5 (40519); R1/R2 C5972814 x2 (2477).
- JLC's "top" is the board's LED side (F.Cu). Nothing on the other side.
- Preview checks:
  - **LEDs D1-D10, rotation 180:** each body centred on its two lands, cathode mark on the **large** pad (1.91 x
    0.92, toward +X). Decline any ~0.2 mm "library alignment" shift proposed by the engineer.
  - **R1, R2, rotation 0:** non-polar, no check.
- J1/J2 are through-hole: JLC hand-solders them if THT assembly is included (rotation 0; J1 pins in holes 5/6, J2 in
  11, bodies flush on the LED side). To solder them yourself, untick J1/J2 on JLC's BOM page.

## Headers (builder, 3 joints)
- J1 = Hong Cheng HC-PZ254-11.5L-1x2PZ (LCSC C27985187), J2 = HC-PZ254-11.5L-1x1PZ (LCSC C27985186). Any standard
  2.54 mm straight male header with a 2.5 body, 6.0 post and 3.0 tail works (DigiKey: Harwin M20-9990246, 6.1 post).
- Insert from the **LED side**, body flat on the board, solder on the plain side. Tails stay (2.0 mm proud; the lid
  has a pocket). Pads: J1 = J6-5 (square pad) and J6-6, J2 = J6-11.
- Do not plug the bare board into J6: only the housing keys it.
