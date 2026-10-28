# Lesson 52, in Godot: runtime, editor, and hand-painted areas together. The generator remembers the cells it painted, so a Generate
# takes those away and paints them again and leaves what was painted by hand; a Clear button empties the level; and the game can
# generate the level when it starts, with a new seed each run.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, click_tab, save_code, build, inspector_set, show_row, INSPECTOR)
from lesson52_pieces import SCATTER, GENERATOR, PIECES

GENERATED = 'res://levels/generated.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Generated/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

# What the reader paints by hand, over the generated ground: a lake of 8 by 6 cells in open meadow, and a dirt clearing of 12 by 12 cells
# where a grove stood.
LAKE = [[x, z] for x in range(8, 16) for z in range(14, 20)]
CLEARING = [[x, z] for x in range(8, 20) for z in range(-10, 2)]

PRESS_BUTTON = '''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for button in plugin._collect(dock, "Button", ""):
	if str(button.text) == "{text}":
		editor.get_inspector().ensure_control_visible(button)
		button.pressed.emit()
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		return ""
return "no {text} button"
'''

# A report of the level the editor has, or the game is running: how many cells of each kind, the trees, what was painted by hand, a
# signature of all of it, and the seed.
REPORT = '''
var root: Node = {root}
var ground := root.get_node("GroundTiles") as GridMap
var generator := root.get_node("WorldGenerator")
var counts := {{}}
var lines := []
for cell in ground.get_used_cells():
	counts[ground.get_cell_item(cell)] = counts.get(ground.get_cell_item(cell), 0) + 1
	lines.append("%d,%d,%d" % [cell.x, cell.z, ground.get_cell_item(cell)])
lines.sort()
var trees := []
for prop in root.get_node("Trees").get_children():
	trees.append("%s %.3f %.3f" % [prop.name, prop.position.x, prop.position.z])
trees.sort()
var lake_ok := true
for cell in {lake}:
	lake_ok = lake_ok and ground.get_cell_item(Vector3i(cell[0], 0, cell[1])) == 3
var clearing_ok := true
for cell in {clearing}:
	clearing_ok = clearing_ok and ground.get_cell_item(Vector3i(cell[0], 0, cell[1])) == 2
var trees_in_clearing := 0
for prop in root.get_node("Trees").get_children():
	if prop.position.x >= 4.0 and prop.position.x < 10.0 and prop.position.z >= -5.0 and prop.position.z < 1.0:
		trees_in_clearing += 1
print("[{tag}] seed ", generator.get("Profile").get("Seed"), " cells ", ground.get_used_cells().size(), " by item ", counts, " trees ", trees.size(), " painted ", generator.get("Painted").size(), " signature ", (",".join(lines) + "|" + ",".join(trees)).hash(), " lake kept ", lake_ok, " clearing kept ", clearing_ok, " trees in the clearing ", trees_in_clearing, " bank pieces ", root.get_node("Bank").get_used_cells().size())
'''


def report(root, tag):
    return REPORT.format(root=root, tag=tag, lake=LAKE, clearing=CLEARING)


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Generated/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size, time=0.5):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Generated/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'l52_{name}', 'frames': 10}]


def run_level(prefix, tag, shots):
    game = game_steps(os.path.join(out_dir, f'game-{prefix}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 5},
        {'op': 'eval', 'code': report('tree.root.get_node("Generated")', tag)},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *[step for shot in shots for step in look(*shot)],
        {'op': 'quit'}])
    steps = play(game, 45 + 12 * len(shots))
    for step in steps:
        if step.get('code') == 'editor.play_main_scene()':
            step['code'] = 'editor.play_current_scene()'
    return steps


def set_property(property, value):
    return [show_row(property), inspector_set(property, value), {'op': 'wait', 'frames': 20}]


steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code('res://src/Ground/GrassScatter.cs', SCATTER),
    save_code('res://src/Generation/WorldGenerator.cs', GENERATOR),
    *build('l52_built'),
    click_tab('Scene'),
    {'op': 'open', 'path': GENERATED},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'WorldGenerator'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l52_generator'},
    # The ground in the scene was painted by the generator of lesson 50, which kept no list: to this one it is all by hand.
    eval_(PRESS_BUTTON.format(text='Generate')),
    {'op': 'sleep', 'seconds': 3},
    eval_(report('editor.get_edited_scene_root()', 'before clear')),
    {'op': 'capture', 'name': 'l52_nothing'},
    # Clear: nothing is left.
    eval_(PRESS_BUTTON.format(text='Clear')),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'l52_cleared'},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] after Clear: ground ", (root.get_node("GroundTiles") as GridMap).get_used_cells().size(), " bank ", (root.get_node("Bank") as GridMap).get_used_cells().size(), " trees ", root.get_node("Trees").get_child_count(), " grass nodes ", root.get_node("Grass").get_child_count(), " painted ", root.get_node("WorldGenerator").get("Painted").size())
