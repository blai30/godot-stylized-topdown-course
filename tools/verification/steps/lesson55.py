# Lesson 55, in Godot: a Theme and a pause panel. A Theme resource styled in the Theme editor, a pause panel scene built from containers
# and controls that takes the theme, a PausePanel script, and the panel instanced in the world environment so every level has it.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, instantiate_under, quick_load, game_steps, play, click_tab,
                   make_folder, new_standalone_resource, save_resource_as, open_bottom_panel, close_bottom_panel, save_code, build,
                   open_in_file_dialog)
from lesson55_pieces import PAUSE_PANEL, PIECES

THEME = 'res://ui/theme.tres'
SCRIPT = 'res://src/UI/PausePanel.cs'
PANEL_SCENE = 'res://ui/pause_panel.tscn'
ENVIRONMENT = 'res://world/environment/world_environment.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
PANEL = 'Meadow/WorldEnvironment/PausePanel'
CLOCK = 'Meadow/WorldEnvironment/Day'
out_dir = os.path.dirname(sys.argv[2])

# The theme: the panel and the button states, with the corner radius and margins that make the soft look.
PANEL_STYLE = {'bg_color': 'Color("#1c2a22eb")', 'corner_radius_top_left': 14, 'corner_radius_top_right': 14, 'corner_radius_bottom_right': 14,
               'corner_radius_bottom_left': 14, 'content_margin_left': 28, 'content_margin_top': 24, 'content_margin_right': 28, 'content_margin_bottom': 24}
BUTTON_RADIUS = {'corner_radius_top_left': 8, 'corner_radius_top_right': 8, 'corner_radius_bottom_right': 8, 'corner_radius_bottom_left': 8}
BUTTON_STYLES = [('normal', '#3f6b4a'), ('hover', '#528a5d'), ('pressed', '#2f5238')]


def theme_editor(tooltip):
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "ThemeEditor")
for button in plugin._collect(panel, "Button", ""):
	if button.tooltip_text.begins_with("{tooltip}") or button.text == "{tooltip}":
		button.pressed.emit()
		return ""
return "no Theme editor button {tooltip}"
''')


def add_theme_type(name):
    return [
        theme_editor('Add a type'),
        {'op': 'wait', 'frames': 40},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "ThemeTypeDialog":
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "{name}"
		edit.text_changed.emit(edit.text)
		window.get_ok_button().pressed.emit()
		return ""
return "no Add Item Type dialog"
'''),
        {'op': 'wait', 'frames': 40},
    ]


def stylebox_tab():
    return eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "ThemeEditor")
for bar in plugin._collect(panel, "TabBar", ""):
	if bar.tab_count == 8:
		bar.current_tab = 5
		bar.tab_changed.emit(5)
		bar.tab_selected.emit(5)
		return ""
return "no item tabs"
''')


def open_stylebox(item):
    # The item's StyleBox button opens the box in the Inspector, as clicking it does. The button shares a row with the item's name.
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "ThemeEditor")
for label in plugin._collect(panel, "Label", ""):
	if label.is_visible_in_tree() and label.text == "{item}" and label.tooltip_text.begins_with("theme_item|"):
		var row: Node = label
		while row != null and row != panel:
			var boxes := plugin._collect(row, "Button", "").filter(func(b): return b.tooltip_text.begins_with("Type: StyleBox"))
			if boxes.size() == 1:
				boxes[0].pressed.emit()
				return ""
			if boxes.size() > 1:
				return "{item} has no box of its own"
			row = row.get_parent()
return "no style box {item}"
''')


def override_item(item):
    # The + beside a default item copies just that item into the theme, so the file holds only what the game changes.
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "ThemeEditor")
for label in plugin._collect(panel, "Label", ""):
	if label.is_visible_in_tree() and label.text == "{item}" and label.tooltip_text.begins_with("theme_item|"):
		var row: Node = label
		while row != null and row != panel:
			var overrides := plugin._collect(row, "Button", "").filter(func(b): return b.tooltip_text == "Override Item" and b.is_visible_in_tree())
			if overrides.size() == 1:
				overrides[0].pressed.emit()
				return ""
			if overrides.size() > 1:
				return "{item} has no override button of its own"
			row = row.get_parent()
return "no item {item}"
''')


def new_stylebox(item):
    # The overridden item holds nothing yet. Its resource menu's New StyleBoxFlat hands the item a new StyleBoxFlat, as this does.
    return [eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "ThemeEditor")
for label in plugin._collect(panel, "Label", ""):
	if label.is_visible_in_tree() and label.text == "{item}" and label.tooltip_text.begins_with("theme_item|"):
		var row: Node = label
		while row != null and row != panel:
			var pickers := plugin._collect(row, "EditorResourcePicker", "").filter(func(p): return p.is_visible_in_tree())
			if pickers.size() == 1:
				var box := StyleBoxFlat.new()
				pickers[0].resource_changed.emit(box)
				return ""
			if pickers.size() > 1:
				return "{item} has no picker of its own"
			row = row.get_parent()
return "no item {item}"
'''), {'op': 'wait', 'frames': 30}]


