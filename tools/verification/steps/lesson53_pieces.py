# The code lesson 53 types, shared by its step script and the exporter. The include is new; the other files are the lesson-52 files with the lines this lesson adds.

CLOUDS = '''// Cloud shadows: one drifting noise that darkens the ground and everything on it, and that the water reflects.
#include "res://art/shaders/wind.gdshaderinc"

// The noise, how many meters it repeats across, and how dark the shadows are, from 0 to 1. Project Settings define them.
global uniform sampler2D cloud_texture : filter_linear_mipmap, repeat_enable;
global uniform float cloud_scale;
global uniform float cloud_strength;

// The clouds drift downwind this many meters a second.
const float CLOUD_SPEED = 0.5;
// The noise values where a cloud starts and where it is solid.
const vec2 CLOUD_EDGE = vec2(0.35, 0.65);

// How much of a point is under cloud, from 0 to 1. time is the shader's TIME.
float cloud_cover(vec2 world_xz, float time) {
	vec2 drifted = world_xz - normalize(wind_direction) * time * CLOUD_SPEED;
	return smoothstep(CLOUD_EDGE.x, CLOUD_EDGE.y, texture(cloud_texture, drifted / cloud_scale).r);
}

// The light a point keeps under the clouds: 1 in the open, less in a shadow.
float cloud_shadow(vec3 world_position, float time) {
	return 1.0 - cloud_cover(world_position.xz, time) * cloud_strength;
}
'''

WIND = '''#ifndef WIND_INCLUDED
#define WIND_INCLUDED

// Wind for anything that sways: one gust front that crosses the meadow, and the sway and flutter it drives.

// Which way the wind blows along the ground (x east, y south), and how hard, from 0 to 1.
global uniform vec2 wind_direction;
global uniform float wind_strength;

// A gust is a long wave that travels downwind. The wind never drops below GUST_FLOOR of its strength.
const float GUST_LENGTH = 24.0;
const float GUST_SECONDS = 8.0;
const float GUST_FLOOR = 0.4;
// A whole tree leans and returns SWAY_HZ times a second, and leans TREE_BEND of its height at the top.
const float SWAY_HZ = 0.5;
const float TREE_BEND = 0.03;
const float CANOPY_HEIGHT = 6.0;
// A card flutters FLUTTER_HZ times a second, up to CARD_FLUTTER meters at its far edge.
const float FLUTTER_HZ = 1.125;
const float CARD_FLUTTER = 0.06;

// The wind's strength here, now: the wave's crest passes each spot in turn, from upwind to downwind.
float gust_strength(vec3 world_position) {
	vec2 heading = normalize(wind_direction);
	float wave = 0.5 + 0.5 * sin(TAU * (TIME / GUST_SECONDS - dot(world_position.xz, heading) / GUST_LENGTH));
	return wind_strength * mix(GUST_FLOOR, 1.0, wave);
}

// How far the whole tree leans at a point on it, in world space. The tree's own phase keeps a grove from swaying in step.
vec3 tree_sway(vec3 world_position, vec3 tree_origin, float tree_phase) {
	vec2 heading = normalize(wind_direction);
	// The top moves most: the lean grows with the square of the height.
	float rise = (world_position.y - tree_origin.y) / CANOPY_HEIGHT;
	float swing = sin(TAU * (tree_phase + SWAY_HZ * TIME));
	float lean = TREE_BEND * CANOPY_HEIGHT * rise * rise * gust_strength(world_position) * swing;
	return vec3(heading.x, 0.0, heading.y) * lean;
}

// How far a card flutters, in world space: along its own direction, more at its far edge, in step with its own phase.
vec3 card_flutter(vec3 world_position, float tree_phase, float card_phase, float far_edge) {
	float angle = TAU * card_phase;
	vec3 direction = vec3(cos(angle), 0.6, sin(angle));
	float beat = sin(TAU * (tree_phase + card_phase + FLUTTER_HZ * TIME));
	return direction * CARD_FLUTTER * far_edge * gust_strength(world_position) * beat;
}

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

#endif
'''

GROUND = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

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
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
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

BANK = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

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
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
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

