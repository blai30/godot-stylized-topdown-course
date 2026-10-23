using Godot;

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
