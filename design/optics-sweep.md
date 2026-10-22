# Top-edge light bar: optics sweep

Status: done 2026-09-25. Model: `tools/optics_sim.py` (new, numpy + matplotlib, no KiCad). Outputs:
`design/optics/optics_summary.json` (picks, Pareto sets, what-ifs, references), `optics_internal.json` (108 rows),
`optics_external.json` (896 main + 2750 beam-sweep rows), and three PNGs: `optics_profiles.png`, `optics_heatmaps.png`,
`optics_external_map.png`. Re-run: `python tools/optics_sim.py` (about 2 min). One geometry:
`python tools/optics_sim.py --eval "kind=external,page=FT01C,z=16,y=117,tilt=0,angle=40,layout=L5-w12.5-s1.2"`.

Frame: enclosure frame (X = KiCad X - 44.24, Y = 148.25 - KiCad Y, +Y = top edge, Z = 0 at the PCB rear, +Z toward the viewer).
"d" is the distance below the active area's top edge (y 107.90). "Tilt" is positive when the axis is tilted toward the page (-Z)
and negative when it is tilted away from it, toward the viewer.

## Headline
1. **With 120 deg LEDs, the internal variant and the external variant look almost the same.** The best internal geometry
   (LEDs 7 mm above the active top) gives 10 mm below the top about **15x the brightness of the middle and about 85-90x the
   bottom edge**. An external 120 deg bar with its LEDs 4 mm in front of the face gives 15x and 87x. For grazing sources the
   emitter height h cancels out of every ratio, so only the distance from the LEDs to the page top changes the gradient.
   Raising h only adds flux: about 6 % at h 1.2 versus 1.6 % at h 0.3.
2. **Tilting the LEDs toward the page never helps uniformity with a broad LED.** It only moves flux onto the page
   (flux 0.21 -> 0.47) and makes the gradient steeper (nf 45 -> 141). Every best-uniformity pick in the requested
   0..35 deg range is at tilt 0.
3. **Only one thing actually flattens the page: a narrow-beam LED (40-60 deg full angle) mounted high, 8-10 mm in front of
   the face, aimed along the page or slightly away from it.** This is the external variant only.
   - One geometry serves both panels: 40 deg LEDs at z 16 / y 117 / tilt 0.
   - The brightest band (about 20 mm down) is about **7-8x the bottom edge** (FT01C 8.2, PLAIN 6.9), compared with
     45-260x for a 120 deg bar.
   - 26-27 % of the flux lands on the page (far edge 72-77 lux per lumen per LED, against 7.6 for the 120 deg z 10 bar).
4. **Layout:** 5 pairs at a **12.5 mm pitch with tight pairs (warm/cool 2.4 mm apart)**. Compared with an even 11.1 pitch
   and 4.4 mm pairs, this raises the ends-to-middle brightness from 0.64 to 0.76-0.88 and cuts the colour-mix error from
   0.05 to about 0.01. **Six pairs change no ratio by more than 1 %** and add only brightness (+20 %), so 5 per string stays.
5. **A glossy front film roughly doubles every ratio.** This is the Fresnel sensitivity: 6.2 -> 11.8 for the best
   external case and 89 -> 402 for the internal case. A matte (anti-glare) film sits nearer the no-Fresnel numbers.

## Panel front z (which page plane the model uses)
| Panel | Thickness | Page (front) z in the case | Evidence |
|---|---|---|---|
| GDEQ0426T82-**FT01C** (touch + light) | 1.98 +-0.2 (touch 0.30, OCA 0.18, LGP 0.40, OCA 0.18, EPD 0.92) | **4.98**, pressed to the lip | `silkscreen-enclosure-claude/src/params.py:24-26` (DISP_REAR 3.0, DISP_FRONT = 3.0 + PANEL_T, LIP = DISP_FRONT); README.md:102 (stack); README.md:532-536 (the 7 midplate bridge springs push plate + glass against the lip) |
| GDEQ0426T82-**T01C** (touch only) | **1.41** | **4.41** once held by stops (3.0 + 1.41). Loose in the stock case | de-link_pcb `docs/final-review-2026-09-19/sections/11_mechanical_enclosure_assembly.md:405` ("1.41 mm for the non-front-light T01C"). This matches the FT01C stack minus the LGP and one OCA (1.98 - 0.58 = 1.40) |
| **GDEY0426T82** (plain) | **0.926** +-0.1 (glass 0.5, FPL 0.17, PS 0.256) | **3.926** (PLAIN_FRONT), held by PANEL_STOPS | light-strip copy `enclosures/silkscreen-enclosure-claude/src/params.py`, "light-strip variant" block: PLAIN, `PLAIN_FRONT = DISP_REAR + PLAIN['t']` (3.926), "the PS face is 1.054 under the lip", PANEL_STOPS rails hang from the lip onto the PS |

