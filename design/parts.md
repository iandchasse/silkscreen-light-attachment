# Light attachment - parts sourcing

Snapshot 2026-09-25. DigiKey product pages returned HTTP 403 to the fetch tool, so the DigiKey data
below comes from search-result titles (product ID, description) and **stock and price were NOT
captured**. Re-check both, and the LCSC numbers marked TBD, before ordering.

Rules applied: DigiKey-primary (Value = MPN, Manufacturer, DigiKey product), LCSC as an extra field.
Electrical targets (research/electrical-j6.md): N = 5 LEDs per colour, 13.3 mA per string,
IF >= 20 mA, IFP >= 80-100 mA, the same family and Vf bin for warm and cool, Rs = 120 R per string that
survives ~1.9 W / 0.5 ms pulses, one BAW56-class common-anode dual per string at the cathode end,
and male pins 5, 6 and 11 only.

Tags: [DS x p.N] = datasheet page (PDF page), [DK n] = DigiKey product ID in the URL
digikey.com/en/products/detail/<mfr>/<mpn>/<n>, [LS] = silkscreen-light-strip/docs/research/leds.md.

---------------------------------------------------------------------------------------------------

## Summary BOM (recommended)

| Ref | Qty | Value / MPN | Manufacturer | DigiKey | LCSC | Package |
|---|---|---|---|---|---|---|
| D1-D5 (warm) | 5 | L130-3090001400001 | Lumileds | [DK 5765368] | TBD (none found) | 3014, 3.0 x 1.4 x 0.70 |
| D6-D10 (cool) | 5 | L130-5790001400001 | Lumileds | [DK 5877570] | TBD (none found) | 3014, 3.0 x 1.4 x 0.70 |
| R1, R2 | 2 | CRCW0805120RFKEAHP | Vishay Dale | 541-120TCT-ND [DK 5326877] | TBD | 0805 |
| D11, D12 | 2 | BAW56,215 | Nexperia | stocked (PN not captured) | C8663 | SOT-23 |
| J1 | 1 | TSW-102-07-G-D-0xx (one omitted position) **or** PRPC006DAAN-RC with pins pulled | Samtec / Sullins | TSW-102 family / [DK 2775288] | TSW-106-07-G-D = C3337759 (JLC) | THT 2.54, .230 post |

For a side-view build (the PCB lies parallel to the glass, as on the light strip), swap D1-D10 for
XINGLIGHT XL-4008WWC / XL-4008UWC (LCSC-only; see 1b). No DigiKey warm/cool side-view pair was found.

---------------------------------------------------------------------------------------------------

## 1. LEDs

### 1a. Top-view (emits perpendicular to the PCB)

**Rank 1: Lumileds LUXEON 3014, 90 CRI. Warm L130-3090001400001 (3000 K) and cool
L130-5790001400001 (5700 K).**
- DigiKey: L130-3090001400001 is [DK 5765368], "White, Warm 3000K 3.1V 60mA 116 deg". L130-5790001400001 is
  [DK 5877570], "White, Cool 5700K 3.1V 60mA 116 deg". Both were listed as "ships today" in search results.
  Other members of the family: L130-6590001400001 (6500 K, 90 CRI), the 80-CRI high-efficacy parts
  L130-3080HE1400001 and L130-5780HE1400001 or L130-6580HE1400001 [DK 14617448], and the older
  L130-3080001400001 [DK 4754498] and L130-5780001400001 [DK 4754502].
- LCSC: none found (TBD). Lumileds 3014 is not a JLC Basic part. Assembly at JLC would need a consigned
  part or a global-sourcing order.
- Package: **3.0 x 1.4 x 0.70 mm** [DS208 p.1]. That is under the 0.8 mm target. The 1.4 mm width is
  the smallest of the candidates, so it gives the lowest emitter height when the PCB is mounted edge-on.
- Absolute maximum ratings [DS208 PDF p.5, Table 4]:
  - DC forward current: 120 mA.
  - Peak pulsed current: **150 mA** at 10 % duty and 10 ms.
  - Reverse voltage: **-5 V** at 2 uA ("not designed to be driven in reverse").
  - ESD: JS-001 Class 2.
  - Tj: 125 C. Operating case temperature: -40 to 105 C.
- **No ESD Zener.** The datasheet rates VR at 5 V and 2 uA, which rules out a reverse Zener (a Zener would
  conduct at about 0.7 V in reverse). No protection device is shown.
