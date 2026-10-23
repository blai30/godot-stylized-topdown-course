shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;

void fragment() {
	ALBEDO = texture(albedo_texture, UV).rgb;
}
