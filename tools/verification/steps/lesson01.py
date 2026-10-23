import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

write(sys.argv[2], [
    {'op': 'menu', 'path': ['Editor', 'Editor Settings...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'set_text', 'find': {'window': 'Editor Settings', 'type': 'LineEdit', 'nth': 0}, 'text': 'external editor'},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Editor Settings":
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		var dotnet = plugin._find_item(tree.get_root(), "Dotnet")
		var item: TreeItem = dotnet.get_first_child()
		tree.set_selected(item, 0)
		print("[probe] selected ", item.get_text(0))
'''),
    {'op': 'wait', 'frames': 30},
    eval_('''
var names := []
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Editor Settings":
		for property in plugin._collect(window, "EditorProperty", ""):
			names.append(str(property.get_edited_property()) + "=" + str(property.label))
print("[probe] properties ", names)
var property = plugin._find_property(plugin.get_tree().root, "external_editor")
if property == null:
	return "no external editor property"
var option = plugin._collect(property, "OptionButton", "")
var items := []
if option.size() > 0:
	for i in option[0].item_count:
		items.append(option[0].get_item_text(i))
print("[probe] external editor options ", items, " label ", property.label)
'''),
    {'op': 'capture', 'name': 'l01_editor_settings', 'window': 'Editor Settings'},
])
