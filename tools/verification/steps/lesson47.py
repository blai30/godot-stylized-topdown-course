# Lesson 47, in Godot: Update shore. GroundMap learns what is water, a BankMap script on the Bank GridMap places the pieces at
# every corner of the pond, its table is tested against all 16 cases, a bigger pond is painted and edged with one button press,
# and a second press changes nothing.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, click_tab, save_code, build, INSPECTOR)
from lesson47_pieces import GROUND_MAP, BANK_MAP, PIECES

GROUND = 'res://src/Ground/GroundMap.cs'
BANK = 'res://src/Ground/BankMap.cs'
MEADOW = 'res://levels/meadow.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

# The pieces and turns the table must give for each set of water cells around a corner, from an independent computation.
CANON = [('bank_straight', [(0, 1), (1, 1)]), ('bank_water_corner', [(1, 1)]), ('bank_land_corner', [(0, 1), (1, 0), (1, 1)]),
         ('bank_diagonal', [(0, 1), (1, 0)])]
EXPECTED = {}
for prefix, water in CANON:
    for turns in range(4):
        mask = 0
        for x, z in water:
            for _ in range(turns):
                x, z = z, 1 - x
            mask |= 1 << (x * 2 + z)
        EXPECTED.setdefault(mask, [prefix, turns])
assert len(EXPECTED) == 14

# The bigger pond: a long arm, a lobe off it, and a second pond that touches the arm at a corner.
ARM = [[x, z] for x in range(-8, 1) for z in range(-4, -1)]
LOBE = [[x, z] for x in range(-6, -3) for z in range(-1, 2)]
SECOND = [[x, z] for x in range(1, 4) for z in range(-1, 2)]
VIEW = (-2.5, -1.0)

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


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size, time=0.5):
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'l47_{name}', 'frames': 10}]


game = game_steps(os.path.join(out_dir, 'game-l47.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *look('pond', *VIEW, 8.0), *look('close', -3.2, -1.6, 2.6), *look('diagonal', 0.5, -1.2, 2.2), *look('dusk', *VIEW, 6.0, 0.78),
    {'op': 'quit'}])

TABLE_TEST = f'''
var library: MeshLibrary = load("res://art/water/bank_kit.glb")
var ground := GridMap.new()
ground.set_script(load("res://src/Ground/GroundMap.cs"))
ground.mesh_library = load("res://art/ground/ground_tiles.meshlib")
ground.cell_size = Vector3(0.5, 0.5, 0.5)
ground.set("Tiles", load("res://art/ground/ground_tile_set.tres"))
var bank := GridMap.new()
bank.set_script(load("res://src/Ground/BankMap.cs"))
bank.mesh_library = library
bank.cell_size = Vector3(0.5, 0.5, 0.5)
bank.set("Ground", ground)
var expected := {EXPECTED!r}
# Every set of water cells around a corner, each in a block of its own: land everywhere, and the pattern around the block's middle corner.
for k in 16:
	var origin := Vector2i((k % 4) * 6, (k / 4) * 6)
	for x in 5:
		for z in 5:
			ground.set_cell_item(Vector3i(origin.x + x, 0, origin.y + z), 0)
	for qx in 2:
		for qz in 2:
			if k & (1 << (qx * 2 + qz)):
				ground.set_cell_item(Vector3i(origin.x + 1 + qx, 0, origin.y + 1 + qz), 3)
bank.call("UpdateShore")
var wrong := []
var checked := 0
for k in 16:
	var corner := Vector3i((k % 4) * 6 + 2, 0, (k / 4) * 6 + 2)
	var item := bank.get_cell_item(corner)
	if not expected.has(k):
		if item != GridMap.INVALID_CELL_ITEM:
			wrong.append("%d placed %s" % [k, bank.mesh_library.get_item_name(item)])
		checked += 1
		continue
	var name := bank.mesh_library.get_item_name(item) if item != GridMap.INVALID_CELL_ITEM else "nothing"
	var orientation := bank.get_cell_item_orientation(corner)
	var wanted := bank.get_orthogonal_index_from_basis(Basis(Vector3.UP, expected[k][1] * PI / 2.0))
	if not name.begins_with(expected[k][0]) or orientation != wanted:
		wrong.append("%d expected %s turn %d, got %s orientation %d (wanted %d)" % [k, expected[k][0], expected[k][1], name, orientation, wanted])
	checked += 1
print("[probe] table test: ", checked, " cases, wrong ", wrong, " pieces ", bank.get_used_cells().size())
'''

