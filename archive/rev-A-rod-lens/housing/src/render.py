"""Offscreen VTK renders of the housing on the stock case (E frame STLs)."""
from pathlib import Path

import vtk


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def render(out_png, parts, view, up, focus, clip=None, size=(1400, 1000), ortho=False, bg='#f4f1ea', zoom=1.0):
    """parts: [(stl_path, '#rrggbb', opacity)], view: camera direction FROM the focus,
    clip: (axis, value, keep_positive) cuts everything on one side of a plane."""
    ren = vtk.vtkRenderer()
    ren.SetBackground(*_rgb(bg))
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(*size)
    win.AddRenderer(ren)
    translucent = any(o < 1 for _p, _c, o in parts)
    if translucent:
        win.SetAlphaBitPlanes(1)
        win.SetMultiSamples(0)
        ren.SetUseDepthPeeling(1)
        ren.SetMaximumNumberOfPeels(40)
    else:
        win.SetMultiSamples(8)
    for path, color, opacity in parts:
        if not Path(path).exists():
            continue
        r = vtk.vtkSTLReader()
        r.SetFileName(str(path))
        src = r
        if clip:
            ax, val, keep_pos = clip
            n = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[ax]
            n = n if keep_pos else tuple(-v for v in n)
            pl = vtk.vtkPlane()
            pl.SetOrigin(*(val if n[i] else 0 for i in range(3)))
            pl.SetNormal(*n)
            c = vtk.vtkClipPolyData()
            c.SetInputConnection(src.GetOutputPort())
            c.SetClipFunction(pl)
            src = c
        nm = vtk.vtkPolyDataNormals()
        nm.SetInputConnection(src.GetOutputPort())
        nm.SetFeatureAngle(35)
        nm.SplittingOn()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nm.GetOutputPort())
        a = vtk.vtkActor()
        a.SetMapper(mp)
        pr = a.GetProperty()
        pr.SetColor(*_rgb(color))
        pr.SetOpacity(opacity)
        pr.SetAmbient(0.3)
        pr.SetDiffuse(0.7)
        pr.SetSpecular(0.15)
        bp = vtk.vtkProperty()
        bp.SetColor(*(min(1, v * 0.5 + 0.35) for v in _rgb(color)))
        bp.SetAmbient(0.6)
        a.SetBackfaceProperty(bp)
        ren.AddActor(a)
    cam = ren.GetActiveCamera()
    cx, cy, cz = ((focus[0] + focus[1]) / 2, (focus[2] + focus[3]) / 2, (focus[4] + focus[5]) / 2)
    cam.SetFocalPoint(cx, cy, cz)
    cam.SetPosition(cx + view[0] * 400, cy + view[1] * 400, cz + view[2] * 400)
    cam.SetViewUp(*up)
    if ortho:
        cam.ParallelProjectionOn()
    ren.ResetCamera(*focus)
    cam.Zoom(zoom)
    ren.ResetCameraClippingRange()
    lk = vtk.vtkLightKit()
    lk.AddLightsToRenderer(ren)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(str(out_png))
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    return out_png


def render_set(E, case_dir, out_dir):
    """E: dict name -> E-frame STL path. Returns the PNG paths."""
    C = {'tub': (case_dir / 'tub.stl', '#d9d4c7', 1.0), 'lid': (case_dir / 'lid.stl', '#c9c3b4', 1.0)}
    col = {'clip': '#4a4a4a', 'cover': '#3d424c', 'carrier': '#666666', 'rod': '#8fd3ff', 'pcb': '#1f6e43',
           'pcba_parts': '#e8e2c8', 'pins': '#d4af37', 'dowels': '#b0b0b0', 'j6': '#8a8a8a'}
    parts = [C['tub'], C['lid']] + [(E[n], col[n], 1.0) for n in E if n in col and n != 'rod'] + [(E['rod'], col['rod'], 0.85)]
    out = []
    near = (-12, 72, 96, 126, -12, 26)
    out.append(render(out_dir / 'assembly_iso.png', parts, (0.55, 0.55, 0.75), (0, 1, 0), near, zoom=1.1))
    out.append(render(out_dir / 'assembly_iso_back.png', parts, (-0.5, 0.45, -0.8), (0, 1, 0), near, zoom=1.1))
    out.append(render(out_dir / 'front.png', parts, (0, 0, 1), (0, 1, 0), (-10, 70, 98, 126, -12, 26), ortho=True, zoom=1.05))
    sec = [C['tub'], C['lid']] + [(E[n], col[n], 1.0) for n in E if n in col]
    out.append(render(out_dir / 'section_J6_x55.9.png', sec, (-1, 0, 0), (0, 1, 0), (55.9, 55.9, 100, 126, -12, 24),
                      clip=('x', 55.9, True), ortho=True, zoom=1.0))
    out.append(render(out_dir / 'section_rod_x30.png', sec, (-1, 0, 0), (0, 1, 0), (30, 30, 100, 126, -12, 24),
                      clip=('x', 30.0, True), ortho=True, zoom=1.0))
    out.append(render(out_dir / 'section_cradle_x-2.1.png', sec, (-1, 0, 0), (0, 1, 0), (-2.1, -2.1, 108, 121, 10, 22),
                      clip=('x', -2.1, True), ortho=True, zoom=1.0))
    return out
