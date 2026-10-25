# Lesson 19: the environment. A world_environment.tscn scene whose WorldEnvironment holds a sky from a small sky shader,
# ambient and reflected light from that sky, AgX, exponential fog, a soft-light glow, and SSAO. The meadow instances it
# in place of the plain WorldEnvironment lesson 3 added.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, new_resource, open_resource, make_folder,
                   open_in_file_dialog, type_shader, instantiate_under, press_delete_in_scene_dock, game_steps, play,
                   view, close_bottom_panel, INSPECTOR)

PIECES = ['''shader_type sky;

// The sky straight up, and at the horizon.
uniform vec3 zenith_color : source_color = vec3(0.31, 0.66, 1.0);
uniform vec3 horizon_color : source_color = vec3(0.56, 0.78, 1.0);
// How much darker the sky gets looking down from the horizon.
uniform float ground_darkening : hint_range(0.0, 1.0) = 0.5;

void sky() {
	// 0 at the horizon and 1 straight up. EYEDIR is the direction this point of the sky is seen in.
	float height = clamp(EYEDIR.y, 0.0, 1.0);
	COLOR = mix(horizon_color, zenith_color, height);
	// Below the horizon the same color fades toward darker.
	COLOR *= 1.0 - ground_darkening * clamp(-EYEDIR.y, 0.0, 1.0);
}
''']
SKY_SHADER = PIECES[0]
SHADER = 'res://world/environment/sky.gdshader'
SCENE = 'res://world/environment/world_environment.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}


CLOSE_BOTTOM_PANEL = close_bottom_panel()


def enable(group):
    # A group's On checkbox sits in its header, not in a row of its own, so it is set on the Environment itself.
    return eval_(f'''
var node := editor.get_edited_scene_root() as WorldEnvironment
node.environment.set("{group}_enabled", true)
node.environment.notify_property_list_changed()
if not node.environment.get("{group}_enabled"):
	return "{group} is not enabled"
''')


def set_all(*pairs):
    return [enable(name[:-8]) if name.endswith('_enabled') else inspector_set(name, value) for name, value in pairs]


ROCKS = ('Rocks/RockSmall', 'Rocks/RockLarge')


def meadow_view(name, *paths):
    # The meadow in the editor's 3D view, framed on some nodes, after the environment scene was saved.
    return [
        {'op': 'open', 'path': 'res://levels/meadow.tscn'},
        {'op': 'main_screen', 'name': '3D'},
        {'op': 'wait', 'frames': 60},
        CLOSE_BOTTOM_PANEL,
        {'op': 'wait', 'frames': 20},
        *view(*(paths or ROCKS)),
        {'op': 'wait', 'frames': 60},
        {'op': 'capture', 'name': name, 'frames': 40},
    ]


def change(rows, name, *pairs):
    # Edits the environment scene's rows, captures the Inspector scrolled to a row, and saves the scene.
    return [*edit_environment(), *set_all(*pairs), {'op': 'wait', 'frames': 60}, show_row(rows), {'op': 'wait', 'frames': 30},
            {'op': 'capture', 'name': name, 'frames': 20}, SAVE_SCENE, {'op': 'wait', 'frames': 40}]


def edit_environment():
    return [{'op': 'open', 'path': SCENE}, {'op': 'wait', 'frames': 30}, {'op': 'select', 'path': '.'}, unfold_inspector(),
            {'op': 'wait', 'frames': 20}]


def open_environment():
    # Clicks the Environment's picture, then unfolds its sections: their rows only exist once a section is open.
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


def read_back(label):
    return eval_(f'''
var environment := (load("{SCENE}").instantiate() as WorldEnvironment).environment
var out := []
for name in ["background_mode", "background_energy_multiplier", "ambient_light_source", "ambient_light_sky_contribution",
		"reflected_light_source", "tonemap_mode", "tonemap_exposure", "ssao_enabled", "ssao_radius", "ssao_intensity",
		"ssao_power", "ssao_detail", "glow_enabled", "glow_blend_mode", "glow_intensity", "glow_bloom", "glow_hdr_threshold",
		"fog_enabled", "fog_mode", "fog_light_color", "fog_density", "fog_aerial_perspective", "fog_sky_affect",
		"fog_sun_scatter"]:
	out.append("%s=%s" % [name, environment.get(name)])
print("[probe] {label} ", ", ".join(out))
print("[probe] sky ", environment.sky, " radiance ", environment.sky.radiance_size if environment.sky else "none", " material ",
		environment.sky.sky_material if environment.sky else "none")
''')


