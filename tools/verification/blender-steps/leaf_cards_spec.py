# The Leaf Cards node group of lesson 26, as data: the lesson's step script builds it in Blender's editor from this, and
# the lesson's tables are written from it, so the text and the group cannot drift apart.
#
# A node is (key, search text, settings, inputs): `search` is what is typed into Shift+A, `settings` are the node's own
# dropdowns (Blender property names), `inputs` the values typed into its fields. A link is (from key, output, to key,
# input). Keys 'in' and 'out' are the Group Input and Group Output nodes.

# What the reader calls each node: a label, set with F2, so the tables and the figures name the same nodes.
LABELS = {
    'pos': 'Position', 'sep': 'Height', 'high': 'High enough', 'd1': 'Clump centers', 'push': 'Push depth',
    'pushv': 'Push inward', 'sp': 'Move inside', 'depth': 'Depth value', 's_depth': 'Store depth', 's_env': 'Store envelope normal',
    'ico': 'Clump ball', 'i1': 'Ball on each center', 'r1': 'Realize balls',
    'd2': 'Card points', 'n_env': 'Envelope normal', 'up': 'Tip up', 'wobble': 'Wobble', 'face': 'Add wobble',
    'facen': 'Facing', 'az': 'Face this way', 'ay': 'Roll to the clump', 'scale': 'Card size', 'grid': 'Card',
    'uv': 'Card UVs', 'i2': 'Card on each point',
    'phase': 'Wind phase', 's_phase': 'Store phase', 's_cn': 'Store clump normal', 'r2': 'Realize cards',
    'n_phase': 'Read phase', 'n_depth': 'Read depth', 'n_uv': 'Read UVs', 'uvsep': 'Card height', 'col': 'Pack colors',
    's_col': 'Store colors', 'n_cn': 'Read clump normal', 'n_env2': 'Read envelope normal', 'cn14': 'Clump strength',
    'nsum': 'Blend normals', 'nnorm': 'Unit normal', 'sn': 'Set normals',
}

