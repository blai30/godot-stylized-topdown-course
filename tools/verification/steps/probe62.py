# Probe: can a navigation mesh be baked from the meadow's colliders (ground plane, trunks, rocks, bank boxes), and does a path go round the pond?
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

steps = [
    {'op': 'sleep', 'seconds': 5},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    eval_('''
var root := editor.get_edited_scene_root()
for name in ["Ground", "GroundTiles", "Bank", "Rocks", "Trees", "Bushes"]:
	root.get_node(name).add_to_group("navigation_geometry", true)
var region := NavigationRegion3D.new()
region.name = "Navigation"
root.add_child(region)
region.owner = root
for variant in [[0.25, 0.25], [0.1, 0.1], [0.25, 0.05]]:
	var mesh := NavigationMesh.new()
	mesh.cell_size = variant[0]
	mesh.cell_height = variant[1]
	mesh.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	mesh.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN
	mesh.geometry_source_group_name = "navigation_geometry"
	region.navigation_mesh = mesh
	region.bake_navigation_mesh(false)
	await plugin.get_tree().create_timer(4.0).timeout
	var map := region.get_navigation_map()
	NavigationServer3D.map_force_update(map)
	var verts := mesh.get_vertices()
	var ys := {}
	for v in verts:
		ys[snappedf(v.y, 0.01)] = true
	print("[probe] cell ", variant, " polygons ", mesh.get_polygon_count(), " vertex heights ", ys.keys())
var shapes := []
for name in ["Ground", "GroundTiles", "Bank"]:
	shapes.append(name)
print("[probe] done")
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
