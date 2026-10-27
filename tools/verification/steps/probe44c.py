# Probes Advanced Import Settings on the bank mesh library: its tree and the material's options.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, open_advanced, dump_windows
from bonemap_ui import ADVANCED, select_node

GLB = 'res://art/water/bank_kit.glb'
steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': GLB},
    *click_file('bank_kit.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 40},
    open_advanced(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'p44_advanced', 'window': 'Advanced'},
    eval_(ADVANCED + '''
var tree: Tree = plugin._collect(advanced, "Tree", "")[0]
var names := []
var item: TreeItem = tree.get_root()
while item:
	names.append(item.get_text(0))
	item = item.get_next_in_tree()
print("[probe] tree ", names)
for button in plugin._collect(advanced, "Button", ""):
	print("[probe] button ", button.text, " ", button.tooltip_text)
for tabs in plugin._collect(advanced, "TabBar", ""):
	var titles := []
	for i in tabs.tab_count:
		titles.append(tabs.get_tab_title(i))
	print("[probe] tabs ", titles)
'''),
    eval_(ADVANCED + '''
for tabs in plugin._collect(advanced, "TabBar", ""):
	for i in tabs.tab_count:
		if tabs.get_tab_title(i) == "Materials":
			tabs.current_tab = i
			tabs.tab_changed.emit(i)
for i in 6:
	await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    eval_(ADVANCED + '''
for tree in plugin._collect(advanced, "Tree", ""):
	var names := []
	var item: TreeItem = tree.get_root()
	while item:
		names.append(item.get_text(0))
		item = item.get_next_in_tree()
	print("[probe] tree ", tree.is_visible_in_tree(), " ", names)
'''),
    {'op': 'capture', 'name': 'p44_materials', 'window': 'Advanced'},
    select_node('bank_earth'),
    {'op': 'wait', 'frames': 20},
    eval_(ADVANCED + '''
for row in plugin._collect(advanced, "EditorProperty", ""):
	print("[probe] row ", row.label, " ", row.get_edited_property(), " ", row.is_visible_in_tree())
'''),
    {'op': 'capture', 'name': 'p44_material_selected', 'window': 'Advanced'},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