def style(item, values, capture=None):
    steps = [override_item(item), {'op': 'wait', 'frames': 30}, *new_stylebox(item), open_stylebox(item), {'op': 'wait', 'frames': 30}, unfold_inspector(), {'op': 'wait', 'frames': 20}]
    steps += [inspector_set(key, value if isinstance(value, str) else str(value)) for key, value in values.items()]
    steps += [{'op': 'wait', 'frames': 20}]
    if capture:
        steps.append({'op': 'capture', 'name': capture})
    return steps


def make_unique(*names):
    # The Scene dock's Access as Unique Name: the node is found by %Name from anywhere in its scene.
    return eval_(f'''
var root := editor.get_edited_scene_root()
for node_name in {list(names)!r}:
	root.find_child(node_name, true, true).unique_name_in_owner = true
''')


def assign_node(property, node, capture=None):
    steps = [
        {'op': 'press', 'find': {'class': 'InspectorDock', 'property': property, 'type': 'Button', 'text': 'Assign...'}},
        {'op': 'wait', 'frames': 40},
        {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': node},
    ]
    if capture:
        steps.append({'op': 'capture', 'name': capture, 'window': 'Select a Node'})
    steps += [{'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}}, {'op': 'wait', 'frames': 30}]
    return steps


def event(action, pressed=True):
    return {'op': 'eval', 'code': f'var event := InputEventAction.new()\nevent.action = "{action}"\nevent.pressed = {str(pressed).lower()}\nInput.parse_input_event(event)'}


def state(tag):
    return {'op': 'eval', 'code': f'''
var panel := tree.root.get_node("{PANEL}")
var clock := tree.root.get_node("{CLOCK}")
var sun := tree.root.get_node("Meadow/WorldEnvironment/Sun") as DirectionalLight3D
print("[game] {tag}: paused ", tree.paused, " panel visible ", panel.visible, " time %.5f" % clock.get("TimeOfDay"), " slider ", panel.get_node("%TimeSlider").value, " shadows ", sun.shadow_enabled, " vsync ", DisplayServer.window_get_vsync_mode())'''}


game = game_steps(os.path.join(out_dir, 'game-l55.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    state('running'),
    {'op': 'capture', 'name': 'l55_running', 'frames': 10},
    # Escape pauses: the clock holds and the panel shows what the game has.
    event('ui_cancel'), {'op': 'wait', 'frames': 20}, event('ui_cancel', False),
    {'op': 'wait', 'frames': 40},
    state('paused'),
    {'op': 'capture', 'name': 'l55_paused', 'frames': 10},
    {'op': 'sleep', 'seconds': 1.5},
    state('paused 1.5 s later'),
    # The controls change the game while it is paused.
    {'op': 'eval', 'code': f'tree.root.get_node("{PANEL}").get_node("%TimeSlider").value = 0.78'},
    {'op': 'wait', 'frames': 40},
    state('slider at 0.78'),
    {'op': 'capture', 'name': 'l55_dusk', 'frames': 10},
    {'op': 'eval', 'code': f'tree.root.get_node("{PANEL}").get_node("%ShadowsToggle").button_pressed = false'},
    {'op': 'wait', 'frames': 40},
    state('shadows off'),
    {'op': 'capture', 'name': 'l55_no_shadows', 'frames': 10},
    {'op': 'eval', 'code': f'tree.root.get_node("{PANEL}").get_node("%ShadowsToggle").button_pressed = true\ntree.root.get_node("{PANEL}").get_node("%VsyncToggle").button_pressed = false'},
    {'op': 'wait', 'frames': 20},
    state('vsync off'),
    {'op': 'eval', 'code': f'tree.root.get_node("{PANEL}").get_node("%VsyncToggle").button_pressed = true'},
    {'op': 'wait', 'frames': 20},
    state('vsync on'),
    # Resume, and the day goes on from the hour the slider chose.
    {'op': 'eval', 'code': f'tree.root.get_node("{PANEL}").get_node("%ResumeButton").pressed.emit()'},
    {'op': 'wait', 'frames': 40},
    state('resumed'),
    {'op': 'sleep', 'seconds': 1.5},
    state('resumed 1.5 s later'),
    # Escape again opens it, and again closes it.
    event('ui_cancel'), {'op': 'wait', 'frames': 20}, event('ui_cancel', False), {'op': 'wait', 'frames': 20},
    state('escape again'),
    event('ui_cancel'), {'op': 'wait', 'frames': 20}, event('ui_cancel', False), {'op': 'wait', 'frames': 20},
    state('escape once more'),
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 5},
    *make_folder('', 'ui'),
    *make_folder('src', 'UI'),
    # The theme.
    *new_standalone_resource('Theme', 'l55_new_theme'),
    *save_resource_as(THEME, 'l55_save_theme'),
    unfold_inspector(),
    inspector_set('default_font_size', '20'),
    {'op': 'wait', 'frames': 20},
    open_bottom_panel('Theme'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l55_theme_editor'},
    *add_theme_type('PanelContainer'),
    {'op': 'capture', 'name': 'l55_type_added'},
    stylebox_tab(),
    {'op': 'wait', 'frames': 30},
    *style('panel', PANEL_STYLE, 'l55_panel_style'),
    *add_theme_type('Button'),
    stylebox_tab(),
    {'op': 'wait', 'frames': 30},
]
for item, color in BUTTON_STYLES:
    steps += style(item, {'bg_color': f'Color("{color}")', **BUTTON_RADIUS}, f'l55_button_{item}')
steps += [
    open_bottom_panel('Theme'),
    theme_editor('Save'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l55_theme_saved'},
    eval_(f'''
var theme: Theme = load("{THEME}")
print("[probe] theme font size ", theme.default_font_size, " types ", theme.get_type_list(), " panel ", theme.get_stylebox("panel", "PanelContainer").bg_color, " normal ", theme.get_stylebox("normal", "Button").bg_color, " hover ", theme.get_stylebox("hover", "Button").bg_color, " pressed ", theme.get_stylebox("pressed", "Button").bg_color, " radius ", theme.get_stylebox("normal", "Button").corner_radius_top_left)
'''),
    close_bottom_panel(),
    # The script.
    save_code(SCRIPT, PAUSE_PANEL),
    *build('l55_built'),
    # The scene.
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l55_new_scene'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'User Interface'}},
    {'op': 'wait', 'frames': 40},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] root ", root.name, " ", root.get_class())
root.name = "PausePanel"
'''),
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    inspector_set('anchors_preset', '15'),
    *quick_load('theme', 'theme.tres'),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'PausePanel.cs'),
    {'op': 'wait', 'frames': 40},
    *add_node('CenterContainer', 'Center'),
    inspector_set('layout_mode', '1'),
    inspector_set('anchors_preset', '15'),
    *add_node('PanelContainer', 'Panel', 'Center'),
    *add_node('VBoxContainer', 'Box', 'Center/Panel'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    inspector_set('theme_override_constants/separation', '12'),
    *add_node('Label', 'Title', 'Center/Panel/Box'),
    inspector_set('text', '"Paused"'),
    inspector_set('horizontal_alignment', '1'),
    *add_node('Label', 'TimeLabel', 'Center/Panel/Box'),
    inspector_set('text', '"Time of day"'),
    *add_node('HSlider', 'TimeSlider', 'Center/Panel/Box'),
    inspector_set('max_value', '1.0'),
    inspector_set('step', '0.001'),
    inspector_set('value', '0.5'),
    inspector_set('custom_minimum_size', 'Vector2(280, 24)'),
    *add_node('CheckButton', 'VsyncToggle', 'Center/Panel/Box'),
    inspector_set('text', '"VSync"'),
    inspector_set('button_pressed', 'true'),
    *add_node('CheckButton', 'ShadowsToggle', 'Center/Panel/Box'),
    inspector_set('text', '"Shadows"'),
    inspector_set('button_pressed', 'true'),
    *add_node('Button', 'ResumeButton', 'Center/Panel/Box'),
    inspector_set('text', '"Resume"'),
    make_unique('TimeSlider', 'VsyncToggle', 'ShadowsToggle', 'ResumeButton'),
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': '.'},
    {'op': 'main_screen', 'name': '2D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'capture', 'name': 'l55_panel_scene', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://ui"
		window.current_file = "pause_panel.tscn"
		return ""
return "no Save Scene dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l55_save_scene', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 60},
    eval_('''
var root := editor.get_edited_scene_root()
var out := []
for node in root.find_children("*", "", true, false):
	out.append("%s %s" % [root.get_path_to(node), node.get_class()])
print("[probe] panel scene ", root.scene_file_path, " anchors ", root.anchor_right, " ", root.anchor_bottom, " nodes ", out)
print("[probe] unique ", root.get_node("%TimeSlider").get_path(), " ", root.get_node("%ResumeButton").get_path())
'''),
    # The panel in the world environment, so every level has it.
    click_tab('Scene'),
    {'op': 'open', 'path': ENVIRONMENT},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *instantiate_under('.', 'pause_panel.tscn', capture='l55_select_scene'),
    {'op': 'select', 'path': 'PausePanel'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    *assign_node('Clock', 'Day', 'l55_assign_clock'),
    *assign_node('Sun', 'Sun'),
    {'op': 'capture', 'name': 'l55_exports', 'frames': 20},
    eval_('''
var panel := editor.get_edited_scene_root().get_node("PausePanel")
print("[probe] exports clock ", panel.get("Clock"), " sun ", panel.get("Sun"))
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The meadow.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(game, 100),
]
write(sys.argv[2], steps)
