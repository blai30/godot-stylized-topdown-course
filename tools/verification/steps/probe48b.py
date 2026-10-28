import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_
steps = [
    {'op': 'sleep', 'seconds': 3},
    eval_('''
var library: MeshLibrary = load("res://art/water/bank_kit.glb")
for id in library.get_item_list():
	var shapes := library.get_item_shapes(id)
	for i in range(0, shapes.size(), 2):
		var points: PackedVector3Array = shapes[i].points
		var low := points[0]
		var high := points[0]
		for p in points:
			low = Vector3(minf(low.x, p.x), minf(low.y, p.y), minf(low.z, p.z))
			high = Vector3(maxf(high.x, p.x), maxf(high.y, p.y), maxf(high.z, p.z))
		print("[probe] ", library.get_item_name(id), " shape ", i / 2, " ", low, " to ", high, " transform ", shapes[i + 1])
'''),
    {'op': 'quit'}]
write(sys.argv[2], steps)
