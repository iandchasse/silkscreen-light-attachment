# Electrical review (independent) - COMPLETE

Reviewer: electrical / schematic / polarity / handedness. Started 2026-09-25.
Status: complete; see Summary at the end.

## Method
Own pcbnew dump of every pad/net (scratch dump.py), own regex parse of the .kicad_sch lib_symbols and instances,
Hongli datasheet p2 (pcb/docs/sources/HL-A-3014H421W_datasheet_p2.png, zoomed crop of the pin symbol),
EasyEDA JSON for C210340 / C210343 / C8663 parsed for pad numbers/positions (units 10 mil).

## VERIFIED 1 - topology (own pcbnew parse, every pad)
- Warm: J1-5 /LED_SW -> D1.2(A) | D1.1(K)=/W_K1 -> D2.2 | D2.1=/W_K2 -> D3.2 | D3.1=/W_K3 -> D4.2 | D4.1=/W_K4 -> D5.2 | D5.1=/W_R -> R1.1 | R1.2=/N_W -> D11.3 (CA) ; D11.1 (K1) = /W- = J1-6 ; D11.2 (K2) = /LED_SW. OK.
- Cool: /LED_SW -> D6.2 | D6.1=/C_K1 -> D7 -> D8 -> D9 | D10.1=/C_R -> R2.1 | R2.2=/N_C -> D12.3 ; D12.1 = /C- = J1-11 ; D12.2 = /LED_SW. OK.
- D1-D5 LCSC C210340 (3000 K, W- string); D6-D10 LCSC C210343 (6000 K, C- string). OK.
- Nets present: '', /C-, /C_K1..4, /C_R, /LED_SW, /N_C, /N_W, /W-, /W_K1..4, /W_R - no stray nets; the 9 NPTH have no net; 3 vias all /LED_SW.

## VERIFIED 2 - LED polarity (three independent views agree)
- Datasheet p2 symbol (zoomed): "1 o--|<|--o 2": the bar is on pin 1, triangle points at pin 1 -> pin 1 = CATHODE, pin 2 = anode.
- Datasheet p2 bottom view: pin 1 electrode 1.68 mm (big), pin 2 0.78 mm, gap 0.55; land pattern 1.91 / 0.55 / 0.91 x 0.92. Top view: chamfered corner on the pin-1 end.
- EasyEDA C210340 (LED-SMD_L3.0-W1.4-RD): pad 1 = 2.00 mm wide at -1.05 mm, pad 2 = 1.20 mm at +1.05 mm. EasyEDA C210343 (LED3014-RD): pad 1 = 2.00 mm at -1.015, pad 2 = 1.00 mm at +1.015, outline chamfer at the pad-1 end. Both LCSC codes: pad 1 (big) on -X at 0 deg.
- KiCad footprint: pad 1 = 1.91 x 0.92 (big) at local -0.73, pad 2 = 0.91 x 0.92 at local +1.23 (span +-1.685, origin = body centre). Symbol LED_3014: pin 1 name K, pin 2 name A. So symbol K -> pad 1 -> big pad -> datasheet cathode. OK.
- Placement: KiCad 0 deg and EasyEDA 0 deg both have pad 1 on -X -> offset 0; CPL 180 = KiCad 180. After JLC places, cathode (big pad) lands at board X = centre + 0.73, which is the pad the netlist calls K (e.g. D1.1 at 101.83 = /W_K1). OK.

## VERIFIED 3 - BAW56 pinning / rotation
- Symbol BAW56: pin 1 K1, pin 2 K2, pin 3 CA (= Nexperia pinning 1 K1, 2 K2, 3 common anode).
- KiCad SOT-23 local: pads 1,2 at x=-0.94 (1 at y=-0.95, 2 at +0.95), pad 3 at +0.94 (standard: pin 3 up -> 1 bottom-left, 2 bottom-right; confirmed on the board at rot 90: pad 3 y=100.812 top, pad 1 x=131.55 left, pad 2 x=133.45 right).
- EasyEDA C8663 (SOT-23-3_L2.9-W1.3-P1.90): pad 1 (+1.0,+0.95), pad 2 (+1.0,-0.95), pad 3 (-1.0,0) = KiCad rotated 180 exactly -> offset +180; CPL 270 = 90 + 180. OK.

