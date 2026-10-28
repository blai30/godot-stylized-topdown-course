using Godot;
using Godot.Collections;

namespace TopDownTemplate.Ground;

// Every kind of ground in the game.
[Tool]
[GlobalClass]
public partial class GroundTileSet : Resource
{
	[Export] public Array<GroundTile> Tiles { get; set; } = [];

	// Finds the tile for a MeshLibrary item number.
	public GroundTile? Find(int item)
	{
		foreach (var tile in Tiles)
		{
			if (tile.Item == item)
			{
				return tile;
			}
		}

		return null;
	}

	// Finds the tile with a display name.
	public GroundTile? Find(string displayName)
	{
		foreach (var tile in Tiles)
		{
			if (tile.DisplayName == displayName)
			{
				return tile;
			}
		}

		return null;
	}
}
