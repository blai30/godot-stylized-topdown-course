# Lesson 28: the tree scene and the grove. A trunk collision, a small script that gives each tree its place in the wind,
# six more oaks with their own turn and scale, and the grove in the running game: collision, zoom, and wind.
import math
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, instantiate_under, save_code, build, game_steps,
                   play, quick_load, new_resource, open_resource, show_row)
from lesson28_pieces import WIND_PHASE, GROVE

SCRIPT = 'res://src/World/WindPhase.cs'
TREE = 'res://art/nature/tree_oak/tree_oak.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [WIND_PHASE]


def vec(position):
    return 'Vector3(%s, %s, %s)' % position


def place(name, position, yaw, scale):
    return [
        {'op': 'select', 'path': f'Trees/{name}'},
        unfold_inspector(),
        {'op': 'wait', 'frames': 10},
        inspector_set('position', vec(position)),
        inspector_set('rotation', f'Vector3(0, deg_to_rad({yaw}), 0)'),
        inspector_set('scale', f'Vector3({scale}, {scale}, {scale})'),
        {'op': 'wait', 'frames': 10},
    ]


def hour(time, name, wheel=0):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l28_{name}', 'frames': 10}]
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l28.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    {'op': 'eval', 'code': '''
var phases := []
for node in tree.root.get_node("Meadow/Trees").get_children():
	var leaves := node.get_node("leaves") as GeometryInstance3D
	phases.append("%s %s turn %d scale %s phase %s" % [node.name, node.position, roundi(node.rotation_degrees.y), node.scale.x, snappedf(leaves.get_instance_shader_parameter("tree_phase"), 0.001)])
print("[game] GROVE ", "\\n".join(phases))
'''},
    *hour(0.5, 'grove_noon'),
    # The trunk is solid: walk the player at the first oak and see where it stops.
    {'op': 'eval', 'code': '''
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
player.global_position = Vector3(-2.5, 0.05, -3)
await tree.process_frame
Input.action_press("move_left")
'''},
    {'op': 'sleep', 'seconds': 1.6},
    {'op': 'eval', 'code': '''
Input.action_release("move_left")
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] WALK stopped at x ", snappedf(player.global_position.x, 0.01), " (trunk at -5, collision radius 0.35)")
'''},
    {'op': 'eval', 'code': '''
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
player.global_position = Vector3(0, 0.05, 0)
'''},
    {'op': 'wheel', 'steps': -6},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l28_grove_far', 'frames': 10},
    *hour(0.8, 'grove_dusk'),
    {'op': 'wheel', 'steps': 10},
    {'op': 'wait', 'frames': 40},
    *hour(0.5, 'grove_close'),
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code(SCRIPT, WIND_PHASE),
    *build(),
    # The tree scene: a trunk collision, and the script on its root.
    {'op': 'open', 'path': TREE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *add_node('StaticBody3D', 'Trunk'),
    *add_node('CollisionShape3D', 'TrunkShape', 'Trunk'),
    {'op': 'select', 'path': 'Trunk/TrunkShape'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *new_resource('shape', 'CylinderShape3D', nth=1),
    open_resource('shape', 'radius'),
    inspector_set('radius', '0.35'),
    inspector_set('height', '2.0'),
    inspector_set('position', 'Vector3(0, 1.0, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l28_trunk_shape', 'frames': 20},
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'WindPhase.cs'),
    {'op': 'wait', 'frames': 40},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] script ", root.get_script().resource_path if root.get_script() else "none", " shape ", (root.get_node("Trunk/TrunkShape") as CollisionShape3D).shape)
'''),
    {'op': 'capture', 'name': 'l28_tree_scene', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The grove.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
]
for index in range(1, len(GROVE)):
    steps += instantiate_under('Trees', 'tree_oak.tscn', capture='l28_select_scene' if index == 1 else None)
for name, position, yaw, scale in GROVE:
    steps += place(name, position, yaw, scale)
steps += [
    eval_('''
var trees := editor.get_edited_scene_root().get_node("Trees")
print("[probe] trees ", trees.get_children().map(func(n): return "%s %s %s" % [n.name, n.position, n.scale.x]))
'''),
    {'op': 'capture', 'name': 'l28_meadow_editor', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    *play(game, 70),
]
write(sys.argv[2], steps)
