# Lesson 58, in Godot: scaffold the project settings. The boot splash color, the user data folder, the base window size, the
# named physics and render layers; the Player, Terrain, and World layers put to use; a stricter project file; a game run that
# reads every setting back and captures the window at four aspect ratios.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, inspector_set, game_steps, play, click_tab
from lesson58_pieces import EDITORCONFIG, CSPROJ

WINDOW = 'Project Settings'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
out_dir = os.path.dirname(sys.argv[2])
FIND_WINDOW = f'''
var window: Window = null
for candidate in plugin._windows(plugin.get_tree().root):
	if candidate.visible and "{WINDOW}" in candidate.title:
		window = candidate
if window == null:
	return "no {WINDOW} window"
'''

# The Inspector draws a layer picker as blocks of four boxes in two rows, 1 to 4 over 5 to 8, then 9 to 12 over 13 to 16.
PHYSICS_LAYERS = {1: 'World', 2: 'Terrain', 3: 'Hazard', 4: 'Interactable', 5: 'Player', 6: 'Enemy', 7: 'Npc', 8: 'Destructible',
                  9: 'Hurtbox', 10: 'Projectile', 11: 'Pickup', 12: 'Sensor'}
RENDER_LAYERS = {1: 'World', 2: 'Terrain', 3: 'Foliage', 4: 'Water', 5: 'Characters', 6: 'Effects'}


def section(*path):
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
    return eval_(FIND_WINDOW + f'''
for property in plugin._collect(window, "EditorProperty", ""):
	if str(property.get_edited_property()) == "{name}":
		property.emit_changed(property.get_edited_property(), {value})
		return ""
return "no row {name}"
''')


def advanced(on):
    return eval_(FIND_WINDOW + f'''
plugin._collect(window, "CheckButton", "Advanced Settings")[0].button_pressed = {str(on).lower()}
''')


def layer_names(group, layers):
    steps = [section('Layer Names', group), {'op': 'wait', 'frames': 20}]
    steps += [setting(f'layer_{number}', f'"{name}"') for number, name in layers.items()]
    return steps + [{'op': 'wait', 'frames': 20}]


def row_list(note):
    # Lists the rows the shown section has, so a name that differs in this Godot version shows up in the log.
    return eval_(FIND_WINDOW + f'''
var names := []
for property in plugin._collect(window, "EditorProperty", ""):
	names.append(str(property.get_edited_property()))
print("[probe] {note} rows: ", names)
''')


def scroll_to(name):
    return eval_(FIND_WINDOW + f'''
for property in plugin._collect(window, "EditorProperty", ""):
	if str(property.get_edited_property()) == "{name}":
		var scroll: Node = property.get_parent()
		while not scroll is ScrollContainer:
			scroll = scroll.get_parent()
		(scroll as ScrollContainer).ensure_control_visible(property)
		return ""
return "no row {name}"
''')


def layer_popup(prop, name):
    # The picker is drawn in the Inspector as a grid of numbered boxes; the row is scrolled into view and captured.
    return [inspector_set_visible(prop), {'op': 'wait', 'frames': 20}, {'op': 'capture', 'name': name}]


def inspector_set_visible(prop):
    return eval_(f'''
for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
	section.unfold()
await plugin.get_tree().process_frame
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{prop}")
if row == null:
	return "no row {prop}"
editor.get_inspector().ensure_control_visible(row)
''')


STATE = '''
var settings := {
	"splash": ProjectSettings.get_setting("application/boot_splash/bg_color"),
	"user_dir": ProjectSettings.get_setting("application/config/use_custom_user_dir"),
	"user_dir_name": ProjectSettings.get_setting("application/config/custom_user_dir_name"),
	"viewport": [ProjectSettings.get_setting("display/window/size/viewport_width"), ProjectSettings.get_setting("display/window/size/viewport_height")],
	"stretch": [ProjectSettings.get_setting("display/window/stretch/mode"), ProjectSettings.get_setting("display/window/stretch/aspect")],
	"physics": ProjectSettings.get_setting("physics/3d/physics_engine"),
	"interpolation": ProjectSettings.get_setting("physics/common/physics_interpolation"),
	"user_data": OS.get_user_data_dir(),
}
print("[game] settings ", settings)
for number in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
	print("[game] physics layer ", number, " ", ProjectSettings.get_setting("layer_names/3d_physics/layer_%d" % number))
for number in [1, 2, 3, 4, 5, 6]:
	print("[game] render layer ", number, " ", ProjectSettings.get_setting("layer_names/3d_render/layer_%d" % number))
var player := tree.root.find_child("Player", true, false) as CharacterBody3D
print("[game] player layer ", player.collision_layer, " mask ", player.collision_mask, " y ", player.global_position.y)
for map in tree.root.find_children("*", "GridMap", true, false):
	print("[game] ", map.name, " layer ", map.collision_layer)
var camera := tree.root.find_child("Camera3D", true, false) as Camera3D
print("[game] camera keep_aspect ", camera.keep_aspect, " projection ", camera.projection)
'''


def ratio(name, width, height):
    return [
        {'op': 'eval', 'code': f'tree.root.mode = Window.MODE_WINDOWED\ntree.root.size = Vector2i({width}, {height})'},
        {'op': 'wait', 'frames': 40},
        {'op': 'eval', 'code': f'print("[game] {name}: window ", tree.root.size, " viewport ", tree.root.get_visible_rect().size, " content scale ", tree.root.content_scale_factor)'},
        {'op': 'capture', 'name': f'l58_{name}', 'frames': 10},
    ]


