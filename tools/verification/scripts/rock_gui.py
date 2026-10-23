# Runs lesson 9 in Blender's real UI on a timer, screenshotting each state, then saves the .blend and quits.
import math
import os
import bpy
import bmesh

OUT = os.path.join(os.environ['TEMP'], 'sgt-phase1', 'shots', 'blender')
BLEND = os.environ['ROCK_BLEND']
# Factory settings show the splash screen, which would cover the viewport in every screenshot.
bpy.context.preferences.view.show_splash = False


def areas(kind):
    window = bpy.context.window_manager.windows[0]
    return window, [area for area in window.screen.areas if area.type == kind]


def shot(name):
    window, _ = areas('VIEW_3D')
    with bpy.context.temp_override(window=window, screen=window.screen):
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT, name + '.png'), check_existing=False)
    print('SHOT', name)


def view(rotation_x, rotation_z, distance, stats=True):
    window, views = areas('VIEW_3D')
    space = views[0].spaces.active
    space.overlay.show_stats = stats
    region = space.region_3d
    region.view_perspective = 'PERSP'
    region.view_location = (0, 0, 0.18)
    euler = __import__('mathutils').Euler((math.radians(rotation_x), 0, math.radians(rotation_z)))
    region.view_rotation = euler.to_quaternion()
    region.view_distance = distance


def properties_tab(tab):
    _, panels = areas('PROPERTIES')
    for area in panels:
        area.spaces.active.context = tab


def edit(mode):
    bpy.ops.object.mode_set(mode=mode)


def steps():
    cube = bpy.data.objects['Cube']
    bpy.ops.object.select_all(action='DESELECT')
    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube
    view(65, 35, 9.0, stats=True)
    yield 1.0
    shot('l09_start')

    cube.name = 'rock_small'
    cube.data.name = 'rock_small'
    cube.scale = (0.3, 0.25, 0.175)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    view(65, 35, 3.2)
    properties_tab('OBJECT')
    yield 0.5
    shot('l09_scaled')

    edit('EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=1)
    mesh = bmesh.from_edit_mesh(cube.data)
    for vertex in mesh.verts:
        if vertex.co.z > 0.1:
            vertex.co.x *= 0.75
            vertex.co.y *= 0.8
            vertex.co.z += 0.03 * (1 if vertex.co.x > 0 else -1)
        if vertex.co.z < -0.1:
            vertex.co.x *= 1.05
    bmesh.update_edit_mesh(cube.data)
    yield 0.5
    shot('l09_blocked')

    bpy.ops.transform.vertex_random(offset=0.03, seed=4)
    mesh = bmesh.from_edit_mesh(cube.data)
    lowest = min(vertex.co.z for vertex in mesh.verts)
    for vertex in mesh.verts:
        vertex.co.z -= lowest
    bmesh.update_edit_mesh(cube.data)
    yield 0.5
    shot('l09_randomized')

    edit('OBJECT')
    bpy.ops.object.shade_smooth()
    yield 0.5
    shot('l09_smooth_only')

    bevel = cube.modifiers.new('Bevel', 'BEVEL')
    bevel.width = 0.04
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    properties_tab('MODIFIER')
    yield 0.5
    shot('l09_bevel')

    weighted = cube.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
    weighted.keep_sharp = True
    yield 0.5
    shot('l09_weighted')

    view(0, 0, 2.4)
    window, views = areas('VIEW_3D')
    views[0].spaces.active.region_3d.view_perspective = 'ORTHO'
    views[0].spaces.active.region_3d.view_rotation = __import__('mathutils').Euler((math.radians(90), 0, 0)).to_quaternion()
    yield 0.5
    shot('l09_front_origin')

    view(55, 30, 2.4)
    yield 0.5
    shot('l09_final')

    os.makedirs(os.path.dirname(BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    evaluated = cube.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated.data.calc_loop_triangles()
    print('DONE tris', len(evaluated.data.loop_triangles), 'modifiers', [m.type for m in cube.modifiers])
    yield None


queue = steps()


def tick():
    try:
        delay = next(queue)
    except StopIteration:
        delay = None
    if delay is None:
        bpy.ops.wm.quit_blender()
        return None
    return delay


bpy.app.timers.register(tick, first_interval=3.0)
