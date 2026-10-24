# Probes the Extract Path folder button's dialog.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows, click_tab, click_file

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': 'res://art/nature/rock_small/rock_small.glb'},
    *click_file('rock_small.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 20},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "materials/extract":
		row.emit_changed("materials/extract", 1)
await plugin.get_tree().process_frame
await plugin.get_tree().process_frame
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "materials/extract_path":
		print("[probe] path row ", row.get_class(), " edits ", plugin._collect(row, "LineEdit", "").map(func(e): return [e.text, e.editable]))
		for button in plugin._collect(row, "Button", ""):
			button.pressed.emit()
			return ""
return "no extract path row"
'''),
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    {'op': 'capture', 'name': 'p11_dir_dialog', 'window': 'Select'},
]
write(sys.argv[2], steps)
