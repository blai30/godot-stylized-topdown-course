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
	if button.shortcut and button.shortcut.get_as_text().ends_with("K") and (button.shortcut.get_as_text().contains("Alt") or button.shortcut.get_as_text().contains("Option")):
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
	# The folder list, not the Recent or Favorites lists: the one whose double-click takes the dialog into the folder.
	var entered := false
	for list in plugin._collect(dialog, "ItemList", ""):
		for i in list.item_count:
			if list.get_item_text(i) == folder:
				list.select(i)
				list.item_activated.emit(i)
				for attempt in 30:
					await plugin.get_tree().process_frame
					if dialog.current_dir.ends_with("/" + folder):
						entered = true
						break
				break
		if entered:
			break
	if not entered:
		return "could not go into " + folder + " from " + dialog.current_dir
	# Let the list show the new folder's contents.
	for attempt in 10:
		await plugin.get_tree().process_frame
print("[probe] file dialog now at ", dialog.current_dir)
if not dialog.current_dir.ends_with("/" + {list(folders)!r}[-1]):
	return "the dialog is at " + dialog.current_dir
''')


def press_delete_in_scene_dock():
    # Presses Delete with the Scene dock focused, as the reader does after selecting a node.
    return eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "SceneTreeDock")
var tree: Tree = plugin._collect(dock, "Tree", "")[0]
tree.grab_focus()
for pressed in [true, false]:
	var event := InputEventKey.new()
	# macOS has no Delete key on its keyboards: the shortcut is Cmd+Backspace.
	var mac := OS.get_name() == "macOS"
	event.keycode = KEY_BACKSPACE if mac else KEY_DELETE
	event.physical_keycode = event.keycode
	event.meta_pressed = mac
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


def click_tab(title):
    # Clicks a dock's tab by its title, at the tab's own position, as the reader does.
    return eval_(f'''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	if not bar.is_visible_in_tree():
		continue
	for i in bar.tab_count:
		if bar.get_tab_title(i) == "{title}":
			var at: Vector2 = bar.get_global_transform_with_canvas() * bar.get_tab_rect(i).get_center()
			for pressed in [true, false]:
				var event := InputEventMouseButton.new()
				event.button_index = MOUSE_BUTTON_LEFT
				event.pressed = pressed
				event.position = at
				event.global_position = at
				bar.get_viewport().push_input(event)
				await plugin.get_tree().process_frame
			return ""
return "no tab {title}"
''')


def close_bottom_panel():
    # Collapses the bottom panel by clicking its current tab again, as the reader does; nothing happens if it is closed.
    return eval_('''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	if bar.current_tab >= 0 and "Output" in titles:
		var at: Vector2 = bar.get_global_transform_with_canvas() * bar.get_tab_rect(bar.current_tab).get_center()
		for pressed in [true, false]:
			var event := InputEventMouseButton.new()
			event.button_index = MOUSE_BUTTON_LEFT
			event.pressed = pressed
			event.position = at
			event.global_position = at
			bar.get_viewport().push_input(event)
			await plugin.get_tree().process_frame
''')


def open_bottom_panel(title):
    # Opens a bottom panel by its tab, unless it is already the open one (a second click would collapse it).
    return eval_(f'''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	if "Output" in titles:
		var index := titles.find("{title}")
		if bar.current_tab == index:
			return ""
		var at: Vector2 = bar.get_global_transform_with_canvas() * bar.get_tab_rect(index).get_center()
		for pressed in [true, false]:
			var event := InputEventMouseButton.new()
			event.button_index = MOUSE_BUTTON_LEFT
			event.pressed = pressed
			event.position = at
			event.global_position = at
			bar.get_viewport().push_input(event)
			await plugin.get_tree().process_frame
		return ""
return "no bottom panel tab"
''')


def click_file(name):
    # Clicks a file in the FileSystem dock's tree, as the reader does to select it.
    return [{'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': name}, {'op': 'wait', 'frames': 30}]


DUMP_IMPORT = eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
var out := []
for row in plugin._collect(dock, "EditorProperty", ""):
	if row.get_edited_object():
		out.append("%s (%s) = %s" % [row.label, row.get_edited_property(), row.get_edited_object().get(row.get_edited_property())])
print("[probe] import dock\\n", "\\n".join(out))
''')


def import_set(property, value):
    # Changes one Import dock option, as picking it in its row does.
    return eval_(f'''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "{property}":
		row.emit_changed("{property}", {value})
		return ""
return "no import option {property}"
''')


