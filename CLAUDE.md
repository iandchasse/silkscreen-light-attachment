# Notes for coding agents

Ian (idc LLC) owns this project: the Silkscreen light attachment, a clip-on warm/cool light that plugs into the main
board's expansion header (`J6`) through the stock 4.26" case's top opening. Status: the rev B board and rev B housing are built and work;
the rev C housing (`housing/out/print/`) is checked in CAD only. Machine paths and local notes are in
`CLAUDE.local.md` (not in git); read it first if it exists.

## Ground rules

- **Commits:** plain messages, with no `Co-Authored-By` or other attribution trailer (public repo).
- **Keep it simple.** Ian rejected an over-engineered version: basic parts, 1-3 printed parts, screws, push on; no
  optics parts, no glue, nothing on the case modified.
- **The PCB is generated.** Change `pcb/tools/params.py` (and the tools), then run `pcb/tools/generate.py` and
  `pcb/tools/make_outputs.py` with KiCad 9's Python. `make_outputs.py` runs every gate first and writes
  `production/`, `docs/` and `build/geometry.json` only if all pass. Close KiCad first (the scripts refuse while a
  `*.lck` exists). Never hand-edit the `.kicad_*` files. `CQ_PYTHON` must name a Python with CadQuery (for the STEP
  models).
- **The housing:** `housing/src/build.py` (a CadQuery venv) builds the base and lid, runs every fit check and exits 1 on
  any failure. It needs `pcb/build/geometry.json` (run the PCB step first) and the stock case's tub/lid meshes:
  `housing/reference/case-426-standard/` by default (a copy from silkscreen-enclosures; refresh rule in its
  `PROVENANCE.md`), or `SILKSCREEN_CASE_OUT`. The 3.68" board is trimmed and has no expansion header (`J6`), so it is not supported.
- **Line endings:** `.gitattributes` stores every file as is (`* -text`). Don't add conversion rules: the fab files'
  bytes must stay the bytes that were checked.
- **Never commit** `workflows/`, `pcb/docs/sources/`, `enclosures/` (the local rev K case copy), G-code, build logs
  with machine paths, or `CLAUDE.local.md`; `.gitignore` covers them.
- **The board and the light strip are separate repos** (silkscreen-pcb, silkscreen-light-strip); cite them, don't copy
  from them without saying so in `NOTICE`.