- Vf at 60 mA, 25 C: 2.8 min, 2.95 typ, 3.3 max. Tempco -2 to -4 mV/K. Rth(j-sp) 35 K/W
  [DS208 PDF p.5, Table 3]. Vf bins at 60 mA go in 0.1 V steps: T 2.80-2.90, V 2.90-3.00, W 3.00-... and
  so on [DS208 p.17, Table 7].
  - **At 13.3 mA, Vf is about 2.65-2.8 V.** This is INFERRED from the Figure 4 I-V curve [DS208 PDF p.9],
    which was not read numerically.
  - N = 5 then gives about 13.5-14 V, plus 1.6 V across Rs and 0.7-0.95 V across the diode. That is well
    under the 22 V ceiling (electrical-j6.md gives 19.5 V worst case for the 3014 class).
- Viewing angle: 116 deg typical, and a 140 deg angle contains 90 % of the flux [DS208 PDF p.4, Table 2].
- CRI: 70, 80, 90 or 95 minimum, set by the 5th-6th digits of the part number. CCT from 2200 to 6500 K
  [DS208 PDF p.4].
- **Flag, Vf bins:** the part numbers ending "1400001" are not sold per Vf bin. The warm and cool reels
  can therefore differ by one or two 0.1 V bins.
  - Rs = 120 R reduces the resulting blend error (electrical-j6.md section 6).
  - If exact matching matters, buy one reel per CCT and measure it, or ask Lumileds or a distributor
    for a kitted Vf bin.
- **Flag, low drive:** flux and CCT are binned at 60 mA. At 13.3 mA the parts are well under-driven.
  That is fine for life and efficacy, but the colour point shifts slightly (not quantified).

**Rank 2: Samsung LM281B+ (2835 class, 0.5 W mid-power).**
- DigiKey, warm: SPMWH1228FD7WAVMSG [DK 7347147], "LM281B+ White, Warm 3000K 3V 150mA 120 deg". Also
  SPMWH1228FD7WAV0S4 [DK 5959129] (LM281B, 3000 K, 3.1 V).
- The cool counterpart uses the same code with the CCT letters changed (positions 15-16), for example the
  5000 K or 6500 K code. Its exact DigiKey number was NOT captured.
- Package: **2.8 x 3.5 x 0.7 mm** ("228" form-factor code [DS LM281B+ Pro PDF p.6]). DigiKey gives
  0.75 mm maximum seated height.
- Absolute maximum ratings [DS PDF p.3]: IF 300 mA, **IFP 450 mA** (1/10 duty, 10 ms), ESD (HBM) 2 kV,
  Tj 115 C. **No reverse-voltage rating is given.**
- **No Zener.** Product-version code "1" means "Without Zener" [DS PDF p.6].
- Vf at 65 mA is binned in 0.1 V ranks: AY 2.6-2.7, AZ 2.7-2.8, A1 2.8-2.9, A2 2.9-3.0 [DS PDF p.4].
  - The ordering code WA or WK covers 2.6-3.0.
  - **WN or WM covers 2.6-2.8** [DS PDF p.6]. This tighter group helps warm/cool matching, and it is the
    lowest-Vf class (best headroom).
- CRI: code 5 = Ra 80 minimum, code 7 = Ra 90 minimum, R9 >= 50 [DS PDF p.4]. Beam angle 120 deg. CCT codes
  cover 2700 K upward.
- **Flag:** Samsung recommends a minimum of 10 mA "to avoid uneven brightness" [DS PDF p.3]. Deep ADIM
  dimming runs well below 10 mA, so check the low-dim appearance.
- Rank 2 because the 2.8 mm width raises the emitter when the PCB is edge-on, and the cool part number
  was not confirmed.
- LCSC: TBD. Samsung LM281B+ does appear on LCSC under some codes, but none was checked.

**Rank 3: XINGLIGHT 0603. Warm XL-1608WWC-06 (LCSC C965810) and cool XL-1608UWC-04 (LCSC C965808).**
- LCSC and JLC only (JLC part page C965810). The price on LCSC starts at about $0.005.
- 1.6 x 0.8 mm footprint (0603), the lowest profile.
- **Flag: the suffixes differ (-06 and -04).** Confirm that both have the same body height and lens
  before treating them as one family.
- The ratings were not fetched (UNVERIFIED). Typical for this vendor's 0603 parts: IF 20 mA,
  IFP 80-100 mA, VR 5 V, CRI about 70-80, no Zener.
- No DigiKey-orderable 0603/0805 warm+cool pair was found:
  - Kingbright's chip-type white range is cool-only: APHCM2012QWF/D (0805), APD3224QWF/D and others.
  - Wurth WL-SMTW has no warm white.
