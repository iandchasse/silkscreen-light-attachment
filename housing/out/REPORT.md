# Housing rev C - check report (2026-10-20)

Rev C = rev B + an enclosing hood in front of the LED row (flat reflector face flared 20 deg, lip y 110.5, closed ends), a rounder print-friendly brow with R3.75 front corners, and a rabbeted lid/base seam. PCBA source: geometry.json rev B (2026-09-25). Lid top y 120.5 (4.9 above the case top). Overall: **PASS**.

| Check | Result | Key numbers |
|---|---|---|
| Seated vs stock case | pass | base (no bumps) 0.001 mm3, lid 0.0, PCBA 0; bumps 0.719 mm3, depth 0.1 |
| PCBA fit | pass | LED-base gap 0.3, LED-lid (hood) 1.0, PCB edge to the lid below its roof (hood, walls) 0.299 (design 0.3, passes at >= 0.29; the roof itself clamps at gap 0), pins-lid 0.3, bodies-base 0.235; float +-0.19 clean |
| Seam (rabbet) | pass | base top edge stepped in 0.8 (shoulder y 115.6); lid skirt wall 0.7, 0.1 lateral clearance, lower edge 0.15 above the shoulder, lid underside 0.1 over the floor top; min gap lid-base 0.1; no contact when the lid is shifted 0.095 in x/z or lowered 0.095 |
| View of the screen top | pass | active top y 107.9 seen past the hood from every eye y 20..160 at z 300 (FT01C/PLAIN pages); highest eye y that still sees it 189.1 / 181.3 |
| -Y insertion | pass | tips reach the J6 face at h [5.05, 4.72]: X play there 0.052 / 0.052 (target <= 0.12), Z 0.052 / 0.047; X play <= 0.12 from h 7.0 (<= 0.35 from h 8.0), Z <= 0.35 from h 7.5; bumps touch ~h 6.0; bodies enter the opening at h 1.5 |
| Screws | pass | M2 x 3 pan; blind dia 1.6 pilots, skin 0.2 (bottom y 115.8); k-max head flush (top y 120.5); tip y 115.9 = 0.1 above the pilot bottom, 0.3 above the case; thread 2.2 mm (5.5 pitches), 0.2 radial |
| Side keep-out | pass | X guides down to y 103.5; below y 107.0 the base is at z >= 2.17 (right, SW10 needs >= 2.0) |
| J6 engagement | pass | [4.72, 5.05] nominal, [4.39, 5.38] worst (limits [3.7, 6.0]) |
| Page-light keep-out | pass | points in the ray wedge (PLAIN/T01C/FT01C): base 0/0/0, lid 0/0/0; base z-margin to the grazing ray 0.218, lowest base point in front of the face y 112.6; hood lip y 110.5 (z >= 11.3, outside the wedge) |
| Printability | pass | base on its back face (back jaw on the bed), lid top-down (roof on the bed) |

## Insertion sweep (h = height above seated; play in mm, None = free > 1.2)

| h | collision mm3 | bumps mm3 | x+ | x- | z+ | z- |
|---|---|---|---|---|---|---|
| 10.0 | 0.0 | 0.0 | None | None | None | 0.619 |
| 9.0 | 0.0 | 0.0 | 0.787 | 0.787 | None | 0.211 |
| 8.5 | 0.0 | 0.0 | 0.516 | 0.516 | None | 0.127 |
| 8.0 | 0.0 | 0.0 | 0.319 | 0.319 | 0.628 | 0.084 |
| 7.5 | 0.0 | 0.0 | 0.188 | 0.188 | 0.267 | 0.061 |
| 7.0 | 0.0 | 0.0 | 0.112 | 0.112 | 0.094 | 0.052 |
| 6.5 | 0.0 | 0.0 | 0.08 | 0.08 | 0.047 | 0.052 |
| 6.0 | 0.0 | 0.099 | 0.066 | 0.066 | 0.047 | 0.052 |
| 5.5 | 0.0 | 0.631 | 0.056 | 0.056 | 0.047 | 0.052 |
| 5.05 | 0.0 | 0.719 | 0.052 | 0.052 | 0.047 | 0.052 |
| 4.72 | 0.0 | 0.719 | 0.052 | 0.052 | 0.047 | 0.047 |
| 4.0 | 0.0 | 0.719 | 0.047 | 0.047 | 0.047 | 0.047 |
| 3.0 | 0.0 | 0.719 | 0.047 | 0.047 | 0.047 | 0.047 |
| 2.0 | 0.0 | 0.719 | 0.047 | 0.047 | 0.047 | 0.047 |
| 1.5 | 0.0 | 0.719 | 0.047 | 0.047 | 0.047 | 0.047 |
| 1.0 | 0.0 | 0.719 | 0.047 | 0.047 | 0.047 | 0.047 |
| 0.5 | 0.0 | 0.719 | 0.047 | 0.047 | 0.047 | 0.047 |
| 0.0 | 0.001 | 0.719 | 0.0 | 0.0 | 0.0 | 0.0 |