**Answer: a thinner panel does NOT get pushed against the lip.**
- The midplate springs only take up the FT01C's +-0.2 mm. The README gives 0.15 mm of deflection for a thin panel and
  0.55 for a thick one, out of 0.6 available; 0.35 at nominal.
- So the springs go slack for any panel thinner than about 1.98 - 0.35 = **1.63 mm** (INFERRED from those numbers).
- In the stock Rev K case, a T01C (1.41) sits at least 0.22 below the lip and a plain panel (0.926) at least 0.70 below
  it. Either one is loose: it rattles and nothing holds its front plane.
- The light-strip copy fixes this for the plain panel with PANEL_STOPS rails. These hold the PS face at 3.926, with the
  panel's rear on the midplate at 3.0, so the springs are loaded exactly as for a nominal FT01C.
- A T01C needs the same kind of stops at 4.41. The light-strip copy also notes that the FT01C no longer fits its tub
  (the stops would press on the touch film).
- **Any modified case must therefore name the panel it supports.** This model uses 4.98 / 4.41 / 3.926.

What this means for the light:
- **Internal variant:** the page's depth below the lip decides how much room the emitter has.
  - PLAIN: 1.054 below the stock lip.
  - T01C: 0.57 below.
  - FT01C: 0 (no room at all).
- **External variant:** a deeper page lies further inside the lip's shadow. PLAIN needs the source about 2 mm higher than
  FT01C for the same shadow band (see the band tables).

## Model (tools/optics_sim.py)
**Sources and irradiance**
- **Page:** the active area, x 2.16..57.84, y 15.10..107.90, in the plane z = z_page.
- **LEDs:** point sources, each with an axis unit vector: -Y, tilted toward -Z by `tilt`.
- **Pattern:** I = cos^m(angle to the axis), and 0 behind the emitter. m = ln 0.5 / ln cos(half-angle), which gives
  m = 1.0 at 120 deg, 2.0 at 90, 4.8 at 60, 9.6 at 40 and 19.4 at 30.
- **Irradiance:** E = sum I cos(incidence) / r^2. The Fresnel transmission of a flat n = 1.5 film can be multiplied in
  as an option.

**Occluders** (z-planes; a ray is blocked only when the plane lies strictly between the source and the page)
- **Front skin:** three `Aperture`s, each opaque except inside the window rectangle:
  - the lip underside: z 4.98, x 1.56..58.44, y 14.5..108.5;
  - the bevel corner: z 5.40, same rectangle;
  - the front face: z 6.00, 0.6 wider on every side.
- **`Plate`s:** the lip underside as a ceiling over y >= 108.5, and an optional visor.
- **Internal sources sit under the (raised) ceiling.** `internal_occluders()` replaces the skin planes below that ceiling,
  so the ceiling can never block them: their rays only descend.
- **So the internal variant has no occlusion problem.** Its limit is the room for the emitter:
  - ceiling needed = z_page + h + 0.40 (half the emitter height) + 0.05;
  - skin left = 6.0 - ceiling;
  - `internal_fit()` classes the result as stock lip / raised ceiling (skin >= 0.6) / thin skin (0.4-0.6) /
    Z_FRONT +x.

**Metrics** (warm string only; the cool string is its mirror image in every layout)
- **profile:** mean across x over the middle 80 %.
- **near/far:** the profile at d = 2 / 5 / 10 / 20 / 40 / 80, divided by the far edge (d = 92.8).
- **nf 10-40:** the maximum of the profile over 10-40 mm, divided by the far edge.
- **peak/far >2mm:** the maximum beyond 2 mm, divided by the far edge. This is the "brightest visible band vs the bottom"
  number that the beam sweep ranks by.
- **vs mid:** the profile divided by its value at d = 46.4.
- **band:** where the profile first reaches 5 % of its maximum, both on the x-mean and on the worst single column.
- **min/max:** over the whole page and over the lower 80 %.
- **scallop:** the max/min ripple at d = 5 / 10 / 20, measured between the 2nd and the 2nd-last LED so that end falloff
  is not counted.
- **ends/mid:** at d = 10 with both strings on.
- **mix:** the maximum |warm share - 0.5| at d = 10.
- **flux:** the fraction of the string's emitted flux that lands on the active area.
- **lux per lm:** lux at the far edge / the middle for each lumen emitted by each LED.
  - A string at about 3 lm per LED gives about 3x these numbers.
  - The ~3 lm per LED at 13.3 mA is an ASSUMPTION that is not verified. The parts task should replace it with the
    chosen LED's datasheet flux.

**Validation:** the new model reproduces the light strip's own top-edge case (6 pairs +-3.3, gap 1.197, h 0.785) as
2313 / 188 / 46.2 / 9.33 at 2 / 10 / 20 / 40 mm, ends/mid 0.645. The light-strip model gave 2017 / 196 / 46.8 / 9.3 and
0.647. The small differences come from the mean vs the median and from its separable cos*cos pattern.

