import bpy
op = bpy.ops.transform.vertex_random.get_rna_type()
print('RANDOMIZE', [(p.identifier, p.name) for p in op.properties if p.identifier != 'rna_type'])
loop = bpy.ops.mesh.loopcut_slide.get_rna_type()
print('LOOPCUT', loop.name, [(p.identifier, p.name) for p in loop.properties if p.identifier != 'rna_type'])
print('DIMENSIONS', bpy.types.Object.bl_rna.properties['dimensions'].name)
print('SHADE SMOOTH', bpy.ops.object.shade_smooth.get_rna_type().name, 'MODIFIERS TAB', bpy.types.SpaceProperties.bl_rna.properties['context'].enum_items['MODIFIER'].name)
