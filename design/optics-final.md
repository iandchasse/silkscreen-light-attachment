# Top-edge light attachment: optics and LED final choice

J6 is the main board's expansion header, where the light plugs in; D1-D10 are the light's LEDs and R1/R2 its resistors.

Status: rev 1 done 2026-09-25; **rev 2 (LCSC LED, PCB 118.61) done 2026-09-25, see the next section.** Scope: the EXTERNAL clip-on only. Frame: enclosure frame (X = KiCad X - 44.24,
Y = 148.25 - KiCad Y, +Y = top edge, Z = 0 at the main-PCB rear, +Z toward the viewer). "d" = distance below the
active area's top edge (y 107.90). Elevation angle theta is measured in the Y-Z plane from -Y (down the page); + means
toward the page (-Z), the same sign as optics_sim's `tilt`.

## Rev 2 - LCSC LED pick
Status: done 2026-09-25. **This section supersedes the LED part numbers, the source height, the rod gap and offset, the
keep-out rule and the lux numbers in sections 0-4 below.** Those sections are kept as the rev 1 record, and each carries a
superseded note. The sourcing detail is in `design/led-choice.md`.

**What changed and why:**
- **LED.**
  - The LUXEON 3014 is not on LCSC. It is replaced by **HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3**: warm 3000 K is
    **LCSC C210340** (102,969 in stock) and cool 6000 K is **LCSC C210343** (40,519). Both are JLC Extended.
  - It is the same 3014 package: 3.00 x 1.40 x **0.70**. Its cavity is **2.50 x ~1.12**, against the LUXEON's
    2.50 x 1.15.
  - Ra >= 80. IF 40 mA, IFP 80 mA. No Zener.
  - At 13.3 mA it gives 6.5 lm typ warm and 7.0 lm typ cool (0.50 x the 30 mA flux, from the Hongli p.5 curve).
- **Source height.**
  - PCB underside **118.61 seated** (mechanical-spec.md sec 2d/3f), not 118.14.
  - Emitter face **y = 118.61 - 0.70 = 117.91**.
- **Model.** Emitter W (across Z) **1.15**, with 1.4 as a variant; L 2.50.
- **Tool.**
  - `tools/rod_lens.py` has new constants (Y_PCB_UNDER 118.61, EMIT_W 1.15, EMIT_L 2.50, LAY L5-w13.5-s1.9) and a new mode,
    `python tools/rod_lens.py --rev2 [--quick] [--at D,gap,dz] [--name ...]`, which runs in about 70 s.
  - The rev 2 fine sweep covers:
    - D 3.0 / 3.175 / 4.0 / 4.76 / 5.0;
    - gap 1.0-2.5 in 0.25 steps;
    - dz -0.7..+0.3 in 0.1 steps;
    - z_e 16.
  - The rank is the worst u2 over FT01C and PLAIN and over the FULL neighbourhood, gap +-0.25 and dz +-0.2. Grid-edge
    points are not ranked. A page-flux swing of more than 2.2x over that neighbourhood is penalised.
  - Outputs:
    - `design/optics/rod_rev2.json` (sweep top 40, best per D, the pick, tolerance, variants, lux, keep-out, lip);
    - `rod_rev2_log.txt`;
    - `rod_pattern_rev2.json`;
    - the alternates `rod_rev2_D3.0.json` / `rod_rev2_D4.0.json`.

**Rod re-optimisation (robust best per D, 150 k rays; u2 = max/min over d >= 2, worse of FT01C and PLAIN):**

| D | gap | dz | aim | FWHM | u2 nominal | u2 robust | flux swing | page flux |
|---|---|---|---|---|---|---|---|---|
| 3.0 | 1.75 | 0.0 | -1.2 | 27 | 5.9 | 9.2 | 2.0 | 0.071 |
| 3.175 | 1.75 | +0.1 | -3.8 | 24 | 6.2 | 7.9 | 2.15 | 0.060 |
| **4.0** | **2.0** | **-0.2** | **+3.8** | **22** | **6.0** | **7.5** | **1.9** | **0.090** |
| 4.76 | 2.25 | -0.4 | +4.8 | 19 | 6.6 | 8.6 (band 0.5) | 1.8 | 0.109 |
| 5.0 | 2.25 | -0.5 | +5.8 | 18 | 7.3 | 10.6 (band 0.5) | - | 0.122 |

- **Rejected alternates: 3.0 and 3.175 rods at gap 1.0, dz +0.1.**
  - The first ranking with edge points picked these; they sit at the edge of the gap grid.
  - Nominal they are flatter: peak/far 3.1-3.6 on FT01C, u2 3.7-4.7.
  - But at 1 M rays, the +-0.2 corners reach u2 8.0, and the **page flux swings 3.7x (0.030-0.113)** with dz +-0.2.
    That would show as unit-to-unit brightness.
  - D 4.0 swings 1.8x, and its worst corner is 7.1.
- The rev 1 setting (4.0 / 1.75 / -0.1) at the new source height still works: about u2 4.8 FT01C and 5.5 PLAIN. Moving it
  0.25 down and 0.1 toward the page is a small carrier change that buys the robustness.

### R2.1 Final geometry (enclosure frame, mm; seated)

