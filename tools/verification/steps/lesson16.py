# Lesson 16: three half-meter ground tiles (grass, dirt, sand) in a tiles scene, exported as a MeshLibrary, and a GridMap in
# the meadow painted with them: grass filled over the area, a dirt path painted, a sand patch filled.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, resource_menu, press_delete_in_scene_dock, open_in_file_dialog, inspector_set, unfold_inspector, show_row, quick_load, dump_popups, add_node,
                   game_steps, play, INSPECTOR)

TEXTURE = 'shader_parameter/albedo_texture'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
VIEWPORT = {'type': 'Node3DEditorViewport'}


def gridmap_tool(shortcut):
    # Clicks the GridMap toolbar button whose shortcut is this key: Q select, W erase, E paint, Z fill.
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "GridMapEditor")
for control in plugin._collect(panel, "Button", ""):
	if control.shortcut and control.shortcut.get_as_text().begins_with("{shortcut} "):
		if control.toggle_mode:
			control.button_pressed = true
		control.pressed.emit()
		return ""
return "no GridMap button {shortcut}"
''')


def palette_pick(name):
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "GridMapEditor")
var list: ItemList = plugin._collect(panel, "ItemList", "")[0]
for i in list.item_count:
	if list.get_item_text(i) == "{name}":
		list.select(i)
		list.item_selected.emit(i)
		return ""
return "no {name} in the GridMap palette"
''')


steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    # Copy TestTile, then delete both test tiles.
    {'op': 'select', 'path': 'TestTile'},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'C', 'ctrl': True},
    {'op': 'wait', 'frames': 10},
    eval_('''
var root := editor.get_edited_scene_root()
editor.get_selection().clear()
editor.get_selection().add_node(root.get_node("TestTile"))
editor.get_selection().add_node(root.get_node("TestTile2"))
'''),
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l16_delete_confirm', 'window': 'class:ConfirmationDialog'},
    {'op': 'press', 'find': {'type': 'Button', 'text': 'Delete'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var root := editor.get_edited_scene_root()
if root.get_node_or_null("TestTile") or root.get_node_or_null("TestTile2"):
	return "the test tiles are still there"
'''),
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 20},
    # A new scene for the tiles: Scene > New Scene, a 3D Scene root named GroundTiles, TestTile pasted under it.
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "SceneTreeDock")
for button in plugin._collect(dock, "Button", ""):
	if button.text == "3D Scene":
		button.pressed.emit()
		return ""
return "no 3D Scene button"
'''),
    {'op': 'wait', 'frames': 20},
    eval_('editor.get_edited_scene_root().name = "GroundTiles"'),
    {'op': 'select', 'path': '.'},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'V', 'ctrl': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root()
var tile := root.get_node_or_null("TestTile")
if tile == null:
	return "TestTile was not pasted: " + str(root.get_children())
tile.name = "Grass"
'''),
    {'op': 'select', 'path': 'Grass'},
    inspector_set('position', 'Vector3(0, 0, 0)'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    # Click the mesh's picture in the Inspector to open the PlaneMesh's own properties below it.
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "mesh")
if row == null:
	return "no mesh row"
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
var main: Button = plugin._collect(picker, "Button", "")[0]
main.pressed.emit()
for attempt in 20:
	await plugin.get_tree().process_frame
	if plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "size") != null:
		return ""
return "the PlaneMesh did not open in the Inspector"
'''),
    {'op': 'wait', 'frames': 10},
    inspector_set('size', 'Vector2(0.5, 0.5)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l16_grass_tile', 'frames': 20},
]
# Dirt and sand: duplicate, then make the mesh and its material unique, and load each texture.
for name, texture in (('Dirt', 'dirt_albedo'), ('Sand', 'sand_albedo')):
    steps += [
        {'op': 'select', 'path': 'Grass'},
        {'op': 'key', 'find': SCENE_TREE, 'key': 'D', 'ctrl': True},
        {'op': 'wait', 'frames': 20},
        eval_(f'''
var root := editor.get_edited_scene_root()
var copy := root.get_node_or_null("Grass2")
if copy == null:
	return "Ctrl+D made no Grass2: " + str(root.get_children())
copy.name = "{name}"
'''),
        {'op': 'select', 'path': name},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        resource_menu('mesh', 'Make Unique'),
        {'op': 'wait', 'frames': 20},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        resource_menu('material', 'Make Unique'),
        {'op': 'wait', 'frames': 20},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
    ]
    if name == 'Dirt':
        steps += [eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window is PopupMenu:
		window.hide()
'''), {'op': 'select', 'path': 'Dirt'}, unfold_inspector(), {'op': 'wait', 'frames': 10}, show_row('material'),
                  {'op': 'capture', 'name': 'l16_make_unique', 'frames': 20}]
    steps += quick_load(TEXTURE, texture)
    # The copy still carries the grass tint; dirt and sand are painted in their own colors, so their tint is white.
    steps += [inspector_set('shader_parameter/albedo_tint', 'Color(1, 1, 1)')]
    steps += [
        inspector_set('position', 'Vector3(%d, 0, 0)' % (1 if name == 'Dirt' else 2)),
        {'op': 'wait', 'frames': 20},
    ]
steps += [
    eval_('''
var root := editor.get_edited_scene_root()
var out := []
for name in ["Grass", "Dirt", "Sand"]:
	var tile := root.get_node(name) as MeshInstance3D
	var mesh := tile.mesh as PlaneMesh
	var material := mesh.material as ShaderMaterial
	out.append("%s size %s texture %s" % [name, mesh.size, material.get_shader_parameter("albedo_texture").resource_path])
print("[probe] tiles ", out)
var grass := (root.get_node("Grass") as MeshInstance3D).mesh
var dirt := (root.get_node("Dirt") as MeshInstance3D).mesh
if grass == dirt or (grass as PlaneMesh).material == (dirt as PlaneMesh).material:
	return "Dirt still shares the grass mesh or material"
'''),
    {'op': 'select', 'path': '.'},
    {'op': 'capture', 'name': 'l16_tiles_scene', 'frames': 30},
    # Save the scene in art/ground.
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
    open_in_file_dialog('art', 'ground'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l16_save_tiles', 'window': 'Save Scene'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
return "no Save Scene dialog"
'''),
    {'op': 'wait', 'frames': 40},
    # Scene > Export As > MeshLibrary..., into art/ground.
    {'op': 'menu', 'path': ['Scene', 'Export As...', 'MeshLibrary...']},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is FileDialog:
		print("[probe] export dialog at ", window.current_dir, " file ", window.current_file)
		window.current_dir = "res://art/ground"
		window.current_file = "ground_tiles.meshlib"
		return ""