## VERIFIED 4 - handedness / J1 position
- Mapping x_K = X+100, y_K = 100-Z. KiCad 3D frame (x3 = x_K, y3 = -y_K, z3 = out of F.Cu). E = (X, Y, Z) = (x3-100, -z3+c, y3+100): matrix [[1,0,0],[0,0,-1],[0,1,0]], det = +1 -> proper rotation (+90 deg about X), NOT a mirror, iff F.Cu faces -Y. OK.
- J1 pads (own pcbnew parse): 5 at (154.662,103.810) -> E (54.662,-3.810); 6 at (157.202,103.810) -> (57.202,-3.810); 11 at (154.662,101.270) -> (54.662,-1.270). J1 is on F.Cu, only 3 pads (pad 5 square = pin-1 mark), drill 1.02, pad 1.70.
- No pad/hole at J6-12 (157.202,101.27) (nearest copper = J1-6/J1-11 pads at 2.54 mm) and none at J6-4 (152.122,103.81) (nearest: /W- F.Cu 0.4 mm track at y=105.3, 1.29 mm edge distance, masked, and J1-5 at 2.54 mm). No zones on the board.
- E-frame STL (own trimesh parse): lowest geometry (post tips) at Y=107.94, board F face at Y=118.69 -> posts point -Y, 10.75 mm long (TSW .100 body + .320 post = 10.67). Tip squares 0.64 mm centred at (54.662,-3.81), (57.202,-3.81), (54.662,-1.27). Zero vertices in the 0.4 mm columns at J6-12 and J6-4. D1 body at E (1.1,16) occupies Y 117.91..118.61 (on the -Y face). OK.
- Silk: B.Silkscreen '5' (153.41,105.31), '6' (158.6,105.31), '11' (152.56,101.27) sit next to the right pads; F.Fab 5/6/11 on the pads plus "no pin (J6-12)" X-mark. OK.

## VERIFIED 5 - rule honesty
- .kicad_pro: "drc_exclusions": [], "erc_exclusions": [], no "ignore" severity anywhere (grep). .kicad_dru has one extra rule only (track-to-NPTH hole_clearance 0.5 mm, a tightening).
- Own re-run (kicad-cli 9, --severity-all, --schematic-parity) into scratch: ERC 0 violations; DRC 0 violations, 0 unconnected, 0 parity issues.

## VERIFIED 6 - main-board J6 nets (own pcbnew parse of de-link_pcb/silkscreen_pcb.kicad_pcb)
J6 (PPPC062LJBN-RC, B.Cu): 4 GND, 5 LED_SW, 6 W-, 11 C-, 12 /P+_FUSE; pin 6 = pin 5 + 2.54 x, pin 11 = pin 5 - 2.54 y (row B).
Q5 drain = W-, Q6 drain = C-, both sources to R37 15 R. D3 SMAJ26A LED_SW-GND, D8 PESD2IVN on W-/C-. Matches the accessory's net names.

## VERIFIED 7 - voltage / current window (own numbers from the Hongli datasheet)
Datasheet p3: VF 2.7-3.3 V at IF = 30 mA (+-0.1 V measuring tolerance). p4: IF 40 mA, IFP 80 mA (0.1 ms, 1/10 duty), VR 5 V, Pd 132 mW, ESD 1 kV HBM.
p5 IV curve (typ): 2.72 V at 10 mA, 2.90 V at 20 mA, 2.97 V at 30 mA, ~3.13 V at 60 mA -> Vf(14 mA) = Vf(30 mA) - 0.18 V; r_d 5-7 R above 20 mA.
String current 13.33 mA nom / 13.96 mA max. Rs drop 150 R x 13.96 mA = 2.09 V.
- Max (cold -10 C, max bin): 5 x (3.30-0.18+0.105) = 16.13 V + 2.09 + BAW56 0.95 + VFB 0.206 + Q 0.14 = 19.5 V (20.0 V adding the +0.1 V measuring tolerance; 20.9 V even if 3.3 V is applied at 14 mA with no curve credit). All < 22.0 V ceiling, >= 3.3 V under OVP min 24.25 V. Builders: 19.66 V. OK.
- Typ: 5 x 2.79 + 2.00 + 0.78 + 0.20 + 0.13 = 17.1 V (builders 17.31). Min hot: ~15.6-15.9 V. OK.
- Hold-off: even at 2.2 V/LED (uA, 65 C) 5 x 2.2 + 0.4 = 11.4 V >> 6.5 V (5.5 V VIN + 1 V); one shorted LED still 9.2 V. OK.
- Hot-plug, TPS923610 (C9 at 25.5 V), loop R37 15 + 2 + 150 + 5 x 5.3 = 193.5 R, knee 5 x V0 (V0 = Vf30 - 30 mA x 5.3 R = 2.54 min / 2.81 typ) + 0.8 V diode: (25.5-12.7-0.8)/193.5 = 62 mA min bin, 55 mA typ. < IFP 80 mA. OK (reproduces 52-64 mA).
- Rs pulse: 62 mA^2 x 150 R = 0.58 W for tau 0.5-0.9 ms (C9 2.5-4.7 uF x 193 R). CRCW0805-HP single-pulse curve (crcwhpe3.pdf p5): ~20 W at 1 ms, ~6 W at 10 ms -> > 10x margin (even the 611 misinsertion case ~1.5 W). Continuous 29 mW vs 0.5 W. OK.
- BAW56: VR 90 V vs 25.5 V (610) / 31.4 V (611) reverse in shift/rotation cases; IF 215 mA vs <= 100 mA. OK.

