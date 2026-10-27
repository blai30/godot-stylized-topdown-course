shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_color.gdshaderinc"

// The ground beside the bank: the top of the bank takes its color, so the two join without a seam.
uniform sampler2D ground_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 ground_tint : source_color = vec3(1.0);
uniform sampler2D dirt_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 dirt_tint : source_color = vec3(0.7, 0.55, 0.42);
// The face is in its own shadow most of the day, so its earth is lighter than the lip's.
uniform vec3 face_color : source_color = vec3(0.44, 0.32, 0.20);
uniform sampler2D edge_noise : filter_linear_mipmap, repeat_enable;
uniform float edge_noise_scale = 0.4;
// Clods of earth: a cellular noise as a height map (cracks are low) and as a normal map, repeating once a meter.
uniform sampler2D clod_height : filter_linear_mipmap, repeat_enable;
uniform sampler2D clod_normals : hint_normal, filter_linear_mipmap, repeat_enable;
uniform float clod_scale = 1.0;
uniform float clod_relief = 0.9;

varying vec2 world_xz;
varying float world_y;
varying vec3 world_normal;

void vertex() {
	vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_xz = world.xz;
	world_y = world.y;
	world_normal = (MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz;
}

void fragment() {
	float face = COLOR.r;
	float broad = texture(edge_noise, world_xz * edge_noise_scale * 2.0).r;

	vec3 land = ground_color(ground_texture, ground_tint, 0.5, edge_noise, edge_noise_scale, world_xz);

	// The face is read on its own vertical plane: along x when it looks along z, and along z otherwise.
	vec3 facing = normalize(world_normal);
	bool along_x = abs(facing.z) > abs(facing.x);
	vec2 plane = along_x ? vec2(world_xz.x, world_y) : vec2(world_xz.y, world_y);

	// The top is the ground's own color, so it joins the land without a seam; the dirt is only on the face.
	vec3 top = land;

	// The face: dirt with clods, dark in the cracks, drier at the top and darker toward the water.
	float clod = texture(clod_height, plane * clod_scale).r;
	float strata = texture(edge_noise, vec2(plane.x * 0.5, world_y * 5.0) * edge_noise_scale).r;
	float depth = clamp(-world_y / 0.35, 0.0, 1.0);
	vec3 earth = face_color * (0.8 + 0.4 * clod) * (0.95 + 0.1 * strata);
	earth *= mix(1.0, 0.8, depth);
	// Turf hangs over the top of the face, in blades.
	float blade = abs(fract(plane.x * 30.0 + broad * 4.0) - 0.5) * 2.0;
	float turf_length = 0.035 + 0.05 * texture(edge_noise, vec2(plane.x * 3.0, 0.5)).r;
	earth = mix(earth, land * 0.85, step(-world_y, turf_length * (1.0 - 0.6 * blade)));
	ALBEDO = mix(top, earth, face);
	ROUGHNESS = 0.95;

	// The clods' relief tilts the face's normal on its plane. The face looks toward the camera, which the sun never
	// lights, so it also leans toward the sky and reads as warm earth rather than a black outline.
	vec3 bump = texture(clod_normals, plane * clod_scale).xyz * 2.0 - 1.0;
	vec3 across = along_x ? vec3(1.0, 0.0, 0.0) : vec3(0.0, 0.0, 1.0);
	vec3 bumped = normalize(facing + clod_relief * (bump.x * across + bump.y * vec3(0.0, 1.0, 0.0)));
	vec3 shaded = normalize(mix(bumped, vec3(0.0, 1.0, 0.0), 0.35));
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(shaded, 0.0)).xyz, face));
	// The face is in the lip's shadow, so the sky's glow, which the day animation already sets for the rim, lifts it.
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO) + face * rim_color.rgb * rim_strength * ALBEDO * 2.2;
}
