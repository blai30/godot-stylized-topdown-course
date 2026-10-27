shader_type spatial;

// The frame drawn so far (the lake bed, the bank, the trees) and its depth.
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;

group_uniforms color;
// What the water looks like when there is a lot of it.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);
// How much of each color the water absorbs per meter the view crosses: red goes first.
uniform vec3 absorption = vec3(3.0, 1.5, 1.0);
// How much of the scatter color shows even over a bed right under the surface.
uniform float min_opacity : hint_range(0.0, 1.0) = 0.25;

group_uniforms reflection;
// What the water reflects on top of Fresnel, which alone is faint at this camera angle.
uniform float reflection_boost : hint_range(0.0, 1.0) = 0.28;
group_uniforms;

// Water's reflectance facing the eye.
const float WATER_F0 = 0.02;

// The scatter's color, set in fragment() for light().
varying vec3 scatter_lit;

// The view-space position of the opaque scene at a screen position.
vec3 scene_at(vec2 uv, mat4 inverse_projection) {
	float depth = textureLod(depth_texture, uv, 0.0).r;
	vec4 position = inverse_projection * vec4(uv * 2.0 - 1.0, depth, 1.0);
	return position.xyz / position.w;
}

void fragment() {
	// How much water the view ray crosses before it meets the bed.
	vec3 behind = scene_at(SCREEN_UV, INV_PROJECTION_MATRIX);
	float thickness = length(behind - VERTEX);

	vec3 bed = textureLod(screen_texture, SCREEN_UV, 0.0).rgb;

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
