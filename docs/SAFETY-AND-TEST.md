# Safety and test (rev B)

Rev B has not been built or powered. Numbers come from [pcb/docs/design_summary.md](../pcb/docs/design_summary.md) and [housing/out/REPORT.md](../housing/out/REPORT.md) unless marked **derived** (worked out here from them).

## 1. The rules

1. **Frontlight off (brightness 0) before you plug the light in or pull it off.** If it was on with nothing attached, wait about 10 s ([§4](#4-hot-plug-why-the-light-off-rule)).
2. **Never plug the bare board into `J6`.** Only the cap lines it up ([§5](#5-keying-and-misinsertion)).
3. **Remove it by the two ends of the cap**, never by the hood.
4. **Bench-test a new board** before it goes on the reader ([§2](#2-bench-test-of-the-bare-board)).
5. **TPS923611 main boards** have less hot-plug margin: rule 1 is a must there ([§6](#6-tps923611-main-boards)).

The highest voltage the board can ever see is the driver's over-voltage limit: 25.5 V on a TPS923610 main board, 31.4 V on a TPS923611 one.

## 2. Bench test of the bare board

Do this after soldering the headers. The pins are `5` (LED_SW, anode), `6` (W−, warm return) and `11` (C−, cool return); the labels are on the plain side.

**Meter, no power.** Resistance and diode test between 5-6, 5-11 and 6-11, both ways round: all **open (OL)**. A meter's 2-3 V cannot light a 5-LED string. Any reading means a solder bridge: do not power it.

**Current-limited supply.** Set **13 mA** and a **22 V** limit. Connect with the output off, then switch it on.

| + lead | − lead | Expect |
|---|---|---|
| 5 | 6 | D1-D5 light (warm); D6-D10 stay dark |
| 5 | 11 | D6-D10 light (cool); D1-D5 stay dark |

- Across the string (5 to 6, or 5 to 11): about **15.7 to 18.4 V**, typically 16.9 V (**derived**: 5 × V_f at 13.3 mA is 13.00 / 14.25 / 15.75 V, plus 2.66 V across 200 Ω). If the supply sits at 22 V and nothing lights, the string is open: look for a reversed or unsoldered LED.
- Across R1 or R2: about 2.6 V.
- All five LEDs glow about the same. One dark LED while the rest light means that LED is shorted.
- **Do not reverse the supply.** Rev B has no blocking diodes, and these LEDs are rated for only 5 V reverse.

## 3. On the reader

With the cap seated and the light on:

| | This light, lit | Nothing attached |
|---|---|---|
| LED_SW (driver output) | 16.01 V min (hot), 17.26 V typ, 19.41 V worst (cold, highest LED bin); ceiling 22.0 V | 24.25-25.5 V (TPS923610 over-voltage limit) |
| LED_MONIT (LED_SW × 0.1071, ESP32 IO2) | **1.71-2.08 V** | **2.60-2.73 V** |

A lit reading above about 2.40 V means the light is not connected or not seated: switch the frontlight off. Warmth 100 % lights the warm string only, 0 % the cool string only. Use 60 % brightness or more for the first test ([FIRMWARE-NOTES §1](FIRMWARE-NOTES.md#1-enable-pulse)).

## 4. Hot-plug: why the light-off rule

If the frontlight is on with nothing plugged in, the driver climbs to its over-voltage limit and latches off, leaving its output capacitor C9 charged for several seconds. Plugging the light in then dumps C9 through one string. The 200 Ω resistor limits the peak:

| Main board | C9 | Peak (typ to min LED bin) |
|---|---|---|
| TPS923610 | 25.5 V | 47.0-52.6 mA |
| TPS923611 | 31.4 V | 71.3-76.8 mA |

Both are under the LEDs' 80 mA pulse rating, but that rating is for 0.1 ms pulses at 1/10 duty and this pulse lasts about 0.25-1 ms, so the margin is an estimate. The resistor takes up to 1.18 W for about 1 ms, which is why it is a pulse-proof part. With brightness at 0 the driver is off and nothing flows.

## 5. Keying and misinsertion

- **Only 3 pins carry metal:** `J6` pins 5, 6 and 11. There is no pin, pad or copper at any other `J6` position. The nearest copper is 1.39 mm from pin 4 (ground, next to LED_SW) and 1.69 mm from pin 12 (the raw battery).
- **The cap keys the plug.** The case's `J6` opening is off-centre, so a cap turned round puts the pins on the solid top of the case. The walls hold the side-to-side play to 0.052 mm by the time the pin tips reach `J6`, so each pin can only enter its own socket. Pin depth in `J6`: 4.72-5.05 mm nominal, 4.39-5.38 mm worst case, inside the 3.7-6.0 mm window.
- **Why the bare board must not be plugged in.** Every shifted, turned and mirrored placement of a bare 3-pin plug was checked ([research/electrical-j6.md](../research/electrical-j6.md) §5). With 200 Ω the main board is safe in all of them. The LEDs are not: some placements put the driver's full output (up to 25.5 V, or 31.4 V) backwards across a string with no diode to stop it, and the anode-on-LED_SW, return-on-ground case pushes about 83 mA on a TPS923611 board until the driver latches off. Neither can happen with the cap on.

## 6. TPS923611 main boards

Some main boards use a TPS923611 in place of the TPS923610 (the out-of-stock swap in the silkscreen-pcb README). Its over-voltage limit is higher (29.6-31.4 V), so its hot-plug pulse (71.3-76.8 mA) sits close to the 80 mA rating. Always switch the light off first on these boards.

## 7. Shared driver

`J3` and `J6` share one current-regulated driver (13.3 mA). With a panel frontlight on `J3` as well, the two share that current unevenly: safe, but dim. This light is not designed for that.

## 8. Not yet tested

Nothing is proven on hardware yet: the fit and press feel on a real case, the pin depth in a real `J6`, the light on the page, the thin screw-hole skins in the print, and the bench numbers above.
