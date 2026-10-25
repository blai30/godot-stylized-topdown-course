import os
import sys
import tempfile
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play
game = game_steps(os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), 'sgt-phase1', 'game-look.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 6},
    {'op': 'capture', 'name': 'look_wide', 'frames': 10},
    {'op': 'wheel', 'steps': 4},
    {'op': 'capture', 'name': 'look_close', 'frames': 10},
    {'op': 'quit'},
])
steps = [{'op': 'sleep', 'seconds': 3}] + play(game, 25)
write(sys.argv[2], steps)
