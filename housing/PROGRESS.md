# Housing rev B - progress

J6 is the main board's expansion header; SW10 is its power button, the right side key.

Contract: `design/DESIGN-SPEC-revB.md`. Rev A (clip + cover + carrier, rod lens) notes: `archive/rev-A-rod-lens/housing/PROGRESS.md`.

## State (2026-09-26, polish pass): DONE, build.py exit 0, all checks PASS
- [x] 0. Rev A `src/`, `out/`, `PROGRESS.md` archived to `archive/rev-A-rod-lens/housing/` (out/ was copied, verified with
      diff, then emptied: a Windows handle blocked the directory rename).
- [x] 1. `src/params.py`, `src/util.py` (copied from rev A), `src/parts.py` (BASE, LID, PCBA from geometry.json rev B;
      contract-number proxy if geometry.json is missing or not rev B).
- [x] 2. `src/build.py`: exports (out/E, out/print STL + STEP, out/print/plate.3mf), checks -> out/checks.json,
      renders -> out/render, out/REPORT.md. Exit 1 on a failed check.
- [x] 3. `src/optics_report.py` -> out/optics.json (bare 120 deg LEDs, FT01C / T01C / PLAIN).
- [x] 4. `src/slice_check.py` (OrcaSlicer, CC2 0.4 / 0.20 Standard / PETG / no supports / detect thin walls ON): base
      20m 7s 3.34 g, lid 10m 29s 3.93 g, no warnings; it now also reads the base G-code and confirms the blind-pilot
      skins are printed (6/6 layers per pilot). Orca's 00000.log now lands in out/slice/<part>/ (cwd), not in src/.
- [x] 5. Final run against the real rev B geometry.json AND the PCB agent's E-frame STL
      `pcb/production/3d/silkscreen-light-attachment_pcba_E.stl` (48 bodies): 0 intersections.
- [x] 6. Polish pass (2026-09-26):
      a. Screws -> M2 x 3 pan head (ISO 7045 / ISO 14583, machine or thread-forming). Pilots dia 1.6 and BLIND
         (bottom y 115.80 = 0.20 skin over the case top). Counterbore floor 118.90 = lid top - k max 1.6 (a k-max head
         sits flush; lid top unchanged at 120.5 = 4.9 above the case). Nominal tip y 115.90: 0.10 above the pilot bottom,
         0.30 above the case. Thread 2.2 mm = 5.5 pitches (1.5 boss + 0.7 floor), 0.2 radial. Screws up to 3.1 seat; a
         4 mm one bottoms with its head 0.9 proud and 0.2 of plastic still under its tip. New check `screws` measures
         the skin and the open pilot on the solid.
      b. X guides: at each front corner the skirt (flat side + corner wrap) runs on down to y 103.5; rear edge rises at
         45 deg to (y 107, z 2.45) so it prints without support and stays at z >= 2.17 below y 107 (SW10 needs >= 2.0);
         R1.0 fillet into the skirt, R1.5 round at the tip (side-view profile `parts.fin_yz`). X play when the post tips
         reach the J6 face: 0.052 (h 5.05 and 4.72; was 0.28 / 0.19); X play <= 0.12 from h 7.0, <= 0.35 from h 8.0;
         Z <= 0.35 from h 7.5. Sweep now samples h 10 .. 0 and requires X <= 0.12 at the tips. New check `keepout`.
         Nothing else changed (base +35 mm3; lid only its counterbore floor, +0.1).
      c. Stray `src/00000.log` deleted; renders (+ `render/side_right.png`), slice report and REPORT.md refreshed.

## Run
    <enclosure venv python> src/build.py          # everything (~100 s; the thin-wall scan is most of it)
    python src/optics_report.py                    # optics numbers (system python)
    <enclosure venv python> src/slice_check.py    # slice report + pilot-skin G-code check (reads out/print/*.stl);
                                                   # run it before build.py so REPORT.md folds in the fresh numbers

