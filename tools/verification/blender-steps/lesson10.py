# Lesson 10: colors the rock from the palette (a palette material, UVs collapsed onto swatches) and exports a .glb
# with a collection exporter, the reader's way, from lesson 9's rock_small.blend.
import os

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d

WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
PALETTE = os.path.join(WORKBENCH, 'art', 'palette')
EXPORT = os.path.join(WORKBENCH, 'art', 'nature', 'rock_small')


def top(y, height=1080):
    return height - y


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    rock = bpy.data.objects['rock_small']
    d.shot('l10_start')

    # Name the mesh after the object too; Godot shows the mesh's name.
    yield from d.press(1595, top(626))
    yield 0.5
    yield from d.press(1760, top(297))
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text('rock_small')
    yield 0.2
    d.key('RET')
    yield 0.4
    d.move(1760, top(1000))
    yield 0.3
    d.shot('l10_mesh_name')
    d.log('MESH {}'.format(rock.data.name))

    # The material: rename Blender's default one to palette and give its Base Color the palette image.
    yield from d.press(1595, top(653))
    yield 0.6
    d.shot('l10_material_tab')
    yield from d.press(1730, top(382))
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text('palette')
    yield 0.2
    d.key('RET')
    yield 0.5
    d.log('MATERIAL {}'.format([slot.material.name for slot in rock.material_slots]))
    yield from d.press(1742, top(508))
    yield 0.3
    d.shot('l10_base_color_menu')
    yield from d.press(1315, top(641))
    yield 0.8
    d.move(1760, top(1000))
    yield 0.4
    d.shot('l10_image_texture')
    yield from d.press(1848, top(533))
    yield 2
    browser = d.browser()
    d.log('BROWSER {}x{} title area {}'.format(browser.width, browser.height, browser.screen.areas[0].type))
    # A new window may take its first click to become active; a second click on a field being edited only moves
    # its cursor, so two clicks are safe either way.
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(PALETTE + os.sep, target=browser)
    yield 0.3
    d.shot('l10_open_path', browser)
    d.key('RET', target=browser)
    yield 1
    # Click palette.png in the file list, then Open Image.
    d.shot('l10_open_list', browser)
    # The first click may only end the path field's editing; a second click on the same row is harmless.
    yield from d.press(300, top(77, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(300, top(77, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.shot('l10_open_image', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    d.log('IMAGES {}'.format([(image.name, image.filepath, tuple(image.size)) for image in bpy.data.images]))
    d.move(1760, top(1000))
    yield 0.3
    d.shot('l10_image_opened')
    yield from d.press(1808, top(558))
    yield 0.3
    d.shot('l10_interpolation_menu')
    yield from d.press(1762, top(631))
    yield 0.5
    node = [node for node in rock.material_slots[0].material.node_tree.nodes if node.type == 'TEX_IMAGE'][0]
    d.log('INTERPOLATION {}'.format(node.interpolation))
    d.move(1760, top(1000))
    yield 0.3
    d.shot('l10_closest')
    yield from d.press(1557, top(38))
    yield 0.4
    d.shot('l10_shading_popover')
    yield from d.press(1555, top(403))
    yield 0.4
    d.key('ESC')
    yield 0.4
    d.log('SHADING color {}'.format(d.area('VIEW_3D').spaces.active.shading.color_type))
    d.shot('l10_texture_solid')

    # UV Editing: the UV Editor on the left, the 3D view on the right in Edit Mode.
    yield from d.press(495, top(13))
    yield 1.5
    d.log('WORKSPACE {} mode {}'.format(d.window().workspace.name, bpy.context.mode))
    editor = d.area('IMAGE_EDITOR')
    viewport = d.area('VIEW_3D')
    d.shot('l10_uv_workspace')
    d.log('UV EDITOR image {}'.format(editor.spaces.active.image.name if editor.spaces.active.image else None))
    # UV Sync Selection is on by default; with it on, selecting faces also selects the corners they share with their
    # neighbors, and collapsing them would drag the neighbors' UVs along. Its button is at the left of the header.
    yield from d.press(57, top(38))
    yield 0.3
    d.log('UV SYNC {}'.format(bpy.context.scene.tool_settings.use_uv_select_sync))
    d.shot('l10_sync_off')

    # Swatch centers in UV units: x = (column + 0.5) / 8, y = 1 - (row + 0.5) / 8, for an 8 by 8 palette.
    def swatch(column, row):
        return '{:.4f}'.format((column + 0.5) / 8), '{:.4f}'.format(1 - (row + 0.5) / 8)

    def uv_points(faces):
        mesh = bmesh.from_edit_mesh(rock.data)
        layer = mesh.loops.layers.uv.active
        return sorted({(round(loop[layer].uv.x, 4), round(loop[layer].uv.y, 4)) for face in mesh.faces if face.index in faces for loop in face.loops})

    sidebar_open = [False]

    def place(column, row, name):
        # Over the UV Editor: S, 0, Enter collapses the selected faces' UVs to one point; the Sidebar's UV Vertex
        # fields then move that point to the swatch's center.
        d.move(editor.x + editor.width // 3, editor.y + editor.height // 2)
        yield 0.2
        # A selects every UV the editor shows: those of the faces selected in the 3D view.
        d.key('A')
        yield 0.2
        d.key('S')
        d.type_text('0')
        d.key('RET')
        yield 0.4
        if not sidebar_open[0]:
            d.key('N')
            yield 0.6
            sidebar_open[0] = True
        x, y = swatch(column, row)
        for field_y, value in ((122, x), (142, y)):
            yield from d.press(640, top(field_y))
            yield 0.2
            d.key('A', ctrl=True)
            d.type_text(value)
            yield 0.2
            d.key('RET')
            yield 0.4
        d.move(editor.x + editor.width // 3, editor.y + editor.height // 2)
        yield 0.3
        d.shot(name)

    # Everything first, on the stone ramp's dark swatch: the sides keep it.
    d.move(*d.center(viewport))
    d.key('THREE')
    d.key('A')
    yield 0.4
    yield from place(1, 0, 'l10_uv_sides')
    mesh = bmesh.from_edit_mesh(rock.data)
    d.log('SIDES uv {}'.format(uv_points({face.index for face in mesh.faces})))

    def faces_facing(sign):
        mesh = bmesh.from_edit_mesh(rock.data)
        return [face.index for face in mesh.faces if face.normal.z * sign > 0.7]

    def face_screen(index):
        mesh = bmesh.from_edit_mesh(rock.data)
        mesh.faces.ensure_lookup_table()
        region = d.region(viewport)
        local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, rock.matrix_world @ mesh.faces[index].calc_center_median())
        return region.x + int(local.x), region.y + int(local.y)

    for sign, view, column, name in ((1, 'top', 2, 'l10_uv_top'), (-1, 'bottom', 0, 'l10_uv_bottom')):
        d.move(*d.center(viewport))
        d.key('NUMPAD_7', ctrl=(sign < 0))
        yield 0.6
        d.key('NUMPAD_PERIOD')
        yield 0.6
        wanted = faces_facing(sign)
        for number, index in enumerate(wanted):
            d.click(*face_screen(index), shift=number > 0)
            yield 0.3
        mesh = bmesh.from_edit_mesh(rock.data)
        selected = [face.index for face in mesh.faces if face.select]
        d.log('{} faces wanted {} selected {}'.format(view.upper(), wanted, selected))
        d.shot('l10_select_' + view)
        yield from place(column, 0, name)
        d.log('{} uv {}'.format(view.upper(), uv_points(set(wanted))))

    # Back to Layout and Object Mode to see the colors.
    yield from d.press(288, top(13))
    yield 1.5
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    if bpy.context.mode != 'OBJECT':
        d.key('TAB')
        yield 0.5
    d.log('LAYOUT mode {} shading {}'.format(bpy.context.mode, viewport.spaces.active.shading.color_type))
    for name in ('NUMPAD_1', 'NUMPAD_8', 'NUMPAD_8', 'NUMPAD_8', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_PERIOD'):
        d.key(name)
        yield 0.3
    yield 0.4
    d.shot('l10_colored')

    # Export: name the collection after the asset, then give it a glTF exporter.
    d.move(1670, top(84))
    yield from d.press(1670, top(84))
    yield 0.3
    d.key('F2')
    yield 0.4
    d.key('A', ctrl=True)
    d.type_text('rock_small')
    yield 0.2
    d.shot('l10_rename_collection')
    d.key('RET')
    yield 0.5
    d.log('COLLECTIONS {}'.format([collection.name for collection in bpy.data.collections]))
    yield from d.press(1595, top(449))
    yield 0.5
    yield from d.press(1892, top(616))
    yield 0.4
    d.shot('l10_add_exporter')
    yield from d.press(1748, top(760))
    yield 0.8
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l10_exporter_panel')
    collection = rock.users_collection[0]
    d.log('EXPORTERS {}'.format([(exporter.name, exporter.filepath if hasattr(exporter, 'filepath') else '') for exporter in collection.exporters]))

    # File Path: the folder button opens the File Browser; the .glb goes in art/nature/rock_small.
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
    d.shot('l10_export_folder', browser)
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('EXPORT folder exists {}'.format(os.path.isdir(EXPORT)))
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('rock_small.glb', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l10_export_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    exporter = collection.exporters[0]
    d.log('FILEPATH {}'.format(exporter.export_properties.filepath))
    yield from d.press(1665, top(898))
    yield 0.6
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l10_data_panel')
    yield from d.press(1680, top(947))
    yield 0.5
    d.move(1760, top(700))
    for _ in range(12):
        d.key('WHEELDOWNMOUSE')
        yield 0.05
    yield 0.5
    d.shot('l10_mesh_panel')
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
    d.shot('l10_material_panel')
    yield from d.press(1820, top(785))
    yield 0.4
    d.shot('l10_images_menu')
    yield from d.press(1763, top(874))
    yield 0.4
    d.log('IMAGES setting {}'.format(properties.export_image_format))
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l10_exporter_settings')
    yield from d.press(1892, top(252))
    yield 2
    glb = os.path.join(EXPORT, 'rock_small.glb')
    d.log('GLB exists {} size {}'.format(os.path.isfile(glb), os.path.getsize(glb) if os.path.isfile(glb) else 0))
    d.shot('l10_exported')
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('S', ctrl=True)
    yield 1
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
