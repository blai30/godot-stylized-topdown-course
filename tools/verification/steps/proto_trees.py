# Prototype: the leaf-card oak in the meadow at noon, close, and at dusk, to judge the look in the real renderer.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'


def hour(time, name, wheel=0):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'proto_{name}', 'frames': 10}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': -wheel})
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-proto.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *hour(0.5, 'noon'), *hour(0.5, 'noon_close', 5), *hour(0.8, 'dusk_close', 5), *hour(0.5, 'noon_closer', 9), *hour(0.5, 'noon_max', 14), *hour(0.0, 'night_close', 5),
    {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 15}, *play(game, 40)]
write(sys.argv[2], steps)
