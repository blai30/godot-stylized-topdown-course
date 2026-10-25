using Godot;
using TopDownTemplate.Ground;

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

	// The ground to walk on, which sets how fast each kind of ground lets the player go.
	[Export] public GroundMap? Ground { get; set; }

	public override void _PhysicsProcess(double delta)
	{
		var step = (float)delta;
		var input = Input.GetVector(MoveLeft, MoveRight, MoveForward, MoveBack);
		var speed = Input.IsActionPressed(Sprint) ? SprintSpeed : Speed;
		speed *= Ground?.TileAt(GlobalPosition)?.WalkSpeed ?? 1f;
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
