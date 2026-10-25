shader_type sky;

// The sky straight up, and at the horizon.
uniform vec3 zenith_color : source_color = vec3(0.31, 0.66, 1.0);
uniform vec3 horizon_color : source_color = vec3(0.56, 0.78, 1.0);
// How much darker the sky gets looking down from the horizon.
uniform float ground_darkening : hint_range(0.0, 1.0) = 0.5;

void sky() {
	// 0 at the horizon and 1 straight up. EYEDIR is the direction this point of the sky is seen in.
	float height = clamp(EYEDIR.y, 0.0, 1.0);
	COLOR = mix(horizon_color, zenith_color, height);
	// Below the horizon the same color fades toward darker.
	COLOR *= 1.0 - ground_darkening * clamp(-EYEDIR.y, 0.0, 1.0);
}
