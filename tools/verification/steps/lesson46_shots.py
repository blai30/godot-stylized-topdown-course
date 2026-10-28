# Retakes lesson 46's final shots from its snapshot. Lesson 46, in Godot: the water shader, part 2. The sky and the light, the waves from one noise texture, refraction of the bed,
# the reflections of the clouds and the shore, and a foam hairline, typed in five steps and judged at noon, dusk, and night.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, resource_menu, open_resource, inspector_set,
                   click_tab, click_file, type_shader, open_bottom_panel, new_standalone_resource, save_resource_as, save_resource,
                   export_mesh_library)

WATER_SHADER = 'res://art/shaders/water.gdshader'
LAKE_BED_SHADER = 'res://art/shaders/lake_bed.gdshader'
MEADOW = 'res://levels/meadow.tscn'
TILES_SCENE = 'res://art/ground/ground_tiles.tscn'
WAVES = 'res://art/water/wave_normals.tres'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

POND = (-0.25, -1.25)
WALL = (-0.25, -1.9)


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def look(prefix, name, x, z, size, time=0.5):
    # The camera follows the player, so the hidden player stands on the spot.
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'{prefix}_{name}', 'frames': 10}]


def run_game(prefix, shots):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *[step for shot in shots for step in look(prefix, *shot)],
        {'op': 'quit'}])
    return play(game, 45 + 12 * len(shots))


def edit_shader(path, code):
    return [eval_(f'EditorInterface.edit_resource(load("{path}"))'), open_bottom_panel('Shader Editor'), {'op': 'wait', 'frames': 40},
            *type_shader(code, path)]


def stage(prefix, code, shots):
    return [*edit_shader(WATER_SHADER, code), {'op': 'capture', 'name': f'{prefix}_editor', 'frames': 20}, *run_game(prefix, shots)]


steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'main_screen', 'name': '3D'},
    *run_game('l46_final', [('pond', *POND, 3.2), ('close', *POND, 1.6), ('wall', *WALL, 1.6), ('dusk', *POND, 3.2, 0.78),
                            ('night', *POND, 3.2, 0.0), ('wide', *POND, 6.0)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