return "no Export Mesh Library dialog"
'''),
    {'op': 'capture', 'name': 'l16_export', 'window': 'Export Mesh Library'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is FileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
var library := load("res://art/ground/ground_tiles.meshlib") as MeshLibrary
var out := []
for id in library.get_item_list():
	out.append("%d %s %s" % [id, library.get_item_name(id), library.get_item_mesh(id)])
print("[probe] mesh library ", out)
if library.get_item_list().size() != 3:
	return "the library does not hold three tiles"
'''),
    # The meadow: hide the placeholder ground, add a GridMap with the library, half-meter cells, tiles at y 0.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "SceneTreeDock")
var tree: Tree = plugin._collect(dock, "Tree", "")[0]
var item := tree.get_root().get_first_child()
while item and item.get_text(0) != "Ground":
	item = item.get_next()
if item == null:
	return "no Ground row"
for column in tree.columns:
	for index in item.get_button_count(column):
		if item.get_button_tooltip_text(column, index).contains("Toggle Visibility"):
			tree.button_clicked.emit(item, column, item.get_button_id(column, index), MOUSE_BUTTON_LEFT)
			return ""
return "no eye on Ground"
'''),
    {'op': 'wait', 'frames': 20},
    eval_('''
var ground := editor.get_edited_scene_root().get_node("Ground") as MeshInstance3D
print("[probe] Ground visible ", ground.visible)
if ground.visible:
	return "the eye did not hide Ground"
