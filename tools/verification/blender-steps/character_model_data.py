# The refined, faceted character's parts, in Blender's axes (forward is -Y, up is +Z). Each row is one object:
#   name, shape, shape numbers, scale, location, turn about Y in degrees
# cone: (vertices, bottom radius, top radius, depth) along Z; ico sphere: (subdivisions, radius); cube: (size,)
# scale is the Tab-separated numbers typed with S after the shape is added (applied afterward); None keeps it as made.
# A side part is listed once, with the numbers for the character's left (+X); its right is the same with X and the turn negated.
CENTER = [
    ('hips', 'cube', (2,), (0.15, 0.10, 0.08), (0.0, 0.0, 0.95), 0),
    ('skirt', 'cone', (8, 0.22, 0.17, 0.17), (1.0, 0.68, 1.0), (0.0, 0.0, 0.90), 0),
    ('tunic', 'cone', (8, 0.17, 0.205, 0.43), (1.0, 0.68, 1.0), (0.0, 0.0, 1.215), 0),
    ('belt', 'cube', (2,), (0.18, 0.12, 0.03), (0.0, 0.0, 1.03), 0),
    ('collar', 'cone', (8, 0.12, 0.085, 0.07), (1.0, 0.9, 1.0), (0.0, 0.0, 1.465), 0),
    ('head', 'ico sphere', (2, 1.0), (0.115, 0.125, 0.14), (0.0, 0.0, 1.66), 0),
    ('nose', 'cube', (2,), (0.017, 0.022, 0.027), (0.0, -0.135, 1.64), 0),
    ('hair', 'ico sphere', (2, 1.0), (0.135, 0.14, 0.125), (0.0, 0.02, 1.675), 0),
    ('hair_back', 'ico sphere', (1, 1.0), (0.11, 0.08, 0.11), (0.0, 0.115, 1.65), 0),
    ('fringe_1', 'cube', (2,), (0.035, 0.035, 0.035), (-0.08, -0.105, 1.745), 18),
    ('fringe_2', 'cube', (2,), (0.035, 0.035, 0.035), (0.0, -0.11, 1.755), 0),
    ('fringe_3', 'cube', (2,), (0.035, 0.035, 0.035), (0.08, -0.105, 1.745), -18),
    ('pack', 'cube', (2,), (0.14, 0.07, 0.15), (0.0, 0.18, 1.22), 0),
]
SIDE = [
    ('thigh', 'cone', (6, 0.07, 0.095, 0.42), None, (0.10, 0.0, 0.71), 0),
    ('shin', 'cone', (6, 0.065, 0.07, 0.30), None, (0.10, 0.0, 0.35), 0),
    ('boot_shaft', 'cone', (6, 0.08, 0.085, 0.20), None, (0.10, 0.0, 0.20), 0),
    ('boot_foot', 'cube', (2,), (0.065, 0.14, 0.05), (0.10, -0.05, 0.05), 0),
    ('arm', 'cone', (6, 0.05, 0.062, 0.43), None, (0.30, 0.0, 1.19), -20.6),
    ('glove', 'cube', (2,), (0.045, 0.045, 0.055), (0.385, 0.0, 0.93), 0),
    ('pad', 'ico sphere', (1, 1.0), (0.085, 0.085, 0.075), (0.215, 0.0, 1.40), 0),
]


def side_rows():
    # Both sides: the left as listed (suffix .L), the right with X and the turn negated (.R).
    rows = []
    for name, shape, numbers, scale, (x, y, z), turn in SIDE:
        rows.append((name + '.L', shape, numbers, scale, (x, y, z), turn))
    for name, shape, numbers, scale, (x, y, z), turn in SIDE:
        rows.append((name + '.R', shape, numbers, scale, (-x, y, z), -turn if turn else 0))
    return rows


PARTS = CENTER + side_rows()
