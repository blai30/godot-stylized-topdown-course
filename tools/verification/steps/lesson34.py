# Lesson 34: decoratives. The new meshes in the preview scene with a material, pebble and mushroom densities on the
# tiles, the scatter growing them, and dirt patches as Decal nodes that clear the grass under them.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, save_code, build, game_steps, play, quick_load,
                   resource_menu, new_resource, open_resource, show_row, press_delete_in_scene_dock, INSPECTOR)
from lesson34_pieces import GROUND_TILE, GRASS_SCATTER

TILE = 'res://src/Ground/GroundTile.cs'
SCATTER = 'res://src/Ground/GrassScatter.cs'
PREVIEW = 'res://art/nature/grass/grass_preview.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [GROUND_TILE, GRASS_SCATTER]

# The dirt patches: where each lies on the ground in meters (x, z), how wide and deep it is, and its turn in degrees.
PATCHES = [((1.9, -0.7), (2.4, 1.6), 20), ((-3.2, 1.0), (1.8, 1.4), 70), ((0.5, 5.0), (3.0, 1.9), 140)]
# The tiles to set: the index in the set, and its densities for pebbles and mushrooms.
TILES = [(0, 0.05, 0.08), (1, 0.15, 0.0), (2, 0.4, 0.0)]

COUNT = '''
var scatter := editor.get_edited_scene_root().get_node("Grass")
var counts := {}
for child in scatter.get_children():
	if child is MultiMeshInstance3D:
		var kind := str(child.name).split("_")[0]
		counts[kind] = counts.get(kind, 0) + child.multimesh.instance_count
print("[probe] {tag} ", counts)
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


def tile_densities(index, pebble, mushroom):
    return [
        eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "indices/{index}")
if row == null:
	return "no tile row {index}"
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
        inspector_set('PebbleDensity', str(pebble)),
        inspector_set('MushroomDensity', str(mushroom)),
        {'op': 'wait', 'frames': 20},
        show_row('MushroomDensity'),
        {'op': 'capture', 'name': f'l34_tile_{index}', 'frames': 10},
    ]


def hour(time, name, wheel=0, x=None):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l34_{name}', 'frames': 10}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': -wheel})
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l34.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    {'op': 'eval', 'code': '''
var info := ["draw calls ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME), " primitives ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME), " fps ", Engine.get_frames_per_second()]
print("[game] ", "".join(info.map(str)))
'''},
    *hour(0.5, 'noon'), *hour(0.5, 'mid', 6), *hour(0.5, 'close', 10), *hour(0.8, 'dusk', 6), *hour(0.0, 'night', 6),
    # Up to a mushroom and a pebble: the player stands beside the first of each, and the view is as close as it goes.
    *[step for kind, at in (('mushroom', (-2.29, -0.30)), ('pebble', (0.16, 1.53))) for step in (
        {'op': 'eval', 'code': f'(tree.root.get_node("Meadow/Player") as CharacterBody3D).global_position = Vector3({at[0] + 0.3}, 0.05, {at[1] + 0.45})'},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)'},
        {'op': 'wheel', 'steps': 12}, {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'l34_{kind}_close', 'frames': 10}, {'op': 'wheel', 'steps': -12})],
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code(TILE, GROUND_TILE),
    save_code(SCATTER, GRASS_SCATTER),
    *build('l34_built'),
    # The preview scene: the new meshes arrive from the file, and take the flower material.
    {'op': 'open', 'path': PREVIEW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    eval_('print("[probe] preview children ", editor.get_edited_scene_root().get_children().map(func(n): return n.name))'),
    {'op': 'capture', 'name': 'l34_preview_before', 'frames': 20},
]
for name in ('pebble_a', 'pebble_b', 'mushroom_a'):
    steps += [
        {'op': 'select', 'path': name},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        *quick_load('material_override', 'flower.tres'),
    ]
steps += [
    eval_('''
var root := editor.get_edited_scene_root()
for node in root.get_children():
	var material := (node as MeshInstance3D).material_override as ShaderMaterial
	print("[probe] ", node.name, " override ", material.resource_path if material else "none")
'''),
    {'op': 'select', 'path': 'mushroom_a'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l34_preview_scene'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The meadow, and the tiles' densities.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'GroundTiles'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "Tiles")
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
for button in plugin._collect(picker, "Button", ""):
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
]
for index, pebble, mushroom in TILES:
    steps += tile_densities(index, pebble, mushroom)
steps += [
    resource_menu('Tiles', 'Save'),
    {'op': 'wait', 'frames': 40},
    eval_('''
