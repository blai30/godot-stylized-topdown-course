# The code lesson 57 types, shared by its step script and the exporter.
from lesson53_pieces import FOLIAGE


def edit(text, old, new):
    # Each change to lesson 27's shader must land exactly once, so the lesson cannot drift from the shader it edits.
    assert text.count(old) == 1, old
    return text.replace(old, new)


SHADER = edit(FOLIAGE, '''// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;
''', '''// The colors the leaves turn to in autumn, from the atlas's darkest gray to its lightest.
uniform sampler2D autumn_ramp : source_color, filter_linear;
// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;
// How far this tree has turned, from 0 (green) to 1 (autumn).
instance uniform float autumn : hint_range(0.0, 1.0) = 0.0;
''')
SHADER = edit(SHADER, '''// Cards facing up''', '''// The darkest and lightest grays the atlas uses, which the ramp is stretched across.
const vec2 GRAY_RANGE = vec2(0.33, 0.72);
// Cards facing up''')
SHADER = edit(SHADER, '''	ALBEDO = leaf_color * leaf.rgb * LEAF_GAIN * mix(CANOPY_UNDER, CANOPY_TOP, top) * inner;''', '''	vec3 green = leaf_color * leaf.rgb * LEAF_GAIN;
	// The leaf's gray picks a color from the ramp: darks turn deep red, lights turn yellow.
	float gray = clamp((leaf.r - GRAY_RANGE.x) / (GRAY_RANGE.y - GRAY_RANGE.x), 0.0, 1.0);
	vec3 turned = texture(autumn_ramp, vec2(gray, 0.5)).rgb;
	ALBEDO = mix(green, turned, autumn) * mix(CANOPY_UNDER, CANOPY_TOP, top) * inner;''')

AUTUMN_TREE = '''using System.Linq;
using Godot;

namespace TopDownTemplate.World;

// A tree that also has its own place in the season, set in the Inspector: 0 is green, 1 is autumn.
public partial class AutumnTree : WindPhase
{
	private static readonly StringName AutumnParameter = "autumn";

	[Export(PropertyHint.Range, "0,1,0.01")]
	public float Autumn { get; set; }

	public override void _Ready()
	{
		base._Ready();
		foreach (var mesh in GetChildren().OfType<GeometryInstance3D>())
		{
			mesh.SetInstanceShaderParameter(AutumnParameter, Autumn);
		}
	}
}
'''

# Autumn for each oak of the grove, in the order of lesson 28's table.
GROVE_AUTUMN = [0.0, 0.3, 0.6, 1.0, 0.8, 0.15, 0.45]
# The ramp's stops: offset and color in 0 to 1 sRGB, with the hex the reader types.
RAMP = [(0.0, '6B1F14'), (0.45, 'CC4D1A'), (0.75, 'EE8C1F'), (1.0, 'FACC47')]
