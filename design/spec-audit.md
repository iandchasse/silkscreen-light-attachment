# Adversarial audit: mechanical + optics interface (pre-implementation)

J6 is the main board's expansion header; SW10 is its power button and SW7 its left-up page key (side keys near the top
of the case). J1 is the light's own pin header; C0/C1 are the rev A cover columns.

Status: DONE 2026-09-25. Audited design/mechanical-spec.md (all numbers) and the geometry of design/optics-final.md.
Frame: enclosure frame (X = KiCad X - 44.24, Y = 148.25 - KiCad Y, Z = 0 main-PCB rear, +Z toward the screen).
Evidence: enclosure source (A\enclosures\silkscreen-enclosure-claude\src params.py / body.py / tub.py / lid.py),
de-link_pcb\silkscreen_pcb.kicad_pcb (J6 pads + nets), the Samtec TSW print (tsw-xxx-xx-xxx-x-xx-xxx-mkt.pdf, text
extracted), samtec.com/products/tsw-102-14-g-d, LCSC C20382277 / C3332404 product pages (fetched 2026-09-25).
Recomputations: scratch python (stack, springs, clearances, Euler, keep-out, plate deflection).

Verdict: the header choice, the stack arithmetic, the case facts and the push-on-tails path hold up. One BLOCKER (the
LED part breaks the LCSC rule) and six MAJORs, mostly interface gaps that would bite at layout or build time: the
light-PCB mirror rule is missing; parts.md still names the wrong header; the header is out of stock at LCSC; J6's
lead-in is unverified; the centering leaves do not fit; and the rod carrier's +Z wall has nothing holding it.

## Findings

### BLOCKER
**B1. The LEDs violate the LCSC rule.** optics-final sec 2 and parts.md pick Lumileds L130-3090001400001 /
L130-5790001400001, both "LCSC none". The rule is that the LEDs MUST be easy to get on LCSC and JLC-assemblable.
- Fix: pick an LCSC-stocked warm + cool 3014 pair from ONE family, with good stock and JLC-assemblable. Record its
  package height h and cavity width.
- Set the emitter y = PCB underside (118.61) - h. Re-run `tools/rod_lens.py --pick` with that height and width,
  keeping the rod gap at 1.75 from the new emitter face.
- Keep the 3.0 x 1.4 footprint so the carrier and keep-out geometry carry over.
- Update parts.md and optics-final sec 2 (DigiKey is a bonus only).

### MAJOR
**M1. parts.md J1 still lists TSW-102-07-G-D-0xx** (.230 post, .430 OAL, JLC C3337759). The mechanical spec needs -14.
- Built from parts.md, the tips stop 2.29 higher: tip 110.23, E = 2.39..2.92. That is below the 3.68 minimum: no
  contact.
- parts.md sec 4 "Samtec tail 2.54, 0.94 proud" is also stale. The real figure is 2.79 and 1.19 proud.
- Fix: replace J1 with TSW-102-14-G-D-004 (LCSC C20382277) in the BOM row, sec 4 and the tail note.

**M2. The header is not in stock at LCSC.** C20382277 (TSW-102-14-G-D-004, USD 2.63 @1) and C3332404
(TSW-102-14-G-D) both read "Out of Stock" on 2026-09-25, so JLC cannot place them from stock.
- Fix: order the -004 through JLC global sourcing / pre-order, or consign parts bought from Samtec or DigiKey. As a
  fallback, mark J1 DNP at JLC and hand-solder it.
- Tell JLC: **no substitution**. A 4-pin TSW-102-14-G-D cannot enter the 3-hole footprint (a good poka-yoke), and a
  different lead style breaks the stack (M1).
- If the -D is used, press pin 4 out before soldering.

