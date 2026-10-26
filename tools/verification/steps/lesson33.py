# Lesson 33: grass that parts around the player. A push_point shader global, a PushPoint script on the player that
# writes it, a shared include with push_aside, and the grass and flower shaders calling it.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, save_code, build, game_steps, play, quick_load,
                   type_shader, close_bottom_panel, show_row)
from shader_ui import SETTINGS, FIND_SETTINGS, select_tab, add_global, new_shader_file
from lesson33_pieces import GROUND_COVER, GRASS, FLOWER, PUSH_POINT

INCLUDE = 'res://art/shaders/ground_cover.gdshaderinc'
GRASS_SHADER = 'res://art/shaders/grass.gdshader'
FLOWER_SHADER = 'res://art/shaders/flower.gdshader'
SCRIPT = 'res://src/Player/PushPoint.cs'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [GROUND_COVER, GRASS, FLOWER, PUSH_POINT]
PIECE_EXTENSIONS = ['.gdshaderinc', '.gdshader', '.gdshader', '.cs']


def open_shader(path, name):
    return [{'op': 'fs', 'path': path}, {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': name, 'double': True},
            {'op': 'wait', 'frames': 40}]


def stand(x, z, name, wheel=10):
    # The player at a spot in the grass, the camera close, and a capture; the zoom is put back.
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nplayer.global_position = Vector3({x}, 0.05, {z})'},
            {'op': 'wheel', 'steps': wheel}, {'op': 'wait', 'frames': 40},
            {'op': 'eval', 'code': 'var point := tree.root.get_node("Meadow/Player/PushPoint")\nprint("[game] push point at ", point.global_position, " radius ", point.get("Radius"))'},
            {'op': 'capture', 'name': f'l33_{name}', 'frames': 10}, {'op': 'wheel', 'steps': -wheel}]


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l33.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)\nclock.set("Running", false)'},
    {'op': 'eval', 'code': 'var point := tree.root.get_node("Meadow/Player/PushPoint")\nprint("[game] push point at start ", point.global_position, " radius ", point.get("Radius"))'},
    *stand(0.0, 0.0, 'parted'),
    # Walk through it.
    {'op': 'wheel', 'steps': 10},
    {'op': 'eval', 'code': 'Input.action_press("move_forward")'},
    {'op': 'sleep', 'seconds': 0.5},
    {'op': 'capture', 'name': 'l33_walk_0', 'frames': 2},
    {'op': 'sleep', 'seconds': 0.5},
    {'op': 'capture', 'name': 'l33_walk_1', 'frames': 2},
    {'op': 'eval', 'code': 'Input.action_release("move_forward")'},
    {'op': 'sleep', 'seconds': 1.0},
    {'op': 'capture', 'name': 'l33_walk_2', 'frames': 2},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    # The shader global.
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    select_tab('Globals'),
    {'op': 'wait', 'frames': 30},
    select_tab('Shader Globals'),
    {'op': 'wait', 'frames': 30},
    *add_global('push_point', 'vec4'),
    {'op': 'capture', 'name': 'l33_globals', 'window': SETTINGS},
    eval_(FIND_SETTINGS + "\nwindow.hide()"),
    {'op': 'wait', 'frames': 30},
    eval_('ProjectSettings.save()'),
    eval_('''
var names := []
for setting in ProjectSettings.get_property_list():
	if str(setting.name).begins_with("shader_globals/push_point"):
		names.append("%s=%s" % [setting.name, ProjectSettings.get_setting(setting.name)])
print("[probe] push global ", names)
'''),
    # The include, and the two shaders calling it.
    *new_shader_file('New Shader Include...', INCLUDE, 'l33_create_include'),
    *type_shader(GROUND_COVER, INCLUDE),
    {'op': 'capture', 'name': 'l33_include_editor', 'frames': 20},
    *open_shader(GRASS_SHADER, 'grass.gdshader'),
    *type_shader(GRASS, GRASS_SHADER),
    {'op': 'capture', 'name': 'l33_grass_editor', 'frames': 20},
    *open_shader(FLOWER_SHADER, 'flower.gdshader'),
    *type_shader(FLOWER, FLOWER_SHADER),
    {'op': 'capture', 'name': 'l33_flower_editor', 'frames': 20},
    close_bottom_panel(),
    # The script, and the node on the player.
    save_code(SCRIPT, PUSH_POINT),
    *build('l33_built'),
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *add_node('Node3D', 'PushPoint'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'PushPoint.cs'),
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'PushPoint'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    show_row('Radius'),
    {'op': 'capture', 'name': 'l33_player_scene', 'frames': 20},
    eval_('''
var node := editor.get_edited_scene_root().get_node("PushPoint")
print("[probe] push point script ", node.get_script().resource_path, " radius ", node.get("Radius"))
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(game, 60),
]
write(sys.argv[2], steps)