## Bare-LED page light (tools/optics_sim.py)

optics_sim external, 120 deg (m=1), z 9.5, y 115.9, tilt 0, layout L5-w13.5-s1.9, case skin occluders

| page | vs mid @2 / 10 / 20 / 40 / far | top shadow band mm | flux on page |
|---|---|---|---|
| FT01C | 36.13 / 12.68 / 4.97 / 1.38 / 0.19 | 0.8 | 14.2% |
| T01C | 33.87 / 12.41 / 4.94 / 1.38 / 0.19 | 1.9 | 13.7% |
| PLAIN | 0.0 / 12.16 / 4.9 / 1.37 / 0.19 | 2.85 | 13.3% |

Real PCBA (pcb\production\3d\silkscreen-light-attachment_pcba_E.stl, 48 bodies, Sun Sep 27 12:16:24 2026): base_nb 0.0 mm3 / gap 0.085, lid 0.0 mm3 / gap 0.005, case 0.0 mm3 / gap 0.235 -> pass.

## OrcaSlicer (Elegoo CC2 0.4, 0.20 Standard, PETG, 3 walls, 30 %, supports OFF, detect thin walls ON)

- base: 20m 20s, 3.25 g, 82 layers, support 0, warnings 0
- lid: 15m 50s, 5.32 g, 50 layers, support 0, warnings 0
- base G-code, blind-pilot skins (y 115.6..115.8): PRINTED (x 10: 6/6 layers through the pilot have extrusion in the skin; x 38: 6/6 layers through the pilot have extrusion in the skin). The CC2 profile's classic wall generator drops these 0.2 skins unless 'Detect thin wall' is on (or use Arachne).

## Page light with the hood (tools/visor_reflector_sim.py via src/hood_light.py)

tools/visor_reflector_sim.py: 10 LEDs (Lambertian about -Y, z 9.5), flat diffuse reflector from (y 116.6, z 11.3) to the lip y 110.5, flared 20.0 deg, x -2.8..62.8; case window occluders as in the sim; middle 80 % of the page width

Relative to the bare-LED page light at mid-page (= 1.00). top = mean over 2..20 mm below the active top; lower half = mean over the lower half of the active area.

| page | case | top 2-20 mm | 10 mm | 20 mm | mid | lower half | top/lower |
|---|---|---|---|---|---|---|---|
| PLAIN | bare LEDs (rev B, no bounce) | 11.60 | 12.18 | 4.90 | 1.00 | 0.46 | 25.4 |
| PLAIN | rev B visor, white print | 11.88 | 12.41 | 4.96 | 1.01 | 0.46 | 25.9 |
| PLAIN | rev C hood, white print R0.80 | 14.66 | 14.87 | 5.76 | 1.13 | 0.51 | 28.6 |
| PLAIN | rev C hood, light grey R0.50 | 13.52 | 13.86 | 5.44 | 1.08 | 0.49 | 27.5 |
| PLAIN | rev C hood, black R0.05 | 11.80 | 12.35 | 4.95 | 1.01 | 0.46 | 25.6 |
| FT01C | bare LEDs (rev B, no bounce) | 14.13 | 12.71 | 4.97 | 1.00 | 0.46 | 31.0 |
| FT01C | rev B visor, white print | 14.41 | 12.92 | 5.03 | 1.01 | 0.46 | 31.5 |
| FT01C | rev C hood, white print R0.80 | 17.57 | 15.63 | 5.89 | 1.14 | 0.51 | 34.2 |
| FT01C | rev C hood, light grey R0.50 | 16.28 | 14.54 | 5.54 | 1.09 | 0.49 | 33.1 |
| FT01C | rev C hood, black R0.05 | 14.34 | 12.89 | 5.03 | 1.01 | 0.46 | 31.2 |

Rev C hood, white print (R 0.80, FT01C page): lower half 0.51 vs 0.46 today (+12 %), mid-page 1.14 vs 1.00 (+14 %), top band 17.57 vs 14.13 (+24 %). **The gain needs a light-coloured lid (white, light grey, silver silk); a black lid (R 0.05) absorbs it: lower half 0.46, +1 %.** The model is diffuse (printed surface), geometry only, no film scatter.

