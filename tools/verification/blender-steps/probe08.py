# Reads the labels and defaults lessons 8 and 10 rely on from Blender itself. Run in the background:
# blender --background --factory-startup --python probe08.py
import bpy


def enum_names(struct, prop):
    return [(item.identifier, item.name) for item in struct.bl_rna.properties[prop].enum_items]


def prop_label(struct, prop):
    return struct.bl_rna.properties[prop].name


print('VERSION', bpy.app.version_string, bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes) else bpy.app.build_hash)
scene = bpy.context.scene
units = scene.unit_settings
print('UNITS', {p: (prop_label(units, p), getattr(units, p)) for p in ('system', 'scale_length', 'use_separate', 'system_rotation', 'length_unit', 'mass_unit', 'time_unit', 'temperature_unit')})
print('OBJECTS', [(o.name, o.type) for o in scene.objects])
print('WORKSPACES', [w.name for w in bpy.data.workspaces])
prefs = bpy.context.preferences
print('PREFS input', prop_label(prefs.inputs, 'use_emulate_numpad'), prefs.inputs.use_emulate_numpad, prop_label(prefs.inputs, 'use_mouse_emulate_3_button'))
print('PREFS autosave', prop_label(prefs, 'use_preferences_save'), prefs.use_preferences_save)
print('OVERLAY stats', prop_label(bpy.types.View3DOverlay, 'show_stats') if hasattr(bpy.types.View3DOverlay, 'bl_rna') else '')
print('SHADING color', enum_names(bpy.types.View3DShading, 'color_type'))
print('SHADING light', enum_names(bpy.types.View3DShading, 'light'))
print('IMAGE interpolation', enum_names(bpy.types.ShaderNodeTexImage, 'interpolation'))
print('SAVE HOME', bpy.ops.wm.save_homefile.get_rna_type().name, '| READ HOME', bpy.ops.wm.read_homefile.get_rna_type().name)
gltf = bpy.ops.export_scene.gltf.get_rna_type()
keep = ('export_format', 'use_selection', 'export_apply', 'export_yup', 'export_texcoords', 'export_normals', 'export_tangents',
        'export_materials', 'export_image_format', 'export_animations', 'export_skins', 'export_def_bones', 'export_extras',
        'export_texture_dir', 'export_keep_originals', 'use_active_collection', 'export_vertex_color', 'export_attributes')
for prop in gltf.properties:
    if prop.identifier in keep:
        items = [(item.identifier, item.name) for item in prop.enum_items] if prop.type == 'ENUM' else ''
        print('GLTF', prop.identifier, '|', prop.name, '| default', prop.default if prop.type != 'ENUM' else prop.default, items)
print('COLLECTION exporters', hasattr(bpy.types.Collection, 'exporters'), [op for op in dir(bpy.ops.collection) if 'export' in op])
for op in ('exporter_add', 'exporter_export', 'export_all'):
    if hasattr(bpy.ops.collection, op):
        print('COLLECTION OP', op, getattr(bpy.ops.collection, op).get_rna_type().name)
print('WM export all', [op for op in dir(bpy.ops.wm) if 'export' in op and 'collection' in op])
print('UV ops', bpy.ops.uv.snap_selected.get_rna_type().name, enum_names(bpy.ops.uv.snap_selected.get_rna_type(), 'target') if False else '')
space_image = bpy.types.SpaceImageEditor
print('IMAGE editor uv props', [p.identifier for p in bpy.types.SpaceUVEditor.bl_rna.properties][:60])

config = bpy.context.window_manager.keyconfigs.default
wanted = {
    'transform.translate', 'transform.rotate', 'transform.resize', 'object.mode_set', 'mesh.select_all', 'object.select_all',
    'object.delete', 'object.duplicate_move', 'mesh.duplicate_move', 'view3d.view_all', 'view3d.view_selected', 'view3d.view_axis',
    'view3d.toggle_xray', 'wm.call_panel', 'wm.search_menu', 'ed.undo', 'ed.redo', 'wm.context_toggle', 'object.hide_view_set',
    'object.hide_view_clear', 'view3d.localview', 'wm.call_menu', 'view3d.view_persportho', 'mesh.select_mode', 'view3d.toggle_shading',
    'wm.call_menu_pie', 'screen.region_toggle', 'view3d.select_box', 'view3d.select', 'mesh.loopcut_slide', 'mesh.extrude_region_move',
    'wm.save_mainfile', 'wm.save_as_mainfile', 'wm.read_homefile', 'wm.open_mainfile', 'object.transform_apply', 'view3d.rotate',
    'view3d.move', 'view3d.zoom', 'view3d.dolly', 'transform.edge_slide', 'mesh.select_linked_pick', 'uv.select_all',
}
seen = set()
for keymap in config.keymaps:
    for item in keymap.keymap_items:
        if item.idname not in wanted or not item.active:
            continue
        extra = ''
        for name in ('name', 'mode', 'type', 'data_path', 'action'):
            if name in item.properties.bl_rna.properties.keys():
                value = getattr(item.properties, name)
                if value not in ('', None):
                    extra += f' {name}={value}'
        mods = ''.join(m for m, on in (('Ctrl+', item.ctrl), ('Shift+', item.shift), ('Alt+', item.alt), ('OS+', item.oskey)) if on)
        key = f'{keymap.name}: {item.idname}{extra} = {mods}{item.type} ({item.value})'
        if key not in seen:
            seen.add(key)
            print('KEY', key)
