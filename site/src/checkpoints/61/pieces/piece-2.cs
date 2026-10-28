using Godot;

namespace TopDownTemplate.Grid;

// Shows which cell of a grid the mouse is over, and says when the mouse moves to a cell or clicks one.
public partial class GridCursor : MeshInstance3D
{
	private static readonly StringName CellSizeParameter = "cell_size";
	private static readonly StringName CellParameter = "cell";
	private static readonly Plane Ground = new(Vector3.Up, 0f);

	[Signal] public delegate void CellHoveredEventHandler(Vector2I cell);
	[Signal] public delegate void CellPickedEventHandler(Vector2I cell);

	// How wide a cell is, in meters.
	[Export] public float CellSize { get; set; } = 1f;

	// The cell under the mouse, once the mouse has moved over the ground.
	private Vector2I? _cell;

	public override void _Ready()
	{
		SetInstanceShaderParameter(CellSizeParameter, CellSize);
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event is InputEventMouseMotion motion)
		{
			Hover(motion.Position);
		}
		else if (@event is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left } && _cell is Vector2I picked)
		{
			EmitSignal(SignalName.CellPicked, picked);
		}
	}

	private void Hover(Vector2 screenPosition)
	{
		var camera = GetViewport().GetCamera3D();
		var point = Ground.IntersectsRay(camera.ProjectRayOrigin(screenPosition), camera.ProjectRayNormal(screenPosition));
		if (point is not Vector3 hit)
		{
			return;
		}

		var cell = new Vector2I(Mathf.FloorToInt(hit.X / CellSize), Mathf.FloorToInt(hit.Z / CellSize));
		if (cell == _cell)
		{
			return;
		}

		_cell = cell;
		SetInstanceShaderParameter(CellParameter, new Vector2(cell.X, cell.Y));
		EmitSignal(SignalName.CellHovered, cell);
	}
}
