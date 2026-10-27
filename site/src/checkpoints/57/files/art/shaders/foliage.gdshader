shader_type spatial;
render_mode cull_disabled;

#include "res://art/shaders/wind.gdshaderinc"

// The leaf atlas from lesson 25, and the color its middle gray becomes.
uniform sampler2D leaf_atlas : filter_linear_mipmap_anisotropic;
uniform vec3 leaf_color : source_color = vec3(0.408, 0.765, 0.263);
// The colors the leaves turn to in autumn, from the atlas's darkest gray to its lightest.
uniform sampler2D autumn_ramp : source_color, filter_linear;
// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;
// How far this tree has turned, from 0 (green) to 1 (autumn).
instance uniform float autumn : hint_range(0.0, 1.0) = 0.0;

// The atlas is a multiplier around 0.5, stored as data: 128 means 1.0, so this gain keeps the leaf color on average.
const float LEAF_GAIN = 255.0 / 128.0;
// The darkest and lightest grays the atlas uses, which the ramp is stretched across.
const vec2 GRAY_RANGE = vec2(0.33, 0.72);
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
	vec3 green = leaf_color * leaf.rgb * LEAF_GAIN;
	// The leaf's gray picks a color from the ramp: darks turn deep red, lights turn yellow.
	float gray = clamp((leaf.r - GRAY_RANGE.x) / (GRAY_RANGE.y - GRAY_RANGE.x), 0.0, 1.0);
	vec3 turned = texture(autumn_ramp, vec2(gray, 0.5)).rgb;
	ALBEDO = mix(green, turned, autumn) * mix(CANOPY_UNDER, CANOPY_TOP, top) * inner;
	ROUGHNESS = 1.0;
}

void light() {
	float wrapped = clamp((dot(NORMAL, LIGHT) + LEAF_WRAP) / (1.0 + LEAF_WRAP), 0.0, 1.0);
	DIFFUSE_LIGHT += wrapped * ATTENUATION * LIGHT_COLOR / PI;
}
