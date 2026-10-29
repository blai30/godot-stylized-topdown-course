# Probes for facts the pages state: the oak's mesh levels of detail and the triangles drawn at three zooms, the library's Walk
# clip, and the BlendSpace1D sync property. Run from the lesson-43 snapshot; output goes to the editor and game logs as [probe] lines.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

out_dir = os.path.dirname(sys.argv[2])
CAMERA = 'tree.root.get_node("Meadow/CameraRig").get("Camera")'

game = game_steps(os.path.join(out_dir, 'game-probe.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': 'var meadow := tree.root.get_node("Meadow")\nfor child in meadow.get_children():\n\tif child is Node3D and not ["CameraRig", "WorldEnvironment", "Trees"].has(str(child.name)):\n\t\tchild.visible = false\nfor tree_node in meadow.get_node("Trees").get_children():\n\tif tree_node.name != "TreeOak":\n\t\ttree_node.visible = false\nprint("[game] start size ", ' + CAMERA + '.size, " trees ", meadow.get_node("Trees").get_children().map(func(n): return str(n.name) + str(n.visible)))'},
    *[step for size in (8.0, 20.0, 48.0) for step in (
        {'op': 'eval', 'code': f'{CAMERA}.size = {size}\n' + 'print("[game] camera size ", ' + CAMERA + '.size)'},
        {'op': 'wait', 'frames': 60},
        {'op': 'eval', 'code': 'print("[game] primitives ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME), " objects ", RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME))'},
        {'op': 'wait', 'frames': 5})],
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    eval_('''
var packed: PackedScene = load("res://art/nature/tree_oak/tree_oak.glb")
var root := packed.instantiate()
for mesh_instance in root.find_children("*", "MeshInstance3D", true, false):
	var mesh: ArrayMesh = mesh_instance.mesh
	var surface := RenderingServer.mesh_get_surface(mesh.get_rid(), 0)
	var lods := []
	for lod in surface.get("lods", []):
		lods.append(lod["index_data"].size() / 2)
	print("[probe] mesh ", mesh_instance.name, " indices ", surface["index_count"], " lod indices ", lods)
'''),
    eval_('''
var library = load("res://art/animations/UAL1_Standard.glb")
var walk: Animation = library.get_animation("Walk")
var position_tracks := 0
for i in walk.get_track_count():
	if walk.track_get_type(i) == Animation.TYPE_POSITION_3D:
		position_tracks += 1
print("[probe] walk tracks ", walk.get_track_count(), " position tracks ", position_tracks)
for property in ClassDB.class_get_property_list("AnimationNodeBlendSpace1D"):
	if str(property["name"]).contains("sync"):
		print("[probe] blend space property ", property)
'''),
    {'op': 'main_screen', 'name': '3D'},
    *play(game, 90),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
