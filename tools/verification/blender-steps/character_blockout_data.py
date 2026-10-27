# The character's blockout parts in Blender's axes (forward is -Y, up is +Z), from the reference sheet's meters:
# name, shape, half sizes along X, Y, and Z, where the center stands, and the turn about Y in degrees. Shared by
# lesson 36's Blender run and the checks that follow it.
PARTS = [
    ('head', 'uv sphere', (0.115, 0.125, 0.14), (0.0, 0.0, 1.66), 0),
    ('hair', 'uv sphere', (0.135, 0.14, 0.10), (0.0, 0.015, 1.70), 0),
    ('neck', 'cube', (0.05, 0.05, 0.05), (0.0, 0.0, 1.48), 0),
    ('torso', 'cube', (0.20, 0.14, 0.205), (0.0, 0.0, 1.225), 0),
    ('skirt', 'cube', (0.20, 0.14, 0.11), (0.0, 0.0, 0.91), 0),
    ('pack', 'cube', (0.14, 0.065, 0.15), (0.0, 0.205, 1.22), 0),
    ('arm.L', 'cube', (0.05, 0.05, 0.245), (0.285, 0.0, 1.19), -20.7),
    ('arm.R', 'cube', (0.05, 0.05, 0.245), (-0.285, 0.0, 1.19), 20.7),
    ('glove.L', 'cube', (0.05, 0.05, 0.06), (0.38, 0.0, 0.91), 0),
    ('glove.R', 'cube', (0.05, 0.05, 0.06), (-0.38, 0.0, 0.91), 0),
    ('leg.L', 'cube', (0.065, 0.065, 0.40), (0.10, 0.0, 0.50), 0),
    ('leg.R', 'cube', (0.065, 0.065, 0.40), (-0.10, 0.0, 0.50), 0),
    ('boot.L', 'cube', (0.07, 0.125, 0.05), (0.10, -0.065, 0.05), 0),
    ('boot.R', 'cube', (0.07, 0.125, 0.05), (-0.10, -0.065, 0.05), 0),
]
# The reference images: the file, where the empty stands (behind the model), and its turn about Z in degrees.
# 512 px per meter on a 1024 px image is 2 m; the ground is 984 px down, so the center is 0.922 m above it.
REFERENCES = [('character_front.png', (0.0, 1.0, 0.922), 0), ('character_side.png', (1.0, 0.0, 0.922), 90)]
