# The character's reference sheet: shapes in meters, shared by lesson 35's Krita run and the Blender lessons' checks.
# The sheet is 2048 by 1024 px at 512 px per meter; the front view is centered at x 512, the side view at x 1536, and the
# ground is at y 984, eight head units of 123 px (0.24 m, a figure of 7.5 heads is 1.8 m tall).
PX_PER_METER = 512
GROUND = 984
FRONT_X, SIDE_X = 512, 1536
HEAD = 123

# Colors as hue, saturation, value in percent, from the design sheet.
COLORS = {
    'skin': (24, 36, 91), 'hair': (12, 66, 48), 'tunic': (206, 71, 64), 'shirt': (39, 17, 94), 'pants': (214, 26, 37),
    'boots': (26, 52, 42), 'bag': (30, 62, 66), 'belt': (22, 60, 36), 'glove': (22, 60, 36),
}

# Each shape: (kind, color, points in meters as (x, z)), x across (front) or forward (side), z up. A rect has two
# corners, an ellipse its bounding corners, and a polygon its corners. 'mirror' repeats it on the other side of the
# view's center (front view only).
FRONT = [
    ('rect', 'pants', ((0.035, 0.10), (0.165, 0.90)), True),
    ('rect', 'boots', ((0.03, 0.0), (0.17, 0.10)), True),
    ('rect', 'tunic', ((-0.20, 0.80), (0.20, 1.02)), False),
    ('rect', 'tunic', ((-0.20, 1.02), (0.20, 1.43)), False),
    ('rect', 'belt', ((-0.20, 1.00), (0.20, 1.06)), False),
    ('poly', 'shirt', ((0.20, 1.42), (0.34, 1.40), (0.40, 0.98), (0.33, 0.97)), True),
    ('rect', 'glove', ((0.33, 0.85), (0.43, 0.97)), True),
    ('rect', 'skin', ((-0.05, 1.43), (0.05, 1.53)), False),
    ('ellipse', 'skin', ((-0.115, 1.52), (0.115, 1.80)), False),
    ('ellipse', 'hair', ((-0.135, 1.60), (0.135, 1.80)), False),
]
SIDE = [
    ('rect', 'pants', ((-0.065, 0.10), (0.065, 0.90)), False),
    ('rect', 'boots', ((-0.06, 0.0), (0.19, 0.10)), False),
    ('rect', 'tunic', ((-0.14, 0.80), (0.14, 1.02)), False),
    ('rect', 'tunic', ((-0.14, 1.02), (0.14, 1.43)), False),
    ('rect', 'belt', ((-0.145, 1.00), (0.145, 1.06)), False),
    ('rect', 'bag', ((-0.27, 1.07), (-0.14, 1.37)), False),
    ('poly', 'shirt', ((-0.05, 1.42), (0.05, 1.42), (0.07, 0.98), (-0.03, 0.98)), False),
    ('rect', 'glove', ((-0.04, 0.86), (0.08, 0.98)), False),
    ('rect', 'skin', ((-0.05, 1.43), (0.05, 1.53)), False),
    ('ellipse', 'skin', ((-0.125, 1.52), (0.125, 1.80)), False),
    ('ellipse', 'hair', ((-0.145, 1.60), (0.12, 1.80)), False),
]


def pixel(view_x, point):
    # A point in meters on a view (front or side, by its center x) to sheet pixels.
    x, z = point
    return view_x + x * PX_PER_METER, GROUND - z * PX_PER_METER
