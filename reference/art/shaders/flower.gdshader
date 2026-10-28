shader_type spatial;
render_mode cull_disabled, world_vertex_coords, specular_disabled;

#include "res://art/shaders/wind.gdshaderinc"
#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/ground_cover.gdshaderinc"
#include "res://art/shaders/clouds.gdshaderinc"

varying vec3 flower_color;

void vertex() {
	// COLOR is the part's own color, and its alpha is 1 on a petal and 0 on the stem and the center. INSTANCE_CUSTOM.x
	// is the flower's phase and INSTANCE_CUSTOM.yzw the color of its petals; a flower that is not in a MultiMesh has
	// neither, so its petals stay white.
	float petal = COLOR.a;
	VERTEX += petal_flutter(VERTEX, INSTANCE_CUSTOM.x, petal);
	// A flower parts by its root: its petals lean away from the character, and the stem stays.
	VERTEX = push_aside(VERTEX, vec3(MODEL_MATRIX[3].x, MODEL_MATRIX[3].y, MODEL_MATRIX[3].z), petal);
	vec3 tint = mix(vec3(1.0), INSTANCE_CUSTOM.yzw, step(0.001, dot(INSTANCE_CUSTOM.yzw, vec3(1.0))));
	flower_color = COLOR.rgb * mix(vec3(1.0), tint, petal);
}

void fragment() {
	ALBEDO = flower_color;
	ALBEDO *= cloud_shadow((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, TIME);
	ROUGHNESS = 1.0;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