## What it is
- **2 printed parts + 2 screws.** BASE: a 1.0 floor lying on the case top with a window over the J6 opening, 2 bosses
  dia 4.40 through the PCB holes (dia 1.6 BLIND pilots: 0.2 of floor stays under them, bottom y 115.80), a 1.2 skirt
  down to y 107.0 all round with 0.05 clearance: end caps that follow the case's R5 corners and wrap its vertical
  front/back corners, a back jaw, and over the window a front jaw that is a 1.2 flat band (y 112.6..113.8) plus the R1.8
  round, its outer face 0.2 outside the grazing ray. At each front corner the skirt (flat side + corner wrap) runs on down
  to y 103.5 as an X guide: its rear edge rises at 45 deg back to the skirt (z 2.45 at y 107), so it prints without support
  and stays clear of the SW10 key; R1.0 fillet into the skirt, R1.5 round at the tip.
  Two 8 mm ridges on the back jaw press 0.10 into the back face (a light press fit; the case has no undercut to snap into).
  **Rev C: the floor's top outer edge is stepped in 0.8 (a rabbet, y 115.6..116.6, all round the sides, back and corner
  wraps; the central front tongue under the PCB is untouched).**
  LID: the cap. Roof on the PCB top (the clamp), pocket over the header tails, boss recesses, counterbores dia 4.6 (floor
  y 118.90: a k-max head sits flush with the top). **Rev C: the lid's wall comes down over the rabbet (0.7 thick,
  0.1 clearance all round, its lower edge 0.15 above the shoulder, outer faces flush with the base), so the joint is a
  hairline in a shadow step; the lid underside stays 0.10 above the floor top (the roof on the PCB top is still the datum).**
- **Hood (rev C).** The lid's front wall is an enclosing hood: a flat reflector face from the PCB underside (y 116.6, z 11.3)
  flared 20 deg away from the case down to the lip at y 110.5 (z 13.52), x -2.8..62.8 (the cavity limits, 0.3 beyond
  the PCB ends); the outer front is vertical at z 15.12 (9.1 in front of the case face), so the wall is 1.6 at the lip and
  thicker above; lip outer edge R0.8, inner edge sharp. End walls (flush with the cap sides) run from the roof to the lip
  beyond the PCB ends, so the LED row and the board edges are hidden from the front and the sides; the only opening is
  the downward slot between the hood and the case face, where the light leaves. The hood stays >= 0.3 from the PCB and
  1.0 from the LEDs. It sits at z >= 11.3, outside the page-light wedge.
- **Look:** top y 120.5 (4.9 above the case top), front 9.1 in front of the case face, 1.25 wider than the case per
  side; X-Y corners R6.25 concentric with the case's R5, back top edge R2.0, hood front corners R3.75 in plan. Brow
  (side view): vertical front -> R8 knee -> 45 deg bevel -> R2 into the roof, no flat slab. Plain, no text or ribs.
- **Build:** solder J1/J2 (3 joints), drop the PCBA on the base (bosses through the holes, LEDs to the front), put the lid
  on, 2 x **M2 x 3 pan head** screws (ISO 7045 cross or ISO 14583 Torx; a machine screw or a thread-forming screw for
  plastics, either cuts its own thread in the pilot), push the assembly straight down onto the case top.
