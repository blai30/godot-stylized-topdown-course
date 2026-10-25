shader_type spatial;

// The ground textures from lessons 13 and 14.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// The ground's color: the texture is multiplied by it, and white leaves the texture as it is.
uniform vec3 albedo_tint : source_color = vec3(1.0);
// How many times the texture repeats per meter: 0.5 is once every 2 meters.
uniform float texture_scale = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb * albedo_tint;
	ROUGHNESS = roughness;
}
