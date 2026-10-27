# Lesson 38, in Blender: the character's UVs. From character.blend (lesson 37): the UV Editing workspace, every face
# collapsed onto a flat color cell of the texture plan, the head projected from the front onto the face patch, and the
# layout saved. The painting itself is lesson 38's Krita run.
import os
import sys

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top
from character_uv_data import SWATCHES, FACE_CENTER, center

STOP = os.environ.get('LESSON38_STOP', '')
WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
# The UV Vertex panel in the UV editor's sidebar: X and Y fields.
UV_X, UV_Y = (638, 123), (638, 142)


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    body = bpy.data.objects['body']

    # Switch to the UV Editing workspace: its tab at the top.
    yield from d.press(495, top(13))
    yield 2.5
    viewport = d.area('VIEW_3D')
    uv = d.area('IMAGE_EDITOR')
    d.shot('l38_workspace')
    # Turn UV Sync Selection off (the arrows button at the UV editor's header): with it on, a UV edit also moves the corners
    # of the neighboring faces that share a vertex. Off, the UV editor shows and moves only the selected faces.
    yield from d.press(57, top(38))
    yield 0.6
    d.log('SYNC {}'.format(bpy.context.tool_settings.use_uv_select_sync))

    def over_view():
        d.move(*d.center(viewport))

    def over_uv():
        d.move(*d.center(uv))

    def mesh():
        bm = bmesh.from_edit_mesh(body.data)
        bm.faces.ensure_lookup_table()
        return bm

    def screen(point):
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, body.matrix_world @ point)
        return region.x + int(local.x), region.y + int(local.y)

    def selected_count():
        return sum(1 for face in mesh().faces if face.select)

    def type_field(position, value):
        yield from d.press(position[0], top(position[1]))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text('{:.4f}'.format(value))
        yield 0.2
        d.key('RET')
        yield 0.35

    def place(name_or_point, note):
        # With faces selected, collapse their UVs to one point and move it: S 0 in the UV editor, then the UV Vertex fields.
        target = center(name_or_point) if isinstance(name_or_point, str) else name_or_point
        over_uv()
        d.key('A')
        yield 0.3
        d.key('S')
        d.type_text('0')
        d.key('RET')
        yield 0.5
        yield from type_field(UV_X, target[0])
        yield from type_field(UV_Y, target[1])
        bm = mesh()
        layer = bm.loops.layers.uv.active
        moved = [loop[layer].uv.copy() for face in bm.faces if face.select for loop in face.loops]
        mid = sum(moved, Vector((0, 0))) / len(moved)
        spread = max((uv_point - mid).length for uv_point in moved)
        d.log('PLACED {} faces {} at ({:.3f}, {:.3f}) spread {:.4f}'.format(note, selected_count(), mid.x, mid.y, spread))
        if abs(mid.x - target[0]) > 0.002 or abs(mid.y - target[1]) > 0.002 or spread > 0.002:
            raise RuntimeError('UVs did not land: ' + note)

    def box_select(note, view_key, ctrl, boxes, axes):
        # Face select with X-ray, B drags over each box (each adds to the selection), and a check against the faces whose
        # centers lie inside the boxes.
        over_view()
        d.key(view_key, ctrl=ctrl)
        yield 0.7
        bm = mesh()
        expected = {face.index for face in bm.faces for low, high in boxes if all(low[i] <= face.calc_center_median()[axes[i]] <= high[i] for i in range(2))}
        over_view()
        d.key('A', alt=True)
        yield 0.3
        for low, high in boxes:
            corners = []
            for corner_values in (low, high):
                corner = Vector((0, 0, 0))
                corner[axes[0]] = corner_values[0]
                corner[axes[1]] = corner_values[1]
                corners.append(screen(corner))
            over_view()
            d.key('B')
            yield 0.3
            yield from d.drag(corners[0], corners[1])
            yield 0.5
        chosen = {face.index for face in mesh().faces if face.select}
        d.log('BOX {} expected {} selected {} missing {} extra {}'.format(note, len(expected), len(chosen), len(expected - chosen), len(chosen - expected)))
        if chosen != expected:
            raise RuntimeError('box select mismatch ' + note)

    def island(note, view_key, ctrl, point, normal_test):
        # Click the face nearest the point (one that faces the view), then Ctrl+L selects what is linked to it.
        over_view()
        d.key(view_key, ctrl=ctrl)
        yield 0.7
        bm = mesh()
        faces = [face for face in bm.faces if normal_test(face.normal)]
        face = min(faces, key=lambda f: (f.calc_center_median() - Vector(point)).length)
        over_view()
        d.key('A', alt=True)
        yield 0.3
        x, y = screen(face.calc_center_median())
        d.click(x, y)
        yield 0.4
        over_view()
        d.key('L', ctrl=True)
        yield 0.5
        chosen = {f.index for f in mesh().faces if f.select}
        linked = {face.index}
        stack = [face]
        while stack:
            current = stack.pop()
            for edge in current.edges:
                for other in edge.link_faces:
                    if other.index not in linked:
                        linked.add(other.index)
                        stack.append(other)
        d.log('ISLAND {} faces {} expected {} at {}'.format(note, len(chosen), len(linked), tuple(round(v, 3) for v in face.calc_center_median())))
        if chosen != linked:
            raise RuntimeError('island mismatch ' + note)

    # Everything starts on the tunic's color; the 3D view is in face select mode, front view.
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('THREE')
    yield 0.5
    d.key('A')
    yield 0.4
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.key('NUMPAD_MINUS')
    yield 0.4
    # The UV editor's sidebar: N, on its Image tab, holds the UV Vertex fields.
    over_uv()
    d.key('N')
    yield 1.0
    d.shot('l38_all_selected')
    yield from place('tunic', 'everything')
    d.shot('l38_tunic')
    over_view()
    d.key('Z', alt=True)
    yield 0.5
    if STOP == 'tunic':
        return

    FRONT, SIDE = (0, 2), (1, 2)
    yield from box_select('neck', 'NUMPAD_1', False, [((-0.09, 1.45), (0.09, 1.545))], FRONT)
    yield from place('skin', 'neck')
    yield from box_select('legs', 'NUMPAD_1', False, [((-0.2, 0.22), (0.2, 0.78))], FRONT)
    yield from place('trousers', 'legs')
    yield from box_select('boots', 'NUMPAD_1', False, [((-0.2, -0.02), (0.2, 0.19))], FRONT)
    yield from place('boots', 'boots')
    yield from box_select('sleeves', 'NUMPAD_1', False, [((0.22, 0.96), (0.46, 1.30)), ((-0.46, 0.96), (-0.22, 1.30))], FRONT)
    yield from place('shirt', 'sleeves')
    yield from box_select('gloves', 'NUMPAD_1', False, [((0.28, 0.78), (0.46, 0.955)), ((-0.46, 0.78), (-0.28, 0.955))], FRONT)
    yield from place('leather', 'gloves')
    yield from box_select('belt', 'NUMPAD_1', False, [((-0.23, 0.99), (0.23, 1.05))], FRONT)
    yield from place('leather', 'belt')
    yield from box_select('pack', 'NUMPAD_3', False, [((0.15, 1.05), (0.30, 1.42))], SIDE)
    yield from place('pack', 'pack')
    d.shot('l38_bodies')
    if STOP == 'boxes':
        return

    # The head: its faces, projected from the front onto the face patch; then the hair, over the top of it.
    yield from box_select('head', 'NUMPAD_1', False, [((-0.13, 1.555), (0.13, 1.83))], FRONT)
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('F3')
    yield 0.8
    d.type_text('project from view bounds')
    yield 1.2
    d.shot('l38_project_search')
    d.key('RET')
    yield 1.0
    d.shot('l38_projected')
    bm = mesh()
    layer = bm.loops.layers.uv.active
    points = [loop[layer].uv.copy() for face in bm.faces if face.select for loop in face.loops]
    d.log('PROJECTED faces {} u {:.3f} to {:.3f} v {:.3f} to {:.3f}'.format(selected_count(), min(p.x for p in points), max(p.x for p in points), min(p.y for p in points), max(p.y for p in points)))
    head_faces = [face for face in mesh().faces if face.select]
    head_points = [vert.co.copy() for face in head_faces for vert in face.verts]
    xs, zs = [p.x for p in head_points], [p.z for p in head_points]
    xmin, xmax, zmin, zmax = min(xs), max(xs), min(zs), max(zs)
    d.log('HEAD BOUNDS x {:.4f} {:.4f} z {:.4f} {:.4f}'.format(xmin, xmax, zmin, zmax))
    over_uv()
    d.key('A')
    yield 0.3
    d.key('S')
    d.type_text('0.45')
    d.key('RET')
    yield 0.6
    # The sidebar shows the selection's median, which is not the middle of its bounds for a head: type the median that puts
    # the bounds' middle on the patch's center.
    points = [loop[layer].uv.copy() for face in mesh().faces if face.select for loop in face.loops]
    median = sum(points, Vector((0, 0))) / len(points)
    middle = Vector(((min(p.x for p in points) + max(p.x for p in points)) / 2, (min(p.y for p in points) + max(p.y for p in points)) / 2))
    target = Vector(FACE_CENTER) + (median - middle)
    d.log('HEAD median {:.4f} {:.4f} bounds middle {:.4f} {:.4f} typed {:.4f} {:.4f}'.format(median.x, median.y, middle.x, middle.y, target.x, target.y))
    yield from type_field(UV_X, target.x)
    yield from type_field(UV_Y, target.y)
    points = [loop[layer].uv.copy() for face in mesh().faces if face.select for loop in face.loops]
    d.log('HEAD UV u {:.3f} to {:.3f} v {:.3f} to {:.3f}'.format(min(p.x for p in points), max(p.x for p in points), min(p.y for p in points), max(p.y for p in points)))
    d.shot('l38_head_uv')
    yield from box_select('hair', 'NUMPAD_3', False, [((-0.2, 1.705), (0.2, 1.83)), ((0.05, 1.555), (0.2, 1.705))], SIDE)
    yield from place('hair', 'hair')
    d.shot('l38_pieces')
    if STOP == 'head':
        return

    # Where the eyes go: the head's own bounds map linearly onto the face patch, so a point on the face has a place on it.
    for name, (x, z) in (('eye_left', (0.05, 1.68)), ('eye_right', (-0.05, 1.68)), ('mouth', (0.0, 1.60)), ('blush_left', (0.085, 1.625)), ('blush_right', (-0.085, 1.625))):
        u = 0.5 + 0.45 * x / (xmax - xmin)
        v = 0.5 + 0.5 * (z - zmin) / (zmax - zmin)
        d.log('FACE {} u {:.4f} v {:.4f}'.format(name, u, v))

    # Every face's UVs now lie in one cell or on the face patch; read them all back.
    over_view()
    d.key('TAB')
    yield 0.8
    bm = bmesh.new()
    bm.from_mesh(body.data)
    layer = bm.loops.layers.uv.active
    tally = {}
    for face in bm.faces:
        mid = sum((loop[layer].uv for loop in face.loops), Vector((0, 0))) / len(face.loops)
        if mid.y > 0.5:
            key = 'face patch'
        else:
            key = [name for name, (column, row, _) in SWATCHES.items() if column * 0.25 <= mid.x <= (column + 1) * 0.25 and row * 0.25 <= mid.y <= (row + 1) * 0.25][0]
        tally[key] = tally.get(key, 0) + 1
    bm.free()
    d.log('CELLS {}'.format(sorted(tally.items())))
    d.shot('l38_done')
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