## VERIFIED 8 - misinsertion re-run against the ACTUAL pads (own enumeration script)
Contacts from the PCB: a = J1-5 (col 5, row A), w = J1-6 (col 6, row A), c = J1-11 (col 5, row B); no other copper.
Accessory model from the netlist: only forward paths are a->w (warm) and a->c (cool) through 5 LEDs + Rs + BAW56 K1; w->a, c->a, w<->c are blocked by a K1 (VR 90 V); K2 clamps the LEDs' reverse voltage to one diode drop.
64 distinct placements (rot 0/180 x column mirror x row offset -1/0/+1 x column shift -6..+6):
- Correct LED_SW/W-/C-: normal. Rot180+mirror+row-1: LED_SW/W-/air: normal (warm only).
- Every placement with LED_SW under w or c: reversed, blocked by K1 (25.5 V / 31.4 V vs VR 90 V). Everything else: forward <= 4.2 V (P+) or 3.3 V, below the ~11 V knee: inert. No placement puts a on LED_SW with w/c on 3V3, I2C or a strap GPIO.
- Exactly 2 hazardous placements, same as research sec 5: mirror + shift -1 (LED_SW / GND(4) / C-) and rot180 + row-1 + shift -1 (LED_SW / GND(4) / air). With 150 R and TPS923610: (24.25..25.5 - 5 x V0 - 0.8)/(150 + 26.5) = 43-68 mA, 1.0-1.7 W from a boost that can deliver ~3.7 W -> reaches OVP and latches in ~ms: bounded. Both need the header on the wrong face or the housing absent.

## VERIFIED 9 - part identities (cached LCSC/JLC JSON) and silk polarity
C210340 = HL-A-3014H421W-S1-08HL-HR3 "Color Temperature 2800-3100K", 3000 K; C210343 = same MPN, 6000 K; C8663 = Nexperia BAW56,215 common anode SOT-23; C313835 = Vishay CRCW0805150RFKEAHP 150 R 500 mW; C20382277 = Samtec TSW-102-14-G-D-004 (stock 0).
LED F.Silkscreen cathode mark: two bars x 101.225..102.735 over D1 pad 1 (101.83) = cathode side; same on D5, D6. LED Description fields carry CCT + LCSC code. OK.

## FINDINGS

### F1 MINOR (docs/pcb) - R2 footprint fields out of sync with the schematic
Evidence: own pcbnew read of the .kicad_pcb: R2 Description = "Resistor", Datasheet = "~"; R1 on the PCB and R2 in the .kicad_sch both carry "150 R 1 % 0.5 W pulse-proof thick film 0805 (CRCW-HP); string series resistor" and https://www.vishay.com/docs/20043/crcwhpe3.pdf. kicad-cli --schematic-parity does not compare these fields, so the gate passes.
Fix: in the PCB generator (tools/build_pcb.py / generate.py) copy Description and Datasheet from the schematic for every footprint (or Update PCB from Schematic with "Update other fields"), then re-run make_outputs.

### F2 MINOR (docs) - DigiKey fields: LEDs empty, J1 not a DigiKey part number
Evidence: schematic D1-D10 DigiKey = "" ; J1 DigiKey = "DK product 1102472 (TSW-102-14-G-D; pull position 4)" - a web product id for the 4-pin part, not an orderable DigiKey PN, and not the -004 MPN. The project rule is DigiKey-primary with LCSC as an extra field.
Fix: LEDs: DigiKey = "n/a - not stocked by DigiKey; order by LCSC C210340 / C210343" (explicit, not blank). J1: put the real DigiKey PN of TSW-102-14-G-D from product page 1102472 and say "pull pin 4 (J6-12) by hand" or "order -004 from Samtec direct".

