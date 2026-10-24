# Lesson 12, in Godot: the large rock shares the palette material and gets collision, a scene of its own, and copies
# in the meadow varied by turning and scaling.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (open_advanced, write, eval_, click_tab, click_file, open_in_file_dialog, inspector_set, game_steps, play, import_set,
                   show_import_row, REIMPORT, instantiate_under)

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': 'res://art/nature/rock_large/rock_large.glb'},
    *click_file('rock_large.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 20},
    show_import_row('materials/extract'),
    import_set('materials/extract', 1),
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "materials/extract_path":
		plugin._collect(row, "Button", "")[0].pressed.emit()
		return ""
return "no Extract Path row"
'''),
    {'op': 'wait', 'frames': 40},
    open_in_file_dialog('art', 'palette'),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for button in plugin._collect(window, "Button", "Select Current Folder"):
			button.pressed.emit()
			return ""
return "no Select Current Folder button"
'''),
    {'op': 'wait', 'frames': 30},
    show_import_row('materials/extract_path'),
    {'op': 'capture', 'name': 'l12_extract'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 4},
    eval_('''
print("[probe] palette folder ", DirAccess.get_files_at("res://art/palette"), " rock_large folder ", DirAccess.get_files_at("res://art/nature/rock_large"))
var scene: PackedScene = load("res://art/nature/rock_large/rock_large.glb")
var root := scene.instantiate()
var mesh := root.find_children("*", "MeshInstance3D", true, false)[0] as MeshInstance3D
print("[probe] large rock material ", mesh.mesh.surface_get_material(0).resource_path)
root.free()
'''),
    # Collision, as for the small rock.
    open_advanced(),
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		var item: TreeItem = tree.get_root()
		while item and item.get_text(0) != "rock_large":
			item = item.get_next_in_tree()
		item.select(0)
		tree.item_selected.emit()
		await plugin.get_tree().process_frame
		for row in plugin._collect(window, "EditorProperty", ""):
			if str(row.get_edited_property()) == "generate/physics":
				row.emit_changed("generate/physics", true)
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		for row in plugin._collect(window, "EditorProperty", ""):
			if str(row.get_edited_property()) == "physics/shape_type":
				row.emit_changed("physics/shape_type", 1)
		return ""
return "no Advanced Import Settings"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l12_advanced', 'window': 'Advanced'},
    {'op': 'press', 'find': {'window': 'Advanced', 'type': 'Button', 'text': 'Reimport'}},
    {'op': 'sleep', 'seconds': 4},
    # The scene: New Inherited Scene, rename the root, save.
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		print("[probe] base scene dialog at ", window.current_dir)
'''),
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'nature', 'rock_large'),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "rock_large.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no rock_large.glb"
'''),
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    eval_('print("[probe] inherited root ", editor.get_edited_scene_root().name)'),
    click_tab('Scene'),
    {'op': 'click', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'item': 'rock_large2', 'double': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible:
		for edit in plugin._collect(window, "LineEdit", ""):
			if edit.text == "rock_large2":
				edit.text = "RockLarge"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no rename field"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		print("[probe] save dialog at ", window.current_dir, " file ", window.current_file)
'''),
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'capture', 'name': 'l12_large_scene'},
]

# Large rocks in the meadow, set among the small ones. The second is squashed flatter: one model, a new shape.
LARGE = [
    ('RockLarge', 'Vector3(-5, 0, 0)', 'Vector3(0, deg_to_rad(20), 0)', 'Vector3(1, 1, 1)'),
    ('RockLarge2', 'Vector3(3.2, 0, -4.8)', 'Vector3(0, deg_to_rad(-110), 0)', 'Vector3(1.1, 0.7, 1.1)'),
    ('RockLarge3', 'Vector3(-3.6, 0, 3.4)', 'Vector3(0, deg_to_rad(-160), 0)', 'Vector3(0.9, 0.8, 0.9)'),
]
steps += [
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
]
for number, (name, position, rotation, scale) in enumerate(LARGE):
    steps += instantiate_under('Rocks', 'rock_large.tscn', capture='l12_select_scene' if number == 0 else None)
    steps += [
        {'op': 'select', 'path': f'Rocks/{name}'},
        inspector_set('position', position),
        inspector_set('rotation', rotation),
        inspector_set('scale', scale),
    ]
steps += [
    {'op': 'select', 'path': 'Rocks/RockLarge2'},
    {'op': 'capture', 'name': 'l12_rock_inspector', 'frames': 20},
    eval_('editor.get_selection().clear()'),
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l12_meadow_editor', 'frames': 20},
    eval_('print("[probe] rocks ", editor.get_edited_scene_root().get_node("Rocks").get_children().map(func(n): return n.name))'),
]

POSITION = '''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] player ", label, " position ", player.global_position.snapped(Vector3.ONE * 0.01))'''


def report(label):
    return {'op': 'eval', 'code': f'var label := "{label}"\n' + POSITION}


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l12.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 8},
    {'op': 'capture', 'name': 'l12_game_wide'},
    # Walk left into the large rock at (-5, 0, 0).
    {'op': 'key', 'key': 'A', 'pressed': True},
    {'op': 'sleep', 'seconds': 2.5},
    {'op': 'key', 'key': 'A', 'pressed': False},
    {'op': 'wait', 'frames': 20},
    report('walking into the large rock'),
    {'op': 'wheel', 'steps': 3},
    {'op': 'capture', 'name': 'l12_game_close', 'frames': 10},
    {'op': 'quit'},
])
steps += play(game, 33, capture_running='l12_running')
write(sys.argv[2], steps)