# Chapter title, intro, and nodes in the order the reader adds them.
CHAPTERS = [
    {
        'key': 'clumps',
        'flow': {'pos': (0, 0), 'sep': (1, 0), 'high': (2, 0), 'd1': (3, 0), 'push': (3, 1.1), 'pushv': (4, 1.1), 'depth': (4, 2.2), 'sp': (5, 0), 's_depth': (6, 0), 's_env': (7, 0)},
        'title': 'Clump centers',
        'nodes': [
            ('pos', 'Position', {}, {}),
            ('sep', 'Separate XYZ', {}, {}),
            ('high', 'Compare', {'data_type': 'FLOAT', 'operation': 'GREATER_THAN'}, {'B': 2.7}),
            ('d1', 'Distribute Points on Faces', {'distribute_method': 'RANDOM'}, {'Density': 0.8, 'Seed': 3}),
            ('push', 'Random Value', {'data_type': 'FLOAT'}, {'Min': -0.9, 'Max': 0.0, 'Seed': 1}),
            ('pushv', 'Vector Math', {'operation': 'SCALE'}, {}),
            ('sp', 'Set Position', {}, {}),
            ('depth', 'Map Range', {'data_type': 'FLOAT'}, {'From Min': -0.9, 'From Max': 0.0, 'To Min': 0.0, 'To Max': 1.0}),
            ('s_depth', 'Store Named Attribute', {'data_type': 'FLOAT', 'domain': 'POINT'}, {'Name': 'depth'}),
            ('s_env', 'Store Named Attribute', {'data_type': 'FLOAT_VECTOR', 'domain': 'POINT'}, {'Name': 'env_normal'}),
        ],
        'links': [
            ('pos', 'Position', 'sep', 'Vector'),
            ('sep', 'Z', 'high', 'A'),
            ('in', 'Geometry', 'd1', 'Mesh'),
            ('high', 'Result', 'd1', 'Selection'),
            ('d1', 'Normal', 'pushv', 'Vector'),
            ('push', 'Value', 'pushv', 'Scale'),
            ('d1', 'Points', 'sp', 'Geometry'),
            ('pushv', 'Vector', 'sp', 'Offset'),
            ('push', 'Value', 'depth', 'Value'),
            ('sp', 'Geometry', 's_depth', 'Geometry'),
            ('depth', 'Result', 's_depth', 'Value'),
            ('s_depth', 'Geometry', 's_env', 'Geometry'),
            ('d1', 'Normal', 's_env', 'Value'),
            ('s_env', 'Geometry', 'out', 'Geometry'),
        ],
    },
    {
        'key': 'spheres',
        'flow': {'ico': (0, 1), 'i1': (1, 0), 'r1': (2, 0)},
        'title': 'Clump spheres',
        'nodes': [
            ('ico', 'Ico Sphere', {}, {'Radius': 0.75, 'Subdivisions': 3}),
            ('i1', 'Instance on Points', {}, {}),
            ('r1', 'Realize Instances', {}, {}),
        ],
        'links': [
            ('s_env', 'Geometry', 'i1', 'Points'),
            ('ico', 'Mesh', 'i1', 'Instance'),
            ('i1', 'Instances', 'r1', 'Geometry'),
            ('r1', 'Geometry', 'out', 'Geometry'),
        ],
    },
    {
        'key': 'cards',
        'flow': {'d2': (0, 0), 'n_env': (0, 1.4), 'up': (1, 1.4), 'wobble': (1, 2.5), 'face': (2, 1.4), 'facen': (3, 1.4), 'az': (4, 1.4), 'ay': (5, 1.4), 'grid': (4, 3.2), 'uv': (5, 3.2), 'scale': (6, 2.6), 'i2': (7, 1.0)},
        'title': 'Cards',
        'nodes': [
            ('d2', 'Distribute Points on Faces', {'distribute_method': 'RANDOM'}, {'Density': 4.0, 'Seed': 5}),
            ('n_env', 'Named Attribute', {'data_type': 'FLOAT_VECTOR'}, {'Name': 'env_normal'}),
            ('up', 'Vector Math', {'operation': 'ADD'}, {'Vector_001': (0.0, 0.0, 0.6)}),
            ('wobble', 'Random Value', {'data_type': 'FLOAT_VECTOR'}, {'Min': (-0.85, -0.85, -0.85), 'Max': (0.85, 0.85, 0.85), 'Seed': 7}),
            ('face', 'Vector Math', {'operation': 'ADD'}, {}),
            ('facen', 'Vector Math', {'operation': 'NORMALIZE'}, {}),
            ('az', 'Align Rotation to Vector', {'axis': 'Z', 'pivot_axis': 'AUTO'}, {}),
            ('ay', 'Align Rotation to Vector', {'axis': 'Y', 'pivot_axis': 'Z'}, {}),
            ('scale', 'Random Value', {'data_type': 'FLOAT_VECTOR'}, {'Min': (0.8, 0.8, 0.8), 'Max': (1.2, 1.2, 1.2), 'Seed': 11}),
            ('grid', 'Grid', {}, {'Size X': 1.25, 'Size Y': 1.25, 'Vertices X': 2, 'Vertices Y': 2}),
            ('uv', 'Store Named Attribute', {'data_type': 'FLOAT2', 'domain': 'CORNER'}, {'Name': 'UVMap'}),
            ('i2', 'Instance on Points', {}, {}),
        ],
        'links': [
            ('r1', 'Geometry', 'd2', 'Mesh'),
            ('n_env', 'Attribute', 'up', 'Vector'),
            ('up', 'Vector', 'face', 'Vector'),
            ('wobble', 'Value', 'face', 'Vector_001'),
            ('face', 'Vector', 'facen', 'Vector'),
            ('facen', 'Vector', 'az', 'Vector'),
            ('az', 'Rotation', 'ay', 'Rotation'),
            ('d2', 'Normal', 'ay', 'Vector'),
            ('grid', 'Mesh', 'uv', 'Geometry'),
            ('grid', 'UV Map', 'uv', 'Value'),
            ('d2', 'Points', 'i2', 'Points'),
            ('uv', 'Geometry', 'i2', 'Instance'),
            ('ay', 'Rotation', 'i2', 'Rotation'),
            ('scale', 'Value', 'i2', 'Scale'),
            ('i2', 'Instances', 'out', 'Geometry'),
        ],
    },
    {
        'key': 'data',
        'flow': {'phase': (0, 1), 's_phase': (1, 0), 's_cn': (2, 0), 'r2': (3, 0)},
        'title': 'Data on every card',
        'nodes': [
            ('phase', 'Random Value', {'data_type': 'FLOAT'}, {'Min': 0.0, 'Max': 1.0, 'Seed': 13}),
            ('s_phase', 'Store Named Attribute', {'data_type': 'FLOAT', 'domain': 'INSTANCE'}, {'Name': 'phase'}),
            ('s_cn', 'Store Named Attribute', {'data_type': 'FLOAT_VECTOR', 'domain': 'INSTANCE'}, {'Name': 'clump_normal'}),
            ('r2', 'Realize Instances', {}, {}),
        ],
        'links': [
            ('i2', 'Instances', 's_phase', 'Geometry'),
            ('phase', 'Value', 's_phase', 'Value'),
            ('s_phase', 'Geometry', 's_cn', 'Geometry'),
            ('d2', 'Normal', 's_cn', 'Value'),
            ('s_cn', 'Geometry', 'r2', 'Geometry'),
            ('r2', 'Geometry', 'out', 'Geometry'),
        ],
    },
    {
        'key': 'shading',
        'flow': {'n_phase': (0, 0), 'n_uv': (0, 1.2), 'uvsep': (1, 1.2), 'n_depth': (0, 2.4), 'col': (2, 0.6), 's_col': (3, 0), 'n_cn': (0, 3.6), 'n_env2': (0, 4.8), 'cn14': (1, 3.6), 'nsum': (2, 4), 'nnorm': (3, 4), 'sn': (4, 1.5)},
        'title': 'Colors and normals',
        'nodes': [
            ('n_phase', 'Named Attribute', {'data_type': 'FLOAT'}, {'Name': 'phase'}),
            ('n_depth', 'Named Attribute', {'data_type': 'FLOAT'}, {'Name': 'depth'}),
            ('n_uv', 'Named Attribute', {'data_type': 'FLOAT_VECTOR'}, {'Name': 'UVMap'}),
            ('uvsep', 'Separate XYZ', {}, {}),
            ('col', 'Combine Color', {'mode': 'RGB'}, {'Alpha': 1.0}),
            ('s_col', 'Store Named Attribute', {'data_type': 'FLOAT_COLOR', 'domain': 'POINT'}, {'Name': 'Col'}),
            ('n_cn', 'Named Attribute', {'data_type': 'FLOAT_VECTOR'}, {'Name': 'clump_normal'}),
            ('n_env2', 'Named Attribute', {'data_type': 'FLOAT_VECTOR'}, {'Name': 'env_normal'}),
            ('cn14', 'Vector Math', {'operation': 'SCALE'}, {'Scale': 1.4}),
            ('nsum', 'Vector Math', {'operation': 'ADD'}, {}),
            ('nnorm', 'Vector Math', {'operation': 'NORMALIZE'}, {}),
            ('sn', 'Set Mesh Normal', {'mode': 'FREE'}, {}),
        ],
        'links': [
            ('n_uv', 'Attribute', 'uvsep', 'Vector'),
            ('n_phase', 'Attribute', 'col', 'Red'),
            ('uvsep', 'Y', 'col', 'Green'),
            ('n_depth', 'Attribute', 'col', 'Blue'),
            ('r2', 'Geometry', 's_col', 'Geometry'),
            ('col', 'Color', 's_col', 'Value'),
            ('n_cn', 'Attribute', 'cn14', 'Vector'),
            ('n_env2', 'Attribute', 'nsum', 'Vector'),
            ('cn14', 'Vector', 'nsum', 'Vector_001'),
            ('nsum', 'Vector', 'nnorm', 'Vector'),
            ('s_col', 'Geometry', 'sn', 'Mesh'),
            ('nnorm', 'Vector', 'sn', 'Custom Normal'),
            ('sn', 'Mesh', 'out', 'Geometry'),
        ],
    },
]


