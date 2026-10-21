# Review: DFM, fab outputs, ordering, sourcing (rev A)

Reviewer: DFM/ordering subagent, 2026-09-25. Status: COMPLETE (sections 1-5 + findings F1-F9).

## 1. Fab outputs
Method: own regex parser of the Gerber X2 / Excellon files (scratchpad gp.py), not the builders' gates.
- VERIFIED zip content: 10 files only - F/B_Cu, F/B_Mask, F/B_Silkscreen, F_Paste, Edge_Cuts, PTH.drl, NPTH.drl
  (no B_Paste: correct, nothing on the back; no job file, no PDFs). PTH and NPTH are separate files.
- VERIFIED outline: 16 primitives, every endpoint shared by exactly two primitives (largest mismatch 1 nm, at
  X96.149999 vs X96.150000 on the left step - harmless). Bounding box 68.40 x 25.80 mm (x 95.80..164.20,
  y -80.40..-106.20); lower part 67.00 wide (steps of 0.70 each side at y -87.90). Arc radii present: R1.00 (4
  outside corners) and R0.35 (4 step fillets).
- VERIFIED drills: PTH = 3 x 1.020 (J1, ComponentDrill) + 3 x 0.300 vias (ViaDrill) - the brief's "3 PTH" omits
  the vias; NPTH = 6 x 1.600 + 3 x 4.200. J1 holes on a 2.54 grid, position (157.202,-101.27) empty (pos 4 omitted).
- VERIFIED annular ring: J1 1.70 pad / 1.02 drill = 0.34 mm; vias 0.60 / 0.30 = 0.15 mm (JLC 2-layer min via
  0.3 hole / 0.5 dia -> 0.10 ring: OK). Vias tented both sides (no mask flash). NPTH have no copper pad on either side;
  mask opening = drill + 0.10 (0.05 per side).
- VERIFIED paste: F_Paste has 20 LED + 6 SOT-23 + 4 R0805 apertures and nothing at the J1 PTH (correct for THT).
- MEASURED web hole-edge (min distance from hole wall to the routed outline, sampled arcs):
  1.6 dowel holes at (115,-81.6) and (145,-81.6): **0.401 mm** to the top edge; 4.2 hole at (161,-102.54):
  **0.400 mm** to the right edge; 1.6 at (97.6/162.4,-84): 1.000; all others >= 1.85. Min hole-hole web 1.39 (J1 pad
  hole to the 4.2 hole). Meets the spec's >= 0.3-0.4 only at the lower bound - see finding F1.
- MEASURED silk: F_Silkscreen strokes 0.150 (39) and **0.120 (34)** mm; B_Silkscreen 0.150 (399, text) and 0.200 (3).
  Both silk layers carry one clear-polarity block (mask openings subtracted) - normal KiCad behaviour.
- VERIFIED job file (not zipped, informational): 2 layers, 1.6 mm, finish "HAL lead-free", mask Black both sides,
  legend White. JLC ignores the job file; colour/finish must be selected on the order form.
- MEASURED silk text (pcbnew, visible text on silk layers): F "W" / "C" 0.80 h x 0.150 stroke; B "SILKSCREEN LIGHT
  ATTACHMENT" 1.00 h, "rev A 2026-09-25", "5", "6", "11", "SCREEN" 0.80 h, all 0.150 stroke. The 0.120 strokes are
  the stock KiCad footprint outlines of D11, D12 (8 each), R1, R2 (2 each), J1 (1) - no text below 0.150.

## 2. JLC assembly files
- VERIFIED format: jlc_bom.csv header `Comment,Designator,Footprint,JLCPCB Part #`; jlc_cpl.csv header
  `Designator,Mid X,Mid Y,Layer,Rotation` with "mm" units and Layer "Top" - both are the column names JLC's upload
  auto-maps. 15 CPL rows = 15 BOM designators (D1..D12, J1, R1, R2), all Top. CPL Y is negative (KiCad y-up export),
  the same sign convention as the Gerbers (outline Y -80.4..-106.2), so placements land inside the outline.
