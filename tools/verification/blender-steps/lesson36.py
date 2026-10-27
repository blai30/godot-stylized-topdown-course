# Lesson 36, in Blender: the character's blockout. From the startup file lesson 8 saved: save as character.blend, add
# the two reference sheets from lesson 35 as image empties in front and left view, build the body from cubes and
# spheres at the sheet's sizes, check it against the sheet and by measurement, and save.
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top
from character_blockout_data import PARTS, REFERENCES

STOP = os.environ.get('LESSON36_STOP', '')
WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
FOLDER = os.path.join(WORKBENCH, 'art_source', 'character')


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    yield 0.4
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
        yield 0.4

    def typed(*values):
        for number, value in enumerate(values):
            if number:
                d.key('TAB')
            d.type_text(str(value))

    d.shot('l36_start')

    # Save As into art_source/character, beside the sheet.
    over_view()
    d.key('S', ctrl=True, shift=True)
    yield 2
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(FOLDER + os.sep, target=browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l36_save_folder', browser)
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('character.blend', target=browser)
    d.key('RET', target=browser)
    yield 0.4
    d.shot('l36_save_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 2.5
    d.wake()
    yield 0.5
    d.log('SAVED {}'.format(bpy.data.filepath))

    # Delete the starting cube: select it by clicking its row in the outliner, then X over the viewport.
    over_view()
    d.key('A')
    d.key('X')
    yield 0.8
    d.shot('l36_delete_menu')
    d.key('RET')
    yield 0.6
    d.log('OBJECTS after delete {}'.format([o.name for o in bpy.data.objects]))

    # The reference images: front view first, Add > Image > Reference, and the sheet picked in the File Browser.
    def add_reference(file_name, shot):
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text('reference')
        yield 1.0
        d.key('RET')
        yield 2.5
        b = d.browser()
        yield from d.press(545, top(19, d.pixels(b.height)), target=b)
        yield 0.3
        yield from d.press(545, top(19, d.pixels(b.height)), target=b)
        yield 0.3
        d.key('A', ctrl=True, target=b)
        d.type_text(FOLDER + os.sep, target=b)
        d.key('RET', target=b)
        yield 1
        yield from d.press(455, top(578, d.pixels(b.height)), target=b)
        yield 0.3
        yield from d.press(455, top(578, d.pixels(b.height)), target=b)
        yield 0.3
        d.key('A', ctrl=True, target=b)
        d.type_text(file_name, target=b)
        d.key('RET', target=b)
        yield 0.5
        d.shot(shot + '_browser', b)
        yield from d.press(d.save_button_x(b), 21, target=b)
        yield 1.5

    for index, (file_name, location, turn) in enumerate(REFERENCES):
        over_view()
        # Front view for the first sheet, Left view (Ctrl+Numpad 3) for the second: the empty faces the view.
        d.key('NUMPAD_1' if index == 0 else 'NUMPAD_3', ctrl=index == 1)
        yield 0.8
        yield from add_reference(file_name, 'l36_ref{}'.format(index))
        empty = bpy.context.active_object
        d.log('EMPTY {} location {} rotation {} size {}'.format(empty.name, tuple(empty.location), tuple(round(v, 3) for v in empty.rotation_euler), empty.empty_display_size))
        d.shot('l36_ref{}_added'.format(index))
        # Object properties: Location Y, X, Z as numbers.
        yield from d.press(1595, top(486))
        yield 0.6
        for row, value in ((361, location[0]), (380, location[1]), (400, location[2])):
            yield from field(1797, row, value)
        d.shot('l36_ref{}_located'.format(index))
        # The Data tab: Size 2 m, drawn behind everything, shown only when looked at straight on, half see-through.
        yield from d.press(1595, top(598))
        yield 0.8
        yield from field(1807, 350, 2)
        yield from d.press(1856, top(420))
        yield 0.4
        yield from d.press(1739, top(507))
        yield 0.4
        yield from d.press(1739, top(532))
        yield 0.4
        yield from field(1817, 532, 0.6)
        over_view()
        d.shot('l36_ref{}_data'.format(index))
        yield from d.press(1595, top(486))
        yield 0.4
        d.log('REF {} depth {} size {} opacity {} axis only {}'.format(file_name, empty.empty_image_depth, empty.empty_display_size, empty.color[3], empty.show_empty_image_only_axis_aligned))
        over_view()
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text('reference_' + ('front' if index == 0 else 'side'))
        d.key('RET')
        yield 0.5
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    d.key('HOME')
    yield 0.8
    for _ in range(5):
        d.key('NUMPAD_PLUS')
        yield 0.25
    yield 0.5
    d.shot('l36_references')
    if STOP == 'references':
        return

    # A collection for the character, so the references stay out of what is exported: the New Collection button in the
    # Outliner's header makes it beside Collection; a click makes it the active collection, and F2 renames it.
    yield from d.press(1899, top(38))
    yield 0.8
    d.shot('l36_new_collection')
    yield from d.press(1700, top(144))
    yield 0.5
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('character')
    d.key('RET')
    yield 0.6
    d.log('COLLECTIONS {} active {}'.format([c.name for c in bpy.data.collections], bpy.context.view_layer.active_layer_collection.name))
    d.shot('l36_collection')
    over_view()

    # The parts: Add > Mesh by search, renamed, scaled to the half sizes (a cube is 2 m wide, a sphere has radius 1 m),
    # the scale applied, and moved and turned to its place on the sheet.
    def part(name, shape, size, location, turn):
        over_view()
        d.key('A', shift=True)
        yield 0.8
        d.type_text(shape)
        yield 0.9
        d.key('RET')
        yield 0.8
        d.key('F2')
        yield 0.5
        d.key('A', ctrl=True)
        d.type_text(name)
        d.key('RET')
        yield 0.5
        over_view()
        d.key('S')
        typed(*size)
        d.key('RET')
        yield 0.4
        d.key('A', ctrl=True)
        yield 0.6
        d.key('S')
        yield 0.5
        d.key('G')
        typed(*location)
        d.key('RET')
        yield 0.4
        if turn:
            d.key('R')
            d.key('Y')
            d.type_text(str(turn))
            d.key('RET')
            yield 0.4
        obj = bpy.data.objects[name]
        d.log('PART {} location {} rotation {} dimensions {}'.format(name, tuple(round(v, 3) for v in obj.location), tuple(round(v, 1) for v in (a * 57.29578 for a in obj.rotation_euler)), tuple(round(v, 3) for v in obj.dimensions)))

    for number, (name, shape, size, location, turn) in enumerate(PARTS):
        yield from part(name, shape, size, location, turn)
        if name in ('head', 'torso', 'arm.L'):
            d.shot('l36_part_' + name.replace('.', '_'))
    # Click the skirt to select it, frame it with Numpad Period, and step back until the whole figure fits.
    over_view()
    d.key('NUMPAD_1')
    yield 0.6
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    region = d.region(viewport)
    local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, bpy.data.objects['skirt'].location)
    d.click(region.x + int(local.x), region.y + int(local.y))
    yield 0.5
    d.key('NUMPAD_PERIOD')
    yield 1.0
    for _ in range(10):
        d.key('NUMPAD_MINUS')
        yield 0.25
    yield 0.5
    d.log('SELECTED {}'.format([o.name for o in bpy.context.selected_objects]))
    d.shot('l36_front')

    # Check against the sheets: X-ray shows the reference through the parts, front and left.
    d.key('Z', alt=True)
    yield 0.6
    d.shot('l36_front_xray')
    d.key('NUMPAD_3', ctrl=True)
    yield 0.8
    d.shot('l36_side_xray')
    d.key('Z', alt=True)
    yield 0.4
    d.key('NUMPAD_1')
    yield 0.4
    # A three-quarter view.
    for name in ('NUMPAD_8', 'NUMPAD_8', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_5'):
        d.key(name)
        yield 0.3
    yield 0.4
    d.shot('l36_three_quarter')
    bounds = [bpy.data.objects[name] for name, *_ in PARTS]
    corners = [obj.matrix_world @ __import__('mathutils').Vector(corner) for obj in bounds for corner in obj.bound_box]
    low = [round(min(c[i] for c in corners), 3) for i in range(3)]
    high = [round(max(c[i] for c in corners), 3) for i in range(3)]
    d.log('BOUNDS min {} max {} height {} widths {}'.format(low, high, round(high[2] - low[2], 3), [round(high[i] - low[i], 3) for i in range(3)]))
    # Export: the collection's own glTF exporter, as in lesson 24, into art/character.
    EXPORT = os.path.join(WORKBENCH, 'art', 'character')
    yield from d.press(1595, top(449))
    yield 0.8
    d.shot('l36_collection_tab')
    yield from d.press(1892, top(616))
    yield 0.4
    d.shot('l36_add_exporter')
    yield from d.press(1748, top(760))
    yield 0.8
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l36_exporter_panel')
    collection = bpy.data.collections['character']
    d.log('EXPORTERS {}'.format([exporter.name for exporter in collection.exporters]))
    if STOP == 'exporter':
        return
    yield from d.press(1892, top(763))
    yield 1.5
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(EXPORT + os.sep, target=browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l36_export_folder', browser)
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('EXPORT folder exists {}'.format(os.path.isdir(EXPORT)))
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('character_blockout.glb', target=browser)
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l36_export_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    d.log('FILEPATH {}'.format(collection.exporters[0].export_properties.filepath))
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l36_exporter_settings')
    yield from d.press(1771, top(708))
    yield 2
    glb = os.path.join(EXPORT, 'character_blockout.glb')
    d.log('GLB exists {} size {}'.format(os.path.isfile(glb), os.path.getsize(glb) if os.path.isfile(glb) else 0))
    d.shot('l36_exported')
    over_view()
    d.key('S', ctrl=True)
    yield 1.5
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
