# Design rationale (rev B)

The short "why" behind rev B. The contract is [design/DESIGN-SPEC-revB.md](../design/DESIGN-SPEC-revB.md). Numbers come from [pcb/docs/design_summary.md](../pcb/docs/design_summary.md) and [housing/out/REPORT.md](../housing/out/REPORT.md). Status: designed and CAD-checked, **not built or tested**.

Coordinates are in the case frame, in mm: X along the top edge, Y up the device (the top face of the case is y 115.60), Z toward the reader (0 = the main board's rear face).

## Why the top edge

- The case (the consolidated 4.26" standard, strip-less build in silkscreen-enclosures/enclosures/case-426; its top is identical to rev K, checked 2026-09-30) is closed apart from its openings. The only one that reaches a light connector is the opening in the top wall above the main board's expansion header (`J6`) (x 42.582..58.922, z −5.415..0.215).
- `J6` carries the same frontlight nets as the frontlight connector (`J3`): LED_SW on pin 5, W− on pin 6, C− on pin 11. So the light runs on the stock driver (13.3 mA regulated, warm/cool picked by the firmware) with no board or firmware change.
- `J6` sits at the top edge of the main board, so the light sits above the top of the screen and shines down the page.

## Why these parts

The brief was: few standard parts, 1-3 printed parts, screws, push on; no glue, no optics parts, nothing modified; low, rounded, matching the case; functional enough.

- **LEDs:** Hongli 3014, warm 3000 K (C210340) and cool 6000 K (C210343). One family with both colours in stock at LCSC, 0.7 mm tall, 120° beam, Ra ≥ 80. **5 per colour**, like the stock panel frontlight: 5 fits under the voltage ceiling with a series resistor, and still stays dark when the driver is off with one LED shorted.
- **200 Ω per string** (Vishay CRCW0805200RFKEAHP, pulse-proof 0805): keeps the hot-plug pulse under the LEDs' 80 mA rating even on a TPS923611 main board. A worst pulse puts 1.18 W into it for about 1 ms, hence the pulse-proof part.
- **No diodes.** Rev A had a BAW56 per string for misinsertion. In rev B the cap keys the plug instead, and with 200 Ω the main board is safe in every misinsertion anyway. Two fewer parts.
- **Pins only where they are used:** a standard 1 × 2 header at `J6` pins 5/6 and a 1 × 1 at pin 11 (2.5 mm body, 6.0 mm post, 3.0 mm tail). No pin, pad or copper at any other `J6` position. 3 hand-soldered joints.
- **1.0 mm board** to keep the cap low. JLC assembles the 12 SMD parts on one side.

## How the cap locates and keys the plug

- **Stack:** base floor 1.0 mm on the case top (y 115.60..116.60), board on the floor (116.60..117.60), lid top at 120.5, i.e. 4.9 mm above the case.
- **Board:** two Ø4.40 bosses in the base pass through Ø4.80 holes in the board; the lid clamps it with 2 × M2 × 3 screws. The board floats about ±0.2 mm, so `J6` centres the pins, not the case.
- **Grip:** a 1.2 mm skirt down to y 107.0 all round (0.05 mm clearance), end caps that follow the case's R5 corners, a back jaw, and a front jaw above the window. Two 8 mm ridges on the back jaw press 0.10 mm into the back face: a light press fit, since the case has no undercut to snap into. At each front corner an X guide runs down to y 103.5, clear of the right-side key.
- **Order of engagement:** side-to-side play is ≤ 0.12 mm from 7.0 mm above seated. When the pin tips reach the `J6` face (5.05 / 4.72 mm above seated), the play is 0.052 mm in X and ≤ 0.052 mm in Z. The ridges touch at about 6.0 mm.
- **Keying:** the `J6` opening is off-centre on the case top, so a cap turned round puts the pins on solid plastic.
- **Pin depth in `J6`:** 4.72-5.05 mm nominal, 4.39-5.38 mm worst case (window 3.7-6.0).
- **Screws:** the Ø1.6 pilots are blind (0.2 mm of floor stays under them), so no screw can reach the case. Thread length 2.2 mm (5.5 pitches); the lid carries no load.
- **Look:** 6.5 mm in front of the case face, 1.25 mm wider than the case each side, front/back edges R1.8/R2.0 like the case, plan corners R6.25 around the case's R5.

## Electrical window

Per colour: LED_SW (`J6`-5) → 5 LEDs → 200 Ω → return (W− on `J6`-6, C− on `J6`-11).

| Item | Value |
|---|---|
| String current (set by the main board's current-set resistor R37) | 13.3 mA nominal, 13.96 mA max |
| 5 × V_f at 13.3 mA | 13.00 / 14.25 / 15.75 V (min / typ / max, 25 °C); 16.27 V max at −10 °C |
| 200 Ω drop | 2.66 V (2.79 V at 13.96 mA); 39 mW |
| LED_SW lit | 16.01 V min (hot), 17.26 V typ, **19.41 V worst** (cold, max bin) |
| Ceiling / over-voltage trip (TPS923610) | 22.0 V (margin 2.59 V) / 24.25 V min (margin 4.84 V) |
| Hold-off at ~14 µA, hot | 11.5 V, above the 6.5 V needed to stay dark while the driver is off |
| LED_MONIT | lit 1.71-2.08 V; nothing attached 2.60-2.73 V |
| Hot-plug peak (typ..min LED bin) | TPS923610 47.0-52.6 mA; TPS923611 71.3-76.8 mA; LED pulse rating 80 mA (for 0.1 ms, so an estimate) |
| LED_SW-to-ground misinsertion (bare board only), TPS923611 | about 83 mA until the over-voltage latch |

## Optics: functional enough

Bare 120° LEDs, emitter face at y 115.9, row at z 9.5, no lens. Nothing of the cap is in the light going to the page (0 points in the ray wedge; the base keeps 0.22 mm off the grazing ray; the visor is above z 11.3).

Page brightness relative to the page middle (tools/optics_sim.py):

| Panel | 2 mm down | 10 mm | 20 mm | 40 mm | bottom | top shadow band | light on the page |
|---|---|---|---|---|---|---|---|
| FT01C | 36.13 | 12.68 | 4.97 | 1.38 | 0.19 | 0.8 mm | 14.2 % |
| T01C | 33.87 | 12.41 | 4.94 | 1.38 | 0.19 | 1.9 mm | 13.7 % |
| PLAIN | 0.0 | 12.16 | 4.90 | 1.37 | 0.19 | 2.85 mm | 13.3 % |

- In plain words: bright at the top, fading down the page. 10 mm down gets about 12 × the light of the middle, 20 mm about 5 ×, 40 mm about 1.4 ×, and the bottom edge about 1/5. The top 0.8-2.9 mm sits in the case lip's shadow.
- Warm and cool mix evenly (≤ 2.6 % off 50/50) and the ends get about 80 % of the middle.
- Fine as a top-of-page reading light; the lower half is visibly dimmer. The model ignores the matte front film's scatter, which should make the far page look a little brighter.
- The rev C hood hides the LEDs completely from a reader: an emitter is visible only from an eye more than 227 mm below the page at 300 mm. It also keeps the top of the page in view for eyes up to about 181-189 mm above it at 300 mm (see housing/out/REPORT.md, view check). Its flat inner face, flared 20°, returns some of the forward-going light: about +12 % on the lower half and +14 % at mid-page with a white lid (the top 20 mm gets +24 %). A light-coloured lid is needed for this; a black lid absorbs it. A strip of mirror tape on that face would roughly double the lower-half light (design/visor-reflector-study.md), but rev C is printed-only by choice.
- Shaping the light further is a job for printed changes to the cap, not extra parts. Rev A's acrylic rod lens evened it out but was dropped for simplicity ([archive/rev-A-rod-lens](../archive/rev-A-rod-lens/docs/README.md)).

## Known limits

1. **Taller than asked:** the top is 4.9 mm above the case, not 3-4. The untrimmed pin tails (2.0 mm above the board) and the screw heads set it.
2. **Short screw thread:** 2.2 mm instead of ≥ 3 mm, so the blind pilots keep every screw off the case. Fine: the lid only clamps the board.
3. **Right X guide below y 107:** it stays at z ≥ 2.17 mm, clear of the right-side key (needs ≥ 2.0), and only touches the case if pushed sideways.
4. **Press fit, not a snap:** the 0.10 mm ridges need a try on a real print; their height is `BUMP['proud']` in `housing/src/params.py`.
5. **Thin screw-hole skins:** they print only with the slicer's "Detect thin wall" on (or Arachne). Without them the holes are open; 3 mm screws still stop 0.3 mm above the case top.
6. **Header pin size** 0.64 mm square is assumed; the part listing does not give it.
7. **No reverse-protection diodes:** never plug the bare board in.
8. **TPS923611 main boards:** small hot-plug margin; light off first, always.
9. **Not built or tested.**
