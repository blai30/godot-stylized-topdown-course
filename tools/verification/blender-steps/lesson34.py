# Lesson 34, in Blender: pebbles and a mushroom, each a rounded box (a cube and Subdivision Surface), colored with the
# Paint Part group kept from lesson 30, and exported in the same grass.glb. Opens art_source/nature/grass/grass.blend.
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, object_menu, top

STOP = os.environ.get('LESSON34_STOP', '')
WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
EXPORT = os.path.join(WORKBENCH, 'art', 'nature', 'grass')

# name, size (half the cube's width, depth, and height, in meters), where it stands, and its color
# name, half sizes, how far along X it stands apart while it is built, and how far its mesh is lifted so it rests on the ground
PEBBLE_A = ('pebble_a', (0.09, 0.07, 0.045), -0.5, 0.0375)
PEBBLE_B = ('pebble_b', (0.06, 0.075, 0.038), -0.3, 0.0315)
STEM = ('mushroom_stem', (0.015, 0.015, 0.07), 0.3, 0.0595)
CAP = ('mushroom_cap', (0.07, 0.07, 0.035), 0.3, 0.15)
GRAY, GRAY_LIGHT = (0.16, 0.16, 0.17, 0.0), (0.24, 0.23, 0.22, 0.0)
CREAM, RED = (0.62, 0.52, 0.36, 0.0), (0.5, 0.06, 0.05, 0.0)


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    viewport = d.area('VIEW_3D')
    d.shot('l34_start')

    def over_view():
        d.move(*d.center(viewport))

    def activate(*names):
        for obj in bpy.context.view_layer.objects:
            obj.select_set(False)
        for name in names:
            bpy.data.objects[name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[names[-1]]

    def typed(*values):
        for number, value in enumerate(values):
            if number:
                d.key('TAB')
            d.type_text(str(value))

    def rounded_box(name, size, apart, lift):
        # A cube, scaled to the size and applied, moved to its place, and rounded with Subdivision Surface.
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text('cube')
        yield 0.8
        d.key('RET')
        yield 0.8
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
        over_view()
        d.key('S')
        typed(*size)
        d.key('RET')
        yield 0.4
        d.key('A', ctrl=True)
        yield 0.6
        d.key('S')
        yield 0.5
        # In Edit Mode the mesh itself moves up, so the object's origin stays on the ground.
        d.key('TAB')
        yield 0.5
        d.key('A')
        d.key('G')
        d.key('Z')
        d.type_text(str(lift))
        d.key('RET')
        yield 0.4
        d.key('TAB')
        yield 0.5
        d.key('G')
        d.key('X')
        d.type_text(str(apart))
        d.key('RET')
        yield 0.5
        yield from d.press(1595, top(514))
        yield 0.6
        yield from d.press(1784, top(298))
        yield 0.8
        d.type_text('subdivision')
        yield 1.0
        d.key('RET')
        yield 1.0
        d.move(1700, top(331))
        yield 0.5
        d.key('A', ctrl=True)
        yield 0.8
        obj = bpy.data.objects[name]
        d.log('BOX {} location {} lowest {} modifiers {} faces {} scale {} dims {}'.format(name, tuple(round(v, 3) for v in obj.location), round(min(v.co.z for v in obj.data.vertices), 4), len(obj.modifiers), len(obj.data.polygons), tuple(obj.scale), tuple(round(v, 3) for v in obj.dimensions)))

    for box in (PEBBLE_A, PEBBLE_B, STEM, CAP):
        yield from rounded_box(*box)
        d.shot('l34_' + box[0])
    over_view()
    d.key('A')
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l34_boxes')
    if STOP == 'pebble':
        return

    # Paint Part, from lesson 30, is still in the file: the modifier picks it from its group list.
    activate('pebble_a')
    yield 0.4
    yield from d.press(1595, top(514))
    yield 0.6
    yield from d.press(1784, top(298))
    yield 0.8
    d.type_text('geometry nodes')
    yield 1.0
    d.shot('l34_add_geometry_nodes')
    d.key('RET')
    yield 1.0
    d.shot('l34_gn_modifier')
    yield from slow_click(d, 1642, top(361))
    yield 1.0
    d.shot('l34_group_list')
    yield from slow_click(d, 1668, top(392))
    yield 1.0
    d.shot('l34_group_chosen')

    def paint_values(name, color):
        activate(name)
        yield 0.3
        for y, value in zip((391, 416, 441, 466), color):
            yield from d.press(1797, top(y))
            yield 0.2
            d.key('A', ctrl=True)
            d.type_text(str(value))
            d.key('RET')
            yield 0.3
        modifier = bpy.data.objects[name].modifiers[0]
        group = modifier.node_group
        got = [round(getattr(modifier.properties.inputs, item.identifier).value, 3) for item in group.interface.items_tree if item.in_out == 'INPUT' and item.socket_type == 'NodeSocketFloat']
        d.log('PAINT {} {} group {}'.format(name, got, group.name))
        if got != list(color):
            raise RuntimeError('paint values of {} are {}'.format(name, got))

    yield from paint_values('pebble_a', GRAY)
    d.shot('l34_paint_values')
    # Copy Modifiers puts the same modifier on the others, and each gets its own numbers.
    activate('pebble_b', 'mushroom_stem', 'mushroom_cap', 'pebble_a')
    yield 0.4
    yield from object_menu(d)
    yield from slow_click(d, 369, top(469))
    yield 0.8
    yield from d.press(548, top(636))
    yield 0.8
    d.log('MODIFIERS {}'.format([(n, [m.name for m in bpy.data.objects[n].modifiers]) for n in ('pebble_a', 'pebble_b', 'mushroom_stem', 'mushroom_cap')]))
    yield from paint_values('pebble_b', GRAY_LIGHT)
    yield from paint_values('mushroom_stem', CREAM)
    yield from paint_values('mushroom_cap', RED)
    d.shot('l34_painted')
    if STOP == 'gn':
        return

    # Object > Convert > Mesh applies the Paint Part modifiers, and the colors become part of the meshes.
    parts = ('pebble_a', 'pebble_b', 'mushroom_cap', 'mushroom_stem')
    activate(*parts)
    yield 0.4
    yield from object_menu(d)
    yield from slow_click(d, 342, top(637))
    yield 0.8
    d.shot('l34_convert_menu')
    yield from d.press(520, top(637))
    yield 0.8
    d.log('CONVERTED {}'.format([(n, len(bpy.data.objects[n].modifiers), [a.name for a in bpy.data.objects[n].data.attributes if not a.name.startswith('.')]) for n in parts]))
    # The mushroom is one mesh: the cap joined into the stem.
    activate('mushroom_cap', 'mushroom_stem')
    yield 0.4
    over_view()
    d.key('J', ctrl=True)
    yield 0.8
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('mushroom_a')
    d.key('RET')
    yield 0.5
    # They stood apart while they were built; Alt+G clears each object's location, and the meshes stay as they are.
    activate('pebble_a', 'pebble_b', 'mushroom_a')
    yield 0.4
    over_view()
    d.key('G', alt=True)
    yield 0.6
    # Local view (Numpad /) shows only the three, away from the clumps.
    d.key('NUMPAD_SLASH')
    yield 1.0
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l34_cleared')
    d.key('NUMPAD_SLASH')
    yield 1.0
    for name in ('pebble_a', 'pebble_b', 'mushroom_a'):
        obj = bpy.data.objects[name]
        d.log('FINAL {} location {} lowest {} highest {} tris {} attributes {}'.format(name, tuple(round(v, 3) for v in obj.location), round(min(v.co.z for v in obj.data.vertices), 4), round(max(v.co.z for v in obj.data.vertices), 4), sum(len(p.vertices) - 2 for p in obj.data.polygons), [a.name for a in obj.data.attributes if not a.name.startswith('.')]))
    # The meshes are named after their objects, since Godot shows the mesh's name.
    for name in ('pebble_a', 'pebble_b', 'mushroom_a'):
        activate(name)
        yield 0.3
        yield from d.press(1595, top(626))
        yield 0.5
        yield from d.press(1760, top(297))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.4
        d.move(1760, top(1000))
        yield 0.3
    d.log('MESH NAMES {}'.format([(n, bpy.data.objects[n].data.name) for n in ('pebble_a', 'pebble_b', 'mushroom_a')]))
    if STOP == 'join':
        return

    # Export again: the `grass` collection already has its exporter.
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['grass']
    yield from d.press(1595, top(449))
    yield 0.6
    d.shot('l34_collection_tab')
    glb = os.path.join(EXPORT, 'grass.glb')
    before = os.path.getmtime(glb)
    yield from slow_click(d, 1772, top(708))
    yield 3.0
    d.log('GLB exported {} size {}'.format(os.path.getmtime(glb) != before, os.path.getsize(glb)))
    if os.path.getmtime(glb) == before:
        raise RuntimeError('the export did not run')
    import json
    import struct
    data = open(glb, 'rb').read()
    header = json.loads(data[20:20 + struct.unpack('<I', data[12:16])[0]])
    d.log('GLB meshes {}'.format([(m['name'], list(m['primitives'][0]['attributes'])) for m in header['meshes']]))
    saved_before = os.path.getmtime(bpy.data.filepath)
    for attempt in range(4):
        over_view()
        d.key('S', ctrl=True)
        yield 2.0
        if os.path.getmtime(bpy.data.filepath) != saved_before:
            break
    d.log('SAVED {} size {}'.format(bpy.data.filepath, os.path.getsize(bpy.data.filepath)))
    if os.path.getmtime(bpy.data.filepath) == saved_before:
        raise RuntimeError('the file did not save')
