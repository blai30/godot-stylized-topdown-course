# Lesson 20: the sun. One DirectionalLight3D in the environment scene, a pale warm light from the top left, with shadows
# set up for an orthographic camera: Orthogonal shadow mode, the camera's far plane pulled in, and a bias that keeps the
# rocks and the player on the ground. The meadow's own Sun is deleted.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, add_node, press_delete_in_scene_dock, game_steps,
                   play, close_bottom_panel)

SCENE = 'res://world/environment/world_environment.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}


def game(name):
    return game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', f'game-{name}.jsonl'), [
        {'op': 'wait', 'frames': 60},
        {'op': 'sleep', 'seconds': 8},
        {'op': 'capture', 'name': f'{name}_wide', 'frames': 10},
        {'op': 'wheel', 'steps': 4},
        {'op': 'capture', 'name': f'{name}_close', 'frames': 10},
        {'op': 'quit'},
    ])


def run_meadow(name):
    return [{'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(game(name), 20)]


def enable(name):
    # The Shadow group's On checkbox sits in its header, not in a row of its own, so it is set on the node.
    return eval_(f'''
var sun := editor.get_edited_scene_root().get_node("Sun") as DirectionalLight3D
sun.set("{name}", true)
sun.notify_property_list_changed()
if not sun.get("{name}"):
	return "{name} is not on"
''')


def edit(*pairs):
    return [enable(name) if name.endswith('_enabled') else inspector_set(name, value) for name, value in pairs]


def select_sun():
    return [{'op': 'open', 'path': SCENE}, {'op': 'wait', 'frames': 30}, {'op': 'select', 'path': 'Sun'}, unfold_inspector(),
            {'op': 'wait', 'frames': 20}]


def rows(row, name):
    return [{'op': 'wait', 'frames': 30}, show_row(row), {'op': 'wait', 'frames': 20}, {'op': 'capture', 'name': name, 'frames': 20}]


steps = [
    {'op': 'sleep', 'seconds': 3},
    # The meadow's own Sun goes; the light moves into the environment scene.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'Sun'},
    unfold_inspector(),
    *rows('shadow_bias', 'l20_old_sun'),
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'type': 'Button', 'text': 'Delete'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
if editor.get_edited_scene_root().get_node_or_null("Sun"):
	return "the old Sun is still there"
'''),
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
    # The new Sun in the environment scene, with Godot's defaults and shadows on.
    {'op': 'open', 'path': SCENE},
    {'op': 'wait', 'frames': 40},
    *add_node('DirectionalLight3D', 'Sun'),
    {'op': 'capture', 'name': 'l20_added', 'frames': 20},
    unfold_inspector(),
    *edit(('shadow_enabled', 'true')),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *run_meadow('l20_default_shadows'),
    # Direction, color, and energy.
    *select_sun(),
    *edit(('rotation', 'Vector3(deg_to_rad(-62), deg_to_rad(225), 0)'), ('light_color', 'Color("#FFE2AD")'),
          ('light_energy', '0.85')),
    *rows('light_energy', 'l20_light_rows'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *run_meadow('l20_sun'),
    # The camera's far plane.
    {'op': 'open', 'path': 'res://world/camera/camera_rig.tscn'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'Pivot/Camera3D'},
    unfold_inspector(),
    *edit(('far', '100')),
    *rows('far', 'l20_camera_far'),
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
    # Orthogonal shadows and bias.
    *select_sun(),
    *edit(('directional_shadow_mode', '0'), ('directional_shadow_max_distance', '100'), ('directional_shadow_fade_start', '1.0')),
    *rows('directional_shadow_fade_start', 'l20_shadow_mode_rows'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *run_meadow('l20_orthogonal'),
    *select_sun(),
    *edit(('light_angular_distance', '0.25'), ('shadow_bias', '0.03'), ('shadow_normal_bias', '1.0'), ('shadow_blur', '1.5')),
    *rows('shadow_blur', 'l20_bias_rows'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *run_meadow('l20_final'),
    eval_('''
var scene = load("res://world/environment/world_environment.tscn").instantiate()
var sun := scene.get_node("Sun") as DirectionalLight3D
print("[probe] sun rotation ", sun.rotation_degrees, " color ", sun.light_color.to_html(false), " energy ", sun.light_energy, " shadow ", sun.shadow_enabled, " mode ", sun.directional_shadow_mode, " max ", sun.directional_shadow_max_distance, " fade ", sun.directional_shadow_fade_start, " angular ", sun.light_angular_distance, " bias ", sun.shadow_bias, " normal ", sun.shadow_normal_bias, " blur ", sun.shadow_blur)
var rig = load("res://world/camera/camera_rig.tscn").instantiate()
var camera := rig.get_node("Pivot/Camera3D") as Camera3D
print("[probe] camera far ", camera.far, " size ", camera.size)
'''),
]
write(sys.argv[2], steps)
