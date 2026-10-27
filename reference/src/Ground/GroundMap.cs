using Godot;

namespace TopDownTemplate.Ground;

// The painted ground, which can say what kind of ground lies at a point.
[Tool]
public partial class GroundMap : GridMap
{
	[Export] public GroundTileSet? Tiles { get; set; }

	// The ground under a point in the world, or null where nothing is painted.
	public GroundTile? TileAt(Vector3 worldPosition)
	{
		var local = ToLocal(worldPosition);
		local.Y = 0f;
		var item = GetCellItem(LocalToMap(local));
		return item == InvalidCellItem ? null : Tiles?.Find(item);
	}

	// Whether the ground in a cell is water.
	public bool IsWater(Vector3I cell)
	{
		var item = GetCellItem(cell);
		return item != InvalidCellItem && Tiles?.Find(item)?.IsWater == true;
	}
}
