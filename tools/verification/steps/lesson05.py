import json
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_popups, dump_windows, add_node, inspector_set, show_row, option_items, view, submenu, INSPECTOR, save_code, build, game_steps, play, open_in_file_dialog, make_folder

piece1 = '''using Godot;

namespace TopDownTemplate.Camera;

public partial class CameraRig : Node3D
{
	[Export] public Camera3D Camera { get; set; } = null!;

	public override void _Ready()
	{
		GD.Print($"Camera size: {Camera.Size}");
	}
}
'''
piece2 = '''using Godot;

namespace TopDownTemplate.Camera;

public partial class CameraRig : Node3D
{
	private static readonly StringName ZoomIn = "zoom_in";
	private static readonly StringName ZoomOut = "zoom_out";

	[Export] public Camera3D Camera { get; set; } = null!;

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event.IsActionPressed(ZoomIn))
		{
			Camera.Size /= 1.15f;
		}
		else if (@event.IsActionPressed(ZoomOut))
		{
			Camera.Size *= 1.15f;
		}
	}
}
'''
piece3 = '''using Godot;

namespace TopDownTemplate.Camera;

// Zooms an orthographic camera with the zoom_in and zoom_out actions.
public partial class CameraRig : Node3D
{
	private static readonly StringName ZoomIn = "zoom_in";
	private static readonly StringName ZoomOut = "zoom_out";

	[Export] public Camera3D Camera { get; set; } = null!;

	// The smallest and largest view heights, in meters.
	[Export] public float MinSize { get; set; } = 8f;
	[Export] public float MaxSize { get; set; } = 48f;

	// How much one wheel notch zooms: 1.15 is 15 percent.
	[Export] public float ZoomStep { get; set; } = 1.15f;

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event.IsActionPressed(ZoomIn))
		{
			Camera.Size = Mathf.Clamp(Camera.Size / ZoomStep, MinSize, MaxSize);
		}
		else if (@event.IsActionPressed(ZoomOut))
		{
			Camera.Size = Mathf.Clamp(Camera.Size * ZoomStep, MinSize, MaxSize);
		}
	}
}
'''
PIECES = [piece1, piece2, piece3]
SCRIPT = 'res://src/Camera/CameraRig.cs'


out_dir = os.path.dirname(sys.argv[2])
game_first = game_steps(os.path.join(out_dir, 'game-l05a.jsonl'), [
    {'op': 'wait', 'frames': 90},
    {'op': 'capture', 'name': 'l05_game_first'},
    {'op': 'sleep', 'seconds': 8},
    {'op': 'quit'},
])
game_zoom = game_steps(os.path.join(out_dir, 'game-l05b.jsonl'), [
    {'op': 'wait', 'frames': 90},
    {'op': 'capture', 'name': 'l05_game_default'},
    {'op': 'wheel', 'steps': 20},
    {'op': 'capture', 'name': 'l05_game_zoom_in', 'frames': 10},
    {'op': 'eval', 'code': 'print("[game] size after zoom in ", tree.root.get_camera_3d().size)'},
    {'op': 'wheel', 'steps': -40},
    {'op': 'capture', 'name': 'l05_game_zoom_out', 'frames': 10},
    {'op': 'eval', 'code': 'print("[game] size after zoom out ", tree.root.get_camera_3d().size)'},
    {'op': 'quit'},
])