- Use this rank only if a JLC-only BOM is acceptable.

Checked and rejected:
- QT-Brightek QBLP670-IW-WW / -CW ([DK 4814836] and [DK 4814705]). This is a DigiKey warm/cool pair, but
  it is a top-view PLCC-2 at 3.2 x 2.8 x **2.1 mm** high. Too tall.

### 1b. Side-view (emits parallel to the PCB)

**Rank 1: XINGLIGHT XL-4008WWC (3000 K, LCSC C5440667) and XL-4008UWC (6000-6500 K, LCSC C2843774).
Confirmed from [LS] (datasheet pp.3-4 and p.7).**
- Package: 4.0 x 1.4 x 0.8 mm. It stands 0.8 mm above the PCB. The emitting face is 4.0 x 0.8 with a
  1.8 mm window.
- Land pattern: two pads, 1.6 x 1.1 mm, at x = +-1.85 mm [LS, datasheet p.7].
- Ratings:
  - IF 20 mA; **IFP 80 mA** (0.1 ms, 1/10 duty).
  - **VR 5 V**, IR 5 uA max.
  - Pd 70 mW; ESD 2000 V; **no Zener** (the light strip depends on this).
- Vf at 20 mA: 2.7-3.3 V, in bins N11-8 (2.7-2.9), N11-9 (2.9-3.1) and N12-1 (3.1-3.3). About 2.9-3.0 V at
  13 mA (read from the graph).
- 120 deg viewing angle. CRI Ra 70 for the UWC; not stated for the WWC. MSL 3.
- Derating: 20 mA flat up to about 27 C, then 10 mA at 85 C. 13.9 mA is allowed up to about 60 C.
- JLC Extended. LCSC stock (2026-09-24): 6,850 (UWC) and 8,840 (WWC), about $0.05-0.07 each.
- **IFP is only 80 mA**, against the 60-77 mA hot-plug peak with Rs = 120 R on the TPS923610. The TPS923611
  case (90-114 mA) exceeds it: use Rs = 150 R (52-64 mA; 78-96 mA on the 611) if this LED is chosen.

**Rank 2: no DigiKey warm/cool side-view pair was found.**
- Kingbright's right-angle white list is cool-only: AA2810AQWS/D and AA2810AVW1S (2.8 x 0.8 face,
  1300-1600 mcd, 110 deg, 20 mA), and AA4040 (4.0 x 4.0).
- Wurth WL-SMSW (side view) has no white at all.
- Lead, UNVERIFIED: the Dialight 0605 right-angle ChipLED (1.6 x 1.15 x 0.55 mm) is marketed across
  "~2700 K to ~6500 K" (dialightsignalsandcomponents.com). Check DigiKey for a matched warm/cool pair
  of order codes.

**Rank 3: a top-view part on an edge-on PCB instead of a side-view part.** Use the LUXEON 3014 (1a rank 1)
mounted as in light-strip-reuse.md mount style (b). This keeps the whole BOM DigiKey-orderable.
Recommended if DigiKey-primary is firm.

---------------------------------------------------------------------------------------------------

## 2. Series resistor, 120 R per string

The worst event is about 60-114 mA decaying with tau 0.4-0.9 ms. That puts 0.4-1.6 W and 0.2-0.6 mJ into
Rs itself; 1.9 W is the whole-string figure, used here as a conservative bound.

**Rank 1: Vishay CRCW0805120RFKEAHP** (CRCW-HP e3, "pulse proof, high power", 0805, 1 %, AEC-Q200).
- DigiKey 541-120TCT-ND [DK 5326877].
- Rated dissipation 0.5 W at 70 C [DS CRCW-HP p.1].
- **Single-pulse chart** [DS CRCW-HP p.5, "Single Pulse": n < 1000, mean P -> 0, dR equal to 8000 h
  of operation]:
  - The CRCW0805-HP curve reads **about 20-30 W at 0.5 ms**, and about 20 W at 1 ms.
  - That is more than 10x margin over 1.9 W.
- The continuous-pulse chart on the same page covers repeated events and also sits far above 1.9 W at
  0.5 ms (read visually).
- LCSC: TBD.

**Rank 2: Vishay CRCW0603120RFKEAHP** (0603-HP, 0.33 W). [DK 2226075].
- The single-pulse curve reads about 12-15 W at 0.5 ms [DS CRCW-HP p.5], more than 6x margin.
- Use this part if board area is tight.

