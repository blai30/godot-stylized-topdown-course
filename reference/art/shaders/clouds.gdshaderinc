// Cloud shadows: one drifting noise that darkens the ground and everything on it, and that the water reflects.
#include "res://art/shaders/wind.gdshaderinc"

// The noise, how many meters it repeats across, and how dark the shadows are, from 0 to 1. Project Settings define them.
global uniform sampler2D cloud_texture : filter_linear_mipmap, repeat_enable;
global uniform float cloud_scale;
global uniform float cloud_strength;

// The clouds drift downwind this many meters a second.
const float CLOUD_SPEED = 0.5;
// The noise values where a cloud starts and where it is solid.
const vec2 CLOUD_EDGE = vec2(0.35, 0.65);

// How much of a point is under cloud, from 0 to 1. time is the shader's TIME.
float cloud_cover(vec2 world_xz, float time) {
	vec2 drifted = world_xz - normalize(wind_direction) * time * CLOUD_SPEED;
	return smoothstep(CLOUD_EDGE.x, CLOUD_EDGE.y, texture(cloud_texture, drifted / cloud_scale).r);
}

// The light a point keeps under the clouds: 1 in the open, less in a shadow.
float cloud_shadow(vec3 world_position, float time) {
	return 1.0 - cloud_cover(world_position.xz, time) * cloud_strength;
}
