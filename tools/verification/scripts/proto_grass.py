# Prototype only: FactoryGame's grass clumps (96 curved blades), built headless and exported as one glb per variant.
# Run: Blender -b -P proto_grass.py -- <output folder>
import bpy, math, random, sys, os
from mathutils import Matrix, Vector

out_dir = sys.argv[sys.argv.index('--') + 1]
BLADES, SPREAD, FALLOFF = 96, 0.45, 0.75
WIDTH, MIDDLE, JOINT, BEND, FAN = (0.05, 0.07), 0.6, 0.55, (15.0, 50.0), 40.0
VARIANTS = {'a': (601, (0.28, 0.36)), 'b': (602, (0.32, 0.40)), 'c': (603, (0.25, 0.31))}
FOOT_RANGE = 0.5


def blade(foot, heading, bend, length, width, phase):
    turn = math.radians(bend)

    def along(share):
        radius = length / turn
        return radius * (1.0 - math.cos(turn * share)), radius * math.sin(turn * share)

    mf, mu = along(JOINT)
    tf, tu = along(1.0)
    half = width / 2
    local = [(-half, 0, 0), (half, 0, 0), (-half * MIDDLE, mf, mu), (half * MIDDLE, mf, mu), (0, tf, tu)]
    shares = [0.0, 0.0, JOINT, JOINT, 1.0]
    rot = Matrix.Translation((foot[0], foot[1], 0)) @ Matrix.Rotation(-math.radians(heading), 4, 'Z')
    green, blue = 0.5 + foot[0] / (2 * FOOT_RANGE), 0.5 - foot[1] / (2 * FOOT_RANGE)
    verts = [tuple(rot @ Vector(p)) for p in local]
    colors = [(phase, green, blue, s) for s in shares]
    return verts, [(0, 1, 3, 2), (2, 3, 4)], colors


def clump(name, seed, lengths):
    rng = random.Random(seed)
    verts, faces, colors = [], [], []
    for _ in range(BLADES):
        angle = rng.uniform(0.0, 360.0)
        reach = SPREAD * rng.random() ** FALLOFF
        foot = (reach * math.sin(math.radians(angle)), reach * math.cos(math.radians(angle)))
        heading = angle + rng.uniform(-FAN, FAN)
        v, f, c = blade(foot, heading, rng.uniform(*BEND), rng.uniform(*lengths), rng.uniform(*WIDTH), rng.random())
        base = len(verts)
        verts += v
        faces += [tuple(base + i for i in face) for face in f]
        colors += c
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    attribute = mesh.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for i, color in enumerate(colors):
        attribute.data[i].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    node = material.node_tree.nodes.new('ShaderNodeVertexColor')
    node.layer_name = 'Col'
    material.node_tree.links.new(node.outputs['Color'], material.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mesh.materials.append(material)
    return obj


STEM, CENTER, PETAL = (0.05, 0.14, 0.02), (1.0, 0.58, 0.04), (1.0, 1.0, 1.0)


class Parts:
    def __init__(self):
        self.verts, self.faces, self.colors = [], [], []

    def add(self, verts, faces, color, mask):
        base = len(self.verts)
        self.verts += [tuple(v) for v in verts]
        self.faces += [tuple(base + i for i in f) for f in faces]
        self.colors += [(*color, mask)] * len(verts)

    def lathe(self, profile, segments, color, mask, offset=(0, 0, 0)):
        verts, rings = [], []
        for radius, height in profile:
            if radius == 0:
                rings.append([len(verts)])
                verts.append((offset[0], offset[1], offset[2] + height))
            else:
                ring = []
                for i in range(segments):
                    angle = math.tau * i / segments
                    ring.append(len(verts))
                    verts.append((offset[0] + radius * math.cos(angle), offset[1] + radius * math.sin(angle), offset[2] + height))
                rings.append(ring)
        faces = []
        for lower, upper in zip(rings, rings[1:]):
            for i in range(segments):
                j = (i + 1) % segments
                if len(lower) == 1:
                    faces.append((lower[0], upper[i], upper[j]))
                elif len(upper) == 1:
                    faces.append((lower[i], lower[j], upper[0]))
                else:
                    faces.append((lower[i], lower[j], upper[j], upper[i]))
        self.add(verts, faces, color, mask)

    def petal(self, top, heading, length, width, tilt):
        local = [Vector((0, 0, 0)), Vector((length * 0.5, -width / 2, 0)), Vector((length, 0, 0)), Vector((length * 0.5, width / 2, 0))]
        turn = Matrix.Translation(top) @ Matrix.Rotation(-math.radians(heading) + math.pi / 2, 4, 'Z') @ Matrix.Rotation(math.radians(tilt), 4, 'Y')
        self.add([turn @ v for v in local], [(0, 1, 2, 3)], PETAL, 1.0)


def daisy():
    parts = Parts()
    parts.lathe([(0.012, 0.0), (0.0, 0.3)], 4, STEM, 0.0)
    parts.lathe([(0.03, 0.0), (0.03, 0.006), (0.0, 0.012)], 6, CENTER, 0.0, (0, 0, 0.295))
    for i in range(8):
        parts.petal((0, 0, 0.3), i * 45, 0.09, 0.05, 15)
    return parts


def cup():
    parts = Parts()
    parts.lathe([(0.012, 0.0), (0.0, 0.26)], 4, STEM, 0.0)
    for i in range(5):
        parts.petal((0, 0, 0.26), i * 72, 0.08, 0.06, -55)
    return parts


def flower(name, parts):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(parts.verts, [], parts.faces)
    mesh.update()
    attribute = mesh.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for i, color in enumerate(parts.colors):
        attribute.data[i].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    node = material.node_tree.nodes.new('ShaderNodeVertexColor')
    node.layer_name = 'Col'
    material.node_tree.links.new(node.outputs['Color'], material.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mesh.materials.append(material)
    return obj


bpy.ops.wm.read_factory_settings(use_empty=True)
os.makedirs(out_dir, exist_ok=True)
for name, parts in (('flower_daisy', daisy()), ('flower_cup', cup())):
    obj = flower(name, parts)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, f'{name}.glb'), export_format='GLB', use_selection=True, export_vertex_color='ACTIVE', export_apply=True)
    print('FLOWER', name, len(obj.data.polygons), 'faces')
    bpy.data.objects.remove(obj)
for variant, (seed, lengths) in VARIANTS.items():
    obj = clump(f'grass_clump_{variant}', seed, lengths)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, f'grass_clump_{variant}.glb'), export_format='GLB', use_selection=True,
                              export_vertex_color='ACTIVE', export_apply=True)
    print('CLUMP', variant, len(obj.data.polygons), 'faces')
    bpy.data.objects.remove(obj)
