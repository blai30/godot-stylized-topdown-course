using Godot;

namespace TopDownTemplate.Ground;

// What one kind of ground means to the game.
[Tool]
[GlobalClass]
public partial class GroundTile : Resource
{
	[Export] public string DisplayName { get; set; } = "";

	// The tile's number in the MeshLibrary.
	[Export] public int Item { get; set; }

	// Which layer the ground sits on, from the lowest at 0.
	[Export] public int Layer { get; set; }

	// How thickly grass grows here, from 0 to 1.
	[Export(PropertyHint.Range, "0,1,0.05")] public float GrassDensity { get; set; }

	// How many of the 1 meter squares of this ground grow a flower, from 0 to 1.
	[Export(PropertyHint.Range, "0,1,0.05")] public float FlowerDensity { get; set; }

	// How many of the 1 meter squares of this ground hold a pebble, and how many a mushroom, from 0 to 1.
	[Export(PropertyHint.Range, "0,1,0.05")] public float PebbleDensity { get; set; }
	[Export(PropertyHint.Range, "0,1,0.05")] public float MushroomDensity { get; set; }

	// How fast the player walks here, as a share of normal speed.
	[Export(PropertyHint.Range, "0,2,0.05")] public float WalkSpeed { get; set; } = 1f;

	// Whether this ground is the bed of a pond or a lake: water lies over it, and the bank kit edges it.
	[Export] public bool IsWater { get; set; }
}