**M3. The light-PCB handedness is not specified (mirror risk onto J6-12 = battery P+_FUSE).** The interface table gives
enclosure (X, Z) only. Flipping a front-side footprint to B.Cu in KiCad mirrors it about its own axis. That moves the
empty corner and puts a pin at (57.202, -1.270) = J6-12 /P+_FUSE (J6 nets verified in silkscreen_pcb.kicad_pcb).
The claim "nothing metal can ever sit at J6 pin 12" holds only if the layout is right. Fix: add this to sec 5.
- Light PCB KiCad: x_k = X + a, y_k = Z + b (KiCad +y = +Z = toward the screen/LED row).
- F.Cu faces +Y (the roof); B.Cu faces the case. LEDs, BAW56, Rs and J1 go on B.Cu.
- F-view sanity check: the LED row is at the BOTTOM, J1 at the RIGHT, and J1's empty corner is its bottom-right.
- Add a scripted check before fab. Transform every PTH centre to the enclosure frame and require
  {(54.662,-3.810): LED_SW, (57.202,-3.810): W-, (54.662,-1.270): C-} within 0.05. Require no hole within 1.0 of
  (57.202,-1.270), and J1 pad nets to match.

Map, viewed from ABOVE (+Y, = KiCad F-view of the light PCB; right = +X, down = +Z):
```
                 X 54.662               X 57.202
  Z -3.810   Samtec pos 1 = J6-5  LED_SW    Samtec pos 3 = J6-6  W-          (row toward the case back)
  Z -1.270   Samtec pos 2 = J6-11 C-        Samtec pos 4 = J6-12 P+_FUSE:    (row toward the LEDs, +Z)
                                            OMITTED, NO HOLE
  (LED row at Z 16.00 lies further DOWN this view; J6 contacts 1-6 are the -3.81 row, 7-12 the -1.27 row)
```
Viewed from BELOW (B-view, "flip board"), X appears mirrored and the empty corner shows bottom-LEFT. Check pad
coordinates, not the picture.

**M4. J6's lead-in capture is unverified, and the worst-case budget exceeds it.**
- The 1.40 sq entry comes from a simplified vendor STEP (its socket depth is also simplified). Sullins does not
  publish the entry size.
- Budget: worst X 0.68 (centred) / 0.93 (uncentred) and Z 0.53 / 0.78, against a 0.38..0.5 capture. Only the RSS
  (0.39 / 0.32) fits.
- If the real entry is 1.0..1.1 sq, the capture is 0.18..0.23: frequent stubbing.
- Fix:
  - Measure a real PPPC062LJBN-RC entry (microscope or pin gauges) before freezing.
  - Tighten the go-gauge to Ø0.84 holes (tips within +-0.10), which cuts the sway term from 0.28 to 0.10.
  - Make centering mandatory. X worst then = 0.25 + 0.10 + 0.10 + 0.05 = 0.50, Z 0.35.
  - Bench-test mating with the fit coupon and a real TSW before the PCB order.

**M5. The centering leaves cannot be built as specified.** "0.8 x 3 x 8 mm leaves hang from the roof onto the PCB
edges", but roof underside (121.40) to clip top (118.40) is only 3.0.
- The back leaf (z -7.0..-6.2, x 20..23) would run 5 mm into the clip's back rail (z -8.05..-4.20, y 116.0..118.4).
- The left leaf (x -4.3..-3.5) runs into the clip's left end.
- A vertical leaf short enough to fit (about 2.5 long, 0.8 thick) is about 50 N/mm: 7 N at the 0.15 preload, which
  would clamp the float.
- The capture budget (M4) depends on these leaves.
- Fix: make each leaf a HORIZONTAL cantilever tongue cut into the cover wall:
  - 8 long along the edge, 0.8 thick, 1.5 tall, centred on y 119.4 (on the PCB edge both seated and resting);
  - a 0.5 slot behind it and a 0.15 bump at the tip;
  - k about 0.75 N/mm: 0.11 N at the preload, 0.34 N at full float.
  - The front one goes on the PCB front edge (see M6), not on the carrier.

