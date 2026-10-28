# Lesson 50, in Godot: generating ground into the GridMap. The profile learns a size, a water level, and a land tile; a
# WorldGenerator node paints the ground from the terrain noise, fills water too narrow for the bank, and presses Update shore and
# Scatter; a level made from the meadow is generated, and the result is checked for repeatability, the spawn, and the edge.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, click_tab, save_code, build, add_node, inspector_set,
                   resource_menu, open_resource, press_delete_in_scene_dock, INSPECTOR)
from lesson50_pieces import TILE_SET, BANK_MAP, PROFILE, GENERATOR, PIECES

MEADOW = 'res://levels/meadow.tscn'
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


def assign_node(property, node, capture=None):
    # The property's Assign... button, the node picked in the Select a Node dialog, and OK.
    steps = [
        {'op': 'press', 'find': {**INSPECTOR, 'property': property, 'type': 'Button', 'text': 'Assign...'}},
        {'op': 'wait', 'frames': 40},
        {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': node},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Select a Node'})
    steps += [
        {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
        {'op': 'wait', 'frames': 30},
    ]
    return steps


def select_all(paths):
    return eval_(f'''
var root := editor.get_edited_scene_root()
editor.get_selection().clear()
for path in {paths!r}:
	editor.get_selection().add_node(root.get_node(path))
''')


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Generated/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size, time=0.5):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Generated/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'l50_{name}', 'frames': 10}]


def run_level(prefix, shots):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *[step for shot in shots for step in look(*shot)],
        {'op': 'quit'}])
    steps = play(game, 45 + 12 * len(shots))
    # The level is run as Run Current Scene does; the main scene is still the meadow.
    for step in steps:
        if step.get('code') == 'editor.play_main_scene()':
            step['code'] = 'editor.play_current_scene()'
    return steps


def cells_of(item):
    return f'''var ground := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
ground.get_used_cells_by_item({item}).size()'''


CHECK = '''
var root := editor.get_edited_scene_root()
var ground := root.get_node("GroundTiles") as GridMap
var bank := root.get_node("Bank") as GridMap
var generator := root.get_node("WorldGenerator")
var profile: Resource = generator.get("Profile")
var snapshot := func() -> Dictionary:
	var out := {}
	for cell in ground.get_used_cells():
		out[cell] = ground.get_cell_item(cell)
	return out
var first: Dictionary = snapshot.call()
var counts := {}
for cell in first:
	counts[first[cell]] = counts.get(first[cell], 0) + 1
print("[probe] cells ", first.size(), " by item ", counts, " bank pieces ", bank.get_used_cells().size())
# The edge and the middle are land.
var edge_water := 0
var spawn_water := 0
for cell in first:
	var distance := mini(mini(cell.x + 48, 47 - cell.x), mini(cell.z + 48, 47 - cell.z))
	if distance < 4 and first[cell] == 3:
		edge_water += 1
	if Vector2(cell.x, cell.z).length() < 6 and first[cell] == 3:
		spawn_water += 1
print("[probe] water within 4 cells of the edge ", edge_water, " within 6 cells of the middle ", spawn_water)
# No water narrower than three cells.
var narrow := 0
for cell in first:
	if first[cell] != 3:
		continue
	var run_x := 1
	var next: Vector3i = cell + Vector3i.RIGHT
	while first.get(next, 0) == 3:
		run_x += 1
		next += Vector3i.RIGHT
	next = cell - Vector3i.RIGHT
	while first.get(next, 0) == 3:
		run_x += 1
		next -= Vector3i.RIGHT
	var run_z := 1
	next = cell + Vector3i.BACK
	while first.get(next, 0) == 3:
		run_z += 1
		next += Vector3i.BACK
	next = cell - Vector3i.BACK
	while first.get(next, 0) == 3:
		run_z += 1
		next -= Vector3i.BACK
	if mini(run_x, run_z) < 3:
		narrow += 1
print("[probe] water cells in water narrower than 3 cells ", narrow)
var water := root.get_node("Water") as Node3D
print("[probe] water plane scale ", water.scale, " plane ", (water.mesh as PlaneMesh).size)
# Generate again: nothing changes.
generator.call("Generate")
var again: Dictionary = snapshot.call()
print("[probe] second Generate identical ", again == first)
# Another seed gives another level, and the first seed gives the first level back.
profile.set("Seed", 16)
generator.call("Generate")
var other: Dictionary = snapshot.call()
var differing := 0
for cell in other:
	if other[cell] != first.get(cell, -1):
		differing += 1
var other_counts := {}
for cell in other:
	other_counts[other[cell]] = other_counts.get(other[cell], 0) + 1
print("[probe] seed 16 differs in ", differing, " cells, by item ", other_counts)
profile.set("Seed", 15)
generator.call("Generate")
print("[probe] seed 15 again identical ", snapshot.call() == first)
'''

steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code('res://src/Ground/GroundTileSet.cs', TILE_SET),
    save_code('res://src/Ground/BankMap.cs', BANK_MAP),
    save_code('res://src/Generation/GenerationProfile.cs', PROFILE),
    save_code('res://src/Generation/WorldGenerator.cs', GENERATOR),
    *build('l50_built'),
    eval_('EditorInterface.edit_resource(load("res://world/generation/generation_profile.tres"))'),
    {'op': 'wait', 'frames': 40},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l50_profile'},
    # The level: the meadow, saved as a new scene and cleared of what was placed by hand.
    click_tab('Scene'),
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'menu', 'path': ['Scene', 'Save Scene As...']},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://levels"
		window.current_file = "generated.tscn"
		return ""
return "no Save Scene As dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l50_save_as', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 60},
    eval_('''
var root := editor.get_edited_scene_root()
root.name = "Generated"
print("[probe] scene ", root.scene_file_path)
'''),
    {'op': 'wait', 'frames': 20},
    # Delete what was placed by hand: the rocks, the dirt patches, and the trees.
    select_all(['Rocks', 'Patches']),
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'type': 'Button', 'text': 'Delete'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var root := editor.get_edited_scene_root()
var paths := []
for child in root.get_node("Trees").get_children():
	paths.append(root.get_path_to(child))
editor.get_selection().clear()
for path in paths:
	editor.get_selection().add_node(root.get_node(path))
'''),
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'type': 'Button', 'text': 'Delete'}},
    {'op': 'wait', 'frames': 30},
    # The floor under the player, as wide as the level.
    {'op': 'select', 'path': 'Ground/StaticBody3D/CollisionShape3D'},
    resource_menu('shape', 'BoxShape3D'),
    open_resource('shape', 'size'),
    inspector_set('size', 'Vector3(52, 1, 52)'),
    inspector_set('position', 'Vector3(0, -0.5, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l50_floor'},
    {'op': 'select', 'path': 'Ground'},
    unfold_inspector(),
    open_resource('mesh', 'size'),
    inspector_set('size', 'Vector2(52, 52)'),
    # The generator.
    *add_node('Node', 'WorldGenerator'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'WorldGenerator.cs'),
    {'op': 'wait', 'frames': 60},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    *quick_load('Profile', 'generation_profile.tres'),
    {'op': 'wait', 'frames': 20},
    *assign_node('Ground', 'GroundTiles'),
    *assign_node('Bank', 'Bank'),
    *assign_node('Grass', 'Grass'),
    *assign_node('Water', 'Water', 'l50_select_water'),
    {'op': 'capture', 'name': 'l50_generator'},
    eval_('''
var generator := editor.get_edited_scene_root().get_node("WorldGenerator")
print("[probe] generator ", generator.get_script().resource_path, " profile ", generator.get("Profile").resource_path, " ground ", generator.get("Ground"), " bank ", generator.get("Bank"), " grass ", generator.get("Grass"), " water ", generator.get("Water"))
'''),
    eval_(PRESS_BUTTON.format(text='Generate')),
    {'op': 'sleep', 'seconds': 3},
    {'op': 'capture', 'name': 'l50_generated'},
    eval_(CHECK),
    {'op': 'select', 'path': 'WorldGenerator'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    *run_level('l50', [('wide', 0.0, 0.0, 60.0), ('north_west', -12.0, -12.0, 20.0), ('lake', 10.0, 12.0, 20.0), ('shore', 0.0, 0.0, 11.0),
                       ('dusk', 0.0, 0.0, 30.0, 0.78)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
