# The code lesson 23 types, shared by its step script and the exporter.
import re

from lesson21_pieces import BUILD_DAY as BUILD_DAY_21

STYLIZED_LIT = '''// Lighting shared by the template's stylized surfaces: wrapped diffuse light and a soft rim.

// The rim's color and strength. DayClock sets them from the day animation.
global uniform vec4 rim_color : source_color;
global uniform float rim_strength;

// How far the light wraps around a surface: 0 is plain diffuse, 1 reaches the far side.
const float WRAP = 0.5;
// How narrow the rim is: a higher power keeps it closer to the silhouette.
const float RIM_POWER = 3.0;

// A faint glow along the silhouette that separates a surface from the ground behind it.
vec3 soft_rim(vec3 view_normal, mat4 inverse_view) {
	// The camera looks along -Z in view space, so a normal turned away from +Z is near the silhouette.
	float edge = pow(1.0 - clamp(view_normal.z, 0.0, 1.0), RIM_POWER);
	// Faces looking up take the whole rim, upright faces half of it, and faces looking down none.
	float world_up = (inverse_view * vec4(view_normal, 0.0)).y;
	float sky = clamp(0.5 + world_up, 0.0, 1.0);
	return rim_color.rgb * rim_strength * edge * sky;
}

void light() {
	// Plain diffuse is the dot product alone. Wrapping shifts it, so the side facing away from the light stays softly lit.
	float wrapped = clamp((dot(NORMAL, LIGHT) + WRAP) / (1.0 + WRAP), 0.0, 1.0);
	DIFFUSE_LIGHT += wrapped * ATTENUATION * LIGHT_COLOR / PI;
}
'''

PALETTE_LIT = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"

// The palette: one swatch for each color of the rocks.
uniform sampler2D palette : source_color, filter_nearest;

void fragment() {
	ALBEDO = texture(palette, UV).rgb;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX);
}
'''

GROUND = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"

// The ground textures from lessons 13 and 14.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// The ground's color: the texture is multiplied by it, and white leaves the texture as it is.
uniform vec3 albedo_tint : source_color = vec3(1.0);
// How many times the texture repeats per meter: 0.5 is once every 2 meters.
uniform float texture_scale = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;
// How far the tile reaches past its cell on each side, in meters.
uniform float overhang = 0.2;
// The GridMap's cell size, in meters.
uniform float cell_size = 0.5;
// Noise that makes the tile's edge ragged, shared by every ground tile.
uniform sampler2D edge_noise : filter_linear_mipmap, repeat_enable;
// How many times the edge noise repeats per meter.
uniform float edge_noise_scale = 0.4;

varying vec3 world_position;
varying vec2 tile_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	tile_position = VERTEX.xz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb * albedo_tint;
	ROUGHNESS = roughness;
	// 0 inside the cell, rising to 1 at the tile's outer edge.
	float outside = length(max(abs(tile_position) - cell_size * 0.5, 0.0)) / overhang;
	// Inside the cell this stays at 0.5 or more, so the cell is always covered; at the outer edge it stays below.
	float noise = texture(edge_noise, world_position.xz * edge_noise_scale).r;
	ALPHA = noise + 0.5 - outside;
	// The same noise, four times as wide, brightens and darkens the ground slowly, so the texture's repeat does not show.
	float tone = texture(edge_noise, world_position.xz * edge_noise_scale * 0.25).r;
	ALBEDO *= 0.75 + 0.5 * tone;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX);
}
'''

