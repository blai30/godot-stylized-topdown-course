using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace TopDownTemplate.Ground;

// Grows grass, flowers, pebbles, and mushrooms on the painted ground. The Scatter button reads the ground's tiles and
// fills a MultiMeshInstance3D for each model in each block of the world. The result is saved in the scene.
[Tool]
public partial class GrassScatter : Node3D
{
	// A block is this many meters on a side. Each block draws on its own, so the camera skips the blocks it cannot see.
	private const float BlockSize = 16f;

	// Keep this node at the origin, so a point in the world is a point in the node.
	[Export] public GroundMap? Ground { get; set; }

	// A scene with a MeshInstance3D for each model, each with its material, named for what it is: grass_clump_a, flower_daisy,
	// pebble_a, mushroom_a, and so on.
	[Export] public PackedScene? Models { get; set; }

	// Dirt patches: each Decal under this node clears the grass and the props from the ground it covers.
	[Export] public Node3D? Patches { get; set; }

	// A different seed grows a different field.
	[Export] public int Seed { get; set; } = 1;

	// The colors a flower's petals can take, one for each flower.
	[Export] public Color[] FlowerColors { get; set; } = [new("FFD23F"), new("FF7EB6"), new("FFFFFF"), new("8FA9FF")];

	[ExportToolButton("Scatter")]
	public Callable ScatterButton => Callable.From(Scatter);

	// What grows one to a square, besides the clumps: the start of its models' names, and how often the ground grows it.
	private static readonly (string Prefix, Func<GroundTile, float> Density)[] Props =
	[
		("flower", tile => tile.FlowerDensity),
		("pebble", tile => tile.PebbleDensity),
		("mushroom", tile => tile.MushroomDensity),
	];

	private readonly record struct Growth(Transform3D Transform, Color Data);

	public void Scatter()
	{
		if (Ground is null || Models is null)
		{
			GD.PushWarning("GrassScatter needs a Ground and Models.");
			return;
		}

		Clear();
		var models = Models.Instantiate();
		var clumps = FindModels(models, "grass_clump");
		var props = Props.Select(prop => (prop.Density, Models: FindModels(models, prop.Prefix))).Where(prop => prop.Models.Count > 0).ToList();
		var fields = new Dictionary<(string Model, Vector2I Block), List<Growth>>();
		foreach (var square in Squares())
		{
			Grow(square, clumps, props, fields);
		}

		// In a fixed order, so the nodes come out the same every time.
		foreach (var ((model, block), growths) in fields.OrderBy(field => field.Key.Model).ThenBy(field => field.Key.Block.X).ThenBy(field => field.Key.Block.Y))
		{
			Build(models.GetNode<MeshInstance3D>(model), block, growths);
		}

		models.Free();
		GD.Print($"Scattered {fields.Sum(field => field.Value.Count)} in {fields.Count} meshes.");
	}

	public void Clear()
	{
		foreach (var child in GetChildren().OfType<MultiMeshInstance3D>())
		{
			RemoveChild(child);
			child.QueueFree();
		}
	}

	private static List<string> FindModels(Node models, string prefix)
	{
		return models.GetChildren().OfType<MeshInstance3D>()
			.Select(model => model.Name.ToString())
			.Where(name => name.StartsWith(prefix))
			.Order()
			.ToList();
	}

	// The 1 meter squares that cover the painted ground.
	private IEnumerable<Vector2I> Squares()
	{
		var half = Ground!.CellSize.X / 2f;
		var centers = Ground.GetUsedCells().Select(cell => Ground.ToGlobal(Ground.MapToLocal(cell))).ToList();
		var low = new Vector2I(Mathf.FloorToInt(centers.Min(center => center.X) - half), Mathf.FloorToInt(centers.Min(center => center.Z) - half));
		var high = new Vector2I(Mathf.CeilToInt(centers.Max(center => center.X) + half), Mathf.CeilToInt(centers.Max(center => center.Z) + half));
		for (var z = low.Y; z < high.Y; z++)
		{
			for (var x = low.X; x < high.X; x++)
			{
				yield return new Vector2I(x, z);
			}
		}
	}

