# The stock case the housing is checked against

`tub.stl` and `lid.stl` are the Silkscreen 4.26" case's **standard** (strip-less) tub and lid in the case's CAD frame,
copied from the silkscreen-enclosures project (idc LLC, CERN-OHL-S v2): `enclosures/case-426/out/standard/`, as built
by its `src/build.py` with `SILKSCREEN_VARIANT=standard`. They are here so `housing/src/build.py` runs its fit checks
from a fresh clone (the case's `out/` is build output, not in git).

| File | Bytes | sha256 |
|---|---|---|
| `tub.stl` | 2,162,984 | `1f28b6b4e1652dca3862147a698b35c9152e9c8cdfb0897aae2dff8de1ccd600` |
| `lid.stl` | 1,411,884 | `e393aee17d3560de3a50a23ac56e1e156a789cd9279547ef9080b36e354fd3fa` |

- Built 2026-10-20 from the case's main at the time (the teardrop side-key rebuild; copied 2026-10-21, at
  silkscreen-light-strip ae9e786, where the cases lived before they moved to silkscreen-enclosures). The 4.26's top,
  which is all the cap touches, is unchanged since rev K (the 2026-09-30 check in `housing/PROGRESS.md`).
- To check against a newer case build without copying, set `SILKSCREEN_CASE_OUT` to its folder, e.g.
  `../silkscreen-enclosures/enclosures/case-426/out/standard`. To refresh this copy, copy both files from there, update
  the table above, and rerun `housing/src/build.py`.