'''),
]
steps += add_node('GridMap', 'GroundTiles')
steps += [unfold_inspector(), {'op': 'wait', 'frames': 20}]
steps += quick_load('mesh_library', 'ground_tiles')
steps += [
    inspector_set('cell_size', 'Vector3(0.5, 0.5, 0.5)'),
    inspector_set('cell_center_y', 'false'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l16_gridmap_inspector', 'frames': 20},
    eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "GridMapEditor")
var out := []
for control in plugin._collect(panel, "Button", ""):
	if control.shortcut:
		out.append("%s=%s" % [control.shortcut.get_as_text(), control.shortcut.resource_name])
print("[probe] gridmap tools ", out)
'''),
    # Look straight down, closer.
    eval_('''
var viewport = plugin._collect(plugin.get_tree().root, "Node3DEditorViewport", "")[0]
for button in plugin._collect(viewport, "MenuButton", "Perspective"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i) == "Top View":
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no Top View"
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'wheel', 'steps': -10},
    {'op': 'capture', 'name': 'l16_top_view', 'frames': 20},
    # Grass: the Select tool, a box over the whole ground, then Fill.
    palette_pick('Grass'),
    gridmap_tool('Q'),
    {'op': 'wait', 'frames': 10},
    {'op': 'paint', 'points': [[-9.9, -9.9], [-5, -5], [0, 0], [5, 5], [9.9, 9.9]]},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l16_selection', 'frames': 10},
    gridmap_tool('Z'),
    {'op': 'wait', 'frames': 30},
    eval_('''
var map := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
print("[probe] after fill ", map.get_used_cells().size(), " cells")
if map.get_used_cells().size() != 1600:
	return "the fill did not cover the 40 by 40 cells: " + str(map.get_used_cells().size()) + " " + str(map.get_used_cells().reduce(func(a, c): return Vector3i(mini(a.x, c.x), 0, mini(a.z, c.z)), Vector3i(99, 0, 99))) + " " + str(map.get_used_cells().reduce(func(a, c): return Vector3i(maxi(a.x, c.x), 0, maxi(a.z, c.z)), Vector3i(-99, 0, -99)))
'''),
    {'op': 'capture', 'name': 'l16_grass_filled', 'frames': 20},
    # Dirt: the Paint tool along a path.
    palette_pick('Dirt'),
    gridmap_tool('E'),
    {'op': 'wait', 'frames': 10},
    {'op': 'paint', 'points': [[-9.8, 1.96], [-9.1, 1.57], [-8.4, 1.18], [-7.7, 0.81], [-7.0, 0.48], [-6.3, 0.21], [-5.6, 0.02], [-4.9, -0.08], [-4.2, -0.09], [-3.5, -0.01], [-2.8, 0.17], [-2.1, 0.43], [-1.4, 0.75], [-0.7, 1.11], [-0.0, 1.5], [0.7, 1.89], [1.4, 2.25], [2.1, 2.57], [2.8, 2.83], [3.5, 3.01], [4.2, 3.09], [4.9, 3.08], [5.6, 2.98], [6.3, 2.79], [7.0, 2.52], [7.7, 2.19], [8.4, 1.82], [9.1, 1.43], [9.8, 1.04]]},
    {'op': 'paint', 'points': [[-9.8, 2.46], [-9.1, 2.07], [-8.4, 1.68], [-7.7, 1.31], [-7.0, 0.98], [-6.3, 0.71], [-5.6, 0.52], [-4.9, 0.42], [-4.2, 0.41], [-3.5, 0.49], [-2.8, 0.67], [-2.1, 0.93], [-1.4, 1.25], [-0.7, 1.61], [-0.0, 2.0], [0.7, 2.39], [1.4, 2.75], [2.1, 3.07], [2.8, 3.33], [3.5, 3.51], [4.2, 3.59], [4.9, 3.58], [5.6, 3.48], [6.3, 3.29], [7.0, 3.02], [7.7, 2.69], [8.4, 2.32], [9.1, 1.93], [9.8, 1.54]]},
    {'op': 'paint', 'points': [[-9.8, 2.96], [-9.1, 2.57], [-8.4, 2.18], [-7.7, 1.81], [-7.0, 1.48], [-6.3, 1.21], [-5.6, 1.02], [-4.9, 0.92], [-4.2, 0.91], [-3.5, 0.99], [-2.8, 1.17], [-2.1, 1.43], [-1.4, 1.75], [-0.7, 2.11], [-0.0, 2.5], [0.7, 2.89], [1.4, 3.25], [2.1, 3.57], [2.8, 3.83], [3.5, 4.01], [4.2, 4.09], [4.9, 4.08], [5.6, 3.98], [6.3, 3.79], [7.0, 3.52], [7.7, 3.19], [8.4, 2.82], [9.1, 2.43], [9.8, 2.04]]},
    {'op': 'paint', 'points': [[1.2, 2.8], [1.68, 3.4], [2.13, 4.0], [2.51, 4.6], [2.8, 5.2], [3.0, 5.8], [3.11, 6.4], [3.15, 7.0], [3.16, 7.6], [3.18, 8.2], [3.25, 8.8], [3.38, 9.4]]},
    {'op': 'paint', 'points': [[1.65, 2.8], [2.13, 3.4], [2.58, 4.0], [2.96, 4.6], [3.25, 5.2], [3.45, 5.8], [3.56, 6.4], [3.6, 7.0], [3.6100000000000003, 7.6], [3.6300000000000003, 8.2], [3.7, 8.8], [3.83, 9.4]]},
    {'op': 'wait', 'frames': 20},
    # Sand: select a patch and fill it.
    palette_pick('Sand'),
    gridmap_tool('Q'),
    {'op': 'paint', 'points': [[-8.5, -8.5], [-6, -6], [-4.5, -5]]},
    gridmap_tool('Z'),
    {'op': 'wait', 'frames': 20},
    eval_('''
var map := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
var counts := {}
for cell in map.get_used_cells():
	var name := map.mesh_library.get_item_name(map.get_cell_item(cell))
	counts[name] = counts.get(name, 0) + 1
print("[probe] painted ", counts)
'''),
    gridmap_tool('Q'),
    {'op': 'capture', 'name': 'l16_painted', 'frames': 20},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
]

def report(label):
    # The player's position, from inside the game.
    return {'op': 'eval', 'code': f'''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] player {label} position ", player.global_position.snapped(Vector3.ONE * 0.01), " on floor ", player.is_on_floor())'''}


game = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l16.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 8},
    report('start'),
    # Walk up the screen, away from the rocks, across grass and the dirt path.
    {'op': 'key', 'key': 'W', 'pressed': True},
    {'op': 'sleep', 'seconds': 1.5},
    {'op': 'key', 'key': 'W', 'pressed': False},
    {'op': 'wait', 'frames': 20},
    report('after walking'),
    {'op': 'capture', 'name': 'l16_game_wide', 'frames': 10},
    {'op': 'quit'},
])
steps += play(game, 30, capture_running='l16_running')
write(sys.argv[2], steps)
