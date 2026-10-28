using Godot;

namespace TopDownTemplate.Player;

// Walks the player one cell at a time, as farming games do: a key press is a step to the next cell, and holding it keeps stepping.
public partial class TileMovement : CharacterBody3D
{
	private static readonly StringName MoveLeft = "move_left";
	private static readonly StringName MoveRight = "move_right";
	private static readonly StringName MoveForward = "move_forward";
	private static readonly StringName MoveBack = "move_back";

	// How wide a cell is, in meters, and how long one step takes, in seconds.
	[Export] public float CellSize { get; set; } = 1f;
	[Export] public float StepSeconds { get; set; } = 0.2f;

	// The middle of the cell the player is walking to, while it walks.
	private Vector3? _destination;

	public override void _Ready()
	{
		// Starts in the middle of the cell it was placed in.
		GlobalPosition = CellCenter(GlobalPosition);
	}

	public override void _PhysicsProcess(double delta)
	{
		if (_destination is null)
		{
			StartStep();
		}

		if (_destination is not Vector3 destination)
		{
			Velocity = Vector3.Zero;
			return;
		}

		var speed = CellSize / StepSeconds;
		var step = speed * (float)delta;
		var remaining = destination - GlobalPosition;
		if (remaining.Length() <= step)
		{
			GlobalPosition = destination;
			_destination = null;
			return;
		}

		// The animation script reads the velocity to choose between standing and walking.
		Velocity = remaining.Normalized() * speed;
		GlobalPosition += Velocity * (float)delta;
	}

	// Turns toward the key held, and steps to the next cell if nothing solid is in it.
	private void StartStep()
	{
		var input = Input.GetVector(MoveLeft, MoveRight, MoveForward, MoveBack);
		if (input == Vector2.Zero)
		{
			return;
		}

		// One direction at a time: the stronger axis wins.
		var direction = Mathf.Abs(input.X) > Mathf.Abs(input.Y) ? new Vector3(Mathf.Sign(input.X), 0f, 0f) : new Vector3(0f, 0f, Mathf.Sign(input.Y));
		LookAt(GlobalPosition + direction, Vector3.Up, true);
		var offset = direction * CellSize;
		if (!TestMove(GlobalTransform, offset))
		{
			_destination = CellCenter(GlobalPosition + offset);
		}
	}

	// The middle of the cell that holds a position, at the same height.
	private Vector3 CellCenter(Vector3 position)
	{
		return new Vector3((Mathf.Floor(position.X / CellSize) + 0.5f) * CellSize, position.Y, (Mathf.Floor(position.Z / CellSize) + 0.5f) * CellSize);
	}
}
