# Bonus lesson 63, in Godot: any rigged character. A model whose bones have another artist's names (pelvis, spine_01,
# upperarm_l ...) is imported with a new BoneMap; the auto-mapper's result is read, the gaps fixed by hand, and the library's
# walk is played on it.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_file, click_tab, open_advanced, add_node, open_in_file_dialog
import os as _os
from bonemap_ui import ADVANCED, select_node, new_humanoid_bone_map

steps = [
    {'op': 'sleep', 'seconds': 30},
    {'op': 'fs', 'path': 'res://art/character/superhero/Superhero_Male_FullBody.gltf'},
    *click_file('Superhero_Male_FullBody.gltf'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 40},
    open_advanced(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l63_advanced', 'window': 'Advanced'},
    select_node('Skeleton3D'),
    {'op': 'capture', 'name': 'l63_skeleton', 'window': 'Advanced'},
    eval_(ADVANCED + '''
var tree: Tree = plugin._collect(advanced, "Tree", "")[0]
var names := []
var item: TreeItem = tree.get_root()
while item:
	names.append(item.get_text(0))
	item = item.get_next_in_tree()
print("[probe] tree ", names)
'''),
    *new_humanoid_bone_map('l63'),
    eval_(ADVANCED + '''
var bone_map: BoneMap = null
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "retarget/bone_map":
		bone_map = row.get_edited_object().get("retarget/bone_map")
var mapped := []
for i in bone_map.profile.bone_size:
	var name := bone_map.profile.get_bone_name(i)
	var target := bone_map.get_skeleton_bone_name(name)
	if target != &"":
		mapped.append("%s=%s" % [name, target])
print("[probe] mapped detail ", " ".join(mapped))
'''),
    {'op': 'press', 'find': {'window': 'Advanced', 'type': 'Button', 'text': 'Reimport'}},
    {'op': 'sleep', 'seconds': 6},
    eval_('''
var root = load("res://art/character/superhero/Superhero_Male_FullBody.gltf").instantiate()
var skeleton := root.find_child("GeneralSkeleton", true, false) as Skeleton3D
var names := []
for i in skeleton.get_bone_count():
	names.append(skeleton.get_bone_name(i))
print("[probe] foreign skeleton ", skeleton.name, " ", names.size(), " bones ", " ".join(names), " motion scale ", skeleton.motion_scale)
root.free()
'''),
    # An inherited scene, with an AnimationPlayer and the library, in the meadow beside the player.
    click_tab('Scene'),
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'character', 'superhero'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "Superhero_Male_FullBody.gltf":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no Superhero_Male_FullBody.gltf in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'select', 'path': '.'},
    *add_node('AnimationPlayer', 'AnimationPlayer'),
    eval_('''
var root := editor.get_edited_scene_root()
var player := root.get_node("AnimationPlayer") as AnimationPlayer
player.add_animation_library("", load("res://art/animations/UAL1_Standard.glb"))
player.play("Walk")
player.advance(0.4)
print("[probe] foreign clips ", player.get_animation_list().size())
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l63_walk_pose', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root()
(root.get_node("AnimationPlayer") as AnimationPlayer).stop()
(root.find_child("GeneralSkeleton", true, false) as Skeleton3D).reset_bone_poses()
'''),
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/character/superhero"
		window.current_file = "superhero.tscn"
		window.get_ok_button().pressed.emit()
'''),
    {'op': 'wait', 'frames': 40},
]
write(sys.argv[2], steps)
