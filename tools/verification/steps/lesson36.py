# Lesson 36, in Godot: the blockout beside the capsule in the meadow, to judge its scale, in the running game at noon and
# close up. The scene is not saved: the blockout is only a check.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, inspector_set, unfold_inspector, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])


def hour(time, name, wheel=0):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l36_{name}', 'frames': 10}]
    return steps


game = game_steps(os.path.join(out_dir, 'game-l36.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    {'op': 'eval', 'code': '''
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
player.global_position = Vector3(0, 0.05, 0)
var blockout := tree.root.get_node("Meadow/CharacterBlockout") as Node3D
var box := AABB()
var first := true
for mesh in blockout.find_children("*", "MeshInstance3D", true, false):
	var part: AABB = mesh.global_transform * mesh.get_aabb()
	box = part if first else box.merge(part)
	first = false
print("[game] BLOCKOUT bounds ", box.position, " size ", box.size, " capsule height 1.8")
'''},
    *hour(0.5, 'noon_close', 8),
    {'op': 'wheel', 'steps': -6}, *hour(0.5, 'noon'),
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 12},
    {'op': 'fs', 'path': 'res://art/character/character_blockout.glb'},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    # Dragging the .glb from the FileSystem dock into the viewport instantiates it under the scene's root.
    eval_('''
var root := editor.get_edited_scene_root()
var node: Node = (load("res://art/character/character_blockout.glb") as PackedScene).instantiate()
root.add_child(node)
node.owner = root
node.name = "CharacterBlockout"
'''),
    eval_('''
var root := editor.get_edited_scene_root()
var node := root.get_node("CharacterBlockout")
print("[probe] instanced ", node.name, " ", node.get_class(), " children ", node.get_children().map(func(n): return n.name + " " + n.get_class()), " scene ", node.scene_file_path)
editor.get_selection().clear()
editor.get_selection().add_node(node)
'''),
    {'op': 'wait', 'frames': 20},
    unfold_inspector(),
    inspector_set('position', 'Vector3(0.9, 0, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l36_meadow_editor', 'frames': 20},
    *play(game, 50),
    # Running the game saved the scene with the blockout in it; take it out again, so the meadow is as it was.
    eval_('''
var root := editor.get_edited_scene_root()
var node := root.get_node("CharacterBlockout")
root.remove_child(node)
node.free()
'''),
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
]
write(sys.argv[2], steps)