## Sweep 1: internal (LEDs under the top bezel skin, 5 pairs L5, 120 deg, tilt 0)
**nf 10-40 by LED face y (the gap to the active top).** These numbers are **identical for FT01C, T01C and PLAIN, and for
every h from 0.3 to 1.2, to within 2 %**, because the grazing ratios do not depend on h:

| LED face y | 108.6 | 109.5 | 110.5 | 111.5 | 113.0 | 115.0 |
|---|---|---|---|---|---|---|
| gap to the active top (mm) | 0.7 | 1.6 | 2.6 | 3.6 | 5.1 | 7.1 |
| nf 10-40 (= near/far @10) | 206 | 178 | 154 | 134 | 112 | 90 |

**Flux fraction on the active area (PLAIN; about the same for the other panels at equal h):**

| h \ face y | 108.6 | 109.5 | 110.5 | 111.5 | 113 | 115 |
|---|---|---|---|---|---|---|
| 0.3 | 0.190 | 0.085 | 0.051 | 0.035 | 0.024 | 0.016 |
| 0.6 | 0.311 | 0.162 | 0.099 | 0.070 | 0.047 | 0.031 |
| 0.8 | 0.358 | 0.205 | 0.130 | 0.092 | 0.062 | 0.042 |
| 1.0 | 0.386 | 0.242 | 0.158 | 0.113 | 0.077 | 0.052 |
| 1.2 | 0.404 | 0.273 | 0.183 | 0.133 | 0.091 | 0.062 |

**Where the emitter fits** (ceiling needed = z_page + h + 0.45; skin left = 6.0 - ceiling; minimum skin 0.4):

| h | PLAIN (page 3.926) | T01C (4.41) | FT01C (4.98) |
|---|---|---|---|
| 0.3 | stock lip (ceiling 4.68) | raised ceiling 5.16 | ceiling 5.73: Z_FRONT +0.13 |
| 0.6 | stock lip (4.98) | thin skin (5.46, 0.54 left) | Z_FRONT +0.43 |
| 0.8 | raised ceiling 5.18 (like STRIP_CEIL 5.30) | Z_FRONT +0.06 | Z_FRONT +0.63 |
| 1.0 | raised ceiling 5.38 | Z_FRONT +0.26 | Z_FRONT +0.83 |
| 1.2 | thin skin (5.58, 0.42 left) | Z_FRONT +0.46 | Z_FRONT +1.03 |

**Constraints on h:**
- Emitter heights below about 0.8 are only possible if the LEDs sit **beyond the glass top edge** (face y >= 110.9, with
  the ledge cut away), on a carrier whose underside is below the page plane.
- A side-view LED such as the XL-4008 lying on the glass border cannot go below h ~0.8-1.05: flex or PCB, plus half of
  the 0.8 body.

**The FT01C has no internal option without raising the front skin.** The page is at the lip, so even h 0.3 needs
Z_FRONT +0.13, and flux would be only 1.5-2.4 %.

**Best internal geometry** (layout L5-w12.5-s1.2, 0.5 mm grid):

| Case | near/far @2/5/10/20/40/80 | nf 10-40 | peak/far >2mm | vs mid @10/@20/far | ends/mid | mix | flux | lux far/mid per lm |
|---|---|---|---|---|---|---|---|---|
| PLAIN h 1.2, face y 115 (gap 7.1, skin 0.42) | 311/175/84.2/29.9/7.72/1.47 | 84 | 311 | 15.2 / 5.4 / 0.18 | 0.75 | 0.015 | 0.059 | 1.76 / 9.7 |
| PLAIN h 1.2, face y 113 (gap 5.1) | 476/239/104/33.7/8.15/1.48 | 104 | 476 | 18.0 / 5.8 / 0.17 | 0.77 | 0.013 | 0.087 | 1.86 / 10.8 |
| T01C h 0.6, face y 115 | 317/177/84.7/30/7.73/1.47 | 85 | 317 | 15.3 / 5.4 / 0.18 | 0.75 | 0.015 | 0.030 | 0.88 / 4.9 |
| FT01C h 0.3, face y 115 (Z_FRONT +0.13) | 319/177/84.8/30/7.73/1.47 | 85 | 319 | 15.3 / 5.4 / 0.18 | 0.75 | 0.015 | 0.015 | 0.44 / 2.4 |

**Things that do not help internally:**
- A narrower LED: 60 deg gives nf 66 instead of 89.
- Tilting away from the page: 60 deg at -20 gives 60. That is a small gain, bought by losing flux (0.12 -> 0.08).