def game(name, scene_root, ratios):
    steps = [{'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 3}, {'op': 'eval', 'code': STATE}]
    for ratio_name, width, height in ratios:
        steps += ratio(f'{name}_{ratio_name}', width, height)
    steps += [
        # The player stands on the ground after the physics has run: it stayed on the Terrain layer's tiles.
        {'op': 'eval', 'code': 'var player := tree.root.find_child("Player", true, false) as CharacterBody3D\nprint("[game] player on floor ", player.is_on_floor(), " y ", player.global_position.y)'},
        {'op': 'quit'},
    ]
    return game_steps(os.path.join(out_dir, f'game-l58_{name}.jsonl'), steps)


RATIOS = [('16x9', 1920, 1080), ('16x10', 1680, 1050), ('21x9', 2560, 1080), ('32x9', 3200, 900)]
meadow = game('meadow', 'Meadow', RATIOS)
generated = game('generated', 'Generated', [('21x9', 2560, 1080)])


def save_file(path, text):
    return eval_(f'''
var file := FileAccess.open("{path}", FileAccess.WRITE)
file.store_string({text!r})
file.close()
''')


steps = [
    {'op': 'sleep', 'seconds': 5},
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    advanced(False),
    {'op': 'wait', 'frames': 30},
    # The boot splash and the user data folder.
    section('Application', 'Boot Splash'),
    {'op': 'wait', 'frames': 20},
    row_list('boot splash'),
    {'op': 'capture', 'name': 'l58_splash_before', 'window': WINDOW},
    setting('bg_color', 'Color("#000000")'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l58_splash', 'window': WINDOW},
    # The user data folder switches are advanced settings.
    advanced(True),
    {'op': 'wait', 'frames': 30},
    section('Application', 'Config'),
    {'op': 'wait', 'frames': 20},
    row_list('config'),
    setting('description', '"A stylized top-down game."'),
    setting('use_custom_user_dir', 'true'),
    setting('custom_user_dir_name', '"YourCompany/TopDownTemplate"'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l58_user_dir', 'window': WINDOW},
    advanced(False),
    {'op': 'wait', 'frames': 30},
    # The window.
    section('Display', 'Window'),
    {'op': 'wait', 'frames': 20},
    setting('size/viewport_width', 1920),
    setting('size/viewport_height', 1080),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l58_window', 'window': WINDOW},
    # Physics: both switches are already on from lesson 3 and the engine from the Project Manager.
    section('Physics', '3D'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l58_physics_3d', 'window': WINDOW},
    # The layers.
    *layer_names('3D Physics', PHYSICS_LAYERS),
    {'op': 'capture', 'name': 'l58_physics_layers', 'window': WINDOW},
    scroll_to('layer_12'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l58_physics_layers_end', 'window': WINDOW},
    *layer_names('3D Render', RENDER_LAYERS),
    {'op': 'capture', 'name': 'l58_render_layers', 'window': WINDOW},
    {'op': 'press', 'find': {'window': WINDOW, 'type': 'Button', 'text': 'Close'}},
    {'op': 'wait', 'frames': 30},
    # The Player stands on the Player layer and looks for the World and the Terrain.
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': '.'},
    {'op': 'wait', 'frames': 20},
    *layer_popup('collision_layer', 'l58_player_layer'),
    inspector_set('collision_layer', 16),
    inspector_set('collision_mask', 3),
    {'op': 'wait', 'frames': 20},
    *layer_popup('collision_layer', 'l58_player_layer_set'),
    *layer_popup('collision_mask', 'l58_player_mask_set'),
    {'op': 'capture', 'name': 'l58_player_collision'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 20},
    {'op': 'menu', 'path': ['Scene', 'Close Scene']},
    {'op': 'wait', 'frames': 30},
]
for level in ('meadow', 'generated'):
    steps += [
        click_tab('Scene'),
        {'op': 'open', 'path': f'res://levels/{level}.tscn'},
        {'op': 'main_screen', 'name': '3D'},
        {'op': 'wait', 'frames': 40},
    ]
    for node in ('GroundTiles', 'Bank'):
        steps += [{'op': 'select', 'path': node}, {'op': 'wait', 'frames': 20}, inspector_set('collision_layer', 2), {'op': 'wait', 'frames': 20}]
        if level == 'meadow' and node == 'GroundTiles':
            steps += [*layer_popup('collision_layer', 'l58_terrain_layer'), {'op': 'capture', 'name': 'l58_ground_tiles'}]
    steps += [{'op': 'select', 'path': '.'}, SAVE_SCENE, {'op': 'wait', 'frames': 20}]
steps += [
    # The project file and the style file.
    save_file('res://TopDownTemplate.csproj', CSPROJ),
    save_file('res://.editorconfig', EDITORCONFIG),
    {'op': 'wait', 'frames': 40},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(meadow, 60),
    {'op': 'open', 'path': 'res://levels/generated.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    eval_('''
OS.set_environment("CAPTURE_GAME_STEPS", %r)
OS.set_environment("CAPTURE_GAME_LOG", %r)
DirAccess.remove_absolute(%r)
editor.play_current_scene()
''' % (generated, generated[:-6] + '.log', generated[:-6] + '.log')),
    {'op': 'sleep', 'seconds': 40},
    eval_('print("[probe] project.godot\\n", FileAccess.get_file_as_string("res://project.godot"))'),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
