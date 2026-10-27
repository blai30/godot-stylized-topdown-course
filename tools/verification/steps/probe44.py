# Probes importing the bank glb as a Mesh Library.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, DUMP_IMPORT, REIMPORT, dump_windows

PATH = 'res://art/water/bank_kit.glb'
steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': PATH},
    *click_file('bank_kit.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for button in plugin._collect(dock, "OptionButton", ""):
	if button.get_item_text(1) == "Mesh Library":
		button.select(1)
		button.item_selected.emit(1)
		print("[probe] selected ", button.text)
'''),
    {'op': 'wait', 'frames': 40},
    DUMP_IMPORT,
    {'op': 'capture', 'name': 'p44_import_meshlib'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 2},
    {'op': 'capture', 'name': 'p44_after_reimport'},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window is ConfirmationDialog and window.visible:
		window.get_ok_button().pressed.emit()
		print("[probe] confirmed")
'''),
    {'op': 'sleep', 'seconds': 6},
    eval_(f'''
print("[probe] import file ", FileAccess.get_file_as_string("{PATH}.import"))
var library = load("{PATH}")
print("[probe] loaded ", library, " ", library.get_class())
if library is MeshLibrary:
	for id in library.get_item_list():
		var mesh: Mesh = library.get_item_mesh(id)
		print("[probe] item ", id, " ", library.get_item_name(id), " surfaces ", mesh.get_surface_count(), " material ", mesh.surface_get_material(0), " transform ", library.get_item_mesh_transform(id))
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
