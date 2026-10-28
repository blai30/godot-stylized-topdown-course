using System.Collections.Generic;
using System.Linq;
using Godot;
using TopDownTemplate.Ground;

namespace TopDownTemplate.Generation;

// Makes the level from a GenerationProfile. Generate paints the ground from the terrain noise, then edges the water with the bank
// and grows the grass, as the buttons on those nodes do. It paints the whole ground again each time, so the same profile gives
// the same level.
[Tool]
public partial class WorldGenerator : Node
{
	// Water this close to the edge of the level, in cells, becomes land, so the level ends on grass.
	private const int EdgeCells = 4;

	// Water this close to the middle of the level, in cells, becomes land, so the player starts on dry ground.
	private const int SpawnCells = 6;

	[Export] public GenerationProfile? Profile { get; set; }
	[Export] public GroundMap? Ground { get; set; }
	[Export] public BankMap? Bank { get; set; }
	[Export] public GrassScatter? Grass { get; set; }

	// The water's plane, stretched to cover the level.
	[Export] public MeshInstance3D? Water { get; set; }

	[ExportToolButton("Generate")]
	public Callable GenerateButton => Callable.From(Generate);

	public void Generate()
	{
		var water = Ground?.Tiles?.Tiles.FirstOrDefault(tile => tile.IsWater);
		var land = Ground?.Tiles?.Find(Profile?.LandTile ?? "");
		if (Profile is null || Ground is null || Bank is null || Grass is null || Water?.Mesh is not PlaneMesh plane || water is null || land is null)
		{
			GD.PushWarning("WorldGenerator needs a Profile, a Ground with a water tile and the land tile, a Bank, Grass, and a Water plane.");
			return;
		}

		var half = Profile.Size / 2;
		var cells = new Dictionary<Vector2I, GroundTile>();
		for (var x = -half.X; x < half.X; x++)
		{
			for (var z = -half.Y; z < half.Y; z++)
			{
				var cell = new Vector2I(x, z);
				cells[cell] = IsWater(cell, half) ? water : land;
			}
		}

		// Water too narrow for the bank to draw becomes land, until none is left.
		for (var narrow = NarrowWater(cells, water); narrow.Count > 0; narrow = NarrowWater(cells, water))
		{
			foreach (var cell in narrow)
			{
				cells[cell] = land;
			}
		}

		Ground.Clear();
		foreach (var (cell, tile) in cells)
		{
			Ground.SetCellItem(new Vector3I(cell.X, 0, cell.Y), tile.Item);
		}

		Bank.UpdateShore();
		Grass.Scatter();
		var size = new Vector2(Profile.Size.X, Profile.Size.Y) * Ground.CellSize.X;
		Water.Scale = new Vector3(size.X / plane.Size.X, 1f, size.Y / plane.Size.Y);
		GD.Print($"Generated {cells.Count} cells, {cells.Values.Count(tile => tile == water)} of them water.");
	}

	// Whether the terrain at the middle of a cell is below the water level, away from the edge and the middle of the level.
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

	private static List<Vector2I> NarrowWater(Dictionary<Vector2I, GroundTile> cells, GroundTile water)
	{
		return BankMap.NarrowWater(cells.Where(pair => pair.Value == water).Select(pair => pair.Key).ToHashSet());
	}
}