**Rank 3: Panasonic ERJ-P06J121V** (0805 anti-surge, 0.5 W, 5 %, AEC-Q200). [DK 525207].
- Panasonic AOA0000C331 gives 0.5 W rated power and a 400 V limiting element voltage (overload 600 V)
  [p.2].
- **This catalogue has no pulse-power curve**, only ESD data [pp.1-5]. The pulse claim therefore rests on
  the "anti-surge" construction and is UNVERIFIED against 1.9 W / 0.5 ms.
- Rohm ESR10EZPJ121 (0805 anti-surge, 0.4-0.5 W) is an equivalent. Its pulse curve was not checked.

LCSC: none of the three had a confirmed C-number in search results.
- Fallback for a JLC build: a JLC Basic 0805 120 R thick-film part. A plain 0805 thick-film resistor has
  a lower pulse rating than the HP series, and the margin was not verified (UNVERIFIED).

---------------------------------------------------------------------------------------------------

## 3. BAW56-class common-anode dual diode (one per string)

**Rank 1: Nexperia BAW56,215 (SOT-23).**
- LCSC **C8663** (stock 56,200 in search results). LCSC lists it as 80 V, 215 mA, 1.25 V at 150 mA,
  trr 4 ns.
- Farnell lists it as "Dual Common Anode, 90 V". Either figure is >= 75 V.
- JLC Basic or Extended class: TBD. DigiKey stocks it; the product number was not captured.
- Datasheet: lcsc.com/datasheet/C8663.pdf (Nexperia). Its text was not extracted.
- **Pinning (standard BAW56, SOT-23):**
  - pin 1 = cathode, diode 1;
  - pin 2 = cathode, diode 2;
  - **pin 3 = common anode.**
- Verify against the datasheet pinning table (p.1-2) when drawing the symbol.
- Wiring per string:
  - pin 3 to the string's cathode end;
  - pin 1 to the W- or C- contact (block);
  - pin 2 to the anode bus / LED_SW pin (clamp).

**Rank 2: Nexperia BAW56W,115 (SOT-323).**
- Same die and the same pin order.
- Matches the light strip's SOT-323 precedent (BAV70W, C28064, CPL rotation +180).
- LCSC number TBD.

**Rank 3:** onsemi BAW56LT1G or Diodes Inc BAW56-7-F (SOT-23, 70-75 V class). Check VR >= 75 V on the
exact part (the brief prefers 75-100 V for TPS923611 builds).

---------------------------------------------------------------------------------------------------

## 4. Male header to mate J6 (Sullins PPPC062LJBN-RC)

J6 constraints:
- .025 in (0.64 mm) square contacts.
- Maximum insertion depth 6.00 mm; minimum engagement about 3.68 mm (research/mechanical-j6.md).
- Pins 5 (x 54.662, row z -3.81), 6 (x 57.202, row z -3.81) and 11 (x 54.662, row z -1.27) only.
- No metal at positions 4 or 12.

The three pins fall in J6 columns 5-6 (k = 4, 5), so **a 2x2 header covering pins 5, 6, 11 and 12 with
position 12 omitted** is the minimum part.

| Rank | Part | DigiKey | LCSC / JLC | Post (mating) | Body | Tail | Notes |
|---|---|---|---|---|---|---|---|
| 1 | **Samtec TSW-102-07-G-D-0xx** (2x2, one position omitted at the factory) | Samtec TSW family is at DigiKey; the omitted-position variant is likely order-to-build (samtec.com direct) | TSW-106-07-G-D = **C3337759** (JLC); 2x2 TBD | **.230 [5.84]** | .100 [2.54] | .100 [2.54] (OAL .430) | See the TSW notes below |
| 2 | **Sullins PRPC006DAAN-RC** (2x6) with pins 1-4, 7-10 and 12 pulled out | [DK 2775288] (likely S2011EC-06-ND) | TBD (none found) | **.230 [5.84]** | .100 [2.54], 15.24 x 5.08 | .120 [3.05] | See the Sullins notes below |
| 2b | Sullins PRPC003DAAN-RC (2x3, columns 4-6) with pins 4, 10 and 12 pulled; or PRPC002DAAN-RC (2x2, TBD) with pin 12 pulled | [DK 2775291] (2x3) | TBD | .230 | .100 | .120 | Smaller body; keying is left to the housing |
| 3 (extended) | **Sullins PRPC006DFAN-RC** (.318 post) | [DK 2775408] | TBD | **.318 [8.08]** | .100 | .120 | Only for the "body outside the wall" variant. It needs a 2.45-2.78 mm standoff (wall or rib) so engagement stays at 5.30-5.63 and < 6.00 |
| reject | Generic JLC Basic 2.54 mm headers (6.0 mm mating, 2.5 body, 3.0 tail) | - | many | 6.0 | 2.5 | 3.0 | **6.0 mm mating equals J6's 6.00 max insertion depth: zero bottoming margin** when the body seats on J6's face |

