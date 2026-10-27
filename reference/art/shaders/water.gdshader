shader_type spatial;
render_mode unshaded;

// The frame drawn so far, with the lake bed and the bank in it, and its depth.
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;

group_uniforms color;
// What the water looks like when there is a lot of it: a deep blue-slate.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);
// How much of each color the water absorbs per meter the view crosses. Red goes first.
uniform vec3 absorption = vec3(3.0, 1.5, 1.0);
// How much of the scatter color shows even over a bed right under the surface.
uniform float min_opacity : hint_range(0.0, 1.0) = 0.25;
group_uniforms;

void fragment() {
	// The view-space position of the opaque surface behind this pixel, rebuilt from its depth.
	float depth = textureLod(depth_texture, SCREEN_UV, 0.0).r;
	vec4 position = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
	vec3 behind = position.xyz / position.w;
	// How much water the view ray crosses before it meets the bed.
	float thickness = length(behind - VERTEX);

	vec3 bed = textureLod(screen_texture, SCREEN_UV, 0.0).rgb;
	// What the water lets through of the bed fades with the thickness, red first, from 1 - min_opacity.
	vec3 transmitted = exp(-absorption * thickness) * (1.0 - min_opacity);
	ALBEDO = bed * transmitted + scatter_color * (1.0 - transmitted);
}
