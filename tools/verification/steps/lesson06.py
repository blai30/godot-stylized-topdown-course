import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, dump_popups, dump_windows, add_node, new_resource, inspector_set, show_row, option_items,
                   unfold_inspector, view, submenu, INSPECTOR, save_code, build, game_steps, play, open_in_file_dialog, make_folder)

piece1 = '''using Godot;

namespace TopDownTemplate.Player;

public partial class PlayerMovement : CharacterBody3D
{
	private static readonly StringName MoveLeft = "move_left";
	private static readonly StringName MoveRight = "move_right";
	private static readonly StringName MoveForward = "move_forward";
	private static readonly StringName MoveBack = "move_back";

	[Export] public float Speed { get; set; } = 3.5f;

	public override void _PhysicsProcess(double delta)
	{
		var input = Input.GetVector(MoveLeft, MoveRight, MoveForward, MoveBack);
		Velocity = new Vector3(input.X, 0f, input.Y) * Speed;
		MoveAndSlide();
	}
}
'''
piece2 = '''using Godot;

namespace TopDownTemplate.Player;

public partial class PlayerMovement : CharacterBody3D
{
	private static readonly StringName MoveLeft = "move_left";
	private static readonly StringName MoveRight = "move_right";
	private static readonly StringName MoveForward = "move_forward";
	private static readonly StringName MoveBack = "move_back";
	private static readonly StringName Sprint = "sprint";

	[Export] public float Speed { get; set; } = 3.5f;
	[Export] public float SprintSpeed { get; set; } = 6f;

	// How quickly the player speeds up and slows down, in meters per second, per second.
	[Export] public float Acceleration { get; set; } = 30f;

	public override void _PhysicsProcess(double delta)
	{
		var step = (float)delta;
		var input = Input.GetVector(MoveLeft, MoveRight, MoveForward, MoveBack);
		var speed = Input.IsActionPressed(Sprint) ? SprintSpeed : Speed;
		var target = new Vector3(input.X, 0f, input.Y) * speed;

		var velocity = Velocity;
		var horizontal = new Vector3(velocity.X, 0f, velocity.Z).MoveToward(target, Acceleration * step);
		velocity.X = horizontal.X;
		velocity.Z = horizontal.Z;
		if (!IsOnFloor())
		{
			velocity += GetGravity() * step;
		}

		Velocity = velocity;
		MoveAndSlide();
	}
}
'''
piece3 = '''using Godot;

namespace TopDownTemplate.Player;

// Walks the player with the move actions and turns it to face where it walks.
public partial class PlayerMovement : CharacterBody3D
{
	private static readonly StringName MoveLeft = "move_left";
	private static readonly StringName MoveRight = "move_right";
	private static readonly StringName MoveForward = "move_forward";
	private static readonly StringName MoveBack = "move_back";
	private static readonly StringName Sprint = "sprint";

	[Export] public float Speed { get; set; } = 3.5f;
	[Export] public float SprintSpeed { get; set; } = 6f;

	// How quickly the player speeds up and slows down, in meters per second, per second.
	[Export] public float Acceleration { get; set; } = 30f;

	public override void _PhysicsProcess(double delta)
	{
		var step = (float)delta;
		var input = Input.GetVector(MoveLeft, MoveRight, MoveForward, MoveBack);
		var speed = Input.IsActionPressed(Sprint) ? SprintSpeed : Speed;
		var target = new Vector3(input.X, 0f, input.Y) * speed;

		var velocity = Velocity;
		var horizontal = new Vector3(velocity.X, 0f, velocity.Z).MoveToward(target, Acceleration * step);
		velocity.X = horizontal.X;
		velocity.Z = horizontal.Z;
		if (!IsOnFloor())
		{
			velocity += GetGravity() * step;
		}

		Velocity = velocity;
		MoveAndSlide();

		if (target != Vector3.Zero)
		{
			// Turns the player's front, +Z, toward where it walks.
			LookAt(GlobalPosition + target, Vector3.Up, true);
		}
	}
}
'''
rig_piece = '''using Godot;

namespace TopDownTemplate.Camera;

// Follows a target and zooms an orthographic camera with the zoom_in and zoom_out actions.
public partial class CameraRig : Node3D
{
	private static readonly StringName ZoomIn = "zoom_in";
	private static readonly StringName ZoomOut = "zoom_out";

	[Export] public Camera3D Camera { get; set; } = null!;

	// The node to follow, such as the player. Leave it empty for a camera that stays put.
	[Export] public Node3D? Target { get; set; }

	// The smallest and largest view heights, in meters.
	[Export] public float MinSize { get; set; } = 8f;
	[Export] public float MaxSize { get; set; } = 48f;

	// How much one wheel notch zooms: 1.15 is 15 percent.
	[Export] public float ZoomStep { get; set; } = 1.15f;

	public override void _Ready()
	{
		if (Target == null)
		{
			return;
		}

		GlobalPosition = Target.GlobalPosition;
		// The rig jumped to its target, so it must not be drawn sliding there.
		ResetPhysicsInterpolation();
	}

	public override void _PhysicsProcess(double delta)
	{
		if (Target != null)
		{
			GlobalPosition = Target.GlobalPosition;
		}
	}

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
PIECES = [piece1, piece2, piece3, rig_piece]
SCRIPT = 'res://src/Player/PlayerMovement.cs'
RIG_SCRIPT = 'res://src/Camera/CameraRig.cs'

POSITION = '''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] player ", "%s" % label, " position ", player.global_position.snapped(Vector3.ONE * 0.01), " yaw ", snappedf(rad_to_deg(player.rotation.y), 0.1), " on floor ", player.is_on_floor(), " rig ", tree.root.get_node("Meadow/CameraRig").global_position.snapped(Vector3.ONE * 0.01))'''


