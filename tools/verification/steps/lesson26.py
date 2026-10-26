# Lesson 26: the oak's glb now holds the leaf cards beside the trunk. Reads the imported mesh back (cards, vertex
# colors, normals, UVs) and shows the tree scene.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, view, click_tab, click_file

GLB = 'res://art/nature/tree_oak/tree_oak.glb'
steps = [
    {'op': 'sleep', 'seconds': 8},
    {'op': 'fs', 'path': GLB},
    eval_(f'''
var scene: PackedScene = load("{GLB}")
var root := scene.instantiate()
var out := []
for node in root.find_children("*", "", true, false):
	if node is MeshInstance3D:
		var mesh: Mesh = node.mesh
		var arrays := mesh.surface_get_arrays(0)
		var colors = arrays[Mesh.ARRAY_COLOR]
		var sample = ""
		if colors != null and colors.size() > 0:
			sample = str(colors[0]) + " " + str(colors[colors.size() - 1])
		var material: Material = mesh.surface_get_material(0)
		out.append("%s: vertices %d triangles %d color %s normals %s uv %s aabb %s material %s" % [node.name, arrays[Mesh.ARRAY_VERTEX].size(), arrays[Mesh.ARRAY_INDEX].size() / 3, colors != null, arrays[Mesh.ARRAY_NORMAL] != null, arrays[Mesh.ARRAY_TEX_UV] != null, str(mesh.get_aabb()), str(material.resource_name) + " vertex_color_albedo " + str(material.vertex_color_use_as_albedo if material is BaseMaterial3D else "n/a")])
		out.append("  first and last color " + sample)
print("[probe] cards mesh\\n", "\\n".join(out))
root.free()
'''),
    {'op': 'open', 'path': 'res://art/nature/tree_oak/tree_oak.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    click_tab('Scene'),
    *view('tree_oak', 'leaves', dx=0, dy=0, wheel=0),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l26_tree_scene'},
    {'op': 'wait', 'frames': 20},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
