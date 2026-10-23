import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows

WINDOW = 'Project Settings'


def settings_section(path):
    # Selects a section in the General tab's tree, as clicking it does, and lists its rows.
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		var item: TreeItem = tree.get_root()
		for part in {path!r}:
			var next: TreeItem = null
			for child in item.get_children():
				if child.get_text(0) == part:
					next = child
			if next == null:
				return "no section " + part
			item = next
		tree.set_selected(item, 0)
		tree.item_selected.emit()
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		var rows := []
		for property in plugin._collect(window, "EditorProperty", ""):
			rows.append(str(property.get_edited_property()) + " = " + str(property.label))
		print("[probe] section {'/'.join(path)}\\n  ", "\\n  ".join(rows))
''')


def tree_dump():
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		print("[probe] title ", window.title)
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		var out := []
		for top in tree.get_root().get_children():
			var children := []
			for child in top.get_children():
				children.append(child.get_text(0))
			out.append(top.get_text(0) + ": " + ", ".join(children))
		print("[probe] tree\\n  ", "\\n  ".join(out))
		for tabs in plugin._collect(window, "TabBar", ""):
			var names := []
			for i in tabs.tab_count:
				names.append(tabs.get_tab_title(i))
			print("[probe] tabs ", names)
''')


write(sys.argv[2], [
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    tree_dump(),
    {'op': 'capture', 'name': 'p03_settings', 'window': WINDOW},
    settings_section(['Display', 'Window']),
    settings_section(['Physics', 'Common']),
    settings_section(['Layer Names', '3D Physics']),
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		for button in plugin._collect(window, "CheckButton", ""):
			print("[probe] check button ", button.text, " ", button.button_pressed)
'''),
])
