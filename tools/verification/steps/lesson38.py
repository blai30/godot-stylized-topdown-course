# Lesson 38, in Godot: a check that the texture and UVs agree. The character in the meadow with a plain material that holds
# the painted texture (lesson 41 gives it the course's shader), at noon, close, and a close-up of the head.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l38.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'tree.root.get_node("{CLOCK}").set("Running", false)\ntree.root.get_node("{CLOCK}").set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': '''
var player := tree.root.get_node("Meadow/Player")
player.get_node("Body").visible = false
player.get_node("Nose").visible = false
var model: Node3D = load("res://art/character/character.glb").instantiate()
player.add_child(model)
var material := StandardMaterial3D.new()
material.albedo_texture = load("res://art/character/character_texture.png")
material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
material.roughness = 1.0
for mesh in model.find_children("*", "MeshInstance3D", true, false):
	mesh.material_override = material
	print("[game] MESH ", mesh.name, " surfaces ", mesh.mesh.get_surface_count(), " uv ", mesh.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV] != null)
'''},
    {'op': 'wheel', 'steps': 8}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l38_meadow', 'frames': 10},
    {'op': 'wheel', 'steps': 8}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l38_close', 'frames': 10},
    {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player")\nplayer.rotation.y = PI * 0.75'},
    {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l38_turned', 'frames': 10},
    {'op': 'quit'}])
write(sys.argv[2], [{'op': 'sleep', 'seconds': 14}, {'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(game, 50)])
