# LED choice (Rev 2): LCSC-stocked warm + cool pair

Status: done 2026-09-25. This replaces the Lumileds LUXEON 3014 (L130-3090001400001 / L130-5790001400001), which LCSC
does not stock. The optics re-run for this LED is in `design/optics-final.md`, "Rev 2 - LCSC LED pick".

Stock, price and JLC class come from the JLCPCB parts API (the same data as jlcpcb.com/partdetail/<C#>), queried
2026-09-25. Datasheets come from lcsc.com/datasheet/<C#>.pdf (the file behind it is on datasheet.lcsc.com). Page numbers
refer to those PDFs.

## 1. Requirements (from the brief and research/electrical-j6.md)
- Top-view white LEDs in one family and one footprint: warm 2700-3500 K and cool 5000-6500 K.
- LCSC stock in the thousands or more; JLC Basic or Extended.
- IF >= 20 mA continuous. IFP >= 80 mA: hot-plug peaks are 60-77 mA with Rs 120 R, and 90-114 mA on TPS923611 boards.
- VR rating stated. No internal ESD Zener.
- Vf about 2.6-3.1 V at 13.3 mA. With N = 5, 120 R and the BAW56, the string must stay below 22 V worst case and above
  about 6.5 V at 14 uA hot.
- For the rod lens, the emitter should be as small as possible across Z.

## 2. Candidates checked

| Family (package) | Warm: LCSC, stock, price @1 | Cool: LCSC, stock, price @1 | CCT | IF / IFP | Notes |
|---|---|---|---|---|---|
| **HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3** (3014, 3.0 x 1.4 x 0.70) | **C210340**, 3000 K (2800-3100), **102,969**, $0.0117 | **C210343**, 6000 K (5700-6500), **40,519**, $0.0138. Also C210342 5000 K (41,479), C210344 6500 K (6000-7000; 51,663), C210341 4000 K (68,461) | in window | 40 / **80 mA** (0.1 ms, 1/10) | Ra >= 80; 5-step MacAdam bins; ESD 1000 V HBM; no Zener. All JLC **Extended**. |
| HONGLITRONIC HL-A-3014H416W-S1-08HL-HR3 (3014) | C210335, 3000 K, 8,065 | C210338 6000 K, 19,820; C210337 5000 K, 41,428 | in window | not read | Sister sub-series; datasheet not read. H421W has more stock. |
| XINGLIGHT XL-3014WWC-02 / XL-3014UWC-02 (3014, 3.0 x 1.4 x **0.8**) | C2843790, 2800-3200 K, 12,697, $0.0118 | C2843791, **6500-7000 K**, 210,161, $0.0116 | **cool is out of window** | 60 / **120 mA** (0.1 ms, 1/10) | 20-33 lm at 60 mA; Vf 2.8-3.4 V at 60 mA (bins N13-3/4/5); ESD 2000 V; VR 5 V; **CRI not stated** (DS pp.3-4). Extended. |
| XINGLIGHT XL-2012WWC / XL-2012UWC (0805) | C965820, 2500-3100 K, 43,755, $0.0137 | C965818, **7500-15000 K**, 333,401 | cool out of window | 20 mA / not read | XL-2012UWC-DS (C3646924, 6000-7500 K) has only 3,921 in stock and is a different sub-series; the whole top of the chip emits (2.0 x 1.25). |
| XINGLIGHT XL-3216WWC / XL-3216UWC (1206) | C965830, 2800-3400 K, 10,554 | C965828, **12000-27000 K**, 206,019 | cool far out of window | 20 mA | Reject. |
| XINGLIGHT XL-1608WWC-06 / XL-1608UWC-04 (0603) | C965810 | C965808 | from parts.md | - | Not re-queried; 0603 flux is about a quarter of a 3014 at the same current. |
| PARALIGHT SZT3014WDT (3014) | - | C2835373, 2,599 | one CCT | 30 mA | No sibling pair found. |
| 2835 mid-power pairs | many | many | - | - | Not pursued: the 2835 cavity is about 2.3-2.4 wide across Z, about 2x the 3014's 1.1, so the rod beam would be about 2x wider. |

DigiKey: none of the ranked LCSC parts turned up on DigiKey. XL-2012WWC is on the DigiKey Marketplace (product 25672999)
only. The brief makes DigiKey optional for the LEDs.

## 3. Ranking and pick

1. **HONGLITRONIC HL-A-3014H421W-S1-08HL-HR3: 3000 K C210340 + 6000 K C210343. The pick.**
   - One datasheet (B-17-A-1548 rev A/3) covers both CCTs, so the two strings share one footprint, one Vf curve and one
     flux curve.
   - Both CCTs sit inside the window, with Ra >= 80 and 5-step MacAdam colour bins.
   - Stock is 40k-100k.
   - The emitter is the same 3014 cavity as the LUXEON (2.50 x ~1.1) at the same 0.70 height, so the rod design carries
     over.
   - It gives more flux at 13.3 mA than the LUXEON (6.5 lm vs 5.8 lm, typical warm).
   - Weak points: IFP is only 80 mA (see section 4, IFP), and the Vf bins are on the reel label but not tabulated.
2. **XINGLIGHT XL-3014WWC-02 + XL-3014UWC-02.**
   - Better electrical margin: IF 60 mA, IFP 120 mA, which also covers the TPS923611's 90-114 mA.
   - But the cool part is 6500-7000 K (outside 5000-6500), there is no CRI spec, and it is 0.8 tall.
   - Use it as the fallback if TPS923611 boards must be covered without changing Rs.
3. **XINGLIGHT XL-2012WWC + XL-2012UWC-DS (0805).** The cool part is 6000-7500 K with 3.9k stock, from a different
   sub-series. The chip is 1.25 wide across Z, and the flux is about 900 mcd, roughly 2.8 lm at 20 mA.

## 4. Chosen LED: detail (HL-A-3014H421W-S1-08HL-HR3)

| Item | Value (datasheet B-17-A-1548 rev A/3, 2019-05-24) |
|---|---|
| **Warm, D1-D5** | LCSC **C210340**, 3000 K bin "WS" (2800-3100 K; centre x 0.440, y 0.403). 12 lm min / 13 typ at 30 mA (p.3, p.7). Stock 102,969, $0.0117 @1. JLC Extended. |
| **Cool, D6-D10** | LCSC **C210343**, 6000 K bin "60-5" (5700-6500 K; centre 0.3220, 0.3365). 13 lm min / 14 typ at 30 mA (p.3, p.7). Stock 40,519, $0.0138 @1. JLC Extended. Alternates: C210342 (5000 K, 4750-5300) and C210344 (6500 K, 6000-7000). |
| **MPN caveat** | **The MPN is the same for every CCT.** The CCT is selected only by the LCSC code (C210340 vs C210343) and the reel label (TC). In KiCad the Value must carry the CCT (for example "HL-A-3014H421W 3000K") and the LCSC field is mandatory. |
| DigiKey | none found (optional for LEDs under the user rule) |
| Absolute max (p.4) | Pd 132 mW; **IF 40 mA**; **IFP 80 mA** (1/10 duty, 0.1 ms); **VR 5 V**; ESD 1000 V HBM; Topr -40..+85 C; Tj 115 C. Derating: 40 mA to 25 C, then linear to 20 mA at 85 C (p.5). |
| Electro-optical at 30 mA (p.3) | Vf 2.7-3.3 V (+-0.1 V); 2theta1/2 120 deg; IR <= 10 uA at VR 5 V; **Ra >= 80** (+-2); flux +-10 %. |
| **Zener** | **None.** The datasheet does not mention one. **IR <= 10 uA at 5 V reverse rules out an anti-parallel ESD diode**, and the 1000 V HBM rating is typical of an unprotected die. |
| **Vf at 13.3 mA** | From the p.5 IF-Vf curve: about 2.78 V at 10 mA and 2.93 V at 20 mA, so **about 2.85 V typ at 13.3 mA**. Scaling the 2.7-3.3 V (30 mA) window gives **about 2.6-3.15 V**. N = 5 then gives 13.0-15.8 V, plus 1.6 V across 120 R: well below 22 V. At microamps (hot, 14 uA) each LED holds about 2.3-2.5 V, so the string holds 11.5 V or more, above 6.5 V. The reel label carries a "VF rank" (p.12), but no bin table is published. For the tightest warm/cool match, order both CCTs with the same VF rank if LCSC can pick. |
| **Flux at 13.3 mA** | From the p.5 "Forward Current vs Relative Intensity" curve (1.0 at 30 mA): 0.40 at 10 mA and 0.72 at 20 mA, so **0.50 +- 0.03 at 13.3 mA**. Warm **6.5 lm typ / 6.0 min**, cool **7.0 typ / 6.5 min**, against 5.8 / 6.2 lm for the LUXEON. |
| Viewing angle | 120 deg (Lambertian-like, p.6 radiation diagram) |
| Package (p.2) | **3.00 (L) x 1.40 (W) x 0.70 (H)**, +-0.15. Reflector cavity opening **2.50 long**. The cavity width is not dimensioned; it scales to **about 1.1 (1.12)** from the top view. Cavity depth 0.40. MSL 4 (p.2; JLC bakes). 4000 pcs/reel, 8 mm tape, 4 mm pitch (p.12). |
| **Emitting area (for the rod)** | **2.50 (X) x ~1.12 (Z)**. The model uses 1.15, with 1.4 (full package width) as a variant. |
| Package pads (bottom view, p.2) | Pin 1: 1.68 x 0.80. Pin 2: 0.78 x 0.80. Gap 0.55. |
| **Land pattern (p.2, "Recommended Soldering Pattern")** | Pin 1: **1.91 x 0.92**. Pin 2: **0.91 x 0.92**. Gap **0.55**. Overall 3.37 x 0.92. |
| **Polarity: pin 1 = CATHODE (K)** | See the two views below. |
| Layout check | Pairs at 3.8 mm centres (L5-w13.5-s1.9) leave 0.43 mm pad to pad (3.8 - 3.37) and 0.8 mm body to body. That suits JLC (>= 0.2-0.3). |

**Polarity from two independent views:**
- **View A (p.2 package drawing).**
  - The symbol "1 o--|<--o 2" has its bar at pin 1, so pin 1 is the cathode.
  - The same page's top view puts a 45 deg chamfer on the cavity corner at the pin 1 end.
  - The bottom view and the land pattern make pin 1 the **large** pad (1.68 / 1.91).
- **View B (p.12 tape drawing).**
  - Each LED sits in its pocket with the chamfered cavity corner toward the sprocket holes.
  - The tape's diode symbol points its bar (cathode) toward the same sprocket-hole side.
- **The two views agree: chamfered corner = large pad = cathode.**

Footprint rules:
- Pad 1 is the large 1.91 pad and is K.
- Put the silkscreen cathode mark (bar or chevron) at the large-pad end.
- The LEDs sit on B.Cu, so place the normal top-view footprint and let KiCad flip it. **Never hand-mirror the pads**:
  that is the light-strip mistake.

**IFP margin: the pick's weak point.**
- TPS923610 boards (Rs 120 R): peaks of 60-77 mA stay below the 80 mA IFP. But the event lasts about 0.5 ms (tau
  0.4-0.9 ms), while the rating is for 0.1 ms at 1/10 duty.
  - Engineering judgement (not verified against the datasheet): a rare single pulse of <= 77 mA puts about 0.25 W into
    the die for about 0.5 ms, only a few kelvin of rise.
  - The same 3014 die class carries 60 mA continuously in the XINGLIGHT part.
  - Acceptable.
- TPS923611 boards: 90-114 mA exceeds the IFP.
  - Either raise Rs (180 R gives about 60-76 mA on the TPS923611; recheck the dim end in electrical-j6.md),
  - or use the XINGLIGHT XL-3014 pair (IFP 120 mA) and accept its 6500-7000 K cool part.

## 5. Series resistor, 120 R per string (pulse)

Requirement: survive about 0.7-1.9 W for about 0.5 ms, as a repeated single pulse (one per hot-plug).

| Rank | Part | LCSC / JLC | Stock, price @1 | DigiKey | Pulse evidence |
|---|---|---|---|---|---|
| **1 (pick)** | **Vishay CRCW0805120RFKEAHP** (CRCW-HP, "pulse proof", 0805, 0.5 W, 1 %, AEC-Q200) | **C844392**, Extended | 18,654, $0.0452 | 541-120TCT-ND [DK 5326877] | CRCW-HP DS p.5 single-pulse chart: about 20-30 W at 0.5 ms (read in parts.md), more than 10x the 1.9 W. The continuous-pulse chart also sits far above 1.9 W. |
| 2 | Panasonic ERJ-P06F1200V (anti-surge 0805, 0.5 W, 1 %) | C543533, Extended | 16,645, $0.0254 | ERJ-P06 series (PN not captured) | Anti-surge construction. No pulse-power curve in the Panasonic catalogue (parts.md): UNVERIFIED. |
| 3 | Panasonic ERJ-P08F1200V (anti-surge 1206, 0.66 W) | C4311641, Extended | 4,798, $0.0338 | ERJ-P08 series | As rank 2 |
| - | ROHM ESR10EZPF1200 (anti-surge 0805) | C559367, Extended | 1,105 only | - | Stock too thin |
| - | UNI-ROYAL 1206W4F1200T5E (standard 1206, 0.25 W) | C17909, **Basic** | 594,231, $0.0068 | - | Fallback only. It is not needed, since pulse-rated parts are stocked. Its pulse curve was not checked. |

## 6. BAW56 (one per string)
- **Nexperia BAW56,215, LCSC C8663: JLC Extended, stock 43,296, $0.0314 @1.** parts.md had seen 56,200 earlier.
- Datasheet (lcsc.com/datasheet/C8663.pdf, Nexperia), section 5, Table 2 "Pinning information":
  - **pin 1 = K1** (cathode, diode 1);
  - **pin 2 = K2** (cathode, diode 2);
  - **pin 3 = CA** (common anode).
  - This matches parts.md's wiring: pin 3 to the string's cathode end, pin 1 to W-/C-, pin 2 to the LED_SW anode bus.
- Section 8 limits: VRRM 90 V; IF 215 mA per diode (125 mA per device); IFSM 4 A (1 us), 1 A (1 ms), 0.5 A (1 s);
  IFRM 500 mA; Ptot 250 mW. Marking code A1%.
- SOT-323 alternative: **Nexperia BAW56W,115, LCSC C426777**, Extended, 11,989 in stock, $0.0488. Its pin order is the
  same as the SOT-23 part per parts.md; the W datasheet was not re-read.
- Other stocked equivalents (70 V class): onsemi BAW56LT1G C82478 (214,646) and onsemi BAW56WT1G C160837 (38,058).
- None is a JLC Basic part.

**JLC build:** 4 Extended lines (warm LED, cool LED, R, BAW56) plus the header, which JLC places by THT.

## 7. Sources
- Hongli datasheet B-17-A-1548 rev A/3 (HL-A-3014H421W-S1-08HL-HR3): lcsc.com/datasheet/C210340.pdf (one file for
  C210340-C210344). p.2 package, land pattern, symbol; p.3 selection guide; p.4 absolute maximum; p.5 curves; p.7 colour
  bins; p.12 tape and label.
- XINGLIGHT XL-3014WWC-02 datasheet: lcsc.com/datasheet/C2843790.pdf (pp.3-4). XL-3014UWC-02: jlcpcb.com/partdetail/XINGLIGHT-XL_3014UWC02/C2843791.
- JLC/LCSC listings: C210340-C210344, C210335-C210338, C2843790/1, C965818/20, C3646924/8, C965828/30, C844392,
  C543533, C4311641, C559367, C17909, C8663, C426777, C82478, C160837.
- Nexperia BAW56 datasheet: lcsc.com/datasheet/C8663.pdf.
- DigiKey Marketplace XL-2012WWC: digikey.in/en/products/detail/xinglight/XL-2012WWC/25672999.
