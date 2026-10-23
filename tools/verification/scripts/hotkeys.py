import bpy
wanted = {'mesh.loopcut_slide', 'transform.resize', 'transform.translate', 'object.mode_set', 'wm.call_menu', 'view3d.view_selected',
          'mesh.select_all', 'object.transform_apply', 'object.delete', 'view3d.view_axis', 'wm.save_mainfile', 'wm.save_as_mainfile',
          'mesh.select_mode', 'view3d.toggle_xray', 'object.select_all', 'wm.call_menu_pie'}
bpy.context.preferences.view.show_splash = False

def dump():
    config = bpy.context.window_manager.keyconfigs.default
    seen = set()
    for keymap in config.keymaps:
        if keymap.name not in ('Mesh', 'Object Mode', 'Object Non-modal', '3D View', '3D View Generic', 'Window', 'Screen'):
            continue
        for item in keymap.keymap_items:
            if item.idname not in wanted or not item.active:
                continue
            extra = ''
            if item.idname in ('wm.call_menu', 'wm.call_menu_pie'):
                extra = item.properties.name
                if extra not in ('VIEW3D_MT_object_apply', 'VIEW3D_MT_edit_mesh_select_mode', 'VIEW3D_MT_object_mode_pie'):
                    continue
            if item.idname == 'object.mode_set':
                extra = f'{item.properties.mode} toggle={item.properties.toggle}'
            if item.idname == 'view3d.view_axis':
                extra = item.properties.type
            mods = ''.join(m for m, on in (('Ctrl+', item.ctrl), ('Shift+', item.shift), ('Alt+', item.alt)) if on)
            key = f'{keymap.name}: {item.idname} {extra} = {mods}{item.type} ({item.value})'
            if key not in seen:
                seen.add(key)
                print('KEY', key)
    bpy.ops.wm.quit_blender()

bpy.app.timers.register(dump, first_interval=2.0)