DAY_CLOCK = '''using Godot;

namespace TopDownTemplate.World;

// Drives the day animation from a time of day, so a slider, a save file, or a cutscene can set the hour.
[Tool]
public partial class DayClock : AnimationPlayer
{
	private static readonly StringName DayAnimation = "day";
	private static readonly StringName RimColorGlobal = "rim_color";
	private static readonly StringName RimStrengthGlobal = "rim_strength";

	private float _timeOfDay = 0.5f;
	private int _hour = -1;
	private Color _rimColor = new("C6E4FF");
	private float _rimStrength = 0.3f;

	// The time of day from 0 (midnight) to 1, with noon at 0.5.
	[Export(PropertyHint.Range, "0,1,0.001")]
	public float TimeOfDay
	{
		get => _timeOfDay;
		set
		{
			_timeOfDay = Mathf.PosMod(value, 1f);
			Apply();
		}
	}

	// How many real seconds a whole day takes at Speed 1.
	[Export] public float DayLengthSeconds { get; set; } = 600f;

	// A multiplier on how fast the day passes.
	[Export] public float Speed { get; set; } = 1f;

	// Whether the day passes at all. Turn it off to hold one hour.
	[Export] public bool Running { get; set; } = true;

	// The color of the soft rim on surfaces. The day animation keys it, and it goes to the rim_color shader global.
	[Export]
	public Color RimColor
	{
		get => _rimColor;
		set
		{
			_rimColor = value;
			RenderingServer.GlobalShaderParameterSet(RimColorGlobal, value);
		}
	}

	// How strong the soft rim is, from 0 to 1. The day animation keys it, and it goes to the rim_strength shader global.
	[Export(PropertyHint.Range, "0,1,0.01")]
	public float RimStrength
	{
		get => _rimStrength;
		set
		{
			_rimStrength = value;
			RenderingServer.GlobalShaderParameterSet(RimStrengthGlobal, value);
		}
	}

	public override void _Ready()
	{
		Apply();
	}

	public override void _Process(double delta)
	{
		if (Engine.IsEditorHint() || !Running)
		{
			return;
		}

		TimeOfDay += (float)delta * Speed / DayLengthSeconds;
		PrintHour();
	}

	// Puts every animated property where the day animation has it at the current time of day.
	private void Apply()
	{
		if (!IsInsideTree() || !HasAnimation(DayAnimation))
		{
			return;
		}

		AssignedAnimation = DayAnimation;
		Seek(_timeOfDay * GetAnimation(DayAnimation).Length, true);
	}

	private void PrintHour()
	{
		var hour = (int)(_timeOfDay * 24f);
		if (hour == _hour)
		{
			return;
		}

		_hour = hour;
		GD.Print($"{hour:00}:00");
	}
}
'''

# The rim keys for the nine keyframes of the day and the midnight that ends it, from FactoryGame's Meridian table.
RIMS = [('#8FA3E0', '0.25f'), ('#A99BD6', '0.25f'), ('#FFADCC', '0.40f'), ('#FFB8DB', '0.40f'), ('#CFE6FF', '0.30f'),
        ('#C6E4FF', '0.30f'), ('#D2E8FF', '0.30f'), ('#FF9E66', '0.45f'), ('#B79AD0', '0.30f'), ('#8FA3E0', '0.25f')]


def build_day():
    text = BUILD_DAY_21
    text = text.replace('string ShadowTint, string HighlightTint, float GradeStrength, float GradeSaturation);',
                        'string ShadowTint, string HighlightTint, float GradeStrength, float GradeSaturation,\n\t\tstring RimColor, float RimStrength);')
    lines = text.split('\n')
    start = next(i for i, line in enumerate(lines) if 'Looks =' in line)
    row = 0
    for i in range(start, len(lines)):
        if lines[i].startswith('\t\tnew('):
            color, strength = RIMS[row]
            lines[i] = re.sub(r'\),$', f', "{color}", {strength}),', lines[i])
            row += 1
    assert row == len(RIMS)
    text = '\n'.join(lines)
    text = text.replace('''			Insert(animation, "Grade/Screen:material:shader_parameter/saturation", key.Time, key.GradeSaturation);
''', '''			Insert(animation, "Grade/Screen:material:shader_parameter/saturation", key.Time, key.GradeSaturation);
			Insert(animation, "Day:RimColor", key.Time, Color.FromHtml(key.RimColor));
			Insert(animation, "Day:RimStrength", key.Time, key.RimStrength);
''')
    text = text.replace('// The ambient light, the sky, the fog, the glow, and the color grade.', '// The ambient light, the sky, the fog, the glow, the color grade, and the rim.')
    return text


BUILD_DAY = build_day()
