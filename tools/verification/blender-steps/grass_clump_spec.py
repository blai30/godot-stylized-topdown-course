# The Grass Clump node group of lesson 30, as data, in the format of leaf_cards_spec.py: the lesson's step script builds
# it in Blender's editor from this, and the lesson's tables are written from it. Keys 'in' and 'out' are the Group Input
# and Group Output nodes; the group has one input besides the geometry, an integer named Seed.
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import leaf_cards_spec as base

IDNAMES = dict(base.IDNAMES, **{'Collection Info': 'GeometryNodeCollectionInfo', 'Math': 'ShaderNodeMath'})

# Each blade is one of three shapes, bent 15, 32, and 50 degrees, 5 vertices: a quad from the foot to the joint and a
# triangle to the tip. The tip is 1 m above the foot, so a blade's height is its scale and its share of its height is
# its height above the ground divided by that scale. (name, joint (y, z), tip (y, z))
BLADES = [
    ('blade_low', (0.04, 0.5547), (0.1317, 1.0)),
    ('blade_mid', (0.0883, 0.5706), (0.2868, 1.0)),
    ('blade_high', (0.147, 0.6028), (0.4663, 1.0)),
]
# The straight blade they start from: the foot 1 wide, the joint 0.6 wide at 0.55 m, the tip at 1 m.
JOINT_HEIGHT, JOINT_WIDTH = 0.55, 0.6

LABELS = {
    'phase': 'Wind phase', 's_phase': 'Store phase', 'length': 'Blade height', 's_length': 'Store height',
    'blades': 'Blades', 'pick': 'Pick a blade', 'pos': 'Position', 'outward': 'Outward', 'wobble': 'Wobble',
    'away': 'Add wobble', 'align': 'Turn away', 'width': 'Blade width', 'n_length': 'Read height', 'size': 'Blade size',
    'inst': 'Blade on each point', 'realize': 'Realize blades',
    'n_phase': 'Read phase', 'n_length2': 'Read height again', 'pos2': 'Blade position', 'sep': 'Height above ground',
    'share': 'Share of height', 'col': 'Pack colors', 's_col': 'Store colors', 'd': 'Blade feet',
}

CHAPTERS = [
    {
        'key': 'feet',
        'title': 'Blade feet',
        'flow': {'d': (0, 0), 'phase': (1, 1.3), 's_phase': (1, 0), 'length': (2, 1.3), 's_length': (2, 0)},
        'nodes': [
            ('d', 'Distribute Points on Faces', {'distribute_method': 'RANDOM'}, {'Density': 150.0}),
            ('phase', 'Random Value', {'data_type': 'FLOAT'}, {'Min': 0.0, 'Max': 1.0, 'Seed': 1}),
            ('s_phase', 'Store Named Attribute', {'data_type': 'FLOAT', 'domain': 'POINT'}, {'Name': 'phase'}),
            ('length', 'Random Value', {'data_type': 'FLOAT'}, {'Min': 0.28, 'Max': 0.36, 'Seed': 2}),
            ('s_length', 'Store Named Attribute', {'data_type': 'FLOAT', 'domain': 'POINT'}, {'Name': 'height'}),
        ],
        'links': [
            ('in', 'Geometry', 'd', 'Mesh'),
            ('in', 'Seed', 'd', 'Seed'),
            ('d', 'Points', 's_phase', 'Geometry'),
            ('phase', 'Value', 's_phase', 'Value'),
            ('s_phase', 'Geometry', 's_length', 'Geometry'),
            ('length', 'Value', 's_length', 'Value'),
            ('s_length', 'Geometry', 'out', 'Geometry'),
        ],
    },
    {
        'key': 'blades',
        'title': 'Blades',
        'flow': {'blades': (0, 2.6), 'pick': (0, 1.3), 'pos': (0, 4.0), 'outward': (1, 4.0), 'wobble': (1, 5.3), 'away': (2, 4.0), 'align': (3, 4.0),
                 'width': (2, 2.6), 'n_length': (2, 1.3), 'size': (3, 2.6), 'inst': (4, 0), 'realize': (5, 0)},
        'nodes': [
            ('blades', 'Collection Info', {'transform_space': 'RELATIVE'}, {'Collection': 'grass_blades', 'Separate Children': True, 'Reset Children': True}),
            ('pick', 'Random Value', {'data_type': 'INT'}, {'Min': 0, 'Max': 2, 'Seed': 3}),
            ('pos', 'Position', {}, {}),
            ('outward', 'Vector Math', {'operation': 'NORMALIZE'}, {}),
            ('wobble', 'Random Value', {'data_type': 'FLOAT_VECTOR'}, {'Min': (-0.84, -0.84, 0.0), 'Max': (0.84, 0.84, 0.0), 'Seed': 4}),
            ('away', 'Vector Math', {'operation': 'ADD'}, {}),
            ('align', 'Align Rotation to Vector', {'axis': 'Y', 'pivot_axis': 'Z'}, {}),
            ('width', 'Random Value', {'data_type': 'FLOAT'}, {'Min': 0.05, 'Max': 0.07, 'Seed': 5}),
            ('n_length', 'Named Attribute', {'data_type': 'FLOAT'}, {'Name': 'height'}),
            ('size', 'Combine XYZ', {}, {}),
            ('inst', 'Instance on Points', {}, {'Pick Instance': True}),
            ('realize', 'Realize Instances', {}, {}),
        ],
        'links': [
            ('s_length', 'Geometry', 'inst', 'Points'),
            ('blades', 'Instances', 'inst', 'Instance'),
            ('pick', 'Value', 'inst', 'Instance Index'),
            ('pos', 'Position', 'outward', 'Vector'),
            ('outward', 'Vector', 'away', 'Vector'),
            ('wobble', 'Value', 'away', 'Vector_001'),
            ('away', 'Vector', 'align', 'Vector'),
            ('align', 'Rotation', 'inst', 'Rotation'),
            ('width', 'Value', 'size', 'X'),
            ('n_length', 'Attribute', 'size', 'Y'),
            ('n_length', 'Attribute', 'size', 'Z'),
            ('size', 'Vector', 'inst', 'Scale'),
            ('inst', 'Instances', 'realize', 'Geometry'),
            ('realize', 'Geometry', 'out', 'Geometry'),
        ],
    },
    {
        'key': 'colors',
        'title': 'Colors',
        'flow': {'n_phase': (0, 0), 'pos2': (0, 1.2), 'sep': (1, 1.2), 'n_length2': (1, 2.4), 'share': (2, 1.8), 'col': (3, 0.6), 's_col': (4, 0)},
        'nodes': [
            ('n_phase', 'Named Attribute', {'data_type': 'FLOAT'}, {'Name': 'phase'}),
            ('pos2', 'Position', {}, {}),
            ('sep', 'Separate XYZ', {}, {}),
            ('n_length2', 'Named Attribute', {'data_type': 'FLOAT'}, {'Name': 'height'}),
            ('share', 'Math', {'operation': 'DIVIDE', 'use_clamp': True}, {}),
            ('col', 'Combine Color', {'mode': 'RGB'}, {'Green': 0.0, 'Blue': 0.0}),
            ('s_col', 'Store Named Attribute', {'data_type': 'FLOAT_COLOR', 'domain': 'POINT'}, {'Name': 'Col'}),
        ],
        'links': [
            ('pos2', 'Position', 'sep', 'Vector'),
            ('sep', 'Z', 'share', 'Value'),
            ('n_length2', 'Attribute', 'share', 'Value_001'),
            ('n_phase', 'Attribute', 'col', 'Red'),
            ('share', 'Value', 'col', 'Alpha'),
            ('realize', 'Geometry', 's_col', 'Geometry'),
            ('col', 'Color', 's_col', 'Value'),
            ('s_col', 'Geometry', 'out', 'Geometry'),
        ],
    },
]


