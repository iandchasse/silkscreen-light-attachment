# Housing CadQuery project: progress

- Folder: `silkscreen-light-attachment/housing`. Nothing is committed.
- Python: the enclosure venv (`silkscreen-enclosure-claude\.venv` beside this repo; CadQuery 2.8, trimesh 5.1, manifold3d, scipy, vtk).
- Contract: `design/DESIGN-SPEC.md` sec 4, plus M-spec secs 3-5, the audit fixes (M4, M5, M6, m1, m3, m4, m6, m7, m8, m10) and optics Rev 2.

## Status: COMPLETE and PASSING (2026-09-25)
- [x] `src/params.py`: all numbers, E frame. The stock case's `params.py` is imported read-only (no .pyc written) and matches on 8 values.
- [x] `src/clip.py`, `src/cover.py`, `src/carrier.py`, `src/pcba_proxy.py`: each builds one valid solid. Features are named so every contact and gap is attributed.
- [x] `src/checks.py`: DESIGN-SPEC checks 1-7, plus springs, the engagement stack, the insertion order, and a cross-check of the PCB agent's E-frame PCBA STL.
- [x] `src/build.py`: build, then checks, exports, renders, `out/checks.json` and `out/REPORT.md`. Exit code 1 on any violation.
- [x] Two consecutive runs: exit 0, and all 24 outputs byte-identical (STL, STEP with fixed timestamp, 3MF, JSON, MD, PNG). About 175 s per run; the thin-wall scan takes 145 s of that.
- [x] `pcb/build/geometry.json` (written by the PCB agent at 14:48) is used for the fit checks: outline 102 pts, 9 NPTH, 15 body boxes, 3 pins. The proxy is only the fallback. `pcb/production/3d/*_pcba_E.stl` is cross-checked: tips 107.94 / tails 121.40 match, and the part bodies sit 0.70 from the clip and 0.73 from the cover (seated).
- [x] OrcaSlicer (Elegoo CC2, 0.4 nozzle, 0.20 Standard, Elegoo PETG, 3 walls, 30 %, supports OFF), no warnings:

  (rev 0 values, superseded by the Rev A fixes section below)
  | Part | Time | Filament | Layers |
  |---|---|---|---|
  | clip | 21m03s | 4.01 g | 77 |
  | cover | 24m16s | 7.99 g | 67 |
  | carrier | 9m57s | 1.48 g | 43 |

## Commands
```
cd housing/src
<venv python> build.py          # everything; exit 1 on any violation (--no-sweep / --no-render for quick runs)
<venv python> slice_check.py    # optional; writes out/slice/slice-report.json, which the next build.py folds into REPORT.md
```
The OCC font manager may leave a `src/00000.log` when "SCREEN" is engraved. It is harmless.

## Key results (out/checks.json)
1. **Seated vs the stock case.**
   - Designed contacts only: P1/P2/P3, lip and ear at gap 0.000.
   - Back-finger bumps 0.30 each, leaf bump 0.40.
   - Clearances: corner fingers 0.096, boss 0.315, spring bodies 0.15, rails and blocks 0.40.
2. **Insertion sweep, h 15 -> 0 in 0.25 steps, bisection-refined.**
   - No undesigned collisions.
   - (rev 0, superseded: rev A gives Z guided from h 10.27) Z guided from h 10.06 (back fingers) and 9.63 (front corner parts). X guided from h 7.31 (corner side parts).
   - Bumps ride the case from 8.74 (back) and 8.13 (leaf).
   - Pins cross the top face at 7.87 and touch J6 at 5.42..4.89.
   - Lip 3.77, ear 3.24, boss 1.40, pads 0.
3. **Pins vs J6.**
   - Tips at 107.94. Engagement 4.68..5.21 nominal, 4.03..5.64 worst (limits 3.68 / 6.00).
   - Wall clearance 1.165 nominal, 1.115 centred, 0.865 at full float (info).
   - Nearest metal to J6-12: 2.54.
4. **Optics keep-out.** Zero intrusion. The carrier walls lie on the boundary by design. The lip bottom is 0.665 above y_ko(7.6).
5. **Float extremes (±0.30 X/Z, 16 directions, seated and resting).**
   - Carrier/rod minimum 0.44. PCBA minimum 0.40 (J1 body to P3), with the designed contacts excluded.
   - The designed contacts behave: Y seat and float stop touch with no volume, tongue bumps ≤ 0.45.
