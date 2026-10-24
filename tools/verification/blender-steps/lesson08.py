# Lesson 8: Blender's first launch, units, axes, the hotkeys, and a startup file for modeling.
import bpy

HEIGHT = 1080


def bpy_extras_location(viewport, point):
    # Window coordinates of a 3D point in the viewport, to click an object as a reader does.
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    found = [item for item in viewport.regions if item.type == 'WINDOW'][0]
    local = location_3d_to_region_2d(found, viewport.spaces.active.region_3d, point)
    return found.x + int(local.x), found.y + int(local.y)

# Keymap entries the lesson's hotkey table names, read from Blender's default keymap.
WANTED = {
    'transform.translate', 'transform.rotate', 'transform.resize', 'object.mode_set', 'mesh.select_all', 'object.select_all',
    'object.delete', 'object.duplicate_move', 'mesh.duplicate_move', 'view3d.view_all', 'view3d.view_selected', 'view3d.view_axis',
    'view3d.toggle_xray', 'wm.search_menu', 'ed.undo', 'ed.redo', 'wm.context_toggle', 'view3d.view_persportho', 'mesh.select_mode',
    'wm.call_menu_pie', 'wm.call_menu', 'mesh.loopcut_slide', 'wm.save_mainfile', 'wm.save_as_mainfile', 'object.transform_apply',
    'view3d.rotate', 'view3d.move', 'view3d.zoom', 'wm.call_panel', 'view3d.localview',
}


def top(y):
    # Converts a screenshot's y (from the top) to Blender's window y (from the bottom).
    return HEIGHT - y


def dump_keymap(d):
    config = bpy.context.window_manager.keyconfigs.default
    seen = set()
    for keymap in config.keymaps:
        if keymap.name not in ('Window', 'Screen', '3D View', '3D View Generic', 'Object Mode', 'Object Non-modal', 'Mesh', 'View3D Walk Modal'):
            continue
        for item in keymap.keymap_items:
            if item.idname not in WANTED or not item.active:
                continue
            extra = ''
            for name in ('name', 'mode', 'type', 'data_path', 'action', 'toggle'):
                if name in item.properties.bl_rna.properties.keys():
                    value = getattr(item.properties, name)
                    if value not in ('', None):
                        extra += ' {}={}'.format(name, value)
            mods = ''.join(m for m, on in (('Ctrl+', item.ctrl), ('Shift+', item.shift), ('Alt+', item.alt), ('OS+', item.oskey)) if on == 1)
            line = 'KEY {}: {}{} = {}{} ({})'.format(keymap.name, item.idname, extra, mods, item.type, item.value)
            if line not in seen:
                seen.add(line)
                d.log(line)