## Design (rev B)
- 2 printed parts + 2 x M2 x 3 pan screws. BASE: 1.0 floor on the case top with the J6 window, bosses dia 4.40
  (top y 118.10) with dia 1.6 blind pilots (0.2 skin), skirt down to y 107.0 all round (walls 1.2, 0.05 clearance) plus
  the two front-corner X guides down to y 103.5, end caps wrap the case's R5 corners and the vertical front/back corners,
  back jaw, front jaw over the window = a 1.2 flat band (y 112.6..113.8) with its outer face on the grazing ray (lowest
  emitter point z 8.94 -> window edge, 0.2 margin), 2 bump ridges (x 8..16, 46..54, y 108.2) on the back jaw, 0.10
  interference. LID: roof on the PCB top (clamp), rim 0.10 above the base, tail pocket (to y 119.9), boss recesses (to
  118.2), counterbores dia 4.6 (floor y 118.90), visor z 11.3..12.5 down to y 115.2, closed ends.
- Print: base on its back face, lid top-down. Slicer: "Detect thin wall" ON (or Arachne), else the 0.2 pilot skins are
  dropped by the CC2 profile's classic wall generator and the pilots open onto the case top (verified both ways).

## Deviations
1. Lid top y 120.5 = 4.9 above the case top (contract "about 3-4"): tails 2.0 proud of the PCB top (tip 119.6) + 0.3 +
   0.6 skin; the screw heads need the same (0.7 under-head layer + 1.6 head).
2. Screw thread in the base 2.2 mm (contract >= 3): blind pilots keep every screw tip off the case top.
3. Screws M2 x 3 pan in dia 1.6 pilots instead of the contract's ST2.2 in dia 1.8 (common part; too-long screws bottom in
   the boss instead of on the case top).
4. The right X guide goes below y 107 (to 103.5), against the contract's literal "nothing may touch the right side below
   y 107.0". It follows the mechanical-spec rule behind that line instead: below y 107, only z >= 2.0 (SW10 slot
   y 89.8..106.0, z <= 0.6, slot top 0.8). The guide is at z >= 2.17 with 0.05 clearance, so it only touches the case
   side when the base is pushed sideways.

## Open items
- The 0.2 skins need the slicer setting above; they print as one ~0.23 line per layer (a stop the builder feels, not a
  structural wall). Screw length tolerance (ISO +-0.2 on 3 mm): a rare 3.2 mm screw sits up to 0.1 proud.
- The X guides' lowest 0.5 mm is only the part of the corner wrap in front of the case face (x 62.3..64.7 and the
  mirror): check the look on a print.
- Snap feel is a press fit (0.10 interference ridges), not a detent: try on a print and tune BUMP['proud'].

## 2026-09-30: checked against the consolidated 4.26" case
- `params.STOCK_OUT` now defaults to `../silkscreen-light-strip/enclosures/case-426/out/standard` (the strip-less standard tub + lid). Override it with `SILKSCREEN_CASE_OUT`.
- `build.py` exits 0 with all 9 checks passing. All 410 values in checks.json are identical to the rev K run; only the PCBA STL mtime differs. The old results are kept as out/checks_revK_case.json.
- Mesh comparison, y >= 100 (everything the cap touches or sweeps): the tub and lid volumes are identical, and the symmetric difference is 0.0000 mm3. Sections at x 0/30/50/55.9/63 are identical. The case's only external change is the bottom, which is 1 mm lower (y -9.4 vs -8.4).
- Side keys: the right keys' nubs moved 0.1 mm inward (inside the case). Their outer envelope is unchanged: SW10 is at y <= 106.0 and z <= 0.6, clear of the cap's right guide (y >= 103.5, z >= 2.17).
- The 3.68" case (case-368) has no J6 and is out of scope.