**M6. The rod carrier's +Z wall has no stiff mount, the front leaf pushes on it, and the -Z wall is 0.4 thick.**
- **+Z wall mount.** The PCB front edge is <= 17.8 but the +Z wall's inner face is at 18.1. The wall (1.0 thick,
  8.61 tall, about 68 long) therefore hangs only from the carrier end walls.
  - As an end-supported plate, 1 N at mid-span deflects it 1.1 (fixed ends) to 4.6 (pinned ends).
  - The wall is only 0.1..0.2 from the rod (rod +Z surface z 17.90), and the aim moves about 16 deg per mm of dz.
- **Front leaf.** The spec's front centering leaf (x 28..31) pushes exactly there. It also contradicts "housing keeps
  >= 0.40 from the carrier everywhere".
- **-Z wall.** The "rod carrier zone z 13.4..17.7" leaves a 0.4 -Z wall (inner face 13.80). The case's own params note
  that a 0.4 wall is below what the slicer keeps as a line.
- Fix:
  - Extend the PCB front edge to z 19.3 under the +Z wall and fix the wall's top flange to the PCB underside along
    its length (the 2 datum pins + 1 mid pin or glue). The optics-final rule "front edge <= 17.8" is obsolete now that
    the lip floats with the PCB.
  - Make the -Z wall 1.2 thick (z 12.6..13.8; its bottom stays at the rod equator 114.16, far above y_ko(12.6) =
    111.33).
  - Carrier zone becomes z 12.2..19.3. The parts-height table then allows parts at z 8.0..12.2 only.
  - Move the cover skirt to z >= 20.2 (PCB edge 19.3 + 0.3 float + 0.6), or drop the skirt.
  - Put the front centering leaf on the PCB front edge.

### MINOR
**m1. Engagement-order table (3c) uses the seated tip.** Off the case the PCBA hangs 0.21 lower (tip 107.73).
- Pins cross the top-face plane at h 7.87 (not 7.65) and first touch J6 at h **5.42..4.89** (not 5.21..4.68).
- The pin-to-opening clearance is min **1.17** (front row post edge to the lintel edge z 0.215) and 1.40 (+X), not
  ">= 1.49".
- The corner fingers' Z guide starts at h 10.1 (x -1.10) to 7.6 (x -2.29), because the flat front face is inset by the
  R5/R1.8 corner (flat top 113.09 at x -1.10). The table says 10.8; the back-finger faces do give Z at 10.6.
- At h 7.87 the corner side parts already ride the R5 corner at x -4.083 (+-0.11).
- The conclusion holds: X/Z are guided >= 2.4 before J6. Fix: correct the table numbers.

**m2. Cover skirt vs the carrier +Z wall.** The gap is 0.4 nominal and 0.1 at full float. With the carrier pin play
(Ø1.50 in Ø1.60 = +-0.05) and +-0.1 print on each part, the worst case is -0.15, which contradicts the ">= 0.40
including float" rule. Fix: skirt inner face at z >= 19.85 (or >= 20.2 with M6).

**m3. The carrier datum holes leave a 0.30 FR4 web.** The holes are Ø1.60 at x -2.40 / 62.40, the edge is at
x -3.50 / 63.50, and the stake heads would overhang the edge. Fix: widen the PCB locally to x -4.2..64.2 over the carrier zone. The cover front-region end walls at
-4.9 / 64.9 then keep 0.7, or 0.4 at full float. Alternatively move the holes to x -1.8 / 61.8 (0.6 clear of the end LED bodies).

**m4. Screws and columns.**
- M2x6 leaves only **2.0 of thread** in the clip (tip 116.4, i.e. 1.0 d). It cannot be longer at C0/C1, because
  P1/P3 land on the case at 115.6.
- The 0.6 column walls (Ø3.4 / Ø2.2) print with an undersize bore and creep under the screw clamp. Every 0.1 of column
  loss adds 0.1 engagement (max margin 0.36).