def steps(d):
    yield 2
    d.shot('l08_quick_setup')
    # Continue on the Quick Setup splash keeps the defaults and saves the preferences.
    d.click(958, top(739))
    yield 1.5
    d.shot('l08_splash')
    d.key('ESC')
    yield 0.5
    d.shot('l08_layout')
    dump_keymap(d)
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    yield 0.3
    d.key('NUMPAD_1')
    yield 0.8
    d.shot('l08_front')
    region = viewport.spaces.active.region_3d
    d.log('FRONT view {} rotation {}'.format(region.view_perspective, tuple(round(v, 3) for v in region.view_rotation)))
    d.key('NUMPAD_7')
    yield 0.8
    d.shot('l08_top')
    d.key('ACCENT_GRAVE')
    yield 0.8
    d.shot('l08_view_pie')
    d.key('ESC')
    yield 0.5
    d.click(183, top(38))
    yield 0.6
    d.move(223, top(302))
    yield 1
    d.shot('l08_viewpoint_menu')
    d.key('ESC')
    yield 0.3
    d.key('ESC')
    yield 0.5
    # Back to perspective, then orbit with the middle mouse button to a three-quarter view.
    d.move(*d.center(viewport))
    d.key('NUMPAD_5')
    yield 0.5
    x, y = d.center(viewport)
    # Dragging up tilts the view to look down at the scene from above.
    yield from d.drag((x, y), (x + 120, y + 160), button='MIDDLEMOUSE')
    yield 0.5
    d.key('HOME')
    yield 0.8
    d.shot('l08_orbited')
    d.log('VIEW after orbit {} {}'.format(region.view_perspective, tuple(round(v, 3) for v in region.view_rotation)))

    # Units: the Scene tab of the Properties editor.
    d.click(1595, top(385))
    yield 0.5
    d.move(1760, top(900))
    d.click(1651, top(444))
    yield 0.8
    d.move(1760, top(1000))
    yield 0.5
    d.shot('l08_units')
    units = bpy.context.scene.unit_settings
    d.log('UNITS {} scale {} length {} rotation {}'.format(units.system, units.scale_length, units.length_unit, units.system_rotation))

    # The startup file: no camera or light, and the Statistics overlay on.
    d.click(1684, top(104))
    yield 0.3
    d.click(1684, top(144), ctrl=True)
    yield 0.3
    d.move(*d.center(viewport))
    yield 0.3
    d.shot('l08_selected_camera_light')
    d.key('DEL')
    yield 0.8
    d.log('OBJECTS after delete {}'.format([o.name for o in bpy.context.scene.objects]))
    d.click(1431, top(38))
    yield 0.8
    d.click(1296, top(256))
    yield 0.5
    d.shot('l08_statistics_on')
    d.key('ESC')
    d.move(*d.center(viewport))
    yield 0.8
    d.log('STATS {}'.format(viewport.spaces.active.overlay.show_stats))
    # Select the cube, so a new file starts with it selected.
    x, y = d.center(viewport)
    cube_screen = bpy_extras_location(viewport, (0, 0, 0))
    d.click(*cube_screen)
    yield 0.5
    # Home frames everything, now only the cube, so the startup file opens centered on it.
    d.move(*d.center(viewport))
    d.key('HOME')
    yield 0.6
    d.log('SELECTED {} active {}'.format([o.name for o in bpy.context.selected_objects], bpy.context.view_layer.objects.active.name))
    d.shot('l08_before_save')
    d.click(40, top(13))
    yield 0.6
    d.move(100, top(411))
    yield 1
    d.shot('l08_defaults_menu')
    d.click(310, top(410))
    yield 1
    d.shot('l08_save_startup')
    d.click(924, top(566))
    yield 1
    d.shot('l08_startup_saved')
    d.log('STARTUP FILE {}'.format(sorted(__import__('os').listdir(__import__('os').environ['BLENDER_USER_CONFIG']))))

    # Try it: a new General file is the startup file.
    d.move(*d.center(viewport))
    d.key('N', ctrl=True)
    yield 0.8
    d.shot('l08_new_menu')
    d.click(686, top(500))
    yield 1
    # The scene has changes, so Blender asks whether to save them first.
    d.shot('l08_save_changes')
    d.log('DIRTY before new file {}'.format(bpy.data.is_dirty))
    yield from d.press(986, top(568))
    yield 2
    d.wake()
    yield 0.5
    d.log('DIRTY after Dont Save {}'.format(bpy.data.is_dirty))
    viewport = d.area('VIEW_3D')
    d.log('NEW FILE objects {} selected {} stats {}'.format([o.name for o in bpy.context.scene.objects], [o.name for o in bpy.context.selected_objects],
                                                             viewport.spaces.active.overlay.show_stats))
    d.shot('l08_new_general')
    d.wake()
    yield 0.5
    d.move(*d.center(viewport))
    d.key('N')
    yield 0.8
    d.shot('l08_sidebar')
    cube = bpy.context.scene.objects['Cube']
    d.log('CUBE dimensions {}'.format(tuple(round(v, 3) for v in cube.dimensions)))
    d.key('N')
    yield 0.5

    # Try it: move, rotate, and scale by typed amounts, then undo all three.
    for keys in (('G', 'X', '2'), ('R', 'Z', '45'), ('S', None, '0.5')):
        d.key(keys[0])
        yield 0.3
        if keys[1]:
            d.key(keys[1])
            yield 0.2
        d.type_text(keys[2])
        yield 0.2
        d.key('RET')
        yield 0.5
    d.log('PRACTICE location {} rotation {} scale {}'.format(tuple(round(v, 3) for v in cube.location), tuple(round(__import__('math').degrees(v), 1) for v in cube.rotation_euler),
                                                          tuple(round(v, 3) for v in cube.scale)))
    d.shot('l08_practice')
    for _ in range(3):
        d.key('Z', ctrl=True)
        yield 0.5
    cube = bpy.context.scene.objects['Cube']
    d.log('UNDONE location {} rotation {} scale {}'.format(tuple(round(v, 3) for v in cube.location), tuple(cube.rotation_euler), tuple(cube.scale)))
