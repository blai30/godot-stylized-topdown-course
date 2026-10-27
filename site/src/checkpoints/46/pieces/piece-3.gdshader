shader_type spatial;

#include "res://art/shaders/wind.gdshaderinc"

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
group_uniforms;

// Water's reflectance facing the eye.
const float WATER_F0 = 0.02;

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

	// What the water lets through of the bed fades with the thickness, red first, from 1 - min_opacity.
	vec3 transmitted = exp(-absorption * thickness) * (1.0 - min_opacity);

	// Godot's reflection of the sky needs a surface that reflects: a metal tinted by how much it should reflect.
	float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float reflectance = clamp(WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - facing, 5.0) + reflection_boost, 0.0, 1.0);
	// The sky reflects through the metallic channel; the scatter is lit like a surface in light() below, so dusk and
	// night tint it. The bed and the found reflections arrive already lit.
	float sky_share = reflectance;
	scatter_lit = max(scatter_color * (1.0 - transmitted) * (1.0 - reflectance), vec3(0.0001));
	ALBEDO = vec3(sky_share);
	METALLIC = 1.0;
	EMISSION = bed * transmitted * (1.0 - reflectance);
	ROUGHNESS = 0.08;
}

// Each light adds the scatter, wrapped so the side away from the sun keeps some of the sky's light. The sun's color
// turns the water warm at dusk, and a night without a sun leaves it dark.
void light() {
	float wrapped = clamp((dot(NORMAL, LIGHT) + 0.6) / 1.6, 0.0, 1.0);
	SPECULAR_LIGHT += scatter_lit * wrapped * ATTENUATION * LIGHT_COLOR / PI;
}
