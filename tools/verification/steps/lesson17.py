# Lesson 17: soft tile edges. Each tile grows to 1.5 m so it overhangs its cell, sits in its own layer (sand, dirt,
# grass), and the ground shader cuts the overhang with alpha scissor, first straight, then ragged with a noise texture
# the three materials share. The MeshLibrary is exported again and the meadow shows the result.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, quick_load, resource_menu, open_resource,
                   type_shader, open_in_file_dialog, game_steps, play)

PIECES = [
    '''shader_type spatial;

// The ground textures you painted in lessons 13 and 14.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// How many times the texture repeats per meter: 0.5 is once every 2 meters.
uniform float texture_scale = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;
// How far the tile reaches past its cell on each side, in meters.
uniform float overhang = 0.2;
// The GridMap's cell size, in meters.
uniform float cell_size = 0.5;

varying vec3 world_position;
varying vec2 tile_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	tile_position = VERTEX.xz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb;
	ROUGHNESS = roughness;
	// 0 inside the cell, rising to 1 at the tile's outer edge.
	float outside = length(max(abs(tile_position) - cell_size * 0.5, 0.0)) / overhang;
	ALPHA = 1.0 - outside;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
}
''',
    '''shader_type spatial;

// The ground textures you painted in lessons 13 and 14.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// How many times the texture repeats per meter: 0.5 is once every 2 meters.
uniform float texture_scale = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;
// How far the tile reaches past its cell on each side, in meters.
uniform float overhang = 0.2;
// The GridMap's cell size, in meters.
uniform float cell_size = 0.5;
// Noise that makes the tile's edge ragged, shared by every ground tile.
uniform sampler2D edge_noise : filter_linear_mipmap, repeat_enable;
// How many times the edge noise repeats per meter.
uniform float edge_noise_scale = 0.4;

varying vec3 world_position;
varying vec2 tile_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	tile_position = VERTEX.xz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb;
	ROUGHNESS = roughness;
	// 0 inside the cell, rising to 1 at the tile's outer edge.
	float outside = length(max(abs(tile_position) - cell_size * 0.5, 0.0)) / overhang;
	// Inside the cell this stays at 0.5 or more, so the cell is always covered; at the outer edge it stays below.
	float noise = texture(edge_noise, world_position.xz * edge_noise_scale).r;
	ALPHA = noise + 0.5 - outside;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
}
''',
]
SHADER = 'res://art/ground/ground.gdshader'
# Layer heights: sand at the bottom, then dirt, then grass, 4 mm apart.
TILES = [('Sand', 0.0), ('Dirt', 0.004), ('Grass', 0.008)]
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}


def meadow_view(name):
    # The meadow from above at an angle, close to the path and the sand, as the reader looks at it.
    return [
        {'op': 'open', 'path': 'res://levels/meadow.tscn'},
        {'op': 'wait', 'frames': 40},
        eval_('''
var root := editor.get_edited_scene_root()
editor.get_selection().clear()
var viewport = plugin._collect(plugin.get_tree().root, "Node3DEditorViewport", "")[0]
var camera := EditorInterface.get_editor_viewport_3d(0).get_camera_3d()
'''),
        {'op': 'capture', 'name': name, 'frames': 40},
    ]


def export_library():
    return [
        {'op': 'menu', 'path': ['Scene', 'Export As...', 'MeshLibrary...']},
        {'op': 'wait', 'frames': 40},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is FileDialog:
		print("[probe] export dialog at ", window.current_dir, " file ", window.current_file)
		window.current_dir = "res://art/ground"
		window.current_file = "ground_tiles.meshlib"
		window.get_ok_button().pressed.emit()
		return ""
return "no Export Mesh Library dialog"
'''),
        {'op': 'wait', 'frames': 30},
        # Saving over the file asks first.
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog and not window is FileDialog:
		for label in plugin._collect(window, "Label", ""):
			print("[probe] export asks: ", label.text)
		window.get_ok_button().pressed.emit()
		return ""
print("[probe] export asked nothing")
'''),
        {'op': 'wait', 'frames': 40},
        eval_('''
var library := load("res://art/ground/ground_tiles.meshlib") as MeshLibrary
var out := []
for id in library.get_item_list():
	var mesh := library.get_item_mesh(id) as PlaneMesh
	out.append("%d %s size %s offset %s" % [id, library.get_item_name(id), mesh.size, mesh.center_offset])
print("[probe] mesh library ", out)
'''),
    ]


steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://art/ground/ground_tiles.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
]
# Size 1.5 and a layer height for each tile.
for name, height in TILES:
    steps += [
        {'op': 'select', 'path': name},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        open_resource('mesh', 'size'),
        {'op': 'wait', 'frames': 10},
        inspector_set('size', 'Vector2(0.9, 0.9)'),
        inspector_set('center_offset', f'Vector3(0, {height}, 0)'),
        {'op': 'wait', 'frames': 20},
    ]
