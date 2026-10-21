# Firmware notes (rev B)

**These are recommendations only. The firmware repository has not been changed.** The light works with the stock firmware, because it uses the same driver and the same frontlight controls as the panel's own frontlight. The changes below make it turn on reliably at low brightness, detect a missing or badly seated light, and avoid needless hot-plug pulses.

Source: [research/electrical-j6.md](../research/electrical-j6.md) §6, updated here for rev B (200 Ω per string, no series diode). Electrical numbers: [pcb/docs/design_summary.md](../pcb/docs/design_summary.md). The `[FW: ...]` references are the file and line citations from that research.

## 0. What the firmware does today

- **Pins.** ADIM (brightness) is on GPIO42, a 10 kHz, 8-bit LEDC channel. COLOR_SEL is on GPIO40, a second LEDC channel. [FW: freeink-sdk/libs/hardware/BoardConfig/include/BoardConfig.h:1872-1873]
- **Warm/cool is time-multiplexed.** `apply()` writes ADIM = total brightness (gamma 1.6554) and GPIO40 = warm % of 255, at 10 kHz. Warm and cool are never on together, apart from the switching overlap. [FW: .../FrontlightManager/src/FrontlightManager.cpp:336-344]
- **Defaults** are 60 % brightness and 50 % warmth. [FW: src/CrossPointSettings.h:337-338]
- **The brightness is restored at boot.** [FW: lib/hal/HalFrontlight.cpp:7-15]
- **There is no enable pulse and no LED_MONIT read.** The main board's hardware notes ask for a ≥ 100 µs enable pulse, over-voltage latch recovery (ADIM low ≥ 3 ms), LED_MONIT monitoring and colour changes only at duty 0. None is implemented yet.

## 1. Enable pulse

- The TPS923610 turns on only after an ADIM HIGH pulse longer than 40 µs (tADIM_EN, TI datasheet p5).
- At 10 kHz the HIGH time is duty × 100 µs. With the gamma curve, the duty reaches 40 µs only above about 58 % brightness (inferred), so turning the light on at a lower setting may never enable the driver.
- **Recommendation:** drive GPIO42 HIGH for **≥ 100 µs**, then start the 10 kHz carrier at the wanted duty.
- Until then, the docs tell users to turn on at 60 % or more first ([SAFETY-AND-TEST §3](SAFETY-AND-TEST.md#3-on-the-reader)).

## 2. LED_MONIT load check

LED_MONIT is ESP32 IO2: LED_SW through a 1 MΩ / 120 kΩ divider (ratio 0.1071), filtered with a time constant of about 10.7 ms. **Read it once, 30 to 50 ms after enabling:**

| Condition | LED_MONIT | LED_SW |
|---|---|---|
| This light, lit (5 LEDs + 200 Ω, no diode), all LED bins and temperatures | **1.71-2.08 V** | 16.01-19.41 V |
| **Threshold** | **about 2.40 V** | about 22.4 V |
| Nothing attached, TPS923610 | 2.60-2.73 V | 24.25-25.5 V (over-voltage limit) |
| Nothing attached, TPS923611 | 3.17-3.36 V (may saturate the ADC, about 3.1 V at 12 dB, unverified; still "open") | 29.6-31.4 V |

- Margins: 0.32 V between the highest lit reading and the threshold, 0.20 V between the threshold and the lowest open reading (**derived**).
- **Above the threshold:** report "no light, or not seated" and set the duty to 0 (shutdown).
- **Probe only when the user acts** (turns the light on, or raises brightness from 0). **Never probe periodically.** Every probe with nothing attached charges C9 back up to the over-voltage limit, which recreates the hot-plug case for the next plug-in ([SAFETY-AND-TEST §4](SAFETY-AND-TEST.md#4-hot-plug-why-the-light-off-rule)).
- At boot, if the restored brightness is above 0, run the check once. If it reads open, shut down and do not retry until the user acts.

## 3. Over-voltage latch recovery

- After three over-voltage trips the driver latches off. Only a shutdown followed by a new enable (or VIN undervoltage) resets it (TI p12). ADIM LOW for longer than 2.5 ms is a shutdown (tADIM_SD).
- This happens every time the light is switched on with nothing attached, and when the light is unplugged while lit.
- **Recommendation:** when the user turns the light on, hold ADIM LOW for **≥ 3 ms** first, then give the enable pulse (§1). Setting the duty to 0 for longer than 2.5 ms already counts.

## 4. Warm/cool switching at 10 kHz

- Both strings share one driver output. After each switch, C9 takes longer to settle than the 100 µs period, so a forward-voltage difference between the warm and cool strings shifts current from one to the other.
- The research estimated 4-8 mA of error for a 0.3 V mismatch with no series resistor, and about 2 mA with 100 Ω. With 200 Ω it should be smaller; this was not recomputed.
- **Recommendations:** change colour only at duty 0, as the hardware notes ask; consider offering fixed warm (100 %) and fixed cool (0 %) settings until blending has been checked on a real light. The two colours are different LCSC codes, so their forward-voltage bins are not matched.

## 5. User interface

- Add a hint: "Switch the light off before attaching or removing the clip-on light." Off means brightness 0; then wait about 10 s.
- No brightness cap is needed. The main board's R37 fixes the total current at 13.96 mA or less.
- If a panel frontlight on `J3` and this light on `J6` are both connected, they share the same regulated current unevenly: safe, but dim.

## 6. Not in scope

The hardware does not depend on any of these changes. Whether they land in the firmware is outside this project.
