import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows, dump_popups
from probe03 import WINDOW

write(sys.argv[2], [
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		var tabs: TabContainer = plugin._collect(window, "TabContainer", "")[0]
		tabs.current_tab = 1
'''),
    {'op': 'wait', 'frames': 30},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		for edit in plugin._collect(window, "LineEdit", ""):
			if edit.placeholder_text == "Add New Action":
				edit.text = "move_left"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no Add New Action field"
'''),
    {'op': 'wait', 'frames': 30},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		var trees := plugin._collect(window, "Tree", "")
		for tree in trees:
			var root: TreeItem = tree.get_root()
			if root == null:
				continue
			for item in root.get_children():
				var buttons := []
				for column in tree.columns:
					for b in item.get_button_count(column):
						buttons.append(str(column) + ":" + str(item.get_button_id(column, b)) + ":" + item.get_button_tooltip_text(column, b))
				print("[probe] action row ", item.get_text(0), " buttons ", buttons)
'''),
    {'op': 'capture', 'name': 'p03_action_added', 'window': WINDOW},
    # Press the row's Add Event button, as clicking the + does.
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		for tree in plugin._collect(window, "Tree", ""):
			var root: TreeItem = tree.get_root()
			if root == null:
				continue
			for item in root.get_children():
				if item.get_text(0) == "move_left":
					for column in tree.columns:
						for b in item.get_button_count(column):
							if item.get_button_tooltip_text(column, b).begins_with("Add Event"):
								tree.button_clicked.emit(item, column, item.get_button_id(column, b), MOUSE_BUTTON_LEFT)
								return ""
return "no Add Event button"
'''),
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    {'op': 'capture', 'name': 'p03_event_dialog', 'window': 'Event Configuration'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "Event Configuration" in window.title:
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		for top in tree.get_root().get_children():
			if top.get_text(0) in ["Mouse Buttons", "Joypad Axes", "Joypad Buttons"]:
				var names := []
				for child in top.get_children():
					names.append(child.get_text(0))
				print("[probe] list ", top.get_text(0), " ", names)
'''),
])
