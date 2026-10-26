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

// A blade's tip sways TIP_SWAY meters along the wind at full strength, bobbing BLADE_HZ times a second, and flutters
// BLADE_FLUTTER meters across it.
const float TIP_SWAY = 0.12;
const float BLADE_FLUTTER = 0.025;
const float BLADE_HZ = 0.8;
// A petal flutters PETAL_FLUTTER meters across the wind, PETAL_HZ times a second.
const float PETAL_FLUTTER = 0.02;
const float PETAL_HZ = 0.5;

// How far a vertex of a grass blade moves, in world space. share is its share of the blade's height, so the foot stays
// put and the tip moves most; the clump's phase and the blade's own keep a field from swaying in step.
vec3 grass_sway(vec3 world_position, float clump_phase, float blade_phase, float share) {
	vec2 heading = normalize(wind_direction);
	vec2 across = vec2(-heading.y, heading.x);
	float beat = TAU * (clump_phase + blade_phase + BLADE_HZ * TIME);
	float reach = share * share * gust_strength(world_position);
	vec2 push = reach * (heading * TIP_SWAY * (0.6 + 0.4 * sin(beat)) + across * BLADE_FLUTTER * sin(2.0 * beat));
	return vec3(push.x, 0.0, push.y);
}

// How far a petal vertex flutters, in world space. mask is 1 on a petal and 0 on the stem and the center.
vec3 petal_flutter(vec3 world_position, float flower_phase, float mask) {
	vec2 heading = normalize(wind_direction);
	vec2 across = vec2(-heading.y, heading.x);
	float beat = TAU * (flower_phase + PETAL_HZ * TIME);
	vec2 push = across * PETAL_FLUTTER * mask * gust_strength(world_position) * sin(2.0 * beat + world_position.x * 5.0);
	return vec3(push.x, 0.0, push.y);
}
