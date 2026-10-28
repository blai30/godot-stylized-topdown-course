# Lesson 54, in Godot: bushes. A scene from the oak's own model, with the trunk hidden and the crown squashed to ground level, a small
# collision body, and the wind script; three bushes planted in the meadow; and a PropRule so the generated level grows them in its groves.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, instantiate_under, quick_load, new_resource, open_resource,
                   resource_menu, open_in_file_dialog, game_steps, play, view, click_tab, save_resource, make_folder)

BUSH_SCENE = 'res://art/nature/bush/bush.tscn'
MEADOW = 'res://levels/meadow.tscn'
GENERATED = 'res://levels/generated.tscn'
PROFILE_RES = 'res://world/generation/generation_profile.tres'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

# The crown is the oak's, squashed to 0.5 by 0.35 by 0.5, and lowered so its underside is at the ground: the oak's leaves start 1.45 m up.
CROWN_SCALE = 'Vector3(0.5, 0.35, 0.5)'
CROWN_POSITION = 'Vector3(0, -0.51, 0)'
# Name, position, yaw in degrees, scale.
BUSHES = [('Bush', (-3.0, 0.0, 6.0), 0, 1.0), ('Bush2', (-1.0, 0.0, 7.0), 120, 0.8), ('Bush3', (0.5, 0.0, 6.2), 250, 0.9)]

PRESS_BUTTON = '''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for button in plugin._collect(dock, "Button", ""):
	if str(button.text) == "{text}":
		editor.get_inspector().ensure_control_visible(button)
		button.pressed.emit()
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		return ""
return "no {text} button"
'''


def place(name, position, yaw, scale):
    return [
        {'op': 'select', 'path': f'Bushes/{name}'},
        unfold_inspector(),
        {'op': 'wait', 'frames': 10},
        inspector_set('position', 'Vector3(%s, %s, %s)' % position),
        inspector_set('rotation', f'Vector3(0, deg_to_rad({yaw}), 0)'),
        inspector_set('scale', f'Vector3({scale}, {scale}, {scale})'),
        {'op': 'wait', 'frames': 10},
    ]


def hour(root, time, name, x, z, size):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("{root}/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'tree.root.get_node("{root}/WorldEnvironment/Day").set("TimeOfDay", {time})'},
            {'op': 'eval', 'code': f'tree.root.get_node("{root}/CameraRig").get("Camera").size = {size}'},
            {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'l54_{name}', 'frames': 10}]


def run_scene(prefix, root, shots, extra=()):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'tree.root.get_node("{root}/WorldEnvironment/Day").set("Running", false)'},
        *[step for shot in shots for step in hour(root, *shot)], *extra,
        {'op': 'quit'}])
    steps = play(game, 60 + 12 * len(shots))
    for step in steps:
        if step.get('code') == 'editor.play_main_scene()':
            step['code'] = 'editor.play_current_scene()'
    return steps


# Walk into a bush: it should stop the player, as a tree trunk does.
WALK = [
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(-1.0, 0.05, 10.0)\nawait tree.process_frame\nInput.action_press("move_forward")'},
    {'op': 'sleep', 'seconds': 2.0},
    {'op': 'eval', 'code': 'Input.action_release("move_forward")\nvar player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nprint("[game] WALK stopped at z ", snappedf(player.global_position.z, 0.01), " (bush at z 7.0, collision radius 0.7)")'},
]

CHECK = '''
var root := editor.get_edited_scene_root()
var ground := root.get_node("GroundTiles") as GridMap
var props := root.get_node("Trees")
var generator := root.get_node("WorldGenerator")
var profile: Resource = generator.get("Profile")
var rules: Array = profile.get("Rules")
print("[probe] rules ", rules.size(), " ", rules.map(func(r): return "%s weight %s spacing %s shore %s" % [r.get("Scene").resource_path.get_file(), r.get("Weight"), r.get("Spacing"), r.get("ShoreDistance")]))
var snapshot := func() -> Array:
	var out := []
	for prop in props.get_children():
		out.append([prop.name, prop.scene_file_path.get_file(), snappedf(prop.position.x, 0.001), snappedf(prop.position.z, 0.001), snappedf(prop.rotation.y, 0.001), snappedf(prop.scale.x, 0.001)])
	return out
var first: Array = snapshot.call()
var counts := {}
for prop in first:
	counts[prop[1]] = counts.get(prop[1], 0) + 1
print("[probe] props ", first.size(), " by scene ", counts)
var closest := 1e9
var bush_closest := 1e9
var in_water := 0
for i in first.size():
	var a := Vector2(first[i][2], first[i][3])
	for j in range(i + 1, first.size()):
		var distance := a.distance_to(Vector2(first[j][2], first[j][3]))
		closest = minf(closest, distance)
		if first[i][1] == "bush.tscn" or first[j][1] == "bush.tscn":
			bush_closest = minf(bush_closest, distance)
	if ground.get_cell_item(Vector3i(floori(a.x / 0.5), 0, floori(a.y / 0.5))) == 3:
		in_water += 1
print("[probe] closest pair %.2f m, closest pair with a bush %.2f m, in water %d" % [closest, bush_closest, in_water])
generator.call("Generate")
print("[probe] second Generate identical ", snapshot.call() == first)
'''