- VERIFIED rotations independently. EasyEDA API refetch from here is blocked (CloudFront 403 to curl), so I parsed the
  builder's saved raw API responses (pcb/docs/sources/ee_*.json: PAD records, 10-mil units, y down) myself and applied
  JLC's CCW-positive rotation to the EasyEDA pads, comparing against the pcbnew pad positions of the placed footprints:
  - LED C210340 "LED-SMD_L3.0-W1.4-RD": at 0 deg pad 1 = the LARGE pad (2.00 x 1.00) at x -1.05, pad 2 (1.20 x 1.00)
    at +1.05. KiCad D1..D10 orientation 180: pad 1 (1.91 x 0.92, cathode, nets W_K1/C_K1) at +0.73, pad 2 (anode,
    LED_SW) at -1.23. EasyEDA rotated 180 puts the large pad at +x = KiCad pad 1. CPL 180 is CORRECT (large pad =
    cathode in both; polarity not mirrored).
  - BAW56 C8663 "SOT-23-3_L2.9-W1.3-P1.90": at 0 deg pads 1 (+1.0,+0.95), 2 (+1.0,-0.95), 3 (-1.0,0) (pins 1/2 right,
    pin 3 left = KiCad SOT-23 at 180). KiCad D11/D12 orientation 90: pad 1 (-0.95,+0.94), 2 (+0.95,+0.94),
    3 (0,-0.94). Rotating EasyEDA by 270 CCW maps 1->(-0.95,+1.0), 2->(+0.95,+1.0), 3->(0,-1.0): matches. CPL 270
    CORRECT (KiCad 90 + 180).
  - R C313835 "R0805": pads 1 (-1,0) / 2 (+1,0); KiCad R1/R2 orientation 270: pad 1 top, pad 2 bottom; 270 maps
    EasyEDA pad 1 to top. CPL 270 CORRECT (non-polar anyway).
  - J1 C20382277: no EasyEDA footprint (builder got 404); CPL 0 is meaningless for a THT part that will be hand
    soldered or consigned - see finding on J1 below.
## 3. Sourcing (re-verified 2026-09-25)
JLC parts API (cart.jlcpcb.com getComponentDetail, fetched by me today; raw JSON in the review scratchpad):
| LCSC | Part | Stock | Class | Unit $ | JLC min / attrition |
|---|---|---|---|---|---|
| C210340 | HL-A-3014H421W-S1-08HL-HR3 2800-3100 K | 102,969 | extended | 0.0117 | 20 / +10 |
| C210343 | HL-A-3014H421W-S1-08HL-HR3 (cool) | 40,519 | extended | 0.0138 | 15 / +4 |
| C313835 | CRCW0805150RFKEAHP | 12,187 | extended | 0.0583 | 5 / +4 |
| C8663 | BAW56,215 SOT-23 | 43,296 | extended | 0.0314 | 5 / +5 |
| C20382277 | TSW-102-14-G-D-004 | **0** | extended, THT | 2.6958 | min purchase 4 |
- All five lines are "expand" (extended) - there are 4 extended SMT lines + J1, not "4 extended lines" in total.
- DigiKey (digikey.com, fetched today): CRCW0805150RFKEAHP = **541-150TCT-ND** (cut tape; 541-150TTR-ND reel,
  541-150TDKR-ND Digi-Reel), 40,101 in stock, $0.20 @1 - the builder's inferred number is CORRECT.
  BAW56,215 = **1727-2916-1-ND** (cut tape; confirmed by the DigiKey product URL .../BAW56215/1727-2916-1-ND/763453) - CORRECT.
  TSW-102-14-G-D = **612-TSW-102-14-G-D-ND**, 4,889 in stock, $0.83 @1, MOQ 1, active, 2-week factory lead - the
  BOM field holds "DK product 1102472", which is DigiKey's page id, not an orderable part number (finding F4).
