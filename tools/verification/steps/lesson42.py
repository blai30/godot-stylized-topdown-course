# Lesson 42, in Godot: the Universal Animation Library imported as an Animation Library with its own auto-mapped BoneMap
# (the reference project uses UAL1_Standard.glb, UAL's clips on the humanoid names, CC0), read back, and the library loaded into an
# AnimationPlayer on the character, which plays Idle, Walk, and Run.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_file, click_tab, open_advanced, add_node, game_steps, play
import os as _os
from bonemap_ui import ADVANCED, select_node, new_humanoid_bone_map

steps = [
    {'op': 'sleep', 'seconds': 40},
    {'op': 'fs', 'path': 'res://art/animations/UAL1_Standard.glb'},
    *click_file('UAL1_Standard.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l42_import_dock', 'frames': 20},
    # Import As: the option at the top of the Import dock, Scene by default; Animation Library is first in its list.
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for option in plugin._collect(dock, "OptionButton", ""):
	if option.get_item_text(0) == "Animation Library":
		option.select(0)
		option.item_selected.emit(0)
		for i in 30:
			await plugin.get_tree().process_frame
		return ""
return "no Import As option"
'''),
    {'op': 'capture', 'name': 'l42_library_dock', 'frames': 20},
    open_advanced(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l42_advanced', 'window': 'Advanced'},
    select_node('Skeleton3D'),
    {'op': 'capture', 'name': 'l42_skeleton', 'window': 'Advanced'},
    *new_humanoid_bone_map('l42'),
    # The clips ending in _Loop import as looping clips, without their suffix: check one in the Advanced window's tree.
    select_node('Idle'),
    {'op': 'capture', 'name': 'l42_idle_options', 'window': 'Advanced'},
    {'op': 'press', 'find': {'window': 'Advanced', 'type': 'Button', 'text': 'Reimport'}},
    {'op': 'sleep', 'seconds': 8},
    eval_('''
var library = load("res://art/animations/UAL1_Standard.glb")
print("[probe] library class ", library.get_class())
if library is AnimationLibrary:
	var out := []
	for name in library.get_animation_list():
		var animation: Animation = library.get_animation(name)
		out.append("%s loop %s tracks %d length %.2f" % [name, animation.loop_mode, animation.get_track_count(), animation.length])
	print("[probe] clips\\\\n", "\\\\n".join(out))
	var walk: Animation = library.get_animation("Walk")
	var tracks := []
	for i in 6:
		tracks.append(str(walk.track_get_path(i)) + " type " + str(walk.track_get_type(i)))
	print("[probe] walk tracks ", tracks)
	var position_tracks := 0
	for i in walk.get_track_count():
		if walk.track_get_type(i) == Animation.TYPE_POSITION_3D:
			position_tracks += 1
	print("[probe] walk position tracks ", position_tracks)
'''),
    # The character scene gets an AnimationPlayer, and the library is loaded into it.
    click_tab('Scene'),
    {'op': 'open', 'path': 'res://art/character/character.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': '.'},
    *add_node('AnimationPlayer', 'AnimationPlayer'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l42_player_added', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root()
var player := root.get_node("AnimationPlayer") as AnimationPlayer
player.add_animation_library("", load("res://art/animations/UAL1_Standard.glb"))
print("[probe] player library ", player.get_animation_list())
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l42_player_library', 'frames': 20},
    eval_('''
var player := editor.get_edited_scene_root().get_node("AnimationPlayer") as AnimationPlayer
player.play("Walk")
player.advance(0.4)
await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l42_walk_pose', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root()
var player := root.get_node("AnimationPlayer") as AnimationPlayer
player.stop()
# Playing a clip in the editor leaves its pose on the skeleton, and the scene would save it: put the bones back to rest.
(root.find_child("GeneralSkeleton", true, false) as Skeleton3D).reset_bone_poses()
'''),
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
    *play(game_steps(_os.path.join(_os.path.dirname(sys.argv[2]), 'game-l42.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': 'var clock := tree.root.get_node("Meadow/WorldEnvironment/Day")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
        {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player") as CharacterBody3D\nplayer.global_position = Vector3(0, 0.05, 0)'},
        {'op': 'wheel', 'steps': 12}, {'op': 'wait', 'frames': 30},
        {'op': 'eval', 'code': 'var animation := tree.root.get_node("Meadow/Player/character/AnimationPlayer") as AnimationPlayer\nanimation.play("Walk")\nvar skeleton := tree.root.get_node("Meadow/Player").find_child("GeneralSkeleton", true, false) as Skeleton3D\nvar foot := skeleton.find_bone("LeftFoot")\nprint("[game] FOOT start ", skeleton.get_bone_global_pose(foot).origin, " clips ", animation.get_animation_list())'},
        {'op': 'sleep', 'seconds': 0.25}, {'op': 'capture', 'name': 'l42_walk_0', 'frames': 2},
        {'op': 'sleep', 'seconds': 0.25}, {'op': 'capture', 'name': 'l42_walk_1', 'frames': 2},
        {'op': 'sleep', 'seconds': 0.25}, {'op': 'capture', 'name': 'l42_walk_2', 'frames': 2},
        {'op': 'eval', 'code': 'var animation := tree.root.get_node("Meadow/Player/character/AnimationPlayer") as AnimationPlayer\nvar skeleton := tree.root.get_node("Meadow/Player").find_child("GeneralSkeleton", true, false) as Skeleton3D\nprint("[game] FOOT later ", skeleton.get_bone_global_pose(skeleton.find_bone("LeftFoot")).origin, " position ", animation.current_animation_position, " playing ", animation.current_animation)'},
        {'op': 'eval', 'code': 'var animation := tree.root.get_node("Meadow/Player/character/AnimationPlayer") as AnimationPlayer\nanimation.play("Sprint")'},
        {'op': 'sleep', 'seconds': 0.3}, {'op': 'capture', 'name': 'l42_run', 'frames': 2},
        {'op': 'eval', 'code': 'var animation := tree.root.get_node("Meadow/Player/character/AnimationPlayer") as AnimationPlayer\nanimation.play("Idle")'},
        {'op': 'sleep', 'seconds': 0.5}, {'op': 'capture', 'name': 'l42_idle', 'frames': 2},
        {'op': 'quit'}]), 50),
]
write(sys.argv[2], steps)
