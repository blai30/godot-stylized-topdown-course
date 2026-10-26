# The code lesson 28 types, shared by its step script and the exporter.

WIND_PHASE = '''using System.Linq;
using Godot;

namespace TopDownTemplate.World;

// Gives a tree its own place in the wind, so a grove does not sway in step.
public partial class WindPhase : Node3D
{
	private static readonly StringName PhaseParameter = "tree_phase";

	public override void _Ready()
	{
		// A number from 0 up to 1 made from where the tree stands, so every tree has its own and keeps it.
		var phase = Mathf.PosMod(GlobalPosition.X * 0.37f + GlobalPosition.Z * 0.61f, 1f);
		foreach (var mesh in GetChildren().OfType<GeometryInstance3D>())
		{
			mesh.SetInstanceShaderParameter(PhaseParameter, phase);
		}
	}
}
'''

# Each tree of the grove: position, turn about the vertical in degrees, and scale.
GROVE = [
    ('TreeOak', (-5, 0, -3), 0, 1.0),
    ('TreeOak2', (-7.5, 0, -0.5), 70, 0.92),
    ('TreeOak3', (-2.6, 0, -4.8), 215, 1.08),
    ('TreeOak4', (4.5, 0, -4.2), 140, 1.0),
    ('TreeOak5', (7.2, 0, -1.5), 300, 0.95),
    ('TreeOak6', (6.0, 0, 3.6), 20, 1.1),
    ('TreeOak7', (-6.2, 0, 3.8), 250, 0.9),
]

# The pines of lesson 29: position, turn about the vertical in degrees, and scale.
PINES = [
    ('TreePine', (1.2, 0, -3.4), 0, 1.0),
    ('TreePine2', (2.8, 0, 3.2), 120, 0.9),
    ('TreePine3', (-1.5, 0, 4.4), 250, 1.1),
]
