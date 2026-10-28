using System.Linq;
using Godot;

namespace TopDownTemplate.World;

// A tree that has its own place in the season, set in the Inspector: 0 is green, 1 is autumn.
public partial class AutumnTree : Node3D
{
	private static readonly StringName AutumnParameter = "autumn";

	[Export(PropertyHint.Range, "0,1,0.01")]
	public float Autumn { get; set; }

	public override void _Ready()
	{
		foreach (var mesh in GetChildren().OfType<GeometryInstance3D>())
		{
			mesh.SetInstanceShaderParameter(AutumnParameter, Autumn);
		}
	}
}