## Sweep 2: external (LEDs in front of the face, on a clip-on housing)
Setup: layout L5, 120 deg LEDs, source z 6.5..16, y 109..118, tilt 0..35 toward the page; page = FT01C (4.98) and
PLAIN (3.926). Housing-ok means y_src >= 109.8, which keeps the housing off the window: the bevel edge is at 109.1 and
half the LED's depth adds about 0.7.

**Shadowed band at the top of the page (mm), tilt 20.**

FT01C:
| z_src \ y_src | 109 | 110 | 111 | 112 | 113 | 114 | 116 | 118 |
|---|---|---|---|---|---|---|---|---|
| 6.5 | 0 | 0.65 | 2.7 | 4.7 | 6.75 | 8.8 | 12.9 | 17.0 |
| 7 | 0 | 0 | 0.75 | 1.75 | 2.8 | 3.8 | 5.85 | 7.9 |
| 8 | 0 | 0 | 0 | 0.3 | 0.8 | 1.3 | 2.3 | 3.35 |
| 10 | 0 | 0 | 0 | 0 | 0 | 0.05 | 0.55 | 1.05 |
| 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.3 |
| 14-16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

PLAIN (the page is 1.05 deeper, so the lip corner shadows more):
| z_src \ y_src | 109 | 110 | 111 | 112 | 113 | 114 | 116 | 118 |
|---|---|---|---|---|---|---|---|---|
| 6.5 | 0.05 | 2.55 | 6.7 | 10.85 | 15.0 | 19.15 | 27.5 | 35.7 |
| 7 | 0 | 0.8 | 2.75 | 4.8 | 6.9 | 8.95 | 13.1 | 17.25 |
| 8 | 0 | 0.25 | 0.8 | 1.8 | 2.85 | 3.9 | 5.95 | 8.05 |
| 10 | 0 | 0 | 0.2 | 0.5 | 0.85 | 1.35 | 2.4 | 3.4 |
| 12 | 0 | 0 | 0 | 0.2 | 0.4 | 0.65 | 1.2 | 1.9 |
| 14 | 0 | 0 | 0 | 0 | 0.15 | 0.35 | 0.7 | 1.1 |
| 16 | 0 | 0 | 0 | 0 | 0.05 | 0.15 | 0.45 | 0.7 |

The band tables show two things:
- **The research note's claim does not hold.** It said an LED at (y 110, z 6.5) lights the glass down to about 107.93.
  The **front face itself** (z 6.0 from y 109.1 up) blocks those rays: a source only 0.5 mm above the face at y 110
  leaves a 0.65 mm band on FT01C and 2.55 mm on PLAIN.
- **A shadow-free top needs the source roughly 2 mm above the face for every 2 mm it sits behind the window edge**
  (FT01C), and more for PLAIN.

**Best (y_src, tilt) per source height, 120 deg, with band <= 0.5 and housing-ok** (tilt 0 wins every row):
| page | z_src | y_src | near/far @2/5/10/20/40/80 | nf 10-40 | peak/far | band | vs mid @10/@20/far | flux | lux far/mid per lm |
|---|---|---|---|---|---|---|---|---|---|
| FT01C | 7 | 110 | 1118/450/159/42.9/9.07/1.51 | 159 | 1118 | 0 | 25.2 / 6.8 / 0.16 | 0.30 | 3.5 / 21.8 |
| FT01C | 8 | 112 | 527/274/118/36.8/8.51/1.49 | 118 | 527 | 0.3 | 19.7 / 6.2 / 0.17 | 0.22 | 4.9 / 29.1 |
| FT01C | 10 | 114 | 264/168/86.5/31.4/7.97/1.48 | 87 | 264 | 0.05 | 15.2 / 5.5 / 0.18 | 0.23 | 7.6 / 43.3 |
| FT01C | 12 | 118 | 133/95.1/56.9/24.4/7.11/1.46 | 57 | 133 | 0.3 | 10.9 / 4.7 / 0.19 | 0.17 | 9.5 / 49.2 |
| FT01C | 14 | 118 | 105/80.2/51.1/23.1/6.99/1.45 | 51 | 105 | 0 | 9.9 / 4.5 / 0.20 | 0.20 | 12.1 / 62.1 |
| FT01C | 16 | 118 | 81.6/66.3/45.1/21.8/6.85/1.45 | 45 | 82 | 0 | 8.9 / 4.3 / 0.20 | 0.21 | 14.7 / 74.1 |
| PLAIN | 8 | 110 | 550/329/140/41.3/8.98/1.51 | 140 | 550 | 0.25 | 22.4 / 6.6 / 0.16 | 0.35 | 7.0 / 43.4 |
| PLAIN | 10 | 112 | 258/183/96.9/34.3/8.35/1.49 | 97 | 258 | 0.5 | 16.4 / 5.8 / 0.17 | 0.29 | 9.7 / 57.5 |
| PLAIN | 12 | 113 | 156/124/75.7/30.3/7.97/1.48 | 76 | 156 | 0.4 | 13.3 / 5.3 / 0.18 | 0.28 | 12.5 / 71.2 |
| PLAIN | 14 | 114 | 103/88.4/59.8/26.8/7.6/1.47 | 60 | 103 | 0.35 | 10.9 / 4.9 / 0.18 | 0.27 | 15.0 / 82.7 |
| PLAIN | 16 | 116 | 73.4/63.9/45.9/22.7/7.07/1.46 | 46 | 73 | 0.45 | 8.8 / 4.4 / 0.19 | 0.24 | 16.9 / 87.8 |

