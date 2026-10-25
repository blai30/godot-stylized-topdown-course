shader_type canvas_item;

// The frame Godot has drawn, after tonemapping.
uniform sampler2D screen_texture : hint_screen_texture, filter_nearest;
// The tint lifted into the shadows and the tint gained in the highlights. Only their color counts, not their brightness.
uniform vec3 shadow_tint : source_color = vec3(1.0);
uniform vec3 highlight_tint : source_color = vec3(1.0);
// How much of the grade shows: 0 leaves the frame as it is.
uniform float strength : hint_range(0.0, 1.0) = 0.0;
// The graded color's saturation, where 1 keeps it.
uniform float saturation : hint_range(0.0, 2.0) = 1.0;

// How bright a color looks to the eye.
float luma(vec3 color) {
	return dot(color, vec3(0.2126, 0.7152, 0.0722));
}

void fragment() {
	vec3 color = texture(screen_texture, SCREEN_UV).rgb;
	float light = luma(color);
	// A tint's chroma is the tint less its own gray: white has none.
	vec3 shadow_chroma = shadow_tint - luma(shadow_tint);
	vec3 highlight_chroma = highlight_tint - luma(highlight_tint);
	// Dark pixels take the shadow tint, bright pixels the highlight tint, mid tones the least of both.
	vec3 graded = light + (color - light) * saturation
			+ (1.0 - light) * (1.0 - light) * shadow_chroma
			+ light * light * highlight_chroma;
	COLOR = vec4(clamp(mix(color, graded, strength), 0.0, 1.0), 1.0);
}