### F3 MINOR (design) - TPS923611 main-board variant drives the LEDs past IFP; DESIGN-SPEC is silent on it
Evidence: de-link_pcb/README.md:235-245 makes U10 TPS923611DRLR (+ D3 SMAJ33A) the official swap when the TPS923610 is out of stock; OVP 29.6-31.4 V. Own calc, C9 at 31.4 V, loop 193.5 R, knee 12.7-14.05 V + 0.8 V: hot-plug peak 85 mA (typ bin) - 92 mA (min bin), tau 0.5-0.9 ms; misinsertion LED_SW->GND(4): (31.4-12.7-0.8)/176.5 = 101 mA until the latch. Hongli p4: IF 40 mA, IFP 80 mA at 0.1 ms / 1:10 only. pcb/PROGRESS.md:31 records "TPS923611: 78-96 mA, over IFP" yet the verdict is PASS; DESIGN-SPEC.md has no 611 line.
Fix (pick one, record it in DESIGN-SPEC): (a) R1/R2 -> 200 R CRCW0805200RFKEAHP: 611 hot-plug (31.4-13.5)/243.5 = 73 mA < 80, misinsertion 79 mA; 610 worst V_OUT 19.66 + 0.70 = 20.36 V (20.9 + 0.7 = 21.6 V with no curve credit) still < 22.0 V; or (b) keep 150 R and state in the user guide "on a TPS923611 board, switch the frontlight off before plugging the light in".

### F4 MINOR (pcb/assembly) - JLC library origin of both LED codes is 0.2 mm off the body centre
Evidence: EasyEDA C210340 (LED-SMD_L3.0-W1.4-RD): pads at -1.05 (2.00 wide) / +1.05 (1.20 wide), origin = pad-centre midpoint, outline centre -0.19 mm, gap centre +0.20 -> body centre ~0.2-0.25 mm toward pad 1. C210343 (LED3014-RD): pads -1.015 (2.00) / +1.015 (1.00), outline centre -0.18 mm. The KiCad footprint origin = body centre (lands span +-1.685), and jlc_cpl.csv gives that point. If JLC drops its library origin on the CPL point, the body sits ~0.2 mm toward the cathode: the 0.78 mm anode electrode then covers only ~62 % of the 0.91 mm anode land and starts over the 0.55 mm land gap (tombstone/skew risk).
Fix: in the JLC placement preview confirm every LED body is centred on its two lands and ask JLC to nudge if not (do not blindly edit the CPL); optionally add a note to pcb/PROGRESS.md / ordering notes. Rotation itself is right (offset 0 LEDs, +180 BAW56).

## VERIFIED 10 - BAW56 datasheet and distributor numbers
Nexperia BAW56 datasheet (scratch baw56.pdf) Table 2: pin 1 K1 cathode (diode 1), pin 2 K2 cathode (diode 2), pin 3 CA common anode = symbol and footprint mapping. VRRM = VR = 90 V; IF 215 mA single / 125 mA per device; IFRM 500 mA; IFSM 4 A (1 us), 1 A (1 ms), 0.5 A (1 s). VF <= 1.25 V at 150 mA.
DigiKey 1727-2916-1-ND = Nexperia BAW56,215 cut tape (web search: digikey.com.au product-detail .../BAW56215/1727-2916-1-ND/763453). OK.
DigiKey 541-150TCT-ND for CRCW0805150RFKEAHP: my web search did not confirm or deny it. Check it on digikey.com before ordering; the MPN and LCSC C313835 are confirmed.

## Summary
No BLOCKER and no MAJOR. Topology, LED polarity (three independent views agree: pad 1 = big pad = cathode = symbol K), BAW56 pinning and the +180 offset, handedness (det +1, F.Cu -Y, post tips at the J6-5/6/11 X/Z, nothing at J6-4/J6-12), voltage window, hold-off, TPS923610 hot-plug, Rs pulse rating, BAW56 ratings, misinsertion (64 placements: 2 hazardous, both bounded) and rule honesty all verified independently.
Minor findings: F1 R2 PCB fields out of sync; F2 DigiKey fields (LEDs blank, J1 not a PN); F3 TPS923611 variant goes past the LED IFP and DESIGN-SPEC does not cover it; F4 JLC library origin 0.2 mm off the LED body centre, so check the placement preview.
Status: COMPLETE (2026-09-25).
