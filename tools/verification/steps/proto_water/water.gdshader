shader_type spatial;

#include "res://art/shaders/wind.gdshaderinc"

// The frame drawn so far (the lake bed, the bank, the trees) and its depth.
uniform sampler2D screen_texture : hint_screen_texture, filter_linear, repeat_disable;
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest, repeat_disable;
// A seamless normal map of ripples.
uniform sampler2D wave_normals : filter_linear_mipmap, repeat_enable;

// What the water looks like when there is a lot of it.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);
// How much of each color the water absorbs per meter the view crosses: red goes first.
uniform vec3 absorption = vec3(3.0, 1.5, 1.0);
// How much of the scatter color shows even over a bed right under the surface.
uniform float min_opacity : hint_range(0.0, 1.0) = 0.25;
uniform float wave_strength : hint_range(0.0, 1.0) = 0.5;
uniform float refraction_strength : hint_range(0.0, 0.2) = 0.06;
uniform float reflection_boost : hint_range(0.0, 1.0) = 0.3;
uniform float hairline : hint_range(0.0, 1.0) = 0.35;

// Meters per repeat of the three wave layers, how far each drifts a second in repeats, their angle from the wind, and their weight.
const float WAVE_METERS[3] = float[](12.0, 4.0, 1.5);
const float WAVE_SPEED[3] = float[](0.025, 0.06, 0.13);
const float WAVE_ANGLE[3] = float[](0.0, 0.52, -0.7);
const float WAVE_WEIGHT[3] = float[](0.5, 0.35, 0.15);
// The waves calm to nothing where the water is thinner than this, so the edge stays clean.
const float CALM_THICKNESS = 0.3;
// Refraction bends the bed by at most this many meters of water's worth.
const float REFRACTION_DEPTH = 1.5;
// The hairline is as thick as two pixels' worth of the water's thickness, between these two.
const vec2 HAIRLINE_THICKNESS = vec2(0.08, 0.16);
// Water's reflectance facing the eye.
const float WATER_F0 = 0.02;
const vec3 HAIRLINE_COLOR = vec3(0.9, 0.93, 0.95);

// The reflection march reaches this many meters and counts a hit while the ray is at most REFLECT_THICKNESS behind what it passes.
// It fades out as a pixel grows from REFLECT_FADE.x to REFLECT_FADE.y meters, where a tree's reflection is a few pixels.
const int REFLECT_STEPS = 24;
const int REFLECT_REFINE = 4;
const float REFLECT_REACH = 8.0;
const float REFLECT_THICKNESS = 1.0;
const vec2 REFLECT_FADE = vec2(0.06, 0.08);

varying vec2 world_xz;

// The view-space position of the opaque scene at a screen position.
vec3 scene_at(vec2 uv, mat4 inverse_projection) {
	float depth = textureLod(depth_texture, uv, 0.0).r;
	vec4 position = inverse_projection * vec4(uv * 2.0 - 1.0, depth, 1.0);
	return position.xyz / position.w;
}

// The screen position of a view-space position.
vec2 screen_of(vec3 position, mat4 projection) {
	vec4 clip = projection * vec4(position, 1.0);
	return clip.xy / clip.w * 0.5 + 0.5;
}

vec2 rotate(vec2 value, float angle) {
	float cosine = cos(angle);
	float sine = sin(angle);
	return vec2(cosine * value.x - sine * value.y, sine * value.x + cosine * value.y);
}

// The slope of the waves at a point, in world space: three layers of the ripple texture drifting across each other.
vec2 wave_slope(vec2 position, float heading) {
	vec2 slope = vec2(0.0);
	for (int layer = 0; layer < 3; layer++) {
		float angle = heading + WAVE_ANGLE[layer];
		vec2 frame = rotate(position, -angle) / WAVE_METERS[layer];
		frame.x -= TIME * WAVE_SPEED[layer];
		vec2 layer_slope = (texture(wave_normals, frame).rg - 0.5) * 2.0;
		slope += WAVE_WEIGHT[layer] * rotate(layer_slope, angle);
	}
	return slope;
}

// Where a view-space ray first passes behind the opaque scene, refined by bisection: xy the screen position, z how much to trust it.
vec3 reflection_hit(vec3 origin, vec3 direction, mat4 projection, mat4 inverse_projection) {
	float before = 0.0;
	for (int i = 1; i <= REFLECT_STEPS; i++) {
		float along = REFLECT_REACH * float(i) / float(REFLECT_STEPS);
		vec3 point = origin + direction * along;
		vec2 uv = screen_of(point, projection);
		if (any(lessThan(uv, vec2(0.0))) || any(greaterThan(uv, vec2(1.0)))) {
			return vec3(0.0);
		}
		float behind = scene_at(uv, inverse_projection).z - point.z;
		if (behind > 0.0 && behind < REFLECT_THICKNESS) {
			float after = along;
			for (int refine = 0; refine < REFLECT_REFINE; refine++) {
				float middle = 0.5 * (before + after);
				vec3 probe = origin + direction * middle;
				if (scene_at(screen_of(probe, projection), inverse_projection).z > probe.z) {
					after = middle;
				} else {
					before = middle;
				}
			}
			vec2 hit = screen_of(origin + direction * after, projection);
			vec2 edge = min(hit, 1.0 - hit);
			return vec3(hit, smoothstep(0.0, 0.06, min(edge.x, edge.y)) * (1.0 - after / REFLECT_REACH));
		}
		before = along;
	}
	return vec3(0.0);
}

