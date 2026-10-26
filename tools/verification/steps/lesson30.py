# Lesson 30, in Godot: the grass .glb imports with its five meshes, its vertex colors, and no generated LODs.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, import_set, show_import_row, open_advanced, REIMPORT, DUMP_IMPORT

PROBE = eval_('''
var scene: PackedScene = load("res://art/nature/grass/grass.glb")
var root := scene.instantiate()
for node in root.get_children():
	var mesh: ArrayMesh = node.mesh
	var arrays := mesh.surface_get_arrays(0)
	var colors: PackedColorArray = arrays[Mesh.ARRAY_COLOR] if arrays[Mesh.ARRAY_COLOR] != null else PackedColorArray()
	var alpha_max := 0.0
	var red_max := 0.0
	for color in colors:
		alpha_max = maxf(alpha_max, color.a)
		red_max = maxf(red_max, color.r)
	print("[probe] mesh ", node.name, " surfaces ", mesh.get_surface_count(), " vertices ", arrays[Mesh.ARRAY_VERTEX].size(), " triangles ", arrays[Mesh.ARRAY_INDEX].size() / 3, " colors ", colors.size(), " max red ", snapped(red_max, 0.001), " max alpha ", snapped(alpha_max, 0.001), " aabb ", mesh.get_aabb())
root.free()
''')

steps = [
    {'op': 'sleep', 'seconds': 8},
    {'op': 'fs', 'path': 'res://art/nature/grass/grass.glb'},
    *click_file('grass.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 20},
    show_import_row('meshes/generate_lods'),
    DUMP_IMPORT,
    PROBE,
    {'op': 'capture', 'name': 'l30_import_before'},
    import_set('meshes/generate_lods', 'false'),
    {'op': 'wait', 'frames': 10},
    show_import_row('meshes/generate_lods'),
    {'op': 'capture', 'name': 'l30_import_lods_off'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 4},
    PROBE,
    open_advanced(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l30_advanced', 'window': 'Advanced'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		window.hide()
'''),
    {'op': 'wait', 'frames': 20},
]
write(sys.argv[2], steps)
