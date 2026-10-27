# Probes why the flat water does not show in the running game.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-p45.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 3},
    {'op': 'eval', 'code': '''
var water := tree.root.get_node("Meadow/Water") as MeshInstance3D
print("[game] water ", water.position, " visible ", water.visible, " mesh ", water.mesh, " material ", water.mesh.material, " shader ", water.mesh.material.shader.code.left(60) if water.mesh.material else "none", " aabb ", water.get_aabb())
print("[game] global ", water.global_position, " layers ", water.layers, " transparency ", water.transparency)
'''},
    {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3(-0.25, 0.0, -1.25)\nplayer.visible = false\ntree.root.get_node("Meadow/CameraRig").get("Camera").size = 3.2'},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'p45_a', 'frames': 5},
    {'op': 'eval', 'code': 'var water := tree.root.get_node("Meadow/Water") as MeshInstance3D\nvar material := StandardMaterial3D.new()\nmaterial.albedo_color = Color(1, 0, 0)\nwater.material_override = material'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'p45_b', 'frames': 5},
    {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 3}, *play(game, 40)]
write(sys.argv[2], steps)
