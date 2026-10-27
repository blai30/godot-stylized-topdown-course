# Lesson 45, in Godot: the water's depth and color. A Water ground tile that is only the lake bed, the pond painted with it, and
# a water surface, a plane with a shader that reads the depth under it: a flat color, the thickness as gray, then the bed faded by
# the thickness with the red absorbed first.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, resource_menu, open_resource, new_resource,
                   inspector_set, click_tab, save_code, build, add_node, type_shader, instantiate_under, press_delete_in_scene_dock, open_bottom_panel)
from shader_ui import new_shader_file
from lesson45_pieces import GROUND_TILE, LAKE_BED, WATER_FLAT, WATER_THICKNESS, WATER, PIECES

TILE = 'res://src/Ground/GroundTile.cs'
LAKE_BED_SHADER = 'res://art/shaders/lake_bed.gdshader'
WATER_SHADER = 'res://art/shaders/water.gdshader'
MEADOW = 'res://levels/meadow.tscn'
TILES_SCENE = 'res://art/ground/ground_tiles.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
STOP = os.environ.get('LESSON45_STOP', '')
POND = [[x, z] for x in range(-2, 1) for z in range(-4, -1)]
out_dir = os.path.dirname(sys.argv[2])

SAVE_DIALOG = '''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "{folder}"
		window.current_file = "{name}"
		return ""
return "no Save dialog"
'''
PRESS_SAVE = '''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
return "no Save dialog"
'''


def save_to(folder, name, capture=None):
    steps = [{'op': 'wait', 'frames': 30}, eval_(SAVE_DIALOG.format(folder=folder, name=name)), {'op': 'wait', 'frames': 20}]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'class:EditorFileDialog'})
    return steps + [eval_(PRESS_SAVE), {'op': 'wait', 'frames': 40}]


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def look(prefix, name, x, z, size, time=0.5):
    # The camera follows the player, so the hidden player stands on the spot.
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'{prefix}_{name}', 'frames': 10}]


def run_game(prefix, shots):
    # One run of the game: the pond at the shots' distances and hours.
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *[step for shot in shots for step in look(prefix, *shot)],
        {'op': 'quit'}])
    return play(game, 45 + 12 * len(shots))


def stage(code, prefix, shots):
    return [eval_(f'EditorInterface.edit_resource(load("{WATER_SHADER}"))'), open_bottom_panel('Shader Editor'), {'op': 'wait', 'frames': 40},
            *type_shader(code, WATER_SHADER), {'op': 'capture', 'name': f'{prefix}_editor', 'frames': 20}, *run_game(prefix, shots)]


