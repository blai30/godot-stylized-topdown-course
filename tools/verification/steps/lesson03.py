import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

WINDOW = 'Project Settings'
EVENT_WINDOW = 'Event Configuration'
FIND_WINDOW = f'''
var window: Window = null
for candidate in plugin._windows(plugin.get_tree().root):
	if candidate.visible and "{WINDOW}" in candidate.title:
		window = candidate
if window == null:
	return "no {WINDOW} window"
'''


def section(*path):
    # Clicks a section in the General tab's tree.
    return eval_(FIND_WINDOW + f'''
var tree: Tree = plugin._collect(window, "Tree", "")[0]
var item: TreeItem = tree.get_root()
for part in {list(path)!r}:
	var next: TreeItem = null
	for child in item.get_children():
		if child.get_text(0) == part:
			next = child
	if next == null:
		return "no section " + part
	item = next
tree.set_selected(item, 0)
tree.item_selected.emit()
tree.scroll_to_item(item)
''')


def setting(name, value):
    # Changes one row in the shown section, as editing its field does.
    return eval_(FIND_WINDOW + f'''
for property in plugin._collect(window, "EditorProperty", ""):
	if str(property.get_edited_property()) == "{name}":
		property.emit_changed(property.get_edited_property(), {value})
		return ""
return "no row {name}"
''')


def tab(index):
    return eval_(FIND_WINDOW + f'''
var tabs: TabContainer = plugin._collect(window, "TabContainer", "")[0]
tabs.current_tab = {index}
''')


def add_action(name):
    return eval_(FIND_WINDOW + f'''
for edit in plugin._collect(window, "LineEdit", ""):
	if edit.placeholder_text == "Add New Action":
		edit.text = "{name}"
		edit.text_changed.emit(edit.text)
		edit.text_submitted.emit(edit.text)
		return ""
return "no Add New Action field"
''')


def open_event_dialog(action):
    # Clicks the + at the right of the action's row.
    return eval_(FIND_WINDOW + f'''
for tree in plugin._collect(window, "Tree", ""):
	var root: TreeItem = tree.get_root()
	if root == null:
		continue
	for item in root.get_children():
		if item.get_text(0) == "{action}":
			for column in tree.columns:
				for b in item.get_button_count(column):
					if item.get_button_tooltip_text(column, b) == "Add Event":
						tree.button_clicked.emit(item, column, item.get_button_id(column, b), MOUSE_BUTTON_LEFT)
						return ""
return "no Add Event button for {action}"
''')


def press_key(key):
    # Presses a key while the dialog listens, with the fields Godot's Windows backend fills in for a real press: a letter
    # carries its character, and Shift arrives as the left Shift key. Godot never sets a modifier key's own modifier flag
    # (display_server_windows.cpp, "if (keycode != Key::SHIFT)").
    shift = key == 'KEY_SHIFT'
    unicode = 0 if shift else f'"{key[4:].lower()}".unicode_at(0)'
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{EVENT_WINDOW}" in window.title:
		plugin._collect(window, "EventListenerLineEdit", "")[0].grab_focus()
		for pressed in [true, false]:
			var event := InputEventKey.new()
			event.keycode = {key}
			event.physical_keycode = {key}
			event.key_label = {key}
			event.unicode = {unicode} if pressed else 0
			event.location = KEY_LOCATION_LEFT if {str(shift).lower()} else KEY_LOCATION_UNSPECIFIED
			event.pressed = pressed
			window.push_input(event)
			await plugin.get_tree().process_frame
		return ""
return "no event dialog"
''')


def pick_from_list(group, item_text):
    # Opens a group in the dialog's list and selects one input in it.
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{EVENT_WINDOW}" in window.title:
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		for top in tree.get_root().get_children():
			if top.get_text(0) == "{group}":
				top.collapsed = false
				for child in top.get_children():
					if child.get_text(0) == "{item_text}":
						tree.set_selected(child, 0)
						tree.item_selected.emit()
						tree.scroll_to_item(child)
						return ""
return "no list item {item_text}"
''')


def ok_event():
    return {'op': 'press', 'find': {'window': EVENT_WINDOW, 'type': 'Button', 'text': 'OK'}}


def key_event(action, key, capture=None):
    steps = [open_event_dialog(action), {'op': 'wait', 'frames': 30}, press_key(key), {'op': 'wait', 'frames': 20}]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': EVENT_WINDOW})
    return steps + [ok_event(), {'op': 'wait', 'frames': 20}]


