shader_type spatial;

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
