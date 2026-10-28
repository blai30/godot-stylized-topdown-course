# Probes how a mesh library import treats collision nodes: -colonly children of a piece.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, REIMPORT, import_set

GLB = 'res://art/water/col_kit.glb'
steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': GLB},
    *click_file('col_kit.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for button in plugin._collect(dock, "OptionButton", ""):
	if button.get_item_text(1) == "Mesh Library":
		button.select(1)
		button.item_selected.emit(1)
'''),
    {'op': 'wait', 'frames': 40},
    import_set('mesh_library/use_node_names_as_mesh_names', 'true'),
    REIMPORT,
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'sleep', 'seconds': 6},
    eval_(f'''
var library: MeshLibrary = load("{GLB}")
for id in library.get_item_list():
	var shapes := library.get_item_shapes(id)
	print("[probe] item ", id, " ", library.get_item_name(id), " shapes ", shapes.size() / 2, " ", shapes)
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