	// Each square has two clumps, one in each half, and one of each prop. Every roll is drawn whether or not it is used, so
	// a square grows the same however its neighbors are painted.
	private void Grow(Vector2I square, List<string> clumps, List<(Func<GroundTile, float> Density, List<string> Models)> props, Dictionary<(string, Vector2I), List<Growth>> fields)
	{
		var random = new RandomNumberGenerator { Seed = SquareSeed(square) };
		for (var half = 0; half < 2; half++)
		{
			var position = new Vector3(square.X + 0.25f + 0.5f * half + random.RandfRange(-0.2f, 0.2f), 0f, square.Y + random.Randf());
			var roll = random.Randf();
			var model = clumps[random.RandiRange(0, clumps.Count - 1)];
			var growth = Place(position, random, new Color(random.Randf(), 0f, 0f, 0f));
			if (roll < Ground!.TileAt(position)?.GrassDensity && !InPatch(position))
			{
				Add(fields, model, growth);
			}
		}

		foreach (var (density, models) in props)
		{
			var position = new Vector3(square.X + random.Randf(), 0f, square.Y + random.Randf());
			var roll = random.Randf();
			var model = models[random.RandiRange(0, models.Count - 1)];
			// The petal color, which only a flower's petals use.
			var tint = FlowerColors[random.RandiRange(0, FlowerColors.Length - 1)].SrgbToLinear();
			var growth = Place(position, random, new Color(random.Randf(), tint.R, tint.G, tint.B));
			var tile = Ground!.TileAt(position);
			if (tile is not null && roll < density(tile) && !InPatch(position))
			{
				Add(fields, model, growth);
			}
		}
	}

	// Whether a point on the ground lies under one of the dirt patches: inside the ellipse its box makes on the ground.
	private bool InPatch(Vector3 position)
	{
		return Patches?.GetChildren().OfType<Decal>().Any(decal =>
		{
			var local = decal.ToLocal(position);
			var half = decal.Size / 2f;
			return Mathf.Pow(local.X / half.X, 2f) + Mathf.Pow(local.Z / half.Z, 2f) < 1f;
		}) ?? false;
	}

	// A growth at a position, turned any way about the vertical and a little larger or smaller than the model.
	private static Growth Place(Vector3 position, RandomNumberGenerator random, Color data)
	{
		var basis = new Basis(Vector3.Up, random.Randf() * Mathf.Tau).Scaled(Vector3.One * random.RandfRange(0.9f, 1.1f));
		return new Growth(new Transform3D(basis, position), data);
	}

	private static void Add(Dictionary<(string, Vector2I), List<Growth>> fields, string model, Growth growth)
	{
		var block = new Vector2I(Mathf.FloorToInt(growth.Transform.Origin.X / BlockSize), Mathf.FloorToInt(growth.Transform.Origin.Z / BlockSize));
		if (!fields.TryGetValue((model, block), out var growths))
		{
			growths = [];
			fields[(model, block)] = growths;
		}

		growths.Add(growth);
	}

	// A number from the square and the seed, the same on every machine.
	private ulong SquareSeed(Vector2I square)
	{
		return unchecked((ulong)((square.X * 73856093) ^ (square.Y * 19349663) ^ (Seed * 83492791)));
	}

	private void Build(MeshInstance3D model, Vector2I block, List<Growth> growths)
	{
		var multiMesh = new MultiMesh
		{
			TransformFormat = MultiMesh.TransformFormatEnum.Transform3D,
			UseCustomData = true,
			Mesh = model.Mesh,
			InstanceCount = growths.Count,
		};
		for (var i = 0; i < growths.Count; i++)
		{
			multiMesh.SetInstanceTransform(i, growths[i].Transform);
			multiMesh.SetInstanceCustomData(i, growths[i].Data);
		}

		var instance = new MultiMeshInstance3D
		{
			Name = $"{model.Name}_{block.X}_{block.Y}",
			Multimesh = multiMesh,
			MaterialOverride = model.MaterialOverride,
			CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
		};
		AddChild(instance);
		// Owned by the scene's root, so the scene saves it.
		instance.Owner = Owner ?? this;
	}
}
