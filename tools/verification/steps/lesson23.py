# Lesson 23: stylized lighting. A shader include with wrapped diffuse light and a soft rim tinted by two shader globals,
# included by the ground shader and by a new palette shader for the rocks; DayClock sets the globals from keys on the day.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, make_folder, save_code, build, game_steps, play,
                   open_bottom_panel, type_shader, quick_load, resource_menu, open_resource, new_resource, open_in_file_dialog,
                   run_tool_script, close_bottom_panel, INSPECTOR)
from lesson23_pieces import STYLIZED_LIT, PALETTE_LIT, GROUND, DAY_CLOCK, BUILD_DAY

SCENE = 'res://world/environment/world_environment.tscn'
INCLUDE = 'res://art/shaders/stylized_lit.gdshaderinc'
PALETTE_SHADER = 'res://art/palette/palette_lit.gdshader'
GROUND_SHADER = 'res://art/ground/ground.gdshader'
CLOCK_SCRIPT = 'res://src/World/DayClock.cs'
BUILD_SCRIPT = 'res://src/Tools/BuildDay.cs'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
SETTINGS = 'Project Settings'
PIECES = [STYLIZED_LIT, PALETTE_LIT, GROUND, DAY_CLOCK, BUILD_DAY]

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


def game(name, extra):
    return game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', f'game-{name}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
        *extra, {'op': 'quit'}])


def hour(time, name, close=True):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
             {'op': 'wait', 'frames': 40},
             {'op': 'eval', 'code': f'print("[game] {name} rim ", RenderingServer.global_shader_parameter_get("rim_color"), " ", RenderingServer.global_shader_parameter_get("rim_strength"))'},
             {'op': 'capture', 'name': f'l23_{name}', 'frames': 10}]
    return steps


def run_meadow(name, extra):
    return [{'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(game(name, extra), 40)]


def zoomed(time, name):
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            {'op': 'wheel', 'steps': 5}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l23_{name}', 'frames': 10},
            {'op': 'wheel', 'steps': -5}]


def open_shader(path, name):
    return [{'op': 'fs', 'path': path}, {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': name, 'double': True},
            {'op': 'wait', 'frames': 40}]


def rock_material(scene, first):
    steps = [{'op': 'open', 'path': scene}, {'op': 'wait', 'frames': 40}, {'op': 'select', 'path': 'rock_small' if 'small' in scene else 'rock_large'},
             unfold_inspector(), {'op': 'wait', 'frames': 20}]
    if first:
        steps += [
            *new_resource('material_override', 'ShaderMaterial'),
            open_resource('material_override', 'shader'),
            *quick_load('shader', 'palette_lit.gdshader'),
            unfold_inspector(),
            {'op': 'wait', 'frames': 20},
            *quick_load('shader_parameter/palette', 'palette.png'),
            show_row('shader_parameter/palette'),
            {'op': 'capture', 'name': 'l23_rock_material', 'frames': 20},
            resource_menu('material_override', 'Save As...'),
            {'op': 'wait', 'frames': 30},
            open_in_file_dialog('art', 'palette'),
            eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_file = "palette_lit.tres"
		return ""
return "no Save Resource dialog"
'''),
            {'op': 'capture', 'name': 'l23_save_material', 'window': 'class:EditorFileDialog'},
            eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
            {'op': 'wait', 'frames': 40},
        ]
    else:
        steps += quick_load('material_override', 'palette_lit.tres')
    steps += [
        eval_('''
var node := editor.get_edited_scene_root().get_child(0) as MeshInstance3D
print("[probe] override ", node.material_override.resource_path, " shader ", (node.material_override as ShaderMaterial).shader.resource_path)
'''),
        {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
        {'op': 'wait', 'frames': 30},
    ]
    return steps


steps = [
    {'op': 'sleep', 'seconds': 3},
    # Before: dusk and noon, close to the rocks.
    *run_meadow('l23_before', [
        *hour(0.8, 'before_dusk'), *zoomed(0.8, 'before_dusk_close'), *zoomed(0.5, 'before_noon_close')]),
    *make_folder('art', 'shaders'),
    # The two shader globals.
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    select_tab('Globals'),
    {'op': 'wait', 'frames': 30},
    select_tab('Shader Globals'),
    {'op': 'wait', 'frames': 30},
    *add_global('rim_color', 'color'),
    *add_global('rim_strength', 'float'),
    {'op': 'capture', 'name': 'l23_globals', 'window': SETTINGS},
    eval_(FIND_SETTINGS + "\nwindow.hide()"),
    {'op': 'wait', 'frames': 30},
    eval_('''
var names := []
for setting in ProjectSettings.get_property_list():
	if str(setting.name).begins_with("shader_globals/"):
		names.append("%s=%s" % [setting.name, ProjectSettings.get_setting(setting.name)])
print("[probe] shader globals ", names)
'''),
    # The include.
    *new_shader_file('New Shader Include...', INCLUDE, 'l23_create_include'),
    *type_shader(STYLIZED_LIT, INCLUDE),
    {'op': 'capture', 'name': 'l23_include_editor', 'frames': 20},
    # The ground includes it.
    *open_shader(GROUND_SHADER, 'ground.gdshader'),
    *type_shader(GROUND, GROUND_SHADER),
    # A palette shader for the rocks.
    *new_shader_file('New Shader...', PALETTE_SHADER, 'l23_create_palette_shader'),
    *type_shader(PALETTE_LIT, PALETTE_SHADER),
    close_bottom_panel(),
    *rock_material('res://art/nature/rock_small/rock_small.tscn', True),
    *rock_material('res://art/nature/rock_large/rock_large.tscn', False),
    # DayClock takes the rim, and BuildDay keys it.
    save_code(CLOCK_SCRIPT, DAY_CLOCK),
    save_code(BUILD_SCRIPT, BUILD_DAY),
    *build(),
    {'op': 'open', 'path': SCENE},
    {'op': 'wait', 'frames': 40},
    *run_tool_script(BUILD_SCRIPT),
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    eval_('''
var player := editor.get_edited_scene_root().get_node("Day") as AnimationPlayer
var animation := player.get_animation("day")
print("[probe] day tracks ", animation.get_track_count())
for i in animation.get_track_count():
	if str(animation.track_get_path(i)).begins_with("Day:"):
		print("[probe] track ", animation.track_get_path(i), " keys ", animation.track_get_key_count(i))
'''),
    {'op': 'select', 'path': 'Day'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    inspector_set('TimeOfDay', '0.5'),
    {'op': 'wait', 'frames': 30},
    show_row('RimStrength'),
    {'op': 'capture', 'name': 'l23_clock_rim', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # After: the same views.
    *run_meadow('l23_after', [
        *hour(0.2, 'dawn'), *hour(0.5, 'noon'), *hour(0.8, 'dusk'), *hour(0.95, 'night'),
        *zoomed(0.8, 'dusk_close'), *zoomed(0.5, 'noon_close')]),
]
write(sys.argv[2], steps)
