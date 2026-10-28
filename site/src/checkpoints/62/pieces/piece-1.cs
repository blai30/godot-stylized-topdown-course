using Godot;

namespace TopDownTemplate.Player;

// Walks the player to where the mouse clicks, round whatever the navigation mesh says is in the way.
public partial class ClickMovement : CharacterBody3D
{
	private static readonly Plane Ground = new(Vector3.Up, 0f);

	[Export] public float Speed { get; set; } = 3.5f;

	// How quickly the player speeds up and slows down, in meters per second, per second.
	[Export] public float Acceleration { get; set; } = 30f;

	private NavigationAgent3D _agent = null!;

	public override void _Ready()
	{
		_agent = GetNode<NavigationAgent3D>("Agent");
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event is not InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left } click)
		{
			return;
		}

		var camera = GetViewport().GetCamera3D();
		var point = Ground.IntersectsRay(camera.ProjectRayOrigin(click.Position), camera.ProjectRayNormal(click.Position));
		if (point is Vector3 hit)
		{
			_agent.TargetPosition = hit;
		}
	}

	public override void _PhysicsProcess(double delta)
	{
		var step = (float)delta;
		var target = Vector3.Zero;
		if (!_agent.IsNavigationFinished())
		{
			// Only the walk along the ground counts: the mesh floats a little above it.
			var toNext = _agent.GetNextPathPosition() - GlobalPosition;
			toNext.Y = 0f;
			target = toNext.Normalized() * Speed;
		}

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
