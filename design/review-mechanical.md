# Review: mechanical fit, assembly, optics as built (rev A)

J6 is the main board's expansion header and SW10 its power button (the right side key near the top). C0-C2 are the rev A
cover columns; D2/D9 are the light's own LEDs.

Status: COMPLETE 2026-09-25. 0 BLOCKER, 4 MAJOR, 5 MINOR.

Method: independent sections of housing/out/E/*.stl, pcb/production/3d/*_pcba_E.stl and the stock case
enclosures/silkscreen-enclosure-claude/out/{tub,lid}.stl. Sections are built by the reviewer from
trimesh.intersections.mesh_plane segments (linemerge + even-odd fill, shapely distances), 525 planes
(x -7..67, z -9.5..23, y 100..124, 0.25 step). Designed contact zones are masked before measuring the
undesigned gaps. Scripts: reviewer scratchpad meas.py / meas2.py (not in the repo). Not the builders' checks.py.

## Verified OK

- V1 Reproduced: `housing/src/build.py` (enclosure venv, cwd housing/src) exit 0, "OVERALL PASS in 195s", all 7 checks
  PASS, checks.json rewritten.
- V2 Seated vs stock case, independent: 0 undesigned intersections over 525 planes (clip, cover, carrier, rod, dowels,
  PCBA STL). Designed contacts measured at 0.000: P1, P2, P3 on the top face, lip on the front face, ear on the right
  side; back bumps and the left-leaf bump overlap the case (designed preload).
- V3 Five smallest undesigned gaps (clip is the only part within 0.5 of the case):
  1. 0.017 at (64.09, 111.0, z -3..3.25): the ear's inner face where the R5 corner starts to fall away (case x 64.074 at
     y 111.0). It is the continuation of the ear datum, not a new contact.
  2. 0.096 corner-finger front parts (z 6.10 vs case front 6.00), both sides, y 104..111.
  3. 0.100 corner-finger side parts (x -4.19 vs -4.09), y 107.4..110.6.
  4. 0.150 back-finger inner faces (z -6.85 vs back face -6.70), both fingers.
  5. 0.267 right corner finger at (64.0, 104.0, 5.03) against the front-edge radius; then 0.315 J6 boss to the opening
     wall (x 43..46, y 114.5, z -5.10).
  These match REPORT.md check 1 (0.096 / 0.15 / 0.315) to 0.001.

- V4 Engagement stack, measured from the STLs (vertex extremes): clip pads P1/P2/P3 min y 115.600; clip top 118.400;
  cover column bottoms 118.400 (C0/C1/C2 land on the clip top, so +2.800); cover tail pad 121.400 (+3.000, box x
  52.9..58.2 so the C2 boss shoulder at 120.66 is excluded); header from the PCB agent's PCBA STL: pins 5/6/11 each
  107.940..121.400, OAL 13.460 = datasheet .530 (.320 post + .100 body + .110 tail). Tip seated = 121.40 - 13.46 =
  107.94; engagement 5.21 / 4.99 / 4.88 / 4.68 against J6 faces 113.15 / 112.93 / 112.82 / 112.62 (window 3.68..6.00).
  Same as REPORT.md.
- V5 Pins in the case's J6 opening (reviewer y-sections of tub+lid, y 113.25..115.55, pins from the PCBA STL):
  nominal clearance 1.165 (y 115.35); worst with +-0.30 X/Z float 0.865 (dz +0.3). Meets >= 1.0 nominal.
- V6 Lip bottom y 110.000 (clip, z 6.05..7.55): 0.90 above the window edge 109.1. Keep-out (x -0.9..60.9, 0.25 step):
  no intrusion by clip / cover / carrier; minimum distance clip 0.626, cover 2.25, carrier 0.000 (its +Z wall inner
  face lies on the polygon edge z 18.10, as designed). A section exactly at x -1.0 / 61.0 shows the end-wall inner
  faces lying in the plane (3.4 mm2), a coincident-face artefact, not an intrusion.
- V7 Right side near SW10 (slot x 61.435..65.59, y 89.8..106.0, z -6.7..0.6): cover and carrier have no vertex below
  y 107 at x > 59. Only the clip's right corner finger (front part z >= 6.1, side part z >= 2.0) reaches down to y 103.0
  there, 1.4 clear of the slot's z 0.6 edge in z; the ear stops at y 107.0.
- V8 Optics nominal geometry as built: rod.stl axis y 113.910 z 15.800 (d 3.999, x -3.000..63.000); both cradles fitted
  from the carrier sections at x -2.2 / 62.2: bore centre (z 15.800, y 113.910), R 2.075 (155 pts), mouth chord 3.900
  at y 113.19, slot open through the end wall to its bottom (y 110.0), so the rod can go in from below after gluing.
  LED lowest faces in the PCBA STL: all ten at y 117.910 (= geometry.json emitter y; the 0.085 slab offset is only the
  board slab at 118.695). Nominal gap 117.91 - 115.91 = 2.000, dz 15.80 - 16.00 = -0.200. Carrier at x 30: -Z wall +
  flange z 12.0..14.2 down to y 113.91; +Z wall + flange z 17.2..19.3 down to y 110.0.

- V9 Centering tongues engage (cover vertices + sections against the builders' clean pcb.stl): all four crests stand
  0.150 inward of the PCB edges (left -3.35, right 63.35, back -6.05, front 19.45) and overlap the board both seated
  (17 section hits) and resting (14). Contact height y 119.05..120.21 seated.
- V10 Walls measured in reviewer sections: clip pilots C0 wall 2.20, C1 3.20 (0.85 only in the 0.4-tall P3 pad layer,
  y < 116.0), C2 0.90 over the full pilot; carrier dowel holes dia 1.45, wall 0.675 both ends; cover columns bore 2.30,
  wall 0.65 for y 119.0..120.66, 1.45 inside the boss.
- V11 Mass: clip 4.36 g, cover 8.56 g, carrier 1.63 g (solid volume x 1.27), rod 0.99 g, PCB 4.99 g, so about 21 g
  with the parts and screws. Orca at 30 %: 4.01 / 7.99 / 1.48 g. Envelope x -6.55..66.55, y 103.0..123.4,
  z -8.95..22.35. That is 7.8 above the case top, 16.35 in front of the front face (z 6.0), 2.25 behind the back and
  0.96 beyond the lid's sides.
- V12 The reader cannot see the rod or the LEDs. The rod bottom (111.91) sits 1.91 above both the lip bottom
  (z 19.1, y 110.0) and the skirt bottom (y 110.0). A sight line from any rod point clears the lip only when the eye is
  more than about 28 deg below the rod; normal reading is about 5..20 deg. The emitters (117.91) sit deeper still.
- V13 The assembly order works: dowels, glue, then the rod snaps in from below after the glue step (slot open through
  the end wall to y 110). Then the PCBA goes onto the clip and the cover goes on: the columns (bottom 118.40) enter the
  4.2 holes 0.65 before the tongue bumps (bottom 119.05) reach the resting PCB top (120.0). Then the screws. Nothing is
  trapped, and the counterbores are open from the roof.
- V14 The header load path is sound. The roof pad (121.40, x 52.9..58.2, z -5.6..0.5) bears on the three tail tips
  (1.19 above the PCB top), so the J6 insertion reaction goes pad -> pins -> J6 and never loads the solder joints.
  Short or trimmed tails: the PCB stops on the column-boss shoulders (120.66, 0.45 higher), so engagement stays
  >= 4.23 (> 3.68). A 0.3 solder cap on a tail gives 5.51 (<= 6.00). Removal loads the joints with only about 4 N.
- V15 Printability: the renders (iso front/back, front, J6 and rod sections) agree with the measured geometry. The Orca
  slices need no supports and give no warnings. The carrier prints mouth-up, and the mouth flanks are 0..20 deg from
  vertical (bore arc 70..90 deg from the crown), so they print without support.

## Findings

### MAJOR-1 (design/housing): the rod is neither held at the design axis nor retained
- Evidence:
  - The mouth faces -Y (DEV 4). Bore R 2.075 and mouth chord 3.900 at y 113.19 (measured on both cradles), so the
    snap is only 0.05 per side.
  - With the device upright, gravity is -Y and the rod rests on the two mouth edges. Its centre drops 0.264, to
    y 113.646, so the gap is 2.264 against the 2.0 +-0.1 contract (DESIGN-SPEC sec 4). Across orientations the rod
    moves between gap 1.925 and 2.264 (0.34 of rattle), plus +-0.075 in Z.
  - Optical effect: reviewer run of rod_lens.rev2(quick=True, at=(4.0, 2.264, -0.2)) from a scratch copy.
    - FT01C u2 goes from 5.48 to 6.16 (+12 %).
    - Flux goes from 0.090 to 0.0854 (-5 %).
    - Aim stays at 3.75 deg.
    - The builders' own tolerance row at gap +0.2 agrees: u2 6.33 vs 5.66.
  - Retention: a 1 g rod held by a 0.10 total snap in PETG (printed holes vary +-0.1) can pop out on a drop. Nothing
    catches it, because the space below the mouth opens straight onto the screen.
- Fix: datum the rod on the bore crown.
  - Move both cradle bore centres to y 113.835 (-0.075), so crown contact gives a gap of exactly 2.00.
  - Make each mouth lip compliant: a flexure about 0.8 wide x 1.5 long behind a 0.4 slot, with 0.15..0.20 interference,
    so the rod is preloaded up onto the crown.
  - ASSEMBLY step 10: after the snap, put a dot of 5-minute epoxy (not CA) on each rod end at the mouth.
  - Alternative: go back to the contract's +Y mouth and move the datum dowel off the rod end.

### MAJOR-2 (housing): the centering-tongue bumps have no lead-in along Y
- Evidence:
  - On all four tongues the crest runs y 119.05..121.20, starting at the tongue's bottom edge (cover vertices within
    0.02 of the crest).
  - The bump stands 0.60 and interferes 0.15 with the PCB edge (confirmed against pcb.stl).
  - As the cover is lowered, each bump's flat bottom lands square on the PCB top edge (120.0 resting). The cover hangs
    up, or the routed FR4 edge shaves the bumps and the preload is lost.
- Fix: add a 45 deg lead-in chamfer, 0.45..0.60, at the bottom of every bump, so the full crest starts at y >= 119.5.
  Contact stays over 119.5..120.21 seated. The chamfer is at the top of the roof-down print, so it prints cleanly.

### MAJOR-3 (housing/assembly): 2.0 mm of thread engagement and a tight pilot
- Evidence:
  - Screw stack: counterbore floor 122.400; the columns land on the clip at 118.400; pilots dia 1.6 run through
    115.6..118.4 (C0, C1) and 116.0..118.4 (C2).
  - An ST2.2 x 6 therefore ends at 116.40 with only 2.0 engaged (about 2.5 turns at P 0.8). A PT screw in plastic
    wants >= 2d = 4.4.
  - The pilot is 0.73 d, and vertical printed holes come out 0.1..0.15 small, so the forming torque is close to the
    stripping torque.
  - The C2 wall is 0.90 to the header-notch face x 59.3 (0.6 once the thread is formed). C2 is also the screw nearest
    the tail pad that carries the J6 insertion reaction, so a stripped C2 lets the roof lift and cuts engagement.
  - The column bore 2.3 against the screw's 2.2 major leaves 0.05 radial. An undersize print makes the screw cut into
    the 0.65 column wall.
- Fix:
  - Clip pilots dia 1.8 (0.8 d; prints about 1.65..1.7).
  - Specify ST2.2 x 6.5: tip 115.90, 2.5 engaged, still 0.30 above the case top (at C2, 0.10 below the block underside
    and 0.30 above the case).
  - Column bore dia 2.5, and add "drill 2.4 through each column" to ASSEMBLY.
  - ASSEMBLY: pre-form each pilot once with a spare screw and stop at head contact. Note that the heads stand 0.6 proud
    (k 1.6 in a 1.0 counterbore).

### MAJOR-4 (design/use): pulling the visor levers the posts in J6
- Evidence:
  - The cover reaches z 22.35, 16.35 in front of the case front face; the posts sit at z -3.81 / -1.27.
  - A pull on the front edge pivots about the back-finger line (z about -6.7). The lever is about 29 mm, against 3..5 mm
    to the posts.
  - Lifting the front 1 mm tilts the housing 2 deg, and the post tips (7.7 below the pivot) sweep about 0.27 mm
    sideways inside J6.
  - The PCB's 0.21 Y float over its 25.8 mm depth absorbs only about 0.5 deg.
  - The docs say "pull straight up", but the only natural grip is the visor, and the cover's end faces are smooth.
- Fix:
  - Add grip features on both cover end faces (x -6.55 / 66.55), centred at z about -2.5 over the posts: 3 horizontal
    ribs or a finger dimple. Optionally add a rear pull lip at z -8.95.
  - ASSEMBLY 7 and SAFETY: "remove it by the two ends, never by the visor; light off".
  - Install takes two hands: hold the reader and press about 9 N on the middle of the cover.

### MINOR-5 (housing/docs): the dowel press fit goes into a 0.675 wall
- Evidence: holes dia 1.45 (measured), wall 0.675 to the end-wall inner face at both ends. ASSEMBLY step 2 opens the
  hole to 1.4 and presses a 1.5 dowel in: 0.1 interference is about 7 % hoop strain, which splits or bulges the thin
  wall. The dowel can then lean and shift the carrier (dz budget +-0.1).
- Fix: make the hole a dia 1.55 slip fit (ream 1.5) and set the dowel in the same 5-minute epoxy. Or move the PCB
  datum holes and dowels to x -2.60 / 62.60 so both walls are 0.875.

### MINOR-6 (docs): glue can squeeze out into the channel
- Evidence:
  - The +Z glue holes (x 15 / 45, z 17.6..19.2) sit 0.4 from the flange inner edge (17.2) and 0.9 from the D2 / D9
    bodies (16.7).
  - The -Z holes (12.3..13.9) sit 0.3 from the flange inner edge (14.2).
  - Capillary flow along the flange/PCB crevice reaches the channel and can run down the optical lip face. The emitter
    faces are 0.7 below the board and stay clean.
- Fix: in ASSEMBLY step 6, apply a 0.5 mm bead with a pin, and cure with the channel facing down. Optionally add a
  0.3 x 0.3 glue-dam groove along both flange inner edges.

### MINOR-7 (housing): spring stress runs across the layers, and PETG creeps
- Evidence:
  - The back fingers and the leaf are Y cantilevers printed along the bed normal, so their root bending stress crosses
    the layer lines.
  - Stress is 10.8 MPa nominal and 19.8 MPa at 0.55 deflection (REPORT strain 0.54 / 0.99 %). PETG interlayer strength
    is about 25..35 MPa, and its long-term creep limit is about 10 MPa.
  - Result: the preload relaxes (spring friction is 3.79 N of the 7.96 N retention), and the root can delaminate after
    repeated fits.
- Fix: root fillet R1.5 (from 1.0), and taper each finger from 1.4 at the root to 1.0 at the tip, which roughly halves
    the root stress at the same k. Add a 20-cycle on/off test to the 7-day spring check.

### MINOR-8 (housing): the attachment can scuff the case face
- Evidence:
  - The lip (contact at z 6.0, 0.3 chamfer) slides 3.77 down the front face.
  - The back bumps ride 8.7 down the back face at 0.30 preload. Their crests are a 0.2 flat with sharp edges (DEV 12).
  - The corner fingers pass 0.096 off the front face at y 104..111.
- Fix: R0.3 edge breaks on the bump crests, R0.5 instead of the 0.3 chamfer on the lip bottom edge, and add a note on
  PTFE tape for painted cases.

### MINOR-9 (docs/tools): the rod_lens.py command line does not match its docstring
- Evidence: lines 31-32 advertise --rev2 [--quick] [--at D,gap,dz] [--name], but main() (lines 263-266) parses only
  --quick, so the command in the review brief cannot run.
- Fix: add --rev2, --at and --name to argparse and route them to rev2(quick, at, name=...).