void vertex() {
	world_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
}

void fragment() {
	// How much water the view ray crosses before it meets the bed.
	vec3 behind = scene_at(SCREEN_UV, INV_PROJECTION_MATRIX);
	float thickness = length(behind - VERTEX);

	// Waves, bigger in the wind and calm where the water is thin.
	vec2 heading_xz = normalize(wind_direction);
	float heading = atan(heading_xz.y, heading_xz.x);
	float strength = wave_strength * mix(0.5, 1.0, wind_strength) * smoothstep(0.0, CALM_THICKNESS, thickness);
	vec2 slope = wave_slope(world_xz, heading) * strength;
	vec3 normal_world = normalize(vec3(slope.x, 1.0, slope.y));
	NORMAL = normalize((VIEW_MATRIX * vec4(normal_world, 0.0)).xyz);

	// The bed is read where the waves bend the view ray. A bent sample in front of the surface would show the bank bleeding in, so it falls back.
	vec2 bed_uv = SCREEN_UV;
	vec3 bend = (VIEW_MATRIX * vec4(normal_world.x, 0.0, normal_world.z, 0.0)).xyz * refraction_strength * min(thickness, REFRACTION_DEPTH);
	vec2 bent = SCREEN_UV + screen_of(VERTEX + bend, PROJECTION_MATRIX) - screen_of(VERTEX, PROJECTION_MATRIX);
	vec3 bent_behind = scene_at(bent, INV_PROJECTION_MATRIX);
	if (bent_behind.z < VERTEX.z) {
		bed_uv = bent;
		thickness = length(bent_behind - VERTEX);
	}
	vec3 bed = textureLod(screen_texture, bed_uv, 0.0).rgb;

	// A slow patchwork of noise, for the color's wobble and the foam's ragged width.
	float mottle = texture(wave_normals, world_xz / 7.0 + vec2(TIME * 0.004, 0.0)).g;

	// What the water lets through of the bed fades with the thickness, red first, from 1 - min_opacity.
	vec3 transmitted = exp(-absorption * thickness) * (1.0 - min_opacity);
	// The color wobbles a little from place to place, as if the water were not quite the same everywhere.
	float wobble = (mottle * 2.0 - 1.0) * 0.18;

	// Foam where the water is thin: along the bank and around anything standing in it. A noise moves how thin counts, so the edge is ragged.
	float foam_width = clamp(2.0 * fwidth(thickness), HAIRLINE_THICKNESS.x, HAIRLINE_THICKNESS.y) * (0.5 + 1.5 * mottle);
	float line = hairline * pow(1.0 - smoothstep(0.0, foam_width, thickness), 2.0);

	// The scatter is lit like a surface. The bed already arrives lit, so it goes out as emission.
	// Godot's reflection of the sky needs a surface that reflects: a metal tinted by how much it should reflect.
	float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float reflectance = clamp(WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - facing, 5.0) + reflection_boost, 0.0, 1.0);
	// Where the march finds the bank or a tree, their color replaces the sky's.
	vec3 toward_eye = vec3(0.0, 0.0, 1.0);
	vec3 reflected = reflect(-toward_eye, NORMAL);
	float meters_per_pixel = max(length(dFdx(world_xz)), length(dFdy(world_xz)));
	vec3 hit = reflection_hit(VERTEX, reflected, PROJECTION_MATRIX, INV_PROJECTION_MATRIX);
	float found = hit.z * (1.0 - smoothstep(REFLECT_FADE.x, REFLECT_FADE.y, meters_per_pixel));
	vec3 seen = textureLod(screen_texture, hit.xy, 0.0).rgb * found;
	ALBEDO = vec3(reflectance * (1.0 - found));
	METALLIC = 1.0;
	vec3 body = pow(max(scatter_color * (1.0 - transmitted) + bed * transmitted, vec3(0.0001)), vec3(1.0 + wobble));
	EMISSION = (body * (1.0 - reflectance) + seen * reflectance) * (1.0 - line) + HAIRLINE_COLOR * line;
	ROUGHNESS = mix(0.08, 0.6, line);
}
