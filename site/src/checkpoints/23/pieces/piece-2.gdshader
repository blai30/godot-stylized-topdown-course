shader_type spatial;

#include "res://art/shaders/stylized_lit.gdshaderinc"

// The palette: one swatch for each color of the rocks.
uniform sampler2D palette : source_color, filter_nearest;

void fragment() {
	ALBEDO = texture(palette, UV).rgb;
	EMISSION += soft_rim(NORMAL, INV_VIEW_MATRIX);
}