def build(tree, only=None):
    # Builds the whole group, or the chapters named in `only`, with the API: for the headless checks.
    nodes = {'in': next(n for n in tree.nodes if n.bl_idname == 'NodeGroupInput'), 'out': next(n for n in tree.nodes if n.bl_idname == 'NodeGroupOutput')}
    for chapter in CHAPTERS:
        if only and chapter['key'] not in only:
            continue
        for key, search, settings, inputs in chapter['nodes']:
            node = tree.nodes.new(IDNAMES[(search, settings.get('data_type'))] if (search, settings.get('data_type')) in IDNAMES else IDNAMES[search])
            nodes[key] = node
            node.label = LABELS[key]
            apply(node, settings, inputs)
        for a, output, b, inp in chapter['links']:
            tree.links.new(socket(nodes[a], output, True), socket(nodes[b], inp, False))
    return nodes


IDNAMES = {
    'Position': 'GeometryNodeInputPosition',
    'Separate XYZ': 'ShaderNodeSeparateXYZ',
    'Compare': 'FunctionNodeCompare',
    'Distribute Points on Faces': 'GeometryNodeDistributePointsOnFaces',
    'Random Value': 'FunctionNodeRandomValue',
    'Vector Math': 'ShaderNodeVectorMath',
    'Set Position': 'GeometryNodeSetPosition',
    'Map Range': 'ShaderNodeMapRange',
    'Store Named Attribute': 'GeometryNodeStoreNamedAttribute',
    'Ico Sphere': 'GeometryNodeMeshIcoSphere',
    'Instance on Points': 'GeometryNodeInstanceOnPoints',
    'Realize Instances': 'GeometryNodeRealizeInstances',
    'Named Attribute': 'GeometryNodeInputNamedAttribute',
    'Align Rotation to Vector': 'FunctionNodeAlignRotationToVector',
    'Grid': 'GeometryNodeMeshGrid',
    'Combine Color': 'FunctionNodeCombineColor',
    'Set Mesh Normal': 'GeometryNodeSetMeshNormal',
}


def socket(node, name, output):
    # An enabled socket by name; names repeat in Vector Math and Random Value, so 'Vector_001' means the second one.
    sockets = node.outputs if output else node.inputs
    index = 0
    if name.endswith('_001'):
        name, index = name[:-4], 1
    found = [item for item in sockets if item.name == name and item.enabled]
    return found[index]


def apply(node, settings, inputs):
    for key, value in settings.items():
        setattr(node, key, value)
    for name, value in inputs.items():
        found = socket(node, name, False)
        found.default_value = value
