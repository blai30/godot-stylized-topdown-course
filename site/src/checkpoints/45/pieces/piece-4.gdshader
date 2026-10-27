shader_type spatial;
render_mode unshaded;

// The depth of the frame drawn so far, which the water reads to find what lies behind it.
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;

void fragment() {
	// The view-space position of the opaque surface behind this pixel, rebuilt from its depth.
	float depth = textureLod(depth_texture, SCREEN_UV, 0.0).r;
	vec4 position = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
	vec3 behind = position.xyz / position.w;
	// How much water the view ray crosses before it meets the bed.
	float thickness = length(behind - VERTEX);
	ALBEDO = vec3(thickness);
}
