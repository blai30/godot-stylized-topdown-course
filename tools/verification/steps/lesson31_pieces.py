# The code lesson 31 types, shared by its step script and the exporter.
from lesson27_pieces import WIND as WIND_30

GROUND_COLOR = '''// The ground's color at a point on the ground: the texture, tinted, brightened and darkened slowly by noise so the
// texture's repeat does not show. The ground shader and the grass share it, so a blade's root is the ground's own color.

// position is in meters (x and z in the world), and the other arguments are the ground shader's own uniforms.
vec3 ground_color(sampler2D albedo_texture, vec3 albedo_tint, float texture_scale, sampler2D edge_noise, float edge_noise_scale, vec2 position) {
	vec3 albedo = texture(albedo_texture, position * texture_scale).rgb * albedo_tint;
	// The same noise as the tile's edge, four times as wide, brightens and darkens the ground slowly.
	float tone = texture(edge_noise, position * edge_noise_scale * 0.25).r;
	return albedo * (0.75 + 0.5 * tone);
}
'''

GROUND = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"

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
	ALBEDO = ground_color(albedo_texture, albedo_tint, texture_scale, edge_noise, edge_noise_scale, world_position.xz);
	ROUGHNESS = roughness;
	// 0 inside the cell, rising to 1 at the tile's outer edge.
	float outside = length(max(abs(tile_position) - cell_size * 0.5, 0.0)) / overhang;
	// Inside the cell this stays at 0.5 or more, so the cell is always covered; at the outer edge it stays below.
	float noise = texture(edge_noise, world_position.xz * edge_noise_scale).r;
	ALPHA = noise + 0.5 - outside;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
'''

WIND_ADDITION = '''
// A blade's tip sways TIP_SWAY meters along the wind at full strength, bobbing BLADE_HZ times a second, and flutters
// BLADE_FLUTTER meters across it.
const float TIP_SWAY = 0.12;
const float BLADE_FLUTTER = 0.025;
const float BLADE_HZ = 0.8;
// A petal flutters PETAL_FLUTTER meters across the wind, PETAL_HZ times a second.
const float PETAL_FLUTTER = 0.02;
const float PETAL_HZ = 0.5;

// How far a vertex of a grass blade moves, in world space. share is its share of the blade's height, so the foot stays
// put and the tip moves most; the clump's phase and the blade's own keep a field from swaying in step.
vec3 grass_sway(vec3 world_position, float clump_phase, float blade_phase, float share) {
	vec2 heading = normalize(wind_direction);
	vec2 across = vec2(-heading.y, heading.x);
	float beat = TAU * (clump_phase + blade_phase + BLADE_HZ * TIME);
	float reach = share * share * gust_strength(world_position);
	vec2 push = reach * (heading * TIP_SWAY * (0.6 + 0.4 * sin(beat)) + across * BLADE_FLUTTER * sin(2.0 * beat));
	return vec3(push.x, 0.0, push.y);
}

// How far a petal vertex flutters, in world space. mask is 1 on a petal and 0 on the stem and the center.
vec3 petal_flutter(vec3 world_position, float flower_phase, float mask) {
	vec2 heading = normalize(wind_direction);
	vec2 across = vec2(-heading.y, heading.x);
	float beat = TAU * (flower_phase + PETAL_HZ * TIME);
	vec2 push = across * PETAL_FLUTTER * mask * gust_strength(world_position) * sin(2.0 * beat + world_position.x * 5.0);
	return vec3(push.x, 0.0, push.y);
}
'''

WIND = WIND_30 + WIND_ADDITION

GRASS = '''shader_type spatial;
render_mode cull_disabled, world_vertex_coords, specular_disabled;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"

// The ground this grass grows from, as the ground shader draws it: its texture, tint, and noise.
uniform sampler2D ground_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 ground_tint : source_color = vec3(1.0);
uniform float ground_scale = 0.5;
uniform sampler2D field_noise : filter_linear_mipmap, repeat_enable;
uniform float field_noise_scale = 0.4;
// The color of a blade's tip.
uniform vec3 tip_color : source_color = vec3(0.525, 0.733, 0.298);

// A blade runs from the ground's color under it, darkened to ROOT_SHADE, through the middle at MID_AT of its height,
// MID_BLEND of the way to the tip and darkened to MID_SHADE, to the tip's own color.
const float ROOT_SHADE = 0.25;
const float MID_AT = 0.55;
const float MID_BLEND = 0.15;
const float MID_SHADE = 0.6;
// Each clump varies by up to CLUMP_VALUE in value and CLUMP_HUE in hue, and the field by FIELD_VALUE and FIELD_HUE in
// patches FIELD_METERS across.
const float CLUMP_VALUE = 0.06;
const float CLUMP_HUE = 0.06;
const float FIELD_VALUE = 0.1;
const float FIELD_HUE = 0.1;
const float FIELD_METERS = 48.0;
// Light a blade as the ground: its normal leans FLATTEN of the way to up, with the wrap of the ground's light.
const float FLATTEN = 0.85;
const float GRASS_WRAP = 0.5;
// Light that the ground gives back, so the grass in a shadow stays green and not blue: a share of its own color.
const float BOUNCE = 0.1;
// The satin on the tips: its strength, its roughness, how much of the lobe's normal is the blade's own, how far a gust
// bends it downwind, and how much of its tint is the blade's color.
const float SHEEN_STRENGTH = 0.09;
const float SHEEN_ROUGHNESS = 0.55;
const float SHEEN_BLADE_MIX = 0.1;
const float SHEEN_WIND_TILT = 1.0;
const float SHEEN_ALBEDO_TINT = 0.75;

