# Safety and test (rev A)

Rev A has not been built, powered or fitted to a reader. This page is the test plan for the first build. Every limit below comes from a generated report or a design note, named beside it. A few values are worked out here from those reports; they are marked **derived**.

## 1. The rules

1. **Light off before you plug it in or pull it off.** Set the frontlight brightness to 0, then wait about 10 s ([§5](#5-hot-plug-why-the-light-off-rule)).
2. **Never plug the bare board into `J6`.** Only the clip and cover fix its position. Without them, the posts can land on the wrong pins ([§6](#6-misinsertion-what-happens-if-it-goes-on-wrong)).
3. **Remove it by the two ribbed ends, never by the visor.** The visor is the part that reaches out over the screen. Pulling it levers the posts sideways inside `J6` ([§3](#3-fitting-on-the-case)).
4. **Bench-test every new board** before it goes near a reader ([§2](#2-bench-test-of-the-bare-pcba)).
5. **Run the go-gauge** after soldering `J1` and after any forced or wrong-way fitting attempt ([ASSEMBLY §4](ASSEMBLY.md#4-header-qa-length-and-go-gauge)).
6. **TPS923611 main boards** have less margin. Treat rule 1 as mandatory on them ([§9](#9-tps923611-main-boards)).

The whole board is SELV. The highest voltage it can ever see is the driver's over-voltage limit: 25.5 V on a TPS923610 board, 31.4 V on a TPS923611 board ([research/electrical-j6.md](../research/electrical-j6.md), key numbers).

## 2. Bench test of the bare PCBA

Do this with `J1` soldered and before the carrier goes on, so every LED is easy to see.

**2.0 Before you order: polarity of one loose LED.** Do the coin-cell test in [ASSEMBLY §1](ASSEMBLY.md#1-coin-cell-test-of-one-loose-led) on a loose C210340 or C210343 first. It confirms that the large pad is the cathode, which the footprint and the CPL assume.

**2.1 Meter checks, no power.** The three header posts are `5` (LED_SW, anode), `6` (W−, warm return) and `11` (C−, cool return). The labels are on the text side beside the tails.

| Meter mode | Probe pair (both polarities) | Expect | A reading means |
|---|---|---|---|
| Resistance | 5-6, 5-11, 6-11 | open (OL) | a solder bridge or a damaged part. Do not power it |
| Diode test | 5-6, 5-11, 6-11 | open (OL) | the same. A meter's 2-3 V cannot light a 5-LED string, and the reverse directions are blocked by the BAW56 |
| Diode test, on each BAW56 | red on the single pin (pin 3, toward the resistor), black on each of the two pins toward the `J1` edge | about 0.6-0.7 V each; OL when reversed (**derived**: a normal silicon junction) | a missing, reversed or wrongly rotated diode |

Also look at the ten LEDs under a loupe. Inside each warm/cool pair the pads are only 0.43 mm apart, so check for bridges there.

**2.2 Light each string from a current-limited supply.** Set the supply to **13 mA** and about **22 V** (22.0 V is the design ceiling). Connect the leads with the output switched off, then switch it on. That way the supply's own output capacitor does not dump into the string.

| Test | + lead | − lead | Expect |
|---|---|---|---|
| Warm string | 5 | 6 | D1-D5 light (warm, slightly orange); D6-D10 stay dark |
| Cool string | 5 | 11 | D6-D10 light (cool, bluish); D1-D5 stay dark |

Readings in constant-current mode at 13 mA and room temperature:
- **Across the string terminals (5 to 6, or 5 to 11): about 16.4 to 19.3 V, typically about 17.7 V.** This is **derived**: 5 × V_f at 13.3 mA is 13.00 / 14.25 / 15.75 V (min / typ / max), plus 2.66 V across 200 Ω, plus about 0.75-0.86 V for the BAW56 ([pcb/docs/design_summary.md](../pcb/docs/design_summary.md)). If the supply sits at its 22 V limit and the LEDs stay dark, the string is open: look for a reversed or unsoldered LED.
- **Across R1 (warm) or R2 (cool): about 2.6 V.** That is 200 Ω × 13 mA. About 2.0 V would mean a 150 Ω part was fitted (the value before the review).
- Every LED in the string glows about the same. One dark LED while the rest are lit means that LED is shorted.

No adjustable supply? A fixed 24 V supply through a 510 Ω resistor gives about 9 to 15 mA (**derived**: (24 − 19.3) / 510 to (24 − 16.4) / 510). Connect the resistor and the board first, and switch the supply on last.

**2.3 Reverse and cross checks.** Keep the 13 mA limit and use up to 10 V.

| + lead | − lead | Expect |
|---|---|---|
| 6 | 5 | Nothing lights, and the current reads 0 (microamps at most). The warm BAW56 blocks it |
| 11 | 5 | The same, for the cool string |
| 6 | 11, then 11 to 6 | Nothing lights, 0 current. The two block diodes stop any warm-to-cool path |

A board that fails any of 2.1 to 2.3 does not go on the reader.

## 3. Fitting on the case

- **Clip alone first.** Print only the clip and try it on the case before anything else. It has no metal, so this is safe with the reader on. It should seat flat on its three pads with light force and not rock ([ASSEMBLY §7a](ASSEMBLY.md#7-fit-it-on-the-case-light-off)).
- **The full attachment, light off.** Set brightness to 0 and wait about 10 s.
  - Hold the reader in one hand. Line up the cover's SCREEN arrow with the screen side.
  - Lower the light straight down and press on the middle of the cover. Expect a firm press of about 9 N (8.8 N computed, [housing/out/REPORT.md](../housing/out/REPORT.md) springs).
  - The clip's fingers take hold before the posts reach `J6`: front-to-back from 10.27 mm above seated and sideways from 7.31 mm. The posts meet `J6` at 5.42 to 4.89 mm (REPORT, engagement order).
- **If it stops hard before it seats, stop.** A post is landing on the edge of a socket. Lift it, re-centre it, and try again. Never push harder: each post buckles at about 56 N ([design/mechanical-spec.md](../design/mechanical-spec.md) §3d).
- **Removing it.** Light off. Grip the two ribbed ends of the cover and pull straight up (about 8 N). Do not pull on the visor. Lifting its front edge by 1 mm tilts the housing about 2° and sweeps the post tips about 0.27 mm sideways inside `J6` ([design/review-mechanical.md](../design/review-mechanical.md) MAJOR-4).

## 4. On the reader: LED_SW and LED_MONIT

With the light seated and switched on, the main board's driver output (LED_SW) and its sense line (LED_MONIT) should read as below ([pcb/docs/design_summary.md](../pcb/docs/design_summary.md)).

| Quantity | Lit, this light (N = 5, 200 Ω) | Nothing attached (open) |
|---|---|---|
| LED_SW (driver output) | 16.61 V min (hot), 17.98 V typ, 20.36 V worst (cold, highest LED bin) | 24.25-25.5 V (TPS923610 over-voltage limit) |
| LED_MONIT (LED_SW × 0.1071) | **1.78-2.18 V** | **2.60-2.73 V** (TPS923611: 3.17-3.36 V) |

- LED_MONIT is on the main board: ESP32 IO2, through a 1 MΩ / 120 kΩ divider (R39 / R41). You can read it only with the main board exposed (a meter from IO2 or R41 to ground) or through a firmware readout ([FIRMWARE-NOTES.md §2](FIRMWARE-NOTES.md#2-led_monit-load-check)).
- A lit reading above about 2.40 V means the driver is climbing toward its limit: the light is not connected or not seated. Switch the frontlight off.
- Each string lights on its own: warmth 0 % is cool only, and 100 % is warm only. In between, the firmware switches between the two strings at 10 kHz.
- The stock firmware may not turn the driver on below about 58 % brightness ([FIRMWARE-NOTES.md §1](FIRMWARE-NOTES.md#1-enable-pulse)). Use 60 % or more for the first test.

## 5. Hot-plug: why the light-off rule

If the frontlight is on (brightness above 0) with nothing plugged in, the driver goes to its over-voltage limit and latches off. Its output capacitor C9 is left charged:
- to 24.25-25.5 V on a TPS923610 board, or up to 31.4 V on a TPS923611 board;
- it drains only through the 1.12 MΩ sense divider, which takes about 4 to 8 s to bring it down to 6 V ([research/electrical-j6.md](../research/electrical-j6.md) §4).

Plugging the light in during that time dumps C9 through one LED string. The 200 Ω resistor limits the peak ([pcb/docs/design_summary.md](../pcb/docs/design_summary.md), string sanity):

| Main board | Peak (typ to min LED bin) | LED pulse rating (IFP) |
|---|---|---|
| TPS923610 (C9 at 25.5 V) | **43.7-49.3 mA** | 80 mA |
| TPS923611 (C9 at 31.4 V) | **68.0-73.5 mA** | 80 mA |

> **About the 80 mA rating.** The Hongli IFP of 80 mA is specified only for 0.1 ms pulses at 1/10 duty (datasheet p.4). This pulse decays over roughly 0.25-1 ms, so "under 80 mA" is an estimate, not a datasheet guarantee. Treat "light off, wait 10 s" as mandatory on every main board.

- Both are under the rating, and the pulse lasts about a millisecond. Still, repeated pulses age the LEDs, and on a TPS923611 board the margin is small.
- With brightness at 0 for more than 2.5 ms, the driver is shut down. LED_SW then sits at 5.2 V or less, far below the roughly 11 V a 5-LED string needs, so no current flows.
- If the light was on with nothing attached, wait the full 10 s after switching it off.
- Unplugging while lit is harmless in itself: the break is only 14 mA at 25 V or less. The risk is plugging it straight back in, which is the hot-plug case above.

## 6. Misinsertion: what happens if it goes on wrong

**With the housing, the posts can only reach `J6` one way.**
- Turned 180°, the posts (then at x 2.80 / 5.34) land on the solid top face of the case at about 7.9 mm above seated (housing/out/REPORT.md), well before anything else. Nothing electrical happens ([design/mechanical-spec.md](../design/mechanical-spec.md) §3d).
- The clip's fingers fix the front-to-back and sideways position before the posts reach `J6`. A shifted fit cannot happen while the clip is on the case.

**Forced attempts bend posts; they do not short anything.** After any forced, rotated or tilted attempt, take the light off and run the go-gauge ([ASSEMBLY §4](ASSEMBLY.md#4-header-qa-length-and-go-gauge)). A bent post can land on the edge of a socket next time.

**Why the bare board must never be plugged in.** Every rotation, shift and mirror of a bare 3-post plug was enumerated ([research/electrical-j6.md](../research/electrical-j6.md) §5, re-run on the real pads in [design/review-electrical.md](../design/review-electrical.md) VERIFIED 8).
- All placements are inert except one: the anode post on LED_SW with a return post on `J6`-4 (ground). There the driver has no current feedback. It ramps up until its over-voltage protection trips three times and latches, in under about 1 ms.
- The 200 Ω resistor limits that pulse to about **79 mA** even on a TPS923611 board (less on a TPS923610). That is just under the 80 mA rating, which is itself specified only for 0.1 ms pulses (see the note above).
- No placement can drive the LEDs from the battery, 3.3 V or a GPIO: 4.2 V is far below the string's knee.

**Only three posts carry metal: `J6` pins 5, 6 and 11.**
- The board has no hole or copper at pin 4 (ground, next to LED_SW) or at pin 12 (the raw battery, P+_FUSE).
- The generated gate keeps copper 1.290 mm from pin 4 and 1.690 mm from pin 12 ([pcb/docs/design_summary.md](../pcb/docs/design_summary.md), handedness gate).
- The empty fourth corner also checks that position 4 was pushed out of the header.

## 7. Measure the J6 entry

The capture budget depends on the size of the socket entry, and that is known only from models:

| Source | Entry size |
|---|---|
| Vendor STEP of `J6` (Sullins PPPC062LJBN-RC) | 1.40 × 1.40 mm lead-in square at the face, narrowing to 0.60 × 0.60 ([research/mechanical-j6.md](../research/mechanical-j6.md)) |
| Stock case model ([research/enclosure.md](../research/enclosure.md)) | about 1.1-1.14 mm, 0.15 mm below the face |
| Housing check model ([housing/PROGRESS.md](../housing/PROGRESS.md), open items) | 1.04 mm, 0.1 mm below the face. Only indicative: the model's contacts are simplified |

For a 0.64 mm square post, a 1.04-1.14 mm entry leaves only ±0.20-0.25 mm of capture. A 1.40 mm entry leaves ±0.38 mm (**derived**: (entry − 0.64) / 2). Measure a real entry before relying on the fit:
- look into your `J6` through the case opening with a loupe or USB microscope, next to a known reference (a 0.64 mm post or a drill shank); or
- measure a loose PPPC062LJBN-RC with pin gauges or drill shanks, and note the largest one that enters 0.1-0.2 mm.

If the real entry is small (about 1.0 mm or less), take extra care with the go-gauge and with post straightness.

## 8. Pull-off force, 20 cycles and the 7-day check

The clip holds by spring friction plus the `J6` contacts. There is no snap. Computed values are about **8 N** to pull off (`J6` 4.17 N + friction 3.8 N) and about 8.8 N to push on. **The target is 5 to 12 N pull-off** ([housing/out/REPORT.md](../housing/out/REPORT.md)).

1. **Measure the pull-off force.** Hook a luggage scale or spring scale to a loop of string under the grip ribs at both ends. Hold the reader down and pull straight up. Read the peak. 5-12 N is 0.51-1.22 kgf.
2. **Do 20 on/off cycles.** With the light off, fit and remove the light 20 times, by the ends. Then:
   - measure the pull-off force again;
   - look for whitening or cracks at the roots of the two back spring fingers and the left leaf;
   - run the go-gauge on the posts.
3. **Do the 7-day spring check.** Leave the light fitted for 7 days. Then check that it still seats flat without rocking and that the pull-off force is still 5 N or more. PETG creeps, so some loss is expected. When new, the back fingers push 2.61 N each and the leaf 1.11 N (REPORT, springs).

If it falls below 5 N, the mechanical spec has an optional M2 × 12 screw-lock tab. It is described in [design/mechanical-spec.md](../design/mechanical-spec.md) §3d but not modelled in rev A.

## 9. TPS923611 main boards

Some Silkscreen main boards are built with a TPS923611 in place of the TPS923610 (the out-of-stock swap in the silkscreen-pcb README). Check your board's order record or the marking on U10.

| Item | TPS923610 | TPS923611 |
|---|---|---|
| Over-voltage limit | 24.25-25.5 V | 29.6-31.4 V |
| Hot-plug peak with 200 Ω | 43.7-49.3 mA | 68.0-73.5 mA (under the 80 mA rating; rated at 0.1 ms only) |
| LED_SW-to-ground misinsertion (bare plug only) | less than on the 611 | about 79 mA until the latch |
| LED_MONIT, nothing attached | 2.60-2.73 V | 3.17-3.36 V (may saturate the ADC; it still reads as "open") |

- 200 Ω was chosen over 150 Ω so that TPS923611 boards stay under the rating too. With 150 Ω they reached 78-96 mA ([design/review-electrical.md](../design/review-electrical.md) F3; [pcb/PROGRESS.md](../pcb/PROGRESS.md), rev A fixes).
- On a TPS923611 board the light-off rule is mandatory, not a courtesy.
- The 611's own unplug overshoot (about 31.7 V against its 32 V absolute maximum) is a main-board margin issue. This light neither adds to it nor fixes it ([research/electrical-j6.md](../research/electrical-j6.md) §2).

## 10. Not yet tested

Nothing on this page has been measured on hardware. Still open: a real print on a real case, a real `J6` entry, the spring force after 7 days, the hot-plug pulse on a scope, and the light on a real page.
