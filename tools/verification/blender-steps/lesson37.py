# Lesson 37, in Blender: the character's body by box modeling. From character.blend (lesson 36): the blockout is deleted;
# one cube becomes half the torso, the body grows from it by inset and extrude, a Mirror modifier makes the other half,
# and a few separate pieces (head, hair, nose, pack, collar, feet) are added, joined, shaded flat, and exported.
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

    # One cube: half the torso and hips. Its mesh is moved so its left side lies on the center plane; the object stays
    # at the origin, which is where the Mirror modifier mirrors.
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
    yield from scale(0.1, 0.14, 0.265)
    yield from move(0.1, 0, 1.165)
    d.shot('l37_half_torso')
    mesh = body_mesh()
    d.log('HALF TORSO x {} to {} z {} to {}'.format(round(min(v.co.x for v in mesh.verts), 3), round(max(v.co.x for v in mesh.verts), 3), round(min(v.co.z for v in mesh.verts), 3), round(max(v.co.z for v in mesh.verts), 3)))
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
    if STOP == 'torso':
        return

    # The Mirror modifier: Modifiers tab, Add Modifier, search. Merge welds the two halves where they meet.
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
    if STOP == 'mirror':
        return

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
        d.log('{} faces {} selected {} at {} normal {}'.format(note, len(mesh.faces), len(chosen), tuple(round(v, 3) for v in center), tuple(round(v, 2) for v in chosen[0].normal) if chosen else None))

    # The arm: the torso's side face, an inset, a squash to arm size, and extrusions turned down.
    yield from select_face('NUMPAD_3', False, lambda face: face.normal.x > 0.9 and face.calc_center_median().z > 1.0, 'side face')
    yield from inset(0.09)
    yield from scale(1, 1, 0.29)
    yield from move(0, 0, 0.2)
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

    # The legs: the bottom face, inset to leave a gap at the center, squashed to leg width, then extruded down.
    yield from select_face('NUMPAD_7', True, lambda face: face.normal.z < -0.9 and abs(face.calc_center_median().z - 0.9) < 0.01, 'bottom face')
    yield from inset(0.035)
    yield from scale(1, 0.62, 1)
    log_selected('LEG FACE')
    for distance, factor in ((0.4, 0.95), (0.3, 0.95), (0.1, 1.15), (0.1, 1.0)):
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

    # The foot: the front of the boot's last segment, extruded forward.
    yield from select_face('NUMPAD_1', False, lambda face: face.normal.y < -0.9 and face.calc_center_median().z < 0.1 and face.calc_center_median().x > 0.05, 'boot front')
    yield from extrude(0.13)
    log_selected('TOE')
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('A')
    yield 0.4
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.key('NUMPAD_MINUS')
    yield 0.4
    d.key('A', alt=True)
    yield 0.4
    d.shot('l37_body_front')
    over_view()
    d.key('NUMPAD_3', ctrl=True)
    yield 0.8
    d.shot('l37_body_side')
    # The neck: the top face, extruded up, squashed to neck size, and moved back onto the center plane.
    yield from select_face('NUMPAD_7', False, lambda face: face.normal.z > 0.9 and abs(face.calc_center_median().z - 1.43) < 0.01, 'top face')
    yield from extrude(0.0)
    yield from scale(0.25, 0.4, 1)
    yield from move(-0.075, 0, 0)
    yield from extrude(0.14)
    log_selected('NECK')
    mesh = body_mesh()
    d.log('NECK x {} to {}'.format(round(min(v.co.x for v in mesh.verts if v.co.z > 1.45), 3), round(max(v.co.x for v in mesh.verts if v.co.z > 1.45), 3)))
    over_view()
    d.key('NUMPAD_1')
    yield 0.7
    d.shot('l37_neck')

    # Apply the Mirror modifier: hover it and press Ctrl+A. Object Mode first, so the pieces are separate objects.
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
    if STOP == 'applied':
        return

    # The separate pieces: head, hair, nose, pack. Each is added, sized in the redo panel, and named.
    PANEL = {'ico sphere': {'subdivisions': 767, 'radius': 789}, 'cube': {'size': 789}}
    LOCATION = (855, 874, 894)
    state = {'open': False}

    def piece(name, shape, numbers, scale_values, location, turn=0):
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text(shape)
        yield 0.9
        d.key('RET')
        yield 0.9
        if not state['open']:
            yield from d.press(75, top(963))
            yield 0.8
            state['open'] = True
        for label, value in zip(('subdivisions', 'radius') if shape == 'ico sphere' else ('size',), numbers):
            yield from field(257, PANEL[shape][label], value)
        for y, value in zip(LOCATION, location):
            if value:
                yield from field(257, y, value)
        if turn:
            yield from field(257, 937, turn)
        over_view()
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
        over_view()
        d.key('S')
        typed(*scale_values)
        d.key('RET')
        yield 0.4
        d.key('A', ctrl=True)
        yield 0.6
        d.key('S')
        yield 0.5
        obj = bpy.data.objects[name]
        d.log('PIECE {} faces {} location {} dimensions {}'.format(name, len(obj.data.polygons), tuple(round(v, 3) for v in obj.location), tuple(round(v, 3) for v in obj.dimensions)))

    PIECES = [
        ('head', 'ico sphere', (2, 1.0), (0.115, 0.125, 0.14), (0.0, 0.0, 1.66), 0),
        ('nose', 'cube', (2,), (0.017, 0.022, 0.027), (0.0, -0.135, 1.64), 0),
        ('hair', 'ico sphere', (2, 1.0), (0.135, 0.14, 0.125), (0.0, 0.02, 1.675), 0),
        ('hair_back', 'ico sphere', (1, 1.0), (0.11, 0.08, 0.11), (0.0, 0.115, 1.65), 0),
        ('fringe_1', 'cube', (2,), (0.035, 0.035, 0.035), (-0.08, -0.105, 1.745), 18),
        ('fringe_2', 'cube', (2,), (0.035, 0.035, 0.035), (0.0, -0.11, 1.755), 0),
        ('fringe_3', 'cube', (2,), (0.035, 0.035, 0.035), (0.08, -0.105, 1.745), -18),
        ('pack', 'cube', (2,), (0.14, 0.07, 0.15), (0.0, 0.18, 1.22), 0),
        ('belt', 'cube', (2,), (0.21, 0.15, 0.03), (0.0, 0.0, 1.03), 0),
        ('skirt', 'cube', (2,), (0.22, 0.155, 0.085), (0.0, 0.0, 0.86), 0),
        ('pad.L', 'ico sphere', (1, 1.0), (0.085, 0.085, 0.075), (0.215, 0.0, 1.40), 0),
        ('pad.R', 'ico sphere', (1, 1.0), (0.085, 0.085, 0.075), (-0.215, 0.0, 1.40), 0),
    ]
    for row in PIECES:
        yield from piece(*row)
        if row[0] in ('head', 'skirt'):
            d.shot('l37_piece_' + row[0])

    # Join everything into the body: select every mesh, Ctrl+click the body row so it is the active one, Ctrl+J.
    yield from search('select all by type mesh')
    yield from d.press(1700, top(184), ctrl=True)
    yield 0.5
    d.log('SELECTED {} active {}'.format(len(bpy.context.selected_objects), bpy.context.active_object.name))
    over_view()
    d.key('J', ctrl=True)
    yield 1.0
    d.log('JOINED objects {}'.format([o.name for o in bpy.data.objects]))
    joined = bpy.data.objects['body']
    d.log('FACES {} VERTICES {}'.format(len(joined.data.polygons), len(joined.data.vertices)))
    yield from search('shade flat')
    d.log('FLAT {}'.format(all(not polygon.use_smooth for polygon in joined.data.polygons)))
    joined.data.calc_loop_triangles()
    d.log('TRIANGLES {} HEIGHT {:.4f} to {:.4f}'.format(len(joined.data.loop_triangles), min(v.co.z for v in joined.data.vertices), max(v.co.z for v in joined.data.vertices)))
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