At z 6.5 (both pages), and at z 7 for PLAIN, no geometry keeps the band <= 0.5 mm.

**Pareto sets** (least band, lowest nf 10-40, most flux; housing-ok; 120 deg; tilt 0..35) have 38 of 448 members for
FT01C and 36 for PLAIN. They are dominated by z 16:

| Pareto member | FT01C | PLAIN |
|---|---|---|
| Least band + best nf | z16 y118 t0: band 0, nf 45, flux 0.21 | z16 y112 t0: band 0, nf 54, flux 0.29 |
| Middle of the front | z16 y113 t0: band 0, nf 58, flux 0.29 | z16 y110 t0: band 0, nf 57, flux 0.31 |
| Most flux | z12 y110 t35: band 0, nf 141, flux 0.47 | z10 y110 t35: band 0, nf 151, flux 0.47 |

Every step along the front trades about +0.01 of flux for about +2 of nf.
- The front's other extreme is a 6.5 mm source at y 118. It looks uniform (nf 34 on FT01C, 9 on PLAIN) only because the
  top 17-36 mm is in shadow, so it is not a usable design.
- Full lists are in `optics_summary.json -> external_pareto`, and the grid map is in `optics_external_map.png`.

**Beam and tilt what-if** (FT01C and PLAIN, L5; full angle 120/90/60/40/30; z 8..16; y 110..118; tilt -30..+30;
best by peak/far with band <= 0.5):

| page | angle | z_src | y_src | tilt | near/far @2/5/10/20/40/80 | peak/far | band / worst col | scallop @5 | flux | lux far per lm |
|---|---|---|---|---|---|---|---|---|---|---|
| FT01C | 120 | 16 | 114 | -30 | 19.9/35.3/35.5/20.8/6.91/1.46 | 37.6 | 0.4 / 0.4 | 1.04 | 0.14 | 13.3 |
| FT01C | 90 | 16 | 116 | -30 | 8.2/15.2/18.8/14.1/5.82/1.42 | 18.8 | 0 / 0 | 1.03 | 0.10 | 14.9 |
| FT01C | 60 | 12 | 116 | -30 | 5.6/10.5/13.8/11.2/5.14/1.40 | 13.9 | 0 / 0 | 1.07 | 0.06 | 11.1 |
| FT01C | 60 | 16 | 118 | -25 | 1.7/3.9/6.7/7.5/4.37/1.37 | 7.7 | 0 / 0 | 1.02 | 0.07 | 19.1 |
| FT01C | 40 | 10 | 114 | -20 | 2.0/6.3/10.6/9.6/4.69/1.38 | 11.1 | 0.4 / 2.5 | 1.96 | 0.07 | 15.7 |
| FT01C | 40 | 12 | 118 | -25 | 0.8/2.0/4.0/5.2/3.57/1.33 | 5.2 | 0.3 / 1.45 | 1.20 | 0.03 | 11.2 |
| FT01C | 40 | 14 | 118 | -15 | 0.7/2.0/4.1/5.5/3.73/1.34 | 5.5 | 0.25 / 1.35 | 1.14 | 0.09 | 31.5 |
| FT01C | **40** | **16** | **118** | **-5** | **1.05/2.6/5.1/6.5/4.11/1.36** | **6.6** | **0 / 0.75** | 1.10 | **0.20** | **62.1** |
| FT01C | 30 | 16 | 118 | +10 | 2.0/5.2/10.0/10.8/5.3/1.41 | 11.5 | 0 / 1.4 | 1.41 | 0.54 | 113 |
| PLAIN | 60 | 16 | 116 | -15 | 1.9/4.5/8.2/8.9/4.84/1.39 | 9.4 | 0.45 / 0.45 | 1.02 | 0.14 | 32.4 |
| PLAIN | **40** | **16** | **116** | **+5** | **1.4/3.9/8.0/9.5/5.05/1.40** | **9.8** | **0.45 / 1.3** | 1.13 | **0.37** | **87.6** |
| PLAIN | 40 | 14 | 114 | +10 | 4.1/11.2/19.1/16.0/6.23/1.44 | 19.8 | 0.35 / 1.05 | 1.35 | 0.51 | 75.6 |

