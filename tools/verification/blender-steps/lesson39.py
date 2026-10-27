# Lesson 39, in Blender: the armature on Godot's humanoid bone names. From character.blend (lesson 38): back to the Layout
# workspace, one Armature object, its first bone made into Hips, the spine, the left arm and leg extruded one bone at a
# time with their names and positions typed in the Bone tab, then Symmetrize makes the right side.
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top
from character_armature_data import SPINE, ARM, LEG, ARM_ROOT, LEG_ROOT

STOP = os.environ.get('LESSON39_STOP', '')
NAME_FIELD = (1777, 298)
HEAD_ROWS = (366, 385, 405)
TAIL_ROWS = (428, 447, 467)
FIELD_X = 1807


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    # Lesson 38 left the file in the UV Editing workspace: back to Layout.
    yield from d.press(288, top(13))
    yield 2.0
    viewport = d.area('VIEW_3D')

    def over_view():
        d.move(*d.center(viewport))

    def field(x, y, value):
        yield from d.press(x, top(y))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(str(value))
        yield 0.2
        d.key('RET')
        yield 0.35

    def armature():
        return bpy.data.objects['Armature'].data

    def bone_values(bone):
        return tuple(round(v, 4) for v in bone.head), tuple(round(v, 4) for v in bone.tail)

    d.shot('l39_start')
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('A', shift=True)
    yield 0.8
    d.type_text('armature')
    yield 0.9
    d.shot('l39_add_search')
    d.key('RET')
    yield 1.0
    over_view()
    d.key('TAB')
    yield 0.8
    d.shot('l39_first_bone')
    # The Bone tab of the Properties editor: the bone's name, head, and tail.
    yield from slow_click(d, 1595, top(598))
    yield 1.0
    d.shot('l39_bone_tab')

    state = {'relations': False}

    def make(name, head, tail, connected, first=False):
        if not first:
            over_view()
            d.key('E')
            yield 0.4
            d.key('RET')
            yield 0.6
        yield from field(NAME_FIELD[0], NAME_FIELD[1], name)
        if head is not None:
            if connected is False:
                # Not attached to the parent's tail: uncheck Connected in the Relations panel first.
                yield from d.press(1650, top(597))
                yield 0.6
                d.shot('l39_relations')
                state['relations'] = True
            for row, value in zip(HEAD_ROWS, head):
                yield from field(FIELD_X, row, value)
        for row, value in zip(TAIL_ROWS, tail):
            yield from field(FIELD_X, row, value)
        bone = armature().edit_bones[name]
        d.log('BONE {} head {} tail {} parent {} connected {}'.format(name, *bone_values(bone), bone.parent.name if bone.parent else None, bone.use_connect))
        want_head = head if head is not None else tuple(round(v, 4) for v in bone.parent.tail)
        if bone_values(bone) != (tuple(round(v, 4) for v in want_head), tuple(round(v, 4) for v in tail)):
            raise RuntimeError('bone not where typed: ' + name)

    yield from make(*SPINE[0], first=True)
    for row in SPINE[1:]:
        yield from make(*row)
    d.shot('l39_spine')
    if STOP == 'spine':
        return

    # A branch starts as a new single bone, not an extrusion: Add > Single Bone, then its parent is chosen in the Relations
    # panel. (An extrusion from a joint that two bones share also extrudes from the other one.)
    def branch(name, head, tail, parent):
        over_view()
        d.key('A', shift=True)
        yield 1.0
        # The new bone is selected but the old one is still the active bone, which is the one the Bone tab shows. Click
        # the new bone, at the 3D cursor's end of the world and clear of the others, to make it active.
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        from mathutils import Vector
        region = d.region(viewport)
        point = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, Vector((0, 0, 0.3)))
        d.click(region.x + int(point.x), region.y + int(point.y))
        yield 0.6
        d.log('NEW BONE {}'.format(bpy.context.active_bone.name if bpy.context.active_bone else None))
        if bpy.context.active_bone is None or bpy.context.active_bone.name in ('Head', 'Hips'):
            raise RuntimeError('the new bone is not active')
        yield from field(NAME_FIELD[0], NAME_FIELD[1], name)
        for row, value in zip(HEAD_ROWS, head):
            yield from field(FIELD_X, row, value)
        for row, value in zip(TAIL_ROWS, tail):
            yield from field(FIELD_X, row, value)
        # The Relations panel: its Parent field is a search list.
        if not state['relations']:
            yield from d.press(1650, top(597))
            yield 0.8
            state['relations'] = True
        d.shot('l39_relations_panel')
        yield from d.press(1810, top(629))
        yield 1.0
        d.shot('l39_parent_list')
        d.type_text(parent)
        yield 0.8
        d.key('RET')
        yield 0.8
        bone = armature().edit_bones[name]
        d.log('BRANCH {} parent {} connected {}'.format(name, bone.parent.name if bone.parent else None, bone.use_connect))

    yield from branch(*ARM_ROOT)
    for row in ARM:
        yield from make(*row)
    d.shot('l39_arm')
    yield from branch(*LEG_ROOT)
    for row in LEG:
        yield from make(*row)
    d.shot('l39_leg')
    d.log('ALL {}'.format([(b.name, b.parent.name if b.parent else None, b.use_connect) for b in armature().edit_bones]))
    if STOP == 'left':
        return

    # The right side: select every bone and Armature > Symmetrize, which mirrors the left bones across the center line and
    # flips Left to Right in their names.
    over_view()
    d.key('A')
    yield 0.5
    over_view()
    d.key('F3')
    yield 0.8
    d.type_text('symmetrize')
    yield 1.2
    d.shot('l39_symmetrize_search')
    d.key('RET')
    yield 1.2
    d.shot('l39_symmetrized')
    d.log('SYMMETRIZED {}'.format(sorted(b.name for b in armature().edit_bones)))
    if STOP == 'symmetrize':
        return

    # Back to Object Mode; show the bones in front of the mesh so the skeleton can be seen: Armature properties, Viewport Display.
    over_view()
    d.key('TAB')
    yield 0.8
    yield from slow_click(d, 1595, top(570))
    yield 1.0
    yield from d.press(1650, top(619))
    yield 0.8
    yield from d.press(1739, top(740))
    yield 0.5
    yield from d.press(1739, top(674))
    yield 0.6
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.shot('l39_viewport_display')
    d.log('DISPLAY in front {} names {}'.format(bpy.data.objects['Armature'].show_in_front, armature().show_names))
    # The skeleton, read back against Godot's humanoid names and the parent of each bone.
    expected = ['Hips', 'Spine', 'Chest', 'UpperChest', 'Neck', 'Head'] + [side + part for side in ('Left', 'Right') for part in ('Shoulder', 'UpperArm', 'LowerArm', 'Hand', 'UpperLeg', 'LowerLeg', 'Foot', 'Toes')]
    names = sorted(bone.name for bone in armature().bones)
    d.log('NAMES match {} count {}'.format(names == sorted(expected), len(names)))
    d.log('PARENTS {}'.format(sorted((bone.name, bone.parent.name if bone.parent else None) for bone in armature().bones)))
    if names != sorted(expected):
        raise RuntimeError('bone names are not the humanoid names')
    over_view()
    d.key('NUMPAD_3', ctrl=True)
    yield 0.8
    d.shot('l39_side')
    d.key('NUMPAD_1')
    yield 0.6
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