'''),
    # Generate on the empty ground: the generator lists what it paints.
    eval_(PRESS_BUTTON.format(text='Generate')),
    {'op': 'sleep', 'seconds': 4},
    eval_(report('editor.get_edited_scene_root()', 'first generate')),
    {'op': 'capture', 'name': 'l52_first'},
    # Paint a lake and a dirt clearing by hand, over the generated ground.
    eval_(f'''
var ground := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
for cell in {LAKE!r}:
	ground.set_cell_item(Vector3i(cell[0], 0, cell[1]), 3)
for cell in {CLEARING!r}:
	ground.set_cell_item(Vector3i(cell[0], 0, cell[1]), 2)
print("[probe] painted by hand: ", {len(LAKE) + len(CLEARING)}, " cells")
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l52_painted'},
    eval_(PRESS_BUTTON.format(text='Generate')),
    {'op': 'sleep', 'seconds': 4},
    eval_(report('editor.get_edited_scene_root()', 'generated')),
    {'op': 'capture', 'name': 'l52_generated'},
    eval_('''
var root := editor.get_edited_scene_root()
var generator := root.get_node("WorldGenerator")
var profile: Resource = generator.get("Profile")
var signature := func() -> int:
	var ground := root.get_node("GroundTiles") as GridMap
	var lines := []
	for cell in ground.get_used_cells():
		lines.append("%d,%d,%d" % [cell.x, cell.z, ground.get_cell_item(cell)])
	lines.sort()
	var trees := []
	for tree in root.get_node("Trees").get_children():
		trees.append("%s %.3f %.3f" % [tree.name, tree.position.x, tree.position.z])
	trees.sort()
	return (",".join(lines) + "|" + ",".join(trees)).hash()
var first: int = signature.call()
generator.call("Generate")
print("[probe] second Generate identical ", signature.call() == first)
profile.set("Seed", 16)
generator.call("Generate")
var other: int = signature.call()
print("[probe] seed 16 differs ", other != first)
var ground := root.get_node("GroundTiles") as GridMap
var kept := true
for cell in {lake}:
	kept = kept and ground.get_cell_item(Vector3i(cell[0], 0, cell[1])) == 3
for cell in {clearing}:
	kept = kept and ground.get_cell_item(Vector3i(cell[0], 0, cell[1])) == 2
print("[probe] seed 16: the hand-painted cells are kept ", kept, " painted ", generator.get("Painted").size())
profile.set("Seed", 15)
generator.call("Generate")
print("[probe] seed 15 again identical ", signature.call() == first)
'''.replace('{lake}', repr(LAKE)).replace('{clearing}', repr(CLEARING))),
    {'op': 'select', 'path': 'WorldGenerator'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    # The baked level, run as it is.
    *run_level('l52_baked', 'baked game', [('hand', 7.0, 3.0, 24.0), ('wide', 0.0, 0.0, 60.0)]),
    # Generate on ready, with the saved seed: the same level.
    {'op': 'select', 'path': 'WorldGenerator'},
    unfold_inspector(),
    *set_property('GenerateOnReady', 'true'),
    {'op': 'capture', 'name': 'l52_on_ready'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    *run_level('l52_ready', 'ready game', [('ready', 0.0, 0.0, 60.0)]),
    # And a new seed each run.
    *set_property('NewSeedEachRun', 'true'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    *run_level('l52_new_a', 'new seed game a', [('new_a', 0.0, 0.0, 60.0), ('new_a_hand', 7.0, 3.0, 24.0)]),
    *run_level('l52_new_b', 'new seed game b', [('new_b', 0.0, 0.0, 60.0)]),
    # Back to the baked level: the saved scene is what the game runs.
    *set_property('NewSeedEachRun', 'false'),
    *set_property('GenerateOnReady', 'false'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 60},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