What the beam sweep shows:
- **For broad LEDs, the uniformity optimum sits at the -30 deg edge of the sweep:** throwing the near light away keeps
  helping, at the cost of flux.
- **Narrow beams get there without throwing much away.** With a 40 deg LED at z 16 the axis only needs -5..+5 deg.
- **Beams of 30 deg or less scallop badly near the top** (up to 14x at 5 mm with the 11.1 mm pitch), so 40-60 deg is the
  useful range.

**Recommended external geometries** (0.5 mm grid, layout L5-w12.5-s1.2):

| case | fresnel | near/far @2/5/10/20/40/80 | peak/far | band / worst col | vs mid @10/@20/far | ends/mid | mix | flux | lux far/mid per lm |
|---|---|---|---|---|---|---|---|---|---|
| **FT01C and PLAIN, one housing: 40 deg z16 y117 t0** | no | FT01C: vs mid @2/5 0.40/0.99 | FT01C 8.2, PLAIN 6.9 | FT01C 0 / 0.1, PLAIN 0.6 / 0.8 | FT01C 1.88 / 2.17 / 0.27; PLAIN 1.44 / 1.94 / 0.28 | ~0.86 | ~0.01 | 0.27 / 0.26 | 72 / 77 far |
| FT01C 40 deg z16 y118 t-5 | no | 0.96/2.4/4.8/6.2/3.99/1.35 | 6.2 | 0 / 0.25 | 1.44 / 1.86 / 0.30 | 0.86 | 0.009 | 0.19 | 60.4 / 201 |
| same | yes | 2.0/5.0/9.7/11.4/6.08/1.48 | 11.8 | 0 / 0.05 | 2.03 / 2.40 / 0.21 | 0.86 | 0.009 | 0.14 | 26.8 / 128 |
| FT01C 60 deg z16 y118 t-25 | no | 1.6/3.6/6.3/7.1/4.26/1.36 | 7.3 | 0 / 0 | 1.80 / 2.04 / 0.29 | 0.77 | 0.016 | 0.07 | 18.7 / 65.6 |
| FT01C 40 deg z12 y118 t-25 (lower brow) | no | 0.69/1.85/3.7/4.9/3.46/1.32 | 4.9 | 0.3 / 0.9 | 1.26 / 1.66 / 0.34 | 0.88 | 0.013 | 0.03 | 10.9 / 32.2 |
| FT01C 60 deg z12 y116 t-30 (lower brow) | no | 5.1/9.7/12.9/10.7/5.01/1.39 | 13.0 | 0 / 0 | 3.25 / 2.69 / 0.25 | 0.81 | 0.011 | 0.06 | 10.9 / 43.2 |
| PLAIN 40 deg z16 y116 t+5 | no | 1.27/3.6/7.5/9.0/4.89/1.39 | 9.3 | 0.45 / 0.65 | 1.91 / 2.30 / 0.26 | 0.87 | 0.012 | 0.35 | 85.1 / 334 |
| PLAIN 60 deg z16 y116 t-15 | no | 1.7/4.2/7.7/8.5/4.71/1.39 | 8.9 | 0.45 / 0.45 | 2.02 / 2.24 / 0.26 | 0.78 | 0.015 | 0.13 | 31.9 / 121 |
| PLAIN 60 deg z12 y112 t-10 (lower brow) | no | 4.4/13.7/21.3/16.0/6.12/1.43 | 21.4 | 0.4 / 0.75 | 4.58 / 3.43 / 0.22 | 0.85 | 0.013 | 0.21 | 29.2 / 136 |

The shared z16 / y117 / t0 row was checked with `--eval` (0.5 mm grid). Tilting it by -5 or +5 moves each panel toward
its own optimum.

**Housing keep-out (for the mechanical task).**
- Every ray to the active top passes the lip corner (108.5, 5.4) and the face-bevel edge (109.1, 6.0). The page-bound
  light fills the wedge below the plane through the LED row and the line (y 107.9, z = z_page).
- For a source at (y_s, z_s), housing material below the LEDs must stay at
  **y >= 107.9 + (z - z_page) * (y_s - 107.9) / (z_s - z_page)**.
  - Example, FT01C with z 16 / y 118: the slope is 47.5 deg, so material must stay at y >= 108.8 at z 6, >= 112.5 at
    z 10 and >= 116.2 at z 14.
  - Use PLAIN's 3.926 for a housing meant for both panels.
- A visor above the LEDs does not block page light. Its job is to hide the emitters from the reader, and with negative
  tilts it takes most of the upward flux.
  - A matte black underside keeps the model valid.
  - A white underside adds unmodelled diffuse fill, which would be worth a bench test.

