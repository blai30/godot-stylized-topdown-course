# The code lesson 43 types, shared by its step script and the exporter.

PLAYER_ANIMATION = '''using Godot;

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
'''

# The blend space: the clip at each speed (meters per second), and the length it is stretched to so its planted foot keeps
# still on the ground at that speed: the clip's length times its own stride speed over the speed it is played at.
POINTS = [('idle', 0.0, None), ('jog', 3.5, 1.344), ('run', 6.0, 0.556)]
