# Lesson 62 (bonus), in Godot: click to move for action RPGs. A navigation mesh baked from the meadow's colliders, a NavigationAgent3D on the
# player, and a script that walks the player to where the mouse clicks, round the trees and the pond.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, new_resource, open_resource, quick_load, game_steps, play,
                   save_code, build, click_tab, show_row)
from lesson62_pieces import CLICK_MOVEMENT, PIECES

SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
out_dir = os.path.dirname(sys.argv[2])
CLOCK = 'Meadow/WorldEnvironment/Day'
GROUP = 'navigation_geometry'
GEOMETRY = ['Ground', 'GroundTiles', 'Bank', 'Rocks', 'Trees', 'Bushes']


def dock_tab(title):
    # The Inspector dock's tabs scroll when they do not fit; the tab is switched to by its index.
    return eval_(f'''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	for i in bar.tab_count:
		if bar.get_tab_title(i) == "{title}" and bar.get_tab_title(0) == "Inspector":
			var container = bar.get_parent()
			while container != null and not container is TabContainer:
				container = container.get_parent()
			if container == null:
				return "no tab container above the dock tabs"
			container.current_tab = i
			return ""
return "no dock tab {title}"
''')


def make_group(name):
    # The Groups tab's + opens Create New Group: the name typed in its field, Add pressed. The group exists, with no node in it yet.
    return [
        dock_tab('Groups'),
        {'op': 'wait', 'frames': 20},
        eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "GroupsEditor")
for button in dock.find_children("*", "Button", true, false):
	if button.tooltip_text == "Add a new group.":
		button.pressed.emit()
		return ""
return "no Add a new group button"
'''),
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		var fields := plugin._collect(window, "LineEdit", "")
		print("[probe] group dialog ", window.title, " fields ", fields.size())
		fields[0].text = "{name}"
		fields[0].text_changed.emit(fields[0].text)
		return ""
return "no Create New Group dialog"
'''),
        {'op': 'wait', 'frames': 20},
        {'op': 'capture', 'name': 'l62_new_group', 'window': 'class:ConfirmationDialog'},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
        {'op': 'wait', 'frames': 30},
    ]


def select_nodes(names):
    # The nodes selected together, as ctrl-clicking them in the Scene dock does.
    return [
        eval_(f'''
var root := editor.get_edited_scene_root()
var selection := EditorInterface.get_selection()
selection.clear()
for node_name in {names!r}:
	selection.add_node(root.get_node(node_name))
'''),
        {'op': 'wait', 'frames': 30},
    ]


def group_nodes(names, name):
    # The nodes selected together, as ctrl-clicking them in the Scene dock does, and the group's box ticked in the Groups tab.
    return [
        eval_(f'''
var root := editor.get_edited_scene_root()
var selection := EditorInterface.get_selection()
selection.clear()
for node_name in {names!r}:
	selection.add_node(root.get_node(node_name))
'''),
        {'op': 'wait', 'frames': 30},
        dock_tab('Groups'),
        {'op': 'wait', 'frames': 20},
        eval_(f'''
var dock = plugin._find_class(plugin.get_tree().root, "GroupsEditor")
var seen := []
for tree in dock.find_children("*", "Tree", true, false):
	var stack := [tree.get_root()]
	while not stack.is_empty():
		var current: TreeItem = stack.pop_back()
		if current == null:
			continue
		seen.append(current.get_text(0))
		if current.get_text(0) == "{name}":
			print("[probe] group row checked ", current.is_checked(0), " checkable ", current.is_checkable(0))
			current.set_checked(0, true)
			tree.item_edited.emit()
			return ""
		var child := current.get_first_child()
		while child != null:
			stack.append(child)
			child = child.get_next()
print("[probe] group tree items ", seen)
return "no group row {name}"
'''),
        {'op': 'wait', 'frames': 30},
    ]


def sample(label, seconds):
    return [
        {'op': 'sleep', 'seconds': seconds},
        {'op': 'eval', 'code': f'''
var player := tree.root.get_node("Meadow/Player")
var tile = tree.root.get_node("Meadow/GroundTiles").call("TileAt", player.global_position)
print("[game] {label} ", snappedf(player.global_position.x, 0.01), " ", snappedf(player.global_position.z, 0.01), " speed ", snappedf(Vector2(player.velocity.x, player.velocity.z).length(), 0.01), " tile ", tile.get("DisplayName") if tile != null else "none")
'''},
    ]


def click_on_ground(x, z):
    # A left click at the screen position of a point on the ground, sent into the game as the operating system sends one.
    return {'op': 'eval', 'code': f'''
var camera := tree.root.get_viewport().get_camera_3d()
var screen := camera.unproject_position(Vector3({x}, 0.0, {z}))
for pressed in [true, false]:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	event.position = screen
	Input.parse_input_event(event)
'''}


