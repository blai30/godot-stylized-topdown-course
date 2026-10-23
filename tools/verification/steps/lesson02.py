import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_popups, dump_windows, submenu, show_submenu


def new_folder(name, capture=False):
    steps = [
        {'op': 'click', 'find': {'class': 'FileSystemDock'}, 'item': 'res://', 'button': 'right'},
        {'op': 'wait', 'frames': 20},
    ]
    if capture:
        steps += [dump_popups(), show_submenu('Create New'), {'op': 'capture', 'name': 'l02_create_new_menu', 'frames': 20}]
    steps += [submenu('Create New', 'Folder...'), {'op': 'wait', 'frames': 30}]
    if capture:
        steps += [dump_windows()]
    steps += [
        {'op': 'set_text', 'find': {'window': 'Create Folder', 'type': 'LineEdit', 'nth': 0}, 'text': name},
        {'op': 'wait', 'frames': 10},
    ]
    if capture:
        steps += [{'op': 'capture', 'name': 'l02_create_folder', 'window': 'Create Folder'}]
    steps += [
        {'op': 'press', 'find': {'window': 'Create Folder', 'type': 'Button', 'text': 'OK'}},
        {'op': 'wait', 'frames': 30},
    ]
    return steps


steps = [
    {'op': 'capture', 'name': 'l02_editor_first', 'frames': 60},
    # Connect the code editor.
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
var property = null
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Editor Settings":
		for candidate in plugin._collect(window, "EditorProperty", ""):
			print("[probe] setting ", candidate.get_edited_property())
			if str(candidate.get_edited_property()).ends_with("external_editor"):
				property = candidate
if property == null:
	return "no external editor property"
var option: OptionButton = plugin._collect(property, "OptionButton", "")[0]
var items := []
for i in option.item_count:
	items.append(option.get_item_text(i))
print("[probe] external editor options ", items, " label ", property.label)
'''),
    {'op': 'capture', 'name': 'l02_editor_settings', 'window': 'Editor Settings'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Editor Settings":
		window.hide()
'''),
    # Create the C# solution.
    {'op': 'menu', 'path': ['Project', 'Tools', 'C#', 'Create C# solution']},
    {'op': 'sleep', 'seconds': 5},
    eval_('''
for file in DirAccess.get_files_at("res://"):
	print("[probe] root file ", file)
print("[probe] csproj\\n", FileAccess.get_file_as_string("res://TopDownTemplate.csproj"))
'''),
    # The folder layout.
    {'op': 'fs', 'path': 'res://'},
]
steps += new_folder('art', capture=True)
for name in ('art_source', 'levels', 'ui', 'world'):
    steps += new_folder(name)
steps += [
    {'op': 'fs', 'path': 'res://'},
    {'op': 'capture', 'name': 'l02_folders', 'frames': 30},
]
write(sys.argv[2], steps)
