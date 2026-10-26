# Probe: Color Attributes panel and the exporter's vertex color settings.
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
import leaf_cards_spec as spec


def top(y, height=1080):
    return height - y


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    coll = bpy.data.objects['tree_oak'].users_collection[0]
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    me = bpy.data.meshes.new('leaves'); bm.to_mesh(me); bm.free()
    leaves = bpy.data.objects.new('leaves', me); coll.objects.link(leaves)
    for o in bpy.context.view_layer.objects: o.select_set(False)
    leaves.select_set(True); bpy.context.view_layer.objects.active = leaves
    yield 1
    yield from d.press(1595, top(626))
    yield 0.8
    d.move(1760, top(900))
    yield 0.4
    d.shot('l26_p_data')
    yield from d.press(1680, top(657), ctrl=True)
    yield 0.8
    d.move(1760, top(950))
    yield 0.4
    d.shot('l26_p_colorpanel')
    d.move(1892, top(442))
    yield 1.0
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=1892, y=top(442))
    yield 0.3
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=1892, y=top(442))
    yield 1.0
    d.shot('l26_p_coloradd')
    yield 1.5
    d.shot('l26_p_coloradd2')
    d.move(1860, top(470))
    yield 0.6
    d.shot('l26_p_coloradd3')
    d.log('ATTRS {}'.format([a.name for a in leaves.data.color_attributes]))
    d.log('POPUP regions {}'.format([(w.width, w.height) for w in bpy.context.window_manager.windows]))