steps = [
    # Folders for the camera's scene and its code.
    *make_folder('world', 'camera'),
    *make_folder('src', 'Camera'),
    # The rig scene.
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': '3D Scene'}},
    {'op': 'wait', 'frames': 30},
    eval_('editor.get_edited_scene_root().name = "CameraRig"'),
]
steps += add_node('Node3D', 'Pivot')
steps += [inspector_set('rotation', 'Vector3(deg_to_rad(-55), 0, 0)')]
steps += add_node('Camera3D', 'Camera3D', parent='Pivot')
steps += [
    inspector_set('position', 'Vector3(0, 0, 60)'),
    option_items('projection'),
    inspector_set('projection', 1),
    {'op': 'wait', 'frames': 20},
    inspector_set('size', 20.0),
    show_row('projection'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l05_camera_inspector', 'frames': 20},
    eval_('''
var camera := editor.get_edited_scene_root().get_node("Pivot/Camera3D") as Camera3D
print("[probe] camera global position ", camera.global_position, " keep aspect ", camera.keep_aspect, " near ", camera.near, " far ", camera.far)
'''),
    *view('Pivot/Camera3D', wheel=-6),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'l05_rig_scene', 'frames': 20},
    # Save it in world/camera.
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 40},
    open_in_file_dialog('world', 'camera'),
    {'op': 'capture', 'name': 'l05_save_dialog', 'window': 'Save Scene As'},
    {'op': 'wait', 'frames': 20},
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
    # Attach the script.
    {'op': 'select', 'path': '.'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Attach a new or existing script'}},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var language: OptionButton = plugin._collect(window, "OptionButton", "")[0]
		for i in language.item_count:
			if language.get_item_text(i) == "C#":
				language.select(i)
				language.item_selected.emit(i)
		await plugin.get_tree().process_frame
		for edit in plugin._collect(window, "LineEdit", ""):
			if str(edit.text).begins_with("res://"):
				print("[probe] default script path ", edit.text)
				edit.text = "{SCRIPT}"
				edit.text_changed.emit(edit.text)
'''.replace("{SCRIPT}", SCRIPT)),
    {'op': 'wait', 'frames': 30},
    dump_windows(),
    {'op': 'capture', 'name': 'l05_attach_script', 'window': 'Attach Node Script'},
    {'op': 'press', 'find': {'window': 'Attach Node Script', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    eval_(f'print("[probe] template\\n", FileAccess.get_file_as_string("{SCRIPT}"))'),
    {'op': 'capture', 'name': 'l05_script_created', 'frames': 20},
    # Piece 1, built.
    save_code(SCRIPT, piece1),
    *build('l05_built_piece1'),
    {'op': 'select', 'path': '.'},
    {'op': 'wait', 'frames': 30},
    eval_('''
for property in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorProperty", ""):
	print("[probe] rig row ", property.get_edited_property(), " label ", property.label, " ", property.get_class())
'''),
    {'op': 'capture', 'name': 'l05_export_empty', 'frames': 20},
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'Camera', 'type': 'Button', 'text': 'Assign...'}},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': 'Camera3D'},
    {'op': 'capture', 'name': 'l05_select_node', 'window': 'Select a Node'},
    {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l05_export_assigned', 'frames': 20},
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    eval_('print("[probe] camera_rig.tscn\\n", FileAccess.get_file_as_string("res://world/camera/camera_rig.tscn"))'),
    # Put the rig in the meadow.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': '.'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Instantiate a scene file'}},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Select Scene"):
		for edit in plugin._collect(window, "LineEdit", ""):
			edit.text = "camera_rig"
			edit.text_changed.emit(edit.text)
			break
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l05_instantiate', 'window': 'Select Scene'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Select Scene"):
		for button in plugin._collect(window, "Button", ""):
			print("[probe] instantiate button '", button.text, "'")
'''),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Select Scene"):
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.grab_focus()
		for pressed in [true, false]:
			var event := InputEventKey.new()
			event.keycode = KEY_ENTER
			event.pressed = pressed
			window.push_input(event)
			await plugin.get_tree().process_frame
		return ""
return "no Select Scene dialog"
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
var root := editor.get_edited_scene_root()
for child in root.get_children():
	print("[probe] meadow child ", child.name, " ", child.scene_file_path)
'''),
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    # Run it: the first run asks for a main scene.
    *play(game_first, 20, capture_dialog='l05_main_scene_dialog', capture_output='l05_output_piece1', capture_running='l05_running'),
    # Pieces 2 and 3.
    {'op': 'open', 'path': 'res://world/camera/camera_rig.tscn'},
    save_code(SCRIPT, piece2),
    *build(),
    save_code(SCRIPT, piece3),
    *build(),
    {'op': 'select', 'path': '.'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l05_exports_final', 'frames': 20},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    *play(game_zoom, 25),
    eval_('print("[probe] project main scene ", FileAccess.get_file_as_string("res://project.godot").contains("main_scene"))'),
]
write(sys.argv[2], steps)