GRASS = '''shader_type spatial;
render_mode cull_disabled, world_vertex_coords, specular_disabled;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"
#include "res://art/shaders/ground_cover.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

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
	// A clump is wider than a push, so each blade parts by its own spot on the ground, not by the clump's root.
	VERTEX = push_aside(VERTEX, vec3(VERTEX.x, clump_origin.y, VERTEX.z), COLOR.a);

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
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
	ROUGHNESS = 1.0;
	EMISSION = ALBEDO * BOUNCE;
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
#include "res://art/shaders/ground_cover.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

varying vec3 flower_color;

void vertex() {
	// COLOR is the part's own color, and its alpha is 1 on a petal and 0 on the stem and the center. INSTANCE_CUSTOM.x
	// is the flower's phase and INSTANCE_CUSTOM.yzw the color of its petals; a flower that is not in a MultiMesh has
	// neither, so its petals stay white.
	float petal = COLOR.a;
	VERTEX += petal_flutter(VERTEX, INSTANCE_CUSTOM.x, petal);
	// A flower parts by its root: its petals lean away from the character, and the stem stays.
	VERTEX = push_aside(VERTEX, vec3(MODEL_MATRIX[3].x, MODEL_MATRIX[3].y, MODEL_MATRIX[3].z), petal);
	vec3 tint = mix(vec3(1.0), INSTANCE_CUSTOM.yzw, step(0.001, dot(INSTANCE_CUSTOM.yzw, vec3(1.0))));
	flower_color = COLOR.rgb * mix(vec3(1.0), tint, petal);
}

void fragment() {
	ALBEDO = flower_color;
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
	ROUGHNESS = 1.0;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
'''

FOLIAGE = '''shader_type spatial;
render_mode cull_disabled;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

// The leaf atlas from lesson 25, and the color its middle gray becomes.
uniform sampler2D leaf_atlas : filter_linear_mipmap_anisotropic;
uniform vec3 leaf_color : source_color = vec3(0.408, 0.765, 0.263);
// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;

// The atlas is a multiplier around 0.5, stored as data: 128 means 1.0, so this gain keeps the leaf color on average.
const float LEAF_GAIN = 255.0 / 128.0;
// Cards facing up take CANOPY_TOP, lighter and warmer, and cards facing down CANOPY_UNDER, darker and cooler.
const vec3 CANOPY_TOP = vec3(1.25, 1.22, 0.95);
const vec3 CANOPY_UNDER = vec3(0.5, 0.6, 0.6);
// The heights of the card's normal where the grade starts and where it is complete.
const vec2 CANOPY_GRADE = vec2(-0.4, 0.85);
// Leaves deep in the canopy darken to CANOPY_INNER, from the depth CANOPY_DEPTH.y inward to CANOPY_DEPTH.x.
const float CANOPY_INNER = 0.55;
const vec2 CANOPY_DEPTH = vec2(0.3, 0.95);
// Leaves wrap light less than rocks do, so each clump keeps a shaded side.
const float LEAF_WRAP = 0.25;

varying vec3 world_normal;
varying float canopy_depth;
varying float atlas_cell;

void vertex() {
	// The normal stored in lesson 26, kept in world space: Godot flips NORMAL on the back of a card, this does not.
	world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
	canopy_depth = COLOR.b;
	// A card's phase also picks which of the atlas's four sprays it shows.
	atlas_cell = floor(COLOR.r * 3.999);
	vec3 world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 tree_origin = MODEL_MATRIX[3].xyz;
	vec3 wind = tree_sway(world_position, tree_origin, tree_phase) + card_flutter(world_position, tree_phase, COLOR.r, COLOR.g);
	// The shader moves the vertex in model space, so turn the world-space push around.
	VERTEX += inverse(mat3(MODEL_MATRIX)) * wind;
}

void fragment() {
	vec2 cell = vec2(mod(atlas_cell, 2.0), floor(atlas_cell / 2.0));
	vec4 leaf = texture(leaf_atlas, (UV + cell) * 0.5);
	ALPHA = leaf.a;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
	// Light every card with the stored normal, turned to view space.
	NORMAL = normalize((VIEW_MATRIX * vec4(world_normal, 0.0)).xyz);
	float top = smoothstep(CANOPY_GRADE.x, CANOPY_GRADE.y, world_normal.y);
	float inner = mix(CANOPY_INNER, 1.0, smoothstep(CANOPY_DEPTH.x, CANOPY_DEPTH.y, canopy_depth));
	ALBEDO = leaf_color * leaf.rgb * LEAF_GAIN * mix(CANOPY_UNDER, CANOPY_TOP, top) * inner;
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
	ROUGHNESS = 1.0;
}

void light() {
	float wrapped = clamp((dot(NORMAL, LIGHT) + LEAF_WRAP) / (1.0 + LEAF_WRAP), 0.0, 1.0);
	DIFFUSE_LIGHT += wrapped * ATTENUATION * LIGHT_COLOR / PI;
}
'''

