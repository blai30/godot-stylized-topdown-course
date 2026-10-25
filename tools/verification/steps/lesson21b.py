# Lesson 21, part 2: the day. An AnimationPlayer with a `day` animation of one minute. The ambient energy is keyed by hand
# in the Animation panel; BuildDay, a tool script, adds the other tracks from tables, and the game plays the day.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, add_node, save_code, build, new_script,
                   run_tool_script, game_steps, play, close_bottom_panel, dump_windows)
from lesson21_pieces import BUILD_DAY

SCENE = 'res://world/environment/world_environment.tscn'
SCRIPT = 'res://src/Tools/BuildDay.cs'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
# The ambient energy keys, in seconds of the 60-second day, from the Meridian table.
# The daytime value goes first: keying a property makes a RESET animation that holds its value then, and saving restores it.
AMBIENT = [(16.2, 0.65), (0, 1.5), (7.2, 1.5), (9, 1.0), (12, 1.0), (43.8, 0.65), (48, 1.1), (51, 1.0), (60, 1.5)]
GAME_TIMES = [0, 7.2, 9, 12, 16.2, 30, 43.8, 48, 51, 55]
PLAYER = 'Meadow/WorldEnvironment/Day'


def animation_menu(item):
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "AnimationPlayerEditor")
for button in plugin._collect(panel, "MenuButton", "Animation"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i).begins_with("{item}"):
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no {item} in the Animation menu"
''')


def seek(time):
    return eval_(f'''
var player := editor.get_edited_scene_root().get_node("Day") as AnimationPlayer
player.seek({time}, true)
''')


def panel_time(time):
    # Types a time into the Animation panel's position box, as the reader does.
    return eval_(f'''
var panel = plugin._find_class(plugin.get_tree().root, "AnimationPlayerEditor")
for spin in plugin._collect(panel, "SpinBox", ""):
	if spin.tooltip_text.begins_with("Animation position"):
		spin.value = {time}
		print("[probe] panel time ", spin.value)
		return ""
return "no position box"
''')


def open_environment():
    return eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "environment")
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
plugin._collect(picker, "Button", "")[0].pressed.emit()
for attempt in 20:
	await plugin.get_tree().process_frame
	for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
		section.unfold()
	if plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "background_mode") != null:
		return ""
return "the Environment did not open"
''')


KEY_AMBIENT = eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "background_energy_multiplier")
if row == null:
	return "no row background_energy_multiplier"
row.emit_signal("property_keyed", "background_energy_multiplier", false)
for attempt in 30:
	await plugin.get_tree().process_frame
	for window in plugin._windows(plugin.get_tree().root):
		if window.visible and window is ConfirmationDialog:
			for label in plugin._collect(window, "Label", ""):
				print("[probe] key dialog: ", label.text)
			window.get_ok_button().pressed.emit()
			return ""
''')

PROBE_TRACKS = eval_('''
var player := editor.get_edited_scene_root().get_node("Day") as AnimationPlayer
var animation := player.get_animation("day")
print("[probe] day length ", animation.length, " loop ", animation.loop_mode, " tracks ", animation.get_track_count())
for i in animation.get_track_count():
	print("[probe] track ", animation.track_get_path(i), " keys ", animation.track_get_key_count(i))
''')


def read_at(label, time):
    return [seek(time), {'op': 'wait', 'frames': 20}, eval_(f'''
var root := editor.get_edited_scene_root() as WorldEnvironment
var sun := root.get_node("Sun") as DirectionalLight3D
var material := (root.get_node("Grade/Screen") as ColorRect).material as ShaderMaterial
var environment := root.environment
print("[probe] {label} t={time} sun ", sun.light_color.to_html(false), " ", snappedf(sun.light_energy, 0.001), " ", sun.rotation_degrees.snapped(Vector3.ONE * 0.1),
		" ambient ", snappedf(environment.background_energy_multiplier, 0.001), " fog ", environment.fog_light_color.to_html(false),
		" saturation ", snappedf(environment.adjustment_saturation, 0.001), " glow ", snappedf(environment.glow_intensity, 0.001),
		" zenith ", (environment.sky.sky_material as ShaderMaterial).get_shader_parameter("zenith_color").to_html(false),
		" grade ", material.get_shader_parameter("shadow_tint").to_html(false), " ", snappedf(material.get_shader_parameter("strength"), 0.001))
