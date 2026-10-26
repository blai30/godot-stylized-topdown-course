// Wind for anything that sways: one gust front that crosses the meadow, and the sway and flutter it drives.

// Which way the wind blows along the ground (x east, y south), and how hard, from 0 to 1.
global uniform vec2 wind_direction;
global uniform float wind_strength;

// A gust is a long wave that travels downwind. The wind never drops below GUST_FLOOR of its strength.
const float GUST_LENGTH = 24.0;
const float GUST_SECONDS = 8.0;
const float GUST_FLOOR = 0.4;
// A whole tree leans and returns SWAY_HZ times a second, and leans TREE_BEND of its height at the top.
const float SWAY_HZ = 0.5;
const float TREE_BEND = 0.03;
const float CANOPY_HEIGHT = 6.0;
// A card flutters FLUTTER_HZ times a second, up to CARD_FLUTTER meters at its far edge.
const float FLUTTER_HZ = 1.125;
const float CARD_FLUTTER = 0.06;

// The wind's strength here, now: the wave's crest passes each spot in turn, from upwind to downwind.
float gust_strength(vec3 world_position) {
	vec2 heading = normalize(wind_direction);
	float wave = 0.5 + 0.5 * sin(TAU * (TIME / GUST_SECONDS - dot(world_position.xz, heading) / GUST_LENGTH));
	return wind_strength * mix(GUST_FLOOR, 1.0, wave);
}

// How far the whole tree leans at a point on it, in world space. The tree's own phase keeps a grove from swaying in step.
vec3 tree_sway(vec3 world_position, vec3 tree_origin, float tree_phase) {
	vec2 heading = normalize(wind_direction);
	// The top moves most: the lean grows with the square of the height.
	float rise = (world_position.y - tree_origin.y) / CANOPY_HEIGHT;
	float swing = sin(TAU * (tree_phase + SWAY_HZ * TIME));
	float lean = TREE_BEND * CANOPY_HEIGHT * rise * rise * gust_strength(world_position) * swing;
	return vec3(heading.x, 0.0, heading.y) * lean;
}

// How far a card flutters, in world space: along its own direction, more at its far edge, in step with its own phase.
vec3 card_flutter(vec3 world_position, float tree_phase, float card_phase, float far_edge) {
	float angle = TAU * card_phase;
	vec3 direction = vec3(cos(angle), 0.6, sin(angle));
	float beat = sin(TAU * (tree_phase + card_phase + FLUTTER_HZ * TIME));
	return direction * CARD_FLUTTER * far_edge * gust_strength(world_position) * beat;
}
