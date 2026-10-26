// The ground's color at a point on the ground: the texture, tinted, brightened and darkened slowly by noise so the
// texture's repeat does not show. The ground shader and the grass share it, so a blade's root is the ground's own color.

// position is in meters (x and z in the world), and the other arguments are the ground shader's own uniforms.
vec3 ground_color(sampler2D albedo_texture, vec3 albedo_tint, float texture_scale, sampler2D edge_noise, float edge_noise_scale, vec2 position) {
	vec3 albedo = texture(albedo_texture, position * texture_scale).rgb * albedo_tint;
	// The same noise as the tile's edge, four times as wide, brightens and darkens the ground slowly.
	float tone = texture(edge_noise, position * edge_noise_scale * 0.25).r;
	return albedo * (0.75 + 0.5 * tone);
}
