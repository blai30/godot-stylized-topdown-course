# Shows the bank's top edge with the new turf, at the pond close and mid, noon and dusk.
import os, sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play
out_dir = os.path.dirname(sys.argv[2])
CLOCK = 'Meadow/WorldEnvironment/Day'
def look(name, x, z, size, time=0.5):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'},
            {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'p49_{name}', 'frames': 10}]
game = game_steps(os.path.join(out_dir, 'game-p49.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *look('close', -3.2, -1.6, 2.6), *look('mid', -2.5, -1.0, 6.0), *look('dusk', -3.2, -1.6, 2.6, 0.78), {'op': 'quit'}])
write(sys.argv[2], [{'op': 'sleep', 'seconds': 5}, *play(game, 70)])
