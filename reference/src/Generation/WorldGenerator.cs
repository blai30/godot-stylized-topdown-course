using System.Collections.Generic;
using System.Linq;
using Godot;
using TopDownTemplate.Ground;

namespace TopDownTemplate.Generation;

// Makes the level from a GenerationProfile. Generate paints the ground from the terrain noise, then edges the water with the bank
// and grows the grass and the trees. It remembers the cells it painted, so the next Generate takes those away and paints them
// again, and leaves any cell you painted over by hand as it is. The same profile gives the same level around your work.
[Tool]
public partial class WorldGenerator : Node
{
	// Water this close to the edge of the level, in cells, becomes land, so the level ends on grass.
	private const int EdgeCells = 4;

	// Water and props keep this far from the middle of the level, in cells, so the player starts on open ground.
	private const int SpawnCells = 6;

	[Export] public GenerationProfile? Profile { get; set; }
	[Export] public GroundMap? Ground { get; set; }
	[Export] public BankMap? Bank { get; set; }
	[Export] public GrassScatter? Grass { get; set; }

	// The water's plane, stretched to cover the level.
	[Export] public MeshInstance3D? Water { get; set; }

	// The node the props are added under.
	[Export] public Node3D? Props { get; set; }

	// Whether the game generates the level when it starts, and whether it picks a new seed each time it does.
	[Export] public bool GenerateOnReady { get; set; }
	[Export] public bool NewSeedEachRun { get; set; }

	// The cells the last Generate painted, each as x, y, z and the item painted there. A cell that holds a different item now was
	// painted over by hand, and is left alone.
	[Export] public Godot.Collections.Array<Vector4I> Painted { get; set; } = [];

	[ExportToolButton("Generate")]
	public Callable GenerateButton => Callable.From(Generate);

	[ExportToolButton("Clear")]
	public Callable ClearButton => Callable.From(Clear);

	public override void _Ready()
	{
		if (Engine.IsEditorHint() || !GenerateOnReady)
		{
			return;
		}

		// The new seed is only in memory: the profile's file on disk is not changed.
		if (Profile is not null && NewSeedEachRun)
		{
			Profile.Seed = (int)GD.Randi();
		}

		Generate();
	}

	// Empties the level: the ground, its shore, the grass, the props, and the list of what was painted.
	public void Clear()
	{
		Ground?.Clear();
		Bank?.Clear();
		Grass?.Clear();
		ClearProps();
		Painted.Clear();
	}

	public void Generate()
	{
		var water = Ground?.Tiles?.Tiles.FirstOrDefault(tile => tile.IsWater);
		var land = Ground?.Tiles?.Find(Profile?.LandTile ?? "");
		if (Profile is null || Ground is null || Bank is null || Grass is null || Props is null || Water?.Mesh is not PlaneMesh plane || water is null || land is null)
		{
			GD.PushWarning("WorldGenerator needs a Profile, a Ground with a water tile and the land tile, a Bank, Grass, Props, and a Water plane.");
			return;
		}

		var started = Time.GetTicksMsec();
		foreach (var painted in Painted)
		{
			var cell = new Vector3I(painted.X, painted.Y, painted.Z);
			if (Ground.GetCellItem(cell) == painted.W)
			{
				Ground.SetCellItem(cell, (int)GridMap.InvalidCellItem);
			}
		}

		// What is left on the ground was painted by hand.
		var byHand = Ground.GetUsedCells().Select(cell => new Vector2I(cell.X, cell.Z)).ToHashSet();
		var half = Profile.Size / 2;
		var cells = new Dictionary<Vector2I, GroundTile>();
		var generated = new HashSet<Vector2I>();
		for (var x = -half.X; x < half.X; x++)
		{
			for (var z = -half.Y; z < half.Y; z++)
			{
				var cell = new Vector2I(x, z);
				if (byHand.Contains(cell))
				{
					cells[cell] = Ground.Tiles!.Find(Ground.GetCellItem(new Vector3I(x, 0, z))) ?? land;
					continue;
				}

				cells[cell] = IsWater(cell, half) ? water : land;
				generated.Add(cell);
			}
		}

		// Water too narrow for the bank to draw becomes land, until none is left. Water you painted is left as it is.
		for (var narrow = NarrowWater(cells, water, generated); narrow.Count > 0; narrow = NarrowWater(cells, water, generated))
		{
			foreach (var cell in narrow)
			{
				cells[cell] = land;
			}
		}

		Painted.Clear();
		foreach (var cell in generated)
		{
			Ground.SetCellItem(new Vector3I(cell.X, 0, cell.Y), cells[cell].Item);
			Painted.Add(new Vector4I(cell.X, 0, cell.Y, cells[cell].Item));
		}

		Bank.UpdateShore();
		Grass.Scatter();
		var props = PlaceProps(half, byHand);
		var size = new Vector2(Profile.Size.X, Profile.Size.Y) * Ground.CellSize.X;
		Water.Scale = new Vector3(size.X / plane.Size.X, 1f, size.Y / plane.Size.Y);
		GD.Print($"Generated {generated.Count} cells, {cells.Values.Count(tile => tile == water)} of them water, and {props} props, from seed {Profile.Seed}, in {Time.GetTicksMsec() - started} ms.");
	}

	// Whether the terrain at the middle of a cell is below the water level, away from the edge and the middle of the level.
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
	private int PlaceProps(Vector2I half, HashSet<Vector2I> byHand)
	{
		ClearProps();
		var parent = Props!;
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
				if (rule is null || IsKeptClear(cell, half) || byHand.Contains(cell) || roll >= Density(rule, point) || IsNearWater(cell, rule.ShoreDistance)
					|| placed.Any(other => other.DistanceTo(point) < rule.Spacing))
				{
					continue;
				}

				var prop = rule.Scene!.Instantiate<Node3D>();
				prop.Name = $"Prop_{x}_{z}";
				prop.Position = new Vector3(point.X, 0f, point.Y);
				prop.Rotation = new Vector3(0f, turn, 0f);
				prop.Scale = Vector3.One * scale;
				parent.AddChild(prop);
				// Owned by the scene's root, so the scene saves it.
				prop.Owner = Owner;
				placed.Add(point);
			}
		}

		return placed.Count;
	}

	private void ClearProps()
	{
		if (Props is null)
		{
			return;
		}

		foreach (var child in Props.GetChildren())
		{
			Props.RemoveChild(child);
			child.QueueFree();
		}
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

	// The cells among the generated ones that lie in water too narrow for the bank.
	private static List<Vector2I> NarrowWater(Dictionary<Vector2I, GroundTile> cells, GroundTile water, HashSet<Vector2I> generated)
	{
		var narrow = BankMap.NarrowWater(cells.Where(pair => pair.Value == water).Select(pair => pair.Key).ToHashSet());
		return narrow.Where(generated.Contains).ToList();
	}
}
