# Probes the Inspector's resource options menu: New Resource and its dialog.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows

steps = [
    {'op': 'sleep', 'seconds': 3},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for menu in plugin._collect(dock, "MenuButton", ""):
	var popup: PopupMenu = menu.get_popup()
	var items := []
	for i in popup.item_count:
		items.append([i, popup.get_item_text(i), popup.get_item_id(i)])
	print("[probe] menu ", menu.tooltip_text, " ", items)
	if menu.tooltip_text.begins_with("Extra resource"):
		for i in popup.item_count:
			if popup.get_item_text(i).begins_with("New Resource"):
				popup.id_pressed.emit(popup.get_item_id(i))
'''),
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