| Item | Rev 2 value | Rev 1 (superseded) |
|---|---|---|
| **LED, warm (D1-D5)** | **HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3, 3000 K bin WS (2800-3100 K), LCSC C210340** | Lumileds L130-3090001400001 |
| **LED, cool (D6-D10)** | **Same MPN, 6000 K bin 60-5 (5700-6500 K), LCSC C210343.** The MPN does not encode the CCT, so the LCSC code is the key. | L130-5790001400001 |
| LED x positions | **L5-w13.5-s1.9, unchanged:** warm at x 1.1, 14.6, 28.1, 41.6, 55.1; cool at x 4.9, 18.4, 31.9, 45.4, 58.9. The 3.0-long package and its 3.37-long land pattern (Hongli p.2) need a centre spacing of at least 3.6. Tight 2.4 mm pairs are therefore impossible, and 3.8 leaves 0.43 pad to pad and 0.8 body to body. | same |
| Orientation | Long side along X. Pad 1 (large, 1.91 x 0.92) = **cathode** = the chamfered cavity corner (led-choice.md sec 4). | - |
| **Emitter face y** | **117.91** (PCB underside 118.61 - 0.70). **117.70** when the PCB rests on the clip off the case. | 117.44 |
| Emitter centre z | **16.00** (not moved: the LED body edge is at 16.70, the PCB front edge limit is 17.6-17.8 and the +Z wall is at 18.1) | 16.00 |
| **Rod** | Clear PMMA, **D 4.0**, length 66.0 (x -3.0..63.0), ends cut square. **Axis y 113.91, z 15.80**: top **y 115.91 (gap 2.0** below the emitter face), bottom **y 111.91**, centre offset **dz -0.20** (toward the page). | axis 114.16 (at 118.61), z 15.90; gap 1.75, dz -0.10 |
| Beam | Far-field peak **+3.75 deg** toward the page, **FWHM 21 deg** (-7.25..+13.25), peak 1.82 I0. Ledger: 49.5 % hits the rod, 41.4 % passes it, 8.0 % Fresnel loss. | +1.25 deg, 24 deg |
| **Carrier -Z wall** | **Inner face z 13.70** (0.10 off the rod), from the PCB underside **down to y 113.91** (the rod equator), no lower | z 13.80, to 114.16 |
| **Carrier +Z wall = front lip** | **Inner face z 18.1** (0.30 off the rod; the computed minimum is 18.0), outer face >= 19.1, **lower edge y 110.0 absolute**. The allowed range is now **108.01..111.07**: at 111.07 or below it hides the rod from eyes at y 20..110, z 300; at 108.01 or above the reader still sees the page top. | 18.1, 110.0 (range 108.0..110.85) |
| Rod end sockets | Bore 4.1-4.2, 2.0 deep, inner faces x -1.0 / 61.0, now centred at y 113.91, z 15.80 | - |
| PCB front edge | z 17.6..17.8, unchanged | - |

**Keep-out (rev 2).** It is the 99.9 % envelope of the page-bound rays over FT01C, T01C and PLAIN, + 0.3, valid for
x -1.0..61.0:

**y_ko(z) = 108.05 + 0.357 (z - 4.00)** for z 3.93..13.70 (rev 1: 107.99 + 0.341 (z - 4.00) to 13.80).

| z | y | Note |
|---|---|---|
| 3.93 | 100.0 | |
| 3.93 | 108.02 | |
| 6.00 | 108.76 | |
| 7.60 | 109.34 | the clip's front lip bottom at 110.0 clears it by 0.66 |
| 10.00 | 110.19 | |
| 13.70 | 111.51 | |
| 13.70 | 113.91 | -Z wall bottom |
| (arc) | | the rod's lower half, through (15.80, 111.91) |
| 18.10 | 113.91 | |
| 18.10 | 100.0 | close |

- Raw envelope (z: y): 4: 107.73; 6: 108.43; 8: 109.14; 10: 109.86; 12: 110.57.
- The front jaw may cover the case face at z 6.0..7.2 from **y 109.2** up.
- A brow floor at **y >= 111.9** is clear for z 6..13.7.
- The cover skirt bottom at y 110.0 stays inside 108.01..111.07.

### R2.2 Page profile
Monte Carlo, 3 M rays, layout L5-w13.5-s1.9, warm string, x-mean over the middle 80 %.

