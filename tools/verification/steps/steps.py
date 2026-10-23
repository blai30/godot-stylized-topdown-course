# Writes a driver steps file: each argument after the output path is one step as a Python dict literal, or the
# helper functions below are imported by step scripts.
import json
import sys


def write(path, steps):
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        for step in steps:
            file.write(json.dumps(step) + '\n')


def eval_(code):
    return {'op': 'eval', 'code': code.strip('\n')}


def dump_popups():
    return eval_('''
var out := []
for window in plugin._windows(plugin.get_tree().root):
	if window is PopupMenu and window.visible:
		for i in window.item_count:
			out.append(window.get_item_text(i))
print("[probe] popup ", out)
''')


def dump_windows():
    return eval_('''
var out := []
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window != plugin.get_window():
		out.append(window.title + " <" + window.get_class() + ">")
		for control in plugin._collect(window, "", ""):
			if control is Label or control is BaseButton or control is LineEdit:
				out.append("  " + control.get_class() + ": " + str(control.get("text")))
print("[probe] windows\n", "\n".join(out))
''')


INSPECTOR = {'class': 'InspectorDock'}


def submenu(parent_text, item_text):
    # Opens a visible popup's submenu where the reader hovers it, then presses an item in it.
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window is PopupMenu and window.visible:
		for i in window.item_count:
			if window.get_item_text(i) == "{parent_text}":
				var sub: PopupMenu = window.get_item_submenu_node(i)
				var items := []
				for j in sub.item_count:
					items.append(sub.get_item_text(j))
				print("[probe] submenu {parent_text} ", items)
				for j in sub.item_count:
					if sub.get_item_text(j) == "{item_text}":
						sub.id_pressed.emit(sub.get_item_id(j))
						window.hide()
						return ""
return "no submenu item {item_text}"
''')


def show_submenu(parent_text):
    # Shows a submenu beside its parent item, as hovering does, for the capture.
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window is PopupMenu and window.visible:
		for i in window.item_count:
			if window.get_item_text(i) == "{parent_text}":
				window.set_focused_item(i)
				var sub: PopupMenu = window.get_item_submenu_node(i)
				sub.position = window.position + Vector2i(window.size.x - 4, i * 30)
				sub.popup()
				return ""
return "no item {parent_text}"
''')


def unfold_inspector():
    return eval_('''
for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
	section.unfold()
''')


def add_node(type_name, name, parent='.'):
    # Selects the parent, opens Create New Node with the + button, searches, creates, and renames the node.
    return [
        {'op': 'select', 'path': parent},
        {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Add/Create a New Node'}},
        {'op': 'wait', 'frames': 30},
        {'op': 'set_text', 'find': {'window': 'Create New Node', 'type': 'LineEdit', 'nth': 0}, 'text': type_name},
        {'op': 'wait', 'frames': 30},
        {'op': 'press', 'find': {'window': 'Create New Node', 'type': 'Button', 'text': 'Create'}},
        {'op': 'wait', 'frames': 30},
        eval_(f'''
var root := editor.get_edited_scene_root()
var parent := root if "{parent}" == "." else root.get_node("{parent}")
var node := parent.get_node_or_null("{type_name}")
if node == null:
	return "no {type_name} was added"
node.name = "{name}"
'''),
        {'op': 'select', 'path': name if parent == '.' else f'{parent}/{name}'},
    ]


def new_resource(property, type_name, nth=0):
    # Opens a resource property's menu in the Inspector and picks a type under New.
    return [
        unfold_inspector(),
        {'op': 'wait', 'frames': 10},
        {'op': 'press', 'find': {**INSPECTOR, 'property': property, 'type': 'Button', 'nth': nth}},
        {'op': 'wait', 'frames': 20},
        dump_popups(),
        {'op': 'popup', 'text': type_name},
        {'op': 'wait', 'frames': 30},
    ]


def inspector_set(property, value):
    # Edits one Inspector row, as changing its field does.
    return eval_(f'''
for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
	section.unfold()
await plugin.get_tree().process_frame
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{property}")
if row == null:
	return "no row {property}"
row.emit_changed("{property}", {value})
''')


def option_items(property):
    return eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{property}")
if row == null:
	return "no row {property}"
var option: OptionButton = plugin._collect(row, "OptionButton", "")[0]
var items := []
for i in option.item_count:
	items.append(option.get_item_text(i))
print("[probe] options {property} ", items, " label ", row.label)
''')


def show_row(property):
    return eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{property}")
if row == null:
	return "no row {property}"
editor.get_inspector().ensure_control_visible(row)
''')


def view(*paths, dx=0, dy=0, wheel=0):
    # Frames the given nodes with the viewport's Focus and Frame Selection, orbits and zooms like the middle mouse
    # button and wheel, then clears the selection so no gizmo covers the result.
    steps = []
    if paths:
        steps.append(eval_(f'''
var root := editor.get_edited_scene_root()
editor.get_selection().clear()
for path in {list(paths)!r}:
	editor.get_selection().add_node(root.get_node(path))
var viewport = plugin._collect(plugin.get_tree().root, "Node3DEditorViewport", "")[0]
for button in plugin._collect(viewport, "MenuButton", "Perspective"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i) == "Focus and Frame Selection":
			popup.id_pressed.emit(popup.get_item_id(i))
'''))
        steps.append({'op': 'wait', 'frames': 30})
    if dx or dy:
        steps.append({'op': 'orbit', 'dx': dx, 'dy': dy})
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps.append(eval_('editor.get_selection().clear()'))
    return steps


