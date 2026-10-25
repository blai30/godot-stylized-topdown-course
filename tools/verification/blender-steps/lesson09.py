# Lesson 9: models the small rock the reader's way, with the hotkeys and menus the lesson names, from the startup
# file lesson 8 saved. Blender starting up opens that file, the same scene File > New > General gives.
import math
import os

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d

HEIGHT = 1080
FOLDER = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'workbench', 'art_source', 'nature', 'rock_small')


def top(y, height=HEIGHT):
    # Converts a screenshot's y (from the top) to Blender's window y (from the bottom).
    return height - y


def screen_point(d, point):
    # Window coordinates of a point given in the rock's local space.
    viewport = d.area('VIEW_3D')
    region = d.region(viewport)
    obj = bpy.context.active_object
    local = location_3d_to_region_2d(region, viewport.spaces.active.region_3d, obj.matrix_world @ point)
    return region.x + int(local.x), region.y + int(local.y)


def steps(d):
    yield 2
    d.key('ESC')
    yield 0.5
    d.shot('l09_start')
    viewport = d.area('VIEW_3D')

    # Rename with F2 over the 3D view: type, Enter.
    d.move(*d.center(viewport))
    d.key('F2')
    yield 0.5
    d.key('A', ctrl=True)
    d.type_text('rock_small')
    yield 0.3
    d.shot('l09_rename_field')
    d.key('RET')
    yield 0.5
    d.log('NAME {}'.format(bpy.context.active_object.name))

    # File > Save As into the project's art_source/nature/rock_small folder.
    d.move(*d.center(viewport))
    d.key('S', ctrl=True, shift=True)
    yield 2
    browser = d.browser()
    d.shot('l09_save_as', browser)
    yield from d.press(545, top(19, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.key('A', ctrl=True, target=browser)
    d.type_text(FOLDER + os.sep, target=browser)
    yield 0.3
    d.shot('l09_path_typed', browser)
    d.key('RET', target=browser)
    yield 1
    d.shot('l09_create_folder', browser)
    d.click(516, top(54, d.pixels(browser.height)), target=browser)
    yield 1
    d.log('FOLDER exists {} browser dir {}'.format(os.path.isdir(FOLDER), browser.screen.areas[0].spaces.active.params.directory))
    d.click(455, top(578, d.pixels(browser.height)), target=browser)
    yield 0.5
    d.key('A', ctrl=True, target=browser)
    d.type_text('rock_small.blend', target=browser)
    yield 0.3
    d.key('RET', target=browser)
    yield 0.3
    d.shot('l09_file_name', browser)
    yield from d.press(d.save_button_x(browser), 21, target=browser)
    yield 0.5
    d.shot('l09_after_save_click', browser) if len(bpy.context.window_manager.windows) > 1 else None
    yield 2
    d.log('BROWSER size {}x{}'.format(browser.width, browser.height))
    d.log('WINDOWS after save {} file {}'.format(len(bpy.context.window_manager.windows), bpy.data.filepath))

    # Size: the Sidebar's Dimensions, then apply the scale.
    d.wake()
    yield 0.3
    rock = bpy.context.active_object
    d.move(*d.center(viewport))
    d.key('N')
    yield 0.8
    for row, value in ((406, '0.6'), (426, '0.5'), (446, '0.35')):
        yield from d.press(1425, top(row))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(value)
        yield 0.2
        d.key('RET')
        yield 0.4
    d.log('DIMENSIONS {} scale {}'.format(tuple(round(v, 3) for v in rock.dimensions), tuple(round(v, 3) for v in rock.scale)))
    d.shot('l09_dimensions')
    d.move(*d.center(viewport))
    d.key('A', ctrl=True)
    # Capture before the hovered item's tooltip appears.
    yield 0.3
    d.shot('l09_apply_menu')
    yield from d.press(666, top(539))
    yield 0.5
    d.log('APPLIED scale {} dimensions {}'.format(tuple(round(v, 3) for v in rock.scale), tuple(round(v, 3) for v in rock.dimensions)))
    d.move(*d.center(viewport))
    d.key('N')
    yield 0.3
    d.key('NUMPAD_PERIOD')
    yield 0.8
    d.key('TAB')
    yield 0.5
    d.log('MODE {}'.format(bpy.context.mode))

    # Three loop cuts: hover an edge, Ctrl+R, click, right-click. Each cut runs across the hovered edge.
    def nearest_edge(axis):
        mesh = bmesh.from_edit_mesh(rock.data)
        eye = viewport.spaces.active.region_3d.view_matrix.inverted().translation
        best = None
        for edge in mesh.edges:
            direction = (edge.verts[1].co - edge.verts[0].co).normalized()
            if abs(direction[axis]) < 0.99:
                continue
            middle = (edge.verts[0].co + edge.verts[1].co) / 2
            distance = (rock.matrix_world @ middle - eye).length
            if best is None or distance < best[0]:
                best = (distance, edge.verts[0].co.copy(), edge.verts[1].co.copy())
        return best[1].lerp(best[2], 0.35)

    for number, axis in enumerate((2, 0, 1)):
        point = d.screen_point(nearest_edge(axis)) if hasattr(d, 'screen_point') else screen_point(d, nearest_edge(axis))
        d.move(*point)
        yield 0.3
        d.key('R', ctrl=True)
        yield 0.5
        if number == 0:
            d.shot('l09_loopcut_preview')
        d.click(*point)
        yield 0.3
        d.click(*point, button='RIGHTMOUSE')
        yield 0.5
        d.log('CUT {} vertices {}'.format(number, len(rock.data.vertices) if bpy.context.mode != 'EDIT_MESH' else len(bmesh.from_edit_mesh(rock.data).verts)))
    d.shot('l09_cuts')

    # A narrower top: vertex select, front view, X-ray, box select the top row, scale 0.75.
    d.move(*d.center(viewport))
    d.key('ONE')
    d.key('NUMPAD_1')
    yield 0.5
    d.key('Z', alt=True)
    yield 0.5
    mesh = bmesh.from_edit_mesh(rock.data)
    highest = max(vertex.co.z for vertex in mesh.verts)
    row = [screen_point(d, vertex.co) for vertex in mesh.verts if vertex.co.z > highest - 0.01]
    xs = [point[0] for point in row]
    y = row[0][1]
    start, end = (min(xs) - 40, y + 25), (max(xs) + 40, y - 25)
    d.log('BOX from {} to {} region {}'.format(start, end, (d.region(viewport).x, d.region(viewport).y, d.region(viewport).width, d.region(viewport).height)))
    # Alt+A selects nothing; B starts a box select that adds to the selection; then press, drag, and release.
    d.move(*start)
    yield 0.2
    d.key('A', alt=True)
    yield 0.2
    d.key('B')
    yield 0.3
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=start[0], y=start[1])
    yield 0.1
    for index in range(1, 11):
        d.move(start[0] + (end[0] - start[0]) * index // 10, start[1] + (end[1] - start[1]) * index // 10)
        yield 0.05
    d.shot('l09_box_drag')
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=end[0], y=end[1])
    yield 0.3
    yield 0.3
    mesh = bmesh.from_edit_mesh(rock.data)
    d.log('TOP ROW selected {} of {}'.format(sum(1 for vertex in mesh.verts if vertex.select), len(row)))
    d.move(*d.center(viewport))
    d.key('S')
    d.type_text('0.75')
    d.key('RET')
    yield 0.5
    d.shot('l09_blocked')

    # Break the outline from above: top view, X-ray still on. Each corner of the outline is a base vertex with a
    # middle-ring vertex right above it; box both with B and push them with G.
    d.key('NUMPAD_7')
    yield 0.5
    mesh = bmesh.from_edit_mesh(rock.data)
    highest = max(vertex.co.z for vertex in mesh.verts)
    def column(sx, sy):
        return [v.co.copy() for v in mesh.verts if v.co.z < highest - 0.05 and (v.co.x * sx > 0.2 if sx else abs(v.co.x) < 0.05) and (v.co.y * sy > 0.15 if sy else abs(v.co.y) < 0.05)]
    moves = [((1, 1), (55, 25)), ((-1, -1), (-35, -30)), ((0, -1), (10, -50)), ((-1, 1), (30, -25))]
    for (sx, sy), offset in moves:
        mesh = bmesh.from_edit_mesh(rock.data)
        points = [screen_point(d, co) for co in column(sx, sy)]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        d.move(min(xs) - 10, max(ys) + 10)
        d.key('A', alt=True)
        yield 0.2
        d.key('B')
        yield 0.3
        yield from d.drag((min(xs) - 10, max(ys) + 10), (max(xs) + 10, min(ys) - 10))
        yield 0.3
        mesh = bmesh.from_edit_mesh(rock.data)
        selected = sum(1 for v in mesh.verts if v.select)
        x, y = sum(xs) // len(xs), sum(ys) // len(ys)
        d.move(x, y)
        d.key('G')
        yield 0.2
        d.move(x + offset[0], y + offset[1])
        yield 0.2
        d.click(x + offset[0], y + offset[1])
        yield 0.4
        d.log('COLUMN {} selected {} of {}'.format((sx, sy), selected, len(points)))
    d.key('Z', alt=True)
    yield 0.3
    d.shot('l09_corners')
    d.key('A')
    yield 0.3
    yield from d.press(356, top(38))
    yield 0.5
    d.shot('l09_mesh_menu')
    d.move(393, top(60))
    yield 0.8
    d.shot('l09_transform_menu')
    d.move(545, top(60))
    yield 0.3
    yield from d.press(575, top(332))
    yield 0.8
    d.shot('l09_randomize_collapsed')
    yield from d.press(73, top(969))
    yield 0.8
    d.shot('l09_randomize_panel')
    for row, value in ((899, '0.03'), (965, '4')):
        yield from d.press(255, top(row))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(value)
        yield 0.2
        d.key('RET')
        yield 0.5
    d.shot('l09_randomized')
    mesh = bmesh.from_edit_mesh(rock.data)
    lowest = min(vertex.co.z for vertex in mesh.verts)
    d.log('RANDOMIZED lowest {:.4f}'.format(lowest))

    # Rest it on the ground: front view, G, Z, and the distance up.
    d.move(*d.center(viewport))
    d.key('NUMPAD_1')
    yield 0.6
    d.key('G')
    d.key('Z')
    d.type_text('{:.3f}'.format(-lowest))
    d.key('RET')
    yield 0.5
    mesh = bmesh.from_edit_mesh(rock.data)
    d.log('GROUNDED lowest {:.4f}'.format(min(vertex.co.z for vertex in mesh.verts)))
    d.shot('l09_grounded')
    d.key('TAB')
    yield 0.5
    d.key('NUMPAD_1') if False else None
    yield from d.press(312, top(38))
    yield 0.6
    d.shot('l09_object_menu')
    yield from d.press(355, top(492))
    yield 0.6
    d.log('SMOOTH {}'.format(all(polygon.use_smooth for polygon in rock.data.polygons)))
    d.move(*d.center(viewport))
    d.key('NUMPAD_PERIOD')
    yield 0.6
    d.shot('l09_smooth_only')
    yield from d.press(1595, top(514))
    yield 0.6
    d.log('PROPERTIES tab {}'.format(d.area('PROPERTIES').spaces.active.context))
    d.shot('l09_modifiers_tab')
    yield from d.press(1784, top(304))
    yield 0.8
    d.shot('l09_add_modifier_menu')
    d.move(1693, top(348))
    yield 0.8
    d.shot('l09_generate_menu')
    d.move(1520, top(348))
    yield 0.2
    yield from d.press(1508, top(387))
    yield 0.8
    d.log('MODIFIERS {}'.format([(m.name, m.type) for m in rock.modifiers]))
    d.shot('l09_bevel_added')
    for row, value in ((411, '0.04'), (436, '2')):
        yield from d.press(1816, top(row))
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(value)
        yield 0.2
        d.key('RET')
        yield 0.5
    bevel = rock.modifiers['Bevel']
    d.log('BEVEL width {} segments {} limit {} angle {:.1f}'.format(round(bevel.width, 4), bevel.segments, bevel.limit_method, math.degrees(bevel.angle_limit)))
    d.shot('l09_bevel')
    yield from d.press(1784, top(304))
    yield 0.6
    # Blender reopens the menu with the last item used, Generate, under the pointer, and opens its submenu; Normals
    # is two rows below it. Move there the way a hand does, a little at a time.
    for y in range(304, 344, 5):
        d.move(1711, top(y))
        yield 0.08
    yield 0.8
    d.shot('l09_normals_menu')
    for x in range(1711, 1538, -25):
        d.move(x, top(343))
        yield 0.05
    yield from d.press(1539, top(362))
    yield 0.8
    d.log('MODIFIERS {}'.format([(m.name, m.type) for m in rock.modifiers]))
    d.shot('l09_weighted_added')
    yield from d.press(1755, top(700))
    yield 0.5
    weighted = rock.modifiers['WeightedNormal']
    d.move(*d.center(viewport))
    yield 0.5
    d.log('WEIGHTED keep_sharp {} mode {} weight {}'.format(weighted.keep_sharp, weighted.mode, weighted.weight))
    d.shot('l09_weighted')
    evaluated = rock.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated.data.calc_loop_triangles()
    d.log('TRIS {} dimensions {} origin {}'.format(len(evaluated.data.loop_triangles), tuple(round(v, 3) for v in rock.dimensions), tuple(rock.location)))

    # Check from the front, then a three-quarter view, then save.
    d.move(*d.center(viewport))
    d.key('NUMPAD_1')
    yield 0.6
    d.key('NUMPAD_PERIOD')
    yield 0.6
    d.shot('l09_front_origin')
    x, y = d.center(viewport)
    for name in ('NUMPAD_8', 'NUMPAD_8', 'NUMPAD_8', 'NUMPAD_4', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_MINUS', 'NUMPAD_MINUS', 'NUMPAD_MINUS'):
        d.key(name)
        yield 0.3
    yield 0.5
    d.shot('l09_final')
    d.key('S', ctrl=True)
    yield 1
    d.log('SAVED {} dirty {}'.format(bpy.data.filepath, bpy.data.is_dirty))