steps = [
    {'op': 'sleep', 'seconds': 5},
    *make_folder('art/nature', 'bush'),
    # The scene: a new inherited scene from the oak's model.
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'nature', 'tree_oak'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "tree_oak.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no tree_oak.glb in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l54_inherit_dialog', 'window': 'Open Base Scene'},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    {'op': 'main_screen', 'name': '3D'},
    click_tab('Scene'),
    eval_('print("[probe] inherited scene root ", editor.get_edited_scene_root().name, " children ", editor.get_edited_scene_root().get_children().map(func(n): return n.name))'),
    {'op': 'click', 'find': SCENE_TREE, 'item': 'tree_oak2', 'double': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible:
		for edit in plugin._collect(window, "LineEdit", ""):
			if edit.text == "tree_oak2":
				edit.text = "Bush"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no rename field"
'''),
    {'op': 'wait', 'frames': 20},
    # No trunk: the bush is all crown.
    {'op': 'select', 'path': 'tree_oak'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    inspector_set('visible', 'false'),
    {'op': 'wait', 'frames': 20},
    {'op': 'select', 'path': 'leaves'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('material_override', 'leaves.tres'),
    inspector_set('scale', CROWN_SCALE),
    inspector_set('position', CROWN_POSITION),
    {'op': 'wait', 'frames': 20},
    *view('leaves', dx=0, dy=0, wheel=0),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l54_crown'},
    # A body the player cannot walk through, and the wind script.
    {'op': 'select', 'path': '.'},
    *add_node('StaticBody3D', 'Body'),
    *add_node('CollisionShape3D', 'Shape', 'Body'),
    {'op': 'select', 'path': 'Body/Shape'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *new_resource('shape', 'CylinderShape3D', nth=1),
    open_resource('shape', 'radius'),
    inspector_set('radius', '0.7'),
    inspector_set('height', '1.0'),
    inspector_set('position', 'Vector3(0, 0.5, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'WindPhase.cs'),
    {'op': 'wait', 'frames': 40},
    *view('leaves', dx=0, dy=0, wheel=0),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l54_bush_scene'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/nature/bush"
		window.current_file = "bush.tscn"
		return ""
return "no Save Scene dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l54_save_scene', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 60},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path, " nodes ", editor.get_edited_scene_root().get_children().map(func(n): return n.name))'),
    # Three bushes in the meadow, under a group of their own.
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *add_node('Node3D', 'Bushes'),
]
for index in range(len(BUSHES)):
    steps += instantiate_under('Bushes', 'bush.tscn', capture='l54_select_scene' if index == 0 else None)
for name, position, yaw, scale in BUSHES:
    steps += place(name, position, yaw, scale)
steps += [
    eval_('''
var bushes := editor.get_edited_scene_root().get_node("Bushes")
print("[probe] bushes ", bushes.get_children().map(func(n): return "%s %s %s" % [n.name, n.position, n.scale.x]))
'''),
    {'op': 'capture', 'name': 'l54_meadow_editor', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    *run_scene('l54_meadow', 'Meadow', [(0.5, 'meadow', -1.0, 6.5, 9.0), (0.5, 'meadow_wide', 0.0, 2.0, 20.0), (0.78, 'meadow_dusk', -1.0, 6.5, 9.0)], WALK),
    # A rule for the generated level.
    eval_(f'EditorInterface.edit_resource(load("{PROFILE_RES}"))'),
    {'op': 'wait', 'frames': 40},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    eval_('''
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
var toggle: Button = plugin._collect(rows[0], "Button", "")[0]
toggle.button_pressed = true
toggle.toggled.emit(true)
toggle.pressed.emit()
await plugin.get_tree().process_frame
await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    eval_('''
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
var slider: EditorSpinSlider = plugin._collect(rows[0], "EditorSpinSlider", "")[0]
slider.value = 3
slider.value_changed.emit(3)
for attempt in 20:
	await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    resource_menu('indices/2', 'PropRule'),
    {'op': 'wait', 'frames': 20},
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "indices/2")
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
for button in plugin._collect(picker, "Button", ""):
	if str(button.text).begins_with("PropRule"):
		button.pressed.emit()
		for attempt in 30:
			await plugin.get_tree().process_frame
		return ""
return "no PropRule button"
'''),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('Scene', 'bush.tscn'),
    {'op': 'wait', 'frames': 20},
    inspector_set('Weight', '2.0'),
    inspector_set('Spacing', '1.5'),
    inspector_set('ShoreDistance', '1.5'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l54_rule'},
    *save_resource(),
    # Generate again, with the bush in the rules.
    click_tab('Scene'),
    {'op': 'open', 'path': GENERATED},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'WorldGenerator'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_(PRESS_BUTTON.format(text='Generate')),
    {'op': 'sleep', 'seconds': 4},
    {'op': 'capture', 'name': 'l54_generated'},
    eval_(CHECK),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    *run_scene('l54_generated', 'Generated', [(0.5, 'gen_grove', -10.0, -4.0, 20.0), (0.5, 'gen_close', -10.0, -4.0, 11.0), (0.5, 'gen_wide', 0.0, 0.0, 60.0), (0.78, 'gen_dusk', -6.0, -6.0, 30.0)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