def report(label):
    return {'op': 'eval', 'code': f'var label := "{label}"\n' + POSITION}


out_dir = os.path.dirname(sys.argv[2])
game_walk = game_steps(os.path.join(out_dir, 'game-l06a.jsonl'), [
    {'op': 'wait', 'frames': 60},
    report('start'),
    {'op': 'key', 'key': 'W', 'pressed': True},
    {'op': 'sleep', 'seconds': 1.0},
    {'op': 'key', 'key': 'W', 'pressed': False},
    {'op': 'wait', 'frames': 20},
    report('after W'),
    {'op': 'quit'},
])
game_final = game_steps(os.path.join(out_dir, 'game-l06b.jsonl'), [
    {'op': 'wait', 'frames': 60},
    report('start'),
    {'op': 'capture', 'name': 'l06_game_start'},
    {'op': 'key', 'key': 'D', 'pressed': True},
    {'op': 'sleep', 'seconds': 1.0},
    report('walking D'),
    {'op': 'capture', 'name': 'l06_game_walk_right'},
    {'op': 'key', 'key': 'S', 'pressed': True},
    {'op': 'sleep', 'seconds': 0.6},
    {'op': 'capture', 'name': 'l06_game_walk_diagonal'},
    report('walking D and S'),
    {'op': 'key', 'key': 'D', 'pressed': False},
    {'op': 'key', 'key': 'S', 'pressed': False},
    {'op': 'wait', 'frames': 20},
    {'op': 'key', 'key': 'Shift', 'pressed': True},
    {'op': 'key', 'key': 'W', 'pressed': True},
    {'op': 'sleep', 'seconds': 1.0},
    report('sprinting W'),
    {'op': 'eval', 'code': 'print("[game] sprint speed ", snappedf((tree.root.get_node("Meadow/Player") as CharacterBody3D).velocity.length(), 0.01))'},
    {'op': 'key', 'key': 'W', 'pressed': False},
    {'op': 'key', 'key': 'Shift', 'pressed': False},
    {'op': 'wait', 'frames': 30},
    # A short step back turns the nose toward the camera for the close-up.
    {'op': 'key', 'key': 'D', 'pressed': True},
    {'op': 'key', 'key': 'S', 'pressed': True},
    {'op': 'sleep', 'seconds': 0.15},
    {'op': 'key', 'key': 'S', 'pressed': False},
    {'op': 'key', 'key': 'D', 'pressed': False},
    {'op': 'wait', 'frames': 30},
    {'op': 'wheel', 'steps': 5},
    {'op': 'capture', 'name': 'l06_game_close', 'frames': 10},
    report('stopped'),
    # Walk off the 20 m ground and fall.
    {'op': 'key', 'key': 'A', 'pressed': True},
    {'op': 'sleep', 'seconds': 5.0},
    {'op': 'key', 'key': 'A', 'pressed': False},
    report('off the edge'),
    {'op': 'quit'},
])