var set = load("res://art/ground/ground_tile_set.tres")
var out := []
for tile in set.get("Tiles"):
	out.append([tile.get("DisplayName"), snappedf(tile.get("GrassDensity"), 0.001), snappedf(tile.get("FlowerDensity"), 0.001), snappedf(tile.get("PebbleDensity"), 0.001), snappedf(tile.get("MushroomDensity"), 0.001)])
print("[probe] tile densities ", out)
'''),
    # Scatter, without patches first.
    {'op': 'select', 'path': 'Grass'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    PRESS_SCATTER,
    {'op': 'sleep', 'seconds': 2},
    eval_(COUNT.replace('{tag}', 'scatter with props')),
    {'op': 'capture', 'name': 'l34_props', 'frames': 20},
    # The dirt patches: a Node3D with a Decal for each.
    *add_node('Node3D', 'Patches'),
]
for number, (position, size, yaw) in enumerate(PATCHES, 1):
    name = f'Patch{number}'
    steps += [
        *add_node('Decal', name, 'Patches'),
        {'op': 'select', 'path': f'Patches/{name}'},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        inspector_set('position', f'Vector3({position[0]}, 0.0, {position[1]})'),
        inspector_set('rotation', f'Vector3(0, deg_to_rad({yaw}), 0)'),
        inspector_set('size', f'Vector3({size[0]}, 0.6, {size[1]})'),
    ]
    if number == 1:
        steps += [
            *new_resource('texture_albedo', 'GradientTexture2D'),
            open_resource('texture_albedo', 'gradient'),
            inspector_set('fill', '1'),
            inspector_set('width', '256'),
            inspector_set('height', '256'),
            inspector_set('fill_from', 'Vector2(0.5, 0.5)'),
            inspector_set('fill_to', 'Vector2(1.0, 0.5)'),
            inspector_set('gradient', '''(func():
	var gradient := Gradient.new()
	gradient.offsets = PackedFloat32Array([0.0, 0.55, 1.0])
	gradient.colors = PackedColorArray([Color("7A5638"), Color("8A6342"), Color("8A634200")])
	return gradient).call()'''),
            {'op': 'wait', 'frames': 20},
            show_row('texture_albedo'),
            {'op': 'capture', 'name': 'l34_decal_inspector', 'frames': 20},
            resource_menu('texture_albedo', 'Save As...'),
            {'op': 'wait', 'frames': 30},
            eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/ground"
		window.current_file = "dirt_patch.tres"
		return ""
return "no Save Resource dialog"
'''),
            {'op': 'capture', 'name': 'l34_save_texture', 'window': 'class:EditorFileDialog'},
            eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
            {'op': 'wait', 'frames': 40},
        ]
    else:
        steps += [*quick_load('texture_albedo', 'dirt_patch.tres')]
steps += [
    eval_('''
var patches := editor.get_edited_scene_root().get_node("Patches")
for decal in patches.get_children():
	print("[probe] ", decal.name, " ", decal.position, " size ", decal.size, " texture ", decal.texture_albedo.resource_path)
'''),
    {'op': 'select', 'path': 'Grass'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    # The scatter's Patches property.
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'Patches', 'type': 'Button', 'text': 'Assign...'}},
    {'op': 'wait', 'frames': 40},
    {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': 'Patches'},
    {'op': 'capture', 'name': 'l34_select_patches', 'window': 'Select a Node'},
    {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
    {'op': 'wait', 'frames': 30},
    show_row('Patches'),
    {'op': 'capture', 'name': 'l34_grass_patches', 'frames': 20},
    PRESS_SCATTER,
    {'op': 'sleep', 'seconds': 2},
    eval_(COUNT.replace('{tag}', 'scatter with patches')),
    {'op': 'capture', 'name': 'l34_patches', 'frames': 20},
    eval_('''
var scatter := editor.get_edited_scene_root().get_node("Grass")
for kind in ["mushroom", "pebble"]:
	var best := Vector3(1000, 0, 1000)
	for child in scatter.get_children():
		if child is MultiMeshInstance3D and str(child.name).begins_with(kind):
			for i in child.multimesh.instance_count:
				var at: Vector3 = child.multimesh.get_instance_transform(i).origin
				if at.length() < best.length():
					best = at
	print("[probe] nearest ", kind, " ", best)
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    *play(game, 70),
]
write(sys.argv[2], steps)