## Rev C (2026-10-20): enclosing hood, rounder brow, rabbeted seam. build.py exit 0, all 11 checks PASS
Rev B was printed and built by the owner (pins, fit, snap good). His notes: board not fully enclosed (open under the overhang and at
the ends), weak light on the lower half of the page, could look nicer. Chosen: printed-only hood, softer/rounder, tighter seam.
Rev B print files are kept in `archive/rev-B-housing/print/`. No new parts, no glue, no supports: still 2 printed parts + 2 screws.
- **Hood (lid).** Flat reflector face from the PCB underside (y 116.60, z 11.30) flared 20 deg away from the case down to the lip at
  y 110.50 (z 13.52); x -2.8..62.8 (the PCB cavity limits; the brief said -2.6/62.6, a 0.2 ledge on the PCB underside plane was avoided).
  Outer front vertical at z 15.12 (9.1 in front of the case face): wall 1.6 at the lip, thicker above. Lip outer edge R0.8, inner edge
  sharp. Closed end walls (flush with the cap sides, x +-5.34 to +-2.8, from z 7.4 forward) run from the roof to the lip, so the LED
  bar and the board edges are hidden from the front and the sides; the opening is the downward slot between hood and case face. Hood
  >= 0.3 from the PCB edge (0.299 measured on the tessellation), >= 1.0 from the LEDs.
- **Outer shape.** Side view: vertical front -> R8 knee -> 45 deg bevel (leg 4.5) -> R2 into the roof (print-friendly: roof-down
  print, nothing steeper than 45 deg except the R2 / R6.25 / R2 bed rounds, patch tops <= 1.46 mm). Front corners R3.75 in plan
  (was R3.0), X-Y corners R6.25 and back R2.0 as before. Lid is 5206 mm3 (rev B 4039), base 2645 (rev B 2725).
- **Seam.** Base: top outer edge stepped in 0.8 for the floor's thickness (y 115.6..116.6), all round the sides, back and corner
  wraps; the front tongue under the PCB is untouched. Lid: skirt wall 0.7 over the rabbet, 0.10 clearance all round, lower edge y 115.75
  (0.15 above the shoulder), outer faces flush; lid underside still 116.70 (0.10 over the floor top); roof on the PCB top is still
  the datum. Check `seam`: lid shifted 0.095 in x/z (and 0.067 diagonally) or lowered 0.095 stays clear of the base, min gap 0.10.
- **Checks (all pass).** Existing 9 plus `seam` and `view` (new); fit now also requires the lid below its roof >= 0.29 from the PCB
  edge. View of the screen top (y 107.90, FT01C 4.98 / PLAIN 3.926) from eyes at z 300, y 20..160: nothing blocked; highest eye y that
  still sees it 189.1 / 181.3 (the lip). Page-light wedge: 0 points, hood at z >= 11.3. An emitter is visible only from y < -227 (z 300).
- **Light (src/hood_light.py wrapping tools/visor_reflector_sim.py; white print R0.80, diffuse; relative to bare-LED mid-page = 1.00).**
  FT01C: lower half 0.51 vs 0.46 (+12 %), mid-page 1.14 vs 1.00 (+14 %), top band 2-20 mm 17.6 vs 14.1 (+24 %); PLAIN similar
  (0.51 / 1.13 / 14.7 vs 0.46 / 1.00 / 11.6). Light grey R0.50 about half of that; black R0.05 +1 %. The gain needs a light-coloured
  lid. A white rev B visor would already have given +1 %. It is a modest gain; a mirror strip would give 2x but is not printed-only.
- **Slice (OrcaSlicer CC2, PETG, 0.20, 3 walls, 30 %, detect thin wall, no supports):** base 20m 20s 3.25 g (rev B 20m 7s 3.34 g), lid 15m 50s
  5.32 g (rev B 10m 29s 3.93 g); no warnings; blind-pilot skins still printed. Total 36 min 10 s, 8.6 g (rev B 30 min 36 s, 7.3 g).
- **New:** src/section2d.py (capped 2-D sections), src/hood_light.py, `build.py --report-only` (rebuilds REPORT.md from checks.json
  after slice_check.py without the 3 min check run), renders hood_corner_iso / hood_from_below / section_led_row_x28.1 /
  section_hood_end_x-4. README and docs/ORDERING.md print lines updated (light-coloured lid).
- **Open / to look at on a print:** the 0.7 skirt (two perimeters, ~1 mm tall) and the 0.15 shadow gap; the base's back rabbet is a
  1.0 mm wide cantilever 0.8 above the bed (bed-edge rule, expected to print); the hood-corner facets where the plan round meets the
  bevel are creases, not a blend; ASSEMBLY / SAFETY / DESIGN docs still say "visor".
