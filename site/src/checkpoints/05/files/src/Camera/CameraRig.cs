using Godot;

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
