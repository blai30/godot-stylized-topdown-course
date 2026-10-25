shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 albedo_tint : source_color = vec3(1.0);
uniform float texture_scale = 0.5;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb * albedo_tint;
}
