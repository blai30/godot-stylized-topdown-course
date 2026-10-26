// The ground cover's push: a character parts the grass and the flowers around it.

// The character's position (xyz) and how far its push reaches in meters (w); a w of 0 pushes nothing.
global uniform vec4 push_point;

// A blade or petal within the radius leans PUSH_DISTANCE meters away from the character and sinks PUSH_FLATTEN of its
// height at the character's feet, less toward the radius.
const float PUSH_DISTANCE = 0.25;
const float PUSH_FLATTEN = 0.5;

// The vertex, pushed away from the character. ground is the spot on the ground it is rooted at, and mask is how much of
// the part moves: 0 at a blade's foot and 1 at its tip, 1 on a petal and 0 on a stem.
vec3 push_aside(vec3 vertex, vec3 ground, float mask) {
	vec2 away = ground.xz - push_point.xz;
	float distance_to_point = length(away);
	// A point whose radius is 0 reaches nothing.
	float push = push_point.w > 0.0 ? 1.0 - clamp(distance_to_point / push_point.w, 0.0, 1.0) : 0.0;
	vec2 direction = distance_to_point > 0.001 ? away / distance_to_point : vec2(1.0, 0.0);
	vertex.xz += direction * PUSH_DISTANCE * mask * push;
	vertex.y = ground.y + (vertex.y - ground.y) * (1.0 - PUSH_FLATTEN * mask * push);
	return vertex;
}