6. **Printability.**
   - Clip: 0 overhang patches. Cover: 15, carrier: 2; all are bridge-width (≤ 1.05).
   - Undeclared minimum wall 1.0 on the cover and carrier; the clip has none below 1.0.
7. **Exports.** STL + STEP per part in print orientation, one 3MF plate, 5 PNGs, and the E-frame STLs + `assembly_E.step`.

**Springs.**

| Spring | k (N/mm) | Force | Strain |
|---|---|---|---|
| Back fingers | 8.64 | 2.59 N (0.43..4.75) | 0.54 % / 0.99 % |
| Leaf | 2.84 | 1.14 N (0.43..1.85) | 0.54 % / 0.88 % |
| Tongues | 2.92 | 0.44 N preload / 1.32 N full float | - |

Retention about 8.0 N, insertion about 8.8 N.

**Stack.** 115.60 + 2.80 + 3.00 = tail pad 121.40, tip 107.94. This matches M-spec 2d exactly.

## Deviations from DESIGN-SPEC (numbers)

**Tongues and pins**

1. **Centering tongues.**
   - They are full-height flexures, y 119.05..123.40, cut through the roof with U-slits. The contract has 1.5-tall floating tongues centred on y 119.4.
   - Reason: a mid-wall horizontal cantilever is an unsupported 8 mm overhang when the cover prints roof-down.
   - As built, k is 2.9 N/mm (audit 0.75), giving 0.44 N at preload and 1.3 N at full float. The pins bend about 0.05.
   - The tongue face sits 0.45 behind the PCB edge, with a 0.60 bump giving the 0.15 preload. This way the rigid root never touches the PCB at full float.
   - The bump stops at y 121.20, 0.40 under the roof. An earlier version welded the tongue to the roof; this is fixed and verified: the slit, slot and tip gap are empty.
2. **Carrier pins.**
   - Printed pins are impossible when the carrier prints flanges-down, as the contract requires.
   - (rev 0, superseded: rev A uses Ø1.5 x 4 ISO 8734 dowels in epoxy in Ø1.55 x 2.4 slip holes) The two datum pins are steel dowels, Ø1.5 x 3, pressed into Ø1.45 x 1.5 holes. They sit flush with the PCB top.
   - The 4 stake holes become CA/epoxy points. Heat-staking is dropped.

**Rod carrier**

3. **C-cradle mouth.** It faces -Y (away from the PCB). The datum hole at (-2.40, 16.00) sits directly above the rod end, so that material must be solid. Wrap 220 deg, bore Ø4.15, mouth chord 3.90.
4. **Socket depth.** 2.2, not 2.0. This gives 0.20 axial play per end and keeps 1.0 of end wall behind the socket.

**Clip**

5. **P3 pad and back-rail notch.** P3 z0 moves 0.6 -> 0.7 and the notch -5.70 -> -5.80, so the header body clears the clip by ≥ 0.40 at full float.
6. **Left leaf and corner finger.** The leaf is narrowed to b 5.0 (z -3.0..2.0), and the left corner-finger side part becomes z 2.5..4.2. In the M-spec they overlapped.
7. **Contract-forced thin walls (declared).**
   - C1 pilot in the P3 pad: 0.85 / 0.95.
   - C2 pilot to x 59.3: 0.90.
   - Dowel hole to the carrier end-wall inner face: 0.675.
   - Columns Ø3.6 / Ø2.3: 0.65.
   - Engraved-text ribs.
8. **Pilots.** They are through holes.
9. **Detail simplifications.**
   - Corner fingers are 1.5 thick.
   - Bump crests are a 0.2 flat.
   - The text is engraved.
   - Elephant-foot chamfers are left to the slicer.

**Cover**

10. **Roof and columns.**
    - Roof 1.8 thick, with the tail pad 0.20 proud at 121.40.
    - Column bosses Ø5.2 run down to 120.66.
    - Counterbores Ø4.4 x 1.0.
11. **Walls and envelope.**
    - Walls sit 0.75 off the PCB edges and are 2.0 thick in the back region.
    - Skirt inner face at z 20.35, 2.0 thick.
    - Front-region end walls at x -4.95 / 64.95.
    - Envelope x -6.55..66.55, z -8.95..22.35.

