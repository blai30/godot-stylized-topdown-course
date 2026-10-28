# The code lesson 51 types, shared by its step script and the exporter.
from lesson50_pieces import PROFILE as PROFILE_50, GENERATOR as GENERATOR_50, replace

RULE = '''using Godot;

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
'''

PROFILE = replace(PROFILE_50, '''	// High values are where the trees grow thickest.
	[Export] public FastNoiseLite? Forest { get; set; }
''', '''	// High values are where the trees grow thickest.
	[Export] public FastNoiseLite? Forest { get; set; }

	// The props that grow, each with its own rules.
	[Export] public Godot.Collections.Array<PropRule> Rules { get; set; } = [];
''')

GENERATOR = GENERATOR_50
GENERATOR = replace(GENERATOR, '''	// Water this close to the middle of the level, in cells, becomes land, so the player starts on dry ground.
	private const int SpawnCells = 6;
''', '''	// Water and props keep this far from the middle of the level, in cells, so the player starts on open ground.
	private const int SpawnCells = 6;
''')
GENERATOR = replace(GENERATOR, '''	// The water's plane, stretched to cover the level.
	[Export] public MeshInstance3D? Water { get; set; }
''', '''	// The water's plane, stretched to cover the level.
	[Export] public MeshInstance3D? Water { get; set; }

	// The node the props are added under.
	[Export] public Node3D? Props { get; set; }
''')
GENERATOR = replace(GENERATOR, "|| Grass is null || Water?.Mesh is not PlaneMesh plane", "|| Grass is null || Props is null || Water?.Mesh is not PlaneMesh plane")
GENERATOR = replace(GENERATOR, "a Bank, Grass, and a Water plane.", "a Bank, Grass, Props, and a Water plane.")
GENERATOR = replace(GENERATOR, '''		Bank.UpdateShore();
		Grass.Scatter();
''', '''		Bank.UpdateShore();
		Grass.Scatter();
		var props = PlaceProps(half);
''')
GENERATOR = replace(GENERATOR, '''		GD.Print($"Generated {cells.Count} cells, {cells.Values.Count(tile => tile == water)} of them water.");''',
                    '''		GD.Print($"Generated {cells.Count} cells, {cells.Values.Count(tile => tile == water)} of them water, and {props} props.");''')
GENERATOR = replace(GENERATOR, '''	// Whether the terrain at the middle of a cell is below the water level, away from the edge and the middle of the level.
	private bool IsWater(Vector2I cell, Vector2I half)
	{
		var edge = Mathf.Min(Mathf.Min(cell.X + half.X, half.X - 1 - cell.X), Mathf.Min(cell.Y + half.Y, half.Y - 1 - cell.Y));
		if (edge < EdgeCells || cell.Length() < SpawnCells)
		{
			return false;
		}

		var point = (new Vector2(cell.X, cell.Y) + Vector2.One / 2f) * Ground!.CellSize.X;
		return Profile!.TerrainAt(point) < Profile.WaterLevel;
	}
''', '''	// Whether the terrain at the middle of a cell is below the water level, away from the edge and the middle of the level.
	private bool IsWater(Vector2I cell, Vector2I half)
	{
		if (IsKeptClear(cell, half))
		{
			return false;
		}

		var point = (new Vector2(cell.X, cell.Y) + Vector2.One / 2f) * Ground!.CellSize.X;
		return Profile!.TerrainAt(point) < Profile.WaterLevel;
	}

	// Whether a cell is too near the edge of the level or its middle to hold water or props.
	private static bool IsKeptClear(Vector2I cell, Vector2I half)
	{
		var edge = Mathf.Min(Mathf.Min(cell.X + half.X, half.X - 1 - cell.X), Mathf.Min(cell.Y + half.Y, half.Y - 1 - cell.Y));
		return edge < EdgeCells || cell.Length() < SpawnCells;
	}

	// Grows the props, one candidate in each square meter, in the same order every time. Each candidate rolls everything it
	// might need whether or not it is used, so a square comes out the same however its neighbors do. Returns how many grew.
	private int PlaceProps(Vector2I half)
	{
		foreach (var child in Props!.GetChildren())
		{
			Props.RemoveChild(child);
			child.QueueFree();
		}

		var rules = Profile!.Rules.Where(rule => rule.Scene is not null).ToList();
		var totalWeight = rules.Sum(rule => rule.Weight);
		var placed = new List<Vector2>();
		var cellSize = Ground!.CellSize.X;
		var extent = new Vector2I(Mathf.FloorToInt(half.X * cellSize), Mathf.FloorToInt(half.Y * cellSize));
		for (var x = -extent.X; x < extent.X; x++)
		{
			for (var z = -extent.Y; z < extent.Y; z++)
			{
				var square = new Vector2I(x, z);
				var random = new RandomNumberGenerator { Seed = SquareSeed(square) };
				var point = new Vector2(x + random.Randf(), z + random.Randf());
				var roll = random.Randf();
				var pick = random.Randf() * totalWeight;
				var turn = random.Randf() * Mathf.Tau;
				var scale = random.RandfRange(0.85f, 1.2f);
				var rule = PickRule(rules, pick);
				var cell = new Vector2I(Mathf.FloorToInt(point.X / cellSize), Mathf.FloorToInt(point.Y / cellSize));
				if (rule is null || IsKeptClear(cell, half) || roll >= Density(rule, point) || IsNearWater(cell, rule.ShoreDistance)
					|| placed.Any(other => other.DistanceTo(point) < rule.Spacing))
				{
					continue;
				}

				var prop = rule.Scene!.Instantiate<Node3D>();
				prop.Name = $"Prop_{x}_{z}";
				prop.Position = new Vector3(point.X, 0f, point.Y);
				prop.Rotation = new Vector3(0f, turn, 0f);
				prop.Scale = Vector3.One * scale;
				Props.AddChild(prop);
				// Owned by the scene's root, so the scene saves it.
				prop.Owner = Owner;
				placed.Add(point);
			}
		}

		return placed.Count;
	}

	// The rule a roll between 0 and the total weight lands on, when the rules take turns along it in order.
	private static PropRule? PickRule(List<PropRule> rules, float pick)
	{
		foreach (var rule in rules)
		{
			pick -= rule.Weight;
			if (pick < 0f)
			{
				return rule;
			}
		}

		return null;
	}

	// How likely a prop is to grow at a point: 0 where the forest noise is at StartsAt, and 1 where it is at FullAt.
	private float Density(PropRule rule, Vector2 point)
	{
		return Mathf.Clamp(Mathf.Remap(Profile!.ForestAt(point), rule.StartsAt, rule.FullAt, 0f, 1f), 0f, 1f);
	}

	// Whether there is water within a distance in meters of a cell.
	private bool IsNearWater(Vector2I cell, float distance)
	{
		var reach = Mathf.CeilToInt(distance / Ground!.CellSize.X);
		for (var x = -reach; x <= reach; x++)
		{
			for (var z = -reach; z <= reach; z++)
			{
				if (new Vector2(x, z).Length() * Ground.CellSize.X <= distance && Ground.IsWater(new Vector3I(cell.X + x, 0, cell.Y + z)))
				{
					return true;
				}
			}
		}

		return false;
	}

	// A number from the square and the seed, the same on every machine.
	private ulong SquareSeed(Vector2I square)
	{
		return unchecked((ulong)((square.X * 73856093) ^ (square.Y * 19349663) ^ (Profile!.Seed * 83492791)));
	}
''')

PIECES = [RULE, PROFILE, GENERATOR]