| | FT01C | T01C | PLAIN |
|---|---|---|---|
| vs mid at d 2 / 5 / 10 / 20 / 40 / far | 0.38 / 0.81 / 1.37 / 1.52 / 1.14 / 0.28 | 0.33 / 0.72 / 1.27 / 1.51 / 1.13 / 0.31 | 0.29 / 0.65 / 1.17 / 1.43 / 1.09 / 0.31 |
| **Peak / far (d > 2)** | **5.54** | **4.95** | **4.58** |
| max/min over d 2..92.8 | 5.56 | 4.90 | 4.59 |
| Shadow band at the top | 0 | 0 | 0 |
| Flux on the page (share of the LED's lumens) | 0.090 | 0.087 | 0.084 |
| Ends / mid (both strings, d 10) | 0.73 | 0.72 | 0.72 |
| **Lux, warm string, 13.3 mA, typ 6.5 lm/LED: d 2 (top) / d 5 / d 10 / d 20 / mid / bottom** | **250** / 530 / 895 / 997 / **655** / **185** | 210 / 456 / 803 / 952 / 632 / 194 | 183 / 404 / 734 / 898 / 626 / 197 |
| Lux at min flux (6.0 lm): top / mid / bottom | 231 / 604 / 170 | 194 / 583 / 179 | 169 / 578 / 182 |

Notes:
- Cool string: x 1.08 (7.0 lm typ).
- Page average: about 570 lux (0.09 x 5 x 6.5 lm over 5167 mm2).
- **Rev 1 comparison:**
  - peak/far was 4.96 / 4.62 / 3.93 and vs mid @2 was 0.26 / 0.22 / 0.19;
  - the higher source and the new aim lift the top edge (0.29-0.38 x mid at d 2) and brighten mid-page (655 vs 612 lux);
  - the price is a slightly stronger band at d 15-20 (1.4-1.5 x mid).
- **Variants:**
  - emitter W 1.4 (full package width): peak/far 6.6 / 5.8 / 5.1;
  - no baffle: about 35;
  - polycarbonate rod (n 1.586): 8.0 / 7.9 / 6.7;
  - glossy film (Fresnel): FT01C 10.6 / T01C 9.5 / PLAIN 8.3.
- **Lateral.** The MC scallop is 1.25-1.30; that is bin noise. The tabulated pattern gives 1.09-1.27. Physically the
  lateral spread stays Lambertian (s is conserved in the rod), which gives about 1.04-1.07.

### R2.3 Tolerance
FT01C / PLAIN max/min over d >= 2; far-field aim; FT01C page flux. 1 M rays each (nominal here 5.66 / 4.90; the 2-3 M
runs give 5.5 / 4.6, so MC noise is about +-5 %).

| rod dz \ gap | 1.8 (-0.2) | **2.0** | 2.2 (+0.2) |
|---|---|---|---|
| -0.4 (0.2 toward the page) | aim +6.8: 6.82 / 5.66, flux 0.123 | aim +5.8: 7.13 / 5.75, 0.115 | aim +5.8: 7.10 / 6.12, 0.108 |
| **-0.2 (nominal)** | aim +2.8: 4.91 / 4.84, 0.094 | **aim +3.8: 5.66 / 4.90, 0.090** | aim +2.8: 6.33 / 5.11, 0.086 |
| 0.0 (0.2 away) | aim +1.3: 4.74 / 5.93, 0.069 | aim -0.3: 4.80 / 6.07, 0.068 | aim -0.3: 5.41 / 5.70, 0.067 |

- **Worst corner of the +-0.2 box:** FT01C 7.13, T01C 6.66, PLAIN 6.12. There is no band anywhere, and the page flux
  spans 0.067-0.123 (1.8x).
  - Rev 1's box reached 7.6 / 8.0.
- Rod dz +-0.3 (outside the box): 8.73 / 6.50 at dz -0.5 (flux 0.128); 5.27 / 6.66 at dz +0.1 (flux 0.058).
- **LED row z +-0.3** (the whole PCB-registered engine: the PCB float): 5.85 / 4.92 at z 15.7; 5.58 / 4.96 at z 16.3.
  Flux 0.088-0.092. **Insensitive.**
- LED row z +-1.0: 6.82 / 5.50 at z 15; 4.63 / 5.66 at z 17.
- **The rod-to-LED registration (dz) is still the tolerance that matters:** about 10 deg of aim per 0.4 mm. Keep the carrier
  pinned to the PCB NPTH datums (mechanical-spec 3f).

### R2.4 Follow-ups for other documents (not edited here)
- **mechanical-spec.md sec 3f** still lists the rod axis at 114.16 / z 15.90, the -Z wall at z 13.80 down to 114.16, and the
  old keep-out rule. Update to: rod axis **113.91 / 15.80**, -Z wall **z 13.70 down to 113.91**, and
  **y_ko = 108.05 + 0.357 (z - 4)**. The lip at z 18.1 and y 110.0 stays.
- **parts.md** D1-D10 should become the Hongli LCSC parts (led-choice.md). R1/R2 get LCSC **C844392**
  (CRCW0805120RFKEAHP). BAW56 C8663 is Extended, 43,296 in stock.

New tools and outputs (rev 1):
- `tools/rod_lens.py`: a 3D Monte Carlo ray trace (skew rays included) of an extended Lambertian emitter through a
  cylindrical rod. It uses vector Snell and unpolarised Fresnel at both surfaces, and traces rays that miss the rod or
  are absorbed by a black channel. Rays are then projected straight onto the page (near field, through `optics_sim.skin()`).
  - `python tools/rod_lens.py`: the screening sweep. `--final`: the tolerance-aware fine sweep. `--pick 4,1.75,-0.1,16`:
    the pick, its variants, tolerances and baselines.
- `tools/rod_report.py` draws the figure and adds follow-up numbers. `tools/rod_layout_check.py` checks the final layout
  and computes lux.
- The sweeps, the tolerance runs and the figure use rod_lens.py's default layout, L5-w12.5-s1.2, which is not buildable
  with 3.0 mm-long LEDs. The x-mean profile barely depends on the layout (peak/far 5.03 vs 4.96 on FT01C).
  `rod_layout_check.py` recomputes every section 0 and section 4 number with the chosen L5-w13.5-s1.9.
- `tools/optics_sim.py` is extended and stays backward compatible (the 40 deg z16 y117 regression still gives peak/far
  8.18 and flux 0.274):
  - `Source.pattern`;
  - `TabulatedPattern` (I/I0 over theta and s = ux);
  - `sources_tabulated()`;
  - `--eval ...,pattern=design/optics/rod_pattern_pick.json`;
  - layouts `L5-w13.5-s1.9` and `L5-w12.5-s1.9`.
- `design/optics/`:
  - `rod_sweep.json` (screening, 480 rows);
  - `rod_fine.json` (fine sweep, 1170 rows plus a robustness rank);
  - `rod_final.json` (the pick, its variants, tolerance, keep-out envelope, lip, baselines, and the refs for (a) and (b));
  - `rod_report.json`, `rod_layout_check.json`;
  - `rod_pattern_pick.json` (the far-field table);
  - `rod_final.png` (4 panels: elevation patterns, page profiles, Y-Z section with the keep-out and lip, tolerance).

## 0. Recommendation (one)
> **SUPERSEDED (rev 2, see "Rev 2 - LCSC LED pick" above):** the LED is now HONGLITRONIC HL-A-3014H421W (LCSC C210340 / C210343); the source sits at y 117.91 (not 117.44); the rod is 4.0 at gap 2.0, dz -0.2; the numbers below are rev 1.

**(c) Lumileds LUXEON 3014 warm and cool LEDs, top-view on the PCB underside, with a clear PMMA rod (4.0 mm) used as a
cylindrical lens below them, held in a matte-black printed channel that is registered to the PCB.**

| | FT01C | T01C | PLAIN |
|---|---|---|---|
| Brightest band / bottom edge (peak/far, d > 2) | **4.96** | **4.62** | **3.93** |
| max/min over d 2..92.8 | 4.92 | 5.42 | 5.96 |
| vs mid at d 2 / 5 / 10 / 20 / far | 0.26 / 0.61 / 1.10 / 1.32 / 0.27 | 0.22 / 0.55 / 1.04 / 1.31 / 0.29 | 0.19 / 0.49 / 0.97 / 1.26 / 0.32 |
| Shadow band at the top | 0 | 0 | 0 |
| Flux on the page (share of the 3014's lumens) | 0.085 | 0.082 | 0.079 |
| Lux at full drive, warm string, typ. flux: d 2 / d 10 / mid / bottom | 158 / 677 / 612 / 166 | 129 / 607 / 583 / 167 | 111 / 555 / 575 / 185 |
| Worst max/min, rod dz +-0.2 and gap +-0.2 | 7.6 | - | 8.0 |

(Monte Carlo, 3 M rays, layout L5-w13.5-s1.9, emitter width 1.4.)

Why this option:
- **It is the most uniform page of all options.** It is about 1.7x flatter than an ideal 40 deg LED (8.2 / 6.9) and
  15x flatter than the bare 3014 (73 / 65).
- There is no shadow band on any panel, and it stays at max/min <= 8 across the print tolerance.
- The LEDs are the DigiKey-stocked parts already chosen in parts.md.
- The PCB stays flat and single-sided SMT.
- The rod is a EUR 1 piece of stock: cut to length, with no polishing, because its ends sit in black sockets.
- Light is not a limit: about 600 lux mid-page at full drive, and the firmware dims from there.
- **Cost of the choice:**
  - The top 2-5 mm fall to 0.2-0.6x mid, which reads as a soft darker top edge.
  - The ends reach 0.74-0.75x mid (both strings on, d 10), against 0.87 for a symmetric 40 deg beam.

## 1. Options evaluated
All options use the same 5-pair string, the same PCB height (header body on the case top, PCB underside y 118.14) and
emitter z 16 (10 mm in front of the case face). The PCB is flat, so tilt is 0. The page profile is the x-mean over the
middle 80 %, warm string only.

| Option | peak/far FT01C / PLAIN | vs mid @2 | band FT01C / PLAIN | page flux | lateral | sourcing | verdict |
|---|---|---|---|---|---|---|---|
| (a) ideal 40 deg lensed SMD, y 117.2 | 8.22 / 6.91 | 0.44 / 0.25 | 0 / 0.6 | 0.27 of its own lumens | scallop@5 1.24, ends/mid 0.87 | **no DigiKey warm+cool narrow SMD family found** | reject (sourcing) |
| (a) 30 deg | 4.35 / 3.69 | 0.02 / 0.01 | **3.6 / 4.8** | 0.25 | scallop@5 1.9 | same | reject (dark top band, scallop) |
| (a) 60 deg | 21.0 / 17.5 | 3.7 / 2.8 | 0 / 0.6 | 0.28 | ends 0.77 | same | reject |
| (b) 3 mm THT 40 deg, die y 116.1 | 8.01 / 6.73 | 0.26 / 0.14 | 0.55 / 1.35 | 0.27 | scallop@5 1.31 | cool white only | reject |
| (b) 3 mm THT 30 deg | 4.24 / 3.60 | 0.01 / 0.00 | **4.7 / 5.9** | 0.25 | scallop@5 2.1 | cool white only | reject |
| **(c) 3014 + 4.0 PMMA rod (pick)** | **4.96 / 3.93** | 0.26 / 0.19 | **0 / 0** | 0.085 of the 3014's lumens | ends 0.75, scallop <= 1.15-1.2 (upper bound; see 1c) | DigiKey LEDs + stock rod | **pick** |
| (d) bare 3014 (120 deg), z 16 | 73.1 / 65.2 | 15.7 / 13.8 | 0 / 0.5 | 0.21 | ends 0.78, scallop 1.04 | DigiKey | reject (top-heavy) |
| (d) bare 3014 + best printed knife-edge, z 16 (plate 1.0 below the face, edge at z_e - 0.7) | 37.3 / 29.1 | 4.9 / 3.1 | 0 / 0.5 | 0.13 | as bare | DigiKey | reject |
| (d) bare 3014 + knife, z 18 (plate 0.5 below, edge at z_e) | 23.5 / 19.1 | 1.9 / 1.0 | 0.5 / 1.0 | 0.058 | as bare | DigiKey | reject |

Notes on (a) and (b):
- These use optics_sim's rotationally symmetric cos^m model at the stated y and z, with tilt 0.
- The flux column is relative to each part's OWN lumens. A narrow-beam indicator LED at 13.3 mA emits about 1-1.5 lm
  (for example INL-3AW30: 5-8.5 cd at 20 mA in a 30 deg beam, about 2 lm at 20 mA). That puts about 0.35 lm per LED on
  the page, against 0.49 lm for the 3014 behind the rod (5.8 lm x 0.085). **So (c) puts at least as much light on the page.**

### (a) Lensed narrow-beam SMD, warm + cool from one family
The searches covered DigiKey first, then manufacturer datasheets. **No DigiKey-orderable warm and cool pair from one
narrow-beam SMD family was found.**

| Part | Data | Why not |
|---|---|---|
| **Cree CLM1C-WKW** (PLCC2, 3.2 x 2.8) | Cool white only: 4600 K min / 6800 K typ. 1400-2800 mcd at 20 mA. IF 25 mA; IFP 100 mA (<= 0.1 ms, <= 1/10); VR 5 V; Vf 3.1 typ / 4.0 max at 20 mA; no Zener listed. The datasheet calls it "wide viewing angle" (HB-CLM1C-WKW, CLD-CT879 rev 14, pp.1-2). DigiKey PN not captured. | Cool only, and not narrow |
| **Dialight 598 series** (PLCC-4 dome, 30 deg, 3.5 mm tall) | Red, yellow, amber, blue and green only (DigiKey product highlight) | No white |
| **Wurth, Kingbright chip whites** | See parts.md: the chip-type whites are cool-only | No warm |
| **Everlight EAHP5630WA3** (5630, 3000 K) | Surfaced by search; a wide-angle PLCC, no narrow-lens sibling | Not narrow |

- Generic domed "narrow" 3528 parts exist on LCSC and marketplaces, but none was verified with a warm and cool pair,
  binned Vf and an IFP rating. Not pursued (DigiKey-primary).
- **Even if a part existed**, a rotationally symmetric 30-40 deg beam also narrows the LATERAL spread. At the 12.5-13.5 pitch
  that gives scallop@5 of 1.24 (40 deg) to 1.9 (30 deg) and a mix error of about 0.01-0.05. The rod narrows the
  elevation only.

### (b) 3 mm through-hole narrow-beam
| Part | Data | Why not |
|---|---|---|
| **Inolux INL-3AW30** (3 mm, 5.08 lens height) | White at x 0.28 / y 0.28, i.e. cool, about 9-10 kK. 5000-8500 mcd at 20 mA. 30 deg in the Inolux table (the DigiKey listing says 40 deg). IF 25 mA; IFP 100 mA (1/10 duty, 0.1 ms); VR 5 V; Pd 95 mW; Vf 2.8-3.8 V at 20 mA; no Zener mentioned (INL-3AX30 datasheet, 2017-07-10, pp.2-3). DigiKey 7604621 (from the search-result URL). LCSC not checked. | The INL-3AX30 series has no warm white |
| **Kingbright WP7104QWC/D** (1500-2700 mcd) and **WP7104VW1C** (3600-6000 mcd) | Both 3 mm, 30 deg, 20 mA | Cool white only; Kingbright USA's through-hole white list has no warm 3 mm part |
| **Kingbright WP5603VW1W/SD** (5 mm) | **80 deg (H) x 40 deg (V) elliptical**: exactly the "narrow elevation, wide lateral" shape wanted | Cool only, 5 mm |
| Everlight 334-15/X1C3-1TVA (warm white) | Surfaced by search | 5 mm, beam angle not captured (UNVERIFIED) |

Other points for (b):
- **No 90 deg bend is needed.** With the PCB horizontal, a lamp inserted from the underside already points -Y. Its die
  sits at about y 116.1 (1 mm standoff) and its tip at about y 111.8.
- The aim then depends on the lead standoff and bending: a +-2 deg lean at 5 mm lead length is plausible. The part also
  needs hand or wave soldering on an otherwise single-sided SMT board.
- 30 deg lamps leave a 4.7-5.9 mm dark band at the top; 40 deg lamps land at about the (a) numbers.

### (c) LUXEON 3014 plus a PMMA rod (cylindrical lens): 2D/3D ray trace
**Model** (`tools/rod_lens.py`):
- Emitter: a 1.4 (Z) x 2.5 (X) Lambertian area at the 3014's top face, y 117.44 (0.70 package on a PCB underside at
  118.14).
  - DS208 Fig. 5 is Lambertian-like: 50 % at 60 deg and about 88 % at 30 deg.
  - The DS208 Fig. 9 cavity is 2.50 x 1.15 (see the variants below).
- Rod: an infinite cylinder along X; n 1.491 (PMMA); diameter D; its top `gap` below the emitter face; its centre offset
  `dz` in Z from the emitter centre.
- The chief ray runs from the emitter through the rod centre, so the aim is about atan(-dz / (gap + D/2)).
- **The lateral direction cosine s = ux is preserved exactly through a cylinder along X** (the surface normals have no X
  component). The lateral spread therefore stays the LED's own Lambertian spread. Only the elevation is focused.
- Baffle: a matte-black channel whose walls are tangent to the rod at its equator. Every ray that misses the rod is
  absorbed, and so is every Fresnel-reflected ray.
- No TIR occurs on a circular section; this was checked and the count is 0.

**Sweeps.**
- Screening: D 2 / 3 / 4 / 5, gap 0-1.5, dz -1.2..+0.8, z_e 12-18.
- Fine: D 3 / 3.175 / 4 / 4.76 / 5, gap 0.75-2.0, dz -1.0..+0.2 in 0.1 steps, z_e 14 / 16 / 18.
- Rank: the worst max/min (d >= 2) over FT01C and PLAIN, and over the neighbours dz +-0.2 and gap +-0.25. The band must
  be <= 1 mm.

| D (mm) | z_e 14 | z_e 16 | z_e 18 |
|---|---|---|---|
| 3.0 | gap 1.5, dz 0: u2 10.3 (robust 17.6) | gap 1.75, dz 0: 8.6 (10.5) | gap 1.5, dz 0: 5.5 (8.0), flux 0.070 |
| 3.175 (1/8 in) | 9.0 (17.8) | gap 1.5, dz 0: 7.1 (10.2) | gap 1.75, dz 0: **5.6 (7.1)**, flux 0.066 |
| **4.0** | gap 1.75, dz 0: 7.6 (11.0) | **gap 1.75, dz -0.1: 6.2 (8.4), flux 0.087, band 0** | gap 2.0, dz -0.4: 6.3 (8.8), flux 0.105 |
| 4.76 (3/16 in) | 7.3 (9.3), band 0.5 | 8.2 (11.4) | 10.9 (14.5) |
| 5.0 | 9.1 (9.9), band 1.0 | 10.7 (13.3), band 1.0 | 13.9 (17.6), band 1.5 |

u2 = max/min over d >= 2, the worse of FT01C and PLAIN; "robust" is the worst neighbour within dz +-0.2 and gap +-0.25.

- **Why D 4 at z 16:** it gives the best robust uniformity at the brief's 10 mm brow. z 18 is marginally better (7.1)
  but adds 2 mm of overhang. At z 14, D 4 still reaches 7.6 (robust 11).
- 2-3 mm rods give 30-50 deg beams (not enough). 5 mm rods go below 20 deg and open a 1-1.5 mm band.

**The pick: D 4.0, gap 1.75, dz -0.1, emitter z 16.**

Flux ledger (share of the LED's lumens):

| Rays reaching the rod | Passing it | Lost to Fresnel | Absorbed by the channel |
|---|---|---|---|
| 52.6 % | 44.1 % | 8.5 % | 47.4 % |

Beam:
- Elevation FWHM **24 deg**, from -10 to +13 deg, with the peak at **+1.25 deg** and I = 1.8 I0.
- **Toward the reader** (theta -70 to -90 deg): at most 0.024 I0.

Page profile:
- The pick puts the brightest band at d 15-20.
- The page seen from the rod centre spans 6..62 deg. The upper flank of the beam supplies the far edge, and the beam's
  lower half passes below the page (onto the desk or lap, away from the reader's eyes).

Variants (full panel numbers are in `rod_final.json`):

| Variant | peak/far FT01C / T01C / PLAIN | page flux | What it shows |
|---|---|---|---|
| **Emitter W 1.15** (the DS208 cavity) | 4.3 / 3.8 / 3.7 | 0.083 | 1.4 is conservative |
| **No baffle** (misses go straight) | 40.6 / 37.6 / 36.1 | 0.167 | The black channel is essential |
| **Polycarbonate rod** (n 1.586), same geometry | 7.3 / 6.8 / 6.7 | about 0.09 | PC is usable after re-tuning the gap; PMMA preferred (lower dispersion and Fresnel loss, no yellowing) |
| **Glossy film** (n 1.5 Fresnel) | 9.9 / 8.5 / 7.3 | x0.74 | A glossy film roughly doubles every ratio, as in the sweep; matte sits near the base numbers |

**Tolerance** (FT01C / PLAIN max/min d >= 2; aim = far-field peak; 1 M rays each):

| rod dz \ gap | 1.55 | 1.75 | 1.95 |
|---|---|---|---|
| -0.3 (0.2 toward the page) | aim +5.8: 7.2 / 5.8, flux 0.122 | aim +5.8: 7.0 / 5.3, flux 0.114 | aim +4.3: 7.6 / 6.0, flux 0.108 |
| **-0.1 (nominal)** | aim +1.8: 5.1 / 6.1, flux 0.091 | **aim +1.3: 5.3 / 6.1, flux 0.087** | aim +3.8: 6.0 / 6.3, flux 0.084 |
| +0.1 | aim -1.3: 6.4 / 8.0, flux 0.064 | aim -0.8: 6.2 / 7.7, flux 0.063 | aim -0.8: 6.0 / 7.7, flux 0.063 |

- **Moving the whole LED row +-1 mm in z** gives 6.5 / 5.2 at z 15 and 6.1 / 7.5 at z 17.
- **Aim sensitivity is about 16 deg per mm of dz** (+4.5 deg for dz -0.2, -2 deg for dz +0.2). The gap matters little.
  Every corner stays within max/min 5-8, with no band.
- **Therefore the rod must be registered to the PCB, not to the housing.** The architecture lets the PCB float +-0.25 in
  Z inside the housing so that J6 can self-centre it. That float would add straight into dz (+-4 deg of aim).

**Accuracy caveat.** The far-field table in optics_sim (a point source at the rod centre) is NOT accurate over the top
20 mm with a rod: the 4 mm aperture seen from about 19 mm is about 12 deg, half the beam width.

| | optics_sim table | Monte Carlo |
|---|---|---|
| FT01C vs mid @2 | 0.70 | 0.25 |
| FT01C peak/far | 6.5 | 5.0 |

- Use `rod_lens.py` for profiles. The table is fine for lateral ratios and for d > 30.
- Its scallop (1.08-1.2) and mix (0.02-0.09) values are noise-limited (MC-binned table). Physically the lateral
  pattern is the LED's Lambertian one (s is conserved), which gives 1.04-1.07 and 0.015-0.027 for a bare 120 deg LED on
  the same layout.
- **Ends/mid is real:** 0.70 for w12.5 and **0.75 for w13.5** (bare 120 deg: 0.73 / 0.78).

### (d) Baseline: bare 120 deg 3014, best tilt, printed cut-off
- **Tilt is fixed at 0 by the flat PCB.** The sweep's best tilt for a broad LED was -30 deg (peak/far 37.6, flux 0.14 at
  z16 y114). Getting it would need a wedged or bent PCB, which is incompatible with the flat single-sided board.
- **Bare 3014 at tilt 0:**

  | z_e | peak/far FT01C / PLAIN | top 2 mm vs mid |
  |---|---|---|
  | 12 | 118 / 103 | - |
  | 14 | 92 / 91 | - |
  | 16 | 73 / 65 | 15.7x |
  | 18 | 58 / 52 | - |

- **Printed knife-edge** (a black plate hk below the LED face, blocking rays that cross it at z < z_e + zk; flux floor
  0.05):

  | z_e | plate hk | edge zk | peak/far FT01C / PLAIN | flux |
  |---|---|---|---|---|
  | 16 | 1.0 | -0.7 | 37 / 29 | 0.126 |
  | 18 | 0.5 | 0 | 23.5 / 19 | 0.058 |

  The extended emitter's penumbra makes a soft cut-off, but it cannot reach single-digit ratios without starving the page.

## 2. Final geometry (enclosure frame, mm)
> **SUPERSEDED by Rev 2 R2.1:** LEDs are C210340 / C210343; emitter face 117.91; rod axis y 113.91, z 15.80 (gap 2.0, dz -0.2); -Z wall z 13.70 down to 113.91. The table below is the rev 1 record (PCB 118.14, LUXEON).

| Item | Value |
|---|---|
| **LED, warm** | Lumileds **L130-3090001400001** (LUXEON 3014, 3000 K, CRI 90 min), DigiKey [5765368], LCSC none. 24.3 lm typ / 19.0 min at 60 mA (DS208 Table 1). |
| **LED, cool** | Lumileds **L130-5790001400001** (5700 K, CRI 90 min), DigiKey [5877570], LCSC none. 26.0 typ / 20.0 min at 60 mA. |
| LED ratings (DS208) | IF 120 mA DC; IFP 150 mA (10 % duty, 10 ms); VR -5 V at 2 uA; no Zener. Vf 2.95 V typ at 60 mA, about 2.65-2.8 V at 13.3 mA (Fig. 4). **Flux at 13.3 mA = 0.24 x the 60 mA value** (Fig. 3: 0.22 at 12 mA, 0.36 at 20 mA): warm **5.8 lm** typ / 4.6 min, cool **6.2 lm** typ / 4.8 min. |
| LED position | On the PCB **underside**, emitting -Y. Long (3.0) side along X. **Emitting face y 117.44** (PCB underside 118.14 = case top 115.6 + 2.54 header body; 0.70 package). **Emitter centre z 16.00** for all 10 LEDs (one line). |
| Lateral layout | **L5-w13.5-s1.9.** Pair centres x 3.0, 16.5, 30.0, 43.5, 57.0, with warm at -1.9 and cool at +1.9. LEDs at x 1.1/4.9, 14.6/18.4, 28.1/31.9, 41.6/45.4, 55.1/58.9, leaving 0.8 mm between bodies. Check the pad-to-pad gap against DS208 Fig. 11. |
| PCB front edge | **z >= 17.6** (LED body edge 16.70 + 0.9). Keep it <= 17.8 so the lip wall (inner face 18.1) passes in front with float clearance. |
| **Rod** | Clear **PMMA** (cast or extruded acrylic), **diameter 4.0** (5/32 in = 3.97 is fine), **length 66.0** (x -3.0..63.0), ends cut square. **Axis at y 113.69, z 15.90**: top 1.75 below the emitter face, centre 0.10 toward the page, bottom y 111.69. |
| Rod holder | A matte-black printed **rod carrier registered to the PCB** (two NPTH datum holes or pins beside the LED row), clamped between the PCB and the housing. It carries: **(1)** two end sockets (4.1-4.2 bore, 2.0 deep; inner faces at x <= -1.0 and >= 61.0); **(2)** the **-Z channel wall**, inner face at z **13.80**, from the PCB underside down to **y 113.69, the rod equator, and no lower**; **(3)** the **+Z wall**, inner face at z **18.0-18.1**, from the PCB down to **y 110.0** (it doubles as the front lip). The walls close the space between the LED row and the rod so that no ray misses the rod. A 4 mm PMMA rod over a 62 mm free span sags about 0.001 mm under its own weight, so no mid supports are needed (they would shadow the page). |
| Tilt | 0 (flat PCB). The aim comes from the rod offset: beam peak +1.25 deg toward the page, FWHM 24 deg. |
| Tolerances to hold | Rod centre to emitter: dz +-0.2, gap +-0.2 (the table above). Emitter z +-1. Rod diameter +-0.1-0.2 (extruded stock) acts like a gap change. |
| Solder mask | Matte black preferred on the light PCB underside around the LEDs. The Fresnel-reflected 8.5 % otherwise recycles as unmodelled fill. |

## 3. Visor keep-out and front lip
> **SUPERSEDED by Rev 2 R2.1:** y_ko = 108.05 + 0.357 (z - 4.00) for z 3.93..13.70; the lip lower-edge range is 108.01..111.07 (the lip stays at z 18.1, y 110.0).

**Keep-out** (the housing must NOT occupy this region; a Y-Z polygon valid for every x in [-1.0, 61.0]):
- Its upper edge is the 99.9 % envelope of the page-bound rays of all three panels, plus 0.3 mm:
  **y_ko(z) = 107.99 + 0.341 (z - 4.00)** for z 3.93..13.80.
- It is traced with the FT01C, T01C and PLAIN page planes (PLAIN's z 3.93 is the lowest).

Vertices (z, y), in order:

| z | y | Note |
|---|---|---|
| 3.93 | 100.0 | |
| 3.93 | 107.96 | |
| 6.00 | 108.67 | |
| 10.00 | 110.04 | |
| 13.80 | 111.33 | |
| 13.80 | 113.69 | -Z channel wall bottom |
| (arc) | | the rod's lower half, through (15.90, 111.69) |
| 18.00 | 113.69 | |
| 18.00 | 100.0 | close |

Envelope samples (z: y): 4.0: 107.69, 6.0: 108.37, 8.0: 109.04, 10.0: 109.71, 12.0: 110.39, 14.0: 111.10, 15.0: 111.76
(rod bottom).

What the keep-out allows:
- **Front jaw on the case's front face:** z 6.0..7.2 may cover the whole flat face from y 109.1 up (the keep-out at z 7.2 is
  109.08). A jaw thicker than 1.2 mm must lift its lower edge along y_ko.
- **Brow floor** between the case and the rod: any underside at **y >= 111.5** for z 6..13.8 is clear. Make that underside
  matte black: the reader sees it at grazing angles.
- Nothing may hang below the rod's equator on its -Z side. Page-bound rays leave the rod's lower -Z quadrant heading
  -Z and down.

**Front lip** (hides the lit rod from a reader at z 300, y 20..110):
- The +Z channel wall: **inner face z 18.1, outer face >= 19.1, lower edge y 110.0**, straight along X from x -4 to 64,
  matte black.
- The allowed range for the lower edge is **108.0..110.85**:
  - at 110.85 or below, it blocks every sightline from the rod's surface to eyes at y 20..110 (the worst case is the eye
    at y 20 looking at the rod bottom);
  - at 108.0 or above, the reader's sightline to the active area's top edge still clears the lip, for all three panels
    and eye y 20..110.
- The lip is out of the page-bound bundle, since every page-bound ray has dz < 0.
- **The glare budget is already small:** the far-field intensity toward the reader is <= 0.024 I0. The lip removes the
  view of the glowing rod.

Housing depth: case back z -6.7 to lip face z 19.1-19.3, i.e. **about 26 mm**. The LED row sits 10 mm and the lip 13 mm
in front of the case face.

## 4. Absolute illuminance
> **SUPERSEDED by Rev 2 R2.2:** 6.5 lm per LED (Hongli, 13.3 mA); FT01C gives 250 / 655 / 185 lux at top / mid / bottom.

Warm string at 13.3 mA, typical flux 5.8 lm per LED (DS208 Table 1 x Fig. 3). Multiply by 0.79 for the minimum flux bin
and by 1.07 for the cool string. Full ADIM duty. At a 50/50 warm/cool mix each string is lit half the time, so the page
sees about the same level as one string.

| Page (layout L5-w13.5-s1.9, Monte Carlo) | d 2 (top) | d 5 | d 10 | d 20 (peak band) | mid (d 46) | bottom (d 92.8) |
|---|---|---|---|---|---|---|
| FT01C | 158 lux | 373 | 677 | 809 | **612** | **166** |
| T01C | 129 | 320 | 607 | 761 | 583 | 167 |
| PLAIN | 111 | 279 | 555 | 725 | 575 | 185 |
| For comparison: bare 3014, z16, FT01C | ~6650 | 5460 | 3790 | 1830 | 425 | 90 |

- The average over the page is about 480 lux (0.085 x 5 x 5.8 lm over 5167 mm2).
- A glossy front film lowers these levels to about 0.74x and steepens the ratios (section 1c).
- 100-200 lux is comfortable reading on e-paper, so normal use will sit at about 20-35 % ADIM.

## 5. Open items
1. **Rod supply.**
   - No DigiKey part is verified. Search surfaced Bivar PLPC1-4MM (DigiKey 5721850), which looks like a short
     panel-mount light pipe, not a 66 mm rod (UNVERIFIED).
   - Buy clear cast or extruded PMMA rod, 4 mm (or 5/32 in), from a plastics stockist. It is a mechanical BOM line, not an
     electrical one.
2. **Rod carrier registration** to the PCB, via datum holes. This needs the mechanical and PCB tasks. It is essential
   because of the +-0.25 PCB float.
3. **Bench test** one pair behind a 4 mm rod on a printed page, matte vs glossy (FT01C), with a black channel.
   - The model ignores surface scatter on extruded rods (die lines), channel reflectance, and the FT01C light guide.
   - A white channel might add useful diffuse fill; it is not modelled.
4. **Pad pitch.** The 3.8 mm pair pitch against the DS208 Fig. 11 land pattern (not read here).
5. **Flux at 13.3 mA** was read from the DS208 Fig. 3 graph (0.24 +- 0.02). The CCT shift at low current is not
   quantified (parts.md).
6. **Lateral mix and scallop** for the rod are bounded, not resolved: 0.015-0.09 and 1.04-1.2. If mixing matters,
   rebuild the table with more than 10 M rays or smooth it in s.
7. **Eyes outside the y 20..110 range.** A reader far above the device (eye y > 112) will see the rod under the lip. Such
   a reader also sees the rod's specular image in a glossy film only when looking from above the device top.

Sources:
- Lumileds DS208 LUXEON 3014 datasheet (2025-09-23): Table 1 p.3, Fig. 3 p.7, Fig. 5 p.9, Fig. 9 p.17
  (lumileds.com/wp-content/uploads/files/DS208-luxeon-3014-datasheet.pdf).
- Inolux INL-3AX30 datasheet: inolux-corp.com/datasheet/Display/Through-Hole-Display/Round-Lamp/INL-3AX30%20series.pdf
- Cree HB-CLM1C-WKW: downloads.cree-led.com/files/ds/h/HB-CLM1C-WKW.pdf
- Kingbright USA through-hole white list: kingbrightusa.com (category KCThru-Hole White LED).
- DigiKey Dialight 598 series highlight: digikey.com/en/product-highlight/d/dialight/598-series-plcc-4-domed-lens-smd-led
- DigiKey PLPC1-4MM listing: digikey.com/en/products/detail/bivar-inc/PLPC1-4MM/5721850
