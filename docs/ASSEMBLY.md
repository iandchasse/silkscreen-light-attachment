# Assembly (rev B)

The rev B board and the rev B housing are built and work; the rev C housing (enclosing hood, rounder brow, rabbeted seam) is checked in CAD only and has not been printed (see the [README](../README.md)). If a step does not work as written, stop and note what happened.

You need: the assembled board, the two pin headers (1 × 2 and 1 × 1; `J1` and `J2` in the BOM), a spare 2.54 mm 2-row female header as a jig, the printed base and lid, 2 × M2 × 3 pan-head screws, a soldering iron and a small screwdriver. Parts list: [ORDERING](ORDERING.md).

## 0. Try the empty cap first

Before anything is soldered, push the empty base onto your reader. The base does all the gripping, and it has no metal, so this is safe with the reader on. It should go straight down, seat flat on the top of the case with a light press, and not rock. Take it off by its two ends.

## 1. Look over the board

- 10 LEDs on one side (the LED side), plus the two resistors near the three header holes. The other side is plain, with the white text.
- Inside each warm/cool LED pair the pads are only 0.43 mm apart. Check those gaps for solder bridges under a loupe.

## 2. Solder the headers

Skip this section if JLC fitted the headers; just check the bodies sit flat against the LED side.

1. Push the 1 × 2 and the 1 × 1 header into the three holes **from the LED side**, short tails first, so the plastic bodies sit flat against the LED side. The tails come out of the plain side next to the labels `5`, `6` and `11` (the square pad is `5`).
2. Press the long posts into the female header. It holds them square and parallel while you solder. Set it down with the board on top, plain side up.
3. Solder the 3 tails on the plain side. Check that the bodies are still flat and the posts straight, then pull the jig off.
4. **Do not trim the tails.** They stand 2.0 mm proud of the board, and the lid has a pocket for them.

Optional but recommended: the bench test in [SAFETY-AND-TEST §2](SAFETY-AND-TEST.md#2-bench-test-of-the-bare-board), while the LEDs are easy to see.

## 3. Put the cap together

1. Lay the board in the base, LED side down. It fits one way only: the header bodies drop into the window in the floor, the two bosses come up through the board's two holes, and the LED row lies along the front edge.
2. Put the lid on. Its hood goes in front of the LED row.
3. Drive the 2 screws through the lid into the bosses. They cut their own thread. Stop when they are snug and the heads sit flush with the lid top. Do not overtighten.

## 4. Fit it on the reader

1. **Turn the frontlight off** (brightness 0). If it was on with nothing attached, wait about 10 s.
2. Hold the cap with the hood toward the screen side and line it up over the top edge.
3. **Push it straight down** with a thumb on the middle of the top until it seats flat. The walls line up the pins before they reach the main board's expansion header, so it should not need any hunting.
4. If it stops hard before it seats, stop. Lift it off and try again. Never force it: a pin landing on the edge of a socket bends.

**Removing it:** frontlight off, then grip the **two ends** of the cap and pull straight up. Do not pull on the hood.

## 5. First light

- Set the brightness to **60 % or more** for the first test: the stock firmware may not start the driver at lower settings ([FIRMWARE-NOTES §1](FIRMWARE-NOTES.md#1-enable-pulse)).
- Warmth 100 % lights the warm LEDs only, 0 % the cool LEDs only.
- Nothing lights? Frontlight off, take the cap off, and check the three solder joints and the LEDs with the bench test.