Samtec TSW-102-07-G-D-0xx:
- Samtec's own pages confirm the TSW-106-07-G-D figures: .230 post and .430 OAL, i.e. .100 body and .100 tail.
- Samtec drawing TSW-XXX-XX-XXX-X-XX-XXX: "-XXX = polarizing specification, position to be omitted"
  (FIG 3). Samtec's catalogue lists TSW-106-07-G-D-007 as a product.
- -G = 10 u" gold on the contact area, 3 u" on the tail. Phosphor bronze terminals, black PBT body
  [Samtec print, sheet 1].
- **Samtec numbers double-row parts odd/even across the rows** (1/2 = first column). J6 numbers them
  1-6 / 7-12. Map carefully: the omitted position is J6 pin 12, which is the near-board row in the +X column.
- Only ONE omitted position is guaranteed by the standard suffix. That is exactly what a 2x2 needs.

Sullins PRPC006DAAN-RC:
- Mating length from the Sullins code table AA = .230 / .120 (Square Post Header catalogue, pp.74-75).
  DigiKey lists the single-row PRPC006SAAN-RC (S1011EC-06-ND) at .230 mating.
- Pulling pins by hand is INFERRED to be feasible (breakaway-style press-fit posts), but it is not a
  factory option.
- The full 12-position body keeps the whole 15.24 mm body for keying inside the stock J6 opening.

Other header notes:
- **THT over SMT:** use a through-hole part. The plug takes about 5 N insertion and 4 N withdrawal with
  3 pins, and more with a 12-pin body, which is why THT is preferred.
  - JLC can place THT headers (THT assembly) only if the part has an LCSC or JLC number. Otherwise, hand
    solder 1-3 pins.
- **Tail trimming:**
  - The Sullins tail is 3.05 mm, so it stands 1.45 mm proud of a 1.6 mm PCB.
  - The Samtec tail is 2.54 mm, so it stands 0.94 mm proud.
  - Trim flush, or cover the tails with the housing. The light PCB's +Y face must stay smooth where a
    finger or the case wall meets it.
- **Plating:** choose gold (-G, or Sullins "AN" = gold flash?, UNVERIFIED) to match J6's gold contacts.
  Avoid tin-on-gold fretting.

---------------------------------------------------------------------------------------------------

## 5. TVS on the accessory

**Recommendation: fit none.**
- The main board already has D3 SMAJ26A on LED_SW and D8 PESD2IVN-UX on W-/C-.
- The accessory has no ground: pin 4 is unpopulated by rule, so a TVS to GND is impossible.
- The BAW56 clamp already limits reverse ESD across each string.

---------------------------------------------------------------------------------------------------

## Sources
- Lumileds DS208 LUXEON 3014 (20250923): lumileds.com/wp-content/uploads/files/DS208-luxeon-3014-datasheet.pdf
- Samsung LM281B+ Pro datasheet Rev 1.2: www1.futurelightingsolutions.com/.../Data_Sheet_LM281B_plus_Pro_VK_General_Rev_1.2.pdf
- DigiKey product pages: IDs 5765368, 5877570, 7347147, 5959129, 4814836, 4814705, 5326877, 2226075,
  525207, 2775288, 2775291, 2775408 (search-result titles; the pages returned 403)
- Vishay CRCW-HP e3: vishay.com/docs/20043/crcwhpe3.pdf (single-pulse chart p.5, read visually)
- Panasonic ERJ-P anti-surge: industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/AOA0000C331.pdf
- LCSC: C8663 (BAW56,215), C965810 and C965808 (XL-1608), C5440667 and C2843774 (XL-4008);
  JLC C3337759 (TSW-106-07-G-D)
- Samtec TSW print: suddendocs.samtec.com/prints/tsw-xxx-xx-xxx-x-xx-xxx-mkt.pdf; samtec.com/products/tsw-106-07-g-d
- Kingbright USA right-angle white and chip white lists; Wurth WL-SMSW catalogue page
- research/mechanical-j6.md section 9 (Sullins S2 catalogue, engagement table); [LS] for XL-4008
