# Lesson 24: imports the oak's trunk and branches, makes its scene with the shared palette material, and plants one in
# the meadow beside the rocks.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, instantiate_under, quick_load, game_steps, play,
                   open_in_file_dialog, view, click_tab, INSPECTOR)

SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
TREE_SCENE = 'res://art/nature/tree_oak/tree_oak.tscn'

steps = [
    {'op': 'sleep', 'seconds': 8},
    {'op': 'fs', 'path': 'res://art/nature/tree_oak/tree_oak.glb'},
    eval_('''
var scene: PackedScene = load("res://art/nature/tree_oak/tree_oak.glb")
var root := scene.instantiate()
var out := []
for node in root.find_children("*", "", true, false):
	var extra := ""
	if node is MeshInstance3D:
		var mesh: Mesh = node.mesh
		var arrays := mesh.surface_get_arrays(0)
		extra = " vertices %d indices %d material %s aabb %s uv %s normals %s" % [arrays[Mesh.ARRAY_VERTEX].size(), arrays[Mesh.ARRAY_INDEX].size(), str(mesh.surface_get_material(0).resource_name), str(mesh.get_aabb()), arrays[Mesh.ARRAY_TEX_UV] != null, arrays[Mesh.ARRAY_NORMAL] != null]
	out.append(str(root.get_path_to(node)) + " <" + node.get_class() + ">" + extra)
print("[probe] imported tree ", root.name, " <", root.get_class(), ">\\n", "\\n".join(out))
root.free()
'''),
    # The prop scene: Scene > New Inherited Scene from the .glb, as for the rocks.
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'nature', 'tree_oak'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "tree_oak.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no tree_oak.glb in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l24_inherit_dialog', 'window': 'Open Base Scene'},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] inherited scene root ", root.name, " <", root.get_class(), "> children ", root.get_children().map(func(n): return n.name))
'''),
    {'op': 'main_screen', 'name': '3D'},
    click_tab('Scene'),
    {'op': 'click', 'find': SCENE_TREE, 'item': 'tree_oak2', 'double': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible:
		for edit in plugin._collect(window, "LineEdit", ""):
			if edit.text == "tree_oak2":
				edit.text = "TreeOak"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no rename field"
'''),
    {'op': 'wait', 'frames': 20},
    # The bark takes the shared palette material, as the rocks do.
    {'op': 'select', 'path': 'tree_oak'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('material_override', 'palette_lit.tres'),
    eval_('''
var node := editor.get_edited_scene_root().get_child(0) as MeshInstance3D
print("[probe] override ", node.material_override.resource_path)
'''),
    *view('tree_oak', dx=0, dy=0, wheel=0),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l24_tree_scene'},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l24_save_scene', 'window': 'Save Scene As'},
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
    # Plant one in the meadow, away from the rocks.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    *add_node('Node3D', 'Trees'),
    *instantiate_under('Trees', 'tree_oak.tscn', capture='l24_select_scene'),
    eval_('''
var trees := editor.get_edited_scene_root().get_node("Trees")
print("[probe] trees children ", trees.get_children().map(func(n): return n.name))
'''),
    {'op': 'select', 'path': 'Trees/TreeOak'},
    inspector_set('position', 'Vector3(-5, 0, -3)'),
    {'op': 'capture', 'name': 'l24_tree_inspector', 'frames': 20},
    *view('Trees/TreeOak', dx=0, dy=0, wheel=-2),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'l24_meadow_tree', 'frames': 20},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
]

out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l24.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 6},
    {'op': 'capture', 'name': 'l24_game_start'},
    {'op': 'wheel', 'steps': 4},
    {'op': 'capture', 'name': 'l24_game_close', 'frames': 10},
    {'op': 'quit'},
])
steps += play(game, 25)
write(sys.argv[2], steps)