def save_scene_in(*folder):
    return [
        {'op': 'menu', 'path': ['Scene', 'Save Scene']},
        {'op': 'wait', 'frames': 40},
        open_in_file_dialog(*folder),
        {'op': 'wait', 'frames': 20},
        {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
        {'op': 'wait', 'frames': 40},
        eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
    ]


def instantiate(query, capture=None):
    steps = [
        {'op': 'select', 'path': '.'},
        {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Instantiate a scene file'}},
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Select Scene"):
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "{query}"
		edit.text_changed.emit(edit.text)
'''),
        {'op': 'wait', 'frames': 30},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Select Scene'})
    steps.append(eval_('''
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
'''))
    return steps + [{'op': 'wait', 'frames': 40}]


steps = [
    *make_folder('world', 'player'),
    *make_folder('src', 'Player'),
    # The player scene: Other Node opens Create New Node for the root.
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'Other Node'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'set_text', 'find': {'window': 'Create New Node', 'type': 'LineEdit', 'nth': 0}, 'text': 'CharacterBody3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l06_create_root', 'window': 'Create New Node'},
    {'op': 'press', 'find': {'window': 'Create New Node', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] root ", root.name, " ", root.get_class())
root.name = "Player"
'''),
    {'op': 'select', 'path': '.'},
    {'op': 'capture', 'name': 'l06_warning', 'frames': 20},
]
# Collision shape.
steps += add_node('CollisionShape3D', 'CollisionShape3D')
steps += [
    {'op': 'capture', 'name': 'l06_shape_added', 'frames': 20},
    eval_('print("[probe] new collision shape holds ", (editor.get_edited_scene_root().get_node("CollisionShape3D") as CollisionShape3D).shape)'),
]
steps += new_resource('shape', 'CapsuleShape3D', nth=-1)
steps += [
    {'op': 'capture', 'name': 'l06_capsule_shape', 'frames': 20},
    eval_('''
var shape := (editor.get_edited_scene_root().get_node("CollisionShape3D") as CollisionShape3D).shape as CapsuleShape3D
print("[probe] capsule shape radius ", shape.radius, " height ", shape.height)
'''),
    inspector_set('radius', 0.3),
    inspector_set('height', 1.8),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l06_capsule_set', 'frames': 20},
    {'op': 'select', 'path': 'CollisionShape3D'},
    inspector_set('position', 'Vector3(0, 0.9, 0)'),
]
# The body you see.
steps += add_node('MeshInstance3D', 'Body')
steps += new_resource('mesh', 'CapsuleMesh', nth=-1)
steps += [
    eval_('''
var mesh := (editor.get_edited_scene_root().get_node("Body") as MeshInstance3D).mesh as CapsuleMesh
print("[probe] capsule mesh radius ", mesh.radius, " height ", mesh.height)
'''),
    inspector_set('radius', 0.3),
    inspector_set('height', 1.8),
    {'op': 'select', 'path': 'Body'},
    inspector_set('position', 'Vector3(0, 0.9, 0)'),
]
# A nose that shows which way the player faces.
steps += add_node('MeshInstance3D', 'Nose')
steps += [
    # A new MeshInstance3D starts with a BoxMesh; clicking it opens its properties.
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'mesh', 'type': 'Button', 'nth': 0}},
    {'op': 'wait', 'frames': 20},
    inspector_set('size', 'Vector3(0.15, 0.15, 0.3)'),
    {'op': 'select', 'path': 'Nose'},
    inspector_set('position', 'Vector3(0, 1.5, 0.3)'),
    # Collision layers on the root.
    {'op': 'select', 'path': '.'},
    inspector_set('collision_layer', 2),
    inspector_set('collision_mask', 1),
    show_row('collision_layer'),
    {'op': 'wait', 'frames': 20},
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "collision_layer")
print("[probe] layer row ", row.label, " ", row.get_class())
'''),
    {'op': 'capture', 'name': 'l06_layers', 'frames': 20},
    {'op': 'main_screen', 'name': '3D'},
    *view('Body', 'Nose', dx=-200, dy=40, wheel=-2),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'l06_player_scene', 'frames': 20},
    *save_scene_in('world', 'player'),
    # The script.
    {'op': 'select', 'path': '.'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Attach a new or existing script'}},
    {'op': 'wait', 'frames': 40},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var language: OptionButton = plugin._collect(window, "OptionButton", "")[0]
		for i in language.item_count:
			if language.get_item_text(i) == "C#":
				language.select(i)
				language.item_selected.emit(i)
		await plugin.get_tree().process_frame
		var path: LineEdit = null
		for edit in plugin._collect(window, "LineEdit", ""):
			if str(edit.text).begins_with("res://"):
				path = edit
		print("[probe] default script path ", path.text)
		var template: OptionButton = plugin._collect(window, "OptionButton", "")[1]
		for i in template.item_count:
			if template.get_item_text(i) == "Node: Default":
				template.select(i)
				template.item_selected.emit(i)
		path.text = "{SCRIPT}"
		path.text_changed.emit(path.text)
'''),
    {'op': 'wait', 'frames': 30},
    dump_windows(),
    {'op': 'capture', 'name': 'l06_attach_script', 'window': 'Attach Node Script'},
    {'op': 'press', 'find': {'window': 'Attach Node Script', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    eval_(f'print("[probe] template class line ", Array(FileAccess.get_file_as_string("{SCRIPT}").split("\\n")).filter(func(l): return l.contains("class")))'),
    save_code(SCRIPT, piece1),
    *build(),
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    # Ground collision in the meadow.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'select', 'path': 'Ground'},
    {'op': 'wait', 'frames': 30},
    eval_('''
for button in plugin._collect(plugin.get_tree().root, "MenuButton", "Mesh"):
	button.show_popup()
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l06_mesh_menu', 'frames': 10},
    eval_('''
for button in plugin._collect(plugin.get_tree().root, "MenuButton", "Mesh"):
	var popup: PopupMenu = button.get_popup()
	popup.hide()
	var items := []
	for i in popup.item_count:
		items.append(popup.get_item_text(i))
	print("[probe] mesh menu ", items)
	for i in popup.item_count:
		if popup.get_item_text(i) == "Create Collision Shape...":
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no Create Collision Shape item"
'''),
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Collision"):
		for option in plugin._collect(window, "OptionButton", ""):
			var items := []
			for i in option.item_count:
				items.append(option.get_item_text(i))
			print("[probe] collision option ", items, " selected ", option.text)
'''),
    {'op': 'capture', 'name': 'l06_collision_dialog', 'window': 'Collision'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Collision"):
		var options := plugin._collect(window, "OptionButton", "")
		for option in options:
			for i in option.item_count:
				if option.get_item_text(i) in ["Static Body Child", "Trimesh"]:
					option.select(i)
					option.item_selected.emit(i)
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l06_collision_dialog_set', 'window': 'Collision'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Collision"):
		for button in plugin._collect(window, "Button", ""):
			print("[probe] collision button '", button.text, "'")
'''),
    {'op': 'press', 'find': {'window': 'Collision', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 40},
    eval_('''
var ground := editor.get_edited_scene_root().get_node("Ground")
for child in ground.get_children():
	print("[probe] ground child ", child.name, " ", child.get_class(), " layer ", child.get("collision_layer"))
	for grandchild in child.get_children():
		print("[probe] ground grandchild ", grandchild.name, " ", grandchild.get_class(), " ", grandchild.get("shape"))
'''),
    # The player in the meadow, after the camera rig.
    *instantiate('player', capture='l06_instantiate'),
    eval_('''
var root := editor.get_edited_scene_root()
for child in root.get_children():
	print("[probe] meadow child ", child.name, " ", child.scene_file_path)
'''),
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    *play(game_walk, 20, capture_output='l06_output_piece1'),
    # Pieces 2 and 3, then the camera follow.
    save_code(SCRIPT, piece2),
    *build(),
    save_code(SCRIPT, piece3),
    *build(),
    save_code(RIG_SCRIPT, rig_piece),
    *build(),
    {'op': 'select', 'path': 'CameraRig'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l06_rig_target_empty', 'frames': 20},
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'Target', 'type': 'Button', 'text': 'Assign...'}},
    {'op': 'wait', 'frames': 40},
    {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': 'Player'},
    {'op': 'capture', 'name': 'l06_select_player', 'window': 'Select a Node'},
    {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l06_rig_target', 'frames': 20},
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'main_screen', 'name': '3D'},
    *view('Player', 'CameraRig', dy=30, wheel=-3),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'l06_meadow_editor', 'frames': 20},
    eval_('print("[probe] meadow.tscn\\n", FileAccess.get_file_as_string("res://levels/meadow.tscn"))'),
    eval_('print("[probe] player.tscn\\n", FileAccess.get_file_as_string("res://world/player/player.tscn"))'),
    *play(game_final, 40, capture_output='l06_output_final', capture_running='l06_running'),
]
write(sys.argv[2], steps)
