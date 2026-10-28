# Lesson 53, in Godot: cloud shadows. A seamless noise texture and three shader globals, a clouds include that works out how much of a
# point is under cloud, and the ground, bank, grass, flower, foliage, and bark shaders darkening by it; the water reflects the same clouds.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, resource_menu, open_resource, inspector_set, open_bottom_panel,
                   type_shader, close_bottom_panel, new_standalone_resource, save_resource_as, make_folder)
from shader_ui import SETTINGS, FIND_SETTINGS, select_tab, add_global, set_global, set_texture_global, new_shader_file
from lesson53_pieces import CLOUDS, WIND, GROUND, BANK, GRASS, FLOWER, FOLIAGE, BARK, WATER, PIECES

NOISE = 'res://art/clouds/cloud_noise.tres'
SHADERS = [('res://art/shaders/wind.gdshaderinc', 'wind.gdshaderinc', WIND), ('res://art/ground/ground.gdshader', 'ground.gdshader', GROUND),
           ('res://art/shaders/bank.gdshader', 'bank.gdshader', BANK), ('res://art/shaders/grass.gdshader', 'grass.gdshader', GRASS),
           ('res://art/shaders/flower.gdshader', 'flower.gdshader', FLOWER), ('res://art/shaders/foliage.gdshader', 'foliage.gdshader', FOLIAGE),
           ('res://art/shaders/bark.gdshader', 'bark.gdshader', BARK), ('res://art/shaders/water.gdshader', 'water.gdshader', WATER)]
INCLUDE = 'res://art/shaders/clouds.gdshaderinc'
CLOCK = 'Meadow/WorldEnvironment/Day'
POND = (-0.25, -1.25)
out_dir = os.path.dirname(sys.argv[2])


def open_shader(path, name):
    return [{'op': 'fs', 'path': path}, {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': name, 'double': True},
            {'op': 'wait', 'frames': 40}]


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size, time=0.5, strength=None):
    # The camera follows the player, so the hidden player stands on the spot.
    steps = [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
             {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if strength is not None:
        steps.append({'op': 'eval', 'code': f'RenderingServer.global_shader_parameter_set("cloud_strength", {strength})'})
    return [*steps, zoom(size), {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'l53_{name}', 'frames': 10}]


PROBE = '''
print("[game] cloud globals: ", ProjectSettings.get_setting("shader_globals/cloud_scale"), " ", ProjectSettings.get_setting("shader_globals/cloud_strength"), " ", ProjectSettings.get_setting("shader_globals/cloud_texture"))'''


def run_game(prefix, shots):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *[step for shot in shots for step in look(*shot)],
        {'op': 'eval', 'code': PROBE},
        {'op': 'quit'}])
    return play(game, 45 + 12 * len(shots))


steps = [
    {'op': 'sleep', 'seconds': 3},
    *make_folder('art', 'clouds'),
    # The noise: one seamless texture, big soft patches.
    *new_standalone_resource('NoiseTexture2D', 'l53_new_noise'),
    unfold_inspector(),
    inspector_set('width', '512'),
    inspector_set('height', '512'),
    inspector_set('seamless', 'true'),
    resource_menu('noise', 'FastNoiseLite'),
    {'op': 'wait', 'frames': 30},
    open_resource('noise', 'frequency'),
    inspector_set('frequency', '0.012'),
    inspector_set('fractal_octaves', '3'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l53_noise'},
    *save_resource_as(NOISE, 'l53_save_noise'),
    eval_(f'''
var texture: NoiseTexture2D = load("{NOISE}")
print("[probe] cloud noise ", texture.width, "x", texture.height, " seamless ", texture.seamless, " noise ", texture.noise.noise_type, " ", texture.noise.frequency, " octaves ", texture.noise.fractal_octaves)
'''),
    # The three globals, with values.
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    select_tab('Globals'),
    {'op': 'wait', 'frames': 30},
    select_tab('Shader Globals'),
    {'op': 'wait', 'frames': 30},
    *add_global('cloud_texture', 'sampler2D'),
    *add_global('cloud_scale', 'float'),
    *add_global('cloud_strength', 'float'),
    *set_texture_global('cloud_texture', NOISE),
    *set_global('cloud_scale', [45.0]),
    *set_global('cloud_strength', [0.5]),
    {'op': 'capture', 'name': 'l53_globals', 'window': SETTINGS},
    eval_(FIND_SETTINGS + "\nwindow.hide()"),
    {'op': 'wait', 'frames': 30},
    eval_('ProjectSettings.save()'),
    eval_('''
var names := []
for setting in ProjectSettings.get_property_list():
	if str(setting.name).begins_with("shader_globals/cloud"):
		names.append("%s=%s" % [setting.name, ProjectSettings.get_setting(setting.name)])
print("[probe] cloud globals ", names)
'''),
    # The wind include learns to be included twice, and the clouds include is new.
    *open_shader('res://art/shaders/wind.gdshaderinc', 'wind.gdshaderinc'),
    open_bottom_panel('Shader Editor'),
    {'op': 'wait', 'frames': 40},
    *type_shader(WIND, 'res://art/shaders/wind.gdshaderinc'),
    {'op': 'capture', 'name': 'l53_wind_editor', 'frames': 20},
    *new_shader_file('New Shader Include...', INCLUDE, 'l53_create_include'),
    *type_shader(CLOUDS, INCLUDE),
    {'op': 'capture', 'name': 'l53_include_editor', 'frames': 20},
]
for path, name, code in SHADERS[1:]:
    steps += [*open_shader(path, name), *type_shader(code, path)]
    if name in ('ground.gdshader', 'water.gdshader'):
        steps.append({'op': 'capture', 'name': 'l53_' + name.split('.')[0] + '_editor', 'frames': 20})
steps += [
    close_bottom_panel(),
    {'op': 'wait', 'frames': 30},
    *run_game('l53_run', [('wide', 0.0, 0.0, 20.0), ('wide_off', 0.0, 0.0, 20.0, 0.5, 0.0), ('wide_on', 0.0, 0.0, 20.0, 0.5, 0.5),
                          ('grove', -3.0, -2.0, 11.0, 0.5, 0.5), ('pond', *POND, 3.2, 0.5, 0.5), ('pond_off', *POND, 3.2, 0.5, 0.0),
                          ('dusk', 0.0, 0.0, 20.0, 0.78, 0.5), ('night', 0.0, 0.0, 20.0, 0.0, 0.5)]),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