varying vec3 blade_color;
varying float tip_share;
varying float gust;
varying vec3 sheen_normal;

// A number from 0 to 1 made from a place, to vary each clump a little.
float place_hash(vec2 position, vec2 salt) {
	return fract(sin(dot(position, salt)) * 43758.5453);
}

// The color moved toward yellow (shift above 0) or toward blue-green (below 0).
vec3 shift_hue(vec3 color, float shift) {
	return color * vec3(1.0 + shift, 1.0, 1.0 - shift);
}

void vertex() {
	// COLOR.r is the blade's own phase and COLOR.a its share of its height; INSTANCE_CUSTOM.x is the clump's phase.
	tip_share = COLOR.a;
	vec3 clump_origin = MODEL_MATRIX[3].xyz;
	gust = gust_strength(VERTEX);
	VERTEX += grass_sway(VERTEX, INSTANCE_CUSTOM.x, COLOR.r, COLOR.a);

	// The root is the ground's color under the blade; the middle and tip come from it and the tip color.
	vec3 root = ground_color(ground_texture, ground_tint, ground_scale, field_noise, field_noise_scale, VERTEX.xz);
	vec3 middle = mix(root, tip_color, MID_BLEND) * MID_SHADE;
	vec3 color = tip_share < MID_AT ? mix(root * ROOT_SHADE, middle, tip_share / MID_AT) : mix(middle, tip_color, (tip_share - MID_AT) / (1.0 - MID_AT));
	// A little variation: per clump, and across the field.
	float field = texture(field_noise, clump_origin.xz / FIELD_METERS).r - 0.5;
	float clump_value = place_hash(clump_origin.xz, vec2(12.9898, 78.233)) - 0.5;
	float clump_hue = place_hash(clump_origin.xz, vec2(39.3468, 11.135)) - 0.5;
	color = shift_hue(color, 2.0 * (clump_hue * CLUMP_HUE + field * FIELD_HUE));
	blade_color = color * (1.0 + 2.0 * (clump_value * CLUMP_VALUE + field * FIELD_VALUE));
}

void fragment() {
	ALBEDO = blade_color;
	ROUGHNESS = 1.0;
	EMISSION = blade_color * BOUNCE;
	// Every blade takes the ground's up, so the field lights as one matte surface.
	vec3 up = (VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz;
	NORMAL = normalize(mix(NORMAL, up, FLATTEN));
	// The satin's normal: the ground's up, bent downwind by the gust, with a little of the blade's own.
	vec2 heading = normalize(wind_direction);
	vec3 world_up = normalize(vec3(0.0, 1.0, 0.0) + vec3(heading.x, 0.0, heading.y) * SHEEN_WIND_TILT * gust);
	sheen_normal = normalize(mix((VIEW_MATRIX * vec4(world_up, 0.0)).xyz, NORMAL, SHEEN_BLADE_MIX));
}

void light() {
	float n_dot_l = dot(NORMAL, LIGHT);
	vec3 sun = LIGHT_COLOR * ATTENUATION;
	DIFFUSE_LIGHT += sun * clamp((n_dot_l + GRASS_WRAP) / (1.0 + GRASS_WRAP), 0.0, 1.0) / PI;
	// The satin: one broad highlight, on the upper blade.
	vec3 half_vector = normalize(LIGHT + VIEW);
	float n_dot_h = clamp(dot(sheen_normal, half_vector), 0.0, 1.0);
	float alpha2 = pow(SHEEN_ROUGHNESS, 4.0);
	float denominator = n_dot_h * n_dot_h * (alpha2 - 1.0) + 1.0;
	float distribution = alpha2 / (PI * denominator * denominator);
	float mask = smoothstep(0.25, 1.0, tip_share) * clamp(n_dot_l + 0.2, 0.0, 1.0);
	vec3 tint = mix(vec3(1.0), ALBEDO / max(max(ALBEDO.r, ALBEDO.g), max(ALBEDO.b, 0.001)), SHEEN_ALBEDO_TINT);
	// Clamped, so the lobe cannot make bright specks in the glow.
	SPECULAR_LIGHT += sun * tint * min(distribution, 3.0) * SHEEN_STRENGTH * mask;
}
'''

FLOWER = '''shader_type spatial;
render_mode cull_disabled, world_vertex_coords, specular_disabled;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/stylized_lit.gdshaderinc"

varying vec3 flower_color;

void vertex() {
	// COLOR is the part's own color, and its alpha is 1 on a petal and 0 on the stem and the center. INSTANCE_CUSTOM.x
	// is the flower's phase and INSTANCE_CUSTOM.yzw the color of its petals; a flower that is not in a MultiMesh has
	// neither, so its petals stay white.
	float petal = COLOR.a;
	VERTEX += petal_flutter(VERTEX, INSTANCE_CUSTOM.x, petal);
	vec3 tint = mix(vec3(1.0), INSTANCE_CUSTOM.yzw, step(0.001, dot(INSTANCE_CUSTOM.yzw, vec3(1.0))));
	flower_color = COLOR.rgb * mix(vec3(1.0), tint, petal);
}

void fragment() {
	ALBEDO = flower_color;
	ROUGHNESS = 1.0;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
'''