## Sweep 3: layouts, 6 pairs, and the light-strip references
**Layouts** (external FT01C z 10 / y 114 / t 0, 120 deg; the internal results differ by at most 3 %; the scallop range
for the new layouts comes from the recommended table):

| layout | nf 10-40 | scallop @5/10/20 | ends/mid @10 | mix @10 | lux far per lm |
|---|---|---|---|---|---|
| L5: 5 pairs, pitch 11.14, pair +-2.2 | 86.6 | 1.04/1.04/1.07 | 0.64 | 0.049 | 7.6 |
| L5-s3.3: pair +-3.3 (light strip) | 86.2 | 1.04/1.04/1.07 | 0.63 | 0.074 | 7.6 |
| L5-s1.2: pair +-1.2 | 86.7 | 1.04/1.04/1.07 | 0.64 | 0.026 | 7.6 |
| L5-wide: pitch 12.5, +-2.2 (fits XL-4008) | 81.4 | 1.07/1.04/1.06 | 0.75 | 0.028 | 7.5 |
| **L5-w12.5-s1.2**: pitch 12.5, +-1.2 | 81.5 | 1.03-1.37 @5 (narrow beams), about 1.03 @10-20 | **0.76** (0.77-0.88 with narrow beams) | **0.015** (0.009-0.016) | 7.5 |
| L5-w13.5-s1.2: end pairs over the active edges | 77.8 | 1.06-1.54 @5 | 0.82 (0.84-0.93) | 0.010 | 7.4 |
| ALT10: W C W C at 5.57 | 86.4 | 1.04/1.04/1.07 | 0.64 | 0.062 | 7.6 |
| L6: 6 pairs, pitch 9.28 | 86.4 | 1.04/1.08/1.11 | 0.64 | 0.049 | **9.1** (+20 %) |

Pair centres for L5-w12.5-s1.2 (enclosure X): 5.0, 17.5, 30.0, 42.5, 55.0, with warm at -1.2 and cool at +1.2.
- This needs LEDs no longer than about 2.0 mm along x (0603/0805/1206-class top-view on an edge-on PCB, or one dual-CCT
  package per pair).
- With the 4.0 mm XL-4008, use L5-wide (+-2.2).
- L5-w13.5-s1.2 evens out the corners further but scallops more near the top with narrow beams.

