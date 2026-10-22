# Rev B "simple" spec (supersedes DESIGN-SPEC.md for everything below)

2026-09-25. Owner direction, verbatim essentials:
> "This should be as simple as soldering a board with LEDs [and] headers, fitting into a case with 1-3 parts, screwing it
> together, and popping it on. No acrylic rods, no epoxy setting, no pushing out of pins from an existing part. Basic. If a
> pin isn't used, don't populate it on the daughterboard ... simple, low profile, rounded and matching to the case it fits on,
> functional 'enough' ... mitigating [the LED direction] would be the job of a 3d printer on the case itself, not an acrylic
> rod."

Rev A (rod lens, carrier, clip + cover, BAW56, TSW long-post header) moves to `archive/rev-A-rod-lens/`. The electrical
limits in `research/electrical-j6.md` and the stock-case facts in `design/mechanical-spec.md` sec 1 still apply.

## Frame
- **E frame:** same as before. X = main KiCad X - 44.24; Y = 148.25 - KiCad Y (+Y is the top edge); Z = 0 at the main PCB
  rear, +Z toward the reader.
- **Stock case (unmodified rev K):**
  - top face y 115.60, flat over x 0.91..59.09 and z -4.70..4.20; front edge R1.8, back edge R2.0;
  - plan corners R5 (arc centres (0.91, 110.6) / (59.09, 110.6));
  - sides x -4.09 / 64.09, flat below y 110.6; front face z 6.00; back face z -6.70;
  - J6 (the main board's expansion header) opening x 42.582..58.922, z -5.415..0.215; J6 face y 112.82..113.15;
  - window top edge y 109.1 at the face; active area y 15.10..107.90, x 2.16..57.84;
  - page front z: FT01C 4.98, T01C 4.41, PLAIN 3.926;
  - right side key SW10 (the power button): nothing may touch the right side below y 107.0;
  - back-face counterbore at (40.2, 112.8), D4.2.

## Electrical (simplified)
Per colour: LED_SW -> 5 LEDs in series -> 200 R -> return.
- Warm: D1-D5 -> R1 -> W- (J6-6).
- Cool: D6-D10 -> R2 -> C- (J6-11).
- **The BAW56 diodes are removed.** The housing keys the plug: the opening is off-centre, and the walls hold X/Z before
  the pins reach J6. With 200 R, the main board is safe in every misinsertion (research/electrical-j6.md sec 5). The only
  risk left is reverse stress on the accessory's own LEDs if a BARE board is forced in wrongly; the docs say "don't plug
  the bare board".
- **Worst V_OUT** without the diode is about 19.4 V, under the 22 V ceiling. The hot-plug limits from rev A still hold.

| Ref | Part | LCSC | Notes |
|---|---|---|---|
| D1-D5 | HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3, 3000 K | C210340 | pad 1 (large) = cathode |
| D6-D10 | same MPN, 6000 K | C210343 | |
| R1, R2 | Vishay CRCW0805200RFKEAHP, 200 R pulse-proof 0805 | C5972814 | or a JLC Basic 0805/1206 200 R, if its pulse rating is shown to cover ~1 W for 1 ms |
| J1 | standard 2.54 mm **1x2** male pin header, straight | Basic if possible | pins at J6-5 and J6-6 |
| J2 | standard 2.54 mm **1x1** male pin header, straight | Basic if possible | pin at J6-11 |

- **Header geometry assumed:** body 2.5 tall, post (mating) 6.0, tail 3.0, 0.64 mm square. Record the real part's
  numbers; the housing reads them from geometry.json.
- **J6 positions:**
  - J1 at (54.662, -3.810) and (57.202, -3.810);
  - J2 at (54.662, -1.270);
  - **nothing** at any other J6 position (no pad, no hole).
- The builder hand-solders J1 and J2 (3 joints). JLC assembles the 12 SMD parts, all on one side.

## PCB
- **Board:** 2 layers, **1.0 mm**, black or any mask colour.
- **Outline:** rounded rectangle x -2.50..62.50, z -6.00..11.00, corners R2.0.
- **Frame mapping** (unchanged; handedness gate kept):
  - F.Cu = underside, facing -Y toward the case, component side;
  - x_K = X + 100, y_K = 100 - Z.
- **Height:** PCB underside **y 116.60** (it rests on the housing base's 1.0 mm floor, which rests on the case top 115.60).
  PCB top y 117.60.
- **LEDs:** on the underside, emitting -Y, long axis along X, centres **z 9.50**.
  - Warm D1..D5 at x 1.1, 14.6, 28.1, 41.6, 55.1.
  - Cool D6..D10 at x 4.9, 18.4, 31.9, 45.4, 58.9.
  - Emitter face y 115.90.
- **R1, R2:** underside, **inside the J6-opening zone** x 43.5..52.5, z -4.8..-0.4 (they sit in the opening, below the
  floor window). Height <= 0.7.
- **Headers:** bodies on the underside. Body bottom at y 114.10, 1.5 into the opening. Post tips at y 108.10, which gives
  J6 engagement 4.7..5.05 nominal (limits 3.7..6.0).
- **Mounting holes:** 2 x **Ø4.80 NPTH** at **(10.00, -1.00)** and **(38.00, -1.00)**. The base's Ø4.40 bosses pass
  through them (float +-0.2). No copper within 0.4.
- **Underside keep-outs:**
  - no parts anywhere over the case top (x 0.5..59.5, z -5.2..5.2) except inside the J6-opening zone;
  - boss holes +0.4;
  - LEDs only in z 8.0..11.0.
- **Top side:** no parts. Silk: name, rev B, a "SCREEN" arrow toward +Z, and pin labels.
- **Gates (keep the rev A pipeline's):**
  - ERC 0;
  - DRC 0 with parity;
  - handedness (pads exactly at the 3 J6 positions; no copper within 1.0 of J6-4 (52.122, -3.810) or J6-12
    (57.202, -1.270));
  - NPTH webs >= 0.5;
  - silk >= 0.15 / 1.0;
  - field sync;
  - string sanity for 200 R without the diode.
- **Outputs:** gerbers zip, bom.csv (DigiKey + LCSC columns), jlc_bom/jlc_cpl (SMD only), PDFs, board STEP, **E-frame PCBA
  STEP/STL** (underside at 116.60), build/geometry.json (outline, holes, LED boxes, part boxes, header pins with the tip Y).

## Housing: 2 printed parts + 2 screws (1 part is fine if it is simpler and meets everything)
- **Base:**
  - a 1.0 mm floor lying on the case top face (y 115.60..116.60), with a window over the J6 opening for the header
    bodies and R1/R2;
  - 2 bosses Ø4.40 rising through the PCB holes to the lid, with Ø1.8 pilots for ST2.2 plastic thread-forming screws
    (>= 3 mm of thread);
  - walls that wrap the case top and grip it: the ends follow the R5 corners (inner R about 5.1) and come down the sides to
    y ~107 (right) / lower on the left; a back jaw on the back face; a front jaw on the front face band above the window
    (must stay at y >= 109.6 and out of the page light);
  - small bumps or light interference for a snap-on feel;
  - the walls must align X and Z before the posts reach J6's face (the insertion sweep must show it).
- **Lid:**
  - roof over the PCB, clamping it onto the floor through the 2 screws into the base bosses; a pocket over the header
    tails (no tail trimming needed);
  - a front **visor** in front of the LED row that hides the LEDs from the reader: it comes down just below the emitter
    face, and it never enters the page-light wedge (all page-bound light goes -Y/-Z, away from the visor);
  - **optional printed light mitigation:** a matte inner face; model or reason about an angled inner surface only if it is
    simple.
- **Style:**
  - outer shape continues the case: same edge radii (front R1.8, back R2.0), plan corners rounded like the case R5;
  - top about 3-4 mm above the case top;
  - front about 6-7 mm in front of the case face;
  - width at most a wall thickness wider than the case each side.
  - It should look like a smooth rounded cap on the device.
- **Print:** PETG (or PLA for a trial), each part support-free in a sensible orientation, walls >= 1.2.
- **Screws:** 2 x ST2.2 x (length to suit) pan head, from the top, heads in counterbores.
- **Checks (reuse the rev A housing check code where it helps):**
  - seated interference against the stock case STL, designed contacts only;
  - -Y insertion sweep with engagement-order heights;
  - post engagement against J6;
  - the page-light keep-out for bare LEDs (from tools/optics_sim.py geometry: rays from the LED row to the page);
  - PCB fit;
  - printability;
  - exports and renders;
  - slice report if cheap.
- Also report the bare-LED page profile at the chosen LED position for FT01C / T01C / PLAIN, with tools/optics_sim.py:
  near/far, top shadow band, and flux on the page.

## As built (2026-09-26); supersedes the matching lines above
- Screws: **M2 x 3 pan head** (ISO 7045 / ISO 14583) in **Ø1.6 blind pilots** with a 0.2 skin, giving 2.2 mm of thread (was ST2.2 in Ø1.8, >= 3 mm). The skin prints only with the slicer's Detect thin wall; without it the pilot is open and a 3 mm screw still ends 0.3 above the case top.
- Height: the lid top is **4.9 mm** above the case top (was 3-4). The 2.0 mm untrimmed header tails and the counterbored heads set it.
- Right side: the X guide at the front corner runs down to **y 103.5 at z >= 2.17**, clear of the SW10 slot (z <= 0.8) and its root at y 106. The rule "nothing below y 107 on the right" becomes "nothing at z < 2.0 below y 107". X play at pin arrival is 0.052 mm.
- Headers: HC-PZ254-11.5L 1x2 (LCSC C27985187) + 1x1 (C27985186); body 2.5, post 6.0, tail 3.0. J6 engagement 4.72-5.05 nominal.
- Retention: a press fit on two 0.10 mm ridges on the back jaw, not a detent.