def list_event(action, group, item_text, capture=None):
    steps = [open_event_dialog(action), {'op': 'wait', 'frames': 30}, pick_from_list(group, item_text), {'op': 'wait', 'frames': 20}]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': EVENT_WINDOW})
    return steps + [ok_event(), {'op': 'wait', 'frames': 20}]


steps = [
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    # A new project starts with Advanced Settings off.
    eval_(FIND_WINDOW + '''
plugin._collect(window, "CheckButton", "Advanced Settings")[0].button_pressed = false
'''),
    {'op': 'wait', 'frames': 30},
    # The window.
    section('Display', 'Window'),
    {'op': 'wait', 'frames': 20},
    setting('size/viewport_width', 1280),
    setting('size/viewport_height', 720),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l03_window', 'window': WINDOW},
    eval_(FIND_WINDOW + '''
for property in plugin._collect(window, "EditorProperty", ""):
	if str(property.get_edited_property()) == "vsync/vsync_mode":
		var scroll: Node = property.get_parent()
		while not scroll is ScrollContainer:
			scroll = scroll.get_parent()
		(scroll as ScrollContainer).ensure_control_visible(property)
		var option: OptionButton = plugin._collect(property, "OptionButton", "")[0]
		var items := []
		for i in option.item_count:
			items.append(option.get_item_text(i))
		print("[probe] vsync options ", items, " selected ", option.text)
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l03_vsync', 'window': WINDOW},
    # Physics interpolation is an advanced setting.
    section('Physics', 'Common'),
    {'op': 'wait', 'frames': 20},
    eval_(FIND_WINDOW + '''
plugin._collect(window, "CheckButton", "Advanced Settings")[0].button_pressed = true
'''),
    {'op': 'wait', 'frames': 30},
    eval_(FIND_WINDOW + '''
var tree: Tree = plugin._collect(window, "Tree", "")[0]
print("[probe] section after advanced on: ", tree.get_selected().get_text(0) if tree.get_selected() else "none")
var names := []
for property in plugin._collect(window, "EditorProperty", ""):
	names.append(str(property.get_edited_property()))
print("[probe] rows after advanced on: ", names)
'''),
    setting('physics_interpolation', 'true'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l03_physics', 'window': WINDOW},
    eval_(FIND_WINDOW + '''
plugin._collect(window, "CheckButton", "Advanced Settings")[0].button_pressed = false
'''),
    {'op': 'wait', 'frames': 30},
    # Layer names.
    section('Layer Names', '3D Physics'),
    {'op': 'wait', 'frames': 20},
    setting('layer_1', '"World"'),
    setting('layer_2', '"Player"'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l03_layers', 'window': WINDOW},
    # The input map.
    tab(1),
    {'op': 'wait', 'frames': 30},
]
for action in ('move_left', 'move_right', 'move_forward', 'move_back', 'sprint', 'zoom_in', 'zoom_out'):
    steps += [add_action(action), {'op': 'wait', 'frames': 20}]
steps += [{'op': 'capture', 'name': 'l03_actions_added', 'window': WINDOW}]
steps += key_event('move_left', 'KEY_A', capture='l03_event_key')
steps += list_event('move_left', 'Joypad Axes', 'Joypad Axis 0 - (Left Stick Left, Joystick 0 Left)', capture='l03_event_stick')
steps += key_event('move_right', 'KEY_D')
steps += list_event('move_right', 'Joypad Axes', 'Joypad Axis 0 + (Left Stick Right, Joystick 0 Right)')
steps += key_event('move_forward', 'KEY_W')
steps += list_event('move_forward', 'Joypad Axes', 'Joypad Axis 1 - (Left Stick Up, Joystick 0 Up)')
steps += key_event('move_back', 'KEY_S')
steps += list_event('move_back', 'Joypad Axes', 'Joypad Axis 1 + (Left Stick Down, Joystick 0 Down)')
steps += key_event('sprint', 'KEY_SHIFT', capture='l03_event_shift')
steps += list_event('zoom_in', 'Mouse Buttons', 'Mouse Wheel Up', capture='l03_event_wheel')
steps += list_event('zoom_out', 'Mouse Buttons', 'Mouse Wheel Down')
steps += [
    {'op': 'capture', 'name': 'l03_input_map', 'window': WINDOW},
    {'op': 'press', 'find': {'window': WINDOW, 'type': 'Button', 'text': 'Close'}},
    {'op': 'wait', 'frames': 30},
    eval_('print("[probe] project.godot\\n", FileAccess.get_file_as_string("res://project.godot"))'),
]
write(sys.argv[2], steps)
