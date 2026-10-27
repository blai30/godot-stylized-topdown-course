# Lesson 40, in Blender: skinning. From character.blend (lesson 39): the mesh is parented to the armature with automatic
# weights, the weights are looked at in Weight Paint mode, limited to four influences and normalized, the parts that should
# not bend (skirt, hips, pack) are made rigid, and the result is tested by posing the bones.
import math
import os
import sys

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top

STOP = os.environ.get('LESSON40_STOP', '')


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    viewport = d.area('VIEW_3D')

    def over_view():
        d.move(*d.center(viewport))

    def search(text):
        over_view()
        d.key('F3')
        yield 0.8
        d.type_text(text)
        yield 1.2
        d.key('RET')
        yield 0.8

    body = bpy.data.objects['body']
    arm = bpy.data.objects['Armature']
    d.shot('l40_start')
    # Select the mesh, then the armature last, so the armature is the active object: click each row in the Outliner.
    yield from d.press(1690, top(184))
    yield 0.4
    yield from d.press(1690, top(164), ctrl=True)
    yield 0.6
    d.log('SELECTED {} active {}'.format(sorted(o.name for o in bpy.context.selected_objects), bpy.context.active_object.name))
    d.shot('l40_selected')
    over_view()
    d.key('P', ctrl=True)
    yield 1.0
    d.shot('l40_parent_menu')
    yield from slow_click(d, 680, top(642))
    yield 1.5
    me = body.data
    groups = [g.name for g in body.vertex_groups]
    most = max(sum(1 for g in v.groups if g.weight > 0.0001) for v in me.vertices)
    d.log('PARENTED parent {} modifiers {} groups {} most influences {}'.format(body.parent.name if body.parent else None, [(m.name, m.type) for m in body.modifiers], len(groups), most))
    d.shot('l40_parented')
    # Click the mesh in the viewport, on the side of the chest, away from the bones: it becomes the selected object.
    over_view()
    d.key('ESC')
    yield 0.4
    region = d.region(viewport)
    point = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, Vector((0.15, 0.0, 1.2)))
    d.click(region.x + int(point.x), region.y + int(point.y))
    yield 0.6
    d.log('ACTIVE {}'.format(bpy.context.active_object.name))
    # The Object Data tab lists the vertex groups the automatic weights made: one per bone.
    d.shot('l40_groups')

    def stats(note):
        me = body.data
        counts = [sum(1 for g in v.groups if g.weight > 0.0001) for v in me.vertices]
        sums = [sum(g.weight for g in v.groups) for v in me.vertices]
        d.log('WEIGHTS {} most influences {} vertices over 4 {} sum range {:.3f} to {:.3f}'.format(note, max(counts), sum(1 for c in counts if c > 4), min(sums), max(sums)))

    def show_group(name, shot):
        body.vertex_groups.active_index = body.vertex_groups[name].index
        yield 0.8
        d.shot(shot)

    def pose(rotations, shot):
        # Rotate bones in Pose Mode, as the reader does with R, and look; then clear the pose again.
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
        for name, (axis, degrees) in rotations.items():
            bone = arm.pose.bones[name]
            bone.rotation_mode = 'XYZ'
            euler = [0.0, 0.0, 0.0]
            euler['XYZ'.index(axis)] = math.radians(degrees)
            bone.rotation_euler = euler
        bpy.context.view_layer.update()
        yield 0.8
        d.shot(shot)
        for bone in arm.pose.bones:
            bone.rotation_euler = (0.0, 0.0, 0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = body
        yield 0.4

    stats('automatic')
    # Weight Paint mode (the mode menu in the header), and the weights of a few bones: red is 1, blue is 0.
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    yield 1.0
    yield from show_group('LeftUpperArm', 'l40_weights_arm')
    yield from show_group('LeftUpperLeg', 'l40_weights_leg')
    yield from show_group('Hips', 'l40_weights_hips')
    bpy.ops.object.mode_set(mode='OBJECT')
    yield 0.6
    # The first pose test: the left arm raised, the left leg lifted, the spine bent.
    TEST = {'LeftUpperArm': ('Y', 80), 'LeftUpperLeg': ('X', -60), 'Spine': ('X', 25)}
    yield from pose(TEST, 'l40_pose_automatic')
    if STOP == 'pose':
        return

    # Limit Total, from Weight Paint mode's Weights menu: no vertex keeps more than four bones. Then Normalize All.
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    yield 0.8
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    stats('limited')
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    stats('normalized')
    d.shot('l40_limited')
    bpy.ops.object.mode_set(mode='OBJECT')
    yield 0.6

    # Rigid parts: in Edit Mode, box select a part's vertices, remove them from every group, and Assign them to one group at
    # weight 1. The Assign button is in the Object Data tab.
    over_view()
    d.key('TAB')
    yield 1.0
    d.key('ONE')
    yield 0.4
    d.key('Z', alt=True)
    yield 0.5

    def box_vertices(note, view_key, ctrl, low, high, axes, predicate):
        over_view()
        d.key(view_key, ctrl=ctrl)
        yield 0.8
        bm = bmesh.from_edit_mesh(body.data)
        expected = {v.index for v in bm.verts if predicate(v.co)}
        corners = []
        for corner_values in (low, high):
            corner = Vector((0, 0, 0))
            corner[axes[0]] = corner_values[0]
            corner[axes[1]] = corner_values[1]
            region = d.region(viewport)
            local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, body.matrix_world @ corner)
            corners.append((region.x + int(local.x), region.y + int(local.y)))
        over_view()
        d.key('A', alt=True)
        yield 0.3
        d.key('B')
        yield 0.3
        yield from d.drag(corners[0], corners[1])
        yield 0.5
        chosen = {v.index for v in bmesh.from_edit_mesh(body.data).verts if v.select}
        d.log('BOX {} expected {} selected {} missing {} extra {}'.format(note, len(expected), len(chosen), len(expected - chosen), len(chosen - expected)))
        if chosen != expected:
            raise RuntimeError('box select mismatch ' + note)

    def rigid(group):
        # Remove the selected vertices from every group, then Assign them to the group at weight 1.
        bpy.ops.object.vertex_group_remove_from(use_all_groups=True)
        body.vertex_groups.active_index = body.vertex_groups[group].index
        yield 0.5
        yield from d.press(1657, top(486))
        yield 0.6
        bm = bmesh.from_edit_mesh(body.data)
        deform = bm.verts.layers.deform.active
        weights = {tuple(round(w, 3) for w in v[deform].values()) for v in bm.verts if v.select}
        groups = {tuple(sorted(body.vertex_groups[i].name for i in v[deform].keys())) for v in bm.verts if v.select}
        d.log('RIGID {} groups {} weights {}'.format(group, groups, weights))
        if groups != {(group,)} or weights != {(1.0,)}:
            raise RuntimeError('not rigid ' + group)

    yield from box_vertices('skirt', 'NUMPAD_1', False, (-0.235, 0.79), (0.235, 1.005), (0, 2), lambda c: 0.795 <= c.z <= 1.005 and abs(c.x) < 0.235 and c.y < 0.2)
    yield from rigid('Hips')
    yield from box_vertices('pack', 'NUMPAD_3', False, (0.15, 1.05), (0.30, 1.42), (1, 2), lambda c: c.y > 0.15 and 1.05 <= c.z <= 1.42)
    yield from rigid('UpperChest')
    over_view()
    d.key('Z', alt=True)
    yield 0.4
    d.key('A', alt=True)
    yield 0.3
    d.key('TAB')
    yield 0.8
    stats('rigid')
    d.shot('l40_rigid')

    # The second pose test, the same as the first.
    yield from pose(TEST, 'l40_pose_final')
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
