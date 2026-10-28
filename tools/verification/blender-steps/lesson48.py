# Lesson 48, in Blender: the bank kit's collision. From bank.blend (lesson 44): a box over each piece's water side, named
# -convcolonly and parented to the piece, 10 boxes for the 7 pieces, shown as wire, and the kit exported again.
import json
import os
import struct
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import top

WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
GLB = os.path.join(WORKBENCH, 'art', 'water', 'bank_kit.glb')
HEIGHT = 1.75
CENTER_Z = 0.125

# For each piece: its boxes as the center (X, Y, Z) on the piece and the size, in Blender's axes, the water at -Y. The wall is
# 0.2 meters from the middle and the cell reaches 0.25, so a box beside the wall is 5 centimeters thick.
BOXES = {
    'bank_straight': [((0, -0.225, CENTER_Z), (0.5, 0.05, HEIGHT))],
    'bank_land_corner': [((0, -0.225, CENTER_Z), (0.5, 0.05, HEIGHT)), ((0.225, 0.025, CENTER_Z), (0.05, 0.45, HEIGHT))],
    'bank_water_corner': [((0.225, -0.225, CENTER_Z), (0.05, 0.05, HEIGHT))],
    'bank_diagonal': [((-0.225, -0.225, CENTER_Z), (0.05, 0.05, HEIGHT)), ((0.225, 0.225, CENTER_Z), (0.05, 0.05, HEIGHT))],
}


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    viewport = d.area('VIEW_3D')

    def over_view():
        d.move(*d.center(viewport))

    def run(operator, **options):
        with d.override():
            return operator(**options)

    def typed(*values):
        for number, value in enumerate(values):
            if number:
                d.key('TAB')
            d.type_text(str(value))

    d.shot('l48_start')
    # The bank collection takes what is added: a click on its row.
    d.click(1657, top(84))
    yield 0.5
    d.log('ACTIVE {}'.format(bpy.context.view_layer.active_layer_collection.name))

    def box(piece, name, center, size, shot=None):
        # The importer keeps a collision box's shape and drops its place, so the box is made at the piece's origin: the 3D cursor
        # goes to the piece, the cube is added there, and in Edit Mode its points are scaled to the size and moved to the place.
        run(bpy.ops.object.select_all, action='DESELECT')
        piece.select_set(True)
        bpy.context.view_layer.objects.active = piece
        run(bpy.ops.view3d.snap_cursor_to_selected)
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text('cube')
        yield 0.9
        d.key('RET')
        yield 0.8
        over_view()
        d.key('TAB')
        yield 0.5
        d.key('A')
        d.key('S')
        typed(*[value / 2 for value in size])
        d.key('RET')
        yield 0.4
        d.key('G')
        typed(*center)
        d.key('RET')
        yield 0.4
        d.key('TAB')
        yield 0.5
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
        # Ctrl+P > Object (Keep Transform): the header menus do not open under simulated input, so it runs as an operator.
        obj = bpy.context.active_object
        run(bpy.ops.object.select_all, action='DESELECT')
        obj.select_set(True)
        piece.select_set(True)
        bpy.context.view_layer.objects.active = piece
        run(bpy.ops.object.parent_set, type='OBJECT', keep_transform=True)
        yield 0.4
        bounds = [tuple(round(v, 4) for v in corner) for corner in (obj.bound_box[0], obj.bound_box[6])]
        d.log('BOX {} parent {} object at {} points from {} to {}'.format(obj.name, obj.parent.name, tuple(round(v, 4) for v in obj.location), bounds[0], bounds[1]))
        if shot:
            d.shot(shot)

    pieces = sorted((o for o in bpy.data.objects if o.type == 'MESH' and '-' not in o.name), key=lambda o: o.name)
    d.log('PIECES {}'.format([(o.name, round(o.location.x, 3)) for o in pieces]))
    first = True
    for piece in pieces:
        kind = next(prefix for prefix in BOXES if piece.name.startswith(prefix))
        for center, size in BOXES[kind]:
            yield from box(piece, piece.name + '-convcolonly', center, size, 'l48_first_box' if first else None)
            first = False
    for obj in bpy.data.objects:
        if 'colonly' in obj.name:
            obj.display_type = 'WIRE'
    run(bpy.ops.object.select_all, action='DESELECT')
    over_view()
    d.key('NUMPAD_7')
    d.key('HOME')
    yield 0.8
    d.shot('l48_top')
    # A three-quarter view of everything, for the figures.
    import math
    from mathutils import Euler
    r3d = viewport.spaces.active.region_3d
    r3d.view_rotation = Euler((math.radians(55), 0, math.radians(25))).to_quaternion()
    r3d.view_perspective = 'ORTHO'
    over_view()
    d.key('HOME')
    yield 0.8
    d.shot('l48_boxes')

    # Export again from the collection's exporter, as in lesson 44: the Collection tab and Export All.
    before = os.path.getmtime(GLB) if os.path.exists(GLB) else 0
    yield from d.press(1595, top(449))
    yield 0.8
    d.shot('l48_exporter')
    yield from d.press(1771, top(708))
    yield 2.5
    d.log('EXPORTED changed {} size {}'.format(os.path.getmtime(GLB) > before, os.path.getsize(GLB)))
    data = open(GLB, 'rb').read()
    length = struct.unpack('<I', data[12:16])[0]
    gltf = json.loads(data[20:20 + length])
    names = [node['name'] for node in gltf['nodes']]
    d.log('GLB nodes {} with collision {}'.format(len(names), sorted(name for name in names if 'colonly' in name)))
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
