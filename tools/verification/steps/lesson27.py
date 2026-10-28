# Lesson 27: the foliage shader and wind. Two shader globals, a wind include, the foliage shader for the cards and a bark
# shader for the trunk, their materials on the oak, and the tree in the running game by day, dusk, and night, and in the wind.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, resource_menu, open_resource,
                   new_resource, open_in_file_dialog, open_bottom_panel, type_shader, close_bottom_panel)
from shader_ui import SETTINGS, FIND_SETTINGS, select_tab, add_global, set_global, new_shader_file
from lesson27_pieces import WIND, FOLIAGE, BARK

INCLUDE = 'res://art/shaders/wind.gdshaderinc'
FOLIAGE_SHADER = 'res://art/shaders/foliage.gdshader'
BARK_SHADER = 'res://art/shaders/bark.gdshader'
TREE = 'res://art/nature/tree_oak/tree_oak.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [WIND, FOLIAGE, BARK]


def material_on(node, shader_file, parameters, save_as, captures, clear=False):
    steps = [
        {'op': 'select', 'path': node},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        # The trunk still has lesson 24's palette material: clear it first.
        *([resource_menu('material_override', 'Clear'), {'op': 'wait', 'frames': 20}] if clear else []),
        *new_resource('material_override', 'ShaderMaterial'),
        open_resource('material_override', 'shader'),
        *quick_load('shader', shader_file),
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
    ]
    for parameter, file in parameters:
        steps += [*quick_load(f'shader_parameter/{parameter}', file)]
    steps += [
        {'op': 'capture', 'name': captures, 'frames': 20},
        resource_menu('material_override', 'Save As...'),
        {'op': 'wait', 'frames': 30},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/nature/tree_oak"
		window.current_file = "{save_as}"
		return ""
return "no Save Resource dialog"
'''),
        {'op': 'capture', 'name': captures + '_save', 'window': 'class:EditorFileDialog'},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
        {'op': 'wait', 'frames': 40},
    ]
    return steps


def hour(time, name):
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l27_{name}', 'frames': 10}]


def wind_strip(name, count, seconds):
    steps = []
    for index in range(count):
        steps += [{'op': 'sleep', 'seconds': seconds}, {'op': 'capture', 'name': f'l27_{name}_{index}', 'frames': 2}]
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l27.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Trees/TreeOak").position = Vector3(-2.2, 0, -0.2)'},
    {'op': 'eval', 'code': 'print("[game] wind ", RenderingServer.global_shader_parameter_get("wind_direction"), " ", RenderingServer.global_shader_parameter_get("wind_strength"))'},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l27_noon', 'frames': 10},
    {'op': 'wheel', 'steps': 4},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l27_noon_close', 'frames': 10},
    *hour(0.8, 'dusk_close'),
    *hour(0.0, 'night_close'),
    *hour(0.5, 'noon_again'),
    {'op': 'eval', 'code': 'RenderingServer.global_shader_parameter_set("wind_strength", 1.0)'},
    {'op': 'eval', 'code': 'print("[game] wind now ", RenderingServer.global_shader_parameter_get("wind_strength"))'},
    *wind_strip('wind', 6, 0.5),
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    # The two shader globals, with values.
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    select_tab('Globals'),
    {'op': 'wait', 'frames': 30},
    select_tab('Shader Globals'),
    {'op': 'wait', 'frames': 30},
    *add_global('wind_direction', 'vec2'),
    *add_global('wind_strength', 'float'),
    *set_global('wind_direction', [1.0, 0.4]),
    *set_global('wind_strength', [0.6]),
    {'op': 'capture', 'name': 'l27_globals', 'window': SETTINGS},
    eval_(FIND_SETTINGS + "\nwindow.hide()"),
    {'op': 'wait', 'frames': 30},
    eval_('ProjectSettings.save()'),
    eval_('''
var names := []
for setting in ProjectSettings.get_property_list():
	if str(setting.name).begins_with("shader_globals/"):
		names.append("%s=%s" % [setting.name, ProjectSettings.get_setting(setting.name)])
print("[probe] shader globals ", names)
'''),
    # The wind include, the foliage shader, and the bark shader.
    *new_shader_file('New Shader Include...', INCLUDE, 'l27_create_include'),
    *type_shader(WIND, INCLUDE),
    {'op': 'capture', 'name': 'l27_wind_editor', 'frames': 20},
    *new_shader_file('New Shader...', FOLIAGE_SHADER, 'l27_create_foliage'),
    *type_shader(FOLIAGE, FOLIAGE_SHADER),
    {'op': 'capture', 'name': 'l27_foliage_editor', 'frames': 20},
    *new_shader_file('New Shader...', BARK_SHADER, 'l27_create_bark'),
    *type_shader(BARK, BARK_SHADER),
    close_bottom_panel(),
    # The materials, on the tree scene.
    {'op': 'open', 'path': TREE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *material_on('leaves', 'foliage.gdshader', [('leaf_atlas', 'leaf_atlas.png')], 'leaves.tres', 'l27_leaves_material'),
    *material_on('tree_oak', 'bark.gdshader', [('palette', 'palette.png')], 'bark.tres', 'l27_bark_material', clear=True),
    eval_('''
var root := editor.get_edited_scene_root()
for name in ["leaves", "tree_oak"]:
	var node := root.get_node(name) as MeshInstance3D
	var material := node.material_override as ShaderMaterial
	print("[probe] ", name, " override ", material.resource_path, " shader ", material.shader.resource_path)
'''),
    {'op': 'select', 'path': 'leaves'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l27_tree_scene'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The meadow, in the running game.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(game, 60),
]
write(sys.argv[2], steps)
