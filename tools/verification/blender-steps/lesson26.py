# Lesson 26: leaf cards. Three spheres make the crown's envelope in one object; a Geometry Nodes group, built node by
# node in the editor, scatters clumps of cards through it, with data for the shader in vertex colors and normals.
import math
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(__file__))
import leaf_cards_spec as spec
from node_ui import NodeUI

WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
ONLY = [name for name in os.environ.get('LESSON26_ONLY', '').split(',') if name]


def top(y, height=1080):
    return height - y


# Where each chapter's nodes go, in node space: origin and the number of columns.
LAYOUT = {'clumps': ((0, 300), 5), 'spheres': ((2000, 300), 3), 'cards': ((2900, 450), 4), 'data': ((4900, 300), 4), 'shading': ((6000, 450), 4)}
COLUMN, ROW = 220, 360


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    viewport = d.area('VIEW_3D')
    d.shot('l26_start')

    # Three ellipsoids in one mesh: a sphere, then two more added in Edit Mode, each scaled and moved by typing.
    d.move(*d.center(viewport))
    d.key('A', shift=True)
    yield 0.8
    d.shot('l26_add_menu')
    d.type_text('uv sphere')
    yield 0.8
    d.shot('l26_add_search')
    d.key('RET')
    yield 0.8
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('leaves')
    d.shot('l26_rename_field')
    d.key('RET')
    yield 0.5
    d.key('TAB')
    yield 0.6
    shapes = (((1.25, 1.2, 1.1), (0, 0, 3.45)), ((0.9, 0.85, 0.8), (0.45, 0.3, 3.95)), ((0.85, 0.85, 0.75), (-0.5, -0.25, 3.85)))
    for number, (radii, place) in enumerate(shapes):
        if number:
            d.move(*d.center(viewport))
            d.key('A', shift=True)
            yield 0.8
            d.type_text('uv sphere')
            yield 0.6
            d.key('RET')
            yield 0.8
        d.key('S')
        d.type_text(str(radii[0]))
        d.key('TAB')
        d.type_text(str(radii[1]))
        d.key('TAB')
        d.type_text(str(radii[2]))
        d.key('RET')
        yield 0.4
        d.key('G')
        d.type_text(str(place[0]))
        d.key('TAB')
        d.type_text(str(place[1]))
        d.key('TAB')
        d.type_text(str(place[2]))
        d.key('RET')
        yield 0.5
        d.shot('l26_sphere_{}'.format(number + 1))
    d.key('TAB')
    yield 0.6
    envelope = bpy.data.objects['leaves']
    d.log('ENVELOPE verts {} dims {}'.format(len(envelope.data.vertices), tuple(round(v, 3) for v in envelope.dimensions)))
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.shot('l26_envelope')

    # The Geometry Nodes workspace, a new group, and the node editor over the whole window.
    yield from d.press(980, top(13))
    yield 1.5
    yield from d.press(790, top(516))
    yield 1.0
    tree = envelope.modifiers[0].node_group
    d.log('GROUP {} {}'.format(tree.name, [n.name for n in tree.nodes]))
    d.shot('l26_new_group')
    editor = d.area('NODE_EDITOR')
    d.move(*d.center(editor))
    d.key('SPACE', ctrl=True)
    yield 1.0
    ui = NodeUI(d, tree)
    bpy.context.preferences.view.smooth_view = 0
    nodes = {'in': tree.nodes['Group Input'], 'out': tree.nodes['Group Output']}
    # The group's two ends go to the corners, away from the nodes.
    nodes['in'].location = (-330, 300)
    nodes['out'].location = (-330, 60)
    d.shot('l26_group_ready')

    if os.environ.get('LESSON26_FAST'):
        # For testing the steps after the group: build it with the API instead.
        spec.build(tree)
    else:
        for chapter in spec.CHAPTERS:
            if ONLY and chapter['key'] not in ONLY:
                continue
            yield from build_chapter(d, ui, tree, nodes, chapter)
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('HOME')
    yield 1.0
    d.shot('l26_all_nodes')
    d.log('LINKS {} NODES {}'.format(len(tree.links), len(tree.nodes)))
    mesh = envelope.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    d.log('RESULT faces {} attributes {} custom normals {}'.format(len(mesh.polygons), [a.name for a in mesh.attributes if not a.name.startswith('.')], mesh.has_custom_normals))
    dump = []
    for node in sorted(tree.nodes, key=lambda item: item.name):
        row = [node.name]
        for item in node.inputs:
            value = getattr(item, 'default_value', None)
            if value is not None and not item.is_linked and item.enabled:
                row.append('{}={}'.format(item.name, tuple(round(v, 4) for v in value) if hasattr(value, '__len__') and not isinstance(value, str) else (round(value, 4) if isinstance(value, float) else value)))
        for name in ('data_type', 'domain', 'operation', 'distribute_method', 'mode', 'axis', 'pivot_axis'):
            if hasattr(node, name):
                row.append('{}:{}'.format(name, getattr(node, name)))
        dump.append(' '.join(row))
    d.log('STATE ' + ' | '.join(dump))
    # Back to the whole window.
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('SPACE', ctrl=True)
    yield 1.0
    # The Data tab: the mesh's name, since Godot shows it, and a color attribute named Col, which the exporter writes
    # as the mesh's vertex colors. The group fills it in.
    yield from d.press(1595, top(626))
    yield 0.8
    yield from rename(d, 1760, top(297), 'leaves')
    d.log('MESH NAME {}'.format(envelope.data.name))
    yield from d.press(1680, top(657), ctrl=True)
    yield 0.8
    d.move(1760, top(950))
    yield 0.4
    d.shot('l26_color_attributes')
    yield from slow_click(d, 1892, top(442))
    yield 1.5
    d.move(1860, top(470))
    yield 0.6
    d.shot('l26_color_attribute_dialog')
    yield from d.press(1815, top(451))
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text('Col')
    d.key('RET')
    yield 0.5
    d.shot('l26_color_attribute_named')
    yield from d.press(1829, top(556))
    yield 1.0
    d.log('COLOR ATTRIBUTES {} active {}'.format([(a.name, a.domain, a.data_type) for a in envelope.data.color_attributes], envelope.data.color_attributes.active_color_name))
    d.move(1760, top(950))
    yield 0.4
    d.shot('l26_color_attribute_added')
    # The Layout workspace, the crown, and the exporter.
    yield from d.press(288, top(13))
    yield 1.5
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('NUMPAD_PERIOD')
    yield 1.0
    d.shot('l26_crown')
    yield from d.press(1595, top(449))
    yield 0.8
    d.move(1760, top(900))
    for _ in range(40):
        d.key('WHEELUPMOUSE')
        yield 0.03
    yield 0.5
    d.shot('l26_collection_tab')
    # Exporter, Data > Vertex Colors: write the active color attribute, and only that one.
    d.move(1760, top(900))
    for _ in range(40):
        d.key('WHEELDOWNMOUSE')
        yield 0.03
    yield 0.5
    yield from slow_click(d, 1688, top(512))
    yield 0.6
    d.move(1760, top(900))
    yield 0.4
    d.shot('l26_vertex_colors')
    props = bpy.data.collections['tree_oak'].exporters[0].export_properties
    # The dropdown is set directly; the lesson names the item to pick.
    props.export_vertex_color = 'ACTIVE'
    yield 0.4
    yield from d.press(1747, top(572))
    yield 0.5
    d.move(1760, top(900))
    yield 0.4
    d.log('VERTEX COLOR SETTINGS {} all {}'.format(props.export_vertex_color, props.export_all_vertex_colors))
    if props.export_all_vertex_colors or props.export_vertex_color != 'ACTIVE':
        raise RuntimeError('the vertex color settings did not take')
    d.shot('l26_vertex_color_settings')
    # Back up to the Export All button.
    for _ in range(40):
        d.key('WHEELUPMOUSE')
        yield 0.03
    yield 0.5
    glb = os.path.join(WORKBENCH, 'art', 'nature', 'tree_oak', 'tree_oak.glb')
    before = os.path.getmtime(glb)
    yield from slow_click(d, 1772, top(707))
    yield 3.0
    d.log('GLB exported {} size {}'.format(os.path.getmtime(glb) != before, os.path.getsize(glb)))
    if os.path.getmtime(glb) == before:
        raise RuntimeError('the export did not run')
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))


