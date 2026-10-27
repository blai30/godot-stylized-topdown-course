# Design sheet: a low-poly adventurer in the style of Synty's POLYGON characters: faceted, flat-shaded, simple forms.
import bpy, math, sys
from mathutils import Vector, Euler

out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def srgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def material(name, h, rough=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(h), 1)
    b.inputs['Roughness'].default_value = rough
    return m

C = dict(skin='E9B796', hair='7A3B2A', eye='2A2020', shirt='F0E2C8', tunic='2F6FA3', trim='E8B04A', belt='5B3A24', pants='46505F', boots='6B4A33', bag='A9743F', glove='5B3A24', metal='B8BEC6')
MAT = {k: material(k, v) for k, v in C.items()}

def done(obj, mat):
    obj.data.materials.append(MAT[mat])
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj

def ico(mat, loc, scale, sub=1, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=1, location=loc, rotation=[math.radians(a) for a in rot])
    o = bpy.context.active_object
    o.scale = scale
    return done(o, mat)

def block(mat, loc, size, rot=(0, 0, 0), taper=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=[math.radians(a) for a in rot])
    o = bpy.context.active_object
    o.scale = size
    if taper:
        # Narrow the top face: a simple wedge for soles and shoulders.
        bpy.ops.object.transform_apply(scale=True)
        for v in o.data.vertices:
            if v.co.z > 0:
                v.co.x *= taper[0]
                v.co.y *= taper[1]
    return done(o, mat)

def limb(mat, p0, p1, r0, r1, verts=6, squash=1.0):
    a, b = Vector(p0), Vector(p1)
    mid = (a + b) / 2
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r0, radius2=r1, depth=(b - a).length, location=mid)
    o = bpy.context.active_object
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    o.scale = (1, squash, 1)
    return done(o, mat)

# ---- 1.8 m, seven and a half heads, faces +Y ----
for side in (-1, 1):
    x = side * 0.10
    limb('pants', (x, 0, 0.92), (x, 0.01, 0.50), 0.095, 0.07)      # thigh
    limb('pants', (x, 0.01, 0.50), (x, 0, 0.20), 0.07, 0.065)       # shin
    limb('boots', (x, 0, 0.30), (x, 0, 0.10), 0.085, 0.08)          # boot shaft
    block('boots', (x, 0.05, 0.05), (0.13, 0.28, 0.10), taper=(0.8, 0.8))
    block('belt', (x, 0.05, 0.005), (0.14, 0.29, 0.02))
# Hips, torso, belt, tunic skirt flaps.
block('pants', (0, 0, 0.95), (0.30, 0.20, 0.16), taper=(1.0, 1.0))
limb('tunic', (0, 0, 1.00), (0, 0, 1.43), 0.17, 0.205, verts=8, squash=0.68)
block('belt', (0, 0, 1.04), (0.36, 0.23, 0.05))
block('trim', (0, 0.118, 1.04), (0.06, 0.02, 0.06))
block('tunic', (0, 0.0, 0.88), (0.30, 0.22, 0.14), taper=(1.1, 1.1), rot=(180, 0, 0))
block('tunic', (0.1, 0.0, 0.86), (0.12, 0.23, 0.18), taper=(1.2, 1.0), rot=(180, 0, 0))
block('tunic', (-0.1, 0.0, 0.86), (0.12, 0.23, 0.18), taper=(1.2, 1.0), rot=(180, 0, 0))
# Collar, shoulders, arms (an A-pose), bracers, gloves.
limb('shirt', (0, 0, 1.43), (0, 0, 1.50), 0.12, 0.085, verts=8, squash=0.9)
for side in (-1, 1):
    ico('tunic', (side * 0.215, 0, 1.40), (0.085, 0.085, 0.075), 1)
    limb('shirt', (side * 0.225, 0, 1.39), (side * 0.33, 0.02, 1.12), 0.062, 0.052)
    limb('trim', (side * 0.33, 0.02, 1.12), (side * 0.375, 0.04, 0.99), 0.056, 0.052)
    block('glove', (side * 0.385, 0.05, 0.93), (0.08, 0.09, 0.11), rot=(0, 0, side * 15))
# Pack on the back.
block('bag', (0, -0.18, 1.22), (0.28, 0.14, 0.30))
block('belt', (0, -0.255, 1.22), (0.28, 0.02, 0.05))
# Head: a faceted egg, small nose and ears, hair as a faceted cap with a swept fringe.
ico('skin', (0, 0.0, 1.66), (0.115, 0.125, 0.14), 2)
block('skin', (0, 0.135, 1.64), (0.035, 0.045, 0.055), rot=(20, 0, 0), taper=(0.4, 0.6))
for side in (-1, 1):
    ico('skin', (side * 0.118, 0.0, 1.655), (0.022, 0.03, 0.04), 1)
    ico('eye', (side * 0.05, 0.112, 1.685), (0.014, 0.008, 0.02), 1)
ico('hair', (0, -0.02, 1.705), (0.135, 0.14, 0.125), 2)
ico('hair', (0, -0.115, 1.65), (0.11, 0.08, 0.11), 1)
for x, tilt in ((-0.08, 18), (-0.02, 6), (0.05, -8), (0.10, -20)):
    block('hair', (x, 0.105, 1.775), (0.07, 0.07, 0.07), rot=(25, tilt, tilt))

# ---- Scene ----
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 700
scene.render.resolution_y = 900
world = bpy.data.worlds.new('w')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.78, 0.84, 0.92, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
scene.world = world
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
sun.data.energy = 1.9
sun.data.angle = math.radians(8)
sun.rotation_euler = Euler((math.radians(55), math.radians(15), math.radians(145)))
scene.collection.objects.link(sun)
scene.view_settings.view_transform = 'Standard'

cam_data = bpy.data.cameras.new('cam')
cam_data.type = 'ORTHO'
cam = bpy.data.objects.new('cam', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

def shoot(name, location, rotation, scale):
    cam_data.ortho_scale = scale
    cam.location = location
    cam.rotation_euler = [math.radians(a) for a in rotation]
    scene.render.filepath = f'{out}/{name}.png'
    bpy.ops.render.render(write_still=True)

shoot('front', (0, 10, 0.9), (90, 0, 180), 2.3)
shoot('side', (10, 0, 0.9), (90, 0, 90), 2.3)
shoot('back', (0, -10, 0.9), (90, 0, 0), 2.3)
shoot('top', (0, 0, 10), (0, 0, 0), 1.2)
shoot('three_quarter', (6, 6, 5.6), (63, 0, 135), 2.6)
bpy.ops.mesh.primitive_plane_add(size=40)
ground = bpy.context.active_object
ground.data.materials.append(material('grass', '7DB356'))
forward = Euler((math.radians(35), 0, math.radians(180)), 'XYZ').to_matrix() @ Vector((0, 0, -1))
shoot('game_front', tuple(Vector((0, 0, 0.9)) - forward * 20), (35, 0, 180), 2.8)
tris = sum(len(o.data.polygons) for o in scene.objects if o.type == 'MESH' and o.name != ground.name)
print('POLYGONS', tris)
