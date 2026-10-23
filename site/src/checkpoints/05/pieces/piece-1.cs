using Godot;

namespace TopDownTemplate.Camera;

public partial class CameraRig : Node3D
{
	[Export] public Camera3D Camera { get; set; } = null!;

	public override void _Ready()
	{
		GD.Print($"Camera size: {Camera.Size}");
	}
}