game_before = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l19-before.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 8},
    {'op': 'capture', 'name': 'l19_game_before', 'frames': 10},
    {'op': 'quit'},
])
game_fog = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l19-fog.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 8},
    {'op': 'capture', 'name': 'l19_game_fog_default', 'frames': 10},
    {'op': 'quit'},
])
game_after = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l19-after.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 8},
    {'op': 'capture', 'name': 'l19_game_after', 'frames': 10},
    {'op': 'wheel', 'steps': 4},
    {'op': 'capture', 'name': 'l19_game_close', 'frames': 10},
    {'op': 'quit'},
])

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(game_before, 20),
    *make_folder('world', 'environment'),
    # The scene: Scene > New Scene, Other Node, WorldEnvironment.
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'Other Node'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'set_text', 'find': {'window': 'Create New Node', 'type': 'LineEdit', 'nth': 0}, 'text': 'WorldEnvironment'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l19_create_root', 'window': 'Create New Node'},
    {'op': 'press', 'find': {'window': 'Create New Node', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 30},
    eval_('print("[probe] root ", editor.get_edited_scene_root().name, " ", editor.get_edited_scene_root().get_class())'),
    {'op': 'select', 'path': '.'},
    {'op': 'capture', 'name': 'l19_root', 'frames': 20},
    # Godot gave the new node an Environment; open it.
    open_environment(),
    {'op': 'capture', 'name': 'l19_new_environment', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    open_in_file_dialog('world', 'environment'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l19_save_scene', 'window': 'Save Scene'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		print("[probe] save file name ", window.current_file)
		window.get_ok_button().pressed.emit()
		return ""
return "no Save Scene dialog"
'''),
    {'op': 'wait', 'frames': 40},
    # The meadow takes the new scene in place of its own WorldEnvironment.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'WorldEnvironment'},
    press_delete_in_scene_dock(),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l19_delete_confirm', 'window': 'class:ConfirmationDialog'},
    {'op': 'press', 'find': {'type': 'Button', 'text': 'Delete'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
if editor.get_edited_scene_root().get_node_or_null("WorldEnvironment"):
	return "the old WorldEnvironment is still there"
'''),
    *instantiate_under('.', 'world_environment', capture='l19_instantiate'),
    eval_('''
var node := editor.get_edited_scene_root().get_node_or_null("WorldEnvironment")
if node == null:
	return "no WorldEnvironment instance"
print("[probe] instance ", node.scene_file_path)
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    *meadow_view('l19_empty'),
    # The sky: background mode Sky, a new Sky, a ShaderMaterial, a new sky shader.
    *edit_environment(),
    inspector_set('background_mode', '2'),
    {'op': 'wait', 'frames': 20},
    *new_resource('sky', 'Sky'),
    open_resource('sky', 'sky_material'),
    {'op': 'wait', 'frames': 20},
    *new_resource('sky_material', 'ShaderMaterial', nth=-1),
    open_resource('sky_material', 'shader'),
    show_row('shader'),
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'shader', 'type': 'Button', 'nth': 0}},
    {'op': 'wait', 'frames': 20},
    {'op': 'popup', 'text': 'New Shader...'},
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Create Shader":
		for option in plugin._collect(window, "OptionButton", ""):
			var items := []
			for i in option.item_count:
				items.append(option.get_item_text(i))
			print("[probe] create shader options ", items, " selected ", option.get_item_text(option.selected))
			if "Sky" in items:
				option.select(items.find("Sky"))
				option.item_selected.emit(items.find("Sky"))
				return ""
return "no Mode option with Sky"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'set_text', 'find': {'window': 'Create Shader', 'type': 'LineEdit', 'nth': 0}, 'text': SHADER},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l19_create_shader', 'window': 'Create Shader'},
    {'op': 'press', 'find': {'window': 'Create Shader', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    *type_shader(SKY_SHADER, SHADER),
    {'op': 'capture', 'name': 'l19_shader_editor', 'frames': 20},
    CLOSE_BOTTOM_PANEL,
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    show_row('shader_parameter/zenith_color'),
    {'op': 'capture', 'name': 'l19_sky_parameters', 'frames': 30},
    open_resource('sky', 'radiance_size'),
    inspector_set('radiance_size', '2'),
    {'op': 'wait', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *meadow_view('l19_sky'),
    # Ambient and reflected light from the sky, dimmed to 0.65.
    *change('reflected_light_source', 'l19_ambient_rows', ('ambient_light_source', '3'), ('background_energy_multiplier', '0.65'), ('reflected_light_source', '2')),
    *meadow_view('l19_ambient'),
    # AgX.
    *change('tonemap_agx_contrast', 'l19_tonemap_rows', ('tonemap_mode', '4')),
    *meadow_view('l19_tonemap'),
    # SSAO, shown close to a rock before and after.
    *meadow_view('l19_ssao_off', 'Rocks/RockLarge'),
    *change('ssao_sharpness', 'l19_ssao_rows', ('ssao_enabled', 'true'), ('ssao_radius', '1.5'), ('ssao_intensity', '1.0'), ('ssao_power', '1.0'),
            ('ssao_detail', '0.0')),
    *meadow_view('l19_ssao_on', 'Rocks/RockLarge'),
    # Glow.
    *change('glow_hdr_threshold', 'l19_glow_rows', ('glow_enabled', 'true'), ('glow_blend_mode', '2'), ('glow_intensity', '0.45'), ('glow_bloom', '0.05'),
            ('glow_hdr_threshold', '0.9')),
    # Fog: first Godot's own density, which buries the meadow, then the one that fits this camera.
    *change('fog_sun_scatter', 'l19_fog_rows', ('fog_enabled', 'true'), ('fog_light_color', 'Color("#B8DBFF")'), ('fog_aerial_perspective', '0.5'),
            ('fog_sky_affect', '0.0'), ('fog_sun_scatter', '0.15')),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(game_fog, 20),
    *change('fog_density', 'l19_fog_density_rows', ('fog_density', '0.0006')),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(game_after, 20),
    read_back('final'),
    eval_('print("[probe] saved scene\\n", FileAccess.get_file_as_string("%s"))' % SCENE),
]

write(sys.argv[2], steps)
