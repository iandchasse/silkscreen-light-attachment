"""PCBA for the fit checks, E frame, seated (underside y 118.61).

Built from DESIGN-SPEC numbers (proxy). If pcb/build/geometry.json exists it is read and compared,
and its part boxes / pins / holes replace the proxy's where present.
"""
import json

import params as P
from util import box, cyl_y, fuse, cut, prism_y

YP = P.PCB_Y_SEAT


def outline_pts():
    (x0, x1), (z0, z1), (wx0, wx1), zw = P.PCB_X, P.PCB_Z, P.PCB_WIDE_X, P.PCB_WIDE_Z0
    return [(x0, z0), (x1, z0), (x1, zw), (wx1, zw), (wx1, z1), (wx0, z1), (wx0, zw), (x0, zw)]


def proxy_spec():
    s = {'source': 'proxy (DESIGN-SPEC numbers)', 'underside_y': YP, 'outline': outline_pts(),
         'holes': [(x, z, P.COL_HOLE_D) for x, z in P.COLS.values()] +
                  [(x, z, P.DATUM_HOLE_D) for x, z in P.DATUM_HOLES + P.STAKE_HOLES],
         'boxes': {}, 'pins': {}}
    for i, x in enumerate(P.LED_X_WARM + P.LED_X_COOL):
        s['boxes'][f'D{i + 1}'] = (x - P.LED_L / 2, x + P.LED_L / 2, P.LED_Z - P.LED_W / 2, P.LED_Z + P.LED_W / 2, P.LED_H)
    for ref, (x, z, lx, lz, h) in P.PROXY_PARTS.items():
        s['boxes'][ref] = (x - lx / 2, x + lx / 2, z - lz / 2, z + lz / 2, h)
    s['boxes']['J1_body'] = (*P.HDR_BODY_X, *P.HDR_BODY_Z, P.HDR_BODY)
    tip = YP - P.HDR_BODY - P.HDR_POST
    for n, (x, z) in P.PINS.items():
        s['pins'][n] = (x, z, tip, tip + P.HDR_OAL)
    return s


def load_geometry():
    """Reader for pcb/build/geometry.json (schema of pcb/tools/export_geometry.py, 2026-09-25).

    Uses the file's outline, holes, LED / part / header body boxes and header pins. Anything the file
    lacks keeps the proxy value; every substitution is noted.
    """
    if not P.PCB_GEOM.exists():
        return None, None
    g = json.loads(P.PCB_GEOM.read_text())
    s = proxy_spec()
    s['source'] = 'pcb/build/geometry.json (' + str(g.get('generator', '?')) + ', ' + str(g.get('date', '?')) + ')'
    notes, used = [], []
    try:
        pcb = g.get('pcb', {})
        uy = pcb.get('underside_y_seated')
        if uy is not None:
            s['underside_y'] = float(uy)
            if abs(float(uy) - YP) > 1e-6:
                notes.append(f'underside {uy} differs from the contract {YP}')
        if abs(float(pcb.get('thickness', P.PCB_T)) - P.PCB_T) > 1e-6:
            notes.append(f"thickness {pcb.get('thickness')} differs from {P.PCB_T}")
        ol = pcb.get('outline_xz')
        if ol and len(ol) >= 3:
            s['outline'] = [(float(p[0]), float(p[1])) for p in ol]
            used.append(f'outline ({len(ol)} pts)')
        hl = [(float(h['x']), float(h['z']), float(h['dia'])) for h in g.get('holes', []) if not h.get('plated')]
        if hl:
            s['holes'] = hl
            used.append(f'{len(hl)} NPTH holes')
        boxes = {}
        for key in ('leds', 'parts'):
            for b in g.get(key, []):
                bb = b['body_box']
                boxes[b['ref']] = (bb['x'][0], bb['x'][1], bb['z'][0], bb['z'][1], s['underside_y'] - bb['y'][0])
        hd = g.get('header', {})
        if 'body_box' in hd:
            bb = hd['body_box']
            boxes['J1_body'] = (bb['x'][0], bb['x'][1], bb['z'][0], bb['z'][1], s['underside_y'] - bb['y'][0])
        if boxes:
            s['boxes'] = boxes
            used.append(f'{len(boxes)} body boxes')
        pins = {}
        for p in hd.get('pins', []):
            pins[str(p['pad'])] = (float(p['x']), float(p['z']), float(p['y_post_tip']), float(p['y_tail_tip']))
        if pins:
            s['pins'] = pins
            used.append(f'{len(pins)} header pins')
        if set(pins) != set(P.PINS):
            notes.append(f'header pads {sorted(pins)} differ from {sorted(P.PINS)}')
        nop = hd.get('no_pin_at_j6_12')
        if nop and (abs(nop[0] - P.NO_PIN[0]) > 1e-3 or abs(nop[1] - P.NO_PIN[1]) > 1e-3):
            notes.append(f'no-pin position {nop} differs from {P.NO_PIN}')
    except Exception as e:     # never let a schema surprise break the housing build
        notes.append(f'geometry.json parse problem: {e!r}; proxy numbers kept where missing')
    notes.insert(0, 'used from file: ' + ', '.join(used))
    return s, notes


def build(spec=None, y_under=YP):
    """Components dict {name: solid} at the given underside height."""
    spec = spec or proxy_spec()
    dy = y_under - spec['underside_y']
    comps = {}
    board = prism_y(spec['outline'], y_under, y_under + P.PCB_T)
    holes = [cyl_y(x, z, d / 2, y_under - 1, y_under + P.PCB_T + 1) for x, z, d in spec['holes']]
    comps['board'] = cut(board, *holes)
    for ref, (x0, x1, z0, z1, h) in spec['boxes'].items():
        comps[ref] = box(x0, x1, y_under - h, y_under, z0, z1)
    for n, (x, z, y0, y1) in spec['pins'].items():
        a = P.PIN_SQ / 2
        comps['pin_' + n] = box(x - a, x + a, y0 + dy, y1 + dy, z - a, z + a)
    return comps


def compare(spec):
    """Differences between a loaded geometry spec and the proxy (for the report)."""
    p = proxy_spec()
    out = {'source': spec['source']}
    out['pins'] = {n: [round(a - b, 3) for a, b in zip(spec['pins'][n], p['pins'][n])] for n in p['pins']}
    out['holes_file'] = spec['holes']
    out['boxes_only_in_file'] = sorted(set(spec['boxes']) - set(p['boxes']))
    out['boxes_moved'] = {k: [round(a - b, 3) for a, b in zip(spec['boxes'][k], p['boxes'][k])]
                          for k in sorted(set(spec['boxes']) & set(p['boxes']))
                          if max(abs(a - b) for a, b in zip(spec['boxes'][k], p['boxes'][k])) > 1e-3}
    xs = [q[0] for q in spec['outline']]
    zs = [q[1] for q in spec['outline']]
    out['outline_bbox_file'] = [round(min(xs), 3), round(max(xs), 3), round(min(zs), 3), round(max(zs), 3)]
    return out
