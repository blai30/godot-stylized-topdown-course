shader_type spatial;

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