The full text of each deviation is in `src/build.py` DEVIATIONS and `out/REPORT.md`.

## Open / for later agents
- Docs (ASSEMBLY/BOM) should list the new parts: 2 x Ø1.5 x 3 steel dowels, CA/epoxy for the carrier, 3 x ST2.2 x 6 PT screws. Heat-staking is dropped.
- The J6 model's entries measure 1.04 at 0.1 below the face. The pins intersect the simplified contacts, so the model is only indicative (audit M4: measure a real part).
- Bench: fit coupon (lip, ear, bumps), the tongue force on a real print, and a 7-day spring check.

## Rev A fixes (review round 1)

Date: 2026-09-25. Source: `design/review-mechanical.md` (MAJOR-1..4, MINOR-5..8) plus the shared decisions. Only the
sources changed (`src/params.py`, `carrier.py`, `clip.py`, `cover.py`, `checks.py`, `build.py`, `render.py`). Every output
in `out/` was regenerated by `build.py`. The final build ran against `pcb/build/geometry.json` as regenerated by the
PCB fixer (19:13): 9 NPTH holes with C2 at (60.90, -2.54) and the +Z stake holes at z 18.30, and R1/R2 = CRCW0805200RFKEAHP.

### Shared decisions

| Item | Before | After |
|---|---|---|
| C2 column (cover) and pilot (clip) | x 61.00, z -2.54 | x 60.90, z -2.54 (C0 and C1 unchanged) |
| +Z glue / stake holes | z 18.40 (0.40 from the flange inner edge) | z 18.30 (0.30, which is exactly the glue-dam rebate width). The -Z holes stay at z 13.10. The datum holes stay at (-2.40 / 62.40, 16.00), dia 1.60. |
| R1/R2 200 R, J1 DNP at JLC | - | No housing change. The 0805 body boxes are the same. |

### MAJOR-1: rod datum and retention (new check 8)

**Cradle geometry**
- Bore centre: y 113.91 -> 113.835.
  - The crown is at y 115.91, so a rod pushed up onto the crown has its axis at y 113.910.
  - The gap to the LED faces (117.910, the lowest of the 10 LED boxes in geometry.json) is 2.000.
  - Before, the rod rode on the mouth edges: gap 1.925..2.264 depending on orientation, plus +-0.075 in z.
- Each side of each cradle is now a curved lip flexure:
  - 0.8 thick, rooted 56 deg above the equator, behind a 0.4 slot with a round end.
  - It stands free of both socket faces (0.4 gaps), so it is 1.4 long in x.
  - A hook of radius 1.84 about the rod axis, 4..12 deg below the equator, gives 0.160 interference.
  - The tip chord is 4.10, with a lead-in from below. Snap-through is 0.20 per lip (chord 3.60).
  - The mouth still faces -Y.

**Check 8 (measured on the solids)**
- Preloaded rod axis (113.910, 15.800) at both ends, against a target of (113.91, 15.80) +-0.05.
- Method: the rod is moved along +Y against the carrier minus its lips until manifold contact, by bisection.
- Interference 0.160 on all four lips, with contact at 11.3 deg below the equator. The L/R balance gives z 15.800.
- Retained in any orientation, because the snap chord (3.60) is smaller than the rod (4.0).

**Lip spring (curved arm, estimated as a straight cantilever over its 2.76 arc)**

| Quantity | Value |
|---|---|
| k | 17.0 N/mm |
| Force per lip | 2.74 N (2.54..3.39 for 0.15..0.20 interference) |
| Up force per end, frictionless | 0.76 N |
| Hold force per end at mu 0.3 | 2.39 N (rod weight 0.0097 N) |
| Strain | 2.5 % seated, 3.1 % at snap-through |

- The review's 0.8 x 1.5 flexure would reach about 8 % strain at 0.15, so the arm was made longer.
- The strain is below PETG's yield strain (about 4 %), but the preload will relax over time. Keep the epoxy dot on each rod end (review ASSEMBLY step 10) as the long-term retention.

**Walls around the lips**
- Carrier end walls: z 12.50..19.10 -> 12.00..19.60.
- -Z wall outer face: 12.50 -> 12.00. +Z wall outer face: 19.10 -> 19.60.
- Reason: otherwise the slots leave 0.025 slivers at the x -1.0 / 61.0 faces.
- The carrier's worst gap to the cover at full float is 0.443 (>= 0.40).
- The outer strip beside each slot is 0.525 and the dowel-hole floor over the crown is 0.30, both declared thin.
- Carrier volume: 1283 -> 1644 mm3 (about 2.1 g at x 1.27).