def show_import_row(property):
    return eval_(f'''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "{property}":
		var scroll: ScrollContainer = plugin._collect(dock, "ScrollContainer", "")[0]
		scroll.ensure_control_visible(row)
		return ""
return "no import option {property}"
''')


# The Reimport button's label changes when options change, so it is found by how its label starts.
REIMPORT = eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for button in plugin._collect(dock, "Button", ""):
	if str(button.text).begins_with("Reimport"):
		print("[probe] reimport button ", button.text)
		button.pressed.emit()
		return ""
return "no Reimport button"
''')


def instantiate_under(parent, query, capture=None):
    # Instantiate Child Scene with the parent selected: search the quick-open list and press Enter.
    steps = [
        {'op': 'select', 'path': parent},
        {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Instantiate a scene file'}},
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Select Scene"):
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "{query}"
		edit.text_changed.emit(edit.text)
		return ""
return "no Select Scene dialog"
'''),
        {'op': 'wait', 'frames': 30},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Select Scene'})
    steps.append(eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Select Scene"):
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.grab_focus()
		for pressed in [true, false]:
			var event := InputEventKey.new()
			event.keycode = KEY_ENTER
			event.pressed = pressed
			window.push_input(event)
			await plugin.get_tree().process_frame
		return ""
return "no Select Scene dialog"
'''))
    return steps + [{'op': 'wait', 'frames': 40}]


def open_advanced():
    # Presses Advanced... in the Import dock and waits for the window; the first press is sometimes lost while the
    # dock is still updating after a file was selected, so it presses again.
    return eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for attempt in 4:
	for button in plugin._collect(dock, "Button", "Advanced..."):
		button.pressed.emit()
	for frame in 90:
		await plugin.get_tree().process_frame
		for window in plugin._windows(plugin.get_tree().root):
			if window.visible and window.title.contains("Advanced"):
				print("[probe] advanced opened on attempt ", attempt + 1)
				return ""
return "Advanced Import Settings did not open"
''')


def quick_load(property, query, capture=None):
    # A resource row's menu > Quick Load..., the search typed, and Enter, as in lesson 11.
    steps = [
        show_row(property),
        # The row's menu, then Quick Load... in it, in one step: a popup closes when the editor's window loses focus,
        # which the owner's own work on the computer can cause between steps.
        eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{property}")
if row == null:
	return "no row {property}"
# The picker's field and its arrow both open the menu; try them in turn.
for button in plugin._collect(row, "Button", ""):
	button.pressed.emit()
	for attempt in 10:
		await plugin.get_tree().process_frame
		for window in plugin._windows(plugin.get_tree().root):
			if window is PopupMenu and window.visible:
				for i in window.item_count:
					if window.get_item_text(i) == "Quick Load...":
						window.id_pressed.emit(window.get_item_id(i))
						window.hide()
						return ""
return "no Quick Load... in the {property} menu"
'''),
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "EditorQuickOpenDialog":
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "{query}"
		edit.text_changed.emit(edit.text)
		return ""
return "no Quick Load dialog"
'''),
        {'op': 'wait', 'frames': 30},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Quick Load'})
    steps += [
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "EditorQuickOpenDialog":
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.grab_focus()
		for pressed in [true, false]:
			var event := InputEventKey.new()
			event.keycode = KEY_ENTER
			event.pressed = pressed
			window.push_input(event)
			await plugin.get_tree().process_frame
		return ""
return "no Quick Load dialog"
'''),
        {'op': 'wait', 'frames': 30},
    ]
    return steps


def resource_menu(property, item):
    # Opens a resource row's menu in the Inspector and picks an item from it, in one step, so the menu cannot close
    # in between when the editor's window loses focus.
    return eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{property}")
if row == null:
	return "no row {property}"
editor.get_inspector().ensure_control_visible(row)
for button in plugin._collect(row, "Button", ""):
	button.pressed.emit()
	for attempt in 10:
		await plugin.get_tree().process_frame
		for window in plugin._windows(plugin.get_tree().root):
			if window is PopupMenu and window.visible:
				for i in window.item_count:
					if window.get_item_text(i) == "{item}":
						window.id_pressed.emit(window.get_item_id(i))
						window.hide()
						return ""
				window.hide()
return "no {item} in the {property} menu"
''')


