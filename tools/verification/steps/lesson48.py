# Lesson 48, in Godot: the bank's collision. The kit is exported again with a box over each piece's water side, the importer turns
# the -convcolonly boxes into the library's shapes, and the character is walked into the pond from every side and the corners,
# without the shapes and with them.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play, click_tab

GLB = 'res://art/water/bank_kit.glb'
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

# The pond's three parts, as the water inside the walls: x min, x max, z min, z max, in meters.
WATER = [(-3.8, 0.3, -1.8, -0.7), (-2.8, -1.7, -0.7, 0.8), (0.7, 1.8, -0.3, 0.8)]
# Each test: its name, where the character starts, the keys held (W north, S south, A west, D east), and for how long: long enough
# to reach the middle of the water if nothing stops the character.
CASES = [
    ('north side', (-2.0, -3.0), ['S'], 0.6),
    ('south side', (-0.5, 0.8), ['W'], 0.7),
    ('west end', (-5.5, -1.5), ['D'], 1.0),
    ('east end', (0.9, -1.25), ['A'], 0.8),
    ('north east corner', (1.2, -2.6), ['A', 'S'], 0.8),
    ('inside corner', (-0.8, 0.3), ['A', 'W'], 0.6),
    ('lobe, south end', (-2.25, 2.0), ['W'], 0.6),
]

RECORD = '''
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
var at := player.global_position
# The character's middle may come within its radius, 0.3 meters, of a wall and no closer, give or take a little.
var inside := false
for part in {water!r}:
	if at.x > part[0] - 0.24 and at.x < part[1] + 0.24 and at.z > part[2] - 0.24 and at.z < part[3] + 0.24:
		inside = true
print("[game] {label}: {name} stopped at ", snappedf(at.x, 0.01), ", ", snappedf(at.z, 0.01), " IN THE WATER" if inside else " out")
'''


def tests(label):
    # Each test puts the character down, holds its keys for a moment, and records where it stopped.
    out = []
    for name, start, actions, hold in CASES:
        out += [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nplayer.global_position = Vector3({start[0]}, 0.05, {start[1]})\nplayer.velocity = Vector3.ZERO'},
                {'op': 'wait', 'frames': 20}]
        out += [{'op': 'key', 'key': action, 'pressed': True} for action in actions]
        out += [{'op': 'sleep', 'seconds': hold}]
        out += [{'op': 'key', 'key': action, 'pressed': False} for action in actions]
        out += [{'op': 'eval', 'code': RECORD.format(water=[list(part) for part in WATER], label=label, name=name)}, {'op': 'wait', 'frames': 10}]
    return out


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.05, {z})'},
            zoom(size), {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'l48_{name}', 'frames': 10}]


def run(prefix, steps):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
        *steps, {'op': 'quit'}])
    return play(game, 75 + 4 * len(CASES))


NO_SHAPES = {'op': 'eval', 'code': '''
var bank := tree.root.get_node("Meadow/Bank") as GridMap
var library := bank.mesh_library
for id in library.get_item_list():
	library.set_item_shapes(id, [])
print("[game] shapes cleared on ", library.get_item_list().size(), " items")
'''}

steps = [
    {'op': 'sleep', 'seconds': 3},
    # The kit was exported again from Blender: Godot imports it when its window gets the focus back.
    eval_('editor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 8},
    eval_(f'''
var library: MeshLibrary = load("{GLB}")
var out := []
for id in library.get_item_list():
	var shapes := library.get_item_shapes(id)
	var kinds := []
	for i in range(0, shapes.size(), 2):
		kinds.append(shapes[i].get_class())
	out.append("%s %s" % [library.get_item_name(id), kinds])
print("[probe] item shapes ", out)
'''),
    # Without the shapes: the character walks into the water.
    *run('l48_before', [NO_SHAPES, *tests('without'), *look('before', -1.25, -1.2, 6.0)]),
    # With them, and with Debug > Visible Collision Shapes on.
    {'op': 'menu', 'path': ['Debug', 'Visible Collision Shapes']},
    {'op': 'wait', 'frames': 20},
    *run('l48_after', [*tests('with'), *look('stopped', -1.25, -2.12, 6.0), *look('shapes', -1.25, -2.12, 2.6)]),
    {'op': 'menu', 'path': ['Debug', 'Visible Collision Shapes']},
    {'op': 'wait', 'frames': 20},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
