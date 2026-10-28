using Godot;

namespace TopDownTemplate.Generation;

// One kind of prop that grows in the forest, and where it may stand.
[Tool]
[GlobalClass]
public partial class PropRule : Resource
{
	[Export] public PackedScene? Scene { get; set; }

	// How often this prop is chosen, against the other rules.
	[Export(PropertyHint.Range, "0,10,0.1")] public float Weight { get; set; } = 1f;

	// The forest noise where this prop starts to grow, and where it grows as thickly as it can.
	[Export(PropertyHint.Range, "-1,1,0.05")] public float StartsAt { get; set; }
	[Export(PropertyHint.Range, "-1,1,0.05")] public float FullAt { get; set; } = 0.5f;

	// The least distance in meters to any other prop, and to water.
	[Export(PropertyHint.Range, "0,10,0.1")] public float Spacing { get; set; } = 2f;
	[Export(PropertyHint.Range, "0,10,0.1")] public float ShoreDistance { get; set; } = 2f;
}
