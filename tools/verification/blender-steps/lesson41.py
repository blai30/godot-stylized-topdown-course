# Lesson 41, in Blender: export the skinned character. From character.blend (lesson 40): the character collection's exporter
# (set up in lesson 36) writes character.glb with the mesh, its skin, and the armature. The glb is read back for the skin.
import json
import os
import struct
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top

WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
GLB = os.path.join(WORKBENCH, 'art', 'character', 'character.glb')


def read_glb(path):
    data = open(path, 'rb').read()
    length = struct.unpack('<I', data[12:16])[0]
    return json.loads(data[20:20 + length]), data


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
    before = os.path.getmtime(GLB) if os.path.exists(GLB) else 0
    # The Collection tab, the exporter's settings expanded: Data holds the armature options, Animation the clips.
    yield from d.press(1595, top(449))
    yield 0.8
    d.shot('l41_exporter')
    exporter = bpy.data.collections['character'].exporters[0]
    properties = exporter.export_properties
    d.log('EXPORTER path {} skins {} animations {} yup {} apply {}'.format(properties.filepath, properties.export_skins, properties.export_animations, properties.export_yup, properties.export_apply))
    # Animation is off: this file holds no clips, the library supplies them. Click its checkbox in the panel.
    yield from d.press(1660, top(918))
    yield 0.5
    d.log('ANIMATIONS now {}'.format(properties.export_animations))
    d.shot('l41_animation_off')
    yield from d.press(1771, top(708))
    yield 2.5
    after = os.path.getmtime(GLB)
    d.log('EXPORTED changed {} size {}'.format(after > before, os.path.getsize(GLB)))
    gltf, data = read_glb(GLB)
    skin = gltf['skins'][0]
    names = [gltf['nodes'][index]['name'] for index in skin['joints']]
    d.log('SKINS {} joints {} names {}'.format(len(gltf['skins']), len(names), sorted(names)))
    primitive = gltf['meshes'][0]['primitives'][0]
    d.log('ATTRIBUTES {} animations {} images {}'.format(sorted(primitive['attributes']), len(gltf.get('animations', [])), len(gltf.get('images', []))))
    d.shot('l41_exported')
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
