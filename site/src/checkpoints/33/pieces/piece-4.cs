using Godot;

namespace TopDownTemplate.Player;

// Tells the grass where the player stands, so the blades part around it. Put it on the player.
public partial class PushPoint : Node3D
{
	private static readonly StringName PushPointGlobal = "push_point";

	// How far the push reaches, in meters.
	[Export] public float Radius { get; set; } = 0.6f;

	public override void _Process(double delta)
	{
		var position = GlobalPosition;
		RenderingServer.GlobalShaderParameterSet(PushPointGlobal, new Vector4(position.X, position.Y, position.Z, Radius));
	}

	public override void _ExitTree()
	{
		// A character that is gone pushes nothing.
		RenderingServer.GlobalShaderParameterSet(PushPointGlobal, Vector4.Zero);
	}
}
