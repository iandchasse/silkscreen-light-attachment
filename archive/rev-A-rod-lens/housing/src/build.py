"""Build clip, cover and rod carrier -> export (print orientation) -> checks -> renders ->
out/checks.json + out/REPORT.md. Exit code 1 on any violation.

    <enclosure venv python> build.py [--no-sweep] [--no-render]
"""
import datetime
import json
import re
import sys
import time
import zipfile

import cadquery as cq
import numpy as np

import carrier
import checks as C
import params as P
import render
import util as U

OUT = P.OUT
FIXED_TS = '2026-09-25T00:00:00'

DEVIATIONS = [
    'Centering tongues: full-height flexures (y 119.05..123.40, cut through the roof with U-slits) instead of 1.5-tall '
    'tongues floating mid-wall centred on y 119.4. A mid-wall horizontal cantilever is an 8 mm unsupported overhang when the '
    'cover prints roof-down. As built k = 2.92 N/mm (audit 0.75): 0.44 N at the 0.15 preload and 1.32 N at full float. '
    'Three pins give about 26 N/mm laterally, so they bend about 0.05 mm. Contact band y 119.05..121.60 covers the PCB edge '
    'both seated (118.61..120.21) and resting (118.40..120.00).',
    'Tongue face set 0.45 behind the PCB edge with a 0.60 bump (0.15 preload), so the rigid tongue root never touches the PCB at '
    'full float (0.15 clear). The contract says "0.15 bump"; read here as the 0.15 preload. The tongue bottom is at 119.05, not '
    '118.65, so the front tongue keeps 0.44 from the seated carrier flange (>= 0.40).',
    'Rod-carrier pins: printed pins cannot exist on a part printed flanges-down, because they would point into the bed. The two '
    'datum pins are steel dowels, Ø1.5 x 4 (ISO 8734, a stocked length), set in 5-minute epoxy in Ø1.55 x 2.4 slip holes, so '
    'they sit flush with the PCB top (no stake heads, roof clearance 1.39). Rev A: was Ø1.5 x 3 pressed into Ø1.45 x 1.5 '
    '(review MINOR-5: 7 % hoop strain in a 0.675 wall). The hole floor over the cradle crown is 0.30 (declared). The 4 stake '
    'holes are adhesive points: epoxy through the Ø1.6 PCB holes onto the flanges, now at z 13.10 / 18.30, with 0.3 x 0.3 '
    'glue-dam rebates along both flange inner edges. Heat-staking is dropped.',
    'C-cradle mouth faces -Y (away from the PCB), not +Y. The datum hole (-2.40, 16.00) sits directly above the rod end '
    '(x -3.0..-1.0), so the material above the rod must be solid to carry the dowel. Rev A (review MAJOR-1): the rod datums on '
    'the bore crown. Bore Ø4.15 centred at y 113.835, so the crown (115.91) puts the rod axis at 113.91, 2.00 below the LED '
    'faces. Below the equator each side is a curved lip flexure, 0.8 thick, rooted 56 deg above the equator behind a 0.4 slot, '
    'free 0.4 from both socket faces (1.4 long in x). Its hook (radius 1.84 about the rod axis, 4..12 deg below the equator) '
    'gives 0.16 interference and preloads the rod up onto the crown in any orientation. Snap-through 0.20 per lip (chord 3.60). '
    'The end walls widen to z 12.00..19.60 to make room (0.45 from the cover at full float).',
    'Socket depth 2.2 (contract 2.0): 0.20 axial play per end for a hand-cut 66.0 rod, and the end wall behind the socket stays '
    '1.0. Rod-end faces stay at x -3.0 / 63.0 nominal.',
    'Contract-forced thin walls, declared: the C1 pilot (Ø1.8) inside the 0.4-tall P3 pad leaves 0.75 / 0.85 (C1 at z 2.35, P3 '
    'z 0.7..4.1). The C2 pilot (x 60.90) leaves 0.80 to the header-notch face, moved 59.3 -> 59.2 (J1 body keeps 0.43 at full '
    'float). The dowel hole (Ø1.55) at x -2.40 leaves 0.625 to the end-wall inner face and a 0.30 floor over the cradle crown. '
    'The cradle lips are 0.8, the outer strip beside each slot 0.525. The glue-dam rebates leave 0.7 of the 1.0 flange. The '
    'engraved-text ribs are cosmetic, in the top 0.4 of a 1.8 roof.',
    'P3 pad z0 0.6 -> 0.7 and back-rail notch z -5.70 -> -5.80. The header body keeps 0.40 from the clip at full float '
    '(M-spec gave 0.30 / 0.32).',
    'Left leaf b 6.0 (z -2.5..3.5) -> 5.0 (z -3.0..2.0), and the left corner-finger side part z 2.0 -> 2.5..4.2. The M-spec leaf '
    'and finger side part overlap at z 2.0..3.5 on the same x; they are now 0.5 apart. Leaf k 2.84 N/mm, 1.14 N at 0.40 '
    '(M-spec 3.4 / 1.4). Rev A MINOR-7 narrowed it again to b 3.8 (z -2.4..1.4) with the 1.4 -> 1.0 taper.',
    'Roof underside 121.60 (1.8 roof). The tail pad is 0.20 proud at 121.40 (the stack datum) over x 52.9..59.0, z -5.6..0.5. '
    'Column bosses Ø5.2 run down to y 120.66 (0.45 above the seated PCB top) under the Ø4.4 x 1.0 counterbores. The contract '
    'columns are Ø3.6; rev A opens the bore 2.3 -> 2.5 (review MAJOR-3), so the wall is 0.55, declared thin (100 % infill, '
    'drill 2.4 through). Screws: ST2.2 x 6.5 pan, DIN 7981 form / PT-class plastics thread-former; head seat 122.40, tip '
    '115.90 (0.30 above the case top), 2.5 engaged at C0/C1 and 2.4 at C2.',
    'Cover walls sit 0.75 off the PCB edges (0.45 at full float), and the back-region walls are 2.0 thick so 1.0 remains behind '
    'the tongue slots. Skirt inner face at z 20.35 (contract >= 20.30), 2.0 thick. The front-region end walls sit at '
    'x -4.95 / 64.95. Rev A (review MAJOR-4): 3 grip ribs on each end face (x -6.25 / 66.25, z -6.5..1.5, centred over the '
    'posts, 0.5 proud, flat underside + 45-deg top flank) and a 0.6-deep fingernail ledge in the back wall (y 120.4..121.4, '
    'x 3..18 and 30..57). Envelope x -6.75..66.75, y 103.0..123.40, z -8.95..22.35 (M-spec -8.05..21.0).',
    'Clip pilots Ø1.8 (rev A, was 1.6) are through holes. Blind holes would leave 0.4-0.8 floors under P1/P3, below the 1.0 '
    'minimum wall.',
    'Corner fingers are 1.5 thick (M-spec 1.6; its printability table allows 1.5-1.6). Rev A: the back-finger and leaf bump crests '
    'are R0.3 rounds whose top keeps the 0.30 / 0.40 interference exact; the lip bottom inner edge is R0.5 (was a 0.3 chamfer); '
    'the back fingers and leaf taper 1.4 -> 1.0 with R1.5 root fillets, narrowed to b 7.6 / 3.8 so k stays at 8.7 / 2.8 N/mm; '
    'the back-rail outer face moves -8.05 -> -8.25 to meet the 1.4 finger roots. The tongue bumps get a 45-deg 0.50 lead-in '
    '(full crest from 119.55). The orientation arrow and "SCREEN" are engraved 0.4 deep, because the roof top is the print '
    'bed. The 0.2 elephant-foot chamfers are left to the slicer.',
]


