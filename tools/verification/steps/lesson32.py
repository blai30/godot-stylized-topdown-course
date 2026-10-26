# Lesson 32: scatter grass from the tiles. A flower density on the tile, a tool node whose Scatter button fills a
# MultiMeshInstance3D for each kind of clump and flower in each block of the world, and the field in the running game.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, save_code, build, game_steps, play, quick_load,
                   resource_menu, press_delete_in_scene_dock, show_row, INSPECTOR)
from lesson32_pieces import GROUND_TILE, GROUND_TILE_SET, GROUND_MAP, GRASS_SCATTER

TILE = 'res://src/Ground/GroundTile.cs'
TILE_SET = 'res://src/Ground/GroundTileSet.cs'
MAP = 'res://src/Ground/GroundMap.cs'
SCATTER = 'res://src/Ground/GrassScatter.cs'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [GROUND_TILE, GROUND_TILE_SET, GROUND_MAP, GRASS_SCATTER]

FIELD = '''
var scatter := editor.get_edited_scene_root().get_node("Grass")
var clumps := 0
var flowers := 0
var meshes := 0
var checksum := 0.0
for child in scatter.get_children():
	if child is MultiMeshInstance3D:
		meshes += 1
		var multimesh: MultiMesh = child.multimesh
		if str(child.name).begins_with("flower"):
			flowers += multimesh.instance_count
		else:
			clumps += multimesh.instance_count
		for i in multimesh.instance_count:
			checksum += multimesh.get_instance_transform(i).origin.x * 1.7 + multimesh.get_instance_transform(i).origin.z * 0.3
print("[probe] {tag} meshes ", meshes, " clumps ", clumps, " flowers ", flowers, " checksum ", snappedf(checksum, 0.0001))
'''

PRESS_SCATTER = eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for button in plugin._collect(dock, "Button", ""):
	if str(button.text) == "Scatter":
		editor.get_inspector().ensure_control_visible(button)
		button.pressed.emit()
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		return ""
return "no Scatter button"
''')


def hour(time, name, wheel=0):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l32_{name}', 'frames': 10}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': -wheel})
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l32.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    {'op': 'eval', 'code': '''
var info := ["draw calls ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME), " primitives ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME), " fps ", Engine.get_frames_per_second()]
print("[game] ", "".join(info.map(str)))
'''},
    *hour(0.5, 'noon'), *hour(0.5, 'mid', 6), *hour(0.5, 'close', 10), *hour(0.8, 'dusk', 6), *hour(0.0, 'night', 6),
    {'op': 'eval', 'code': '''
var info := ["draw calls ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME), " primitives ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME), " fps ", Engine.get_frames_per_second()]
print("[game] close ", "".join(info.map(str)))
'''},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code(TILE, GROUND_TILE),
    save_code(TILE_SET, GROUND_TILE_SET),
    save_code(MAP, GROUND_MAP),
    save_code(SCATTER, GRASS_SCATTER),
    *build('l32_built'),
    # The meadow: the preview goes, and the grass node comes.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'GroundTiles'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    # The grass tile's flower density: the Tiles row opens the set, the array its tiles, and the first tile its fields.
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "Tiles")
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
for button in plugin._collect(picker, "Button", ""):
	print("[probe] tiles button '", button.text, "' tooltip '", button.tooltip_text, "'")
	if str(button.text) != "":
		button.pressed.emit()
		break
for attempt in 20:
	await plugin.get_tree().process_frame
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
var toggle: Button = plugin._collect(rows[0], "Button", "")[0]
toggle.button_pressed = true
toggle.toggled.emit(true)
toggle.pressed.emit()
for attempt in 20:
	await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "indices/0")
if row == null:
	return "no first tile row"
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
for button in plugin._collect(picker, "Button", ""):
	if str(button.text).begins_with("GroundTile"):
		button.pressed.emit()
		for attempt in 30:
			await plugin.get_tree().process_frame
		return ""
return "no tile button"
'''),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    inspector_set('FlowerDensity', '0.25'),
    {'op': 'wait', 'frames': 20},
    show_row('FlowerDensity'),
    {'op': 'capture', 'name': 'l32_flower_density', 'frames': 20},
    resource_menu('Tiles', 'Save'),
    {'op': 'wait', 'frames': 40},
    eval_('''
var set = load("res://art/ground/ground_tile_set.tres")
var out := []
for tile in set.get("Tiles"):
	out.append([tile.get("DisplayName"), snappedf(tile.get("GrassDensity"), 0.001), snappedf(tile.get("FlowerDensity"), 0.001)])
print("[probe] tile densities ", out)
'''),
    {'op': 'select', 'path': 'GrassPreview'},
    {'op': 'wait', 'frames': 20},
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l32_delete_preview', 'frames': 10},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		window.get_ok_button().pressed.emit()
		return ""
return "no delete confirmation"
'''),
    {'op': 'wait', 'frames': 30},
    eval_('print("[probe] meadow children ", editor.get_edited_scene_root().get_children().map(func(n): return n.name))'),
    *add_node('Node3D', 'Grass'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'GrassScatter.cs'),
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'Grass'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'Ground', 'type': 'Button', 'text': 'Assign...'}},
    {'op': 'wait', 'frames': 40},
    {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': 'GroundTiles'},
    {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
    {'op': 'wait', 'frames': 30},
    *quick_load('Models', 'grass_preview.tscn'),
    {'op': 'wait', 'frames': 30},
    show_row('Models'),
    {'op': 'capture', 'name': 'l32_grass_node', 'frames': 20},
    PRESS_SCATTER,
    {'op': 'sleep', 'seconds': 2},
    eval_(FIELD.replace('{tag}', 'first scatter')),
    {'op': 'capture', 'name': 'l32_scattered', 'frames': 20},
    PRESS_SCATTER,
    {'op': 'sleep', 'seconds': 2},
    eval_(FIELD.replace('{tag}', 'second scatter')),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    {'op': 'capture', 'name': 'l32_saved', 'frames': 20},
    *play(game, 70),
]
write(sys.argv[2], steps)
