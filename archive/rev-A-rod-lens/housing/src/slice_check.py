"""Optional: slice the three printed parts with the installed OrcaSlicer (Elegoo Centauri Carbon 2,
0.4 nozzle, 0.20 mm Standard, Elegoo PETG, 3 walls, 30 % infill, supports OFF) and report time,
filament and any support / floating-region warnings. Adapted from the stock case's slice_check.py.
Nothing is sent to a printer. Writes out/slice/slice-report.json (build.py folds it into REPORT.md).

    <enclosure venv python> slice_check.py
"""
import json
import re
import subprocess
from pathlib import Path

import params as P

ORCA = Path(r'C:\Program Files\OrcaSlicer\orca-slicer.exe')
PROFILES = Path(r'C:\Program Files\OrcaSlicer\resources\profiles')
OUT = P.OUT / 'slice'
PRESETS = {'machine': 'Elegoo Centauri Carbon 2 0.4 nozzle',
           'process': '0.20mm Standard @Elegoo CC2 0.4 nozzle',
           'filament': 'Elegoo PETG @ECC2'}
OVERRIDES = {'process': {'wall_loops': '3', 'sparse_infill_density': '30%', 'enable_support': '0'}}


def index():
    idx = {}
    for kind in ('machine', 'process', 'filament'):
        for f in sorted(PROFILES.rglob(f'{kind}/**/*.json')):
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
            except Exception:
                continue
            if 'name' in d:
                idx.setdefault((kind, d['name']), f)
    return idx


def flatten(kind, name, idx):
    d = json.loads(idx[(kind, name)].read_text(encoding='utf-8'))
    parent = d.get('inherits')
    base = flatten(kind, parent, idx) if parent and (kind, parent) in idx else {}
    base.update({k: v for k, v in d.items() if k != 'inherits'})
    return base


def presets():
    idx = index()
    paths = {}
    for kind, name in PRESETS.items():
        d = flatten(kind, name, idx)
        d['name'] = name
        d.pop('instantiation', None)
        d.update(OVERRIDES.get(kind, {}))
        if kind == 'machine' and 'G92 E0' not in (d.get('layer_gcode') or ''):
            d['layer_gcode'] = ((d.get('layer_gcode') or '') + '\nG92 E0').strip()
        p = OUT / f'{kind}.json'
        p.write_text(json.dumps(d, indent=1))
        paths[kind] = p
    return paths


def slice_part(stl, pre):
    dest = OUT / stl.stem
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob('*.gcode'):
        old.unlink()
    cmd = [str(ORCA), '--orient', '0', '--arrange', '1', '--slice', '0', '--load-settings',
           f"{pre['machine']};{pre['process']}", '--load-filaments', str(pre['filament']), '--outputdir', str(dest), str(stl)]
    r = subprocess.run(cmd, capture_output=True, timeout=900, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    log = (r.stdout or b'').decode(errors='ignore') + (r.stderr or b'').decode(errors='ignore')
    g = next(dest.glob('*.gcode'), None)
    info = {'exit': r.returncode, 'gcode': g.name if g else None,
            'warnings': sorted({ln.strip()[:200] for ln in log.splitlines()
                                if re.search(r'support|floating|overhang|cantilever|warning', ln, re.I)})[:20]}
    if g:
        head = g.read_text(errors='ignore')
        for key, pat in {'time': r'estimated printing time \(normal mode\) = (.+)',
                         'grams': r'total filament used \[g\] = ([\d.]+)',
                         'layers': r'total layers count = (\d+)', 'filament_type': r'; filament_type = (\S+)',
                         'support_used': r'; enable_support = (\d)'}.items():
            m = re.search(pat, head)
            info[key] = m.group(1).strip() if m else None
    return info


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    pre = presets()
    report = {'presets': PRESETS, 'overrides': OVERRIDES}
    for name in ('clip', 'cover', 'carrier'):
        info = slice_part(P.OUT / 'print' / f'{name}.stl', pre)
        report[name] = info
        print(name, info, flush=True)
    (OUT / 'slice-report.json').write_text(json.dumps(report, indent=1))
