# Lesson 24: models the oak's trunk and branches from one vertex (extrude, Skin modifier, Subdivision Surface), colors
# them from the palette, and exports a .glb, from the startup file lesson 8 saved.
import math
import os

import bmesh
import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

HEIGHT = 1080
EXPORT = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench', 'art', 'nature', 'tree_oak')
FOLDER = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench', 'art_source', 'nature', 'tree_oak')


ROCK = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench', 'art_source', 'nature', 'rock_small')


def top(y, height=HEIGHT):
    return height - y


def steps(d):
    yield 2
    d.key('ESC')
    yield 0.5
    d.shot('l24_start')
    viewport = d.area('VIEW_3D')

    def screen_point(point):
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, bpy.context.active_object.matrix_world @ Vector(point))
        return region.x + int(local.x), region.y + int(local.y)

    # Rename with F2 over the 3D view: type, Enter.
    d.move(*d.center(viewport))
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('tree_oak')
    yield 0.3
    d.shot('l24_rename_field')
    d.key('RET')
    yield 0.5
    d.log('NAME {}'.format(bpy.context.active_object.name))

    # File > Save As into the project's art_source/nature/tree_oak folder.
    d.move(*d.center(viewport))
    d.key('S', ctrl=True, shift=True)
    yield 2
    browser = d.browser()
    d.shot('l24_save_as', browser)
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.key('A', ctrl=True, target=browser)
    d.type_text(FOLDER + os.sep, target=browser)
    yield 0.3
    d.shot('l24_path_typed', browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l24_create_folder', browser)
    d.click(516, top(54, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('FOLDER exists {} browser dir {}'.format(os.path.isdir(FOLDER), browser.screen.areas[0].spaces.active.params.directory))
    d.click(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.key('A', ctrl=True, target=browser)
    d.type_text('tree_oak.blend', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l24_file_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 0.5
    d.shot('l24_after_save_click', browser) if len(bpy.context.window_manager.windows) > 1 else None
    yield 2
    d.log('BROWSER size {}x{}'.format(browser.width, browser.height))
    d.log('WINDOWS after save {} file {}'.format(len(bpy.context.window_manager.windows), bpy.data.filepath))


    tree = bpy.context.active_object
    d.wake()
    yield 0.3
    d.move(*d.center(viewport))
    d.key('TAB')
    yield 0.5
    d.key('ONE')
    d.key('A')
    yield 0.3
    d.key('M')
    yield 0.5
    d.shot('l24_merge_menu')
    d.key('C')
    yield 0.5
    mesh = bmesh.from_edit_mesh(tree.data)
    d.log('MERGED verts {} edges {} at {}'.format(len(mesh.verts), len(mesh.edges), [tuple(v.co) for v in mesh.verts]))
    d.shot('l24_one_vertex')
    # Sink the foot 10 cm below the ground, so the trunk never floats above it.
    d.key('G')
    d.key('Z')
    d.type_text('-0.1')
    d.key('RET')
    yield 0.4
    def extrude(offset):
        # E extrudes the selected vertex and starts a move; the typed numbers are X, Y, and Z, with Tab between.
        d.key('E')
        yield 0.2
        for number, value in enumerate(offset):
            if number:
                d.key('TAB')
            d.type_text(str(value))
        d.key('RET')
        yield 0.3

    def select_vertex(index):
        # Clicks the vertex that is at position `positions[index]`.
        d.move(*d.center(viewport))
        d.key('A', alt=True)
        yield 0.2
        d.click(*screen_point(positions[index]))
        yield 0.3
        mesh = bmesh.from_edit_mesh(tree.data)
        picked = [tuple(round(c, 3) for c in v.co) for v in mesh.verts if v.select]
        d.log('SELECT {} wanted {} picked {}'.format(index, tuple(round(c, 3) for c in positions[index]), picked))

    positions = [(0.0, 0.0, -0.1)]
    parents = [-1]

    def grow(parent, offset):
        # Extrudes from the selected vertex and records the new position.
        yield from extrude(offset)
        base = positions[parent]
        positions.append(tuple(round(base[axis] + offset[axis], 4) for axis in range(3)))
        parents.append(parent)

    d.key('A', alt=True)
    d.click(*screen_point(positions[0]))
    yield 0.3
    d.key('NUMPAD_PERIOD')
    yield 0.6
    chain = ((0, (0, 0, 0.4)), (1, (0.03, 0, 0.7)), (2, (-0.03, 0.03, 1.15)))
    for parent, offset in chain:
        yield from grow(parent, offset)
    d.key('A')
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l24_trunk')
    for _ in range(6):
        d.key('WHEELDOWNMOUSE')
        yield 0.1
    yield 0.6
    d.log('TRUNK {}'.format(positions))
    # A limb, a second limb, and the leader grow from the fork (vertex 3).
    plans = (
        (3, ((-0.35, 0.02, 0.6), (-0.35, 0.05, 0.6), (-0.1, 0.05, 0.5))),
        (3, ((0.4, -0.13, 0.7), (0.35, -0.05, 0.6), (0.1, 0.05, 0.5))),
        (3, ((0.03, 0.02, 0.9), (0.02, 0.05, 0.8), (-0.02, -0.05, 0.6))),
        (10, ((-0.28, 0.4, 0.5), (-0.1, 0.25, 0.5))),
        (10, ((0.27, -0.55, 0.6), (0.15, -0.2, 0.5))),
    )
    for start, offsets in plans:
        yield from select_vertex(start)
        parent = start
        for offset in offsets:
            yield from grow(parent, offset)
            parent = len(positions) - 1
        d.shot('l24_plan_{}'.format(len(positions)))
    d.log('ALL {}'.format(positions))
    d.shot('l24_skeleton')
    yield 0.5
    mesh = bmesh.from_edit_mesh(tree.data)
    d.log('SKELETON verts {} edges {} max z {}'.format(len(mesh.verts), len(mesh.edges), max(v.co.z for v in mesh.verts)))

    d.move(*d.center(viewport))
    d.key('A')
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.key('A', alt=True)
    yield 0.3
    d.shot('l24_skeleton_framed')
    yield from d.press(1595, top(514))
    yield 0.6
    yield from d.press(1784, top(304))
    yield 0.8
    yield 0.8
    d.shot('l24_add_modifier_menu')
    d.type_text('skin')
    yield 1.0
    d.key('RET')
    yield 1.0
    d.shot('l24_skin_added')
    d.log('MODIFIERS {}'.format([(m.name, m.type) for m in tree.modifiers]))
    # The tree is not symmetric: turn the modifier's X symmetry off.
    yield from d.press(1756, top(386))
    yield 0.4
    d.log('SYMMETRY x {}'.format(tree.modifiers['Skin'].use_x_symmetry))
    d.move(*d.center(viewport))
    d.key('Z', alt=True)
    yield 0.6
    d.shot('l24_skin_thick')

    def radii():
        mesh = bmesh.from_edit_mesh(tree.data)
        layer = mesh.verts.layers.skin.active
        return [round(v[layer].radius[0], 3) for v in mesh.verts]

    d.log('RADII before {}'.format(radii()))
    # The Mesh menu's Transform submenu holds Skin Resize (Ctrl+A).
    yield from d.press(356, top(38))
    yield 0.5
    d.move(393, top(60))
    yield 0.8
    d.move(420, top(60))
    yield 0.6
    d.shot('l24_transform_menu')
    d.key('ESC')
    yield 0.4
    classes = (((0,), 1.6), ((1,), 1.12), ((2,), 0.88), ((3,), 0.8), ((10,), 0.64), ((4, 7), 0.56), ((11, 13, 15), 0.36), ((5, 8), 0.32), ((6, 9, 12, 14, 16), 0.16))
    for members, factor in classes:
        d.move(*d.center(viewport))
        d.key('A', alt=True)
        yield 0.2
        for number, index in enumerate(members):
            d.click(*screen_point(positions[index]), shift=number > 0)
            yield 0.25
        mesh = bmesh.from_edit_mesh(tree.data)
        d.log('CLASS {} selected {}'.format(members, sum(1 for v in mesh.verts if v.select)))
        d.move(*d.center(viewport))
        d.key('A', ctrl=True)
        d.type_text(str(factor))
        yield 0.2
        d.key('RET')
        yield 0.4
    d.log('RADII after {}'.format(radii()))
    d.key('A', alt=True)
    yield 0.4
    d.shot('l24_skin_radii')

    d.move(*d.center(viewport))
    d.key('Z', alt=True)
    yield 0.4
    d.key('TAB')
    yield 0.6
    d.log('MODE {}'.format(bpy.context.mode))
    yield from d.press(1784, top(298))
    yield 0.8
    d.type_text('subdivision')
    yield 1.0
    d.shot('l24_subsurf_search')
    d.key('RET')
    yield 1.0
    d.log('MODIFIERS {}'.format([(m.name, m.type) for m in tree.modifiers]))
    evaluated = tree.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh_eval = evaluated.to_mesh()
    mesh_eval.calc_loop_triangles()
    d.log('EVAL tris {} verts {} uv_layers {} dims {}'.format(len(mesh_eval.loop_triangles), len(mesh_eval.vertices), [u.name for u in mesh_eval.uv_layers], tuple(round(v, 3) for v in tree.dimensions)))
    d.log('BASE uv_layers {}'.format([u.name for u in tree.data.uv_layers]))
    d.shot('l24_subsurf')

    # Shade Smooth from the Object menu, then apply both modifiers (Ctrl+A over each panel), Skin first.
    yield from d.press(312, top(38))
    yield 0.6
    d.shot('l24_object_menu')
    yield from d.press(355, top(492))
    yield 0.6
    d.log('SMOOTH {}'.format(all(polygon.use_smooth for polygon in tree.data.polygons)))
    for name in ('Skin', 'Subdivision'):
        d.move(1700, top(331))
        yield 0.5
        d.key('A', ctrl=True)
        yield 0.8
        d.log('APPLIED {} modifiers {} verts {} uv {}'.format(name, [m.name for m in tree.modifiers], len(tree.data.vertices), [u.name for u in tree.data.uv_layers]))
    d.move(*d.center(viewport))
    yield 0.5
    d.shot('l24_applied')
    d.log('TRIS {} dims {}'.format(sum(len(p.vertices) - 2 for p in tree.data.polygons), tuple(round(v, 3) for v in tree.dimensions)))

    # File > Append: the palette material from the rock's file.
    yield from d.press(40, top(13))
    yield 0.5
    d.move(70, top(40))
    yield 0.6
    d.shot('l24_file_menu')
    for y in range(40, 251, 30):
        d.move(80, top(y))
        yield 0.1
    d.move(80, top(250))
    yield 0.6
    d.shot('l24_append_hover')
    d.click(80, top(250))
    yield 2
    browser = d.browser()
    d.log('WINDOWS {}'.format([(w.width, w.height, [a.type for a in w.screen.areas]) for w in bpy.context.window_manager.windows]))
    d.shot('l24_after_append_click')
    d.log('BROWSER {}x{}'.format(browser.width, browser.height))
    d.shot('l24_append_browser', browser)
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(os.path.join(ROCK, 'rock_small.blend') + os.sep + 'Material' + os.sep, target=browser)
    yield 0.3
    d.shot('l24_append_path', browser)
    d.key('RET', target=browser)
    yield 2.5
    d.shot('l24_append_list', browser)
    yield from d.press(300, top(77, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(300, top(77, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.shot('l24_append_selected', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 2
    d.log('MATERIALS {} IMAGES {}'.format([m.name for m in bpy.data.materials], [(i.name, i.filepath) for i in bpy.data.images]))
    d.log('WINDOWS {}'.format([(w.width, w.height, [a.type for a in w.screen.areas]) for w in bpy.context.window_manager.windows]))
    d.click(1400, 5)
    yield 0.5
    yield from d.press(1595, top(653))
    yield 0.6
    d.move(1700, top(500))
    yield 0.3
    d.shot('l24_material_tab')
    yield from d.press(1634, top(382))
    yield 0.6
    d.move(1640, top(400))
    yield 0.6
    d.shot('l24_material_browse')
    d.type_text('palette')
    yield 0.6
    d.shot('l24_material_search')
    d.key('RET')
    yield 0.6
    d.log('MATERIALS {} IMAGES {}'.format([m.name for m in bpy.data.materials], [(i.name, i.filepath) for i in bpy.data.images]))
    d.log('WINDOWS {}'.format([(w.width, w.height, [a.type for a in w.screen.areas]) for w in bpy.context.window_manager.windows]))
    d.click(1400, 5)
    yield 0.5
    yield from d.press(1595, top(653))
    yield 0.6
    d.move(1700, top(500))
    yield 0.3
    d.shot('l24_material_tab')
    yield from d.press(1634, top(382))
    yield 0.6
    d.move(1640, top(400))
    yield 0.6
    d.shot('l24_material_browse')
    for y in range(400, 436, 7):
        d.move(1660, top(y))
        yield 0.15
    yield 0.4
    d.shot('l24_dbg_hover')
    d.click(1660, top(435))
    yield 0.6
    d.shot('l24_dbg_after')
    d.log('MATERIAL {}'.format([slot.material.name for slot in tree.material_slots]))
    d.move(1700, top(500))
    yield 0.3
    d.shot('l24_material_palette')

    # The mesh is still named Cube.
    yield from d.press(1595, top(626))
    yield 0.5
    yield from d.press(1760, top(297))
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text('tree_oak')
    yield 0.2
    d.key('RET')
    yield 0.4
    d.move(1760, top(1000))
    yield 0.3
    d.log('MESH {}'.format(tree.data.name))
    d.shot('l24_mesh_name')

    # UV Editing: a UV map by Unwrap, then every face's UVs onto one swatch of the bark ramp.
    yield from d.press(495, top(13))
    yield 1.5
    editor = d.area('IMAGE_EDITOR')
    viewport = d.area('VIEW_3D')
    d.log('WORKSPACE {} mode {}'.format(d.window().workspace.name, bpy.context.mode))
    d.shot('l24_uv_workspace')
    # The Data tab's UV Maps panel: the plus button adds a UV map.
    yield from d.press(1665, top(630))
    yield 0.6
    d.move(1760, top(1000))
    yield 0.4
    d.shot('l24_uv_maps_panel')
    yield from d.press(1891, top(660))
    yield 0.8
    d.log('UV layers {}'.format([u.name for u in tree.data.uv_layers]))
    d.move(1760, top(1000))
    yield 0.4
    d.shot('l24_uv_added')
    # UV Sync Selection off, then every UV onto the second swatch of the browns ramp.
    yield from d.press(57, top(38))
    yield 0.3
    d.log('UV SYNC {}'.format(bpy.context.scene.tool_settings.use_uv_select_sync))
    d.shot('l24_sync_off')
    d.move(*d.center(viewport))
    d.key('THREE')
    d.key('A')
    yield 0.4
    d.move(editor.x + editor.width // 3, editor.y + editor.height // 2)
    yield 0.2
    d.key('A')
    yield 0.2
    d.key('S')
    d.type_text('0')
    d.key('RET')
    yield 0.4
    d.key('N')
    yield 0.6
    for field_y, value in ((122, '0.1875'), (142, '0.6875')):
        yield from d.press(640, top(field_y))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(value)
        yield 0.2
        d.key('RET')
        yield 0.4
    d.move(editor.x + editor.width // 3, editor.y + editor.height // 2)
    yield 0.3
    d.shot('l24_uv_collapsed')
    mesh = bmesh.from_edit_mesh(tree.data)
    layer = mesh.loops.layers.uv.active
    points = {(round(loop[layer].uv.x, 4), round(loop[layer].uv.y, 4)) for face in mesh.faces for loop in face.loops}
    d.log('UV points {}'.format(sorted(points)))
    yield from d.press(287, top(13))
    yield 1.5
    d.key('TAB')
    yield 0.6
    d.log('MODE {}'.format(bpy.context.mode))
    # Show the palette in the viewport: Viewport Shading > Color > Texture.
    yield from d.press(1557, top(38))
    yield 0.4
    d.shot('l24_shading_popover')
    yield from d.press(1555, top(403))
    yield 0.4
    d.key('ESC')
    yield 0.4
    d.log('SHADING color {}'.format(d.area('VIEW_3D').spaces.active.shading.color_type))
    d.move(*d.center(d.area('VIEW_3D')))
    for name in ('NUMPAD_4', 'NUMPAD_4'):
        d.key(name)
        yield 0.3
    yield 0.4
    corners = [tree.matrix_world @ Vector(corner) for corner in tree.bound_box]
    d.log('BOUNDS min {} max {}'.format(tuple(round(min(c[i] for c in corners), 3) for i in range(3)), tuple(round(max(c[i] for c in corners), 3) for i in range(3))))
    d.shot('l24_colored')

    # Export: name the collection after the asset, then give it a glTF exporter.
    d.move(1670, top(84))
    yield from d.press(1670, top(84))
    yield 0.3
    d.key('F2')
    yield 0.4
    d.key('A', ctrl=True)
    d.type_text('tree_oak')
    yield 0.2
    d.shot('l24_rename_collection')
    d.key('RET')
    yield 0.5
    d.log('COLLECTIONS {}'.format([collection.name for collection in bpy.data.collections]))
    yield from d.press(1595, top(449))
    yield 0.5
    yield from d.press(1892, top(616))
    yield 0.4
    d.shot('l24_add_exporter')
    yield from d.press(1748, top(760))
    yield 0.8
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l24_exporter_panel')
    collection = tree.users_collection[0]
    d.log('EXPORTERS {}'.format([(exporter.name, exporter.filepath if hasattr(exporter, 'filepath') else '') for exporter in collection.exporters]))

    # File Path: the folder button opens the File Browser; the .glb goes in art/nature/tree_oak.
    yield from d.press(1892, top(763))
    yield 1.5
    browser = d.browser()
    d.log('PATH BROWSER {}x{}'.format(browser.width, browser.height))
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(EXPORT + os.sep, target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 1
    d.shot('l24_export_folder', browser)
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('EXPORT folder exists {}'.format(os.path.isdir(EXPORT)))
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('tree_oak.glb', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l24_export_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    exporter = collection.exporters[0]
    d.log('FILEPATH {}'.format(exporter.export_properties.filepath))
    yield from d.press(1665, top(898))
    yield 0.6
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l24_data_panel')
    yield from d.press(1680, top(947))
    yield 0.5
    d.move(1760, top(700))
    for _ in range(12):
        d.key('WHEELDOWNMOUSE')
        yield 0.05
    yield 0.5
    d.shot('l24_mesh_panel')
    yield from d.press(1747, top(498))
    yield 0.4
    yield from d.press(1659, top(885))
    yield 0.4
    yield from d.press(1674, top(730))
    yield 0.6
    d.move(1760, top(1060))
    yield 0.3
    properties = exporter.export_properties
    d.log('SETTINGS apply {} animations {} images {} materials {}'.format(properties.export_apply, properties.export_animations, properties.export_image_format, properties.export_materials))
    d.shot('l24_material_panel')
    yield from d.press(1820, top(785))
    yield 0.4
    d.shot('l24_images_menu')
    yield from d.press(1763, top(874))
    yield 0.4
    d.log('IMAGES setting {}'.format(properties.export_image_format))
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l24_exporter_settings')
    yield from d.press(1892, top(252))
    yield 2
    glb = os.path.join(EXPORT, 'tree_oak.glb')
    d.log('GLB exists {} size {}'.format(os.path.isfile(glb), os.path.getsize(glb) if os.path.isfile(glb) else 0))
    d.shot('l24_exported')
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('S', ctrl=True)
    yield 1
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