def build(tree, collection, chapters=None):
    # Builds the whole group with the API, for the headless checks. The Seed input is added first.
    if 'Seed' not in [item.name for item in tree.interface.items_tree]:
        tree.interface.new_socket('Seed', in_out='INPUT', socket_type='NodeSocketInt')
    nodes = {'in': next(n for n in tree.nodes if n.bl_idname == 'NodeGroupInput'), 'out': next(n for n in tree.nodes if n.bl_idname == 'NodeGroupOutput')}
    for chapter in (chapters or CHAPTERS):
        for key, search, settings, inputs in chapter['nodes']:
            node = tree.nodes.new(IDNAMES[search])
            nodes[key] = node
            node.label = LABELS[key]
            base.apply(node, settings, {name: value for name, value in inputs.items() if name != 'Collection'})
            if search == 'Collection Info':
                base.socket(node, 'Collection', False).default_value = collection
        for a, output, b, inp in chapter['links']:
            tree.links.new(base.socket(nodes[a], output, True), base.socket(nodes[b], inp, False))
    return nodes


# The Paint Part group: four numbers in, one vertex color out. A flower part gets its color (red, green, blue) and its
# petal mask (alpha) from the numbers typed into its modifier. The group's inputs are made by dragging from the Group
# Input's empty socket to the node's own socket, so each takes that socket's name.
LABELS.update({'mix': 'Pack color', 'paint': 'Store color'})
PAINT_INPUTS = ('Red', 'Green', 'Blue', 'Alpha')
PAINT_CHAPTER = {
    'key': 'paint',
    'title': 'Paint Part',
    'flow': {'mix': (0, 1.0), 'paint': (1, 0)},
    'nodes': [
        ('mix', 'Combine Color', {'mode': 'RGB'}, {}),
        ('paint', 'Store Named Attribute', {'data_type': 'FLOAT_COLOR', 'domain': 'POINT'}, {'Name': 'Col'}),
    ],
    'links': [
        ('in', 'Red', 'mix', 'Red'),
        ('in', 'Green', 'mix', 'Green'),
        ('in', 'Blue', 'mix', 'Blue'),
        ('in', 'Alpha', 'mix', 'Alpha'),
        ('in', 'Geometry', 'paint', 'Geometry'),
        ('mix', 'Color', 'paint', 'Value'),
        ('paint', 'Geometry', 'out', 'Geometry'),
    ],
}

socket = base.socket
