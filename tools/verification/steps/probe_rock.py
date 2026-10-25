# Probe: the rock scene's nodes, and the Shader Editor's File menu.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://art/nature/rock_small/rock_small.tscn'},
    {'op': 'wait', 'frames': 40},
    eval_('''
var root := editor.get_edited_scene_root()
var out := []
for node in root.find_children("*", "", true, false):
	out.append("%s %s" % [root.get_path_to(node), node.get_class()])
print("[probe] rock nodes ", root.name, " ", out)
'''),
    click_tab('Shader Editor'),
    {'op': 'wait', 'frames': 40},
    eval_('''
for button in plugin._collect(plugin.get_tree().root, "MenuButton", "File"):
	var popup: PopupMenu = button.get_popup()
	var items := []
	for i in popup.item_count:
		items.append(popup.get_item_text(i))
	print("[probe] file menu ", items)
'''),
]
write(sys.argv[2], steps)