## 4. JLC order constraints and cost
Sources: jlcpcb.com/capabilities/pcb-assembly-capabilities and /help/article/pcb-assembly-price (fetched 2026-09-25).
- Service: **Economic PCBA** (single board 10x10..470x500 mm; 68.4 x 25.8 qualifies). Standard PCBA needs >= 70 x 70
  (would force a panel with rails). Economic: edge rails / fiducials / tooling holes "Not necessary" -> order single
  boards, no panel, no fiducials needed. Thickness 0.8-1.6 mm (1.6 OK). All 15 parts are Top (F) = single-side.
- Mask: JLC lists Green/Purple/Red/Yellow/Blue/White/Black; no matte black is listed (spec sec "matte if JLC offers
  it" -> it does not; order gloss Black). Economic PCBA has a restricted colour set - confirm Black is selectable for
  2-layer Economic on the form; if not, the fallback is Standard PCBA with a 1 x 3 panel + 5 mm rails, 3 fiducials,
  2 mm tooling holes (+$17 setup, +$6.7 stencil). No colour surcharge on 2-layer, +1-2 days build.
- Finish: 0.43 mm is the smallest copper gap (warm/cool pad pairs) vs JLC 0.15 min, so LF-HASL is electrically fine;
  ENIG recommended for pad flatness (LED seat height/tilt feeds the +-0.1 rod-to-LED target). See F9.
- Fees (Economic): setup $8.18, stencil $1.53, extended-part feeder loading $3.07 x 4 SMT lines = $12.28, SMT joints
  150 (30/board) x $0.0016 = $0.24, parts incl. JLC minimums/attrition ~$2.1 (35 warm, 29 cool, 14 R, 15 BAW56).
  THT hand soldering if JLC fits J1: $3.58 labour + 15 joints x $0.0164 + the part (global sourcing, >= 4 pcs at ~$2.70).
- Estimate, 5 boards, J1 DNP: PCB ~$2 + LF-HASL ~$1 (ENIG instead: roughly +$10-16, check quote) + PCBA ~$24.3
  = **~$27 (LF-HASL) / ~$40 (ENIG)** before shipping and duties; plus 6 x 612-TSW-102-14-G-D-ND ~$5 at DigiKey.

## 5. BOM completeness
Electrical: complete (D1-D10, D11-D12, R1-R2, J1), every line has MPN + LCSC; DigiKey filled except LEDs (Hongli,
no DigiKey listing - LCSC-only is acceptable; order by LCSC code because both CCTs share one MPN).
Mechanical (spec sec 5 + housing REPORT deviations), proposed purchasable items:
| Item | Qty/unit | Proposed buy | Note |
|---|---|---|---|
| PMMA rod, clear, 4.0 x 66.0 | 1 | cast acrylic rod 4 mm x 500 mm (Amazon/AliExpress "4mm clear acrylic rod", or a plastics stockist e.g. TAP Plastics / Kunststofshop), cut + polish ends | cradle bore 4.15 / mouth 3.90 -> ask for dia tolerance <= +-0.05; reject rods > 4.10 |
| Steel dowel 1.5 x 3 | 2 | ISO 8734 / ISO 2338 d1.5 is stocked from L = 4 (Misumi MSTH/MS configurable, McMaster metric dowel pins) | see F7 |
| ST2.2 x 6 plastic thread-forming | 3 | EJOT PT K22x6 (WN 5411) or ISO 7049 ST2.2 x 6.5 pan (AliExpress/Bossard) | 6.5 is the ISO length - check the pilot depth |
| Adhesive for the 4 stake holes | - | medium CA (Loctite 401) or low-bloom CA (Loctite 460) | see F8 |
| PETG, black matte | ~15 g | any matte black PETG filament (e.g. Prusament PETG Jet Black / Polymaker PolyLite PETG) | |
| Optional M2 x 12 + screw-lock tab | 1 | ISO 7380 / DIN 912 M2 x 12 | spec 3d |

## Findings (appended as found)

### F1 MAJOR (pcb) - 0.40 mm hole-to-edge webs are at the fab's routing tolerance
Evidence: own Gerber/Excellon parse: NPTH 1.6 at (115,-81.6) and (145,-81.6) (carrier stake pins, +Z flange, spec
(15.00,18.40)/(45.00,18.40)) leave 0.401 mm of FR4 to the top edge y -80.4; NPTH 4.2 at (161,-102.54) (column C2, spec
(61.00,-2.54)) leaves 0.400 mm to the right edge x 163.5. JLC capabilities page (jlcpcb.com/capabilities/pcb-capabilities,
2026-09-25): routed outline tolerance +-0.2 mm (regular), +-0.1 mm (high precision); JLC publishes no hole-to-edge
minimum. Worst case the web is 0.2 mm (plus drill position error) - it can crack or break out during routing, and a
0.2 mm sliver next to a 1.5 mm dowel / PETG column is not a reliable retaining wall.
Fix: move the two stake holes to z 18.30 (web 0.50) or extend the top edge by 0.2 (check clip/cover clearance with
the housing builder), and move C2 to x 60.90 (web 0.50) with the matching housing column; if the positions are
frozen, order "outline tolerance +-0.1 mm (high precision)" and accept a possible break-out (a notch still locates).

### F2 MINOR (pcb) - silk text 0.80 mm and 0.12 mm outline strokes are below JLC's legend minimums
Evidence: pcbnew text dump: F "W","C" and B "rev A 2026-09-25","5","6","11","SCREEN" are 0.80 mm high (0.150
stroke); D11/D12/R1/R2/J1 outline strokes 0.120 mm (34 draws in F_Silkscreen, aperture C0.120). JLC capabilities
page: legend line width >= 0.15 mm, text height >= 1.0 mm. The 5/6/11 labels are the hand-solder orientation cue for J1.
Fix: in tools/params.py / the footprint generator set silk line width 0.15 for the SOT-23, 0805 and J1 footprints
and text height 1.00 (stroke 0.15) for all silk text, where it fits (the "W"/"C" letters can stay 0.8 if space-bound:
they are cosmetic).

### F3 MINOR (pcb) - concave R0.35 step fillets depend on JLC's router bit
Evidence: Edge_Cuts arcs: concave R0.35 at (96.15,-88.25) and its mirror (needs a <= 0.7 mm cutter); JLC does not
publish its routing bit size, and inner corners come out at the cutter radius (commonly R0.5 with a 1.0 mm bit).
With R0.5 the concave corner keeps up to ~0.06 mm more FR4 at the 45-deg point than modelled.
Fix: none required if the housing end walls clear the step by >= 0.2 mm; otherwise add an order remark "inner
corners R0.35, 0.7 mm router" or relieve the housing corner by 0.15 mm.

### F4 MINOR (docs) - J1 DigiKey field is a page id, not a DigiKey part number
Evidence: production/bom.csv J1 row "DK product 1102472 (TSW-102-14-G-D; pull position 4)"; DESIGN-SPEC line 65 same.
DigiKey product page 1102472 lists the orderable number 612-TSW-102-14-G-D-ND (4,889 in stock, $0.83).
Fix: DigiKey field = "612-TSW-102-14-G-D-ND (TSW-102-14-G-D, push out position 4 before soldering)" in params.py,
bom.csv and DESIGN-SPEC sec BOM; mark R1/R2 541-150TCT-ND as verified (PROGRESS.md deviation 6 / Left-open).

### F5 MAJOR (docs/ordering) - J1 cannot go through JLC as generated; order path
Evidence: JLC API today C20382277 stock 0, assemblyProcess THT, min purchase 4; jlc_bom.csv still lists J1 with
C20382277 and jlc_cpl.csv places it at rotation 0 with no EasyEDA footprint. The board has NO hole at position 4
(own drill parse: (157.202,-101.27) empty), so a stocked TSW-102-14-G-D only fits after pin 4 is pushed out - JLC will
not modify parts, and JLC hand soldering does not hold the post height/perpendicularity that the E-frame tip
positions (Y 107.94 / 121.40) rely on.
Fix: make_outputs.py drops J1 from jlc_bom.csv and jlc_cpl.csv (or emits it marked DNP) so the JLC upload has only the
14 SMT placements; ORDERING.md: "J1 DNP at JLC; buy 612-TSW-102-14-G-D-ND (or Samtec samples of TSW-102-14-G-D-004),
push out position 4 with pliers, hand-solder with the posts mated into a 2x6 female 2.54 header used as a jig, then
go-gauge". JLC THT hand soldering ($3.58 + $0.0164/joint, Economic) exists but only as a fallback via global sourcing
of the exact -004.

### F6 MINOR (pcb) - EasyEDA LED footprint origin is 0.20 mm off the land-pattern centre
Evidence: ee_C210340.json pads (2.00 at -1.05, 1.20 at +1.05) have extents -2.05..+1.65 about the EasyEDA origin
(centre -0.20); the KiCad land (1.91 / 0.55 / 0.91, datasheet B-17-A-1548 p.2, pin 1 = cathode = large pad, confirmed
on the page image) is symmetric +-1.685 about the CPL point. At rotation 180 JLC's preview will draw the EasyEDA
pads ~0.2 mm toward the cathode side of the Gerber pads. Polarity is right (section 2).
Fix: no file change; ORDERING.md: "in JLC's placement preview the LED outline may look 0.2 mm shifted; the CPL point is
the body centre - do not accept an operator 'correction' that moves it; confirm the cathode mark sits on the large pad".

### F7 MINOR (design/housing BOM) - Ø1.5 x 3 dowel is not a stocked ISO length
Evidence: housing/out/REPORT.md deviation 3: dowels Ø1.5 x 3 (ISO 8734) pressed 1.5 into the carrier, flush with the PCB
top (1.5 + 1.6 = 3.1). ISO 8734 / ISO 2338 list d1.5 from L = 4 mm (Misumi/McMaster configurators); a 3 mm pin is a
cut or special part.
Fix: specify Ø1.5 x 4 (ISO 8734, m6) and deepen the carrier press holes to 2.4 mm so the pin stays flush (or accept a
0.9 mm protrusion vs the 1.39 roof clearance); BOM line with a Misumi/McMaster part.

### F8 MINOR (docs) - CA vapour will fog the PMMA rod
Evidence: REPORT.md deviation 3 uses CA/epoxy through the four 1.6 stake holes onto carrier flanges that sit 2.6 mm
(z 13.10 / 18.40 vs rod axis z 15.80) from the clear PMMA rod; CA blooms white on nearby surfaces and can craze acrylic.
Fix: ASSEMBLY.md: glue the carrier with the rod removed (the cradle snaps from below at any time), use a low-bloom CA
(Loctite 460) or 5-min epoxy, vent 24 h, then snap the rod in.

### F9 MINOR (docs/ordering) - finish and mask must be chosen on the form; recommend ENIG + gloss black
Evidence: job file (not uploaded by JLC) says "HAL lead-free", mask Black; JLC offers no matte black (capabilities page);
LED coplanarity matters for the rod-to-LED +-0.1 target and HASL crowns vary tens of um.
Fix: ORDERING.md form fields: 2 layers, 1.6 mm, 68.4 x 25.8, qty 5, Black mask, White silk, ENIG 1U" (LF-HASL acceptable),
Economic PCBA, Top side, 5 assembled, "Confirm parts placement: yes", J1 DNP; board has no castellation or panel.
