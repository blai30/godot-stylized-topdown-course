# The character's texture plan: a 512 by 512 image. The top half (v 0.5 to 1) is the face patch the head is projected onto;
# the bottom half is eight flat color cells, each 128 px, laid out four across and two down. Colors are hue, saturation,
# and value in percent, from lesson 35's sheet.
CELL = 0.25
# name -> (cell column from the left, cell row from the bottom of the image), then the color.
SWATCHES = {
    'skin': (0, 1, (24, 36, 91)),
    'hair': (1, 1, (12, 66, 48)),
    'tunic': (2, 1, (206, 71, 64)),
    'shirt': (3, 1, (39, 17, 94)),
    'leather': (0, 0, (22, 60, 36)),
    'trousers': (1, 0, (214, 26, 37)),
    'boots': (2, 0, (26, 52, 42)),
    'pack': (3, 0, (30, 62, 66)),
}
FACE_CENTER = (0.5, 0.75)


def center(name):
    column, row, _ = SWATCHES[name]
    return (column + 0.5) * CELL, (row + 0.5) * CELL

# The face patch's features, in 512 px image coordinates (x across, y down from the top). Each is where lesson 38's
# Blender run maps a point on the head: u = 0.5 + 0.45 * x / (xmax - xmin), v = 0.525 + 0.45 * (z - zmin) / (zmax - zmin),
# with the head's bounds x -0.115 to 0.115 and z 1.55 to 1.80, from the log of that run.
FACE_FEATURES = {
    'eye_left': (306.1, 123.3), 'eye_right': (205.9, 123.3), 'mouth': (256.0, 197.1),
    'blush_left': (341.1, 174.1), 'blush_right': (170.9, 174.1),
}
EYE = (36, 50)
EYE_SHINE = (11, 14)
BLUSH = (40, 22)
MOUTH = (18, 7)
EYE_COLOR = (260, 30, 22)
SHINE_COLOR = (0, 0, 100)
BLUSH_COLOR = (355, 38, 100)
MOUTH_COLOR = (355, 55, 55)
