# Lesson 30: a grass clump and two flowers. A blade by hand (a quad and a tip triangle), three bends of it, a Geometry
# Nodes group that scatters a patch of blades with data for the shader in vertex colors, then a daisy and a cup flower by
# hand, all exported in one .glb, from the startup file lesson 8 saved.
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

sys.path.insert(0, os.path.dirname(__file__))
import grass_clump_spec as spec
import lesson26
from node_ui import NodeUI

WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
FOLDER = os.path.join(WORKBENCH, 'art_source', 'nature', 'grass')
EXPORT = os.path.join(WORKBENCH, 'art', 'nature', 'grass')
STOP = os.environ.get('LESSON30_STOP', '')
FAST = bool(os.environ.get('LESSON30_FAST'))
CONVERT_MESH_X, CONVERT_MESH_Y = int(os.environ.get('CONVERT_MESH_X', 520)), int(os.environ.get('CONVERT_MESH_Y', 637))
# The flower colors as red, green, blue, and petal mask: a dark green, a yellow, and white petals.
STEM, CENTER, PETAL = (0.05, 0.14, 0.02, 0.0), (1.0, 0.58, 0.04, 0.0), (1.0, 1.0, 1.0, 1.0)
# Where each chapter's nodes go, in node space: origin and the number of columns.
LAYOUT = {'feet': ((0, 300), 3), 'blades': ((1100, 450), 4), 'colors': ((2500, 450), 4)}



def top(y, height=1080):
    return height - y


