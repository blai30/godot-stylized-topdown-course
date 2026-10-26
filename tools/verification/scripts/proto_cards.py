# Prototype only: cards over an envelope with custom normals, vertex colors, exported with the trunk.
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
random.seed(381)
bpy.ops.wm.open_mainfile(filepath='/tmp/sgt-phase1/workbench/art_source/nature/tree_oak/tree_oak.blend')
trunk = bpy.data.objects['tree_oak']
V = [(-1,0,0,-0.1,0.40),(0,0,0,0.3,0.28),(1,0.03,0,1.0,0.22),(2,0,0.03,2.15,0.20),
 (3,-0.35,0.05,2.75,0.14),(4,-0.7,0.1,3.35,0.08),(5,-0.8,0.15,3.85,0.04),
 (3,0.4,-0.1,2.85,0.14),(7,0.75,-0.15,3.45,0.08),(8,0.85,-0.1,3.95,0.04),
 (3,0.03,0.05,3.05,0.16),(10,0.05,0.1,3.85,0.09),(11,0.03,0.05,4.45,0.04),
 (10,-0.25,0.45,3.55,0.09),(13,-0.35,0.7,4.05,0.04),(10,0.3,-0.5,3.65,0.09),(15,0.45,-0.7,4.15,0.04)]
tm = bpy.data.meshes.new('tree_oak_new')
bm = bmesh.new()
vs = [bm.verts.new((x, y, z)) for _, x, y, z, _ in V]
for i, row in enumerate(V):
    if row[0] >= 0: bm.edges.new((vs[row[0]], vs[i]))
bm.to_mesh(tm); bm.free()
tmp = bpy.data.objects.new('tmp_skin', tm); bpy.context.collection.objects.link(tmp)
tmp.modifiers.new('Skin', 'SKIN')
for sv, row in zip(tm.skin_vertices[0].data, V): sv.radius = (row[4], row[4])
tmp.modifiers.new('Sub', 'SUBSURF').levels = 1
dg = bpy.context.evaluated_depsgraph_get()
ev = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
old_mat = trunk.data.materials[0]
# the evaluated mesh has no UVs: collapse them onto the bark swatch
uvl = ev.uv_layers.new(name='UVMap')
for d in uvl.data: d.uv = (0.0625, 0.6875)
ev.materials.append(old_mat)
for p in ev.polygons: p.use_smooth = True
trunk.data = ev
bpy.data.objects.remove(tmp)
ELL = [((0.0, 0.0, 3.45), (1.25, 1.2, 1.1)), ((0.45, 0.3, 3.95), (0.9, 0.85, 0.8)), ((-0.5, -0.25, 3.85), (0.85, 0.85, 0.75))]
BLEND, CLUMP_BLEND, CLUMP_NORMAL, CLUMP_RISE, CLUMP_CORE, CARD_LIFT, CARD_WOBBLE = 6.0, 2.0, 1.4, 0.15, 0.45, 0.6, 0.85
CLUMP_RADIUS, N_CLUMPS, N_CARDS = 0.75, 30, 460
def shape_reach(c, r, p):
    return math.sqrt(((p.x-c[0])/r[0])**2 + ((p.y-c[1])/r[1])**2 + ((p.z-c[2])/r[2])**2)
def shape_normal(c, r, p):
    n = Vector(((p.x-c[0])/r[0]**2, (p.y-c[1])/r[1]**2, (p.z-c[2])/r[2]**2))
    return n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))
def envelope_reach(p):
    return min(shape_reach(c, r, p) for c, r in ELL)
def envelope_normal(p):
    t = Vector()
    for c, r in ELL:
        t += math.exp(-BLEND * shape_reach(c, r, p)) * shape_normal(c, r, p)
    return t.normalized() if t.length > 1e-12 else Vector((0, 0, 1))
def clump_normal(clumps, p):
    t = Vector()
    for m in clumps:
        away = p - m
        if away.length > 1e-9:
            t += math.exp(-CLUMP_BLEND * (away.length / CLUMP_RADIUS) ** 2) * away.normalized()
    return t.normalized() if t.length > 1e-12 else Vector()
def volume_point():
    while True:
        c, r = random.choice(ELL)
        p = Vector([c[i] + random.uniform(-1, 1) * r[i] for i in range(3)])
        if shape_reach(c, r, p) <= 1.0:
            return p