steps = [
    {'op': 'sleep', 'seconds': 3},
    # GroundTile learns what water is.
    save_code(TILE, GROUND_TILE),
    *build('l45_built'),
    # The lake bed's shader.
    *new_shader_file('New Shader...', LAKE_BED_SHADER, 'l45_create_lake_bed'),
    *type_shader(LAKE_BED, LAKE_BED_SHADER),
    {'op': 'capture', 'name': 'l45_lake_bed_shader', 'frames': 20},
    # The tile: a flat quad 75 centimeters under the ground, with the lake bed's material.
    click_tab('Scene'),
    {'op': 'open', 'path': TILES_SCENE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    *add_node('MeshInstance3D', 'Water'),
    *new_resource('mesh', 'PlaneMesh', nth=-1),
    open_resource('mesh', 'size'),
    inspector_set('size', 'Vector2(0.5, 0.5)'),
    inspector_set('center_offset', 'Vector3(0, -0.75, 0)'),
    *new_resource('material', 'ShaderMaterial', nth=-1),
    open_resource('material', 'shader'),
    *quick_load('shader', 'lake_bed.gdshader'),
    unfold_inspector(),
    *quick_load('shader_parameter/albedo_texture', 'dirt_albedo.png'),
    *quick_load('shader_parameter/edge_noise', 'edge_noise.tres'),
    {'op': 'wait', 'frames': 20},
    {'op': 'select', 'path': 'Water'},
    inspector_set('position', 'Vector3(3, 0, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l45_water_tile'},
    eval_('''
var tile := editor.get_edited_scene_root().get_node("Water") as MeshInstance3D
var mesh := tile.mesh as PlaneMesh
var material := mesh.material as ShaderMaterial
print("[probe] water tile ", mesh.size, " ", mesh.center_offset, " ", tile.position, " ", material.shader.resource_path, " ", material.get_shader_parameter("albedo_texture").resource_path)
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    {'op': 'menu', 'path': ['Scene', 'Export As...', 'MeshLibrary...']},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is FileDialog:
		window.current_dir = "res://art/ground"
		window.current_file = "ground_tiles.meshlib"
		window.get_ok_button().pressed.emit()
		return ""
return "no Export Mesh Library dialog"
'''),
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog and not window is FileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
var library := load("res://art/ground/ground_tiles.meshlib") as MeshLibrary
var out := []
for id in library.get_item_list():
	out.append("%d %s" % [id, library.get_item_name(id)])
print("[probe] mesh library ", out)
if library.get_item_list().size() != 4:
	return "the library does not hold four tiles"
'''),
    # The tile as a resource in the set: Water, item 3, the lowest layer, no grass, and IsWater on.
    eval_('''
var set = load("res://art/ground/ground_tile_set.tres")
var tile = load("res://src/Ground/GroundTile.cs").new()
tile.set("DisplayName", "Water")
tile.set("Item", 3)
tile.set("Layer", 0)
tile.set("IsWater", true)
var tiles = set.get("Tiles")
tiles.append(tile)
set.set("Tiles", tiles)
ResourceSaver.save(set, "res://art/ground/ground_tile_set.tres")
EditorInterface.edit_resource(set)
var names := []
for entry in load("res://art/ground/ground_tile_set.tres").get("Tiles"):
	names.append("%s %s water %s" % [entry.get("DisplayName"), entry.get("Item"), entry.get("IsWater")])
print("[probe] tile set ", names)
'''),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l45_tile_set'},
    # The pond: its nine cells painted with the Water tile, and the stand-in bed gone.
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    click_tab('Scene'),
    {'op': 'select', 'path': 'PondBed'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l45_select_bed'},
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l45_delete_bed'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog and not window is FileDialog:
		for label in plugin._collect(window, "Label", ""):
			print("[probe] asks: ", label.text)
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 20},
    eval_(f'''
var ground: GridMap = editor.get_edited_scene_root().get_node("GroundTiles")
print("[probe] items ", ground.mesh_library.get_item_list())
for cell in {POND!r}:
	ground.set_cell_item(Vector3i(cell[0], 0, cell[1]), 3)
print("[probe] water cells ", ground.get_used_cells_by_item(3).size(), " bed removed ", editor.get_edited_scene_root().get_node_or_null("PondBed") == null)
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
]
if STOP == 'tile':
    steps += [{'op': 'quit'}]
    write(sys.argv[2], steps)
    raise SystemExit

steps += [
    # The water scene: a MeshInstance3D with a plane, the shader, and no shadow.
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'Other Node'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'set_text', 'find': {'window': 'Create New Node', 'type': 'LineEdit', 'nth': 0}, 'text': 'MeshInstance3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'window': 'Create New Node', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 30},
    eval_('editor.get_edited_scene_root().name = "Water"'),
    {'op': 'select', 'path': '.'},
    *new_resource('mesh', 'PlaneMesh', nth=-1),
    open_resource('mesh', 'size'),
    inspector_set('size', 'Vector2(19.6, 19.6)'),
    {'op': 'select', 'path': '.'},
    inspector_set('cast_shadow', '0'),
    {'op': 'wait', 'frames': 20},
    # The water shader, first as a flat color.
    *new_shader_file('New Shader...', WATER_SHADER, 'l45_create_water'),
    *type_shader(WATER_FLAT, WATER_SHADER),
    click_tab('Scene'),
    {'op': 'select', 'path': '.'},
    *new_resource('material', 'ShaderMaterial', nth=-1),
    open_resource('material', 'shader'),
    *quick_load('shader', 'water.gdshader'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l45_water_material'},
    resource_menu('material', 'Save As...'),
    *save_to('res://art/water', 'water.tres', 'l45_save_water_material'),
    SAVE_SCENE,
    *save_to('res://art/water', 'water.tscn', 'l45_save_water_scene'),
    eval_('''
var root := editor.get_edited_scene_root()
var mesh := root.mesh as PlaneMesh
print("[probe] water scene ", root.name, " ", mesh.size, " shadow ", root.cast_shadow, " material ", mesh.material.resource_path, " shader ", mesh.material.shader.resource_path)
'''),
    # The water in the meadow, 35 centimeters under the ground.
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *instantiate_under('.', 'water.tscn'),
    {'op': 'select', 'path': 'Water'},
    unfold_inspector(),
    inspector_set('position', 'Vector3(0, -0.35, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l45_water_in_meadow'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # Step 1, a flat color. Step 2, the thickness as gray. Step 3, the bed under the water.
    *run_game('l45_flat', [('pond', -0.25, -1.25, 3.2)]),
    *stage(WATER_THICKNESS, 'l45_thickness', [('pond', -0.25, -1.25, 3.2)]),
    *stage(WATER, 'l45_color', [('pond', -0.25, -1.25, 3.2), ('dusk', -0.25, -1.25, 3.2, 0.78), ('night', -0.25, -1.25, 3.2, 0.0), ('wide', -0.25, -1.25, 6.0)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
