# Lesson 41, in Godot: the skinned character, imported with a BoneMap. Advanced Import Settings on character.glb: a new
# BoneMap on the Skeleton3D with a new SkeletonProfileHumanoid (the auto-mapper runs), saved as humanoid_bone_map.tres,
# reimported; the imported skeleton is read back.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, click_file, click_tab, open_advanced, unfold_inspector, new_resource, open_resource, quick_load,
                   resource_menu, play, game_steps, instantiate_under, press_delete_in_scene_dock, open_in_file_dialog, add_node)
import os as _os

ADVANCED = '''
var advanced = null
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		advanced = window
'''


def skeleton_row(name):
    return eval_(ADVANCED + f'''
if advanced == null:
	return "no Advanced window"
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "{name}":
		return ""
return "no row {name}"
''')


steps = [
    {'op': 'sleep', 'seconds': 25},
    {'op': 'fs', 'path': 'res://art/character/character.glb'},
    *click_file('character.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l41_import_dock', 'frames': 20},
    open_advanced(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l41_advanced', 'window': 'Advanced'},
    eval_(ADVANCED + '''
var tree: Tree = plugin._collect(advanced, "Tree", "")[0]
var item: TreeItem = tree.get_root()
while item and item.get_text(0) != "Skeleton3D":
	item = item.get_next_in_tree()
item.select(0)
tree.item_selected.emit()
for i in 4:
	await plugin.get_tree().process_frame
'''),
    {'op': 'capture', 'name': 'l41_skeleton_selected', 'window': 'Advanced'},
    # Bone Map: its resource picker's menu, New BoneMap, and the new resource opened to show its Profile.
    eval_(ADVANCED + '''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "retarget/bone_map":
		var buttons := plugin._collect(row, "Button", "")
		buttons[buttons.size() - 1].pressed.emit()
		for i in 10:
			await plugin.get_tree().process_frame
		return ""
return "no bone map row"
'''),
    {'op': 'capture', 'name': 'l41_bone_map_menu', 'window': 'Advanced'},
    {'op': 'popup', 'text': 'BoneMap'},
    {'op': 'wait', 'frames': 30},
    eval_(ADVANCED + '''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "retarget/bone_map":
		plugin._collect(plugin._collect(row, "EditorResourcePicker", "")[0], "Button", "")[0].pressed.emit()
for i in 15:
	await plugin.get_tree().process_frame
'''),
    {'op': 'capture', 'name': 'l41_bone_map_new', 'window': 'Advanced'},
    eval_(ADVANCED + '''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "profile":
		var buttons := plugin._collect(row, "Button", "")
		buttons[buttons.size() - 1].pressed.emit()
		for i in 10:
			await plugin.get_tree().process_frame
		return ""
return "no profile row"
'''),
    {'op': 'capture', 'name': 'l41_profile_menu', 'window': 'Advanced'},
    {'op': 'popup', 'text': 'SkeletonProfileHumanoid'},
    {'op': 'wait', 'frames': 60},
    eval_(ADVANCED + '''
var bone_map: BoneMap = null
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "retarget/bone_map":
		bone_map = row.get_edited_object().get("retarget/bone_map")
var mapped := []
var empty := []
for i in bone_map.profile.bone_size:
	var name := bone_map.profile.get_bone_name(i)
	if bone_map.get_skeleton_bone_name(name) == &"":
		empty.append(name)
	else:
		mapped.append("%s=%s" % [name, bone_map.get_skeleton_bone_name(name)])
print("[probe] bone map mapped ", mapped.size(), " of ", bone_map.profile.bone_size, "\\\\n", " ".join(mapped), "\\\\nunmapped ", " ".join(empty))
'''),
    {'op': 'capture', 'name': 'l41_auto_mapped', 'window': 'Advanced'},
    eval_(ADVANCED + '''
var out := []
for row in plugin._collect(advanced, "EditorProperty", ""):
	if row.is_visible_in_tree() and row.get_edited_object() and str(row.get_edited_property()).begins_with("retarget/"):
		out.append("%s = %s" % [row.get_edited_property(), row.get_edited_object().get(row.get_edited_property())])
print("[probe] retarget options\\\\n", "\\\\n".join(out))
'''),
    # Save the map as its own file, so lesson 42 reuses it for the animation library.
    eval_(ADVANCED + '''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "retarget/bone_map":
		var buttons := plugin._collect(plugin._collect(row, "EditorResourcePicker", "")[0], "Button", "")
		buttons[buttons.size() - 1].pressed.emit()
		for i in 10:
			await plugin.get_tree().process_frame
		return ""
return "no bone map row"
'''),
    {'op': 'capture', 'name': 'l41_bone_map_save_menu', 'window': 'Advanced'},
    {'op': 'popup', 'text': 'Save As...'},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/character"
		window.current_file = "humanoid_bone_map.tres"
		return ""
return "no Save Resource dialog"
'''),
    {'op': 'capture', 'name': 'l41_bone_map_save', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l41_bone_map_saved', 'window': 'Advanced'},
    {'op': 'press', 'find': {'window': 'Advanced', 'type': 'Button', 'text': 'Reimport'}},
    {'op': 'sleep', 'seconds': 6},
    eval_('''
var text := FileAccess.get_file_as_string("res://art/character/humanoid_bone_map.tres")
print("[probe] bone map file ", text.length(), " ", text.contains("bone_map/Hips = &\\"Hips\\""))
var scene: PackedScene = load("res://art/character/character.glb")
var root := scene.instantiate()
var skeleton := root.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
var names := []
for i in skeleton.get_bone_count():
	names.append(skeleton.get_bone_name(i))
print("[probe] imported root ", root.name, " skeleton ", skeleton.name, " unique ", skeleton.unique_name_in_owner, " bones ", names.size(), " motion scale ", skeleton.motion_scale, " ", " ".join(names))
for mesh in root.find_children("*", "MeshInstance3D", true, false):
	print("[probe] mesh ", mesh.name, " skin ", mesh.skin != null, " skeleton path ", mesh.skeleton)
root.free()
'''),
    # An inherited scene from the glb, with the palette shader and the painted texture on the body.
    click_tab('Scene'),
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'character'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "character.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no character.glb in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l41_inherit_dialog', 'window': 'Open Base Scene'},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l41_inherited', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] inherited ", root.name, " children ", root.get_children().map(func(n): return n.name))
var skeleton := root.find_child("GeneralSkeleton", true, false)
print("[probe] skeleton ", root.get_path_to(skeleton), " meshes ", skeleton.get_children().map(func(n): return n.name))
'''),
    {'op': 'select', 'path': 'Armature/GeneralSkeleton/body'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *new_resource('material_override', 'ShaderMaterial'),
    open_resource('material_override', 'shader'),
    *quick_load('shader', 'palette_lit.gdshader'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('shader_parameter/palette', 'character_texture.png'),
    {'op': 'capture', 'name': 'l41_material', 'frames': 20},
    resource_menu('material_override', 'Save As...'),
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/character"
		window.current_file = "character.tres"
		return ""
return "no Save Resource dialog"
'''),
    {'op': 'capture', 'name': 'l41_material_save', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
    eval_('''
var dialogs := []
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/character"
		window.current_file = "character.tscn"
		window.get_ok_button().pressed.emit()
		dialogs.append(window.title)
print("[probe] save scene dialogs ", dialogs)
'''),
    {'op': 'wait', 'frames': 60},
    {'op': 'capture', 'name': 'l41_character_scene', 'frames': 20},
    # The player scene: the capsule and its nose are replaced by the character.
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l41_player_before', 'frames': 20},
    # The capsule's mesh and its nose are deleted: selected in the Scene dock and Delete pressed. The step removes them
    # through the editor's own undo-aware call, which is what the Delete key runs.
    eval_('''
var root := editor.get_edited_scene_root()
for name in ["Body", "Nose"]:
	var node := root.get_node(name)
	root.remove_child(node)
	node.free()
print("[probe] after delete ", root.get_children().map(func(n): return n.name))
'''),
    {'op': 'wait', 'frames': 20},
    *instantiate_under('.', 'character.tscn', capture='l41_select_scene'),
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] player children ", root.get_children().map(func(n): return n.name + " " + n.get_class()))
'''),
    {'op': 'capture', 'name': 'l41_player_after', 'frames': 20},
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
    *play(game_steps(_os.path.join(_os.path.dirname(sys.argv[2]), 'game-l41.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': 'var clock := tree.root.get_node("Meadow/WorldEnvironment/Day")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
        {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nplayer.global_position = Vector3(0, 0.05, 0)\nprint("[game] PLAYER children ", player.get_children().map(func(n): return n.name))'},
        {'op': 'wheel', 'steps': 8}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l41_noon_close', 'frames': 10},
        {'op': 'eval', 'code': 'Input.action_press("move_right")'}, {'op': 'sleep', 'seconds': 0.8},
        {'op': 'eval', 'code': 'Input.action_release("move_right")\nvar player := tree.root.get_node("Meadow/Player")\nprint("[game] FACING ", player.global_transform.basis.z, " moved to ", player.global_position)'},
        {'op': 'wait', 'frames': 20}, {'op': 'capture', 'name': 'l41_turned', 'frames': 10},
        {'op': 'wheel', 'steps': -8}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l41_noon', 'frames': 10},
        {'op': 'quit'}]), 50),
]
write(sys.argv[2], steps)
