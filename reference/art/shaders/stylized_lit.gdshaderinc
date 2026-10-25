// Lighting shared by the template's stylized surfaces: wrapped diffuse light and a soft rim.

// The rim's color and strength. DayClock sets them from the day animation.
global uniform vec4 rim_color : source_color;
global uniform float rim_strength;

// How far the light wraps around a surface: 0 is plain diffuse, 1 reaches the far side.
const float WRAP = 0.5;
// How narrow the rim is: a higher power keeps it closer to the silhouette.
const float RIM_POWER = 3.0;

// A faint glow along the silhouette that separates a surface from the ground behind it.
vec3 soft_rim(vec3 view_normal, mat4 inverse_view) {
	// The camera looks along -Z in view space, so a normal turned away from +Z is near the silhouette.
	float edge = pow(1.0 - clamp(view_normal.z, 0.0, 1.0), RIM_POWER);
	// Faces looking up take the whole rim, upright faces half of it, and faces looking down none.
	float world_up = (inverse_view * vec4(view_normal, 0.0)).y;
	float sky = clamp(0.5 + world_up, 0.0, 1.0);
	return rim_color.rgb * rim_strength * edge * sky;
}

void light() {
	// Plain diffuse is the dot product alone. Wrapping shifts it, so the side facing away from the light stays softly lit.
	float wrapped = clamp((dot(NORMAL, LIGHT) + WRAP) / (1.0 + WRAP), 0.0, 1.0);
	DIFFUSE_LIGHT += wrapped * ATTENUATION * LIGHT_COLOR / PI;
}
