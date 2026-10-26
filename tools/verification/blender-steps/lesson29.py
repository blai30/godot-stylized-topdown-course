# Lesson 29: a pine. The trunk is lesson 24's steps again with a straight leader (this script runs lesson24.py with the
# pine's numbers), then the crown is a short Geometry Nodes group in the same file, with the same data as lesson 26's.
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import lesson26
import leaf_cards_spec as spec
from node_ui import NodeUI

ONLY = [name for name in os.environ.get('LESSON29_ONLY', '').split(',') if name]


def top(y, height=1080):
    return height - y


def trunk_source():
    text = open(os.path.join(os.path.dirname(__file__), 'lesson24.py'), encoding='utf-8').read()

    def swap(old, new):
        nonlocal text
        if old not in text:
            raise RuntimeError('lesson 24 no longer has: ' + old[:60])
        text = text.replace(old, new)

    swap('tree_oak', 'tree_pine')
    swap('l24_', 'l29_')
    swap("chain = ((0, (0, 0, 0.4)), (1, (0.03, 0, 0.7)), (2, (-0.03, 0.03, 1.15)))",
         "chain = ((0, (0, 0, 0.4)), (1, (0.04, 0, 0.7)), (2, (0, 0.03, 1.3)), (3, (0, 0, 1.3)), (4, (0.02, 0, 0.8)), (5, (0, 0, 0.7)))")
    a = text.index("    plans = (\n")
    b = text.index("    for start, offsets in plans:")
    text = text[:a] + "    plans = ()\n" + text[b:]
    swap("classes = (((0,), 1.6), ((1,), 1.12), ((2,), 0.88), ((3,), 0.8), ((10,), 0.64), ((4, 7), 0.56), ((11, 13, 15), 0.36), ((5, 8), 0.32), ((6, 9, 12, 14, 16), 0.16))",
         "classes = (((0,), 1.2), ((1,), 0.88), ((2,), 0.64), ((3,), 0.4), ((4,), 0.24), ((5, 6), 0.12))")
    swap("for field_y, value in ((122, '0.1875'), (142, '0.6875')):",
         "for field_y, value in ((122, '0.0625'), (142, '0.6875')):")
    return text


namespace = {'__file__': os.path.join(os.path.dirname(__file__), 'lesson24.py')}
exec(compile(trunk_source(), 'lesson24_as_pine.py', 'exec'), namespace)
trunk_steps = namespace['steps']

# The pine's chapters on the oak's canvas.
LAYOUT = {'tiers': ((0, 300), 4), 'cards': ((1500, 450), 4), 'data': ((4000, 300), 3), 'shading': ((4800, 450), 4)}


def crown(d):
    # A plane to hold the group, named needles: the group ignores its mesh.
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    d.key('A', shift=True)
    yield 0.8
    d.type_text('plane')
    yield 0.6
    d.shot('l29_add_plane')
    d.key('RET')
    yield 0.8
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('needles')
    d.key('RET')
    yield 0.5
    needles = bpy.data.objects['needles']
    d.log('NEEDLES {} {}'.format(needles.name, [o.name for o in bpy.data.objects]))
    yield from d.press(980, top(13))
    yield 1.5
    yield from d.press(790, top(516))
    yield 1.0
    tree = needles.modifiers[0].node_group
    d.shot('l29_new_group')
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('SPACE', ctrl=True)
    yield 1.0
    ui = NodeUI(d, tree)
    bpy.context.preferences.view.smooth_view = 0
    nodes = {'in': tree.nodes['Group Input'], 'out': tree.nodes['Group Output']}
    nodes['in'].location = (-330, 300)
    nodes['out'].location = (-330, 60)
    lesson26.LAYOUT = LAYOUT
    if os.environ.get('LESSON29_FAST'):
        spec.build(tree, chapters=spec.PINE_CHAPTERS)
    else:
        for chapter in spec.PINE_CHAPTERS:
            if ONLY and chapter['key'] not in ONLY:
                continue
            yield from lesson26.build_chapter(d, ui, tree, nodes, chapter)
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('HOME')
    yield 1.0
    d.shot('l29_all_nodes')
    d.log('LINKS {} NODES {}'.format(len(tree.links), len(tree.nodes)))
    mesh = needles.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    d.log('RESULT faces {} attributes {} custom normals {} z {} {}'.format(len(mesh.polygons), [a.name for a in mesh.attributes if not a.name.startswith('.')], mesh.has_custom_normals, round(min(v.co.z for v in mesh.vertices), 2), round(max(v.co.z for v in mesh.vertices), 2)))
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('SPACE', ctrl=True)
    yield 1.0
    # The Data tab: the mesh's name, and a color attribute named Col, as in lesson 26.
    yield from d.press(1595, top(626))
    yield 0.8
    yield from lesson26.rename(d, 1760, top(297), 'needles')
    yield from d.press(1680, top(657), ctrl=True)
    yield 0.8
    yield from lesson26.slow_click(d, 1892, top(442))
    yield 1.5
    d.move(1860, top(470))
    yield 0.6
    yield from d.press(1815, top(451))
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text('Col')
    d.key('RET')
    yield 0.5
    yield from d.press(1829, top(556))
    yield 1.0
    d.log('COLOR ATTRIBUTES {} active {}'.format([(a.name, a.domain, a.data_type) for a in needles.data.color_attributes], needles.data.color_attributes.active_color_name))
    # The Layout workspace, the crown, and the exporter's vertex colors.
    yield from d.press(288, top(13))
    yield 1.5
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('NUMPAD_PERIOD')
    yield 1.0
    d.shot('l29_crown')
    yield from d.press(1595, top(449))
    yield 0.8
    d.move(1760, top(900))
    for _ in range(40):
        d.key('WHEELDOWNMOUSE')
        yield 0.03
    yield 0.5
    yield from lesson26.slow_click(d, 1688, top(512))
    yield 0.6
    props = bpy.data.collections['tree_pine'].exporters[0].export_properties
    props.export_vertex_color = 'ACTIVE'
    yield 0.4
    yield from d.press(1747, top(572))
    yield 0.5
    d.move(1760, top(900))
    yield 0.4
    d.log('VERTEX COLOR SETTINGS {} all {}'.format(props.export_vertex_color, props.export_all_vertex_colors))
    if props.export_all_vertex_colors or props.export_vertex_color != 'ACTIVE':
        raise RuntimeError('the vertex color settings did not take')
    d.shot('l29_vertex_color_settings')
    for _ in range(40):
        d.key('WHEELUPMOUSE')
        yield 0.03
    yield 0.5
    glb = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench', 'art', 'nature', 'tree_pine', 'tree_pine.glb')
    before = os.path.getmtime(glb)
    yield from lesson26.slow_click(d, 1772, top(707))
    yield 3.0
    d.log('GLB exported {} size {}'.format(os.path.getmtime(glb) != before, os.path.getsize(glb)))
    if os.path.getmtime(glb) == before:
        raise RuntimeError('the export did not run')
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))


def steps(d):
    yield from trunk_steps(d)
    yield from crown(d)
