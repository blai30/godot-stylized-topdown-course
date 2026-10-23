using Godot;

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