- A pan head (k 1.3..1.6) in a 1.0 counterbore stands 0.3..0.6 proud.
- Fix:
  - Use a plastics thread-forming screw (ST2.2 / PT-style, 6 long) in a Ø1.6 pilot.
  - Print the columns and clip blocks at 100 % infill.
  - Columns Ø3.6 with a Ø2.3 bore in Ø4.2 PCB holes (float stays 0.30).
  - Assembly note: tighten to snug, no torque.
  - Accept the proud head, or use a wafer head.

**m5. Spring preload decays.** The back fingers carry about 10.8 MPa across layers at the nominal 0.30 (0.54 %).
PETG relaxes under that, and the low-tolerance corner is already only 0.4 N. Strains (0.99 % / 0.88 % at the maximum,
1.2..1.4 % at the R1.0 root with Kt) are acceptable for a static PETG spring. Fix: bench-check the coupon after 7 days
installed. If Z rattle appears, lengthen the fingers to L 12 (tip y 101.0) with a 0.45 interference: max strain
0.88 %, N 1.0..3.5 N.

**m6. The clip's left end block is not dimensioned, and one keep-out is short.**
- The left end block carries the left leaf root, the left corner-finger root and the cover's left wall seat. It is not
  dimensioned, and the underside keep-out table does not list it.
- The right end block's keep-out should run to z 5.0 (4.6 + 0.4), not 4.9.
- Fix: add a left end block (x -5.8..2.0, z -6.55..4.6, underside y >= 116.0, >= 0.4 off the R5 corner) and its
  keep-out row.

**m7. A 180-degree attempt is fully guided, then stands on the pins.**
- The case outline is centrosymmetric in X-Z. The rotated lip lands on the back face (z -6.7), the ear on the left
  side, and the back fingers over the window. The rotated pins (x 2.80 / 5.34, z 0.57 / 3.11) meet the top face at
  h 7.87.
- No earlier mechanical key is possible: any feature outside the case maps outside the case. The boss arrives only at
  h 1.4.
- The pins take the push: Euler (fixed-free) is 55.6 N each, about 167 N for three, reacted roof -> columns. No
  electrical contact is possible (claim confirmed).
- Fix: moulded orientation cue on the cover (arrow / "SCREEN" on the front), plus the go-gauge after any forced
  attempt.

**m8. Rod insertion and retention are undefined.** A one-piece carrier with two blind Ø4.1 sockets cannot take a
rigid 66 mm rod axially. Fix: C-cradle sockets that open toward +Y with a 200..220 deg wrap, rod snapped in before
staking. The bore, not the cradle floor, sets the gap to +-0.1.

**m9. Solder on the tail tips.** "<= 0.10" is not controllable at JLC (wave or hand soldering can leave 0.1..0.3).
At +0.25 the minimum engagement is still 3.88 > 3.68.
- Keep the push on the tails. It is the best chain:
  - each pin is loaded in pure axial compression, so there is no load on the solder joints or the body press-fit;
  - pushing on the PCB top would add PCB +-0.16, body seating 0..0.2 and body +-0.13.
- Fix: QA step. Measure tail tip to post tip on all 3 pins (13.46 +0.10 / -0.13) and reject icicles.

**m10. Small factual corrections.**
- Side flats are z -3.35..4.20 (V top / R1.8 tangent), not -3.30..4.30. The corner side part's z 4.2..4.3 lies on the
  wrap.
- The SW10 tub slot top is z 0.8 (TAB_Z 0.6 + TAB_SLOT_CLR 0.2), so the finger clears it by 1.2, not 1.4.
- The optics "brow floor y >= 111.5" is below the shifted envelope at z 13.8 (111.80). State >= 112.1. Nothing sits
  there anyway.
- The params.py comment "X0 -3.41" is stale; the value is -4.09.

