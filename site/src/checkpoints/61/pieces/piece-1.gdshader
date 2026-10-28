shader_type spatial;
render_mode unshaded, depth_draw_never;

// The size of a cell and the cell under the cursor, set by GridCursor on this mesh.
instance uniform float cell_size = 1.0;
instance uniform vec2 cell = vec2(1000000.0);

uniform vec4 line_color : source_color = vec4(1.0, 1.0, 1.0, 0.35);
uniform vec4 cursor_color : source_color = vec4(1.0, 0.85, 0.3, 0.55);
// How thick a line is, as a share of a cell, and how far from the cursor the lines fade out, in meters.
uniform float line_width : hint_range(0.0, 0.2) = 0.04;
uniform float fade_distance = 7.0;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 grid = world_position.xz / cell_size;
	// How far this point is from the nearest cell edge, in cells.
	vec2 inside = fract(grid);
	vec2 to_edge = min(inside, 1.0 - inside);
	float line = 1.0 - smoothstep(line_width * 0.5, line_width, min(to_edge.x, to_edge.y));
	float on_cursor = float(all(equal(floor(grid), cell)));
	float near = 1.0 - smoothstep(fade_distance * 0.5, fade_distance, distance(world_position.xz, (cell + 0.5) * cell_size));
	ALBEDO = mix(line_color.rgb, cursor_color.rgb, on_cursor);
	ALPHA = max(line_color.a * line * near, cursor_color.a * on_cursor);
}
