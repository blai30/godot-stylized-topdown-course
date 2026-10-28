# Lesson 49, in Godot: noise as a resource. A NoiseTexture2D shows a FastNoiseLite in the Inspector, one pixel for one meter of the
# level; its frequency, octaves, and seed are tuned there; the terrain and forest noises are saved; and a GenerationProfile resource
# holds them and a seed and answers for any point of the ground.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, click_tab, build, save_code, make_folder, new_standalone_resource, save_resource_as,
                   resource_menu, open_resource, inspector_set, quick_load, show_row, INSPECTOR)
from lesson49_pieces import PROFILE, PIECES

FOLDER = 'res://world/generation'
TERRAIN = f'{FOLDER}/terrain_noise.tres'
FOREST = f'{FOLDER}/forest_noise.tres'
PREVIEW = f'{FOLDER}/noise_preview.tres'
PROFILE_RES = f'{FOLDER}/generation_profile.tres'
PROFILE_CODE = 'res://src/Generation/GenerationProfile.cs'


def save_noise_as(path, capture=None):
    # The noise row's menu > Save As..., the folder and name typed, and Save.
    folder, name = path.rsplit('/', 1)
    steps = [
        resource_menu('noise', 'Save As...'),
        {'op': 'wait', 'frames': 30},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "{folder}"
		window.current_file = "{name}"
		return ""
return "no Save As dialog"
'''),
        {'op': 'wait', 'frames': 20},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'class:EditorFileDialog'})
    steps += [
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
        {'op': 'wait', 'frames': 40},
    ]
    return steps


def tune(name, **values):
    # Sets noise properties and captures the Inspector with the preview.
    return [*[inspector_set(key, value) for key, value in values.items()], {'op': 'wait', 'frames': 30}, {'op': 'capture', 'name': name}]


CHECK = f'''
var profile: Resource = load("{PROFILE_RES}")
print("[probe] profile ", profile.get_script().resource_path, " seed ", profile.get("Seed"), " terrain ", profile.get("Terrain").resource_path, " forest ", profile.get("Forest").resource_path)
var points := [Vector2(0, 0), Vector2(3.5, -7.25), Vector2(-20.25, 11.75), Vector2(23.75, 23.75)]
var first := []
for point in points:
	first.append([profile.call("TerrainAt", point), profile.call("ForestAt", point)])
var again := []
for point in points:
	again.append([profile.call("TerrainAt", point), profile.call("ForestAt", point)])
print("[probe] same seed same values ", first == again, " ", first)
var terrain: FastNoiseLite = profile.get("Terrain")
profile.set("Seed", 8)
var other: float = profile.call("TerrainAt", points[1])
profile.set("Seed", 7)
print("[probe] seed 7 ", first[1][0], " seed 8 ", other, " differ ", not is_equal_approx(first[1][0], other))
# Slid by the seed's offset, the raw noise gives the same number: the profile adds nothing else.
var offset := Vector2(posmod(7 * 7919, 10007), posmod(7 * 104729, 10007))
print("[probe] raw noise at the offset point ", terrain.get_noise_2dv(points[1] + offset), " profile ", first[1][0])
# Values stay in range, and the share of the 96 by 96 cell level that would be water at a level of -0.2.
for seed_value in [1, 7, 8, 9, 10, 11, 12]:
	profile.set("Seed", seed_value)
	var low := 1.0
	var high := -1.0
	var water := 0
	var forest_share := 0
	for cx in range(-48, 48):
		for cz in range(-48, 48):
			var point := (Vector2(cx, cz) + Vector2(0.5, 0.5)) * 0.5
			var value: float = profile.call("TerrainAt", point)
			low = minf(low, value)
			high = maxf(high, value)
			if value < -0.2:
				water += 1
			if float(profile.call("ForestAt", point)) > 0.2:
				forest_share += 1
	print("[probe] seed %d range %.2f to %.2f water %.1f%% forest %.1f%%" % [seed_value, low, high, 100.0 * water / 9216.0, 100.0 * forest_share / 9216.0])
profile.set("Seed", 7)
'''

steps = [
    {'op': 'sleep', 'seconds': 3},
    *make_folder('world', 'generation'),
    *make_folder('src', 'Generation'),
    click_tab('Scene'),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    # A texture to look at the noise through: one pixel is one meter, so 48 pixels are the whole level. Normalize off, so the
    # gray is the value the generator reads, black at -1 and white at 1.
    *new_standalone_resource('NoiseTexture2D', 'l49_new_texture'),
    unfold_inspector(),
    inspector_set('width', '48'),
    inspector_set('height', '48'),
    inspector_set('normalize', 'false'),
    resource_menu('noise', 'FastNoiseLite'),
    {'op': 'wait', 'frames': 30},
    open_resource('noise', 'frequency'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l49_default'},
    # The knobs: frequency, then octaves, then the seed.
    *tune('l49_frequency_low', frequency='0.01'),
    *tune('l49_frequency_high', frequency='0.15'),
    *tune('l49_frequency', frequency='0.04'),
    *tune('l49_octaves_one', fractal_octaves='1'),
    *tune('l49_octaves_three', fractal_octaves='3'),
    *tune('l49_seed', seed='5'),
    *tune('l49_seed_back', seed='0'),
    *save_noise_as(TERRAIN, 'l49_save_terrain'),
    eval_(f'''
var noise: FastNoiseLite = load("{TERRAIN}")
print("[probe] terrain noise ", noise.noise_type, " freq ", noise.frequency, " octaves ", noise.fractal_octaves, " seed ", noise.seed, " fractal ", noise.fractal_type)
'''),
    # The forest noise: a second noise on the same texture.
    resource_menu('noise', 'Clear'),
    {'op': 'wait', 'frames': 20},
    resource_menu('noise', 'FastNoiseLite'),
    {'op': 'wait', 'frames': 30},
    open_resource('noise', 'frequency'),
    unfold_inspector(),
    *tune('l49_forest_default', frequency='0.07'),
    *tune('l49_forest', fractal_octaves='2', seed='2'),
    *save_noise_as(FOREST),
    eval_(f'''
var noise: FastNoiseLite = load("{FOREST}")
print("[probe] forest noise ", noise.noise_type, " freq ", noise.frequency, " octaves ", noise.fractal_octaves, " seed ", noise.seed)
'''),
    *save_resource_as(PREVIEW, 'l49_save_preview'),
    # The profile.
    save_code(PROFILE_CODE, PROFILE),
    *build('l49_built'),
    eval_('''
var names := []
for entry in ProjectSettings.get_global_class_list():
	names.append(entry["class"])
print("[probe] global classes ", names)
'''),
    *new_standalone_resource('GenerationProfile', 'l49_new_profile'),
    unfold_inspector(),
    inspector_set('Seed', '7'),
    *quick_load('Terrain', 'terrain_noise.tres'),
    {'op': 'wait', 'frames': 20},
    *quick_load('Forest', 'forest_noise.tres'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l49_profile'},
    *save_resource_as(PROFILE_RES, 'l49_save_profile'),
    eval_(CHECK),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
