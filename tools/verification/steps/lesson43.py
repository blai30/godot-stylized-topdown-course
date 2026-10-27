# Lesson 43, in Godot: an AnimationTree with a BlendSpace1D on speed on the character, a short script that feeds it the body's
# speed, and the player walking the meadow: idle, walk, and run, with the planted foot's slide measured.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, save_code, build, add_node, unfold_inspector, quick_load, game_steps, play, click_tab)
from lesson43_pieces import PLAYER_ANIMATION, POINTS

SCRIPT = 'res://src/Player/PlayerAnimation.cs'
PIECES = [PLAYER_ANIMATION]
out_dir = os.path.dirname(sys.argv[2])

BUILD_TREE = '''
var root := editor.get_edited_scene_root()
var tree := root.get_node("AnimationTree") as AnimationTree
var space := AnimationNodeBlendSpace1D.new()
space.min_space = 0.0
space.max_space = 6.0
space.sync = true
for point in POINTS:
	var node := AnimationNodeAnimation.new()
	node.animation = point[0]
	if point[2] != null:
		node.use_custom_timeline = true
		node.timeline_length = point[2]
		node.loop_mode = Animation.LOOP_LINEAR
	space.add_blend_point(node, point[1])
tree.tree_root = space
tree.anim_player = NodePath("../AnimationPlayer")
tree.active = false
(root.find_child("GeneralSkeleton", true, false) as Skeleton3D).reset_bone_poses()
print("[probe] blend points ", space.get_blend_point_count())
'''


def measure(speed):
    # The planted foot's slide: while the left foot is on the ground, its speed in the world is the body's speed plus the foot's
    # speed along the body, which is negative (backward) when the foot is planted. Zero means no slide. Windows of six frames
    # average out the uneven frame times.
    return {'op': 'eval', 'code': f'''
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
var skeleton := player.find_child("GeneralSkeleton", true, false) as Skeleton3D
var foot: int = skeleton.find_bone("LeftFoot")
var along: Array = []
var heights: Array = []
var times: Array = []
for frame in 90:
	await tree.process_frame
	var pose: Vector3 = skeleton.get_bone_global_pose(foot).origin
	along.append(pose.z)
	heights.append(pose.y)
	times.append(Time.get_ticks_usec() / 1000000.0)
var lowest: float = heights[0]
for value in heights:
	lowest = minf(lowest, value)
var count := 0
var total := 0.0
for i in 84:
	if heights[i] < lowest + 0.12 and heights[i + 6] < lowest + 0.12:
		total += player.velocity.length() + (along[i + 6] - along[i]) / (times[i + 6] - times[i])
		count += 1
print("[game] SLIDE target {speed} body ", player.velocity.length(), " planted windows ", count, " mean slide ", total / maxf(count, 1.0))
'''.strip()}


game = game_steps(os.path.join(out_dir, 'game-l43.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': 'var clock := tree.root.get_node("Meadow/WorldEnvironment/Day")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nplayer.global_position = Vector3(-2.5, 0.05, 0.5)\nprint("[game] TREE ", player.find_child("AnimationTree", true, false).get("parameters/blend_position"))'},
    {'op': 'wheel', 'steps': 12}, {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l43_idle', 'frames': 5},
    {'op': 'eval', 'code': 'Input.action_press("move_right")'},
    {'op': 'sleep', 'seconds': 0.4},
    {'op': 'capture', 'name': 'l43_walk_0', 'frames': 2}, {'op': 'sleep', 'seconds': 0.15}, {'op': 'capture', 'name': 'l43_walk_1', 'frames': 2},
    {'op': 'eval', 'code': 'print("[game] BLEND walking ", tree.root.get_node("Meadow/Player").find_child("AnimationTree", true, false).get("parameters/blend_position"))'},
    measure(3.5),
    {'op': 'eval', 'code': 'Input.action_release("move_right")\ntree.root.get_node("Meadow/Player").global_position = Vector3(5.5, 0.05, 0.5)\nInput.action_press("move_left")\nInput.action_press("sprint")'},
    {'op': 'sleep', 'seconds': 0.4},
    {'op': 'capture', 'name': 'l43_run_0', 'frames': 2}, {'op': 'sleep', 'seconds': 0.15}, {'op': 'capture', 'name': 'l43_run_1', 'frames': 2},
    {'op': 'eval', 'code': 'print("[game] BLEND running ", tree.root.get_node("Meadow/Player").find_child("AnimationTree", true, false).get("parameters/blend_position"))'},
    measure(6.0),
    {'op': 'eval', 'code': 'Input.action_release("sprint")\nInput.action_release("move_left")'},
    {'op': 'sleep', 'seconds': 1.0},
    {'op': 'eval', 'code': 'print("[game] BLEND stopped ", tree.root.get_node("Meadow/Player").find_child("AnimationTree", true, false).get("parameters/blend_position"))'},
    {'op': 'capture', 'name': 'l43_stopped', 'frames': 5},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 15},
    save_code(SCRIPT, PLAYER_ANIMATION),
    *build(),
    click_tab('Scene'),
    {'op': 'open', 'path': 'res://art/character/character.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': '.'},
    *add_node('AnimationTree', 'AnimationTree'),
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'AnimationTree'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'PlayerAnimation.cs'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l43_tree_added', 'frames': 20},
    eval_('var POINTS = ' + repr([list(point) for point in POINTS]).replace('None', 'null') + BUILD_TREE),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l43_tree_root', 'frames': 20},
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(game, 60),
]
write(sys.argv[2], steps)
