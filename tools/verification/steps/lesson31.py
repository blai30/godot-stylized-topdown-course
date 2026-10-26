# Lesson 31: the grass shader. A shared ground color include, the ground shader using it, the wind include's grass and
# petal motion, the grass and flower shaders, their materials on a preview scene of the lesson 30 meshes, and the preview
# in the meadow by day, dusk, night, and in the wind.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, instantiate_under, game_steps, play, quick_load,
                   resource_menu, open_resource, new_resource, open_in_file_dialog, open_bottom_panel, type_shader,
                   close_bottom_panel, click_tab, show_row)
from shader_ui import new_shader_file
from lesson31_pieces import GROUND_COLOR, GROUND, WIND, GRASS, FLOWER

GROUND_COLOR_INCLUDE = 'res://art/shaders/ground_color.gdshaderinc'
GROUND_SHADER = 'res://art/ground/ground.gdshader'
WIND_INCLUDE = 'res://art/shaders/wind.gdshaderinc'
GRASS_SHADER = 'res://art/shaders/grass.gdshader'
FLOWER_SHADER = 'res://art/shaders/flower.gdshader'
FOLDER = 'res://art/nature/grass'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [GROUND_COLOR, GROUND, WIND, GRASS, FLOWER]


def open_shader(path, name):
    return [{'op': 'fs', 'path': path}, {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': name, 'double': True},
            {'op': 'wait', 'frames': 40}]


def game(name, extra):
    return game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', f'game-{name}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *extra, {'op': 'quit'}])


def noon(name, wheel):
    # Noon, zoomed in by wheel steps, and a capture; the zoom is put back.
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)'},
            *([{'op': 'wheel', 'steps': wheel}] if wheel else []),
            {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': name, 'frames': 10},
            *([{'op': 'wheel', 'steps': -wheel}] if wheel else [])]


def hour(time, name, wheel):
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            *([{'op': 'wheel', 'steps': wheel}] if wheel else []),
            {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l31_{name}', 'frames': 10},
            *([{'op': 'wheel', 'steps': -wheel}] if wheel else [])]


def wind_strip(name, count, seconds):
    steps = []
    for index in range(count):
        steps += [{'op': 'sleep', 'seconds': seconds}, {'op': 'capture', 'name': f'l31_{name}_{index}', 'frames': 2}]
    return steps


def material_on(node, shader_file, parameters, tint, save_as, capture):
    steps = [
        {'op': 'select', 'path': node},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        *new_resource('material_override', 'ShaderMaterial'),
        open_resource('material_override', 'shader'),
        *quick_load('shader', shader_file),
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
    ]
    for parameter, file in parameters:
        steps += [*quick_load(f'shader_parameter/{parameter}', file)]
    if tint:
        steps += [inspector_set('shader_parameter/ground_tint', f'Color("{tint}")')]
    steps += [
        show_row('shader_parameter/ground_tint') if tint else {'op': 'wait', 'frames': 1},
        {'op': 'capture', 'name': capture, 'frames': 20},
        resource_menu('material_override', 'Save As...'),
        {'op': 'wait', 'frames': 30},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "{FOLDER}"
		window.current_file = "{save_as}"
		return ""
return "no Save Resource dialog"
'''),
        {'op': 'capture', 'name': capture + '_save', 'window': 'class:EditorFileDialog'},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
        {'op': 'wait', 'frames': 40},
    ]
    return steps


ground_run = lambda name: [{'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40},
                           *play(game(name, [*noon(f'l31_{name}', 5)]), 40)]

steps = [
    {'op': 'sleep', 'seconds': 3},
    # The ground before: the new include must not change it.
    *ground_run('ground_before'),
    # The ground's color in a shared include, and the ground shader using it.
    *new_shader_file('New Shader Include...', GROUND_COLOR_INCLUDE, 'l31_create_include'),
    *type_shader(GROUND_COLOR, GROUND_COLOR_INCLUDE),
    {'op': 'capture', 'name': 'l31_ground_color_editor', 'frames': 20},
    *open_shader(GROUND_SHADER, 'ground.gdshader'),
    *type_shader(GROUND, GROUND_SHADER),
    {'op': 'capture', 'name': 'l31_ground_editor', 'frames': 20},
    close_bottom_panel(),
    *ground_run('ground_after'),
    # The wind include gets grass and petal motion; then the two shaders.
    *open_shader(WIND_INCLUDE, 'wind.gdshaderinc'),
    *type_shader(WIND, WIND_INCLUDE),
    {'op': 'capture', 'name': 'l31_wind_editor', 'frames': 20},
    *new_shader_file('New Shader...', GRASS_SHADER, 'l31_create_grass'),
    *type_shader(GRASS, GRASS_SHADER),
    {'op': 'capture', 'name': 'l31_grass_editor', 'frames': 20},
    *new_shader_file('New Shader...', FLOWER_SHADER, 'l31_create_flower'),
    *type_shader(FLOWER, FLOWER_SHADER),
    {'op': 'capture', 'name': 'l31_flower_editor', 'frames': 20},
    close_bottom_panel(),
    # A preview scene: the lesson 30 file as an inherited scene, with the materials on its meshes.
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'nature', 'grass'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "grass.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no grass.glb in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l31_inherit_dialog', 'window': 'Open Base Scene'},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] inherited scene root ", root.name, " <", root.get_class(), "> children ", root.get_children().map(func(n): return n.name))
'''),
    {'op': 'main_screen', 'name': '3D'},
    click_tab('Scene'),
    eval_('''
var root := editor.get_edited_scene_root()
root.name = "GrassPreview"
'''),
    *material_on('grass_clump_a', 'grass.gdshader', [('ground_texture', 'grass_detail.png'), ('field_noise', 'edge_noise.tres')], '95CC5A', 'grass.tres', 'l31_grass_material'),
    {'op': 'select', 'path': 'grass_clump_b'},
    unfold_inspector(),
    *quick_load('material_override', 'grass.tres'),
    {'op': 'select', 'path': 'grass_clump_c'},
    unfold_inspector(),
    *quick_load('material_override', 'grass.tres'),
    *material_on('flower_daisy', 'flower.gdshader', [], None, 'flower.tres', 'l31_flower_material'),
    {'op': 'select', 'path': 'flower_cup'},
    unfold_inspector(),
    *quick_load('material_override', 'flower.tres'),
    eval_('''
var root := editor.get_edited_scene_root()
for node in root.get_children():
	var material := (node as MeshInstance3D).material_override as ShaderMaterial
	print("[probe] ", node.name, " override ", material.resource_path, " shader ", material.shader.resource_path)
'''),
    {'op': 'select', 'path': 'grass_clump_a'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l31_preview_scene'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l31_save_scene', 'window': 'Save Scene As'},
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
    # In the meadow, beside the player.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    *instantiate_under('.', 'grass_preview.tscn', capture='l31_select_scene'),
    {'op': 'select', 'path': 'GrassPreview'},
    inspector_set('position', 'Vector3(-1, 0, 1.2)'),
    {'op': 'capture', 'name': 'l31_preview_inspector', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    *play(game('l31_run', [
        *noon('l31_noon', 0), *noon('l31_noon_close', 10), *hour(0.8, 'dusk_close', 10), *hour(0.0, 'night_close', 10), *hour(0.5, 'noon_again', 0),
        {'op': 'eval', 'code': 'RenderingServer.global_shader_parameter_set("wind_strength", 1.0)'},
        {'op': 'wheel', 'steps': 10},
        *wind_strip('wind', 6, 0.5),
    ]), 70),
]
write(sys.argv[2], steps)
