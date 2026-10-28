# The code lesson 49 types, shared by its step script and the exporter.

PROFILE = '''using Godot;

namespace TopDownTemplate.Generation;

// What makes one generated world: a seed and the noises that shape it. The same profile and seed give the same world on every
// machine.
[Tool]
[GlobalClass]
public partial class GenerationProfile : Resource
{
	// A different seed makes a different world.
	[Export] public int Seed { get; set; } = 1;

	// Low values are lakes, and high values are land.
	[Export] public FastNoiseLite? Terrain { get; set; }

	// High values are where the trees grow thickest.
	[Export] public FastNoiseLite? Forest { get; set; }

	// The terrain noise at a point on the ground, in meters, from -1 to 1.
	public float TerrainAt(Vector2 point)
	{
		return Sample(Terrain, point);
	}

	// The forest noise at a point on the ground, in meters, from -1 to 1.
	public float ForestAt(Vector2 point)
	{
		return Sample(Forest, point);
	}

	// The seed slides the world across the noise, so the noise resources stay as they were saved.
	private float Sample(FastNoiseLite? noise, Vector2 point)
	{
		var offset = new Vector2(Mathf.PosMod(Seed * 7919, 10007), Mathf.PosMod(Seed * 104729, 10007));
		return noise?.GetNoise2Dv(point + offset) ?? 0f;
	}
}
'''

PIECES = [PROFILE]
