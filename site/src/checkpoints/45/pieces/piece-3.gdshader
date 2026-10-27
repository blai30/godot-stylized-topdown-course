shader_type spatial;
render_mode unshaded;

// What the water looks like when there is a lot of it: a deep blue-slate.
uniform vec3 scatter_color : source_color = vec3(0.039, 0.055, 0.141);

void fragment() {
	ALBEDO = scatter_color;
	ALPHA = 0.6;
}