def steps(d):
    yield 2
    d.key('ESC')
    yield 0.5
    d.shot('l30_start')
    viewport = d.area('VIEW_3D')

    def screen_point(point):
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, bpy.context.active_object.matrix_world @ Vector(point))
        return int(region.x + local.x), int(region.y + local.y)

    def over_view():
        d.move(*d.center(viewport))

    def typed(*values):
        # Numbers for a transform, X then Y then Z, with Tab between.
        for number, value in enumerate(values):
            if number:
                d.key('TAB')
            d.type_text(str(value))

    def select_box(first, second):
        # B and a drag over two corners, in window coordinates; the selection starts empty.
        over_view()
        d.key('A', alt=True)
        yield 0.2
        d.key('B')
        yield 0.2
        yield from d.drag(first, second, steps=6)
        yield 0.4

    def selected():
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        return [tuple(round(c, 4) for c in v.co) for v in mesh.verts if v.select]

    # The startup file's cube goes, and a plane stands up to become the blade.
    over_view()
    d.key('A')
    d.key('X')
    yield 0.5
    d.shot('l30_delete_menu')
    d.key('RET')
    yield 0.4
    d.log('OBJECTS {}'.format([o.name for o in bpy.data.objects]))

    # File > Save As into the project's art_source/nature/grass folder.
    d.move(*d.center(viewport))
    d.key('S', ctrl=True, shift=True)
    yield 2
    browser = d.browser()
    d.shot('l30_save_as', browser)
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.key('A', ctrl=True, target=browser)
    d.type_text(FOLDER + os.sep, target=browser)
    yield 0.3
    d.shot('l30_path_typed', browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l30_create_folder', browser)
    d.click(516, top(54, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('FOLDER exists {}'.format(os.path.isdir(FOLDER)))
    d.click(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.key('A', ctrl=True, target=browser)
    d.type_text('grass.blend', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l30_file_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 2.5
    d.log('SAVED AS {}'.format(bpy.data.filepath))
    d.wake()
    yield 0.3
    over_view()
    d.key('A', shift=True)
    yield 0.8
    d.shot('l30_add_menu')
    d.type_text('plane')
    yield 0.8
    d.key('RET')
    yield 0.8
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('blade_low')
    d.key('RET')
    yield 0.5
    d.log('NAME {}'.format(bpy.context.active_object.name))
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('TAB')
    yield 0.6
    d.key('A')
    # Stand the plane up: turn it 90 degrees about X, narrow it to 1 m, and make it 0.55 m tall with its foot on the ground.
    d.key('R')
    d.key('X')
    d.type_text('90')
    d.key('RET')
    yield 0.4
    d.key('S')
    d.key('X')
    d.type_text('0.5')
    d.key('RET')
    yield 0.4
    d.key('S')
    d.key('Z')
    d.type_text('0.275')
    d.key('RET')
    yield 0.4
    d.key('G')
    d.key('Z')
    d.type_text('0.275')
    d.key('RET')
    yield 0.4
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l30_quad')
    d.log('QUAD {}'.format(selected()))
    if STOP == 'quad':
        return

    # The joint: the top edge narrows to 0.6 and a copy of it goes up to the tip, where its two vertices merge.
    def row_box(height, half_width):
        left = screen_point((-half_width, 0, height))
        right = screen_point((half_width, 0, height))
        return (left[0] - 45, left[1] - 35), (right[0] + 45, right[1] + 35)

    yield from select_box(*row_box(spec.JOINT_HEIGHT, 0.5))
    d.log('JOINT ROW {}'.format(selected()))
    d.shot('l30_joint_selected')
    over_view()
    d.key('S')
    d.key('X')
    d.type_text(str(spec.JOINT_WIDTH))
    d.key('RET')
    yield 0.4
    d.key('E')
    yield 0.2
    typed(0, 0, round(1 - spec.JOINT_HEIGHT, 2))
    d.key('RET')
    yield 0.5
    d.shot('l30_tip_row')
    d.log('TIP ROW {}'.format(selected()))
    yield from d.press(356, top(38))
    yield 0.5
    yield from slow_click(d, 390, top(175))
    yield 0.8
    d.shot('l30_merge_menu')
    yield from d.press(600, top(175))
    yield 0.6
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    d.log('BLADE verts {} faces {} sizes {}'.format(len(mesh.verts), len(mesh.faces), [len(f.verts) for f in mesh.faces]))
    d.log('BLADE coordinates {}'.format(sorted(tuple(round(c, 4) for c in v.co) for v in mesh.verts)))
    d.key('A', alt=True)
    yield 0.4
    d.shot('l30_blade')
    d.key('TAB')
    yield 0.5
    over_view()
    d.key('HOME')
    yield 0.8
    d.shot('l30_blade_object')
    if STOP == 'blade':
        return

    # Two copies, in place: Shift+D starts a move, and Escape drops it where it was.
    for name in ('blade_mid', 'blade_high'):
        over_view()
        d.key('D', shift=True)
        yield 0.3
        d.key('ESC')
        yield 0.3
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
    d.log('BLADES {}'.format(sorted(o.name for o in bpy.data.objects)))
    d.shot('l30_three_blades')

    # Each blade is bent in edit mode: the joint row moves forward (Y) and up, the tip forward. The outliner lists them
    # alphabetically.
    rows = {'blade_high': 104, 'blade_low': 124, 'blade_mid': 144}
    for name, joint, tip in spec.BLADES:
        yield from d.press(1690, top(rows[name]))
        yield 0.5
        over_view()
        d.key('TAB')
        yield 0.5
        d.key('NUMPAD_1')
        yield 0.5
        d.key('HOME')
        yield 0.6
        yield from select_box(*row_box(spec.JOINT_HEIGHT, 0.3))
        d.log('BEND {} joint row {}'.format(name, selected()))
        over_view()
        d.key('G')
        typed(0, joint[0], round(joint[1] - spec.JOINT_HEIGHT, 4))
        d.key('RET')
        yield 0.4
        tip_point = screen_point((0, 0, 1.0))
        yield from select_box((tip_point[0] - 45, tip_point[1] - 35), (tip_point[0] + 45, tip_point[1] + 35))
        d.log('BEND {} tip {}'.format(name, selected()))
        over_view()
        d.key('G')
        typed(0, tip[0], 0)
        d.key('RET')
        yield 0.4
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        d.log('BENT {} {}'.format(name, sorted(tuple(round(c, 4) for c in v.co) for v in mesh.verts)))
        d.key('A', alt=True)
        d.key('NUMPAD_3')
        yield 0.6
        d.key('HOME')
        yield 0.6
        d.shot('l30_bent_' + name)
        d.key('TAB')
        yield 0.5
    # All three together, from the side.
    over_view()
    d.key('A')
    d.key('NUMPAD_3')
    yield 0.4
    for key in ('NUMPAD_4', 'NUMPAD_4', 'NUMPAD_8'):
        d.key(key)
        yield 0.2
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l30_bends_together')
    if STOP == 'bent':
        return

    # The three blades go into a collection of their own, which Collection Info will read.
    over_view()
    d.key('NUMPAD_PERIOD')
    d.key('A')
    yield 0.4
    # The outliner's New Collection button adds one under Scene Collection; F2 over the outliner names it.
    yield from d.press(1900, top(38))
    yield 0.6
    d.log('COLLECTIONS now {}'.format([c.name for c in bpy.data.collections]))
    d.shot('l30_new_collection')
    # Click the new collection, F2 to name it, and drag the three selected blades onto it.
    yield from d.press(1690, top(164))
    yield 0.4
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('grass_blades')
    d.key('RET')
    yield 0.5
    d.shot('l30_collection_named')
    # M over the 3D view moves the selected objects: type the collection's name in the menu's search.
    over_view()
    d.key('A')
    yield 0.4
    d.key('M')
    yield 0.8
    d.type_text('grass_blades')
    yield 0.6
    d.shot('l30_move_search')
    d.key('RET')
    yield 0.8
    d.log('COLLECTIONS {}'.format([(c.name, [o.name for o in c.objects]) for c in bpy.data.collections]))
    d.shot('l30_collection_made')
    # The blades are only the source: hide their collection, and name the other one `grass`, where the clump goes.
    yield from d.press(1878, top(104))
    yield 0.4
    yield from d.press(1670, top(84))
    yield 0.4
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('grass')
    d.key('RET')
    yield 0.5
    d.log('COLLECTIONS {}'.format([(c.name, [o.name for o in c.objects]) for c in bpy.data.collections]))
    d.shot('l30_collections_ready')

    # The clump's footprint: a circle filled with a face, 0.45 m in radius.
    over_view()
    d.key('A', shift=True)
    yield 0.8
    d.type_text('circle')
    yield 0.8
    d.shot('l30_add_circle')
    d.key('RET')
    yield 0.8
    d.log('CIRCLE {} {} verts {}'.format(bpy.context.active_object.name, bpy.context.active_object.type, len(bpy.context.active_object.data.vertices)))
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('grass_clump_a')
    d.key('RET')
    yield 0.5
    d.key('TAB')
    yield 0.5
    d.key('A')
    d.key('F')
    yield 0.4
    d.key('S')
    d.type_text('0.45')
    d.key('RET')
    yield 0.4
    d.key('NUMPAD_7')
    yield 0.4
    d.key('HOME')
    yield 0.6
    d.shot('l30_footprint')
    d.key('TAB')
    yield 0.5
    mesh = bpy.context.active_object.data
    d.log('FOOTPRINT faces {} radius {}'.format(len(mesh.polygons), round(max(v.co.length for v in mesh.vertices), 3)))
    if STOP == 'footprint':
        return

    # The Geometry Nodes workspace, a new group on the clump, and the node editor over the whole window.
    clump = bpy.context.active_object
    yield from d.press(980, top(13))
    yield 1.5
    yield from d.press(790, top(516))
    yield 1.0
    tree = clump.modifiers[0].node_group
    tree.name = 'Grass Clump'
    d.log('GROUP {} {}'.format(tree.name, [n.name for n in tree.nodes]))
    d.shot('l30_new_group')
    if FAST:
        # For testing the steps after the group: build it with the API instead, and go back to the Layout workspace.
        tree.interface.new_socket('Seed', in_out='INPUT', socket_type='NodeSocketInt')
        spec.build(tree, bpy.data.collections['grass_blades'])
        yield from d.press(288, top(13))
        yield 1.5
    editor = d.area('NODE_EDITOR') if not FAST else None
    if not FAST:
        d.move(*d.center(editor))
        d.key('SPACE', ctrl=True)
        yield 1.0
    ui = NodeUI(d, tree) if not FAST else None
    bpy.context.preferences.view.smooth_view = 0
    nodes = {'in': tree.nodes['Group Input'], 'out': tree.nodes['Group Output']}
    nodes['in'].location = (-330, 300)
    nodes['out'].location = (-330, 60)
    d.shot('l30_group_ready')
    only = [name for name in os.environ.get('LESSON30_ONLY', '').split(',') if name]
    for chapter in ([] if FAST else spec.CHAPTERS):
        if only and chapter['key'] not in only:
            continue
        yield from lesson26.build_chapter(d, ui, tree, nodes, chapter, spec=spec, layout=LAYOUT, prefix='l30')
    if not FAST:
        d.move(*d.center(d.area('NODE_EDITOR')))
        d.key('HOME')
        yield 1.0
        d.shot('l30_all_nodes')
    d.log('LINKS {} NODES {}'.format(len(tree.links), len(tree.nodes)))
    mesh = clump.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    d.log('RESULT faces {} verts {} attributes {}'.format(len(mesh.polygons), len(mesh.vertices), [a.name for a in mesh.attributes if not a.name.startswith('.')]))
    if STOP == 'nodes':
        return
    # Back to the whole window, then the Layout workspace and the modifier tab.
    if not FAST:
        d.move(*d.center(d.area('NODE_EDITOR')))
        d.key('SPACE', ctrl=True)
        yield 1.0
        yield from d.press(288, top(13))
        yield 1.5
    over_view()
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l30_clump')
    yield from d.press(1595, top(514))
    yield 0.8
    d.shot('l30_modifier_tab')
    # The group's one input is the clump's seed. Three clumps: seed, size, and place differ.
    SEED_FIELD = (1797, top(391))
    yield from d.press(*SEED_FIELD)
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text('1')
    d.key('RET')
    yield 0.6
    d.shot('l30_seed')
    variants = (('grass_clump_b', 2, 1.125, -1.0), ('grass_clump_c', 3, 0.875, 1.0))
    for name, seed, size, offset in variants:
        # Each copy starts from the first clump, picked in the outliner.
        yield from d.press(1690, top(104))
        yield 0.4
        over_view()
        d.key('D', shift=True)
        yield 0.3
        d.key('ESC')
        yield 0.3
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
        yield from d.press(*SEED_FIELD)
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(str(seed))
        d.key('RET')
        yield 0.6
        over_view()
        d.key('S')
        d.type_text(str(size))
        d.key('RET')
        yield 0.4
        d.key('G')
        d.key('X')
        d.type_text(str(offset))
        d.key('RET')
        yield 0.6
    over_view()
    d.key('A')
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l30_three_clumps')
    d.log('CLUMPS {}'.format([(o.name, tuple(round(v, 3) for v in o.scale), tuple(round(v, 3) for v in o.location), o.modifiers[0].properties.inputs.Socket_2.value) for o in bpy.data.objects if o.name.startswith('grass_clump')]))
    if STOP == 'modifier':
        return

    # Apply each clump's modifier (Ctrl+A over its panel), so the clumps are plain meshes.
    for number, name in enumerate(('grass_clump_a', 'grass_clump_b', 'grass_clump_c')):
        yield from d.press(1690, top(104 + 20 * number))
        yield 0.5
        d.move(1700, top(331))
        yield 0.5
        d.key('A', ctrl=True)
        yield 0.8
        obj = bpy.data.objects[name]
        d.log('APPLIED {} modifiers {} faces {} attributes {}'.format(name, len(obj.modifiers), len(obj.data.polygons), [a.name for a in obj.data.attributes if not a.name.startswith('.')]))
    d.shot('l30_applied')
    over_view()
    d.key('A')
    yield 0.3
    d.key('A', ctrl=True)
    yield 0.8
    d.shot('l30_apply_menu')
    d.key('S')
    yield 0.6
    d.log('SCALES {}'.format([(o.name, tuple(round(v, 3) for v in o.scale), len(o.data.vertices), round(max(v.co.z for v in o.data.vertices), 3)) for o in bpy.data.objects if o.name.startswith('grass_clump')]))
    d.shot('l30_scale_applied')
    if STOP == 'apply':
        return

    # The flowers. The clumps hide (H) so the origin is free, and each flower is built from separate parts.
    over_view()
    d.key('A')
    d.key('H')
    yield 0.5
    d.key('A', alt=True)

    def add_plane(name):
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text('plane')
        yield 0.8
        d.key('RET')
        yield 0.8
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5

    def merge_at_center():
        # Mesh > Merge > At Center, from the 3D view's header.
        yield from d.press(356, top(38))
        yield 0.5
        yield from slow_click(d, 390, top(175))
        yield 0.8
        yield from d.press(600, top(175))
        yield 0.6

    def tip_up(name, size, height):
        # A square of the given half-width extruded up and pulled to a point: a four-sided spike.
        yield from add_plane(name)
        d.key('TAB')
        yield 0.5
        d.key('A')
        d.key('S')
        d.type_text(str(size))
        d.key('RET')
        yield 0.3
        d.key('E')
        yield 0.2
        typed(0, 0, height)
        d.key('RET')
        yield 0.4
        yield from merge_at_center()
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        d.log('SPIKE {} verts {} faces {} top {}'.format(name, len(mesh.verts), len(mesh.faces), round(max(v.co.z for v in mesh.verts), 4)))
        d.key('TAB')
        yield 0.5

    yield from tip_up('stem', 0.012, 0.3)
    d.shot('l30_stem')
    yield from tip_up('center', 0.03, 0.012)
    over_view()
    d.key('G')
    d.key('Z')
    d.type_text('0.295')
    d.key('RET')
    yield 0.4
    d.shot('l30_center')
    # A petal: a diamond 9 cm long and 5 cm wide with its inner tip at the object's origin, which goes to the top of
    # the stem, and tilted 15 degrees below level.
    yield from add_plane('petal')
    d.key('TAB')
    yield 0.5
    d.key('A')
    d.key('R')
    d.key('Z')
    d.type_text('45')
    d.key('RET')
    yield 0.3
    d.key('S')
    d.key('X')
    d.type_text('0.032')
    d.key('RET')
    yield 0.3
    d.key('S')
    d.key('Y')
    d.type_text('0.018')
    d.key('RET')
    yield 0.3
    d.key('G')
    d.key('X')
    d.type_text('0.045')
    d.key('RET')
    yield 0.3
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    d.log('PETAL {}'.format(sorted(tuple(round(c, 4) for c in v.co) for v in mesh.verts)))
    d.key('TAB')
    yield 0.4
    d.key('G')
    d.key('Z')
    d.type_text('0.3')
    d.key('RET')
    yield 0.3
    d.key('R')
    d.key('Y')
    d.type_text('15')
    d.key('RET')
    yield 0.4
    d.key('NUMPAD_1')
    yield 0.4
    d.key('A')
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l30_daisy_parts')
    d.log('PARTS {}'.format([(o.name, tuple(round(v, 3) for v in o.location), tuple(round(math.degrees(v)) for v in o.rotation_euler)) for o in bpy.data.objects if o.name in ('stem', 'center', 'petal')]))
    if STOP == 'parts':
        return

    def activate(*names):
        # Clicking in the outliner: the last name is the active object.
        for obj in bpy.context.view_layer.objects:
            obj.select_set(False)
        for name in names:
            bpy.data.objects[name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[names[-1]]

    # The Paint Part group: four numbers in, one vertex color out, made on the stem in the Geometry Nodes workspace.
    activate('stem')
    yield 0.4
    yield from d.press(980, top(13))
    yield 1.5
    yield from d.press(790, top(516))
    yield 1.0
    paint = bpy.data.objects['stem'].modifiers[0].node_group
    paint.name = 'Paint Part'
    d.shot('l30_paint_group')
    if FAST and not os.environ.get('LESSON30_PAINT_UI'):
        for name in spec.PAINT_INPUTS:
            paint.interface.new_socket(name, in_out='INPUT', socket_type='NodeSocketFloat')
        paint_nodes = {'in': paint.nodes['Group Input'], 'out': paint.nodes['Group Output']}
        for key, search, settings, inputs in spec.PAINT_CHAPTER['nodes']:
            node = paint.nodes.new(spec.IDNAMES[search])
            paint_nodes[key] = node
            spec.base.apply(node, settings, inputs)
        for a, output, b, name in spec.PAINT_CHAPTER['links']:
            paint.links.new(spec.socket(paint_nodes[a], output, True), spec.socket(paint_nodes[b], name, False))
        yield from d.press(288, top(13))
        yield 1.5
    else:
        d.move(*d.center(d.area('NODE_EDITOR')))
        d.key('SPACE', ctrl=True)
        yield 1.0
        ui = NodeUI(d, paint)
        paint_nodes = {'in': paint.nodes['Group Input'], 'out': paint.nodes['Group Output']}
        paint_nodes['in'].location = (-330, 300)
        paint_nodes['out'].location = (-330, 60)
        yield from lesson26.build_chapter(d, ui, paint, paint_nodes, spec.PAINT_CHAPTER, spec=spec, layout={'paint': ((0, 300), 2)}, prefix='l30')
        # The shield beside the group's name is Fake User: it keeps the group in the file after the parts that use it are joined.
        yield from d.press(973, top(38))
        yield 0.4
        d.shot('l30_fake_user')
        d.move(*d.center(d.area('NODE_EDITOR')))
        d.key('SPACE', ctrl=True)
        yield 1.0
        yield from d.press(288, top(13))
        yield 1.5
    if FAST and not os.environ.get('LESSON30_PAINT_UI'):
        paint.use_fake_user = True
    d.log('PAINT FAKE USER {}'.format(paint.use_fake_user))
    if not paint.use_fake_user:
        raise RuntimeError('the Paint Part group is not kept')
    d.log('PAINT GROUP nodes {} links {} inputs {}'.format(len(paint.nodes), len(paint.links), [(item.name, item.in_out, item.socket_type) for item in paint.interface.items_tree]))
    over_view()
    yield from d.press(1595, top(514))
    yield 0.6
    d.shot('l30_paint_modifier')
    if STOP == 'paint':
        return

    def paint_values(name, red, green, blue, mask):
        # The modifier's four fields: click, select all, type, Enter.
        activate(name)
        yield 0.3
        for y, value in zip((391, 416, 441, 466), (red, green, blue, mask)):
            yield from d.press(1797, top(y))
            yield 0.2
            d.key('A', ctrl=True)
            d.type_text(str(value))
            d.key('RET')
            yield 0.3
        inputs = bpy.data.objects[name].modifiers[0].properties.inputs
        got = [round(getattr(inputs, item.identifier).value, 3) for item in paint.interface.items_tree if item.in_out == 'INPUT' and item.name in spec.PAINT_INPUTS]
        d.log('PAINT {} {}'.format(name, got))
        if got != [red, green, blue, mask]:
            raise RuntimeError('paint values of {} are {}'.format(name, got))

    yield from paint_values('stem', *STEM)
    d.shot('l30_paint_stem')
    # Copy the stem's modifier to the center and the petal: Object > Link/Transfer Data > Copy Modifiers.
    activate('center', 'petal', 'stem')
    yield 0.4
    yield from object_menu(d)
    yield from slow_click(d, 369, top(469))
    yield 0.8
    d.shot('l30_link_menu')
    yield from d.press(548, top(636))
    yield 0.8
    d.log('MODIFIERS {}'.format([(name, [m.name for m in bpy.data.objects[name].modifiers]) for name in ('stem', 'center', 'petal')]))
    yield from paint_values('center', *CENTER)
    yield from paint_values('petal', *PETAL)
    d.shot('l30_painted')

    def duplicate(name, new_name):
        # Shift+D copies the object with its modifier, and Escape drops the copy where it was.
        activate(name)
        yield 0.3
        over_view()
        d.key('D', shift=True)
        yield 0.3
        d.key('ESC')
        yield 0.4
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(new_name)
        d.key('RET')
        yield 0.5

    def ring(names_from, count, step, prefix):
        # Copies of one part, each turned `step` degrees more about the part's own origin (the top of the stem).
        parent = names_from
        made = []
        for number in range(count):
            new_name = '{}_{}'.format(prefix, number + 1)
            yield from duplicate(parent, new_name)
            over_view()
            d.key('R')
            d.key('Z')
            d.type_text(str(step))
            d.key('RET')
            yield 0.4
            made.append(new_name)
            parent = new_name
        return made

    # The daisy has eight petals, 45 degrees apart; the cup's five are 72 apart and rise 55 degrees. The cup's parts
    # stand half a meter to the side, under the cup's own top at 0.26.
    cup_petal_first = 'cup_petal_0'
    yield from duplicate('petal', cup_petal_first)
    over_view()
    d.key('G')
    typed(0.5, 0, -0.04)
    d.key('RET')
    yield 0.3
    d.key('R')
    d.key('Y')
    d.type_text('-70')
    d.key('RET')
    yield 0.4
    yield from duplicate('stem', 'cup_stem')
    over_view()
    d.key('S')
    d.key('Z')
    d.type_text('0.8667')
    d.key('RET')
    yield 0.3
    d.key('G')
    d.key('X')
    d.type_text('0.5')
    d.key('RET')
    yield 0.4
    cup_petals = yield from ring(cup_petal_first, 4, 72, 'cup_petal')
    daisy_petals = yield from ring('petal', 7, 45, 'petal_copy')
    d.shot('l30_flowers_built')
    d.log('FLOWERS petals {} cup petals {}'.format(len(daisy_petals) + 1, len(cup_petals) + 1))
    if STOP == 'flowers':
        return

    def join(parts, final):
        # Convert the parts to plain meshes (which applies their Paint Part modifiers), then join them into the last one.
        activate(*parts)
        yield 0.4
        yield from object_menu(d)
        yield from slow_click(d, 342, top(637))
        yield 0.8
        d.shot('l30_convert_menu')
        yield from d.press(CONVERT_MESH_X, top(CONVERT_MESH_Y))
        yield 0.8
        d.log('CONVERTED {}'.format([(name, len(bpy.data.objects[name].modifiers)) for name in parts]))
        over_view()
        d.key('J', ctrl=True)
        yield 0.8
        joined = bpy.context.active_object
        joined.name = final
        mesh = joined.data
        d.log('JOINED {} verts {} faces {} attributes {} origin {}'.format(final, len(mesh.vertices), len(mesh.polygons), [a.name for a in mesh.attributes if not a.name.startswith('.')], tuple(round(v, 3) for v in joined.location)))

    daisy_parts = ['center', 'petal'] + daisy_petals + ['stem']
    yield from join(daisy_parts, 'flower_daisy')
    cup_parts = [cup_petal_first] + cup_petals + ['cup_stem']
    yield from join(cup_parts, 'flower_cup')
    # The cup's stem was squashed to 0.867 tall, and the joined object keeps that scale: apply it (Ctrl+A, Scale).
    activate('flower_cup')
    yield 0.3
    over_view()
    d.key('A', ctrl=True)
    yield 0.8
    d.key('S')
    yield 0.6
    d.log('CUP SCALE {}'.format(tuple(round(v, 3) for v in bpy.data.objects['flower_cup'].scale)))
    # The two flowers stand side by side beyond the clumps, and the clumps come back (Alt+H).
    for name, place in (('flower_daisy', 2.0), ('flower_cup', 3.0)):
        activate(name)
        yield 0.3
        over_view()
        d.key('G')
        d.key('X')
        d.type_text(str(place - bpy.data.objects[name].location.x))
        d.key('RET')
        yield 0.4
    over_view()
    d.key('H', alt=True)
    yield 0.6
    d.key('NUMPAD_1')
    yield 0.4
    d.key('A')
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l30_all_models')
    # Viewport Shading > Color > Attribute shows the vertex colors: the flowers' own colors, and the clumps' red phases.
    shading = d.area('VIEW_3D').spaces.active.shading
    shading.color_type = 'VERTEX'
    for names, shot in ((('flower_daisy', 'flower_cup'), 'l30_flowers_view'), (('grass_clump_a', 'grass_clump_b', 'grass_clump_c'), 'l30_clumps_view')):
        activate(*names)
        yield 0.3
        over_view()
        d.key('NUMPAD_PERIOD')
        yield 0.6
        for key in ('NUMPAD_4', 'NUMPAD_4', 'NUMPAD_8', 'NUMPAD_8'):
            d.key(key)
            yield 0.2
        yield 0.5
        d.shot(shot)
        d.key('NUMPAD_1')
        yield 0.3
    shading.color_type = 'MATERIAL'
    d.log('MODELS {}'.format([(o.name, o.type, len(o.data.polygons), sum(len(p.vertices) - 2 for p in o.data.polygons), tuple(round(v, 3) for v in o.location), tuple(round(v, 3) for v in o.dimensions)) for o in bpy.data.objects if o.name.startswith(('grass_clump', 'flower'))]))
    if STOP == 'convert':
        return

    # The meshes are named after their objects, since Godot shows them: the Data tab's name field.
    for name in ('grass_clump_a', 'grass_clump_b', 'grass_clump_c', 'flower_daisy', 'flower_cup'):
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
    d.shot('l30_mesh_names')
    d.log('MESH NAMES {}'.format([(o.name, o.data.name) for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('grass_clump', 'flower'))]))

    # Export: the collection `grass` gets a glTF exporter, and the Collection tab shows it.
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['grass']
    yield from d.press(1595, top(449))
    yield 0.6
    d.shot('l30_collection_tab')
    yield from d.press(1892, top(616))
    yield 0.4
    d.shot('l30_add_exporter')
    yield from d.press(1748, top(760))
    yield 0.8
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l30_exporter_panel')
    collection = bpy.data.collections['grass']
    d.log('EXPORTERS {}'.format([exporter.name for exporter in collection.exporters]))

    # File Path: the folder button opens the File Browser; the .glb goes in art/nature/grass.
    yield from d.press(1892, top(763))
    yield 1.5
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(EXPORT + os.sep, target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 1
    d.shot('l30_export_folder', browser)
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('EXPORT folder exists {}'.format(os.path.isdir(EXPORT)))
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('grass.glb', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l30_export_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    exporter = collection.exporters[0]
    d.log('FILEPATH {}'.format(exporter.export_properties.filepath))
    d.shot('l30_exporter_path')
    # Data > Mesh: the vertex colors to write are the active color attribute, and only that one.
    yield from d.press(1665, top(898))
    yield 0.6
    d.move(1760, top(900))
    for _ in range(20):
        d.key('WHEELDOWNMOUSE')
        yield 0.04
    yield 0.6
    d.shot('l30_data_panel')
    yield from d.press(1667, top(672))
    yield 0.6
    d.move(1760, top(950))
    yield 0.4
    d.shot('l30_mesh_panel')
    # The shader never reads UVs, so leave them out of the file.
    yield from d.press(1747, top(727))
    yield 0.4
    yield from d.press(1688, top(899))
    yield 0.6
    d.move(1760, top(950))
    yield 0.4
    d.shot('l30_vertex_colors')
    properties = exporter.export_properties
    # The meshes have no material, so the default (Material, with the active color written when there is none) is right.
    d.log('VERTEX COLOR SETTINGS {} all {} active {}'.format(properties.export_vertex_color, properties.export_all_vertex_colors, properties.export_active_vertex_color_when_no_material))
    glb = os.path.join(EXPORT, 'grass.glb')
    before = os.path.getmtime(glb) if os.path.exists(glb) else 0
    yield from slow_click(d, 1772, top(432))
    yield 3.0
    d.log('UVS {}'.format(properties.export_texcoords))
    d.log('GLB exported {} size {}'.format(os.path.exists(glb) and os.path.getmtime(glb) != before, os.path.getsize(glb) if os.path.exists(glb) else 0))
    if not os.path.exists(glb) or os.path.getmtime(glb) == before:
        raise RuntimeError('the export did not run')
    # Ctrl+S is sometimes lost, so the file's time says whether it saved, and the key is pressed again if not.
    saved_before = os.path.getmtime(bpy.data.filepath)
    for attempt in range(4):
        over_view()
        d.key('S', ctrl=True)
        yield 2.0
        if os.path.getmtime(bpy.data.filepath) != saved_before:
            break
    d.log('SAVED {} dirty {} size {}'.format(bpy.data.filepath, bpy.data.is_dirty, os.path.getsize(bpy.data.filepath)))
    if os.path.getmtime(bpy.data.filepath) == saved_before:
        raise RuntimeError('the file did not save')
    if STOP == 'exporter':
        return


def object_menu(d):
    # The 3D view header's Object menu: it opens when the pointer has hovered the header first.
    d.move(300, top(38))
    yield 0.5
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=312, y=top(38))
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=312, y=top(38))
    yield 1.5
    d.move(315, top(41))
    yield 0.8


def slow_click(d, x, y):
    # Some buttons only take a press that follows a longer hover.
    d.move(x, y)
    yield 1.0
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=x, y=y)
    yield 0.3
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=x, y=y)
    yield 0.5


def slow_drag(d, start, end, steps=10):
    # A drag that waits at every move and before the release, for the outliner's drop targets.
    d.move(*start)
    yield 0.3
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=start[0], y=start[1])
    yield 0.3
    for index in range(1, steps + 1):
        d.move(start[0] + (end[0] - start[0]) * index // steps, start[1] + (end[1] - start[1]) * index // steps)
        yield 0.1
    yield 0.5
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=end[0], y=end[1])
    yield 0.5