steps += [
    show_row('center_offset'),
    {'op': 'capture', 'name': 'l17_grass_mesh', 'frames': 20},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 20},
    # The shader: open it from the FileSystem dock and type piece 1.
    {'op': 'fs', 'path': SHADER},
    {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': 'ground.gdshader', 'double': True},
    {'op': 'wait', 'frames': 40},
    *type_shader(PIECES[0], SHADER),
    eval_('editor.get_selection().clear()'),
    {'op': 'capture', 'name': 'l17_piece1_tiles', 'frames': 40},
    *export_library(),
    *meadow_view('l17_piece1_meadow'),
    # Piece 2: the noise.
    {'op': 'open', 'path': 'res://art/ground/ground_tiles.tscn'},
    {'op': 'wait', 'frames': 30},
    {'op': 'fs', 'path': SHADER},
    {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': 'ground.gdshader', 'double': True},
    {'op': 'wait', 'frames': 40},
    *type_shader(PIECES[1], SHADER),
    # The edge noise on Grass: a new NoiseTexture2D, seamless, 256 px, with a FastNoiseLite of low frequency.
    {'op': 'select', 'path': 'Grass'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    open_resource('mesh', 'material'),
    {'op': 'wait', 'frames': 10},
    open_resource('material', 'shader_parameter/edge_noise'),
    {'op': 'wait', 'frames': 10},
    unfold_inspector(),
    {'op': 'wait', 'frames': 10},
    resource_menu('shader_parameter/edge_noise', 'NoiseTexture2D'),
    {'op': 'wait', 'frames': 30},
    unfold_inspector(),
    open_resource('shader_parameter/edge_noise', 'seamless'),
    {'op': 'wait', 'frames': 10},
    inspector_set('width', '256'),
    inspector_set('height', '256'),
    inspector_set('seamless', 'true'),
    {'op': 'wait', 'frames': 20},
    resource_menu('noise', 'FastNoiseLite'),
    {'op': 'wait', 'frames': 30},
    unfold_inspector(),
    open_resource('noise', 'frequency'),
    {'op': 'wait', 'frames': 10},
    inspector_set('frequency', '0.03'),
    inspector_set('fractal_octaves', '3'),
    {'op': 'wait', 'frames': 60},
    show_row('frequency'),
    {'op': 'capture', 'name': 'l17_noise_settings', 'frames': 30},
    # Save it as its own file, so the three materials share one noise.
    resource_menu('shader_parameter/edge_noise', 'Save As...'),
    {'op': 'wait', 'frames': 30},
    open_in_file_dialog('art', 'ground'),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_file = "edge_noise.tres"
		return ""
return "no Save Resource dialog"
'''),
    {'op': 'capture', 'name': 'l17_save_noise', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
var noise := load("res://art/ground/edge_noise.tres") as NoiseTexture2D
print("[probe] edge noise ", noise.width, "x", noise.height, " seamless ", noise.seamless, " frequency ", (noise.noise as FastNoiseLite).frequency, " octaves ", (noise.noise as FastNoiseLite).fractal_octaves)
'''),
]
for name in ('Dirt', 'Sand'):
    steps += [{'op': 'select', 'path': name}, unfold_inspector(), {'op': 'wait', 'frames': 20},
              open_resource('mesh', 'material'), {'op': 'wait', 'frames': 10},
              open_resource('material', 'shader_parameter/edge_noise'), {'op': 'wait', 'frames': 10}]
    steps += quick_load('shader_parameter/edge_noise', 'edge_noise')
steps += [
    eval_('''
var root := editor.get_edited_scene_root()
var noise := []
for name in ["Grass", "Dirt", "Sand"]:
	var material := ((root.get_node(name) as MeshInstance3D).mesh as PlaneMesh).material as ShaderMaterial
	noise.append(material.get_shader_parameter("edge_noise"))
print("[probe] noise on tiles ", noise.map(func(n): return n.resource_path if n else "none"))
if noise[0] == null or noise[0] != noise[1] or noise[1] != noise[2]:
	return "the three tiles do not share one edge noise"
'''),
    {'op': 'select', 'path': '.'},
    eval_('editor.get_selection().clear()'),
    {'op': 'capture', 'name': 'l17_piece2_tiles', 'frames': 40},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 20},
    *export_library(),
    *meadow_view('l17_piece2_meadow'),
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 20},
]


def report(label):
    return {'op': 'eval', 'code': f'''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] player {label} position ", player.global_position.snapped(Vector3.ONE * 0.01), " on floor ", player.is_on_floor())'''}


game = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l17.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 8},
    report('start'),
    {'op': 'capture', 'name': 'l17_game_wide', 'frames': 10},
    {'op': 'wheel', 'steps': 4},
    {'op': 'capture', 'name': 'l17_game_close', 'frames': 10},
    {'op': 'quit'},
])
steps += play(game, 30, capture_running='l17_running')
write(sys.argv[2], steps)