def open_resource(property, shows):
    # Clicks a resource row's picture, as the reader does, so the resource's own properties open below it; waits
    # until the row named shows appears. A resource already open is left open.
    return eval_(f'''
if plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{shows}") != null:
	return ""
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{property}")
if row == null:
	return "no row {property}"
editor.get_inspector().ensure_control_visible(row)
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
plugin._collect(picker, "Button", "")[0].pressed.emit()
for attempt in 20:
	await plugin.get_tree().process_frame
	if plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{shows}") != null:
		return ""
return "{property} did not open: no row {shows}"
''')


# Godot can raise "The following files are newer on disk" around a shader save. The text in the Shader Editor is the
# reader's, so the answer is Ignore external changes.
DISK_PROMPT = eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		for label in plugin._collect(window, "Label", ""):
			if label.text.contains("newer on disk"):
				for button in plugin._collect(window, "Button", ""):
					if button.text.begins_with("Ignore"):
						print("[probe] newer on disk prompt: ", button.text)
						button.pressed.emit()
						return ""
''')


def type_shader(code, path):
    # The reader types the code into the Shader Editor and saves it with Ctrl+Alt+S; the file must then hold it.
    return [
        eval_(f'''
var edits := plugin._collect(plugin.get_tree().root, "CodeEdit", "")
if edits.is_empty():
	return "no visible CodeEdit"
var edit: CodeEdit = edits[0]
edit.text = {code!r}
edit.text_changed.emit()
'''),
        {'op': 'wait', 'frames': 20},
        {'op': 'key', 'find': {'type': 'CodeEdit'}, 'key': 'S', 'ctrl': True, 'alt': True},
        {'op': 'wait', 'frames': 60},
        DISK_PROMPT,
        {'op': 'wait', 'frames': 20},
        {'op': 'key', 'find': {'type': 'CodeEdit'}, 'key': 'S', 'ctrl': True, 'alt': True},
        {'op': 'wait', 'frames': 40},
        eval_(f'''
var saved := FileAccess.get_file_as_string("{path}")
if saved != {code!r}:
	return "the file on disk is not the typed code: " + saved.left(120)
'''),
    ]


def new_script(path, inherits, capture=None):
    # Script editor > File > New Script..., as the reader makes a script for a resource: the dialog is filled in the
    # way its fields are, then Create is pressed.
    steps = [
        {'op': 'main_screen', 'name': 'Script'},
        {'op': 'wait', 'frames': 30},
        eval_('''
var editor_node = plugin._find_class(plugin.get_tree().root, "ScriptEditor")
for button in plugin._collect(editor_node, "MenuButton", "File"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i) == "New Script...":
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no New Script... item"
'''),
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var language: OptionButton = plugin._collect(window, "OptionButton", "")[0]
		for i in language.item_count:
			if language.get_item_text(i) == "C#":
				language.select(i)
				language.item_selected.emit(i)
		await plugin.get_tree().process_frame
		# The Script editor starts a built-in script, kept inside a scene; C# scripts are files, so it is switched off.
		for box in plugin._collect(window, "CheckBox", "On"):
			box.button_pressed = false
			box.toggled.emit(false)
		await plugin.get_tree().process_frame
		var edits := plugin._collect(window, "LineEdit", "")
		for edit in edits:
			print("[probe] new script field ", edit.text)
		for edit in edits:
			if str(edit.text) == "Node":
				edit.text = "{inherits}"
				edit.text_changed.emit(edit.text)
		await plugin.get_tree().process_frame
		for edit in edits:
			if str(edit.text).ends_with(".cs"):
				edit.text = "{path}"
				edit.text_changed.emit(edit.text)
		return ""
return "no New Script dialog"
'''),
        {'op': 'wait', 'frames': 30},
        dump_windows(),
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Create Script'})
    steps += [
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		window.get_ok_button().pressed.emit()
		return ""
return "no Create Script dialog"
'''),
        {'op': 'wait', 'frames': 60},
    ]
    return steps


def run_tool_script(path):
    # Opens a C# tool script in the Script editor and presses File > Run, as the reader does.
    return [
        {'op': 'main_screen', 'name': 'Script'},
        eval_(f'''
editor.edit_script(load("{path}"))
'''),
        {'op': 'wait', 'frames': 30},
        eval_('''
var editor_node = plugin._find_class(plugin.get_tree().root, "ScriptEditor")
for button in plugin._collect(editor_node, "MenuButton", "File"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i) == "Run":
			print("[probe] run item disabled ", popup.is_item_disabled(i))
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no Run item in the File menu"
'''),
        {'op': 'sleep', 'seconds': 8},
    ]

