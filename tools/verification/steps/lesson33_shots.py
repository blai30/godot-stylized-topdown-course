# Retakes lesson 33's before and after pair from its snapshot: the capsule is hidden so the grass at its feet shows, once with the
# push radius at 0 and once at its default. The wind is off so only the push differs.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'
POINT = 'tree.root.get_node("Meadow/Player/PushPoint")'
out_dir = os.path.dirname(sys.argv[2])

game = game_steps(os.path.join(out_dir, 'game-l33-pair.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)\nclock.set("Running", false)'},
    {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nplayer.global_position = Vector3(0.0, 0.05, 0.0)\nplayer.visible = false'},
    {'op': 'eval', 'code': 'RenderingServer.global_shader_parameter_set("wind_strength", 0.0)'},
    {'op': 'wheel', 'steps': 25}, {'op': 'wait', 'frames': 60},
    {'op': 'eval', 'code': f'var point := {POINT}\nprint("[game] radius ", point.get("Radius"))\npoint.set("Radius", 0.0)'},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l33p_before', 'frames': 10},
    {'op': 'eval', 'code': f'var point := {POINT}\npoint.set("Radius", 0.6)'},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l33p_after', 'frames': 10},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'main_screen', 'name': '3D'},
    *play(game, 60),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
