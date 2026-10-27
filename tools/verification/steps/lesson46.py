# Lesson 46, in Godot: the water shader, part 2. The sky and the light, the waves from one noise texture, refraction of the bed,
# the reflections of the clouds and the shore, and a foam hairline, typed in five steps and judged at noon, dusk, and night.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, resource_menu, open_resource, inspector_set,
                   click_tab, click_file, type_shader, open_bottom_panel, new_standalone_resource, save_resource_as, save_resource,
                   export_mesh_library)
from lesson46_pieces import WATER_LIGHT, WATER_WAVES, WATER_REFRACTION, WATER_REFLECTION, WATER, LAKE_BED, PIECES

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
    # A tree on the pond's north shore, so the water has something to reflect.
    click_tab('Scene'),
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'Trees/TreeOak3'},
    unfold_inspector(),
    inspector_set('position', 'Vector3(-0.3, 0, -3.0)'),
    {'op': 'wait', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The ripples: one seamless noise texture, as a normal map.
    *new_standalone_resource('NoiseTexture2D', 'l46_new_noise'),
    unfold_inspector(),
    inspector_set('width', '256'),
    inspector_set('height', '256'),
    inspector_set('seamless', 'true'),
    inspector_set('as_normal_map', 'true'),
    inspector_set('bump_strength', '6.0'),
    resource_menu('noise', 'FastNoiseLite'),
    {'op': 'wait', 'frames': 30},
    open_resource('noise', 'frequency'),
    inspector_set('noise_type', '1'),
    inspector_set('frequency', '0.02'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l46_wave_noise'},
    *save_resource_as(WAVES, 'l46_save_noise'),
    eval_(f'''
var texture: NoiseTexture2D = load("{WAVES}")
print("[probe] wave normals ", texture.width, "x", texture.height, " seamless ", texture.seamless, " normal map ", texture.as_normal_map, " bump ", texture.bump_strength, " noise ", texture.noise.noise_type, " ", texture.noise.frequency)
'''),
    # Step 1: the sky and the light. Step 2: the waves. Step 3: refraction. Step 4: reflections. Step 5: the edge.
    *stage('l46_light', WATER_LIGHT, [('pond', *POND, 3.2)]),
    *edit_shader(WATER_SHADER, WATER_WAVES),
    eval_('EditorInterface.edit_resource(load("res://art/water/water.tres"))'),
    {'op': 'wait', 'frames': 40},
    unfold_inspector(),
    *quick_load('shader_parameter/wave_normals', 'wave_normals.tres'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l46_wave_param'},
    *save_resource(),
    {'op': 'capture', 'name': 'l46_waves_editor', 'frames': 20},
    *run_game('l46_waves', [('pond', *POND, 3.2), ('close', *POND, 1.6)]),
    *stage('l46_refraction', WATER_REFRACTION, [('wall', *WALL, 1.6), ('close', *POND, 1.6)]),
    *stage('l46_reflection', WATER_REFLECTION, [('pond', *POND, 3.2), ('wall', *WALL, 1.6)]),
    # Step 5: the foam and the color wobble, and the lake bed's caustics.
    *edit_shader(LAKE_BED_SHADER, LAKE_BED),
    click_tab('Scene'),
    {'op': 'open', 'path': TILES_SCENE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'Water'},
    unfold_inspector(),
    open_resource('mesh', 'size'),
    open_resource('material', 'shader'),
    unfold_inspector(),
    *quick_load('shader_parameter/wave_normals', 'wave_normals.tres'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l46_lake_bed_param'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *export_mesh_library(),
    *stage('l46_final', WATER, [('pond', *POND, 3.2), ('close', *POND, 1.6), ('wall', *WALL, 1.6), ('dusk', *POND, 3.2, 0.78),
                                ('night', *POND, 3.2, 0.0), ('wide', *POND, 6.0)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
