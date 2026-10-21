# Assembly (rev A)

Rev A is untested. These steps are the plan, not a record of a build. Where a step gives a number to check, the number comes from the design file named beside it.

Words used here:
- **LED side**: KiCad's top (F) side, with all the parts. In use it faces down, toward the case.
- **Text side**: the other side, with the white text and the three header tails. In use it faces up, into the cover.
- **Visor**: the front part of the housing that reaches out over the top of the screen.

Tools:
- multimeter, current-limited bench supply, calipers;
- a CR2032 coin cell with two short wires (or a coin-cell holder);
- fine tweezers and flat pliers;
- a soldering iron, and a **2.54 mm 2 × 6 female header** as a soldering jig (for example a spare of `J6`'s own part, Sullins PPPC062LJBN-RC);
- a go-gauge plate (§4) and a 1.1 mm drill in a pin vise;
- a 1.5 mm drill and a 2.4 mm drill (by hand), a fine saw or cutter for the rod, and a Phillips #0 screwdriver;
- 5-minute epoxy and a pin to apply it.

## 1. Coin-cell test of one loose LED

Do this before you order assembly, with a few loose LEDs bought from LCSC (C210340 warm, C210343 cool). It confirms on a real part that the footprint reads the datasheet's polarity correctly: large pad = chamfered cavity corner = cathode ([design/led-choice.md](../design/led-choice.md) §4; [pcb/PROGRESS.md](../pcb/PROGRESS.md), datasheet B-17-A-1548 p.2).

1. Look at the LED from the top. One corner of the yellow cavity is cut at 45°. That end is the cathode (−).
2. Turn it over. The pad under the chamfered end is the large one (pad 1, 1.91 × 0.92 mm, cathode).
3. Touch CR2032 **+ to the small pad** and **− to the large pad**. The LED should light, dimly.
4. Reverse the leads. It should stay dark. That is safe: the LED is rated for 5 V reverse and the cell gives about 3 V.

If it lights the other way round, stop. The footprint and the CPL assume large pad = cathode. Do not order assembly until this is resolved.

## 2. Inspect the assembled board

1. Ten LEDs in one row, in pairs. The silk letters **W** and **C** at the left end mark the order: warm, cool, warm, cool... Warm LEDs have a more orange phosphor.
2. Each LED has two short silk bars on its long sides at the cathode end. All ten must have their bars at the same end, and each LED body must sit centred on its two lands.
3. Two BAW56 (SOT-23) near the middle of the board. Each has its single pin (pin 3, common anode) toward its **200 Ω** resistor and the LED row, and its two pins toward the `J1` edge.
4. R1 and R2 must be **200 Ω** (CRCW0805200RFKEAHP). 150 Ω is the value before the review and must not be used. The bench test confirms the value: about 2.6 V across each resistor at 13 mA ([SAFETY-AND-TEST §2.2](SAFETY-AND-TEST.md#2-bench-test-of-the-bare-pcba)).
5. Coin-cell check of every fitted LED: touch **+** to the pad at the end **without** the silk bars and **−** to the end with the bars. Each LED lights on its own. Only that LED lights, because the rest of its string needs far more than 3 V.
6. Solder: no bridges between the LED pads inside a pair (they are only 0.43 mm apart).

## 3. Fit J1

`J1` is **not placed by JLC** (DNP) on every board. It is hand-soldered by the builder ([pcb/docs/jlc-notes.md](../pcb/docs/jlc-notes.md)).

**The part.** Buy **Samtec TSW-102-14-G-D** (DigiKey **612-TSW-102-14-G-D-ND**). It is a 2 × 2 header with a long gold post (.320", 8.13 mm), a short tail (.110", 2.79 mm) and a .100" body. The **TSW-102-14-G-D-004**, which already has position 4 left out, is also fine if you can get it from Samtec (LCSC C20382277 was out of stock on 2026-09-25). **Do not substitute any other header.** The post and tail lengths set how deep the posts go into `J6`.

**1. Push out position 4** (4-pin part only).
- Position 4 is the pin that would sit at `J6`-12, the raw battery. The board has no hole there.
- Hold the header against the LED side with its body over the three holes. The pin over the empty corner (diagonal to the hole labelled **5**) is position 4.
- Hold the body, grip that pin with flat pliers, and push it out of the body.
- Check that the other three pins did not move in the body (the length check in §4 confirms it).

**2. Set up the jig.**
- Plug the three long posts fully into three sockets of the 2 × 6 female header, in the same L shape.
- Stand the female header on the bench, so that the header body sits on top and the three short tails point up.
- The jig holds the posts square and at the right pitch while you solder.

**3. Place the board.**
- Lower the board **LED side down** over the tails. The tails pass through the three plated holes, and the body sits on the LED side.
- On the text side, the tails come out beside the silk labels **5**, **6** and **11**, and the empty corner has no hole.
- The board rests flat on the header body. The gap under the body must be under 0.1 mm.

**4. Solder** the three tails on the text side.
- Use a small fillet.
- **Keep solder off the tail tips, with no icicles.** The cover pushes on the tail tips, so a blob there changes how deep the posts go into `J6`.
- Keep solder and flux off the gold posts.
- Let the joints cool before you lift the board out of the jig.

## 4. Header QA: length and go-gauge

**Length.** Measure each of the three pins with calipers, from tail tip to post tip. Each must be **13.46 mm, +0.10 / −0.13** (13.33 to 13.56 mm). That is post 8.13 + body 2.54 + tail 2.79 ([design/spec-audit.md](../design/spec-audit.md) m9; [housing/out/REPORT.md](../housing/out/REPORT.md), stack: tail pad Y 121.40, post tips Y 107.94).
- A pin that is short or long has moved in the body, from the push-out or the soldering heat. Reject it, or reheat the joint and reseat the pin in the jig.
- Reject any solder icicle or blob on a tail tip. Clean it off with wick.
- Also check that the tails stand **1.19 mm** proud of the text side (2.79 mm tail − 1.60 mm board).

**Go-gauge.** This catches a bent post before it meets `J6`.
- Make a plate about 1.0 mm thick with three holes in an L at (0, 0), (2.54, 0) and (0, 2.54) mm. Any 3-hole L fits, because flipping the plate only rotates the L.
- **Hole size: Ø1.10 mm, drilled** (tips within ±0.10 mm on the post corners; [design/DESIGN-SPEC.md](../design/DESIGN-SPEC.md) §7).
- Slide the plate onto the post tips. All three posts must enter freely.
- If a post does not enter, straighten it gently with flat pliers and check again. If it does not straighten cleanly, replace the header.
- Run the gauge again after any forced, rotated or tilted attempt to fit the light.

> **Why Ø1.10 and not Ø0.84.** The posts are 0.64 mm square ([research/mechanical-j6.md](../research/mechanical-j6.md)), so they measure 0.905 mm across the corners. A round Ø0.84 hole cannot pass them: it only catches the tip chamfer. The Ø0.84 figure assumed a round 0.64 pin (0.84 − 0.64 = 2 × 0.10). A drilled **Ø1.10 mm** hole (0.905 + 2 × 0.10) gives the same ±0.10 mm on the corners, and it is what the contract now specifies. Print or cut the holes small and open them with a 1.1 mm drill in a pin vise, because printed holes come out undersized. A scrap of 2.54 mm-pitch perfboard with holes of at least 1.0 mm also works, and it is stricter.

## 5. Bench test

Test the bare board now, while the LEDs are still easy to see: [SAFETY-AND-TEST.md §2](SAFETY-AND-TEST.md#2-bench-test-of-the-bare-pcba). Do not continue with a board that fails it.

## 6. Carrier, rod, clip and cover

Use **5-minute epoxy only**. Do not use CA glue anywhere near the rod: CA fumes fog the acrylic (PMMA) rod and haze the LED lenses. Glue the carrier with the rod removed.

**Carrier and dowels**
1. Clean the carrier. Remove strings and any elephant foot from the channel and the two end cradles.
2. The carrier has a Ø1.55 × 2.4 mm slip hole in each end wall, on the flange side. The two **Ø1.5 × 4 mm steel dowels** (ISO 8734) go in here, set in 5-minute epoxy. They slide in; they are not a press fit. If a printed hole is tight, open it by hand with a 1.5 mm drill.
3. Put a small drop of epoxy in each dowel hole and insert the dowels. Then fit the carrier on the LED side of the board while the epoxy is still wet, so the dowels line up with the two Ø1.60 holes at the ends of the LED row.
   - The flanges lie flat on the board, and the LEDs sit in the channel between the two walls.
   - The tall wall (the optical lip, about 8.6 mm) runs along the board edge next to the LEDs, away from the header.
   - The dowels come through the board **flush with the text side** (4.0 mm pin = 2.4 mm in the carrier + 1.6 mm board). Nothing may stand above the text side: the cover roof is just above it.

**Glue the carrier to the board**
4. Hold the carrier against the board with two small spring clips or a rubber band around the ends, clear of the LEDs.
5. From the text side, apply a **thin bead, about 0.5 mm**, of epoxy with a pin at each of the four small Ø1.60 holes over the flanges (two on each side of the LED row). The glue wets the flange underneath. The 0.3 × 0.3 mm glue-dam grooves along the flange edges stop it from creeping into the channel.
6. **Cure with the channel facing down** (text side up). Let it cure fully.

**Rod**
7. Measure the rod with calipers: use it only if it is Ø3.90-4.10 mm (over 4.15 it will not seat in the bore; under about 3.9 the lips lose most of their 0.16 mm preload). Cut the clear PMMA rod, Ø4.0 mm, to **66.0 mm** with square ends. It must not be longer than 66.4 mm: each socket allows 0.2 mm of play per end. Deburr the ends; they need no polish.
8. Handle the rod by its ends. Clean it only with water and a soft cloth. Alcohol and solvents can craze acrylic.
9. **Snap the rod into the carrier from below.** The two end cradles open away from the board. Push the rod into each cradle until its lips click past the middle of the rod. The lips press the rod up onto the top of the bore, which puts its axis 2.00 mm below the LED faces ([housing/out/REPORT.md](../housing/out/REPORT.md), check 8).
10. Put **a dot of epoxy on each rod end**, where it meets its cradle. The lip preload will relax over time, so the epoxy is the long-term retention. Keep epoxy off the rest of the rod and out of the channel.

**Screws: prepare the holes**
11. **Pre-form each of the three pilot holes** in the clip (Ø1.8 mm, through holes) once, with a spare ST2.2 × 6.5 screw. Drive it in until the head touches, then back it out. This cuts the thread before the real assembly.
12. Try a screw through each of the three cover columns (bore Ø2.5 mm). **If it binds, run a 2.4 mm drill through that column by hand.** Printed holes come out undersized.

**Clip and cover**
13. Lay the clip on the bench with its board seat (the flat top) up.
14. Put the board on it, LED side down, with the SCREEN arrow on the text side pointing toward the clip's front lip. The posts pass down through the clip and stick out below. The carrier and rod hang in front of the clip. The board rests loosely: it is meant to float about ±0.3 mm.
15. Put the cover on. Its three columns go through the three Ø4.20 holes in the board, and its engraved SCREEN arrow points the same way as the board's.
16. Fit the three **ST2.2 × 6.5 mm** pan-head screws (PT / DIN 7981 class, thread-forming for plastics). **Tighten until the head just seats, then stop: snug, no torque.** They form their own thread in PETG and strip easily. The heads stand about 0.6 mm proud of their counterbores; that is normal. Never use a screw longer than 6.5 mm: its tip would reach the case, which the 6.5 mm screw clears by only 0.30 mm.
17. Check:
    - the board can still be nudged a little sideways;
    - with the board pushed up against the cover (as in use), the post tips stand **7.66 mm** below the clip's pads (115.60 − 107.94, [housing/out/REPORT.md](../housing/out/REPORT.md) stack). If it is more than 0.3 mm off, check the header length and the tail tips;
    - run the go-gauge over the post tips once more.

## 7. Fit it on the case (light off)

**7a. Clip alone (before you order anything).** Print only the clip and push it onto the top edge. It has no metal, so this is safe with the reader on. Check that:
- it goes on straight with light force;
- the three pads sit flat on the top face;
- the front lip touches the front face above the screen;
- the right ear touches the side;
- it does not rock or rattle.

**7b. The full attachment.**
1. Set the frontlight brightness to **0** (off) and wait about 10 s.
2. Hold the reader screen up in one hand, with the cover's SCREEN arrow pointing toward the screen side and the rod over the top of the screen.
3. Lower the light straight down onto the top edge. The fingers catch the case first, then the posts enter `J6`. Press on the middle of the cover until the pads sit on the top face. Expect about 9 N, a firm press.
4. If it stops hard before it seats, **stop**. A post is landing on the edge of a socket. Lift it, re-centre it and try again. Never push harder: that bends posts. Run the go-gauge after any forced attempt.
5. Check that it sits flat: lip on the front face, no gap under the pads, no rocking.

**Removing it:** brightness 0 first. Then **grip the two ribbed ends** of the cover and pull straight up (about 8 N). **Never pull by the visor**: it levers the posts sideways inside `J6`. The fingernail ledge along the back wall also gives a straight pull.

Storage: off the case, set the light down on its clip. The clip's fingers stand 4.7 mm beyond the post tips, so the posts carry no load.

## 8. First power-on

1. With the light fitted, switch the frontlight on at **60 % brightness or more**. The stock firmware may not enable the driver at lower settings ([FIRMWARE-NOTES.md §1](FIRMWARE-NOTES.md#1-enable-pulse)).
2. Set warmth to 0 % (cool only), then 100 % (warm only). Each string should light evenly along the row.
3. If nothing lights: switch off, wait 10 s, then switch on again at a higher brightness. If it still does not light, take it off (light off first) and repeat the bench test.
4. Look at the page. Expect a brighter band 10 to 20 mm below the top of the text area and a slightly dimmer top edge. The bottom of the page is about a third as bright as the band ([DESIGN.md §4](DESIGN.md#4-what-the-reader-sees)).
5. Then run the checks in [SAFETY-AND-TEST.md §4 and §8](SAFETY-AND-TEST.md#4-on-the-reader-led_sw-and-led_monit): the LED_SW / LED_MONIT reading, the pull-off force, 20 on/off cycles and the 7-day spring check.
