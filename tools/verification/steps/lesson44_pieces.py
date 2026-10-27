# The code lesson 44 types, shared by its step script and the exporter.

BANK = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"

// The ground's own textures and noise, so the top of a bank piece is exactly the ground's color and joins the land without a seam.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 albedo_tint : source_color = vec3(1.0);
uniform float texture_scale = 0.5;
uniform sampler2D edge_noise : filter_linear_mipmap, repeat_enable;
uniform float edge_noise_scale = 0.4;

group_uniforms earth;
// The wall's earth, a dark brown: the wall is in its own shadow most of the day.
uniform vec3 earth_color : source_color = vec3(0.44, 0.32, 0.20);
// Clods of earth: one noise shown as a height map and as a normal map, read on the wall's own plane.
uniform sampler2D clod_height : filter_linear_mipmap, repeat_enable;
uniform sampler2D clod_normals : hint_normal, filter_linear_mipmap, repeat_enable;
// How many times the clods repeat per meter.
uniform float clod_scale : hint_range(0.1, 4.0) = 1.0;
// How strongly the clods tilt the light on the wall.
uniform float clod_relief : hint_range(0.0, 2.0) = 0.9;
// How far the wall's light leans toward the sky, so it reads as warm earth and not as a black outline.
uniform float sky_lean : hint_range(0.0, 1.0) = 0.35;
// How much darker the wall is at the water than at the lip.
uniform float depth_darkening : hint_range(0.0, 1.0) = 0.2;
group_uniforms;

group_uniforms turf;
// How far the grass hangs over the top of the wall, in meters, at least and at most.
uniform vec2 turf_length = vec2(0.035, 0.085);
// How many blades hang per meter of wall.
uniform float turf_blades : hint_range(5.0, 60.0) = 30.0;
group_uniforms;

// The height of the bank piece's top, from lesson 44, and how far below it the wall begins.
const float TOP = 0.012;
const float LIP = 0.005;
// How deep the wall's darkening takes to reach full, in meters.
const float WALL_DEPTH = 0.35;

varying vec2 world_xz;
varying vec3 world_normal;
varying float height;

void vertex() {
	world_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
	world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
	height = VERTEX.y;
}

void fragment() {
	// The top is flat at TOP and the wall is below it, so the height alone tells them apart.
	float wall = 1.0 - smoothstep(TOP - LIP - 0.004, TOP - LIP, height);
	vec3 ground = ground_color(albedo_texture, albedo_tint, texture_scale, edge_noise, edge_noise_scale, world_xz);

	// The wall is read on its own vertical plane: along x when it faces along z, and along z otherwise.
	bool along_x = abs(world_normal.z) > abs(world_normal.x);
	vec2 plane = vec2(along_x ? world_xz.x : world_xz.y, height);

	float clod = texture(clod_height, plane * clod_scale).r;
	float depth = clamp((TOP - height) / WALL_DEPTH, 0.0, 1.0);
	vec3 earth = earth_color * (0.8 + 0.4 * clod) * mix(1.0, 1.0 - depth_darkening, depth);
	// Turf hangs over the top of the wall in blades of uneven length.
	float blade = abs(fract(plane.x * turf_blades + texture(edge_noise, world_xz * edge_noise_scale * 2.0).r * 4.0) - 0.5) * 2.0;
	float length_noise = texture(edge_noise, vec2(plane.x * 3.0, 0.5)).r;
	float hang = mix(turf_length.x, turf_length.y, length_noise) * (1.0 - 0.6 * blade);
	earth = mix(earth, ground * 0.85, step(TOP - height, hang));
	ALBEDO = mix(ground, earth, wall);
	ROUGHNESS = 0.95;

	// The clods tilt the wall's normal on its plane, and the whole normal leans toward the sky.
	vec3 bump = texture(clod_normals, plane * clod_scale).xyz * 2.0 - 1.0;
	vec3 across = along_x ? vec3(1.0, 0.0, 0.0) : vec3(0.0, 0.0, 1.0);
	vec3 bumped = normalize(world_normal + clod_relief * (bump.x * across + bump.y * vec3(0.0, 1.0, 0.0)));
	vec3 leaned = normalize(mix(bumped, vec3(0.0, 1.0, 0.0), sky_lean));
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(leaned, 0.0)).xyz, wall));
	// The sky's glow, which the day animation already sets for the rim, lifts the wall that the sun never lights.
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO) + wall * rim_color.rgb * rim_strength * ALBEDO * 2.2;
}
'''

PIECES = [BANK]
