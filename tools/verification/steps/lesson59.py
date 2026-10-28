# Lesson 59, in Godot: clean up and draw the art library's boundary. An audit script finds what breaks the rules; the tree phase moves
# from a script into the shaders, the character's animation script moves into the player, the tile set moves to world/, the vendor
# animation file is renamed to the naming rule, two READMEs are written, and the style rules are enforced by the build.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, game_steps, play, build, make_folder, save_code, quick_load, resource_menu, run_tool_script,
                   open_bottom_panel, close_bottom_panel, click_tab)
from lesson59_pieces import AUDIT, README, ART_README

SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
out_dir = os.path.dirname(sys.argv[2])

# The phase a tree gets from where it stands: the same numbers WindPhase used, now in the wind include.
WIND_FUNCTION = '''// Where a tree stands decides its place in the wind, so a grove does not sway in step.
float tree_phase_at(vec3 tree_origin) {
	return fract(tree_origin.x * 0.37 + tree_origin.z * 0.61);
}

'''
INSTANCE_UNIFORM = '''// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;
'''
CSPROJ_OLD = '    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>\n'
CSPROJ_NEW = '    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>\n' + CSPROJ_OLD
BLOCK_NAMESPACE = '''using Godot;

namespace TopDownTemplate.Camera
{
	public partial class Bad : Node
	{
	}
}
'''


def edit_text(path, old, new):
    # The reader edits the file in their code editor; Godot sees the change on disk.
    return eval_(f'''
var text := FileAccess.get_file_as_string("{path}")
var old_text := {old!r}
if not text.contains(old_text):
	return "{path} does not contain " + old_text.left(40)
var file := FileAccess.open("{path}", FileAccess.WRITE)
file.store_string(text.replace(old_text, {new!r}))
file.close()
''')


def output_text(tag):
    return eval_(f'''
var log = plugin._find_class(plugin.get_tree().root, "EditorLog")
for label in log.find_children("*", "RichTextLabel", true, false):
	print("[probe] output {tag}\\n", label.get_parsed_text())
''')


def clear_output():
    return eval_('''
var log = plugin._find_class(plugin.get_tree().root, "EditorLog")
for button in log.find_children("*", "Button", true, false):
	if button.shortcut and button.shortcut.get_as_text().ends_with("K") and (button.shortcut.get_as_text().contains("Alt") or button.shortcut.get_as_text().contains("Option")):
		button.pressed.emit()
		return ""
''')


def move_file(old, new):
    # What dragging a file onto a folder in the FileSystem dock does: the file and its .import move, and every scene and resource
    # that names the old path is rewritten. (A drag cannot be made by the test harness.)
    return [eval_(f'''
DirAccess.make_dir_recursive_absolute("{new}".get_base_dir())
for suffix in ["", ".import"]:
	if FileAccess.file_exists("{old}" + suffix):
		var error := DirAccess.rename_absolute("{old}" + suffix, "{new}" + suffix)
		if error != OK:
			return "could not move %s: %d" % ["{old}", error]
var old_name := "{old}".get_file()
var new_name := "{new}".get_file()
if FileAccess.file_exists("{new}.import") and old_name != new_name:
	var import_path := "{new}.import"
	var import_text := FileAccess.get_file_as_string(import_path).replace(old_name, new_name)
	var import_file := FileAccess.open(import_path, FileAccess.WRITE)
	import_file.store_string(import_text)
	import_file.close()
var pending := ["res://"]
while not pending.is_empty():
	var folder: String = pending.pop_back()
	for name in DirAccess.get_directories_at(folder):
		if not name.begins_with("."):
			pending.append(folder.path_join(name))
	for name in DirAccess.get_files_at(folder):
		if name.get_extension() in ["tscn", "tres"]:
			var path := folder.path_join(name)
			var text := FileAccess.get_file_as_string(path)
			if text.contains("{old}"):
				var file := FileAccess.open(path, FileAccess.WRITE)
				file.store_string(text.replace("{old}", "{new}"))
				file.close()
				print("[probe] rewrote ", path)
editor.get_resource_filesystem().scan()
'''), {'op': 'sleep', 'seconds': 6}]


def delete_in_dock(path):
    # Selects the file in the FileSystem dock and presses Delete (Cmd+Backspace on macOS), then confirms the dialog.
    return [
        {'op': 'fs', 'path': path},
        {'op': 'wait', 'frames': 30},
        eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "FileSystemDock")
