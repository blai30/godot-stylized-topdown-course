# The code lesson 27 types, shared by its step script and the exporter.

WIND = '''// Wind for anything that sways: one gust front that crosses the meadow, and the sway and flutter it drives.

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
'''

FOLIAGE = '''shader_type spatial;
render_mode cull_disabled;

#include "res://art/shaders/wind.gdshaderinc"

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
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
'''
