# Steps shared by the lessons that use Project Settings' shader globals and the Shader Editor's New Shader menu.
from steps import eval_, open_bottom_panel

SETTINGS = 'Project Settings'

FIND_SETTINGS = f"""
var window: Window = null
for candidate in plugin._windows(plugin.get_tree().root):
	if candidate.visible and "{SETTINGS}" in candidate.title:
		window = candidate
if window == null:
	return "no {SETTINGS} window"
"""


def select_tab(title):
    return eval_(FIND_SETTINGS + f"""
for bar in plugin._collect(window, "TabBar", ""):
	for i in bar.tab_count:
		if bar.get_tab_title(i) == "{title}":
			bar.current_tab = i
			return ""
return "no tab {title}"
""")


def add_global(name, type_name):
    return [
        eval_(FIND_SETTINGS + f"""
var edit: LineEdit = null
var option: OptionButton = null
var add: Button = null
for control in plugin._collect(window, "", ""):
	if control is LineEdit and edit == null:
		edit = control
	elif control is OptionButton and option == null and option_is_type(control):
		option = control
	elif control is Button and control.text == "Add":
		add = control
var items := []
for i in option.item_count:
	items.append(option.get_item_text(i))
print("[probe] global types ", items)
edit.text = "{name}"
edit.text_changed.emit("{name}")
option.select(items.find("{type_name}"))
option.item_selected.emit(items.find("{type_name}"))
add.pressed.emit()
""".replace('and option_is_type(control)', '')),
        {'op': 'wait', 'frames': 30},
    ]


def set_global(name, values):
    # Types into the value fields of a shader global's row: one field for a float, two for a vec2.
    return [
        eval_(FIND_SETTINGS + f"""
var values: Array = {values!r}
for row in plugin._collect(window, "EditorProperty", ""):
	if row.label == "{name}":
		var sliders := plugin._collect(row, "EditorSpinSlider", "")
		if sliders.size() != values.size():
			return "{name} has %d fields, wanted %d" % [sliders.size(), values.size()]
		for i in values.size():
			sliders[i].value = values[i]
			sliders[i].value_changed.emit(values[i])
		return ""
return "no row {name}"
"""),
        {'op': 'wait', 'frames': 20},
    ]


def set_texture_global(name, path):
    # Picks a texture into a sampler2D global's row, as dragging a file onto its picker does.
    return [
        eval_(FIND_SETTINGS + f"""
for row in plugin._collect(window, "EditorProperty", ""):
	if row.label == "{name}":
		var pickers := plugin._collect(row, "EditorResourcePicker", "")
		if pickers.is_empty():
			return "{name} has no picker"
		pickers[0].edited_resource = load("{path}")
		pickers[0].resource_changed.emit(load("{path}"))
		return ""
return "no row {name}"
"""),
        {'op': 'wait', 'frames': 20},
    ]


def new_shader_file(menu_item, path, mode_capture=None):
    return [
        open_bottom_panel('Shader Editor'),
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for button in plugin._collect(plugin.get_tree().root, "MenuButton", "File"):
	var popup: PopupMenu = button.get_popup()
	var items := []
	for i in popup.item_count:
		items.append(popup.get_item_text(i))
	print("[probe] file menu ", items)
	for i in popup.item_count:
		if popup.get_item_text(i) == "{menu_item}":
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no {menu_item} in the Shader Editor's File menu"
'''),
        {'op': 'wait', 'frames': 40},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Create Shader":
		for option in plugin._collect(window, "OptionButton", ""):
			var items := []
			for i in option.item_count:
				items.append(option.get_item_text(i))
			print("[probe] create shader ", items, " selected ", option.get_item_text(option.selected))
'''),
        {'op': 'set_text', 'find': {'window': 'Create Shader', 'type': 'LineEdit', 'nth': 0}, 'text': path},
        {'op': 'wait', 'frames': 20},
        *([{'op': 'capture', 'name': mode_capture, 'window': 'Create Shader'}] if mode_capture else []),
        {'op': 'press', 'find': {'window': 'Create Shader', 'type': 'Button', 'text': 'Create'}},
        {'op': 'wait', 'frames': 60},
    ]


