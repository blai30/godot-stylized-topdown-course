# Probe: where the Node dock's Groups editor is, and how it is switched to.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab

steps = [
    {'op': 'sleep', 'seconds': 5},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'Trees'},
    {'op': 'wait', 'frames': 20},
    eval_('''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	for i in bar.tab_count:
		if bar.get_tab_title(i) == "Groups":
			var container = bar.get_parent()
			while container != null and not container is TabContainer:
				container = container.get_parent()
			container.current_tab = i
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'probe62b_groups'},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "GroupsEditor")
var chain := []
var node: Node = dock
while node != null and chain.size() < 8:
	chain.append(node.get_class() + ":" + str(node.name) + (" visible" if node is Control and node.is_visible_in_tree() else " hidden"))
	node = node.get_parent()
print("[probe] groups editor chain ", chain)
var parent = dock.get_parent()
var siblings := []
for child in parent.get_children():
	siblings.append(child.get_class() + ":" + str(child.name))
print("[probe] siblings ", siblings)
for edit in dock.find_children("*", "LineEdit", true, false):
	print("[probe] line edit placeholder [", edit.placeholder_text, "] visible ", edit.is_visible_in_tree(), " editable ", edit.editable, " text [", edit.text, "]")
for button in dock.find_children("*", "Button", true, false):
	print("[probe] button ", button.text, " | ", button.tooltip_text)
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	print("[probe] tabs ", titles)
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
