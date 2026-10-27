shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 albedo_tint : source_color = vec3(0.45, 0.43, 0.36);
uniform float texture_scale = 0.5;
uniform sampler2D edge_noise : filter_linear_mipmap, repeat_enable;
uniform float edge_noise_scale = 0.4;

uniform sampler2D wave_normals : filter_linear_mipmap, repeat_enable;
uniform float caustics = 0.7;

varying vec2 world_xz;

void vertex() {
	world_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
}

void fragment() {
	ALBEDO = ground_color(albedo_texture, albedo_tint, texture_scale, edge_noise, edge_noise_scale, world_xz);
	// Caustics: two ripple layers drifting across each other, bright where both are near a crest's edge.
	float first = 1.0 - abs(texture(wave_normals, world_xz / 1.7 + vec2(TIME * 0.03, 0.0)).r * 2.0 - 1.0);
	float second = 1.0 - abs(texture(wave_normals, world_xz / 1.1 - vec2(0.0, TIME * 0.045)).g * 2.0 - 1.0);
	ALBEDO *= 1.0 + caustics * pow(first * second, 4.0) * 5.0;
	ROUGHNESS = 0.95;
}