## Verified OK
- **Header.** TSW -14 has a .320 [8.13] post, .110 [2.79] tail, .100 [2.54] body and .530 [13.46] OAL.
  - Source: the Samtec product title (.320 post, .530 OAL) and the LCSC C3332404 parameters (8.13 / 2.79 / 2.54).
  - The TSW print (text extracted) confirms: "-XXX indicates pos. to be omitted" (FIG 3); tow & sway 2 deg on all
    positions, post and tail; +-.005.
- **C20382277 is TSW-102-14-G-D-004** (LCSC page and datasheet file name).
- **Samtec numbering.** 1 / 2 run across the rows of the first column, so position 4 is diagonal to 1, which is J6-12
  (57.202, -1.270).
  - J6 nets from the KiCad file: 5 LED_SW, 6 W-, 11 C-, 12 /P+_FUSE; pads 1-6 at Y 100.28 (the -3.81 row), 7-12 at
    102.82 (the -1.27 row).
  - The 2x2 body is square, so the footprint's 3-hole L alone fixes the orientation, and it goes in in exactly one
    rotation.
- **Stack.** Tip 107.94 = 121.40 - 13.46. PCB underside 118.61, PCB top 120.21. Tails 1.19 proud (2.79 - 1.6 = 1.19,
  confirmed). Body bottom 116.07, 0.47 above the top face.
  - Engagement 4.68..5.21 nominal, 4.03..5.64 worst (margins 0.35 / 0.36).
- **The header body cannot rest on the case.** Body 5.08 x 5.08 at z -5.08..0 lies inside the opening (16.34 x 5.63,
  z -5.415..0.215), so it would bottom on J6 at 8.13 > 6.00.
- **Case facts, 12 spot-checked against the source**, all matching:
  - X0 / X1 = POCKET_X0 -1.41 - SIDE_WALL 2.68 = -4.09 / 64.09;
  - Y1 = 113.4 + 2.2 = 115.6;
  - Z_FRONT 6.0, Z_BACK -6.7;
  - CORNER_R 5, FRONT_EDGE_R 1.8, BACK_EDGE_R 2.0 (body.py fillets);
  - SEAM -3.75 with SEAM_CHAMFER 0.4, giving the V at z -4.15..-3.35;
  - J6 opening x 42.582..58.922, z -5.415 (lid) .. 0.215 (tub), from J6 bounds 42.882..58.622 / -5.165..-0.085
    +-0.3 / -0.25;
  - counterbore D4.2 at (40.2, 112.8), z -7.7..-4.9;
  - SW10 root 106.0, SW7 91.0;
  - window 108.5 at the lip and 109.1 at the face, x 0.96..59.04.
- **Springs, recomputed.** Back fingers 8.64 N/mm, 0.99 % at 0.55. Left leaf 3.41 N/mm, 0.88 % at 0.65.
  Retention about 8.1 N (4.2 + 3.1 + 0.8).
- **Keep-outs.**
  - The lip bottom 110.0 is 0.61 above the shifted y_ko(7.6) = 109.39 and 1.23 above y_ko(6.0) = 108.77.
  - Page-bound rays stay within x -0.15..60.15, so the corner fingers (x <= -1.10 / >= 61.10) and the cover end walls
    cannot shadow them.
  - The skirt sits behind the +Z wall.
  - The ear ends at y 107.0, above the SW10 root at 106.0.
  - The back fingers avoid the counterbore.
- **Printability.** Clip (bed = PCB seat) and cover (roof down) are prisms. The only overhangs are the 45-degree bump
  flanks and the Ø1.7 pilot ceilings (trivial bridges). The 1.2 springs and the 1.6 lip / fingers / ear are printable
  with a 0.4 nozzle.
- **Clearances.** Clip-to-PCB-underside keep-outs = clip + 0.4 (float 0.3 + 0.1), except m6.
  - Header body to the back-rail notch 0.62, to the boss 0.79, to the right end block 0.83 (>= 0.49 at float).
- **The corner fingers are rigid enough** to act as the X guide. L-section I about 20 mm^4 gives about 55 N/mm, so the
  1.4 N leaf preload moves them 0.03.
