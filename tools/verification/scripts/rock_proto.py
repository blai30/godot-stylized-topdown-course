# Builds lesson 9's rock with the operators the lesson names, and reports labels, settings, and the triangle count.
import bpy
import bmesh
from mathutils import Vector

def label(op):
    return op.get_rna_type().name

print('LABELS', {name: label(getattr(bpy.ops.object, name)) for name in ('shade_auto_smooth', 'shade_smooth', 'transform_apply', 'modifier_add')},
      label(bpy.ops.mesh.loopcut_slide), label(bpy.ops.transform.vertex_random), label(bpy.ops.mesh.bevel))
cube = bpy.data.objects['Cube']
cube.name = 'rock_small'
cube.data.name = 'rock_small'
# Blocking: a squat box about 0.6 x 0.5 x 0.35 m.
cube.scale = (0.3, 0.25, 0.175)
bpy.context.view_layer.objects.active = cube
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(cube.data)
# One loop cut around the middle, then pull vertices to break the box: the top narrower, one side leaning.
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=1)
mesh = bmesh.from_edit_mesh(cube.data)
for vertex in mesh.verts:
    if vertex.co.z > 0.1:
        vertex.co.x *= 0.75
        vertex.co.y *= 0.8
        vertex.co.z += 0.03 * (1 if vertex.co.x > 0 else -1)
    if vertex.co.z < -0.1:
        vertex.co.x *= 1.05
bmesh.update_edit_mesh(cube.data)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.vertex_random(offset=0.03, seed=4)
# Rest it on the ground: the lowest point at z = 0, so the origin sits at the base center.
mesh = bmesh.from_edit_mesh(cube.data)
lowest = min(vertex.co.z for vertex in mesh.verts)
for vertex in mesh.verts:
    vertex.co.z -= lowest
bmesh.update_edit_mesh(cube.data)
bpy.ops.object.mode_set(mode='OBJECT')
bevel = cube.modifiers.new('Bevel', 'BEVEL')
bevel.width = 0.04
bevel.segments = 2
bevel.limit_method = 'ANGLE'
bpy.ops.object.shade_auto_smooth()
weighted = cube.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
weighted.keep_sharp = True
print('MODIFIERS', [(m.name, m.type) for m in cube.modifiers])
print('BEVEL PROPS', {p.identifier: p.name for p in bevel.bl_rna.properties if p.identifier in ('width', 'segments', 'limit_method', 'angle_limit', 'harden_normals')}, bevel.angle_limit)
print('WEIGHTED PROPS', {p.identifier: p.name for p in weighted.bl_rna.properties if p.identifier in ('mode', 'weight', 'keep_sharp', 'use_face_influence')})
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = cube.evaluated_get(depsgraph)
evaluated.data.calc_loop_triangles()
print('TRIS', len(evaluated.data.loop_triangles), 'DIMENSIONS', tuple(round(d, 3) for d in cube.dimensions), 'ORIGIN', tuple(cube.location))
