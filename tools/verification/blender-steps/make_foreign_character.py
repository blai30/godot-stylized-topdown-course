# Makes the bonus lesson's stand-in for a downloaded model: the course character with another artist's bone names.
import bpy
bpy.ops.wm.open_mainfile(filepath='/tmp/sgt-phase1/workbench/art_source/character/character.blend')
arm=bpy.data.objects['Armature']; body=bpy.data.objects['body']
rename={'Hips':'pelvis','Spine':'spine_01','Chest':'spine_02','UpperChest':'torso_top','Neck':'neck_01','Head':'head',
 'LeftShoulder':'clavicle_l','LeftUpperArm':'upperarm_l','LeftLowerArm':'lowerarm_l','LeftHand':'hand_l',
 'RightShoulder':'clavicle_r','RightUpperArm':'upperarm_r','RightLowerArm':'lowerarm_r','RightHand':'hand_r',
 'LeftUpperLeg':'thigh_l','LeftLowerLeg':'calf_l','LeftFoot':'foot_l','LeftToes':'zz_a',
 'RightUpperLeg':'thigh_r','RightLowerLeg':'calf_r','RightFoot':'foot_r','RightToes':'zz_b'}
for bone in arm.data.bones:
    new=rename[bone.name]
    if bone.name in body.vertex_groups: body.vertex_groups[bone.name].name=new
    bone.name=new
arm.name='root'; body.name='Mesh'
for c in list(bpy.data.collections): pass
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); body.select_set(True); bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.gltf(filepath='/tmp/sgt-phase1/workbench/art/character/foreign_character.glb', use_selection=True, export_format='GLB', export_yup=True, export_animations=False)
print('NAMES', sorted(b.name for b in arm.data.bones))