- **Print:** PETG (PLA for a trial), no supports. Base on its back face (the back jaw's flat outer face on the bed); lid
  top-down (the visible top gets the bed finish; the brow is 45-deg limited, only the R2 / R6.25 / R2 bed rounds start
  tangent to the bed, so the first ~0.5-1.5 mm of those edges may droop a little). **Print the LID in a light colour
  (white, light grey, silver silk): the hood's inner face is a diffuse reflector and only a light colour returns the LED
  light to the page; a black lid absorbs it and the hood then only hides the LEDs.**
  **Slicer: turn on "Detect thin wall"** (OrcaSlicer process setting detect_thin_wall; or pick the Arachne wall
  generator). The 0.2 skins under the screw pilots are thinner than one line; the Elegoo CC2 profile's classic walls
  drop them and the pilots then open onto the case top. With thin walls on they print as one 0.23 line per layer.

## Screws
- A nominal 3 mm screw with a k-max head on the counterbore floor ends at y 115.90: 0.10 above the pilot bottom and
  0.30 above the case top. Thread engagement 2.2 mm (5.5 pitches of M2 x 0.4: 1.5 in the boss above the floor,
  0.7 in the floor), 0.2 radial thread depth into the dia 1.6 pilot. The lid only clamps the PCB; that is plenty.
- Screws up to 3.1 mm long seat fully. A longer one bottoms in the blind pilot and its head stands proud (a 4 mm
  screw by 0.9), so the builder sees it; its tip still has 0.2 of plastic under it and cannot touch the case top.
  The ISO length tolerance on 3 mm is +-0.2, so a rare over-length screw may sit up to 0.1 proud.

## X guidance
- The post tips reach the J6 face at h 5.05 (height above seated); X play there is 0.052 (target <= 0.12; it was 0.28
  with the plain skirt). X play is <= 0.12 from h 7.0 down (sampled every 0.5): the corner guides slide on the flat sides
  of the case before the skirt reaches the R5 corners.

## Deviations from the contract
1. **Top 4.9 above the case top, not 3-4.** The PCB top is already 2.0 up (floor 1.0 + board 1.0) and the untrimmed
   tails stand 2.0 proud of it (tip y 119.6); a closed pocket needs 0.3 clearance + a 0.6 skin. The screw heads need the
   same height (0.7 under-head layer + 1.6 head). Only trimming the tails or leaving the pocket open would lower it.
2. **Screw thread in the base 2.2 mm, not >= 3.** The base is floor 1.0 + boss 1.5 above it (boss top y 118.10) and
   the pilots are blind so no screw can reach the case top; 3 mm of thread would need the whole cap ~0.8 mm taller.
   2.2 mm of M2 in PETG holds roughly 100-200 N per screw; the lid carries no load.
3. **Screw type:** the contract named ST2.2 plastic screws in dia 1.8 pilots; now M2 x 3 pan head (ISO 7045 / 14583) in
   dia 1.6 blind pilots: a common kit part, and a too-long screw can no longer hit the case top and stop the cap seating.
4. **Right X guide below y 107.** The contract says nothing may touch the right side below y 107.0; the guide follows
   the mechanical-spec rule behind it (below y 107 only z >= 2.0; the SW10 slot is at z <= 0.6): it stays at z >= 2.17
   with 0.05 clearance, so it only touches the case side when the base is pushed sideways.
5. **Rev C, hood ends at x -2.8 / 62.8, not -2.6 / 62.6.** The closed ends use the cavity's own x limits (PCB
   outline + 0.3), which avoids a 0.2 ledge touching the PCB underside plane; they are still beyond the PCB ends.
6. **Rev C, hood outer face vertical (z 15.12), not parallel to the flared inner face.** The wall is 1.6 at the lip as asked and
   thicker above; this keeps the front corners a simple constant-radius plan round (R3.75) and the brow printable.
7. **Rev C, lid skirt 0.7 thick** (rabbet 0.8 minus 0.1 clearance): a declared thin wall, two perimeters, about 1 mm tall.

## Page light (bare 120 deg LEDs, tools/optics_sim.py, plain words)
- Nothing of the housing is in the light going to the page (0 points in the ray wedge; the base keeps 0.22 in z off the
  grazing ray; the hood is at z >= 11.3 and all page-bound light leaves the LEDs going -Y/-Z from z <= 10.06).
- The page is lit strongly from the top and falls off fast: 10 mm down it gets about 12x the light of the page middle,
  20 mm down about 5x, 40 mm down about 1.4x, and the bottom edge about 1/5 of the middle (the top-to-bottom ratio at
  10 mm is ~65:1). The top 0.8 mm (FT01C), 1.9 mm (T01C) or 2.9 mm (PLAIN) sits in the case lip's shadow. About 13-14 %
  of the LED light lands on the active area. Warm/cool mixing is even (<= 2.6 % off 50/50) and the ends get ~80 % of the
  middle. Verdict: functional enough as a top-of-page reading light; the lower half is visibly dimmer, as expected for bare
  LEDs without optics (the model ignores the matte front film's scatter, which makes the far page look a bit brighter).
- The hood hides the LED row and the board edge from the front and the sides: an emitter is only visible to an eye far below
  the device (y -227 at z 300), and the lip does not hide the top edge of the active area from any eye y 20..160.
- The hood's flared inner face is a diffuse bounce (see the table above): with a white lid it lifts the whole page a
  little (about +12 % in the lower half, +14 % mid-page, +24 % in the top band, FT01C page). **The gain needs
  a light-coloured lid (white, light grey, silver silk); a black lid absorbs the light and the gain is about +1 %.** A
  mirror strip on the face would do much more, but rev C is printed-only by design.


## Files

- print\base.step
- print\base.stl
- print\lid.step
- print\lid.stl
- print\plate.3mf
- E\base.stl
- E\lid.stl
- E\pcba_header_bodies.stl
- E\pcba_leds.stl
- E\pcba_pcb.stl
- E\pcba_pins.stl
- E\pcba_resistors.stl
- render\assembly_iso.png
- render\exploded_iso.png
- render\front.png
- render\hood_corner_iso.png
- render\hood_from_below.png
- render\section_boss_x10.png
- render\section_hood_end_x-4.png
- render\section_J6_x54.66.png
- render\section_led_row_x28.1.png
- render\section_led_x28.1.png
- render\side_right.png
