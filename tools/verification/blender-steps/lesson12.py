# Lesson 12: a large rock made from the small one's file: Save As, resize, a silhouette check from above, a reshaped
# outline, the second stone ramp by moving every UV half the image across, and an export beside the small rock's.
import math
import os

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d

WORKBENCH = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench')
FOLDER = os.path.join(WORKBENCH, 'art_source', 'nature', 'rock_large')
EXPORT = os.path.join(WORKBENCH, 'art', 'nature', 'rock_large')


def top(y, height=1080):
    return height - y


def screen_point(d, viewport, obj, point):
    region = d.region(viewport)
    local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, obj.matrix_world @ point)
    return region.x + int(local.x), region.y + int(local.y)


def type_into(d, x, y, value, target=None):
    # Click a field, select its text, type, and confirm.
    yield from d.press(x, y, target=target)
    yield 0.2
    d.key('A', ctrl=True, target=target)
    d.type_text(value, target=target)
    yield 0.2
    d.key('RET', target=target)
    yield 0.4


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    rock = bpy.data.objects['rock_small']
    viewport = d.area('VIEW_3D')
    d.shot('l12_start')

    # File > Save As into a new rock_large folder.
    d.move(*d.center(viewport))
    d.key('S', ctrl=True, shift=True)
    yield 2
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(FOLDER + os.sep, target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 1
    yield from d.press(516, top(54, d.pixels(browser.height)), target=browser)
    yield 1
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('rock_large.blend', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    d.log('SAVED AS {}'.format(bpy.data.filepath))

    # Names: the object with F2, the mesh on the Data tab, the collection with F2 over the Outliner.
    d.wake()
    yield 0.3
    d.move(*d.center(viewport))
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('rock_large')
    yield 0.2
    d.key('RET')
    yield 0.5
    yield from d.press(1595, top(626))
    yield 0.5
    yield from type_into(d, 1760, top(297), 'rock_large')
    d.move(1670, top(84))
    yield from d.press(1670, top(84))
    yield 0.3
    d.key('F2')
    yield 0.4
    d.key('A', ctrl=True)
    d.type_text('rock_large')
    yield 0.2
    d.key('RET')
    yield 0.5
    d.log('NAMES object {} mesh {} collections {}'.format(rock.name, rock.data.name, [c.name for c in bpy.data.collections]))
    d.shot('l12_renamed')

    # Clicking the collection deselected the rock; click it again.
    from mathutils import Vector
    d.click(*screen_point(d, viewport, rock, Vector((0, 0, 0.15))))
    yield 0.4
    d.log('SELECTED {}'.format([o.name for o in bpy.context.selected_objects]))

    # Size: about 1.6 by 1.3 by 0.9 meters, applied.
    d.move(*d.center(viewport))
    d.key('N')
    yield 0.8
    for row, value in ((406, '1.6'), (426, '1.3'), (446, '0.9')):
        yield from type_into(d, 1425, top(row), value)
    d.log('DIMENSIONS {} scale {}'.format(tuple(round(v, 3) for v in rock.dimensions), tuple(round(v, 3) for v in rock.scale)))
    d.shot('l12_dimensions')
    d.move(*d.center(viewport))
    d.key('A', ctrl=True)
    yield 0.3
    d.shot('l12_apply_menu')
    d.log('POINTER {}'.format(d.pointer))
    yield from d.press(666, top(539))
    yield 0.5
    d.move(*d.center(viewport))
    d.key('N')
    yield 0.3
    d.key('NUMPAD_PERIOD')
    yield 0.6
    d.log('APPLIED scale {} dimensions {}'.format(tuple(round(v, 3) for v in rock.scale), tuple(round(v, 3) for v in rock.dimensions)))

    # A bevel to suit the bigger rock.
    yield from d.press(1595, top(514))
    yield 0.6
    d.move(1760, top(1000))
    yield 0.3
    d.shot('l12_modifiers')
    yield from type_into(d, 1816, top(411), '0.08')
    d.log('BEVEL width {}'.format(round(rock.modifiers['Bevel'].width, 3)))
    d.move(1760, top(1000))
    yield 0.3
    d.shot('l12_bevel')

    # The silhouette check: flat lighting, one color, from the top.
    yield from d.press(1557, top(38))
    yield 0.5
    d.shot('l12_shading_popover')
    yield from d.press(1634, top(133))
    yield 0.3
    # Flat hides the lighting preview, so the Color rows move up.
    yield from d.press(1635, top(306))
    yield 0.3
    d.shot('l12_shading_flat')
    d.key('ESC')
    yield 0.3
    shading = viewport.spaces.active.shading
    d.log('SHADING light {} color {} single {}'.format(shading.light, shading.color_type, tuple(round(c, 2) for c in shading.single_color)))
    d.move(*d.center(viewport))
    d.key('NUMPAD_7')
    yield 0.6
    d.key('NUMPAD_PERIOD')
    yield 0.6
    d.shot('l12_silhouette_before')

    # Reshape the outline from above: X-ray on, box each corner's stack of vertices, push it with G.
    d.key('TAB')
    yield 0.5
    d.key('ONE')
    d.key('Z', alt=True)
    yield 0.4
    mesh = bmesh.from_edit_mesh(rock.data)
    lowest = min(v.co.z for v in mesh.verts)
    highest = max(v.co.z for v in mesh.verts)
    # The outline from above is the base and middle rings; their corners and side middles sit almost on top of each other.
    def column(sx, sy):
        picked = [v.co.copy() for v in mesh.verts if v.co.z < highest - 0.05 and (v.co.x * sx > 0.3 if sx else abs(v.co.x) < 0.15) and (v.co.y * sy > 0.25 if sy else abs(v.co.y) < 0.15)]
        return picked
    moves = [((1, 1), (60, 30)), ((-1, -1), (-40, -35)), ((0, -1), (10, -60)), ((-1, 1), (30, -30))]
    for (sx, sy), offset in moves:
        points = [screen_point(d, viewport, rock, co) for co in column(sx, sy)]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        d.move(min(xs) - 10, max(ys) + 10)
        d.key('A', alt=True)
        yield 0.2
        d.key('B')
        yield 0.3
        yield from d.drag((min(xs) - 10, max(ys) + 10), (max(xs) + 10, min(ys) - 10))
        yield 0.3
        mesh = bmesh.from_edit_mesh(rock.data)
        selected = sum(1 for v in mesh.verts if v.select)
        x, y = (sum(xs) // len(xs), sum(ys) // len(ys))
        d.move(x, y)
        d.key('G')
        yield 0.2
        d.move(x + offset[0], y + offset[1])
        yield 0.2
        d.click(x + offset[0], y + offset[1])
        yield 0.4
        d.log('COLUMN {} selected {} of {}'.format((sx, sy), selected, len(points)))
    d.shot('l12_reshaped')
    d.key('Z', alt=True)
    yield 0.3

    # A fresh Randomize for this rock, then rest it on the ground again.
    d.move(*d.center(viewport))
    d.key('A')
    yield 0.3
    yield from d.press(356, top(38))
    yield 0.4
    d.move(393, top(60))
    yield 0.6
    d.move(545, top(60))
    yield 0.3
    yield from d.press(575, top(332))
    yield 0.8
    for row, value in ((899, '0.04'), (965, '7')):
        yield from type_into(d, 255, top(row), value)
    mesh = bmesh.from_edit_mesh(rock.data)
    lowest = min(v.co.z for v in mesh.verts)
    d.move(*d.center(viewport))
    d.key('G')
    d.key('Z')
    d.type_text('{:.3f}'.format(-lowest))
    d.key('RET')
    yield 0.5
    d.key('TAB')
    yield 0.5
    d.shot('l12_silhouette_after')
    # Back to normal shading: Studio lighting and Texture color.
    yield from d.press(1557, top(38))
    yield 0.5
    yield from d.press(1475, top(133))
    yield 0.4
    yield from d.press(1555, top(403))
    yield 0.3
    d.key('ESC')
    yield 0.3
    d.log('SHADING back {} {}'.format(viewport.spaces.active.shading.light, viewport.spaces.active.shading.color_type))
    evaluated = rock.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated.data.calc_loop_triangles()
    d.log('ROCK tris {} dimensions {}'.format(len(evaluated.data.loop_triangles), tuple(round(v, 3) for v in rock.dimensions)))

    # The second stone ramp: every UV moves half the image to the right, four swatches across.
    yield from d.press(495, top(13))
    yield 1.5
    editor = d.area('IMAGE_EDITOR')
    viewport_uv = d.area('VIEW_3D')
    d.move(*d.center(viewport_uv))
    d.key('THREE')
    d.key('A')
    yield 0.3
    d.move(editor.x + editor.width // 3, editor.y + editor.height // 2)
    yield 0.2
    d.key('A')
    yield 0.2
    d.key('G')
    d.key('X')
    d.type_text('0.5')
    d.key('RET')
    yield 0.5
    d.shot('l12_uv_moved')
    mesh = bmesh.from_edit_mesh(rock.data)
    layer = mesh.loops.layers.uv.active
    corners = sorted({(round(loop[layer].uv.x, 4), round(loop[layer].uv.y, 4)) for face in mesh.faces for loop in face.loops if face.normal.z > 0.7 or face.normal.z < -0.7 or abs(face.normal.z) < 0.3})
    d.log('UV points {}'.format(corners))
    yield from d.press(288, top(13))
    yield 1.5
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    if bpy.context.mode != 'OBJECT':
        d.key('TAB')
        yield 0.5
    for name in ('NUMPAD_1', 'NUMPAD_8', 'NUMPAD_8', 'NUMPAD_8', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_PERIOD'):
        d.key(name)
        yield 0.3
    yield 0.4
    d.shot('l12_colored')

    # The exporter: same settings, a new file in art/nature/rock_large.
    yield from d.press(1595, top(449))
    yield 0.6
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l12_collection_tab')
    collection = rock.users_collection[0]
    exporter = collection.exporters[0]
    d.log('PATH before {}'.format(exporter.export_properties.filepath))
    yield from d.press(1892, top(763))
    yield 1.5
    browser = d.browser()
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text(EXPORT + os.sep, target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 1
    yield from d.press(516, top(57, d.pixels(browser.height)), target=browser)
    yield 1
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    yield from d.press(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.3
    d.key('A', ctrl=True, target=browser)
    d.type_text('rock_large.glb', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 1.5
    d.log('PATH after {}'.format(exporter.export_properties.filepath))
    d.move(1760, top(1060))
    yield 0.3
    d.shot('l12_exporter_path')
    yield from d.press(1892, top(733))
    yield 2
    glb = os.path.join(EXPORT, 'rock_large.glb')
    small = os.path.join(WORKBENCH, 'art', 'nature', 'rock_small', 'rock_small.glb')
    d.log('GLB exists {} size {} small size {}'.format(os.path.isfile(glb), os.path.getsize(glb) if os.path.isfile(glb) else 0, os.path.getsize(small)))
    d.move(*d.center(d.area('VIEW_3D')))
    d.key('S', ctrl=True)
    yield 1
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
    d.shot('l12_exported')