var tree: Tree = plugin._collect(dock, "Tree", "")[0]
tree.grab_focus()
for pressed in [true, false]:
	var event := InputEventKey.new()
	var mac := OS.get_name() == "macOS"
	event.keycode = KEY_BACKSPACE if mac else KEY_DELETE
	event.physical_keycode = event.keycode
	event.meta_pressed = mac
	event.pressed = pressed
	tree.get_viewport().push_input(event)
	await plugin.get_tree().process_frame
'''),
        {'op': 'wait', 'frames': 40},
        {'op': 'capture', 'name': 'l59_delete_dialog', 'window': 'class:DependencyRemoveDialog'},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		print("[probe] delete dialog ", window.get_class(), " ", window.title)
		window.get_ok_button().pressed.emit()
		return ""
return "no delete dialog"
'''),
        {'op': 'wait', 'frames': 40},
    ]


def clear_script():
    # The Script row's arrow opens its menu, and Clear is in it. The row's field would open the script instead.
    return eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "script")
if row == null:
	return "no row script"
editor.get_inspector().ensure_control_visible(row)
var buttons := plugin._collect(row, "Button", "")
buttons[buttons.size() - 1].pressed.emit()
for attempt in 10:
	await plugin.get_tree().process_frame
	for window in plugin._windows(plugin.get_tree().root):
		if window is PopupMenu and window.visible:
			var items := []
			for i in window.item_count:
				items.append(window.get_item_text(i))
			print("[probe] script menu ", items)
			for i in window.item_count:
				if window.get_item_text(i) == "Clear":
					window.id_pressed.emit(window.get_item_id(i))
					window.hide()
					return ""
			window.hide()
return "no Clear in the script menu"
''')


def noon(tag):
    return [
        # Still wind and no cloud shadows, so a frame does not depend on when it was drawn.
        {'op': 'eval', 'code': 'RenderingServer.global_shader_parameter_set("wind_strength", 0.0)\nRenderingServer.global_shader_parameter_set("cloud_strength", 0.0)'},
        {'op': 'eval', 'code': 'var clock := tree.root.get_node("Meadow/WorldEnvironment/Day")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
        {'op': 'wheel', 'steps': 6},
        {'op': 'wait', 'frames': 40},
        {'op': 'capture', 'name': f'l59_{tag}', 'frames': 10},
    ]


PHASES = '''
var report := []
for node in tree.root.get_node("Meadow/Trees").get_children():
	var position: Vector3 = node.global_position
	report.append("%s %.3f" % [node.name, fposmod(position.x * 0.37 + position.z * 0.61, 1.0)])
