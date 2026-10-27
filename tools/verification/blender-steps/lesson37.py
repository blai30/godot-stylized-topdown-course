# Lesson 37, in Blender: the character's body by box modeling, all from one mesh. From character.blend (lesson 36): the
# blockout is deleted; one cube becomes half of the hips, the body grows from it by extrude, inset, and scale (a belt and
# chest by rings, arms, legs, a pack, a neck and a head), a Mirror modifier makes the other half, and the mesh is cleaned,
# shaded flat, and exported.
import math
import os
import sys

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top

STOP = os.environ.get('LESSON37_STOP', '')
# Rings: name, how far along the face's normal, then the ring's half width along X and half depth along Y.
TORSO_RINGS = [
    ('belt out', 0.0, 0.21, 0.15),
    ('belt', 0.04, 0.21, 0.15),
    ('belt in', 0.0, 0.20, 0.14),
    ('chest', 0.20, 0.20, 0.14),
    ('shoulders', 0.19, 0.20, 0.14),
]
SKIRT_RINGS = [
    ('skirt out', 0.0, 0.215, 0.15),
    ('skirt', 0.10, 0.215, 0.15),
    ('skirt in', 0.0, 0.20, 0.14),
]
HEAD_RINGS = [
    ('collar', 0.03, 0.08, 0.09),
    ('neck', 0.03, 0.05, 0.056),
    ('neck up', 0.06, 0.05, 0.056),
    ('jaw', 0.02, 0.085, 0.10),
    ('cheek', 0.07, 0.11, 0.125),
    ('brow', 0.06, 0.115, 0.13),
    ('crown', 0.07, 0.10, 0.115),
    ('top', 0.03, 0.06, 0.07),
]
WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
EXPORT = os.path.join(WORKBENCH, 'art', 'character')


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    viewport = d.area('VIEW_3D')

    def over_view():
        d.move(*d.center(viewport))

    def field(x, y, value):
        yield from d.press(x, top(y))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(str(value))
        yield 0.2
        d.key('RET')
        yield 0.35

    def typed(*values):
        for number, value in enumerate(values):
            if number:
                d.key('TAB')
            d.type_text(str(value))

    def search(text):
        over_view()
        d.key('F3')
        yield 0.8
        d.type_text(text)
        yield 1.2
        d.key('RET')
        yield 0.8

    def body_mesh():
        return bmesh.from_edit_mesh(bpy.data.objects['body'].data)

    def select_face(view_key, ctrl, predicate, note):
        # Face select mode, the view the face is visible from, and a click on the face's projected center.
        over_view()
        d.key(view_key, ctrl=ctrl)
        yield 0.8
        mesh = body_mesh()
        mesh.faces.ensure_lookup_table()
        body = bpy.data.objects['body']
        matches = [face for face in mesh.faces if predicate(face)]
        if len(matches) != 1:
            d.log('PICK {} matched {} faces'.format(note, len(matches)))
            raise RuntimeError('pick ' + note)
        face = matches[0]
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, body.matrix_world @ face.calc_center_median())
        d.click(region.x + int(local.x), region.y + int(local.y))
        yield 0.5
        mesh = body_mesh()
        chosen = [f for f in mesh.faces if f.select]
        d.log('PICK {} selected {} center {}'.format(note, len(chosen), tuple(round(v, 3) for v in chosen[0].calc_center_median()) if chosen else None))
        if len(chosen) != 1 or (chosen[0].calc_center_median() - face.calc_center_median()).length > 1e-4:
            raise RuntimeError('the click did not select ' + note)

    def extrude(distance):
        over_view()
        d.key('E')
        yield 0.3
        d.type_text(str(distance))
        d.key('RET')
        yield 0.5

    def scale(*values):
        over_view()
        d.key('S')
        typed(*values)
        d.key('RET')
        yield 0.5

    def inset(distance):
        over_view()
        d.key('I')
        yield 0.3
        d.type_text(str(distance))
        d.key('RET')
        yield 0.5

    def move(*values):
        over_view()
        d.key('G')
        typed(*values)
        d.key('RET')
        yield 0.5

    d.shot('l37_start')
    # The blockout did its job as a ruler: select every mesh and delete it.
    yield from search('select all by type mesh')
    over_view()
    d.key('X')
    yield 0.8
    d.shot('l37_delete')
    d.key('RET')
    yield 0.6
    d.log('OBJECTS after delete {}'.format([o.name for o in bpy.data.objects]))

    # One cube: the left half of the hips, 0.2 m across and 0.1 m tall, with its inner side on the center plane.
    over_view()
    d.key('A', shift=True)
    yield 0.8
    d.type_text('cube')
    yield 0.9
    d.key('RET')
    yield 0.8
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('body')
    d.key('RET')
    yield 0.5
    over_view()
    d.key('TAB')
    yield 0.6
    d.key('A')
    yield from scale(0.1, 0.14, 0.05)
    yield from move(0.1, 0, 0.95)
    d.shot('l37_half_hips')
    mesh = body_mesh()
    d.log('HALF HIPS x {} to {} z {} to {}'.format(round(min(v.co.x for v in mesh.verts), 3), round(max(v.co.x for v in mesh.verts), 3), round(min(v.co.z for v in mesh.verts), 3), round(max(v.co.z for v in mesh.verts), 3)))
    # The face on the center plane is inside the finished body: delete it.
    over_view()
    d.key('THREE')
    yield 0.5
    yield from select_face('NUMPAD_3', True, lambda face: face.normal.x < -0.9, 'left face')
    over_view()
    d.key('X')
    yield 0.8
    d.shot('l37_delete_face_menu')
    d.key('F')
    yield 0.6
    d.log('FACES after delete {}'.format(len(body_mesh().faces)))

    # The Mirror modifier, with Clipping off: Merge welds the halves on the center line.
    yield from d.press(1595, top(514))
    yield 0.6
    yield from d.press(1784, top(298))
    yield 0.8
    d.type_text('mirror')
    yield 1.0
    d.key('RET')
    yield 1.0
    d.shot('l37_mirror')
    d.log('MODIFIERS {}'.format([(m.name, m.type) for m in bpy.data.objects['body'].modifiers]))

    def rotate_y(degrees):
        over_view()
        d.key('R')
        d.key('Y')
        d.type_text(str(degrees))
        d.key('RET')
        yield 0.5

    def log_selected(note):
        mesh = body_mesh()
        chosen = [f for f in mesh.faces if f.select]
        center = Vector((0, 0, 0))
        for face in chosen:
            center += face.calc_center_median()
        center /= max(len(chosen), 1)
        d.log('{} faces {} selected {} at {}'.format(note, len(mesh.faces), len(chosen), tuple(round(v, 3) for v in center)))

    # A ring is an extrusion of the selected face, scaled to the ring's size. Scaling is about the face's own center, which
    # is not on the center line, so after each scale the face moves back by half its old width times the scale minus one,
    # keeping its inner edge on the line.
    state = {'half_x': 0.2, 'half_y': 0.14, 'z': 1.0}

    def ring(note, distance, half_x, half_y, sign=1):
        fx, fy = half_x / state['half_x'], half_y / state['half_y']
        yield from extrude(distance)
        if abs(fx - 1) > 1e-9 or abs(fy - 1) > 1e-9:
            yield from scale(fx, fy, 1)
            yield from move(state['half_x'] / 2 * (fx - 1), 0, 0)
        state.update(half_x=half_x, half_y=half_y, z=state['z'] + sign * distance)
        selected = [f for f in body_mesh().faces if f.select]
        xs = [v.co.x for v in selected[0].verts]
        zs = [v.co.z for v in selected[0].verts]
        d.log('RING {} z {:.3f} x {:.4f} to {:.4f} faces {}'.format(note, sum(zs) / len(zs), min(xs), max(xs), len(body_mesh().faces)))
        if len(selected) != 1 or abs(min(xs)) > 1e-4 or abs(max(xs) - half_x) > 1e-4:
            raise RuntimeError('ring off the center line: ' + note)

    # The belt and the chest: rings up from the top of the hips.
    yield from select_face('NUMPAD_7', False, lambda face: face.normal.z > 0.9 and abs(face.calc_center_median().z - 1.0) < 0.01, 'top of the hips')
    for ring_row in TORSO_RINGS:
        yield from ring(*ring_row)
    d.shot('l37_torso')
    if STOP == 'torso':
        return

    # The arm: the side face of the shoulders ring, an inset, squashed to arm size, and extrusions turned down.
    yield from select_face('NUMPAD_3', False, lambda face: face.normal.x > 0.9 and abs(face.calc_center_median().z - 1.335) < 0.01, 'side face')
    yield from inset(0.05)
    yield from scale(1, 0.55, 1.1)
    yield from move(0, 0, 0.03)
    log_selected('ARM FACE')
    d.shot('l37_arm_face')
    yield from extrude(0.04)
    yield from rotate_y(69.4)
    yield from extrude(0.43)
    log_selected('ARM END')
    yield from extrude(0.015)
    yield from scale(1.25, 1.25, 1.25)
    yield from extrude(0.1)
    log_selected('GLOVE')
    over_view()
    d.key('NUMPAD_1')
    yield 0.7
    d.shot('l37_arm')
    if STOP == 'arm':
        return

    # The skirt and the legs: rings down from the bottom of the hips, then the bottom face inset and squashed to a leg.
    yield from select_face('NUMPAD_7', True, lambda face: face.normal.z < -0.9 and abs(face.calc_center_median().z - 0.9) < 0.01, 'bottom face')
    state.update(half_x=0.2, half_y=0.14, z=0.9)
    for note, distance, half_x, half_y in SKIRT_RINGS:
        yield from ring(note, distance, half_x, half_y, sign=-1)
    yield from inset(0.035)
    yield from scale(1, 0.62, 1)
    log_selected('LEG FACE')
    for distance, factor in ((0.3, 0.95), (0.3, 0.95), (0.1, 1.15), (0.1, 1.0)):
        yield from extrude(distance)
        if factor != 1.0:
            yield from scale(factor, factor, 1)
    log_selected('FOOT')
    mesh = body_mesh()
    d.log('LOWEST {}'.format(round(min(v.co.z for v in mesh.verts), 4)))
    over_view()
    d.key('NUMPAD_1')
    yield 0.7
    d.shot('l37_legs')
    # The foot: the front of the boot, extruded forward.
    yield from select_face('NUMPAD_1', False, lambda face: face.normal.y < -0.9 and face.calc_center_median().z < 0.1 and face.calc_center_median().x > 0.05, 'boot front')
    yield from extrude(0.13)
    log_selected('TOE')
    if STOP == 'legs':
        return

    # The pack: both back faces of the chest and shoulders, extruded backward. Visible faces only: X-ray stays off.
    over_view()
    d.key('NUMPAD_1', ctrl=True)
    yield 0.8
    mesh = body_mesh()
    body = bpy.data.objects['body']
    backs = [f for f in mesh.faces if f.normal.y > 0.9 and 1.05 < f.calc_center_median().z < 1.42 and abs(f.calc_center_median().x - 0.1) < 0.011]
    wanted = {f.index for f in backs}
    d.log('PACK faces {}'.format(len(backs)))
    over_view()
    d.key('A', alt=True)
    yield 0.3
    region = d.region(viewport)
    first = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, Vector((0.15, 0.14, 1.07)))
    second = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, Vector((0.02, 0.14, 1.40)))
    over_view()
    d.key('B')
    yield 0.3
    yield from d.drag((region.x + int(first.x), region.y + int(first.y)), (region.x + int(second.x), region.y + int(second.y)))
    yield 0.5
    chosen = [f for f in body_mesh().faces if f.select]
    d.log('PACK selected {} {}'.format(len(chosen), [tuple(round(v, 3) for v in f.calc_center_median()) for f in chosen]))
    if {f.index for f in chosen} != wanted:
        raise RuntimeError('pack box select mismatch')
    yield from extrude(0.1)
    yield from scale(1, 1, 0.8)
    log_selected('PACK')
    if STOP == 'pack':
        return

    # The neck and the head: rings up from the top of the shoulders.
    yield from select_face('NUMPAD_7', False, lambda face: face.normal.z > 0.9 and abs(face.calc_center_median().z - 1.43) < 0.01, 'top of the shoulders')
    state.update(half_x=0.2, half_y=0.14, z=1.43)
    for ring_row in HEAD_RINGS:
        yield from ring(*ring_row)
    over_view()
    d.key('NUMPAD_1')
    yield 0.7
    d.shot('l37_head')
    d.key('NUMPAD_3')
    yield 0.7
    d.shot('l37_head_side')
    if STOP == 'head':
        return

    # The fringe: the front face of the crown ring, extruded forward.
    yield from select_face('NUMPAD_1', False, lambda face: face.normal.y < -0.9 and abs(face.calc_center_median().z - 1.755) < 0.02, 'fringe')
    yield from extrude(0.03)
    log_selected('FRINGE')
    d.shot('l37_fringe')
    if STOP == 'fringe':
        return

    # Apply the Mirror modifier: Object Mode, hover its panel, Ctrl+A.
    over_view()
    d.key('TAB')
    yield 0.6
    d.move(1760, top(331))
    yield 0.5
    d.key('A', ctrl=True)
    yield 0.8
    body = bpy.data.objects['body']
    d.log('APPLIED modifiers {} faces {} vertices {}'.format(len(body.modifiers), len(body.data.polygons), len(body.data.vertices)))
    d.shot('l37_applied')

    # The mirror leaves faces inside the body, along the center line; Select Interior Faces finds them and X deletes them.
    over_view()
    d.key('TAB')
    yield 0.6
    d.key('THREE')
    yield 0.4
    d.key('A', alt=True)
    yield 0.3
    yield from search('select interior faces')
    interior = [f for f in body_mesh().faces if f.select]
    d.log('INTERIOR faces {} centers x {}'.format(len(interior), sorted(set(round(f.calc_center_median().x, 3) for f in interior))))
    d.shot('l37_interior')
    over_view()
    d.key('X')
    yield 0.6
    d.key('F')
    yield 0.6
    d.log('FACES after cleaning {}'.format(len(body_mesh().faces)))
    over_view()
    d.key('TAB')
    yield 0.6
    yield from search('shade flat')
    joined = bpy.data.objects['body']
    d.log('FLAT {}'.format(all(not polygon.use_smooth for polygon in joined.data.polygons)))
    joined.data.calc_loop_triangles()
    d.log('TRIANGLES {} HEIGHT {:.4f} to {:.4f}'.format(len(joined.data.loop_triangles), min(v.co.z for v in joined.data.vertices), max(v.co.z for v in joined.data.vertices)))
    # The origin is already at the feet: the object was added at the 3D cursor, the world origin.
    d.log('ORIGIN {}'.format(tuple(joined.location)))
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.key('NUMPAD_MINUS')
    yield 0.4
    d.shot('l37_front')
    d.key('NUMPAD_3', ctrl=True)
    yield 0.8
    d.shot('l37_side')
    d.key('NUMPAD_1', ctrl=True)
    yield 0.8
    d.shot('l37_back')
    d.key('NUMPAD_7')
    yield 0.8
    d.shot('l37_top')
    d.key('NUMPAD_1')
    yield 0.4
    for name in ('NUMPAD_8', 'NUMPAD_8', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_5'):
        d.key(name)
        yield 0.3
    yield 0.5
    d.shot('l37_three_quarter')
    if STOP == 'joined':
        return

    # Export: the collection's exporter, pointed at character.glb, and save the file.
    yield from d.press(1595, top(449))
    yield 0.8
    yield from d.press(1892, top(763))
    yield 1.5
    browser = d.browser()
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('character.glb', target=browser)
    d.key('RET', target=browser)
    yield 0.4
    d.shot('l37_export_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    collection = bpy.data.collections['character']
    d.log('FILEPATH {}'.format(collection.exporters[0].export_properties.filepath))
    yield from d.press(1771, top(708))
    yield 2
    glb = os.path.join(EXPORT, 'character.glb')
    d.log('GLB exists {} size {}'.format(os.path.isfile(glb), os.path.getsize(glb) if os.path.isfile(glb) else 0))
    d.shot('l37_exported')
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