def save_code(path, code):
    # The reader saves the file in their code editor; Godot sees the change on disk.
    return eval_(f'''
var file := FileAccess.open("{path}", FileAccess.WRITE)
file.store_string({code!r})
file.close()
''')


def build(name=None):
    # Presses the hammer, Build Project, and waits for MSBuild. The button is found by its shortcut's name, because the
    # run buttons beside it change their tooltips while and after a game runs.
    steps = [
        eval_('''
for button in plugin._collect(plugin.get_tree().root, "Button", ""):
	if button.is_visible_in_tree() and button.shortcut and button.shortcut.resource_name == "Build Project":
		button.pressed.emit()
		return ""
return "no Build Project button"
'''),
        {'op': 'sleep', 'seconds': 25},
    ]
    if name:
        steps.append({'op': 'capture', 'name': name, 'frames': 20})
    return steps


def game_steps(path, steps):
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        for step in steps:
            file.write(json.dumps(step) + '\n')
    return path


def play(game_path, wait_seconds, capture_dialog=None, capture_output=None, capture_running=None):
    # Clears the Output panel, runs the main scene as F5 does, and waits for the game's own steps to finish.
    steps = [
        eval_('''
# The Output panel's clear button (Ctrl+Alt+K) has no tooltip; the panel may be closed, so search it whole.
var log = plugin._find_class(plugin.get_tree().root, "EditorLog")
for button in log.find_children("*", "Button", true, false):
	if button.shortcut and button.shortcut.get_as_text() == "Ctrl+Alt+K":
		button.pressed.emit()
		return ""
return "no clear button in the Output panel"
'''),
        eval_(f'''
OS.set_environment("CAPTURE_GAME_STEPS", {game_path!r})
OS.set_environment("CAPTURE_GAME_LOG", {game_path[:-6] + '.log'!r})
DirAccess.remove_absolute({game_path[:-6] + '.log'!r})
'''),
        eval_('editor.play_main_scene()'),
        {'op': 'wait', 'frames': 40},
    ]
    if capture_dialog:
        steps += [
            # The dialog has no title; it is captured by its class.
            {'op': 'capture', 'name': capture_dialog, 'window': 'class:ConfirmationDialog'},
            {'op': 'press', 'find': {'type': 'Button', 'text': 'Select Current'}},
        ]
    if capture_running:
        # The editor while the game runs, a few seconds in.
        steps += [{'op': 'sleep', 'seconds': 6}, {'op': 'capture', 'name': capture_running}]
        wait_seconds -= 6
    steps.append({'op': 'sleep', 'seconds': wait_seconds})
    if capture_output:
        steps.append({'op': 'capture', 'name': capture_output, 'frames': 20})
    steps.append(eval_('print("[probe] main scene ", ProjectSettings.get_setting("application/run/main_scene"))'))
    # The game's own steps must have run to the end; an editor run alone proves nothing about the game.
    steps.append(eval_(f'''
var log := FileAccess.get_file_as_string({game_path[:-6] + '.log'!r})
if not log.contains("[game] quit  ok"):
	return "the game's steps did not finish: " + log.right(200)
'''))
    return steps


def open_in_file_dialog(*folders):
    # Double-clicks folders in the visible file dialog's list, as the reader does, starting from where it opened.
    return eval_(f'''
var dialog: EditorFileDialog = null
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		dialog = window
if dialog == null:
	return "no file dialog"
print("[probe] file dialog opened at ", dialog.current_dir, " with file ", dialog.current_file)
for folder in {list(folders)!r}:
	var found := false
	for list in plugin._collect(dialog, "ItemList", ""):
		for i in list.item_count:
			if list.get_item_text(i) == folder:
				list.select(i)
				list.item_activated.emit(i)
				found = true
				break
		if found:
			break
	if not found:
		return "no folder " + folder + " in the dialog at " + dialog.current_dir
	await plugin.get_tree().process_frame
	await plugin.get_tree().process_frame
print("[probe] file dialog now at ", dialog.current_dir)
''')


def press_delete_in_scene_dock():
    # Presses Delete with the Scene dock focused, as the reader does after selecting a node.
    return eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "SceneTreeDock")
var tree: Tree = plugin._collect(dock, "Tree", "")[0]
tree.grab_focus()
for pressed in [true, false]:
	var event := InputEventKey.new()
	event.keycode = KEY_DELETE
	event.physical_keycode = KEY_DELETE
	event.pressed = pressed
	tree.get_viewport().push_input(event)
	await plugin.get_tree().process_frame
''')


def make_folder(parent, name):
    # Makes a folder without the FileSystem dock's context menu, which Godot opens at the system cursor, on the desktop of
    # whoever is at the computer. Lesson 2 verifies the menu and the Create Folder dialog themselves.
    return [
        eval_(f'''
var error := DirAccess.make_dir_recursive_absolute("res://{parent}/{name}")
if error != OK:
	return "could not make res://{parent}/{name}: %d" % error
editor.get_resource_filesystem().scan()
'''),
        {'op': 'sleep', 'seconds': 2},
    ]
