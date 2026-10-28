# The code lesson 52 types, shared by its step script and the exporter.
import os
from lesson51_pieces import GENERATOR as GENERATOR_51, replace

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_SCATTER = os.path.join(HERE, '..', '..', '..', 'reference', 'src', 'Ground', 'GrassScatter.cs')

SCATTER = open(SNAPSHOT_SCATTER, encoding='utf-8').read().replace('\r\n', '\n').replace('\tprivate void Clear()\n', '\tpublic void Clear()\n')

GENERATOR = GENERATOR_51
GENERATOR = replace(GENERATOR, '''// Makes the level from a GenerationProfile. Generate paints the ground from the terrain noise, then edges the water with the bank
// and grows the grass, as the buttons on those nodes do. It paints the whole ground again each time, so the same profile gives
// the same level.''', '''// Makes the level from a GenerationProfile. Generate paints the ground from the terrain noise, then edges the water with the bank
// and grows the grass and the trees. It remembers the cells it painted, so the next Generate takes those away and paints them
// again, and leaves any cell you painted over by hand as it is. The same profile gives the same level around your work.''')
GENERATOR = replace(GENERATOR, '''	// The node the props are added under.
	[Export] public Node3D? Props { get; set; }
''', '''	// The node the props are added under.
	[Export] public Node3D? Props { get; set; }

	// Whether the game generates the level when it starts, and whether it picks a new seed each time it does.
	[Export] public bool GenerateOnReady { get; set; }
	[Export] public bool NewSeedEachRun { get; set; }

	// The cells the last Generate painted, each as x, y, z and the item painted there. A cell that holds a different item now was
	// painted over by hand, and is left alone.
	[Export] public Godot.Collections.Array<Vector4I> Painted { get; set; } = [];
''')
GENERATOR = replace(GENERATOR, '''	[ExportToolButton("Generate")]
	public Callable GenerateButton => Callable.From(Generate);

	public void Generate()
	{''', '''	[ExportToolButton("Generate")]
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
	{''')
GENERATOR = replace(GENERATOR, '''		var half = Profile.Size / 2;
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
		var props = PlaceProps(half);
''', '''		var started = Time.GetTicksMsec();
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
''')
GENERATOR = replace(GENERATOR, '''		GD.Print($"Generated {cells.Count} cells, {cells.Values.Count(tile => tile == water)} of them water, and {props} props.");''',
                    '''		GD.Print($"Generated {generated.Count} cells, {cells.Values.Count(tile => tile == water)} of them water, and {props} props, from seed {Profile.Seed}, in {Time.GetTicksMsec() - started} ms.");''')
GENERATOR = replace(GENERATOR, '''	private int PlaceProps(Vector2I half)
	{
		foreach (var child in Props!.GetChildren())
		{
			Props.RemoveChild(child);
			child.QueueFree();
		}

''', '''	private int PlaceProps(Vector2I half, HashSet<Vector2I> byHand)
	{
		ClearProps();
		var parent = Props!;
''')
GENERATOR = replace(GENERATOR, "				Props.AddChild(prop);", "				parent.AddChild(prop);")
GENERATOR = replace(GENERATOR, "if (rule is null || IsKeptClear(cell, half) || roll >= Density(rule, point)", "if (rule is null || IsKeptClear(cell, half) || byHand.Contains(cell) || roll >= Density(rule, point)")
GENERATOR = replace(GENERATOR, '''	// The rule a roll between 0 and the total weight lands on''', '''	private void ClearProps()
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

	// The rule a roll between 0 and the total weight lands on''')
GENERATOR = replace(GENERATOR, '''	private static List<Vector2I> NarrowWater(Dictionary<Vector2I, GroundTile> cells, GroundTile water)
	{
		return BankMap.NarrowWater(cells.Where(pair => pair.Value == water).Select(pair => pair.Key).ToHashSet());
	}''', '''	// The cells among the generated ones that lie in water too narrow for the bank.
	private static List<Vector2I> NarrowWater(Dictionary<Vector2I, GroundTile> cells, GroundTile water, HashSet<Vector2I> generated)
	{
		var narrow = BankMap.NarrowWater(cells.Where(pair => pair.Value == water).Select(pair => pair.Key).ToHashSet());
		return narrow.Where(generated.Contains).ToList();
	}''')

PIECES = [SCATTER, GENERATOR]
