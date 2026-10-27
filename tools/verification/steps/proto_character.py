import os, sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])
def shot(name, time):
    return [{'op': 'eval', 'code': f'tree.root.get_node("{CLOCK}").set("TimeOfDay", {time})'}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': name, 'frames': 10}]
game = game_steps(os.path.join(out_dir, 'game-pc.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'tree.root.get_node("{CLOCK}").set("Running", false)'},
    {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player")\nplayer.get_node("Body").visible = false\nplayer.get_node("Nose").visible = false\nvar model = load("res://art/character/character.glb").instantiate()\nplayer.add_child(model)\nplayer.global_position = Vector3(0.5, 0.05, 1.2)'},
    {'op': 'wheel', 'steps': 6},
    *shot('pc_noon', 0.5), *shot('pc_dusk', 0.8),
    {'op': 'wheel', 'steps': -4}, *shot('pc_mid', 0.5),
    {'op': 'quit'}])
write(sys.argv[2], [{'op': 'sleep', 'seconds': 14}, {'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(game, 45)])
