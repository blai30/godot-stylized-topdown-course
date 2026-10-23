using Godot;

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