def rename(d, x, y, text):
    yield from d.press(x, y)
    yield 0.2
    d.key('A', ctrl=True)
    d.type_text(text)
    d.key('RET')
    yield 0.5


def build_chapter(d, ui, tree, nodes, chapter, spec=spec, layout=LAYOUT, prefix='l26'):
    (origin_x, origin_y), columns = layout[chapter['key']]
    count = len(chapter['nodes'])
    rows = -(-count // columns)
    # Two reroutes at the chapter's corners, with the nodes it links from, fit the view to it.
    sources = [nodes[a] for a, _, b, _ in chapter['links'] if a in nodes]
    # While the nodes go in, Group Output waits below and left of them, where the wire from the last chapter does not cross
    # their rows (a node dropped on a wire is inserted into it).
    last = max(column for column, _ in chapter['flow'].values())
    nodes['out'].location = (origin_x - 320, origin_y - 520)
    corners = []
    for corner in ((origin_x - 40, origin_y + 40), (origin_x + columns * COLUMN + 30, origin_y - rows * ROW + 20)):
        reroute = tree.nodes.new('NodeReroute')
        reroute.location = corner
        corners.append(reroute)
    ui.frame(corners + sources + [nodes['out']])
    for reroute in corners:
        tree.nodes.remove(reroute)
    ui.redraw()
    yield 1.5
    d.log('SCALE {} {}'.format(chapter['key'], round(ui.scale(), 3)))
    d.shot(prefix + '_{}_framed'.format(chapter['key']))
    for index, (key, search, settings, inputs) in enumerate(chapter['nodes']):
        x, y = origin_x + (index % columns) * COLUMN, origin_y - (index // columns) * ROW
        before = len(tree.nodes)
        node = yield from ui.place(search, x, y, shot=prefix + '_node' if key == 'pos' else None)
        if len(tree.nodes) != before + 1:
            raise RuntimeError('adding {} made {} nodes'.format(search, len(tree.nodes) - before))
        nodes[key] = node
        # The dropdowns are set directly; the lesson names the item to pick.
        for name, value in settings.items():
            setattr(node, name, value)
        node.location = (x, y)
        yield 0.3
        # F2 names the node, so the lesson's tables and figures call each node the same thing.
        d.key('F2')
        yield 0.4
        d.key('A', ctrl=True)
        d.type_text(spec.LABELS[key])
        d.key('RET')
        yield 0.4
        if node.label != spec.LABELS[key]:
            raise RuntimeError('label of {} is {!r}'.format(key, node.label))
        d.log('PLACED {} as {} at {}'.format(key, node.name, tuple(round(v) for v in node.location)))
    d.shot(prefix + '_{}_placed'.format(chapter['key']))
    # The values, typed into the fields while every field is still showing.
    for key, search, settings, inputs in chapter['nodes']:
        if not inputs:
            continue
        node = nodes[key]
        found = yield from ui.sockets(node)
        for name, value in inputs.items():
            yield from ui.set_value(node, name, value, found)
    ui.redraw()
    d.shot(prefix + '_{}_values'.format(chapter['key']))
    for key, search, settings, inputs in chapter['nodes']:
        node = nodes[key]
        for name, value in inputs.items():
            got = spec.socket(node, name, False).default_value
            expected = value
            if name == 'Collection':
                got = got.name if got else None
            sequence = hasattr(got, '__len__') and not isinstance(got, str)
            same = all(abs(a - b) < 1e-4 for a, b in zip(got, expected)) if sequence else (got == expected if isinstance(expected, str) else abs(got - expected) < 1e-4)
            d.log('VALUE {} {} = {} {}'.format(key, name, tuple(got) if sequence else got, 'ok' if same else 'WRONG, wanted {}'.format(expected)))
            if not same:
                raise RuntimeError('field {}.{} is {}'.format(key, name, got))
    # The links, each a drag from an output socket to an input socket. Per target, the lowest input first: linking
    # an input hides its fields, which moves the rows below it.
    positions = {}
    involved = {key for _, _, key, _ in chapter['links']} | {a for a, _, _, _ in chapter['links']}
    for key in involved:
        positions[key] = yield from ui.sockets(nodes[key])
    # Links from the Group Input go in reading order, each after measuring the Group Input again: dragging from its empty
    # socket makes a new group input named after the socket it lands on, which moves the rows.
    def order(link):
        index = ui.index_of(nodes[link[2]], link[3], False)
        return (link[2], index if link[0] == 'in' else -index)

    ordered = sorted(chapter['links'], key=order)
    for a, output, b, name in ordered:
        if a == 'in':
            positions['in'] = yield from ui.sockets(nodes['in'])
        names = [item.name for item in ui.drawn(nodes[a], True)]
        if a == 'in':
            # Wires leaving the Group Input read as extra glyphs, so its rows are placed by their even spacing, 22.4 node
            # units, down from the first row.
            top = positions['in']['out'][0]
            row_pitch = 22.4 * ui.scale()
            positions['in']['out'] = [top - number * row_pitch for number in range(len(names))]
        out_index = names.index(output) if output in names else names.index('')
        start = (positions[a]['right'], positions[a]['out'][out_index])
        end = (positions[b]['left'], ui.input_y(nodes[b], name, positions[b]))
        yield from ui.link(start, end)
    ui.redraw()
    for a, output, b, name in chapter['links']:
        found = [link for link in tree.links if link.from_node == nodes[a] and link.to_node == nodes[b] and link.to_socket == spec.socket(nodes[b], name, False)]
        d.log('LINK {}.{} -> {}.{} {}'.format(a, output, b, name, 'ok' if found else 'MISSING'))
        if not found:
            d.shot(prefix + '_missing')
            d.log('SOCKETS {} {}'.format(b, positions[b]))
            raise RuntimeError('missing link {}.{} -> {}.{}'.format(a, output, b, name))
    # Tidy the chapter into the order the data flows, and fit the view to it for the figure.
    for key, (column, row) in chapter['flow'].items():
        nodes[key].location = (origin_x + column * COLUMN, origin_y - row * 300)
    nodes['out'].location = (origin_x + (last + 1.3) * COLUMN, origin_y - 150)
    ui.frame([nodes[key] for key in chapter['flow']] + [nodes['out']] + ([nodes['in']] if chapter['key'] == 'clumps' else []))
    yield 1.0
    d.shot(prefix + '_{}_linked'.format(chapter['key']))
    yield from restore_shot(d, prefix + '_{}_view'.format(chapter['key']))


def restore_shot(d, name):
    # Back from the full-window node editor to the workspace, then the 3D view over the whole window for a look at the
    # crown so far, then the node editor over the window again.
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('SPACE', ctrl=True)
    yield 1.2
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.key('SPACE', ctrl=True)
    yield 1.2
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('NUMPAD_PERIOD')
    yield 1.0
    d.shot(name)
    d.key('SPACE', ctrl=True)
    yield 1.2
    d.move(*d.center(d.area('NODE_EDITOR')))
    d.key('SPACE', ctrl=True)
    yield 1.2


def slow_click(d, x, y):
    # Some buttons only take a press that follows a longer hover.
    d.move(x, y)
    yield 1.0
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=x, y=y)
    yield 0.3
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=x, y=y)
    yield 0.5