**References:**
| case | throw | near/far @2/5/10/20/40 | nf 10-40 | peak/far | vs mid @10 | scallop @5 | ends/mid | flux |
|---|---|---|---|---|---|---|---|---|
| light-strip SIDE strip (6 pairs, pitch 15.55, h 0.785, PLAIN; d from the left edge) | 55.7 | 416/117/36/9.5/2.17 | 36 | 416 | 7.5 | 3.29 | 0.78 | 0.26 |
| light-strip top-edge case (its own model's "not built" option) | 92.8 | 2313/636/188/46/9.3 | 188 | 2313 | 29 | 1.36 | 0.65 | 0.25 |
| this work, internal best (PLAIN h 1.2, gap 7.1, L5-w12.5-s1.2) | 92.8 | 311/175/84/30/7.7 | 84 | 311 | 15 | 1.07 | 0.75 | 0.06 |
| this work, external best (FT01C 40 deg z16 y118 t-5, L5-w12.5-s1.2) | 92.8 | 0.96/2.4/4.8/6.2/4.0 | 6.2 | 6.2 | 1.4 | 1.20 | 0.86 | 0.19 |

**Comparing with the side strip:**
- It lights the SHORT way (55.7 mm). Its gradient is about 2.3x gentler at 10 mm than the best internal top bar, but it
  scallops badly near its edge.
- An internal top bar gains over the light strip's own top-edge option only by moving the LEDs back: a 7.1 mm gap
  instead of 1.2 halves every ratio.

**Fresnel sensitivity** (glossy n = 1.5 film):
| case | nf 10-40 | peak/far | lux far per lm |
|---|---|---|---|
| internal PLAIN pick | 89 -> 402 | 341 -> 2404 | 1.8 -> 0.12 |
| external FT01C z 10, 120 deg | 87 -> 262 | 264 -> 948 | 7.6 -> 1.9 |
| external FT01C 40 deg z16 y118 t-5 | 6.2 -> 11.2 | 6.2 -> 11.8 | 60 -> 27 |

**The steeper the grazing angle, the more Fresnel hurts.** This is one more reason to raise the source.

## What the reader will see (plain language)
Brightness is relative to the middle of the page, one colour string lit. Absolute levels are per lumen per LED; at an
ASSUMED ~3 lm per LED, multiply the lux by about 3.

- **Internal brow, 120 deg LEDs** (best: PLAIN, LEDs 7 mm above the active top, h 1.2, 0.42 mm skin left):
  - A bright glow runs along the top: 10 mm down is **15x the middle**, 20 mm down is 5x.
  - The bottom edge gets **0.18x the middle**: the top 2 mm is about 300x as bright as the bottom row.
  - The lower half reads as dim and the top third as bright, much like the light strip from the side but with a longer
    fade.
  - It is dim overall: 1.8 lux per lm at the bottom, about 5 lux at 3 lm.
  - T01C is the same picture at half the flux. FT01C needs the front skin raised and gets a quarter of the flux.
  - Nothing inside the case can flatten this. The gap to the active top is the only lever: moving the LEDs from 1.2 mm to
    7 mm above the top halves every ratio.
- **External clip-on, 120 deg LEDs, a practical low brow** (LEDs 4 mm in front of the face, z 10, y 114, tilt 0):
  - It looks like the internal version: 15x the middle at 10 mm, bottom 0.18x.
  - It puts **4x more light on the page** (23 % of the flux; 7.6 lux per lm at the bottom).
  - Tilting the LEDs toward the page makes it brighter overall and steeper.
- **External clip-on, 120 deg LEDs, a tall brow** (z 16, y 118, tilt 0): 9x the middle at 10 mm, bottom 0.20x. That is
  better but still a clear top-heavy gradient.
- **External clip-on, 40 deg LEDs, a tall brow** (the best found; z 16 = 10 mm in front of the face, y 117-118 = 1.4-2.4 mm
  behind the case's top face, axis about horizontal, pitch 12.5 with tight pairs):
  - The brightest band is about 20 mm down, at **about 2x the middle**.
  - The top rows run 0.2-1x the middle, and the bottom edge is **about 0.3x the middle**.
  - The top edge's ends are 0.86x its centre.
  - **This reads as a desk lamp over the page: a gentle gradient.** Bottom edge 60-77 lux per lm per LED, about 200 lux
    at 3 lm, with no shadow band on FT01C and 0.6 mm on PLAIN.
  - With a glossy film, expect about twice the contrast (peak/far about 12).
  - With a 6 mm brow (z 12) instead, 40 deg LEDs aimed 25 deg up still give peak/far 5. But only 3 % of the light reaches
    the page (11 lux per lm at the bottom), and the worst column has a 0.9-1.45 mm dim band at the top corners.

## Best achievable geometry per variant
| variant | geometry | result |
|---|---|---|
| Internal, PLAIN | LED face y 113-115 (5-7 mm above the active top), h 1.2 (ceiling 5.58, skin 0.42) or h 0.8 under a STRIP_CEIL-style 5.30 ceiling (flux x0.7), L5-w12.5-s1.2, 120 deg | nf 84-104, peak/far 311-476, flux 6-9 %, mid 10 lux per lm |
| Internal, T01C | same y, h 0.6 (ceiling 5.46, skin 0.54) | same ratios, flux 3-4.4 % |
| Internal, FT01C | needs Z_FRONT +0.13 (h 0.3) or more | same ratios, flux 1.5-2.4 %: not worth it (the FT01C has its own front light) |
| External, both panels, one housing | 40 deg LEDs, z 16, y 117, tilt 0, L5-w12.5-s1.2 | peak/far 8.2 (FT01C) / 6.9 (PLAIN), band 0 / 0.6, flux 26-27 % |
| External, FT01C only | 40 deg, z 16, y 118, tilt -5; or 60 deg, z 16, y 118, tilt -25 | peak/far 6.2-7.3, band 0, flux 7-19 % |
| External, PLAIN only | 40 deg, z 16, y 116, tilt +5; or 60 deg, tilt -15 | peak/far 8.9-9.3, band 0.45, flux 13-35 % |
| External, 120 deg LED only | z 16, y 114-118, tilt 0 (FT01C) / y 112-116 (PLAIN) | nf 45-54; tilting up to -30 gives 35 at half the flux |

## Caveats
- **Geometry only.** The model ignores several things:
  - LED body size and near-field effects: numbers inside about 2 mm of an LED are unreliable.
  - Diffuse scattering by a matte front film: this makes the far page look brighter than predicted, so it is optimistic
    for the ratios.
  - Reflections off the ceiling or visor.
  - The FT01C's own LGP.
  - Refraction to the ink plane (about 1 mm deep under the FT01C stack).
- **Beam patterns are idealised cos^m.** Real narrow-beam SMD LEDs have side lobes; use the chosen part's radiation
  diagram (the tool takes any `angle=`).
- **The ~3 lm per LED figure is an assumption.** The drive current is fixed at 13.3 mA per string (by the main board's current-set resistor R37).
- **Colour mix** is for both strings lit at equal duty. Firmware time-multiplexes at 10 kHz, so the eye averages them.
- **Tilt-away and tall-brow geometries point more light toward the reader.** The visor must hide the emitters. Model it
  with `visor_z=` / `visor_y=` in `--eval`.
