# Lesson 23, check: DayClock's rim values at the keyframe times, read back in the running game.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'
extra = []
for time in (0.0, 0.12, 0.15, 0.2, 0.27, 0.5, 0.73, 0.8, 0.85):
    extra += [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})\nprint("[game] rim at {time} ", clock.get("RimColor").to_html(false), " ", snappedf(clock.get("RimStrength"), 0.001))'},
              {'op': 'wait', 'frames': 5}]
path = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l23-rim.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 3},
    {'op': 'eval', 'code': f'tree.root.get_node("{CLOCK}").set("Running", false)'}, *extra, {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 3}, {'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(path, 20)]
write(sys.argv[2], steps)