def fix_step(path):
    t = path.read_text(errors='ignore')
    t = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', FIXED_TS, t)
    path.write_text(t)


def export(shape, stem, folder):
    folder.mkdir(parents=True, exist_ok=True)
    m = U.to_mesh(shape, 0.01, 0.1)
    m.export(str(folder / f'{stem}.stl'))
    cq.exporters.export(cq.Workplane().add(shape), str(folder / f'{stem}.step'), exportType='STEP')
    fix_step(folder / f'{stem}.step')
    return m


def write_3mf(path, items):
    """Minimal deterministic 3MF: items = [(name, trimesh, (dx, dy))]."""
    objs, build = [], []
    for i, (name, m, (dx, dy)) in enumerate(items, start=1):
        v = m.vertices + [dx, dy, 0]
        vs = ''.join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in v)
        ts = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        objs.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{vs}</vertices>'
                    f'<triangles>{ts}</triangles></mesh></object>')
        build.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Title">'
             'silkscreen-light-attachment housing rev A</metadata><resources>' + ''.join(objs) +
             '</resources><build>' + ''.join(build) + '</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, d in (('[Content_Types].xml', ct), ('_rels/.rels', rels), ('3D/3dmodel.model', model)):
            zi = zipfile.ZipInfo(n, date_time=(2026, 9, 25, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, d)


def exports(M):
    pr = OUT / 'print'
    meshes = {}
    for part, shape in (('clip', M.clip), ('cover', M.cover), ('carrier', M.car)):
        meshes[part] = export(C.to_print(shape, part), part, pr)
    # plate: place side by side on a 256 x 256 bed, all on Z = 0
    items, x = [], 10.0
    y0 = {'clip': 20.0, 'cover': 70.0, 'carrier': 130.0}
    for part in ('clip', 'cover', 'carrier'):
        m = meshes[part]
        lo, hi = m.bounds
        items.append((part, m, (10.0 - lo[0], y0[part] - lo[1])))
    write_3mf(pr / 'housing-plate.3mf', items)
    # E-frame references for renders and other tools (PCB seated, pins at 107.94)
    ef = OUT / 'E'
    ef.mkdir(parents=True, exist_ok=True)
    E = {}
    for n, s in (('clip', M.clip), ('cover', M.cover), ('carrier', M.car), ('rod', M.rod)):
        U.to_mesh(s).export(str(ef / f'{n}.stl'))
        E[n] = ef / f'{n}.stl'
    groups = {'pcb': ['board'], 'pins': [k for k in M.pcba if k.startswith('pin_')],
              'pcba_parts': [k for k in M.pcba if k != 'board' and not k.startswith('pin_')]}
    for g, names in groups.items():
        U.to_mesh(U.fuse(*[M.pcba[k] for k in names])).export(str(ef / f'{g}.stl'))
        E[g] = ef / f'{g}.stl'
    U.to_mesh(U.fuse(*M.dowels)).export(str(ef / 'dowels.stl'))
    E['dowels'] = ef / 'dowels.stl'
    try:
        j6 = cq.Shape.importBrep(str(P.STOCK / 'hardware' / 'cache' / 'J6.brep'))
        U.to_mesh(j6, 0.02, 0.2).export(str(ef / 'j6.stl'))
        E['j6'] = ef / 'j6.stl'
    except Exception:
        pass
    asm = cq.Assembly(name='housing_E')
    for n, s in (('clip', M.clip), ('cover', M.cover), ('carrier', M.car), ('rod', M.rod)):
        asm.add(s, name=n)
    asm.add(U.fuse(*M.pcba.values()), name='pcba_proxy')
    asm.add(U.fuse(*M.dowels), name='dowels')
    asm.save(str(ef / 'assembly_E.step'))
    fix_step(ef / 'assembly_E.step')
    return meshes, E


def check_exports(meshes, pngs):
    pr = OUT / 'print'
    files = {}
    ok = True
    for part in ('clip', 'cover', 'carrier'):
        for ext in ('stl', 'step'):
            f = pr / f'{part}.{ext}'
            files[f.name] = f.stat().st_size if f.exists() else 0
            ok &= files[f.name] > 1000
        m = meshes[part]
        ok &= bool(m.is_watertight) and abs(m.bounds[0][2]) < 1e-6
    f = pr / 'housing-plate.3mf'
    files[f.name] = f.stat().st_size if f.exists() else 0
    ok &= files[f.name] > 1000
    for p in pngs:
        files['render/' + p.name] = p.stat().st_size if p.exists() else 0
        ok &= files['render/' + p.name] > 5000
    want = {'assembly_iso.png', 'front.png', 'section_J6_x55.9.png', 'section_rod_x30.png'}
    ok &= want <= {p.name for p in pngs}
    return {'pass': bool(ok), 'files': files,
            'print_orientation': {'clip': 'top face y 118.40 on the bed', 'cover': 'roof top y 123.40 on the bed',
                                  'carrier': 'flanges (PCB face y 118.61) on the bed'},
            'watertight': {k: bool(m.is_watertight) for k, m in meshes.items()},
            'volumes_mm3': {k: round(float(m.volume), 1) for k, m in meshes.items()}}


def report(res):
    L = ['# Housing build report (rev A)', '',
         f'Generated by `housing/src/build.py` (deterministic, E frame). PCBA for the fit checks: {res["meta"]["pcba_source"]}; '
         f'{"; ".join(res["meta"]["pcba_notes"] or [])}.', '',
         '| Check | Result | Key numbers |', '|---|---|---|']
    c = res['checks']
    s1 = c['1_seated_vs_case']
    f = s1['features']
    L.append(f"| 1. Seated vs stock case | {'PASS' if s1['pass'] else 'FAIL'} | back bumps "
             f"{f['clip.back_bump_L'].get('depth')}/{f['clip.back_bump_R'].get('depth')}, leaf bump {f['clip.leaf_bump'].get('depth')}; "
             f"corner fingers gap {f['clip.corner_finger_L']['gap']}/{f['clip.corner_finger_R']['gap']}; boss {f['clip.boss']['gap']} |")
    s2 = c['2_insertion_sweep']
    L.append(f"| 2. Insertion sweep h 15 -> 0 | {'PASS' if s2['pass'] else 'FAIL'} | {s2['n_collisions']} undesigned collisions; "
             f"X guided from h {s2['guided_before_J6']['X_guide_h']}, Z from h {s2['guided_before_J6']['Z_guide_h']}, "
             f"pins touch J6 at h {s2['guided_before_J6']['pins_touch_J6_h(model face)']} |")
    s3 = c['3_pins_vs_J6']
    L.append(f"| 3. Pins vs J6 | {'PASS' if s3['pass'] else 'FAIL'} | tips {sorted(set(s3['tips_seated_y'].values()))}; "
             f"E {min(s3['engagement_by_J6_face'].values())}..{max(s3['engagement_by_J6_face'].values())}; wall clearance "
             f"{s3['pin_wall_clearance']['nominal']} nominal / {s3['pin_wall_clearance']['centred_+-0.05']} centred |")
    s4 = c['4_optics_keepout']
    L.append(f"| 4. Optics keep-out | {'PASS' if s4['pass'] else 'FAIL'} | intrusion "
             f"{ {k: v['intrusion_mm3'] for k, v in s4['parts'].items()} }; clip gap with float {s4['min_gap_with_engine_float']['clip']} |")
    s5 = c['5_float_extremes']
    L.append(f"| 5. PCBA/carrier at float extremes | {'PASS' if s5['pass'] else 'FAIL'} | carrier/rod min "
             f"{s5['carrier_rod_min_gap']}; PCBA min {s5['pcba_min_gap_excl_designed']} (>= 0.40, designed contacts excluded) |")
    xs = res['meta'].get('pcba_E_stl_crosscheck', {})
    if xs.get('present'):
        L.append(f"| 5b. PCB agent's E-frame PCBA STL (cross-check) | {'OK' if xs['tips_match'] else 'MISMATCH'} | y "
                 f"{xs['lowest_y (pin tips, expect 107.94)']}..{xs['highest_y (tail tips, expect 121.40)']}; part bodies to clip "
                 f"{xs['part_bodies_min_gap_clip']}, to cover {xs['part_bodies_min_gap_cover']} (seated nominal) |")
    s6 = c['6_printability']
    L.append(f"| 6. Printability | {'PASS' if s6['pass'] else 'FAIL'} | overhang patches flagged "
             f"{ {k: v['overhang_patches_flagged'] for k, v in s6['parts'].items()} }, all bridge-width; undeclared min wall "
             f"{ {k: v['thin_wall_min_undeclared'] for k, v in s6['parts'].items()} } |")
    s7 = c['7_exports']
    L.append(f"| 7. Exports | {'PASS' if s7['pass'] else 'FAIL'} | {len(s7['files'])} files |")
    s8 = c['8_rod_datum']
    L.append(f"| 8. Rod datum (rev A) | {'PASS' if s8['pass'] else 'FAIL'} | rod axis preloaded y {s8['rod_axis_preloaded']['y']}, "
             f"z {s8['rod_axis_preloaded']['z']} (target 113.91 / 15.80 +-0.05); LED gap {s8['gap_led_to_rod']}; lip interference "
             f"{sorted(set(v['interference'] for v in s8['lips'].values()))}; snap chord {s8['cradle']['snap_chord_at_hook']} |")
    s9 = c['9_tongue_lead_in']
    L.append(f"| 9. Tongue-bump lead-in (rev A) | {'PASS' if s9['pass'] else 'FAIL'} | full crest from y "
             f"{sorted(set(v['full_crest_from_y'] for v in s9['tongues'].values()))}; bump bottom "
             f"{sorted(set(v['bump_bottom_vs_pcb_edge'] for v in s9['tongues'].values()))} vs the PCB edge; overlap at landing "
             f"{max(v['pcb_top_at_bump_bottom_overlap_mm3'] for v in s9['tongues'].values())} mm3 |")
    sc = res['stack']['screws']
    L.append(f"| Screws (rev A) | {'PASS' if sc['pass'] else 'FAIL'} | {sc['screw']}; tip {sc['columns']['C0']['tip_y']}, above the case "
             f"{ {k: v['tip_above_case_top'] for k, v in sc['columns'].items()} }; engaged "
             f"{ {k: v['engaged'] for k, v in sc['columns'].items()} }; walls {sc['walls']} |")
    L += ['', f"**Overall: {'PASS' if res['pass'] else 'FAIL'}**", '', '## Rod datum and retention (check 8, rev A)', '',
          '```', json.dumps({k: s8[k] for k in ('rod_axis_preloaded', 'lips', 'led_face_y_min', 'gap_led_to_rod', 'cradle')},
                            indent=1), '```', '', '## Engagement order (as built, h above seated)', '',
          '| h | event |', '|---|---|']
    for o in s2['engagement_order']:
        L.append(f"| {o['h']} | {o['event']} |")
    L += ['', 'M-spec 3c / audit m1 for comparison: ' + '; '.join(f'{k} {v}' for k, v in s2['m_spec_3c_compare'].items()) + '.']
    L += ['', '## Seated gaps to the stock case, every clip feature (check 1)', '', '| feature | kind | gap | interference mm3 | depth |',
          '|---|---|---|---|---|']
    for k, v in s1['features'].items():
        if k.startswith('clip.'):
            L.append(f"| {k[5:]} | {v['kind']} | {v['gap']} | {v['interference_mm3']} | {v.get('depth', '')} |")
    others = {k: v['gap'] for k, v in s1['features'].items() if not k.startswith('clip.')}
    L += ['', f"Cover, carrier, rod and PCBA minimum gap to the case: {min(others.values()):.3f} "
          f"({min(others, key=others.get)}; the pins sit in the J6 opening).", '']
    st = res['stack']
    L += ['', '## Engagement stack (measured from the solids)', '',
          f"pad face {st['pad_face_y']} -> clip top {st['clip_top_y']} (+{st['clip_pad_to_top']}) -> tail pad {st['tail_pad_y']} "
          f"(+{st['cover_seat_to_pad']}) -> tip {st['tip_seated_y']} (off the case {st['tip_off_case_y']}); PCB underside "
          f"{st['pcb_underside_seated']}.", '',
          f"Engagement nominal {st['engagement_nominal']}; worst {st['engagement_worst']} (limits {P.E_MIN}/{P.E_MAX}, margins "
          f"{st['margins']}). M-spec 2d: {st['m_spec_2d']}.", '', '## Springs (PETG E 2.0 GPa)', '',
          '| spring | L | b | t | deflection | k N/mm | force N | strain % | M-spec / audit |', '|---|---|---|---|---|---|---|---|---|']
    for n, v in res['springs'].items():
        if n == 'retention':
            continue
        if n.startswith('tongue'):
            L.append(f"| {n} | {v['L_to_bump']} | {v['height']} | {v['t']} | 0.15 / 0.45 | {v['k_N_per_mm']} | "
                     f"{v['preload_N']} / {v['full_float_N']} | {v['strain_full_float_pct']} | {v['audit_M5']} |")
        else:
            L.append(f"| {n} | {v['L']} | {v['b']} | {v['t']} | {v['deflection_as_built']} ({v['deflection_range'][0]}.."
                     f"{v['deflection_range'][1]}) | {v['k_N_per_mm']} | {v['force_N']} ({v['force_range_N'][0]}..{v['force_range_N'][1]}) | "
                     f"{v['strain_nominal_pct']} / {v['strain_max_pct']} | {v['m_spec']} |")
    r = res['springs']['retention']
    L += ['', f"Retention about {r['total_N']} N (J6 {r['J6_N']} + friction {r['friction_N']}); insertion about "
          f"{r['insertion_N_approx']} N. {r['m_spec']}.", '', '## Deviations from DESIGN-SPEC', '']
    L += [f'{i}. {d}' for i, d in enumerate(DEVIATIONS, 1)]
    L += ['', '## Outputs', '', '- `out/print/{clip,cover,carrier}.{stl,step}`: print orientation, bed at Z 0.',
          '- `out/print/housing-plate.3mf`: one plate with all three parts.',
          '- `out/E/*.stl`, `out/E/assembly_E.step`: E-frame references (PCB seated).',
          '- `out/render/*.png`: assembly on the case (iso front/back), front view, section at x 55.9 (J6), section at x 30 (rod), '
          'section at x -2.1 (left cradle lips).',
          '- `out/checks.json`: every number behind this report.']
    if res.get('slice'):
        L += ['', '## OrcaSlicer', '', '```', json.dumps(res['slice'], indent=1), '```']
    (OUT / 'REPORT.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def main():
    t0 = time.time()
    args = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    log = lambda *a: print(*a, flush=True)
    log('building model ...')
    M = C.Model(log)
    res = {'meta': {'contract': 'design/DESIGN-SPEC.md sec 4', 'pcba_source': M.pcba_spec['source'],
                    'pcba_notes': M.pcba_notes, 'pcba_compare': M.pcba_cmp, 'stock_params': P.stock_params_check(),
                    'cradle': carrier.wrap_as_built()}, 'checks': {}}
    steps = [('1_seated_vs_case', lambda: C.check_seated(M)),
             ('2_insertion_sweep', (lambda: C.check_sweep(M, log)) if '--no-sweep' not in args else None),
             ('3_pins_vs_J6', lambda: C.check_pins(M)),
             ('4_optics_keepout', lambda: C.check_keepout(M)),
             ('5_float_extremes', lambda: C.check_float(M)),
             ('6_printability', lambda: C.check_print(M, C.declared_thin())),
             ('8_rod_datum', lambda: C.check_rod(M)),
             ('9_tongue_lead_in', lambda: C.check_tongue_lead(M))]
    for name, fn in steps:
        if fn is None:
            res['checks'][name] = {'pass': False, 'skipped': True}
            continue
        t = time.time()
        res['checks'][name] = fn()
        log(f"  {name}: {'PASS' if res['checks'][name]['pass'] else 'FAIL'} ({time.time() - t:.1f}s)")
    res['meta']['pcba_E_stl_crosscheck'] = C.compare_pcba_stl(M)
    res['springs'] = C.springs(res['checks']['1_seated_vs_case'])
    res['stack'] = C.stack(M)
    log(f"  stack: {'PASS' if res['stack']['pass'] else 'FAIL'}; screws: {'PASS' if res['stack']['screws']['pass'] else 'FAIL'}")
    t = time.time()
    meshes, E = exports(M)
    pngs = []
    if '--no-render' not in args:
        rd = OUT / 'render'
        rd.mkdir(exist_ok=True)
        pngs = render.render_set(E, P.STOCK_OUT, rd)
    res['checks']['7_exports'] = check_exports(meshes, pngs)
    log(f"  7_exports: {'PASS' if res['checks']['7_exports']['pass'] else 'FAIL'} ({time.time() - t:.1f}s)")
    slice_json = OUT / 'slice' / 'slice-report.json'
    if slice_json.exists():
        res['slice'] = json.loads(slice_json.read_text())
    res['pass'] = bool(all(v['pass'] for v in res['checks'].values()) and res['stack']['pass'] and
                       res['stack']['screws']['pass'])
    res['deviations'] = DEVIATIONS
    (OUT / 'checks.json').write_text(json.dumps(res, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else str(o)))
    report(res)
    log(f"OVERALL {'PASS' if res['pass'] else 'FAIL'} in {time.time() - t0:.0f}s")
    return 0 if res['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
