# Probe: how far the tile mover walks along several lanes of the meadow before something solid stops it.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play, eval_

out_dir = os.path.dirname(sys.argv[2])


def lane(z):
    return [
        {'op': 'eval', 'code': f'tree.root.get_node("Meadow/Player").global_position = Vector3(8.5, 0.05, {z})'}, {'op': 'sleep', 'seconds': 0.3},
        {'op': 'eval', 'code': 'Input.action_press("move_left")'}, {'op': 'sleep', 'seconds': 4.5}, {'op': 'eval', 'code': 'Input.action_release("move_left")'},
        {'op': 'sleep', 'seconds': 0.4},
        {'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nprint("[game] LANE {z} stops at ", snappedf(player.global_position.x, 0.01), " ", snappedf(player.global_position.z, 0.01))'},
    ]


steps_list = [{'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4}]
for z in (5.5, 4.5, -3.5, -4.5, -5.5, 6.5):
    steps_list += lane(z)
steps_list += [{'op': 'quit'}]
game = game_steps(os.path.join(out_dir, 'game-l64.jsonl'), steps_list)
steps = [
    {'op': 'sleep', 'seconds': 5},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(game, 40),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
