using Godot;

namespace TopDownTemplate.Player;

// Blends the character's clips by how fast the body it stands in is moving.
public partial class PlayerAnimation : AnimationTree
{
	private static readonly StringName BlendPosition = "parameters/blend_position";

	private CharacterBody3D? _body;

	public override void _Ready()
	{
		// The character is a child of the player's body, so its owner's parent is the body.
		_body = Owner?.GetParent() as CharacterBody3D;

		// Off in the editor, so a saved scene never keeps the pose of a clip, on when the game runs.
		Active = true;
	}

	public override void _Process(double delta)
	{
		if (_body is null)
		{
			return;
		}

		// Only the walk along the ground counts: falling is not a stride.
		var speed = new Vector2(_body.Velocity.X, _body.Velocity.Z).Length();
		Set(BlendPosition, speed);
	}
}
