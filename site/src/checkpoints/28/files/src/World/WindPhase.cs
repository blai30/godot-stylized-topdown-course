using System.Linq;
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
