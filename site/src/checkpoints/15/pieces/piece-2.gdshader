shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// The ground's color: the texture is multiplied by it, and white leaves the texture as it is.
uniform vec3 albedo_tint : source_color = vec3(1.0);

void fragment() {
	ALBEDO = texture(albedo_texture, UV).rgb * albedo_tint;
}
