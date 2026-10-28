# Lesson 44, in Blender: the bank kit. From the startup file lesson 8 saved: save as bank.blend, build the straight bank
# piece by hand (a plane for the top, the waterline edge subdivided and extruded down in rows, a vertex group, a Displace
# modifier for the lumps), then the corner pieces, and export the collection to art/water/bank_kit.glb.
import json
import math
import os
import struct
import sys

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top

STOP = os.environ.get('LESSON44_STOP', '')
WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
FOLDER = os.path.join(WORKBENCH, 'art_source', 'water')
EXPORT = os.path.join(WORKBENCH, 'art', 'water')

TOP = 0.012
ROWS = 12
ROW = 0.0635


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    viewport = d.area('VIEW_3D')

    def over_view():
        d.move(*d.center(viewport))

    def screen_point(point):
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, bpy.context.active_object.matrix_world @ Vector(point))
        return int(region.x + local.x), int(region.y + local.y)

    def typed(*values):
        for number, value in enumerate(values):
            if number:
                d.key('TAB')
            d.type_text(str(value))

    def select_box(first, second, keep=False):
        # B and a drag over two corners, in window coordinates; the selection starts empty unless keep is set.
        over_view()
        if not keep:
            d.key('A', alt=True)
            yield 0.2
        d.key('B')
        yield 0.2
        yield from d.drag(first, second, steps=6)
        yield 0.4

    def box_around(*points, margin=30):
        # The window corners of a box around 3D points, as the selection needs.
        spots = [screen_point(point) for point in points]
        return (min(s[0] for s in spots) - margin, min(s[1] for s in spots) - margin), (max(s[0] for s in spots) + margin, max(s[1] for s in spots) + margin)

    def run(operator, **options):
        # Menu commands run as operators: the header menus do not open under simulated input.
        with d.override():
            return operator(**options)

    def selected():
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        return sorted(tuple(round(c, 4) for c in v.co) for v in mesh.verts if v.select)

    d.shot('l44_start')

    # Save As into art_source/water, which the lesson makes with the File Browser's new-folder button.
    over_view()
    d.key('S', ctrl=True, shift=True)
    yield 2
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(FOLDER + os.sep, target=browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l44_save_folder', browser)
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('FOLDER exists {}'.format(os.path.isdir(FOLDER)))
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('bank.blend', target=browser)
    d.key('RET', target=browser)
    yield 0.4
    d.shot('l44_save_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 2.5
    d.wake()
    yield 0.5
    d.log('SAVED {}'.format(bpy.data.filepath))

    # The starting cube goes.
    over_view()
    d.key('A')
    d.key('X')
    yield 0.8
    d.key('RET')
    yield 0.6
    d.log('OBJECTS after delete {}'.format([o.name for o in bpy.data.objects]))

    # The startup file's collection takes the kit's name: a click on its row, then F2 over the Outliner.
    d.click(1670, top(84))
    yield 0.5
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('bank')
    d.key('RET')
    yield 0.6
    d.log('COLLECTIONS {}'.format([c.name for c in bpy.data.collections]))
    d.shot('l44_collection')

    # The straight piece's top: a plane 0.5 m square, then the waterline edge 0.2 m from the middle, then up to 0.012.
    over_view()
    d.key('A', shift=True)
    yield 0.8
    d.type_text('plane')
    yield 0.9
    d.key('RET')
    yield 0.8
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('bank_straight_a')
    d.key('RET')
    yield 0.5
    over_view()
    d.key('NUMPAD_7')
    yield 0.6
    d.key('TAB')
    yield 0.6
    d.key('A')
    d.key('S')
    d.type_text('0.25')
    d.key('RET')
    yield 0.4
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l44_plane')
    d.log('PLANE {}'.format(selected()))
    if STOP == 'plane':
        return

    # The waterline edge: the two front vertices move 0.05 m back, so the top spans 0.45 m, then everything goes up to 0.012.
    yield from select_box(*box_around((-0.25, -0.25, 0), (0.25, -0.25, 0), margin=25))
    d.log('FRONT {}'.format(selected()))
    d.shot('l44_front_selected')
    over_view()
    d.key('G')
    d.key('Y')
    d.type_text('0.05')
    d.key('RET')
    yield 0.4
    d.key('A')
    d.key('G')
    d.key('Z')
    d.type_text(str(TOP))
    d.key('RET')
    yield 0.4
    d.log('TOP {}'.format(selected()))
    d.shot('l44_top')

    # Edge > Subdivide on the waterline edge: 15 cuts make 16 segments, one every 3.1 cm.
    yield from select_box(*box_around((-0.25, -0.2, TOP), (0.25, -0.2, TOP), margin=25))
    run(bpy.ops.mesh.subdivide, number_cuts=15)
    yield 0.5
    d.shot('l44_subdivided')
    d.log('SUBDIVIDED {} selected {}'.format(len(bpy.context.active_object.data.vertices), len(selected())))

    # The wall: extrude the edge down by one row, 6.35 cm, and repeat that with Shift+R eleven times (12 rows, 0.762 m).
    over_view()
    d.key('E')
    d.key('Z')
    d.type_text(str(-ROW))
    d.key('RET')
    yield 0.5
    for _ in range(ROWS - 1):
        d.key('R', shift=True)
        yield 0.3
    yield 0.5
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    low = min(v.co.z for v in mesh.verts)
    d.log('WALL verts {} faces {} lowest {}'.format(len(mesh.verts), len(mesh.faces), round(low, 4)))
    d.key('NUMPAD_1')
    yield 0.6
    d.key('HOME')
    yield 0.8
    d.shot('l44_wall_front')
    if STOP == 'wall':
        return

    # The lumps' mask: a vertex group whose weights ramp from 0 at the wall's edges, lip, and foot to 1 inside. Select >
    # Select All by Trait > Non Manifold picks the open mesh's border, Select > Invert leaves the lip and the wall's inside,
    # and each Select More/Less > Less strips one more ring.
    def lump_group():
        obj = bpy.context.active_object
        run(bpy.ops.mesh.select_all, action='DESELECT')
        run(bpy.ops.mesh.select_non_manifold, extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        d.log('BORDER {}'.format(len(selected())))
        run(bpy.ops.mesh.select_all, action='INVERT')
        d.log('INSIDE {}'.format(len(selected())))
        run(bpy.ops.object.vertex_group_add)
        obj.vertex_groups.active.name = 'lumps'
        bpy.context.scene.tool_settings.vertex_group_weight = 0.5
        run(bpy.ops.object.vertex_group_assign)
        run(bpy.ops.mesh.select_less)
        d.log('CORE {}'.format(len(selected())))
        bpy.context.scene.tool_settings.vertex_group_weight = 1.0
        run(bpy.ops.object.vertex_group_assign)
        # The lip's own group, for the jag: Alt+click on a lip edge selects its whole loop, Assign at 1, then the border (the wall's
        # ends and foot) at 0, so the jag leaves the ends alone.
        run(bpy.ops.object.vertex_group_add)
        obj.vertex_groups.active.name = 'lip'
        mesh = bmesh.from_edit_mesh(obj.data)
        for vertex in mesh.verts:
            # The lip is the top's vertices that a wall face hangs from.
            vertex.select_set(abs(vertex.co.z - TOP) < 1e-4 and any(abs(face.normal.z) < 0.5 for face in vertex.link_faces))
        mesh.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)
        d.log('LIP loop {}'.format(len(selected())))
        bpy.context.scene.tool_settings.vertex_group_weight = 1.0
        run(bpy.ops.object.vertex_group_assign)
        run(bpy.ops.mesh.select_all, action='DESELECT')
        run(bpy.ops.mesh.select_non_manifold, extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.context.scene.tool_settings.vertex_group_weight = 0.0
        run(bpy.ops.object.vertex_group_assign)
        bpy.context.scene.tool_settings.vertex_group_weight = 1.0

    lump_group()
    yield 0.6
    d.shot('l44_group')
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    layer = mesh.verts.layers.deform.active
    index = bpy.context.active_object.vertex_groups['lumps'].index
    weights = {round(v.co.x, 4): round(v[layer].get(index, 0.0), 2) for v in mesh.verts if abs(v.co.z - (TOP - 5 * ROW)) < 1e-4}
    d.log('WEIGHTS row 5 {}'.format(sorted(weights.items())))
    if STOP == 'group':
        return

    def to_object_mode():
        over_view()
        d.key('TAB')

    def duplicate(name, offset):
        # Shift+D copies the piece, with its vertex group, and G X slides the copy aside; F2 names it.
        over_view()
        d.key('D', shift=True)
        yield 0.5
        d.key('RET')
        yield 0.4
        d.key('G')
        d.key('X')
        d.type_text(str(offset))
        d.key('RET')
        yield 0.4
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5

    def slide(x):
        over_view()
        d.key('G')
        d.key('X')
        d.type_text(str(x))
        d.key('RET')
        yield 0.4

    def new_plane(name):
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text('plane')
        yield 0.9
        d.key('RET')
        yield 0.8
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
        over_view()
        d.key('NUMPAD_7')
        yield 0.5
        d.key('TAB')
        yield 0.5
        d.key('A')
        d.key('S')
        d.type_text('0.25')
        d.key('RET')
        yield 0.4
        d.key('NUMPAD_PERIOD')
        yield 0.6

    def move_vertices(points, axis, amount, keep=False):
        yield from select_box(*box_around(*points, margin=25), keep=keep)
        over_view()
        d.key('G')
        d.key(axis)
        d.type_text(str(amount))
        d.key('RET')
        yield 0.4

    def raise_to_top():
        over_view()
        d.key('A')
        d.key('G')
        d.key('Z')
        d.type_text(str(TOP))
        d.key('RET')
        yield 0.4

    def pick(*points):
        yield from select_box(*box_around(*[(p[0], p[1], TOP) for p in points], margin=25))

    def extrude_wall():
        over_view()
        d.key('E')
        d.key('Z')
        d.type_text(str(-ROW))
        d.key('RET')
        yield 0.5
        for _ in range(ROWS - 1):
            d.key('R', shift=True)
            yield 0.3
        yield 0.4

    def bevel(point, width, segments):
        yield from pick(point)
        run(bpy.ops.mesh.bevel, offset=width, segments=segments, affect='VERTICES')
        yield 0.5

    # The straight piece is done: leave edit mode, make its two variants, and move all three off the origin.
    to_object_mode()
    yield 0.5
    yield from slide(1.0)
    yield from duplicate('bank_straight_b', 0.7)
    yield from duplicate('bank_straight_c', 0.7)
    d.log('OBJECTS {}'.format([(o.name, round(o.location.x, 3)) for o in bpy.data.objects]))
    d.log('GROUPS {}'.format({o.name: [g.name for g in o.vertex_groups] for o in bpy.data.objects}))
    if STOP == 'straights':
        return

    # The land corner: the land lies at the back left, so the water's side is the front right, which becomes a quarter arc
    # of radius 0.2 m (Vertex > Bevel on one vertex).
    yield from new_plane('bank_land_corner_a')
    yield from move_vertices([(0.25, -0.25, 0), (0.25, 0.25, 0)], 'X', -0.05)
    yield from move_vertices([(-0.25, -0.25, 0), (0.2, -0.25, 0)], 'Y', 0.05)
    yield from raise_to_top()
    yield from bevel((0.2, -0.2), 0.2, 6)
    d.shot('l44_land_bevel')
    d.log('LAND outline {}'.format(selected()))
    # Subdivide the two straight edges (0.25 m long) into 8 segments, then extrude the whole waterline.
    yield from pick((-0.25, -0.2), (0.0, -0.2))
    run(bpy.ops.mesh.subdivide, number_cuts=7)
    yield from pick((0.2, 0.0), (0.2, 0.25))
    run(bpy.ops.mesh.subdivide, number_cuts=7)
    yield from pick((-0.25, 0.25))
    over_view()
    d.key('I', ctrl=True)
    yield 0.4
    d.log('WATERLINE {}'.format(len(selected())))
    yield from extrude_wall()
    lump_group()
    yield 0.5
    to_object_mode()
    yield 0.5
    yield from slide(3.1)
    yield from duplicate('bank_land_corner_b', 0.7)
    d.shot('l44_land')
    if STOP == 'land':
        return

    # The water corner: water at the front right, so the square's front right corner is cut by 0.05 m (Vertex > Bevel).
    yield from new_plane('bank_water_corner_a')
    yield from raise_to_top()
    yield from bevel((0.25, -0.25), 0.05, 1)
    yield from pick((0.2, -0.25))
    yield from select_box(*box_around((0.25, -0.2, TOP), margin=25), keep=True)
    d.log('CHAMFER {}'.format(selected()))
    yield from extrude_wall()
    d.shot('l44_water_corner')
    to_object_mode()
    yield 0.5
    yield from slide(4.5)

    # The diagonal: two opposite corners cut the same way.
    yield from new_plane('bank_diagonal_a')
    yield from raise_to_top()
    yield from bevel((-0.25, -0.25), 0.05, 1)
    yield from bevel((0.25, 0.25), 0.05, 1)
    yield from pick((-0.2, -0.25))
    for point in ((-0.25, -0.2), (0.2, 0.25), (0.25, 0.2)):
        yield from select_box(*box_around((point[0], point[1], TOP), margin=25), keep=True)
    d.log('CHAMFERS {}'.format(selected()))
    yield from extrude_wall()
    d.shot('l44_diagonal')
    to_object_mode()
    yield 0.5
    yield from slide(5.2)
    over_view()
    d.key('NUMPAD_7')
    d.key('HOME')
    yield 0.8
    d.shot('l44_pieces')
    d.log('PIECES {}'.format([(o.name, round(o.location.x, 3), len(o.data.vertices), len(o.data.polygons)) for o in bpy.data.objects]))
    if STOP == 'pieces':
        return

    def world_screen(point):
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, Vector(point))
        return int(region.x + local.x), int(region.y + local.y)

    def look(pitch, turn):
        # A three-quarter view of everything, for the figures.
        r3d = viewport.spaces.active.region_3d
        from mathutils import Euler
        r3d.view_rotation = Euler((math.radians(pitch), 0, math.radians(turn))).to_quaternion()
        r3d.view_perspective = 'ORTHO'
        over_view()
        d.key('HOME')

    def select_objects(names, active):
        run(bpy.ops.object.select_all, action='DESELECT')
        for name in names:
            bpy.data.objects[name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[active]

    LUMPY = ['bank_straight_a', 'bank_straight_b', 'bank_straight_c', 'bank_land_corner_a', 'bank_land_corner_b']

    # The lumps: a Displace modifier on the first straight piece, pushing the wall's vertices along their normals by a Clouds
    # texture read in global coordinates, so a piece moved to another spot gets another pattern. Only the weighted vertices
    # move, which keeps the edges, the lip, and the foot still.
    select_objects(['bank_straight_a'], 'bank_straight_a')
    yield 0.4
    yield from d.press(1595, top(514))
    yield 0.6
    run(bpy.ops.object.modifier_add, type='DISPLACE')
    texture = bpy.data.textures.new('Lumps', 'CLOUDS')
    texture.noise_basis = 'IMPROVED_PERLIN'
    texture.noise_scale = 0.3
    texture.noise_depth = 3
    modifier = bpy.data.objects['bank_straight_a'].modifiers['Displace']
    modifier.name = 'Lumps'
    modifier.texture = texture
    modifier.texture_coords = 'GLOBAL'
    modifier.direction = 'NORMAL'
    modifier.strength = 0.3
    modifier.mid_level = 0.4
    modifier.vertex_group = 'lumps'
    # The jag: a second Displace with a Noise texture, which changes from vertex to vertex, on the lip's own group.
    run(bpy.ops.object.modifier_add, type='DISPLACE')
    jag_texture = bpy.data.textures.new('Jag', 'NOISE')
    jag = bpy.data.objects['bank_straight_a'].modifiers['Displace']
    jag.name = 'Jag'
    jag.texture = jag_texture
    jag.texture_coords = 'GLOBAL'
    jag.direction = 'NORMAL'
    jag.strength = 0.12
    jag.mid_level = 0.5
    jag.vertex_group = 'lip'
    yield 0.8
    d.shot('l44_displace')
    d.log('MODIFIER {} {} {} {} {}'.format(modifier.texture.name, modifier.texture_coords, modifier.direction, modifier.strength, modifier.mid_level))
    look(60, 25)
    yield 0.8
    d.shot('l44_displace_view')
    if STOP == 'displace':
        return
    # Copy Modifiers (Object > Link/Transfer Data) gives the other four lumpy pieces the same modifier, then Convert to Mesh applies them.
    select_objects(LUMPY, 'bank_straight_a')
    run(bpy.ops.object.make_links_data, type='MODIFIERS')
    d.log('COPIED {}'.format({name: [m.name for m in bpy.data.objects[name].modifiers] for name in LUMPY}))
    run(bpy.ops.object.convert, target='MESH')
    yield 0.8
    d.log('APPLIED {}'.format({name: len(bpy.data.objects[name].modifiers) for name in LUMPY}))
    look(60, 25)
    yield 0.8
    d.shot('l44_lumps')
    if STOP == 'lumps':
        return

    # The lip rose and fell with the lumps, but the top must stay at 0.012 to cover the ground's edge: in Edit Mode on all
    # five pieces at once, a front-view box takes the top and the lip, S Z 0 about the 3D cursor (at the origin) flattens
    # them to height 0, and G Z 0.012 lifts them back.
    select_objects(LUMPY, 'bank_straight_a')
    over_view()
    d.key('TAB')
    yield 0.8
    d.key('NUMPAD_1')
    yield 0.6
    d.key('HOME')
    yield 0.8
    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
    # X-ray (Alt+Z) lets the box take the vertices at the back too.
    d.key('Z', alt=True)
    yield 0.5
    yield from select_box(world_screen((0.6, 0, 0.1)), world_screen((4.3, 0, -0.04)))
    d.shot('l44_lip_selected')
    over_view()
    d.key('S')
    d.key('Z')
    d.type_text('0')
    d.key('RET')
    yield 0.4
    d.key('G')
    d.key('Z')
    d.type_text(str(TOP))
    d.key('RET')
    yield 0.5
    d.shot('l44_lip_flat')
    d.key('Z', alt=True)
    yield 0.4
    d.key('TAB')
    yield 0.8
    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
    for name in LUMPY:
        zs = [v.co.z for v in bpy.data.objects[name].data.vertices if v.co.z > -0.03]
        d.log('LIP {} count {} min {} max {}'.format(name, len(zs), round(min(zs), 5), round(max(zs), 5)))
    if STOP == 'lip':
        return

    # Smooth shading with the sharp lip kept: Object > Shade Auto Smooth at 30 degrees, then Convert to Mesh applies it.
    run(bpy.ops.object.select_all, action='SELECT')
    run(bpy.ops.object.shade_auto_smooth, angle=math.radians(30))
    run(bpy.ops.object.convert, target='MESH')
    yield 0.8
    d.log('SMOOTH {}'.format({o.name: len(o.modifiers) for o in bpy.data.objects}))
    run(bpy.ops.object.select_all, action='DESELECT')
    look(55, 25)
    yield 0.8
    d.shot('l44_kit')
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
    if STOP == 'smooth':
        return

    # One material for the whole kit: a new material on the first piece (the Material tab's New button), named bank_earth, then
    # Object > Link/Transfer Data > Link Materials copies it to the other six. Godot swaps it for the bank shader.
    select_objects(list(o.name for o in bpy.data.objects), 'bank_straight_a')
    yield from d.press(1595, top(654))
    yield 0.8
    material = bpy.data.materials.new('bank_earth')
    bpy.data.objects['bank_straight_a'].data.materials.append(material)
    run(bpy.ops.object.make_links_data, type='MATERIAL')
    yield 0.8
    d.shot('l44_material')
    d.log('MATERIALS {}'.format({o.name: [m.name for m in o.data.materials] for o in bpy.data.objects}))
    run(bpy.ops.object.select_all, action='DESELECT')
    yield 0.3
    if STOP == 'material':
        return

    # Export: the collection's own glTF exporter, as in lesson 36, into art/water.
    yield from d.press(1595, top(449))
    yield 0.8
    d.shot('l44_collection_tab')
    yield from d.press(1892, top(616))
    yield 0.4
    d.shot('l44_add_exporter')
    yield from d.press(1748, top(760))
    yield 0.8
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l44_exporter_panel')
    collection = bpy.data.collections['bank']
    d.log('EXPORTERS {}'.format([exporter.name for exporter in collection.exporters]))
    if STOP == 'exporter':
        return
    yield from d.press(1892, top(763))
    yield 1.5
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(EXPORT + os.sep, target=browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l44_export_folder', browser)
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('EXPORT folder exists {}'.format(os.path.isdir(EXPORT)))
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('bank_kit.glb', target=browser)
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l44_export_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    d.log('FILEPATH {}'.format(collection.exporters[0].export_properties.filepath))
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l44_exporter_settings')
    yield from d.press(1771, top(708))
    yield 2
    glb = os.path.join(EXPORT, 'bank_kit.glb')
    d.log('GLB exists {} size {}'.format(os.path.isfile(glb), os.path.getsize(glb) if os.path.isfile(glb) else 0))
    d.shot('l44_exported')
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))

    # Read the glb back: every piece, its triangle count, its extents, and the rule that lets any piece sit beside any other:
    # a wall vertex on a piece's edge is always 0.2 m from the edge's middle, and its rows are the same 13 heights.
    data = open(glb, 'rb').read()
    length = struct.unpack('<I', data[12:16])[0]
    gltf = json.loads(data[20:20 + length])
    chunk = 20 + length + 8
    binary = data[chunk:]
    names = [node['name'] for node in gltf['nodes']]
    d.log('GLB nodes {}'.format(sorted(names)))
    rows = None
    ends = set()
    for node in gltf['nodes']:
        mesh = gltf['meshes'][node['mesh']]
        primitive = mesh['primitives'][0]
        position = gltf['accessors'][primitive['attributes']['POSITION']]
        view = gltf['bufferViews'][position['bufferView']]
        offset = view.get('byteOffset', 0) + position.get('byteOffset', 0)
        points = [struct.unpack_from('<3f', binary, offset + 12 * i) for i in range(position['count'])]
        triangles = gltf['accessors'][primitive['indices']]['count'] // 3
        low = [round(min(p[i] for p in points), 3) for i in range(3)]
        high = [round(max(p[i] for p in points), 3) for i in range(3)]
        along = set()
        heights = set()
        for x, y, z in points:
            for axis, other in ((x, z), (z, x)):
                if abs(abs(axis) - 0.25) < 1e-5 and y < 0.0:
                    along.add(round(abs(other), 3))
                    heights.add(round(y, 3))
        d.log('GLB {} triangles {} min {} max {} wall edge offsets {} rows {}'.format(node['name'], triangles, low, high, sorted(along), len(heights)))
        ends |= along
        if heights:
            rows = rows or heights
            d.log('GLB {} rows match {}'.format(node['name'], heights == rows))
    d.log('GLB all wall edge offsets {}'.format(sorted(ends)))
