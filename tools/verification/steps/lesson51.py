# Lesson 51, in Godot: scattering props by rules. A PropRule resource says what a prop is, where it may stand, and how far it keeps
# from its neighbors and from water; the profile holds an oak rule and a pine rule; the generator grows the trees from them, and the
# result is checked for spacing, the shore, the clearing, repeatability, and where the forest noise puts them.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, click_tab, save_code, build, inspector_set, resource_menu,
                   save_resource, INSPECTOR)
from lesson51_pieces import RULE, PROFILE, GENERATOR, PIECES

PROFILE_RES = 'res://world/generation/generation_profile.tres'
GENERATED = 'res://levels/generated.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Generated/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

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

# The rules: name, scene, weight.
RULES = [('oak', 'tree_oak.tscn', 3.0), ('pine', 'tree_pine.tscn', 2.0)]


def assign_node(property, node, capture=None):
    steps = [
        {'op': 'press', 'find': {**INSPECTOR, 'property': property, 'type': 'Button', 'text': 'Assign...'}},
        {'op': 'wait', 'frames': 40},
        {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': node},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Select a Node'})
    steps += [{'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}}, {'op': 'wait', 'frames': 30}]
    return steps


def open_element(row):
    # An element's name button opens the rule in place, below its row; the rows of the newest rule come last.
    return eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{row}")
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
for button in plugin._collect(picker, "Button", ""):
	if str(button.text).begins_with("PropRule"):
		button.pressed.emit()
		for attempt in 30:
			await plugin.get_tree().process_frame
		return ""
return "no PropRule button in {row}"
''')


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Generated/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size, time=0.5):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Generated/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'l51_{name}', 'frames': 10}]


def run_level(prefix, shots):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *[step for shot in shots for step in look(*shot)],
        {'op': 'quit'}])
    steps = play(game, 45 + 12 * len(shots))
    for step in steps:
        if step.get('code') == 'editor.play_main_scene()':
            step['code'] = 'editor.play_current_scene()'
    return steps


CHECK = '''
var root := editor.get_edited_scene_root()
var ground := root.get_node("GroundTiles") as GridMap
var props := root.get_node("Trees")
var generator := root.get_node("WorldGenerator")
var profile: Resource = generator.get("Profile")
var rules: Array = profile.get("Rules")
print("[probe] rules ", rules.size(), " ", rules.map(func(r): return "%s weight %s from %s to %s spacing %s shore %s" % [r.get("Scene").resource_path.get_file(), r.get("Weight"), r.get("StartsAt"), r.get("FullAt"), r.get("Spacing"), r.get("ShoreDistance")]))
var snapshot := func() -> Array:
	var out := []
	for tree in props.get_children():
		out.append([tree.name, tree.scene_file_path.get_file(), snappedf(tree.position.x, 0.001), snappedf(tree.position.z, 0.001), snappedf(tree.rotation.y, 0.001), snappedf(tree.scale.x, 0.001)])
	return out
var first: Array = snapshot.call()
var oaks := 0
var pines := 0
for tree in first:
	if tree[1] == "tree_oak.tscn":
		oaks += 1
	else:
		pines += 1
print("[probe] props ", first.size(), " oaks ", oaks, " pines ", pines, " owned ", props.get_children().all(func(t): return t.owner == root))
# Spacing, shore, clearing, edge.
var closest := 1e9
var nearest_water := 1e9
var in_water := 0
var in_clearing := 0
var near_edge := 0
var water_cells := ground.get_used_cells_by_item(3)
for i in first.size():
	var a := Vector2(first[i][2], first[i][3])
	for j in range(i + 1, first.size()):
		closest = minf(closest, a.distance_to(Vector2(first[j][2], first[j][3])))
	var cell := Vector3i(floori(a.x / 0.5), 0, floori(a.y / 0.5))
	if ground.get_cell_item(cell) == 3:
		in_water += 1
	if Vector2(cell.x, cell.z).length() < 6:
		in_clearing += 1
	if mini(mini(cell.x + 48, 47 - cell.x), mini(cell.z + 48, 47 - cell.z)) < 4:
		near_edge += 1
	for water in water_cells:
		var middle := (Vector2(water.x, water.z) + Vector2(0.5, 0.5)) * 0.5
		nearest_water = minf(nearest_water, a.distance_to(middle))
print("[probe] closest pair %.2f m, nearest water %.2f m, in water %d, in the clearing %d, near the edge %d" % [closest, nearest_water, in_water, in_clearing, near_edge])
# The forest noise: trees stand where it is high.
var forest_at_trees := 0.0
for tree in first:
	forest_at_trees += profile.call("ForestAt", Vector2(tree[2], tree[3]))
forest_at_trees /= first.size()
var all_forest := 0.0
var count := 0
for x in range(-24, 24):
	for z in range(-24, 24):
		all_forest += profile.call("ForestAt", Vector2(x + 0.5, z + 0.5))
		count += 1
print("[probe] mean forest noise at the trees %.2f, over the level %.2f" % [forest_at_trees, all_forest / count])
# Again: the same trees. Another seed: other trees. Back: the first.
generator.call("Generate")
print("[probe] second Generate identical ", snapshot.call() == first)
profile.set("Seed", 16)
generator.call("Generate")
var other: Array = snapshot.call()
print("[probe] seed 16 gives ", other.size(), " props, same as seed 15 ", other == first)
profile.set("Seed", 15)
generator.call("Generate")
print("[probe] seed 15 again identical ", snapshot.call() == first)
'''

steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code('res://src/Generation/PropRule.cs', RULE),
    save_code('res://src/Generation/GenerationProfile.cs', PROFILE),
    save_code('res://src/Generation/WorldGenerator.cs', GENERATOR),
    *build('l51_built'),
    eval_('''
var names := []
for entry in ProjectSettings.get_global_class_list():
	names.append(entry["class"])
print("[probe] global classes ", names)
'''),
    # The rules, in the profile's Rules array.
    eval_(f'EditorInterface.edit_resource(load("{PROFILE_RES}"))'),
    {'op': 'wait', 'frames': 40},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    eval_('''
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
print("[probe] array rows ", rows.size())
var toggle: Button = plugin._collect(rows[0], "Button", "")[0]
toggle.button_pressed = true
toggle.toggled.emit(true)
toggle.pressed.emit()
await plugin.get_tree().process_frame
await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l51_rules_empty'},
    eval_('''
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
var slider: EditorSpinSlider = plugin._collect(rows[0], "EditorSpinSlider", "")[0]
slider.value = 2
slider.value_changed.emit(2)
for attempt in 20:
	await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
]
for index, (name, scene, weight) in enumerate(RULES):
    row = f'indices/{index}'
    steps += [
        resource_menu(row, 'PropRule'),
        {'op': 'wait', 'frames': 20},
        open_element(row),
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        *quick_load('Scene', scene),
        {'op': 'wait', 'frames': 20},
        inspector_set('Weight', str(weight)),
        {'op': 'wait', 'frames': 20},
    ]
steps += [
    {'op': 'capture', 'name': 'l51_rules'},
    *save_resource(),
    eval_(f'''
var profile: Resource = load("{PROFILE_RES}")
var out := []
for rule in profile.get("Rules"):
	out.append("%s weight %s from %s to %s spacing %s shore %s" % [rule.get("Scene").resource_path.get_file(), rule.get("Weight"), rule.get("StartsAt"), rule.get("FullAt"), rule.get("Spacing"), rule.get("ShoreDistance")])
print("[probe] saved rules ", out)
'''),
    # The level: the generator is told where the trees go, and generates.
    click_tab('Scene'),
    {'op': 'open', 'path': GENERATED},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'WorldGenerator'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    *assign_node('Props', 'Trees', 'l51_select_trees'),
    {'op': 'capture', 'name': 'l51_generator'},
    eval_(PRESS_BUTTON.format(text='Generate')),
    {'op': 'sleep', 'seconds': 4},
    {'op': 'capture', 'name': 'l51_generated'},
    eval_(CHECK),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    *run_level('l51', [('wide', 0.0, 0.0, 60.0), ('grove', -10.0, -4.0, 20.0), ('shore', 8.0, 10.0, 11.0), ('start', 0.0, 0.0, 11.0), ('dusk', -6.0, -6.0, 30.0, 0.78)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