NARROW_TEST = '''
var ground := GridMap.new()
ground.set_script(load("res://src/Ground/GroundMap.cs"))
ground.mesh_library = load("res://art/ground/ground_tiles.meshlib")
ground.cell_size = Vector3(0.5, 0.5, 0.5)
ground.set("Tiles", load("res://art/ground/ground_tile_set.tres"))
var bank := GridMap.new()
bank.set_script(load("res://src/Ground/BankMap.cs"))
bank.mesh_library = load("res://art/water/bank_kit.glb")
bank.cell_size = Vector3(0.5, 0.5, 0.5)
bank.set("Ground", ground)
for x in 12:
	for z in 7:
		ground.set_cell_item(Vector3i(x, 0, z), 0)
# A channel one cell wide, and a lake three cells wide.
for x in 12:
	ground.set_cell_item(Vector3i(x, 0, 1), 3)
for x in range(2, 9):
	for z in range(3, 6):
		ground.set_cell_item(Vector3i(x, 0, z), 3)
bank.call("UpdateShore")
print("[probe] narrow test pieces ", bank.get_used_cells().size())
'''

steps = [
    {'op': 'sleep', 'seconds': 3},
    save_code(GROUND, GROUND_MAP),
    save_code(BANK, BANK_MAP),
    *build('l47_built'),
    eval_('''
var names := []
for entry in ProjectSettings.get_global_class_list():
	names.append(entry["class"])
print("[probe] global classes ", names)
'''),
    # The script on the Bank node, and its ground.
    click_tab('Scene'),
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'Bank'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'BankMap.cs'),
    {'op': 'wait', 'frames': 60},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'Ground', 'type': 'Button', 'text': 'Assign...'}},
    {'op': 'wait', 'frames': 40},
    {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': 'GroundTiles'},
    {'op': 'capture', 'name': 'l47_select_ground', 'window': 'Select a Node'},
    {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l47_bank_map'},
    eval_('''
var bank := editor.get_edited_scene_root().get_node("Bank")
print("[probe] bank script ", bank.get_script().resource_path if bank.get_script() else "none", " ground ", bank.get("Ground"))
'''),
    # The table against all sixteen cases, on a ground of its own.
    eval_(TABLE_TEST),
    eval_(NARROW_TEST),
    # The hand-placed pond of lesson 44, then the button: the same shapes and turns, and a second press changes nothing.
    eval_('''
var bank := editor.get_edited_scene_root().get_node("Bank") as GridMap
var by_hand := {}
for cell in bank.get_used_cells():
	by_hand[cell] = [bank.mesh_library.get_item_name(bank.get_cell_item(cell)).rsplit("_", true, 1)[0], bank.get_cell_item_orientation(cell)]
bank.call("UpdateShore")
var after := {}
for cell in bank.get_used_cells():
	after[cell] = [bank.mesh_library.get_item_name(bank.get_cell_item(cell)).rsplit("_", true, 1)[0], bank.get_cell_item_orientation(cell)]
var same := by_hand.size() == after.size()
for cell in by_hand:
	same = same and after.has(cell) and after[cell] == by_hand[cell]
print("[probe] lesson 44 pond, by hand ", by_hand.size(), " pieces, by code ", after.size(), ", same shapes and turns ", same)
var first := {}
for cell in bank.get_used_cells():
	first[cell] = [bank.get_cell_item(cell), bank.get_cell_item_orientation(cell)]
bank.call("UpdateShore")
var again := {}
for cell in bank.get_used_cells():
	again[cell] = [bank.get_cell_item(cell), bank.get_cell_item_orientation(cell)]
print("[probe] second press identical ", first == again, " ", first.size(), " pieces")
'''),
    # A bigger pond: an arm, a lobe, and a second pond that touches it at a corner.
    eval_(f'''
var ground := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
for cell in {ARM + LOBE + SECOND!r}:
	ground.set_cell_item(Vector3i(cell[0], 0, cell[1]), 3)
print("[probe] water cells ", ground.get_used_cells_by_item(3).size())
'''),
    {'op': 'select', 'path': 'Bank'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_(PRESS_BUTTON.format(text='Update shore')),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l47_updated'},
    eval_('''
var bank := editor.get_edited_scene_root().get_node("Bank") as GridMap
var counts := {}
for cell in bank.get_used_cells():
	var name := bank.mesh_library.get_item_name(bank.get_cell_item(cell)).rsplit("_", true, 1)[0]
	counts[name] = counts.get(name, 0) + 1
print("[probe] pieces by kind ", counts, " total ", bank.get_used_cells().size())
var first := {}
for cell in bank.get_used_cells():
	first[cell] = [bank.get_cell_item(cell), bank.get_cell_item_orientation(cell)]
bank.call("UpdateShore")
var again := {}
for cell in bank.get_used_cells():
	again[cell] = [bank.get_cell_item(cell), bank.get_cell_item_orientation(cell)]
print("[probe] big pond second press identical ", first == again)
'''),
    {'op': 'select', 'path': 'Grass'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_(PRESS_BUTTON.format(text='Scatter')),
    {'op': 'sleep', 'seconds': 2},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *play(game, 90, capture_output='l47_output'),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