### MAJOR-2: centering-tongue bumps (new check 9)
- Every bump gets a 45 deg lead-in, 0.50 deep, at its bottom.
  - Full crest starts at y 119.55 (was 119.05).
  - At its bottom (y 119.05) the bump now stands 0.35 outside the PCB edge. Before, it was 0.15 inside, a square landing.
- Measured: with the PCB top 0.02 above the bump bottom, the overlap is 0.000 mm3 on all four tongues.
- The PCB edge first meets the flank at y 119.40.
- Full-crest contact band: 119.55..120.21 seated, 119.55..120.00 resting.
- Cover insertion onto the resting PCB:
  - The columns enter the holes at h 1.60.
  - The bumps touch the edge at h 0.60, on the flank.
  - The full crest reaches the edge at h 0.45.
- Tongue k 2.92 N/mm and preload 0.44 N are unchanged. The designed penetration stays <= 0.45 at full float.

### MAJOR-3: screws and pilots

| Item | Before | After |
|---|---|---|
| Clip pilots | dia 1.6 | dia 1.8 |
| Screw | ST2.2 x 6 | ST2.2 x 6.5 pan, DIN 7981 form / PT-class plastics thread-former |
| Screw tip | 116.40 | 115.90 (head seat 122.40) |
| Tip above the case top, C0 / C1 / C2 | - | 0.30 / 0.30 / 0.30 (checked) |
| Thread engaged | 2.0 | 2.5 at C0/C1; 2.4 at C2 (the tip ends 0.10 below the right-block underside at 116.0) |
| Cover column bore | 2.30 | 2.50 (wall 0.65 -> 0.55, declared; radial screw clearance 0.05 -> 0.15) |

**C2 pilot wall and header clearance**
- With the x move and dia 1.8, the C2 pilot wall to the header-notch face would have been 0.70 (it was 0.90).
- The notch face moved x 59.3 -> 59.2, so the wall is 0.80 (0.60 after thread forming).
- J1 body to the notch face: 0.728 nominal, 0.428 at full float (>= 0.40).
- C1 walls in the P3 pad: 0.85 / 0.95 -> 0.75 / 0.85.

**C2 column foot**
- Moving C2 brings the PCB hole edge 0.328 from the J1 body, so the column foot beside J1 was 0.332 away at full float.
- The foot now has a flat at x 59.20 below y 118.91. The float check passes, with J1 >= 0.40 from everything.
- The float stop keeps 1.3 of hole wall.

### MAJOR-4: grip
- Three grip ribs on each cover end face:
  - On the faces at x -6.25 / 66.25, z -6.5..1.5 (centred at -2.5 over the posts), y 119.1 / 120.5 / 121.9.
  - Each rib is 0.5 proud, with a flat underside (the finger catch) and a 45 deg top flank, so it prints roof-down.
  - The envelope grows in x from -6.55..66.55 to -6.75..66.75.
- Rear pull: a 0.6-deep fingernail ledge in the back wall.
  - Flat top face at y 121.4, 45 deg lower flank from 120.4.
  - x 3..18 and 30..57, clear of the back-tongue pocket.
  - Inside the envelope; 1.4 of wall remains.
- Nothing enters the keep-out (cover minimum gap 2.25). The cover is >= 2.9 above the case.

### Minors

**Dowels (MINOR-5)**

| | Before | After |
|---|---|---|
| Dowel | dia 1.5 x 3, pressed into dia 1.45 x 1.5 | dia 1.5 x 4 ISO 8734, set in epoxy in dia 1.55 x 2.4 slip holes, flush with the PCB top 120.21 |
| Wall to the end-wall inner face | 0.675 | 0.625 |

**Springs (MINOR-7): 1.4 -> 1.0 taper and R1.5 root fillets**

