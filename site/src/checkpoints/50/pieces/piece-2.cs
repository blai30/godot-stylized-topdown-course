using System.Collections.Generic;
using System.Linq;
using Godot;

namespace TopDownTemplate.Ground;

// Edges every pond with the bank kit. The bank's GridMap sits half a cell off the ground's, so each of its cells is on a corner
// of the ground grid and covers the four ground cells that meet there. Update shore looks at which of the four are water and
// puts the piece that fits, turned to face the water.
[Tool]
public partial class BankMap : GridMap
{
	// A pond narrower than this many cells has walls that meet, and shows no water.
	private const int MinimumWidth = 3;

	// The four cells around a corner are numbered x * 2 + z, with x and z 0 for the lower cell and 1 for the higher.
	// Each piece, as the cells that are water when it is unturned, the way it comes out of Blender.
	private static readonly (string Prefix, (int X, int Z)[] Water)[] Shapes =
	[
		("bank_straight", [(0, 1), (1, 1)]),
		("bank_water_corner", [(1, 1)]),
		("bank_land_corner", [(0, 1), (1, 0), (1, 1)]),
		("bank_diagonal", [(0, 1), (1, 0)]),
	];

	private readonly record struct Placement(string Prefix, int Turns);

	// For each set of water cells around a corner, the piece to place and how many quarter turns it takes.
	private static readonly Dictionary<int, Placement> Placements = BuildPlacements();

	[Export] public GroundMap? Ground { get; set; }

	[ExportToolButton("Update shore")]
	public Callable UpdateShoreButton => Callable.From(UpdateShore);

	private static Dictionary<int, Placement> BuildPlacements()
	{
		var table = new Dictionary<int, Placement>();
		foreach (var (prefix, water) in Shapes)
		{
			for (var turns = 0; turns < 4; turns++)
			{
				var cells = 0;
				foreach (var (x, z) in water)
				{
					var (turnedX, turnedZ) = Turn(x, z, turns);
					cells |= 1 << (turnedX * 2 + turnedZ);
				}

				// A diagonal looks the same after two turns, so its first turns are the ones kept.
				table.TryAdd(cells, new Placement(prefix, turns));
			}
		}

		return table;
	}

	// Where a cell around the corner goes after quarter turns about the vertical axis.
	private static (int X, int Z) Turn(int x, int z, int turns)
	{
		for (var i = 0; i < turns; i++)
		{
			(x, z) = (z, 1 - x);
		}

		return (x, z);
	}

	public void UpdateShore()
	{
		if (Ground is null || MeshLibrary is null)
		{
			GD.PushWarning("BankMap needs a Ground and a MeshLibrary.");
			return;
		}

		var used = Ground.GetUsedCells();
		if (used.Count == 0)
		{
			return;
		}

		Clear();
		var variants = MeshLibrary.GetItemList()
			.GroupBy(item => Shapes.First(shape => MeshLibrary.GetItemName(item).StartsWith(shape.Prefix)).Prefix)
			.ToDictionary(group => group.Key, group => group.Order().ToArray());
		var water = used.Where(Ground.IsWater).Select(cell => new Vector2I(cell.X, cell.Z)).ToHashSet();
		WarnAboutNarrowWater(water);

		var low = new Vector2I(used.Min(cell => cell.X), used.Min(cell => cell.Z));
		var high = new Vector2I(used.Max(cell => cell.X), used.Max(cell => cell.Z));
		var placed = 0;
		for (var x = low.X; x <= high.X + 1; x++)
		{
			for (var z = low.Y; z <= high.Y + 1; z++)
			{
				var cells = 0;
				for (var cornerX = 0; cornerX < 2; cornerX++)
				{
					for (var cornerZ = 0; cornerZ < 2; cornerZ++)
					{
						if (water.Contains(new Vector2I(x - 1 + cornerX, z - 1 + cornerZ)))
						{
							cells |= 1 << (cornerX * 2 + cornerZ);
						}
					}
				}

				if (!Placements.TryGetValue(cells, out var placement))
				{
					continue;
				}

				// The variant comes from the cell, so pressing the button again puts the same pieces in the same places.
				var items = variants[placement.Prefix];
				var item = items[Mathf.PosMod(x * 7 + z * 13, items.Length)];
				var turn = new Basis(Vector3.Up, placement.Turns * Mathf.Pi / 2f);
				SetCellItem(new Vector3I(x, 0, z), item, GetOrthogonalIndexFromBasis(turn));
				placed++;
			}
		}

		GD.Print($"Update shore placed {placed} pieces.");
	}

	// Water that is narrower than MinimumWidth in either direction has walls that meet.
	public static List<Vector2I> NarrowWater(HashSet<Vector2I> water)
	{
		return water.Where(cell => Mathf.Min(Run(water, cell, Vector2I.Right), Run(water, cell, Vector2I.Down)) < MinimumWidth).ToList();
	}

	private static void WarnAboutNarrowWater(HashSet<Vector2I> water)
	{
		var narrow = NarrowWater(water);
		if (narrow.Count > 0)
		{
			GD.PushWarning($"{narrow.Count} water cells lie in water narrower than {MinimumWidth} cells, such as the one at {narrow[0]}.");
		}
	}

	// How many water cells in a row there are through a cell, along a direction and against it.
	private static int Run(HashSet<Vector2I> water, Vector2I cell, Vector2I direction)
	{
		var count = 1;
		for (var next = cell + direction; water.Contains(next); next += direction)
		{
			count++;
		}

		for (var next = cell - direction; water.Contains(next); next -= direction)
		{
			count++;
		}

		return count;
	}
}