# Clump centers: spread through the envelope's volume, each lifted out along the envelope normal.
tips = []
while len(tips) < N_CLUMPS:
    p = volume_point()
    if p.z > 2.7 and all((p - q).length > 0.5 for q in tips):
        tips.append(p)
clumps = [t + envelope_normal(t) * CLUMP_RISE for t in tips]
def depth_at(p):
    nearest = min((p - m).length for m in clumps)
    return min(1.0, envelope_reach(p)) * (CLUMP_CORE + (1 - CLUMP_CORE) * min(1.0, nearest / CLUMP_RADIUS))
verts, faces, normals, colors, uvs = [], [], [], [], []
up = Vector((0, 0, 1))
for i in range(N_CARDS):
    while True:
        mid = random.choice(clumps)
        d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized()
        center = mid + d * CLUMP_RADIUS * random.random() ** 0.5
        reach_c = envelope_reach(center)
        over = random.random() < 0.18
        if reach_c > (1.35 if over else 1.12):
            continue
        # A window in the lower front (toward the camera, Blender -Y) keeps the fork and limbs visible.
        if center.z < 3.35 and center.y < 0.3 and abs(center.x) < 0.9:
            continue
        break
    wobble = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * CARD_WOBBLE
    facing = (envelope_normal(center) + up * (0.1 if reach_c > 1.12 else CARD_LIFT) + wobble + (Vector((0, -0.7, 0.5)) if reach_c > 1.12 else Vector())).normalized()
    perp = facing.cross(Vector((1, 0, 0)) if abs(facing.x) < 0.9 else Vector((0, 1, 0))).normalized()
    across = Matrix.Rotation(random.uniform(0, math.tau), 3, facing) @ perp
    upward = facing.cross(across)
    if upward.dot(center - mid) < 0:
        upward, across = -upward, -across
    size = random.uniform(1.0, 1.5)
    half = size / 2
    offs = [half * (-across - upward), half * (across - upward), half * (across + upward), half * (-across + upward)]
    cell = random.randrange(4)
    u0, v0 = (cell % 2) * 0.5, 1 - (cell // 2 + 1) * 0.5
    mirror = random.random() < 0.5
    phase = random.random()
    base = len(verts)
    for k, off in enumerate(offs):
        pos = center + off
        verts.append(pos)
        normals.append((envelope_normal(pos) + CLUMP_NORMAL * clump_normal(clumps, pos)).normalized())
        colors.append((phase, 0.0 if k < 2 else 1.0, depth_at(pos), 1.0))
        cu = (1 if (k in (1, 2)) else 0) ^ (1 if mirror else 0)
        cv = 0 if k < 2 else 1
        uvs.append((u0 + cu * 0.5, v0 + cv * 0.5))
    faces.append((base, base + 1, base + 2, base + 3))
N = len(faces)
mesh = bpy.data.meshes.new('leaves')
mesh.from_pydata([tuple(v) for v in verts], [], faces)
mesh.update()
uv = mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
    for li in poly.loop_indices:
        uv.data[li].uv = uvs[mesh.loops[li].vertex_index]
col = mesh.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
for i, c in enumerate(colors):
    col.data[i].color = c
mesh.normals_split_custom_set_from_vertices([tuple(n) for n in normals])
obj = bpy.data.objects.new('leaves', mesh)
coll = trunk.users_collection[0]
coll.objects.link(obj)
mat = bpy.data.materials.new('leaves')
mesh.materials.append(mat)
mat.use_nodes = True
vc = mat.node_tree.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
bsdf = mat.node_tree.nodes['Principled BSDF']
mat.node_tree.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
coll.exporters[0].export_properties.filepath = '//../../../art/nature/tree_proto/tree_proto.glb'
bpy.context.view_layer.objects.active = obj
for o in bpy.context.selected_objects: o.select_set(False)
print('CARDS', N, 'TRIS', N*2, 'NORMALS custom', mesh.has_custom_normals)
props = coll.exporters[0].export_properties
print([p for p in dir(props) if 'color' in p or 'normal' in p])
bpy.ops.collection.export_all()
print(os.path.exists('/tmp/sgt-phase1/workbench/art/nature/tree_proto/tree_proto.glb'))
