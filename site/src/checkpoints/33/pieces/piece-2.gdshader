shader_type spatial;
render_mode cull_disabled, world_vertex_coords, specular_disabled;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"
#include "res://art/shaders/ground_cover.gdshaderinc"

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
