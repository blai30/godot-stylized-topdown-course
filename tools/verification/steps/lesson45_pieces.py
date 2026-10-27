# The code lesson 45 types, shared by its step script and the exporter.

GROUND_TILE = '''using Godot;

namespace TopDownTemplate.Ground;

// What one kind of ground means to the game.
[Tool]
[GlobalClass]
public partial class GroundTile : Resource
{
	[Export] public string DisplayName { get; set; } = "";

	// The tile's number in the MeshLibrary.
	[Export] public int Item { get; set; }

	// Which layer the ground sits on, from the lowest at 0.
	[Export] public int Layer { get; set; }

	// How thickly grass grows here, from 0 to 1.
	[Export(PropertyHint.Range, "0,1,0.05")] public float GrassDensity { get; set; }

	// How many of the 1 meter squares of this ground grow a flower, from 0 to 1.
	[Export(PropertyHint.Range, "0,1,0.05")] public float FlowerDensity { get; set; }

	// How many of the 1 meter squares of this ground hold a pebble, and how many a mushroom, from 0 to 1.
	[Export(PropertyHint.Range, "0,1,0.05")] public float PebbleDensity { get; set; }
	[Export(PropertyHint.Range, "0,1,0.05")] public float MushroomDensity { get; set; }

	// How fast the player walks here, as a share of normal speed.
	[Export(PropertyHint.Range, "0,2,0.05")] public float WalkSpeed { get; set; } = 1f;

	// Whether this ground is the bed of a pond or a lake: water lies over it, and the bank kit edges it.
	[Export] public bool IsWater { get; set; }
}
'''

LAKE_BED = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"

// The ground's textures and noise, so the lake bed is silt that continues the ground's own pattern.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// The silt's color: the texture is multiplied by it, a gray-brown darker than the dirt.
uniform vec3 albedo_tint : source_color = vec3(0.45, 0.43, 0.36);
uniform float texture_scale = 0.5;
uniform sampler2D edge_noise : filter_linear_mipmap, repeat_enable;
uniform float edge_noise_scale = 0.4;

varying vec2 world_xz;

void vertex() {
	world_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
}

void fragment() {
	ALBEDO = ground_color(albedo_texture, albedo_tint, texture_scale, edge_noise, edge_noise_scale, world_xz);
	ROUGHNESS = 0.95;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
'''

WATER_FLAT = '''shader_type spatial;
render_mode unshaded;

// What the water looks like when there is a lot of it: a deep blue-slate.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);

void fragment() {
	ALBEDO = scatter_color;
	ALPHA = 0.6;
}
'''

WATER_THICKNESS = '''shader_type spatial;
render_mode unshaded;

// The depth of the frame drawn so far, which the water reads to find what lies behind it.
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;

void fragment() {
	// The view-space position of the opaque surface behind this pixel, rebuilt from its depth.
	float depth = textureLod(depth_texture, SCREEN_UV, 0.0).r;
	vec4 position = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
	vec3 behind = position.xyz / position.w;
	// How much water the view ray crosses before it meets the bed.
	float thickness = length(behind - VERTEX);
	ALBEDO = vec3(thickness);
}
'''

WATER = '''shader_type spatial;
render_mode unshaded;

// The frame drawn so far, with the lake bed and the bank in it, and its depth.
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;

group_uniforms color;
// What the water looks like when there is a lot of it: a deep blue-slate.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);
// How much of each color the water absorbs per meter the view crosses. Red goes first.
uniform vec3 absorption = vec3(3.0, 1.5, 1.0);
// How much of the scatter color shows even over a bed right under the surface.
uniform float min_opacity : hint_range(0.0, 1.0) = 0.25;
group_uniforms;

void fragment() {
	// The view-space position of the opaque surface behind this pixel, rebuilt from its depth.
	float depth = textureLod(depth_texture, SCREEN_UV, 0.0).r;
	vec4 position = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
	vec3 behind = position.xyz / position.w;
	// How much water the view ray crosses before it meets the bed.
	float thickness = length(behind - VERTEX);

	vec3 bed = textureLod(screen_texture, SCREEN_UV, 0.0).rgb;
	// What the water lets through of the bed fades with the thickness, red first, from 1 - min_opacity.
	vec3 transmitted = exp(-absorption * thickness) * (1.0 - min_opacity);
	ALBEDO = bed * transmitted + scatter_color * (1.0 - transmitted);
}
'''

PIECES = [GROUND_TILE, LAKE_BED, WATER_FLAT, WATER_THICKNESS, WATER]