game_steps_list = [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(5.5, 0.05, 0.5)'},
    {'op': 'wheel', 'steps': 2}, {'op': 'sleep', 'seconds': 1.0},
    *sample('START', 0.1),
    {'op': 'capture', 'name': 'l62_start', 'frames': 5},
    # Round the trees and the pond: the straight way is blocked.
    click_on_ground(-2.5, -3.0),
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player/Agent").debug_enabled = true'},
]
for i in range(1, 21):
    game_steps_list += sample(f'WALK{i}', 0.4)
    if i == 6:
        game_steps_list += [{'op': 'capture', 'name': 'l62_midway', 'frames': 3}]
game_steps_list += [
    {'op': 'eval', 'code': '''
var agent: NavigationAgent3D = tree.root.get_node("Meadow/Player/Agent")
print("[game] AGENT target ", agent.target_position, " final ", agent.get_final_position(), " finished ", agent.is_navigation_finished(), " distance ", agent.distance_to_target(), " radius ", agent.radius)
var region := tree.root.get_node("Meadow/Navigation") as NavigationRegion3D
print("[game] NAVMESH polygons ", region.navigation_mesh.get_polygon_count(), " agent radius ", region.navigation_mesh.agent_radius)
print("[game] PATH ", agent.get_current_navigation_path())
'''},
    {'op': 'capture', 'name': 'l62_arrived', 'frames': 5},
    {'op': 'eval', 'code': 'var animation_tree: AnimationTree = tree.root.get_node("Meadow/Player").find_child("AnimationTree", true, false)\nprint("[game] BLEND ", animation_tree.get("parameters/blend_position"))'},
    {'op': 'quit'}]
game = game_steps(os.path.join(out_dir, 'game-l62.jsonl'), game_steps_list)

steps = [
    {'op': 'sleep', 'seconds': 5},
    save_code('res://src/Player/ClickMovement.cs', CLICK_MOVEMENT),
    eval_('editor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 4},
    *build('l62_built'),
    # The navigation mesh, baked from the colliders in the geometry group.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
]
steps += select_nodes(GEOMETRY)
steps += make_group(GROUP)
steps += [
    eval_('''
var root := editor.get_edited_scene_root()
for name in %r:
	print("[probe] groups of ", name, " ", root.get_node(name).get_groups())
''' % GEOMETRY),
    {'op': 'select', 'path': 'Trees'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l62_groups'},
    dock_tab('Inspector'),
    {'op': 'select', 'path': '.'},
    *add_node('NavigationRegion3D', 'Navigation'),
    *new_resource('navigation_mesh', 'NavigationMesh', nth=-1),
    eval_('''
EditorInterface.edit_resource((editor.get_edited_scene_root().get_node("Navigation") as NavigationRegion3D).navigation_mesh)
await plugin.get_tree().create_timer(1.0).timeout
'''),
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    eval_('''
var names := []
for property in plugin._find_class(plugin.get_tree().root, "InspectorDock").find_children("*", "EditorProperty", true, false):
	names.append(str(property.get_edited_property()))
print("[probe] all rows ", names)
'''),
    {'op': 'capture', 'name': 'l62_probe_nav3'},
    inspector_set('geometry_parsed_geometry_type', '1'),
    inspector_set('geometry_source_geometry_mode', '1'),
    inspector_set('geometry_source_group_name', f'"{GROUP}"'),
    # The agent the mesh is baked for is the player: a capsule 0.3 meters in radius and 1.8 tall.
    inspector_set('agent_radius', '0.35'),
    inspector_set('agent_height', '1.8'),
    # Rocks and the tree trunks have slopes and edges the player cannot climb, so they are not floor.
    inspector_set('agent_max_climb', '0.1'),
    inspector_set('agent_max_slope', '20.0'),
    # A fine height step puts the mesh a few centimeters above the ground, not a few tens.
    inspector_set('cell_height', '0.05'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l62_navmesh_settings'},
    eval_('''
for button in plugin._collect(plugin.get_tree().root, "Button", ""):
	if button.is_visible_in_tree() and (button.text.contains("Bake") or button.tooltip_text.contains("Bake")):
		print("[probe] bake button ", button.text, " | ", button.tooltip_text)
		button.pressed.emit()
		return ""
return "no Bake NavigationMesh button"
'''),
    {'op': 'sleep', 'seconds': 8},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l62_baked'},
    eval_('''
var region := editor.get_edited_scene_root().get_node("Navigation") as NavigationRegion3D
print("[probe] baked polygons ", region.navigation_mesh.get_polygon_count())
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The player: the click script, and the agent it asks.
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    *add_node('NavigationAgent3D', 'Agent'),
    inspector_set('path_desired_distance', '0.4'),
    inspector_set('target_desired_distance', '0.3'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l62_agent_settings'},
    {'op': 'select', 'path': '.'},
    {'op': 'wait', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root()
root.set_script(null)
'''),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'ClickMovement'),
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'Agent'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l62_agent'},
    eval_('print("[probe] player script ", editor.get_edited_scene_root().get_script(), " children ", editor.get_edited_scene_root().get_children())'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(game, 60),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
