import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_popups, dump_windows, open_in_file_dialog, press_delete_in_scene_dock, add_node, new_resource, inspector_set, option_items, show_row, unfold_inspector, view, INSPECTOR

steps = [
    # The root node.
    {'op': 'capture', 'name': 'l04_start', 'frames': 40},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': '3D Scene'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] root ", root.name, " ", root.get_class())
root.name = "Meadow"
'''),
    {'op': 'select', 'path': '.'},
    {'op': 'capture', 'name': 'l04_root', 'frames': 30},
    # Save it.
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    {'op': 'capture', 'name': 'l04_save_dialog', 'window': 'Save Scene As'},
    open_in_file_dialog('levels'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l04_save_dialog_levels', 'window': 'Save Scene As'},
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
]
# The ground.
steps += add_node('MeshInstance3D', 'Ground')
steps += new_resource('mesh', 'PlaneMesh', nth=-1)
steps += [
    inspector_set('size', 'Vector2(20, 20)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l04_ground_inspector', 'frames': 20},
    *view(),
    {'op': 'capture', 'name': 'l04_ground', 'frames': 30},
    # The editor's preview sun and environment buttons.
    eval_('''
for button in plugin._collect(plugin.get_tree().root, "Button", ""):
	var rect: Rect2 = button.get_global_rect()
	if button.is_visible_in_tree() and rect.position.y > 75 and rect.position.y < 110 and rect.position.x > 800 and rect.position.x < 920:
		print("[probe] preview button '", button.tooltip_text.replace("\\n", " | "), "' pressed ", button.button_pressed)
'''),
]
# The environment.
steps += add_node('WorldEnvironment', 'WorldEnvironment')
steps += [
    eval_('''
var node := editor.get_edited_scene_root().get_node("WorldEnvironment") as WorldEnvironment
print("[probe] auto environment ", node.environment)
'''),
    {'op': 'capture', 'name': 'l04_environment_added', 'frames': 30},
    # Clicking the Environment resource opens its properties below it.
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'environment', 'type': 'Button', 'nth': 0}},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l04_environment_default', 'frames': 30},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    option_items('background_mode'),
    inspector_set('background_mode', 2),
    {'op': 'wait', 'frames': 20},
]
steps += new_resource('sky', 'Sky')
steps += [eval_('''
var node := editor.get_edited_scene_root().get_node("WorldEnvironment") as WorldEnvironment
print("[probe] new sky ", node.environment.sky, " material ", node.environment.sky.sky_material)
'''), {'op': 'capture', 'name': 'l04_new_sky', 'frames': 20}]
steps += new_resource('sky_material', 'ProceduralSkyMaterial', nth=-1)
steps += [
    {'op': 'capture', 'name': 'l04_environment_sky', 'frames': 30},
    option_items('tonemap_mode'),
    inspector_set('tonemap_mode', 4),
    show_row('tonemap_mode'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l04_environment_tonemap', 'frames': 30},
    *view(),
    {'op': 'capture', 'name': 'l04_with_environment', 'frames': 30},
]
# The sun.
steps += add_node('DirectionalLight3D', 'Sun')
steps += [
    {'op': 'capture', 'name': 'l04_sun_added', 'frames': 30},
    inspector_set('rotation', 'Vector3(deg_to_rad(-55), deg_to_rad(45), 0)'),
    show_row('rotation'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l04_sun_rotation', 'frames': 30},
    # Shadow is a section heading with its own On box.
    eval_('''
var sun := editor.get_edited_scene_root().get_node("Sun") as DirectionalLight3D
var undo := editor.get_editor_undo_redo()
undo.create_action("Set shadow_enabled")
undo.add_do_property(sun, "shadow_enabled", true)
undo.add_undo_property(sun, "shadow_enabled", false)
undo.commit_action()
for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
	section.unfold()
await plugin.get_tree().process_frame
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "shadow_bias")
if row:
	editor.get_inspector().ensure_control_visible(row)
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l04_sun_shadow', 'frames': 30},
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    *view('Ground', dy=40),
    {'op': 'capture', 'name': 'l04_final', 'frames': 60},
]
# Try it: a temporary box shows the sun's shadow.
steps += add_node('MeshInstance3D', 'Box')
steps += [
    eval_('print("[probe] box mesh ", (editor.get_edited_scene_root().get_node("Box") as MeshInstance3D).mesh)'),
    inspector_set('position', 'Vector3(0, 0.5, 0)'),
    *view('Box', dy=50, wheel=-4),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'l04_box_shadow', 'frames': 20},
    {'op': 'select', 'path': 'Sun'},
    inspector_set('rotation', 'Vector3(deg_to_rad(-20), deg_to_rad(45), 0)'),
    eval_('editor.get_selection().clear()'),
    {'op': 'capture', 'name': 'l04_box_low_sun', 'frames': 60},
    {'op': 'select', 'path': 'Sun'},
    inspector_set('rotation', 'Vector3(deg_to_rad(-55), deg_to_rad(45), 0)'),
    {'op': 'select', 'path': 'Box'},
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    dump_windows(),
    {'op': 'capture', 'name': 'l04_delete_box', 'frames': 10},
    {'op': 'capture', 'name': 'l04_delete_confirm', 'window': 'class:ConfirmationDialog'},
    {'op': 'press', 'find': {'type': 'Button', 'text': 'Delete'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
if editor.get_edited_scene_root().get_node_or_null("Box") != null:
	return "the Box is still there"
'''),
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    eval_('print("[probe] meadow.tscn\\n", FileAccess.get_file_as_string("res://levels/meadow.tscn"))'),
]
write(sys.argv[2], steps)
