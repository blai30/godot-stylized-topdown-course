import os, sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-pp.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(0.5, 0.05, 1.2)'},
    {'op': 'wheel', 'steps': 6}, {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': 'pp_noon', 'frames': 10},
    {'op': 'quit'}])
write(sys.argv[2], [{'op': 'sleep', 'seconds': 10}, {'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(game, 35)])
