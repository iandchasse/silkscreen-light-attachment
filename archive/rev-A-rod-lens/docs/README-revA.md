# Silkscreen light attachment

**A clip-on warm/cool reading light for the [Silkscreen](https://github.com/iandchasse/silkscreen-pcb) e-reader.** It plugs into the main board's second light header, `J6`, through the opening the stock case already has in its top wall. The case is not modified.

- A small rigid board holds 5 warm (3000 K) and 5 cool (6000 K) LEDs above the top edge of the screen.
- A clear 4 mm acrylic rod under the LEDs acts as a lens and aims the light down the page. It sits in a black printed carrier.
- A printed clip and cover hold the light on the case. The reader's normal frontlight controls (brightness and warmth) drive it.
- It is meant for a reader with nothing on the frontlight connector `J3` (see [Safety](#safety-summary)). The in-case option is the sibling project [silkscreen-light-strip](../silkscreen-light-strip).

> **Rev A: designed and checked in CAD. NOT built or tested.** The board passes ERC, DRC and schematic parity with no findings, plus its own header, keep-out and string-voltage gates. The printed parts pass every scripted fit check against a model of the stock case. Nothing has been printed, ordered or powered yet.
>
> **Do these first, in this order:**
> 1. Print the **clip only** and try it on your case. It has no metal, so this is safe. Check that it seats flat with light force and does not rock ([ASSEMBLY §7a](docs/ASSEMBLY.md#7-fit-it-on-the-case-light-off)).
> 2. Look at the entry of your `J6` socket through the opening and measure it ([SAFETY-AND-TEST §7](docs/SAFETY-AND-TEST.md#7-measure-the-j6-entry)).
> 3. Buy a few loose LEDs and do the coin-cell polarity test ([ASSEMBLY §1](docs/ASSEMBLY.md#1-coin-cell-test-of-one-loose-led)).
> 4. Then order the boards and the header ([ORDERING](docs/ORDERING.md)), and bench-test the first board before it goes near the reader ([SAFETY-AND-TEST §2](docs/SAFETY-AND-TEST.md#2-bench-test-of-the-bare-pcba)).

| On the stock case (render) | Light board, LED side (faces the case) | Light board, top side (under the cover) |
|:---:|:---:|:---:|
| ![Assembly on the case](housing/out/render/assembly_iso.png) | ![PCBA, LED side](pcb/docs/images/render_top.png) | ![PCBA, top side](pcb/docs/images/render_bottom.png) |

More renders: [back view](housing/out/render/assembly_iso_back.png), [front view](housing/out/render/front.png), [section through `J6`](housing/out/render/section_J6_x55.9.png), [section through the rod](housing/out/render/section_rod_x30.png), [section through the left rod cradle](housing/out/render/section_cradle_x-2.1.png).

## What you need

Every SMD part is stocked at LCSC and assembled by JLCPCB. On 2026-09-25: warm LED C210340 102,969 in stock, cool LED C210343 40,519, BAW56 C8663 43,296, 200 Ω resistor C5972814 2,477.

| Item | Qty | Notes |
|---|---|---|
| Light PCBA | 1 | Rigid 2-layer, 1.6 mm, black mask, 68.4 × 25.8 mm. JLCPCB assembles the 14 SMD parts (Economic PCBA, top side). The header `J1` is **not** placed by JLC. See [ORDERING](docs/ORDERING.md) |
| Header `J1`: Samtec TSW-102-14-G-D | 1 | DigiKey 612-TSW-102-14-G-D-ND. Push out position 4 and hand-solder it. The TSW-102-14-G-D-004 from Samtec (position 4 already omitted) also works. **No substitutes** |
| 2.54 mm 2 × 6 female header | 1 | Soldering jig for `J1` |
| Clip, cover, rod carrier | 1 each | Printed in black PETG, no supports. On the reference printer: 55 min 49 s and 13.9 g for all three |
| Clear PMMA (acrylic) rod, Ø4.0 mm | 66.0 mm | Cast or extruded, cut square. The ends need no polish |
| Steel dowel pins, Ø1.5 × 4 mm, ISO 8734 | 2 | Set in epoxy in the carrier. They locate it on the board |
| Screws, ST2.2 × 6.5 mm pan head, plastics thread-forming (PT / DIN 7981) | 3 | Cover to clip. Tighten snug only |
| Rod check | - | Measure the rod: use Ø3.90-4.10 mm (see [ORDERING](docs/ORDERING.md)) |
| 5-minute epoxy | a few drops | Carrier to board, dowels, and a dot on each rod end. **Not CA glue**: it fogs the acrylic rod |

Tools: a multimeter, a current-limited bench supply, a CR2032 coin cell, calipers, a soldering iron, a go-gauge plate ([ASSEMBLY §4](docs/ASSEMBLY.md#4-header-qa-length-and-go-gauge)), and 1.1 mm, 1.5 mm and 2.4 mm drills.

## How it attaches

The stock case has a rectangular opening in its top wall right above `J6`. The light's three header posts go down through that opening into `J6`. Nothing else enters the case.

- The printed **clip** sits on the flat top face of the case on three pads. Its front lip bears on the front face above the screen, and two back spring fingers press it forward. An ear on the right and a spring leaf on the left locate it sideways.
- The **cover** screws onto the clip and pushes on the header tails. That sets how deep the posts go into `J6`: 4.68 to 5.21 mm nominal, 4.03 to 5.64 mm worst case, inside the 3.68 to 6.00 mm window ([housing/out/REPORT.md](housing/out/REPORT.md)).
- The board floats ±0.30 mm sideways inside the housing, so `J6` centres the posts, not the case.
- The clip's fingers take hold before the posts arrive: front-to-back from 10.27 mm above the seated position and sideways from 7.31 mm, while the posts meet `J6` at 5.42 mm.
- It holds by friction and the `J6` contacts: about 8 N to pull off and about 8.8 N to push on (computed, not measured; target 5 to 12 N).

Push it straight down onto the top edge, with the arrow and the word SCREEN on the cover pointing toward the screen side. It fits only one way round: turned 180°, the posts land on the solid top face and cannot touch any contact. **Remove it by gripping the two ribbed ends, never by the visor** over the screen.

## Safety summary

- **Plug and unplug it only with the frontlight off (brightness 0), then wait about 10 s.** If the light was on with nothing attached, the driver's output capacitor sits at about 25 V for several seconds. Plugging in during that time sends a pulse through one LED string: 43.7 to 49.3 mA on a TPS923610 main board, 68.0 to 73.5 mA on a TPS923611 board. Both are under the LEDs' 80 mA pulse rating (IFP). That rating is specified only for 0.1 ms pulses at 1/10 duty (Hongli datasheet p.4), and this pulse decays over roughly 0.25-1 ms, so the margin is an estimate, not a datasheet guarantee. Treat "light off, wait 10 s" as mandatory on every main board.
- **Only three pins carry metal:** `J6` pin 5 (LED_SW, the anode supply), pin 6 (W−, warm return) and pin 11 (C−, cool return). The board has no pad or copper at any other `J6` position:
  - pin 4 is ground, right next to LED_SW. A pin or solder bridge there could short the light supply to ground;
  - pin 12 is the raw battery (P+_FUSE). A pin there could feed the battery into the light;
  - the other pins are 3.3 V, I²C and boot-strap GPIOs, which the light has no reason to touch.
- Each string has a **200 Ω** pulse-rated resistor and a BAW56 diode. Together they block reverse current, clamp reverse voltage across the LEDs, and limit the current in the one bad misinsertion case (anode on LED_SW, a return on pin 4) to about 79 mA until the driver's over-voltage protection latches off.
- **TPS923611 boards.** Some main boards use a TPS923611 in place of the TPS923610 (the out-of-stock swap in the silkscreen-pcb README). Its over-voltage limit is higher (29.6 to 31.4 V). The 200 Ω resistors were chosen so that it stays under the LED rating too, but the margin is small, so the "light off first" rule is mandatory on those boards.
- **Never plug the bare board into `J6`** without the clip and cover: they are what fix its position. After any forced or wrong-way attempt, check the posts with the go-gauge.
- `J3` and `J6` share one current-regulated driver. If your panel has a frontlight on `J3`, both lights share the same 13.3 mA unevenly. That is safe but dim; this light is not designed for that case.

Details, numbers and the bench test: [docs/SAFETY-AND-TEST.md](docs/SAFETY-AND-TEST.md).

## Docs

| Doc | What it covers |
|---|---|
| [docs/DESIGN.md](docs/DESIGN.md) | Why it is built this way: optics, electrical window, header safety, datum scheme, deviations and known inconsistencies |
| [docs/ORDERING.md](docs/ORDERING.md) | JLCPCB PCB and PCBA form fields, the placement-preview checks, buying `J1`, mechanical parts, printing |
| [docs/ASSEMBLY.md](docs/ASSEMBLY.md) | LED polarity test, soldering `J1` in the jig, header length and go-gauge QA, carrier, rod, cover, fitting |
| [docs/SAFETY-AND-TEST.md](docs/SAFETY-AND-TEST.md) | Bench test, LED_MONIT, hot-plug, misinsertion, `J6` entry, pull-off force and the 7-day spring check |
| [docs/FIRMWARE-NOTES.md](docs/FIRMWARE-NOTES.md) | Recommended firmware changes (enable pulse, load check, latch recovery). The firmware repo is not changed |
| [pcb/docs/jlc-notes.md](pcb/docs/jlc-notes.md) | Generated JLC order notes |

## Folder map

| Path | What it is |
|---|---|
| `docs/` | The docs listed above |
| `pcb/` | Generated KiCad 9 project. `pcb/tools/` generates everything; do not edit the `.kicad_*` files by hand |
| `pcb/production/` | Gerber zip, `bom.csv`, `jlc_bom.csv`, `jlc_cpl.csv`, STEP files (including the enclosure-frame PCBA) |
| `pcb/docs/` | Schematic and layout PDFs, renders, `design_summary.md`, `jlc-notes.md`, ERC/DRC and gate reports, datasheet evidence |
| `housing/src/` | CadQuery source for the clip, cover and carrier, and the fit checks |
| `housing/out/` | Print files (`print/*.stl`, `*.step`, `housing-plate.3mf`), `REPORT.md`, `checks.json`, renders, slicer report |
| `design/` | The contract (`DESIGN-SPEC.md`), mechanical spec, spec audit, optics, LED choice and the three independent reviews |
| `research/` | Source research: `J6` electrical, `J6` mechanical, the stock case, what was reused from the light strip |
| `tools/` | Optics ray-trace scripts (`rod_lens.py`, `optics_sim.py`, `rod_layout_check.py`, `rod_report.py`) |
| `workflows/` | Scripts that drove the design runs |
| `enclosures/silkscreen-enclosure-claude/` | **Local only, not tracked** (see `.gitignore`): a fit-reference copy of the separate silkscreen-enclosure-claude repo (rev K, about 271 MB). The housing checks read it. Copy it in from that repo to rebuild the housing |

## Regenerating

**PCB.** Close KiCad first: the scripts refuse to write while a `*.lck` file exists.

```
cd pcb
"C:\Program Files\KiCad\9.0\bin\python.exe" tools\generate.py
"C:\Program Files\KiCad\9.0\bin\python.exe" tools\make_outputs.py
```

- `generate.py` writes the library, schematic, project files and the routed board.
- `make_outputs.py` runs the gates first (ERC, DRC with parity, the header handedness and keep-out gate, field sync, the string-voltage check). It writes `production/`, `docs/` and `build/geometry.json` only if every gate passes.
- Environment overrides: `KICAD9_DIR`, `KICAD_CLI`, and `CQ_PYTHON` (a Python with CadQuery, used for the STEP models). `CQ_PYTHON` defaults to `..\..\silkscreen-enclosure-claude\.venv\Scripts\python.exe` relative to `pcb\` (the enclosure repo next to this project folder).

**Housing.** Use the enclosure project's venv (CadQuery 2.8, trimesh, manifold3d):

```
cd housing
"..\..\silkscreen-enclosure-claude\.venv\Scripts\python.exe" src\build.py        # add --no-sweep / --no-render for a quick run
"..\..\silkscreen-enclosure-claude\.venv\Scripts\python.exe" src\slice_check.py  # optional; needs OrcaSlicer
```

- `build.py` builds the three parts, runs the checks, and writes `out/`. It exits with code 1 on any violation.
- It reads `pcb/build/geometry.json` (run the PCB step first) and the stock-case files in `enclosures/silkscreen-enclosure-claude/` (`out/tub.stl`, `out/lid.stl`, `hardware/cache/J6.brep`). If those are missing, rebuild the case with its own `src/build.py`.

**Optics.** `python tools/rod_lens.py --rev2` reproduces the rev 2 rod numbers (about 70 s; `--quick` for fewer rays, `--at D,gap,dz` to evaluate one geometry, `--name` for the output tag, `--help` for all modes). See [design/optics-final.md](design/optics-final.md).

## Credits and licence

Designed by Ian Chasse (idc LLC) as a companion to [silkscreen-pcb](https://github.com/iandchasse/silkscreen-pcb). The generator structure and many of its review lessons come from [silkscreen-light-strip](../silkscreen-light-strip). The stock case is silkscreen-enclosure-claude rev K.

CERN-OHL-S-2.0, © 2026 idc LLC. See [LICENSE](LICENSE) and [NOTICE](NOTICE). The KiCad library parts copied into `pcb/lib/` and the third-party evidence in `pcb/docs/sources/` keep their own terms (listed in NOTICE).