| Spring | Change | k (N/mm) | Force | Strain | Root stress |
|---|---|---|---|---|---|
| Back fingers | t 1.2 -> 1.4..1.0; R1.0 -> R1.5; b 10 -> 7.6 | 8.64 -> 8.69 | 2.59 -> 2.61 N (0.43..4.78) | 0.54 / 0.99 % -> 0.52 / 0.96 % | 10.8 -> 10.5 MPa |
| Leaf | t 1.2 -> 1.4..1.0; new R1.5 fillet; b 5.0 -> 3.8 (z -2.4..1.4) | 2.84 -> 2.77 | 1.14 -> 1.11 N | 0.54 / 0.88 % -> 0.51 / 0.83 % | 10.9 -> 10.3 MPa |

- Back fingers: now at x 4.2..11.8 and 44.8..52.4. The right finger moved out of the header notch, because its R1.5 fillet came 0.27 from J1. The back-rail outer face moved -8.05 -> -8.25 so it is flush with the 1.4 roots.
- At equal k the taper cannot halve the nominal root stress (the review's estimate). The gain is the lower stress concentration of the larger fillet.
- Retention 7.96 -> 7.97 N. Insertion stays 8.8 N.

**Edges (MINOR-8)**
- The back-finger and leaf bump crests are now R0.3 rounds. Their tops keep the 0.30 / 0.40 interference (check 1 depth 0.300 / 0.400).
- The clip lip's bottom inner edge is R0.5 instead of the 0.3 chamfer. It stays 0.665 above y_ko(7.6).

**Glue dams (MINOR-6, optional)**
- 0.3 x 0.3 rebates along both flange inner edges, x -1.0..61.0 (z 13.90..14.20 and 17.20..17.50).
- The flange is 0.7 there, declared.

### Gate results (final run)

`build.py` exit 0, `OVERALL PASS`.

| Check | Result | Key numbers |
|---|---|---|
| 1. Seated vs the stock case | PASS | Datums at 0.000. Bumps 0.300 / 0.300 / 0.400. Corner fingers 0.096, boss 0.315. |
| 2. Insertion sweep | PASS | 0 undesigned collisions. Z guided from h 10.27, X from h 7.31. Pins touch J6 at 5.42. |
| 3. Pins vs J6 | PASS | E 4.68..5.21. Wall clearance 1.165 / 1.115. |
| 4. Optics keep-out | PASS | 0 intrusion. |
| 5. Float extremes | PASS | Carrier/rod 0.443. PCBA 0.40 (J1 to P3, unchanged). |
| 6. Printability | PASS | Undeclared minimum wall: clip 1.015, cover 1.0, carrier 1.0. Overhang patches 0 / 15 / 16, all bridge-width (widest 0.957). Declared minimums: dowel floor 0.29, column 0.44 at the C2 flat, tongue 0.5. |
| 7. Exports | PASS | Includes the new render `section_cradle_x-2.1.png`. |
| 8. Rod datum | PASS | See MAJOR-1. |
| 9. Tongue lead-in | PASS | See MAJOR-2. |
| Stack and screws | PASS | Tip 107.94, tail pad 121.40. Screws as in MAJOR-3. |

Keep-out note: check 4 reports the clip 0.10 from the keep-out. That is the corner fingers' front parts at x -1.10 / 61.10, beside the x -1.0 / 61.0 keep-out ends, and it is unchanged from rev 0. The review measured 0.626 because its sections started at x -0.9.

### OrcaSlicer (re-sliced after the fixes)

Settings: Elegoo CC2, 0.4 nozzle, 0.20 Standard, PETG, 3 walls, 30 %, supports off. No warnings.

| Part | Time | Filament | Layers | Supports |
|---|---|---|---|---|
| clip | 21m03s | 3.95 g (was 4.01) | 77 | none |
| cover | 24m24s | 7.98 g (was 7.99) | 67 | none |
| carrier | 10m22s | 1.97 g (was 1.48) | 43 | none |

Superseded: the rev 0 "Open / for later agents" items above that name ST2.2 x 6 screws and dia 1.5 x 3 dowels.

### Open (for the docs and the bench)

**ASSEMBLY/BOM**
- 3 x ST2.2 x 6.5 PT screws.
- 2 x dia 1.5 x 4 ISO 8734 dowels in 5-minute epoxy.
- "Drill 2.4 through each column."
- Pre-form each pilot once with a spare screw.
- The rod snaps in from below, then gets an epoxy dot on each end.
- Remove the attachment by the two ends (grip ribs), never by the visor.

**Bench**
- Print a cradle coupon and check the snap and the preload on the lips.