print("[game] PHASES ", " | ".join(report))
'''
WALK = '''
var player := tree.root.get_node("Meadow/Player")
var animation_tree: AnimationTree = player.find_child("AnimationTree", true, false)
print("[game] velocity ", player.velocity, " animation ", animation_tree.get_script().resource_path if animation_tree.get_script() else "no script", " active ", animation_tree.active, " blend ", animation_tree.get("parameters/blend_position"))
'''


def game(tag, extra=()):
    return game_steps(os.path.join(out_dir, f'game-l59_{tag}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        *noon(tag),
        {'op': 'eval', 'code': PHASES},
        {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(5.5, 0.05, 0.5)\nInput.action_press("move_left")'},
        {'op': 'sleep', 'seconds': 0.8},
        {'op': 'eval', 'code': WALK},
        {'op': 'eval', 'code': 'Input.action_release("move_left")'},
        {'op': 'eval', 'code': 'print("[game] tile set ", tree.root.get_node("Meadow/GroundTiles").get("Tiles").resource_path)'},
        *extra,
        {'op': 'quit'}])


before = game('before')
after = game('after')

steps = [
    {'op': 'sleep', 'seconds': 5},
    # The meadow as it is, to compare with at the end.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(before, 40),
    # The audit.
    eval_('DirAccess.make_dir_recursive_absolute("res://tools")'),
    save_code('res://tools/audit_project.gd', AUDIT),
    eval_('editor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 3},
    clear_output(),
    *run_tool_script('res://tools/audit_project.gd'),
    open_bottom_panel('Output'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l59_audit_before'},
    output_text('audit before'),
    close_bottom_panel(),
    {'op': 'main_screen', 'name': '3D'},
    # The tree phase moves into the shaders.
    edit_text('res://art/shaders/wind.gdshaderinc', '// How far the whole tree leans', WIND_FUNCTION + '// How far the whole tree leans'),
    edit_text('res://art/shaders/bark.gdshader', INSTANCE_UNIFORM, ''),
    edit_text('res://art/shaders/bark.gdshader', 'tree_sway(world_position, tree_origin, tree_phase)', 'tree_sway(world_position, tree_origin, tree_phase_at(tree_origin))'),
    edit_text('res://art/shaders/foliage.gdshader', INSTANCE_UNIFORM, ''),
    edit_text('res://art/shaders/foliage.gdshader', '\tvec3 tree_origin = MODEL_MATRIX[3].xyz;\n', '\tvec3 tree_origin = MODEL_MATRIX[3].xyz;\n\tfloat tree_phase = tree_phase_at(tree_origin);\n'),
    {'op': 'sleep', 'seconds': 3},
]
for scene in ('tree_oak/tree_oak', 'tree_pine/tree_pine', 'bush/bush'):
    steps += [
        {'op': 'open', 'path': f'res://art/nature/{scene}.tscn'},
        {'op': 'main_screen', 'name': '3D'},
        {'op': 'wait', 'frames': 30},
        {'op': 'select', 'path': '.'},
        {'op': 'wait', 'frames': 20},
        eval_('print("[probe] script before ", editor.get_edited_scene_root().get_script())'),
        clear_script(),
        {'op': 'wait', 'frames': 20},
        eval_('print("[probe] script after ", editor.get_edited_scene_root().get_script())'),
    ]
    if scene.startswith('tree_oak'):
        steps += [{'op': 'capture', 'name': 'l59_script_cleared'}]
    steps += [SAVE_SCENE, {'op': 'wait', 'frames': 20}]
steps += [
    # WindPhase has no users left.
    *delete_in_dock('res://src/World/WindPhase.cs'),
    # The character stays script-free in art; the player gives its animation tree the script.
    {'op': 'open', 'path': 'res://art/character/character.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'AnimationTree'},
    {'op': 'wait', 'frames': 20},
    clear_script(),
    {'op': 'wait', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 20},
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    # Right-click > Editable Children, as a menu item does.
    eval_('''
var root := editor.get_edited_scene_root()
root.set_editable_instance(root.get_node("character"), true)
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'character/AnimationTree'},
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'PlayerAnimation'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l59_player_animation'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 20},
    # The tile set is data about the art, so it belongs to the world; the vendor file takes the naming rule.
    *make_folder('world', 'ground'),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    *move_file('res://art/ground/ground_tile_set.tres', 'res://world/ground/ground_tile_set.tres'),
    *move_file('res://art/animations/UAL1_Standard.glb', 'res://art/animations/ual1_standard.glb'),
    {'op': 'sleep', 'seconds': 8},
    edit_text('res://art/animations/README.md', "`UAL1_Standard.glb` is Quaternius's Universal Animation Library (Standard)", "`ual1_standard.glb` is Quaternius's Universal Animation Library (Standard), renamed from the pack's `UAL1_Standard.glb` to follow the project's file naming"),
    {'op': 'fs', 'path': 'res://world/ground/ground_tile_set.tres'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l59_moved'},
    # The READMEs.
    save_code('res://README.md', README),
    save_code('res://art/README.md', ART_README),
    # The audit again.
    clear_output(),
    *run_tool_script('res://tools/audit_project.gd'),
    open_bottom_panel('Output'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l59_audit_after'},
    output_text('audit after'),
    close_bottom_panel(),
    {'op': 'main_screen', 'name': '3D'},
    # The style rules count in the build.
    edit_text('res://TopDownTemplate.csproj', CSPROJ_OLD, CSPROJ_NEW),
    {'op': 'sleep', 'seconds': 3},
    *build('l59_built'),
    # A block-scoped namespace now fails the build.
    save_code('res://src/Camera/Bad.cs', BLOCK_NAMESPACE),
    eval_('editor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 3},
    *build(),
    open_bottom_panel('MSBuild'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l59_style_error'},
    close_bottom_panel(),
    eval_('DirAccess.remove_absolute("res://src/Camera/Bad.cs")\nDirAccess.remove_absolute("res://src/Camera/Bad.cs.uid")\neditor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 3},
    *build('l59_rebuilt'),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(after, 40),
    eval_('print("[probe] project.godot\\n", FileAccess.get_file_as_string("res://project.godot"))'),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