''')]


def game(name, times):
    steps = [{'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
             {'op': 'eval', 'code': f'var player := tree.root.get_node("{PLAYER}") as AnimationPlayer\nprint("[game] autoplay ", player.current_animation, " playing ", player.is_playing())\nplayer.pause()'}]
    for time in times:
        steps += [{'op': 'eval', 'code': f'var player := tree.root.get_node("{PLAYER}") as AnimationPlayer\nplayer.seek({time}, true)'},
                  {'op': 'wait', 'frames': 40},
                  {'op': 'capture', 'name': f'{name}_{int(round(time * 10)):03d}', 'frames': 10}]
    return game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', f'game-{name}.jsonl'), steps + [{'op': 'quit'}])


steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': SCENE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': '.'},
    *add_node('AnimationPlayer', 'Day'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l21_animation_panel', 'frames': 20},
    animation_menu('New...'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l21_new_animation', 'window': 'Create New Animation'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "day"
		edit.text_changed.emit("day")
		window.get_ok_button().pressed.emit()
		return ""
return "no new animation dialog"
'''),
    {'op': 'wait', 'frames': 40},
    animation_menu('Open in Inspector'),
    {'op': 'wait', 'frames': 40},
    unfold_inspector(),
    inspector_set('length', '60'),
    inspector_set('loop_mode', '1'),
    {'op': 'wait', 'frames': 20},
    show_row('loop_mode'),
    {'op': 'capture', 'name': 'l21_animation_rows', 'frames': 20},
    # Adjustments on, so the environment's saturation can be keyed.
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    open_environment(),
    eval_('''
var root := editor.get_edited_scene_root() as WorldEnvironment
root.environment.adjustment_enabled = true
root.environment.notify_property_list_changed()
'''),
    {'op': 'wait', 'frames': 40},
]
# The ambient energy, keyed by hand.
for time, value in AMBIENT:
    steps += [panel_time(time), {'op': 'wait', 'frames': 10}, inspector_set('background_energy_multiplier', str(value)),
              {'op': 'wait', 'frames': 10}, KEY_AMBIENT, {'op': 'wait', 'frames': 20}]
steps += [
    show_row('background_energy_multiplier'),
    {'op': 'capture', 'name': 'l21_ambient_keyed', 'frames': 20},
    PROBE_TRACKS,
    # The other tracks, from the tables.
    *new_script(SCRIPT, 'EditorScript', 'l21_new_script'),
    save_code(SCRIPT, BUILD_DAY),
    *build(),
    *run_tool_script(SCRIPT),
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    PROBE_TRACKS,
    *read_at('pre-dawn', 7.2),
    *read_at('midnight', 0),
    *read_at('early morning', 12),
    *read_at('noon', 30),
    *read_at('late sunset', 48),
    *read_at('sunset', 51),
    *read_at('before wrap', 59.99),
    # Autoplay, and back to noon so the scene is saved at noon.
    {'op': 'press', 'find': {'class': 'AnimationPlayerEditor', 'type': 'Button', 'text': 'tooltip:Autoplay on Load'}},
    panel_time(30),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l21_panel_noon', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    eval_('''
var scene = load("res://world/environment/world_environment.tscn").instantiate()
print("[probe] autoplay ", scene.get_node("Day").autoplay, " saved ambient ", scene.environment.background_energy_multiplier, " sun ", scene.get_node("Sun").light_energy, " glow ", scene.environment.glow_intensity)
'''),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(game('l21_day', GAME_TIMES), 60),
]
write(sys.argv[2], steps)