BARK = '''shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

// The palette, as for the rocks.
uniform sampler2D palette : source_color, filter_nearest;
// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;

void vertex() {
	vec3 world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 tree_origin = MODEL_MATRIX[3].xyz;
	// The bark leans with the cards, so the limbs stay under their leaves.
	VERTEX += inverse(mat3(MODEL_MATRIX)) * tree_sway(world_position, tree_origin, tree_phase);
}

void fragment() {
	ALBEDO = texture(palette, UV).rgb;
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
'''

WATER = '''shader_type spatial;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

// The frame drawn so far (the lake bed, the bank, the trees) and its depth.
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;
// A seamless normal map of ripples.
uniform sampler2D wave_normals : filter_linear_mipmap, repeat_enable;

group_uniforms color;
// What the water looks like when there is a lot of it.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);
// How much of each color the water absorbs per meter the view crosses: red goes first.
uniform vec3 absorption = vec3(3.0, 1.5, 1.0);
// How much of the scatter color shows even over a bed right under the surface.
uniform float min_opacity : hint_range(0.0, 1.0) = 0.25;
// How much the color wobbles from place to place, as a share.
uniform float color_wobble : hint_range(0.0, 0.6) = 0.3;

group_uniforms waves;
uniform float wave_strength : hint_range(0.0, 2.0) = 0.8;
// How far each of the three layers repeats, in meters, the big one first.
uniform vec3 wave_meters = vec3(30.0, 9.0, 2.5);
// How far each layer drifts a second, in repeats.
uniform vec3 wave_speed = vec3(0.025, 0.06, 0.13);
// Each layer's angle from the wind, in radians, and its weight.
uniform vec3 wave_angle = vec3(0.0, 0.52, -0.7);
uniform vec3 wave_weight = vec3(0.6, 0.45, 0.2);
// The waves calm to nothing where the water is thinner than this, in meters, so the edge stays clean.
uniform float calm_thickness : hint_range(0.0, 1.0) = 0.3;

group_uniforms refraction;
uniform float refraction_strength : hint_range(0.0, 0.2) = 0.06;
// Refraction bends the bed by at most this many meters of water's worth.
uniform float refraction_depth : hint_range(0.0, 4.0) = 1.5;

group_uniforms reflection;
// What the water reflects on top of Fresnel, which alone is faint at this camera angle.
uniform float reflection_boost : hint_range(0.0, 1.0) = 0.28;
// How far the screen-space reflection looks, in meters, and how far behind a surface it still counts as a hit.
uniform float reflect_reach : hint_range(1.0, 16.0) = 8.0;
uniform float reflect_thickness : hint_range(0.1, 4.0) = 1.0;
// The reflection fades out as a pixel grows from x to y meters, where a tree's reflection is a few pixels.
uniform vec2 reflect_fade = vec2(0.06, 0.08);

group_uniforms clouds;
// The reflected clouds lie on a plane this many meters over the water. Their noise and drift are the shadows'.
uniform float cloud_height : hint_range(1.0, 60.0) = 12.0;
uniform float cloud_opacity : hint_range(0.0, 1.0) = 0.3;

group_uniforms edge;
uniform float hairline : hint_range(0.0, 1.0) = 0.35;
uniform vec3 hairline_color : source_color = vec3(0.9, 0.93, 0.95);
// The hairline is as thick as two pixels' worth of the water's thickness, between these two meters.
uniform vec2 hairline_thickness = vec2(0.08, 0.16);
group_uniforms;

// Water's reflectance facing the eye.
const float WATER_F0 = 0.02;
// The reflection march's steps, a constant because a loop needs one.
const int REFLECT_STEPS = 24;
const int REFLECT_REFINE = 4;

// The day animation's sky glow, which also tints the reflected clouds and fades them at night.
global uniform vec4 rim_color : source_color;
global uniform float rim_strength;

varying vec2 world_xz;

// The scatter's color, set in fragment() for light().
varying vec3 scatter_lit;

// The view-space position of the opaque scene at a screen position.
vec3 scene_at(vec2 uv, mat4 inverse_projection) {
	float depth = textureLod(depth_texture, uv, 0.0).r;
	vec4 position = inverse_projection * vec4(uv * 2.0 - 1.0, depth, 1.0);
	return position.xyz / position.w;
}

// The screen position of a view-space position.
vec2 screen_of(vec3 position, mat4 projection) {
	vec4 clip = projection * vec4(position, 1.0);
	return clip.xy / clip.w * 0.5 + 0.5;
}

vec2 rotate(vec2 value, float angle) {
	float cosine = cos(angle);
	float sine = sin(angle);
	return vec2(cosine * value.x - sine * value.y, sine * value.x + cosine * value.y);
}

// The slope of the waves at a point, in world space: three layers of the ripple texture drifting across each other.
vec2 wave_slope(vec2 position, float heading) {
	vec2 slope = vec2(0.0);
	for (int layer = 0; layer < 3; layer++) {
		float angle = heading + wave_angle[layer];
		vec2 frame = rotate(position, -angle) / wave_meters[layer];
		frame.x -= TIME * wave_speed[layer];
		vec2 layer_slope = (texture(wave_normals, frame).rg - 0.5) * 2.0;
		slope += wave_weight[layer] * rotate(layer_slope, angle);
	}
	return slope;
}

// Where a view-space ray first passes behind the opaque scene, refined by bisection: xy the screen position, z how much to trust it.
vec3 reflection_hit(vec3 origin, vec3 direction, mat4 projection, mat4 inverse_projection) {
	float before = 0.0;
	for (int i = 1; i <= REFLECT_STEPS; i++) {
		float along = reflect_reach * float(i) / float(REFLECT_STEPS);
		vec3 point = origin + direction * along;
		vec2 uv = screen_of(point, projection);
		if (any(lessThan(uv, vec2(0.0))) || any(greaterThan(uv, vec2(1.0)))) {
			return vec3(0.0);
		}
		float behind = scene_at(uv, inverse_projection).z - point.z;
		if (behind > 0.0 && behind < reflect_thickness) {
			float after = along;
			for (int refine = 0; refine < REFLECT_REFINE; refine++) {
				float middle = 0.5 * (before + after);
				vec3 probe = origin + direction * middle;
				if (scene_at(screen_of(probe, projection), inverse_projection).z > probe.z) {
					after = middle;
				} else {
					before = middle;
				}
			}
			vec2 hit = screen_of(origin + direction * after, projection);
			vec2 edge = min(hit, 1.0 - hit);
			return vec3(hit, smoothstep(0.0, 0.06, min(edge.x, edge.y)) * (1.0 - after / reflect_reach));
		}
		before = along;
	}
	return vec3(0.0);
}

void vertex() {
	world_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
}

void fragment() {
	// How much water the view ray crosses before it meets the bed.
	vec3 behind = scene_at(SCREEN_UV, INV_PROJECTION_MATRIX);
	float thickness = length(behind - VERTEX);

	// Waves, bigger in the wind and calm where the water is thin.
	vec2 heading_xz = normalize(wind_direction);
	float heading = atan(heading_xz.y, heading_xz.x);
	float strength = wave_strength * mix(0.5, 1.0, wind_strength) * smoothstep(0.0, calm_thickness, thickness);
	vec2 slope = wave_slope(world_xz, heading) * strength;
	vec3 normal_world = normalize(vec3(slope.x, 1.0, slope.y));
	NORMAL = normalize((VIEW_MATRIX * vec4(normal_world, 0.0)).xyz);

	// The bed is read where the waves bend the view ray. A bent sample in front of the surface would show the bank bleeding in, so it falls back.
	vec2 bed_uv = SCREEN_UV;
	vec3 bend = (VIEW_MATRIX * vec4(normal_world.x, 0.0, normal_world.z, 0.0)).xyz * refraction_strength * min(thickness, refraction_depth);
	vec2 bent = SCREEN_UV + screen_of(VERTEX + bend, PROJECTION_MATRIX) - screen_of(VERTEX, PROJECTION_MATRIX);
	vec3 bent_behind = scene_at(bent, INV_PROJECTION_MATRIX);
	if (bent_behind.z < VERTEX.z) {
		bed_uv = bent;
		thickness = length(bent_behind - VERTEX);
	}
	vec3 bed = textureLod(screen_texture, bed_uv, 0.0).rgb;

	// A slow patchwork of noise, for the color's wobble and the foam's ragged width.
	float mottle = 0.6 * texture(wave_normals, world_xz / 7.0 + vec2(TIME * 0.004, 0.0)).g + 0.4 * texture(wave_normals, world_xz / 2.3 - vec2(0.0, TIME * 0.01)).b;

	// What the water lets through of the bed fades with the thickness, red first, from 1 - min_opacity.
	vec3 transmitted = exp(-absorption * thickness) * (1.0 - min_opacity);
	// The color wobbles a little from place to place, as if the water were not quite the same everywhere.
	float wobble = (mottle * 2.0 - 1.0) * color_wobble;

	// Foam where the water is thin: along the bank and around anything standing in it. A noise moves how thin counts, so the edge is ragged.
	float foam_width = clamp(2.0 * fwidth(thickness), hairline_thickness.x, hairline_thickness.y) * (0.5 + 1.5 * mottle);
	float line = hairline * pow(1.0 - smoothstep(0.0, foam_width, thickness), 2.0);

	// Godot's reflection of the sky needs a surface that reflects: a metal tinted by how much it should reflect.
	float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float reflectance = clamp(WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - facing, 5.0) + reflection_boost, 0.0, 1.0);
	// Where the march finds the bank or a tree, their color replaces the sky's.
	vec3 toward_eye = vec3(0.0, 0.0, 1.0);
	vec3 reflected = reflect(-toward_eye, NORMAL);
	float meters_per_pixel = max(length(dFdx(world_xz)), length(dFdy(world_xz)));
	vec3 hit = reflection_hit(VERTEX, reflected, PROJECTION_MATRIX, INV_PROJECTION_MATRIX);
	float found = hit.z * (1.0 - smoothstep(reflect_fade.x, reflect_fade.y, meters_per_pixel));
	vec3 seen = textureLod(screen_texture, hit.xy, 0.0).rgb * found;
	// Clouds on a plane above the water, seen where the waves send the reflection.
	// The waves bend the clouds only a little, or they scatter into speckle.
	vec3 cloud_normal = normalize(mix((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz, NORMAL, 0.3));
	vec3 reflected_world = mat3(INV_VIEW_MATRIX) * reflect(-toward_eye, cloud_normal);
	vec2 cloud_at = world_xz + reflected_world.xz * (cloud_height / max(reflected_world.y, 0.1));
	float cover = cloud_cover(cloud_at, TIME) * cloud_opacity * (1.0 - found);
	vec3 cloud_color = rim_color.rgb * rim_strength * 2.0;
	// The sky reflects through the metallic channel; the scatter is lit like a surface in light() below, so dusk and
	// night tint it. The bed and the found reflections arrive already lit.
	float sky_share = reflectance * (1.0 - found) * (1.0 - cover);
	scatter_lit = pow(max(scatter_color * (1.0 - transmitted) * (1.0 - reflectance), vec3(0.0001)), vec3(1.0 + wobble));
	ALBEDO = vec3(sky_share);
	METALLIC = 1.0;
	EMISSION = (bed * transmitted * (1.0 - reflectance) + seen * reflectance + cloud_color * cover * reflectance) * (1.0 - line) + hairline_color * line;
	ROUGHNESS = mix(0.08, 0.6, line);
}

// Each light adds the scatter, wrapped so the side away from the sun keeps some of the sky's light. The sun's color
// turns the water warm at dusk, and a night without a sun leaves it dark.
void light() {
	float wrapped = clamp((dot(NORMAL, LIGHT) + 0.6) / 1.6, 0.0, 1.0);
	SPECULAR_LIGHT += scatter_lit * wrapped * ATTENUATION * LIGHT_COLOR / PI;
}
'''

PIECES = [CLOUDS, WIND, GROUND, BANK, GRASS, FLOWER, FOLIAGE, BARK, WATER]
