shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"
#include "res://art/shaders/wind.gdshaderinc"

// The palette, as for the rocks.
uniform sampler2D palette : source_color, filter_nearest;
// Set on each tree, so a grove does not sway in step.
instance uniform float tree_phase = 0.0;

void vertex() {
	vec3 world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 tree_origin = MODEL_MATRIX[3].xyz;
	// The bark leans with the cards, so the limbs stay under their leaves.
	VERTEX += inverse(mat3(MODEL_MATRIX)) * tree_sway(world_position, tree_origin, tree_phase);
}

void fragment() {
	ALBEDO = texture(palette, UV).rgb;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX, ALBEDO);
}
