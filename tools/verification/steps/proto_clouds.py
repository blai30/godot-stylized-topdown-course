# Prototype: cloud shadows through shader globals, and a bush made from the oak's leaves, to judge the look before any lesson is written.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'
PREFIX = 'protoc'

BUSHES = '''
var meadow := tree.root.get_node("Meadow")
var scene: PackedScene = load("res://art/nature/tree_oak/tree_oak.tscn")
var spots := [Vector3(-3.0, 0.0, 6.0), Vector3(-1.0, 0.0, 7.0), Vector3(0.5, 0.0, 6.2)]
var scales := [0.5, 0.4, 0.45]
for i in 3:
	var bush: Node3D = scene.instantiate()
	bush.get_node("tree_oak").visible = false
	bush.get_node("Trunk").free()
	var s: float = scales[i]
	bush.scale = Vector3(s * 1.2, s * 0.8, s * 1.2)
	bush.rotation.y = i * 2.1
	meadow.add_child(bush)
	var leaves: MeshInstance3D = bush.get_node("leaves")
	var box: AABB = leaves.global_transform * leaves.get_aabb()
	bush.position = spots[i] + Vector3(0.0, -box.position.y, 0.0)
	print("[proto] bush %s box %s" % [i, box])
tree.root.get_node("Meadow/Player").global_position = Vector3(-1.0, 0.0, 10.0)
'''


def strength(value):
    return {'op': 'eval', 'code': f'RenderingServer.global_shader_parameter_set("cloud_strength", {value})'}


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def shot(name, size, value, time=0.5):
    return [{'op': 'eval', 'code': f'tree.root.get_node("{CLOCK}").set("TimeOfDay", {time})'}, strength(value), zoom(size),
            {'op': 'wait', 'frames': 70}, {'op': 'capture', 'name': f'{PREFIX}_{name}', 'frames': 10}]


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-protoc.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    eval_(BUSHES),
    {'op': 'eval', 'code': f'tree.root.get_node("{CLOCK}").set("Running", false)'},
    {'op': 'wait', 'frames': 60},
    *shot('mid_off', 20.0, 0.0), *shot('mid_on', 20.0, 0.4), *shot('mid_full', 20.0, 1.0),
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(-3.0, 0.0, -2.0)'},
    *shot('far_off', 20.0, 0.0), *shot('far_on', 20.0, 0.4), *shot('dusk', 20.0, 0.4, 0.75),
    {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 15}, *play(game, 120, capture_output='protoc_output')]
write(sys.argv[2], steps)
