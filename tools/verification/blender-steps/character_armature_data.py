# The character's skeleton on Godot's humanoid bone names (no fingers, no Root bone). Blender's axes: the character faces
# -Y, so its left side is +X. Each row: name, head, tail, and whether the head is the parent's tail (a connected bone).
# The right side is made from the left with Armature > Symmetrize, which flips Left to Right in the names.
SPINE = [
    ('Hips', (0.0, 0.0, 0.90), (0.0, 0.0, 1.00), None),
    ('Spine', None, (0.0, 0.0, 1.12), True),
    ('Chest', None, (0.0, 0.0, 1.27), True),
    ('UpperChest', None, (0.0, 0.0, 1.40), True),
    ('Neck', None, (0.0, 0.0, 1.52), True),
    ('Head', None, (0.0, 0.0, 1.80), True),
]
# The arm's first bone is a new single bone parented to UpperChest in the Relations panel; the rest are extruded from it.
ARM_ROOT = ('LeftShoulder', (0.0, 0.0, 1.40), (0.20, 0.0, 1.365), 'UpperChest')
ARM = [
    ('LeftUpperArm', None, (0.295, 0.0, 1.163), True),
    ('LeftLowerArm', None, (0.391, 0.0, 0.962), True),
    ('LeftHand', None, (0.432, 0.0, 0.855), True),
]
# The leg: a new single bone parented to Hips (it starts at the hip, not at the Hips bone's tail), then extruded.
LEG_ROOT = ('LeftUpperLeg', (0.10, 0.0, 0.90), (0.10, 0.0, 0.50), 'Hips')
LEG = [
    ('LeftLowerLeg', None, (0.10, 0.0, 0.12), True),
    ('LeftFoot', None, (0.10, -0.10, 0.05), True),
    ('LeftToes', None, (0.10, -0.20, 0.03), True),
]
