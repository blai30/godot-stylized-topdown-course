# Lesson 15: a test tile with a ShaderMaterial, and the ground shader written in four pieces: one color, the grass
# texture by UV, world-space sampling across a second, turned tile, and roughness with comments.
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, new_resource, inspector_set, unfold_inspector, show_row, quick_load,
                   dump_popups, INSPECTOR)

PIECES = [
    '''shader_type spatial;

void fragment() {
	ALBEDO = vec3(0.4, 0.6, 0.2);
}
''',
    '''shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// The ground's color: the texture is multiplied by it, and white leaves the texture as it is.
uniform vec3 albedo_tint : source_color = vec3(1.0);

void fragment() {
	ALBEDO = texture(albedo_texture, UV).rgb * albedo_tint;
}
''',
    '''shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 albedo_tint : source_color = vec3(1.0);
uniform float texture_scale = 0.5;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb * albedo_tint;
}
''',
    '''shader_type spatial;

// The ground textures from lessons 13 and 14.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// The ground's color: the texture is multiplied by it, and white leaves the texture as it is.
uniform vec3 albedo_tint : source_color = vec3(1.0);
// How many times the texture repeats per meter: 0.5 is once every 2 meters.
uniform float texture_scale = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb * albedo_tint;
	ROUGHNESS = roughness;
}
''',
]
TEXTURE = 'shader_parameter/albedo_texture'
# The grass detail averages 0.8 gray, so its tint is the green wanted, divided by 0.8: the palette's light grass swatch,
# 119, 163, 72, becomes 149, 204, 90.
TINT = 'shader_parameter/albedo_tint'
GREEN = 'Color("#95CC5A")'


def frame(*paths, first=False):
    # Frames the tiles with the viewport's Focus and Frame Selection, then clears the selection so no gizmo covers
    # the result. The first time, it also orbits down and zooms in, as the reader looks at the tile.
    return [eval_(f'''
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
'''), {'op': 'wait', 'frames': 30}, *([{'op': 'orbit', 'dy': 120}, {'op': 'wheel', 'steps': 2}] if first else []),
        eval_('editor.get_selection().clear()')]


def type_code(code, name, framed, first=False):
    # The reader types the piece into the Shader Editor and saves it with Ctrl+Alt+S.
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
        # Ctrl+Alt+S in the Shader Editor saves the shader.
        {'op': 'key', 'find': {'type': 'CodeEdit'}, 'key': 'S', 'ctrl': True, 'alt': True},
        {'op': 'wait', 'frames': 60},
        DISK_PROMPT,
        {'op': 'wait', 'frames': 20},
        {'op': 'key', 'find': {'type': 'CodeEdit'}, 'key': 'S', 'ctrl': True, 'alt': True},
        {'op': 'wait', 'frames': 40},
        eval_(f'''
var saved := FileAccess.get_file_as_string("res://art/ground/ground.gdshader")
if saved != {code!r}:
	return "the file on disk is not the typed piece: " + saved.left(120)
'''),
        eval_('''
var tabs := []
for item in plugin._collect(plugin.get_tree().root, "ItemList", ""):
	for i in item.item_count:
		if item.get_item_text(i).contains("ground.gdshader"):
			tabs.append(item.get_item_text(i))
print("[probe] shader list ", tabs)
if tabs.any(func(text): return text.contains("(*)")):
	return "the shader is not saved: " + str(tabs)
'''),
        *frame(*framed, first=first),
        {'op': 'capture', 'name': name, 'frames': 40},
    ]


# The first save of a shader Godot has just created can raise "The following files are newer on disk". The text in
# the Shader Editor is the reader's, so the answer is Ignore external changes, then save again.
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


SAVE_SCENE = {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True}

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
]
# The test tile: a MeshInstance3D named TestTile with a PlaneMesh, lifted 1 cm, with a ShaderMaterial and a new
# shader file.
steps += [
    {'op': 'select', 'path': '.'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Add/Create a New Node'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'set_text', 'find': {'window': 'Create New Node', 'type': 'LineEdit', 'nth': 0}, 'text': 'MeshInstance3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l15_create_node', 'window': 'Create New Node'},
    {'op': 'press', 'find': {'window': 'Create New Node', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var node := editor.get_edited_scene_root().get_node_or_null("MeshInstance3D")
if node == null:
	return "no MeshInstance3D was added"
node.name = "TestTile"
'''),
    {'op': 'select', 'path': 'TestTile'},
    {'op': 'capture', 'name': 'l15_default_box', 'frames': 20},
    unfold_inspector(),
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'mesh', 'type': 'Button', 'nth': -1}},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l15_mesh_menu'},
    {'op': 'popup', 'text': 'PlaneMesh'},
    {'op': 'wait', 'frames': 30},
]
steps += [
    inspector_set('position', 'Vector3(0, 0.01, 0)'),
    {'op': 'wait', 'frames': 20},
]
steps += new_resource('material', 'ShaderMaterial')
steps += [
    show_row('shader'),
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'shader', 'type': 'Button', 'nth': 0}},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l15_shader_menu'},
    {'op': 'popup', 'text': 'New Shader...'},
    {'op': 'wait', 'frames': 30},
    {'op': 'set_text', 'find': {'window': 'Create Shader', 'type': 'LineEdit', 'nth': 0}, 'text': 'res://art/ground/ground.gdshader'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l15_create_shader', 'window': 'Create Shader'},
    {'op': 'press', 'find': {'window': 'Create Shader', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    SAVE_SCENE,
    {'op': 'capture', 'name': 'l15_after_create', 'frames': 20},
]
steps += [eval_('''
var out := []
for button in plugin._collect(plugin.get_tree().root, "MenuButton", ""):
	if button.text in ["File"]:
		var popup: PopupMenu = button.get_popup()
		for i in popup.item_count:
			var shortcut = popup.get_item_shortcut(i)
			out.append(popup.get_item_text(i) + ("" if shortcut == null else " [" + shortcut.get_as_text() + "]"))
print("[probe] shader File menu ", out)
var edits := plugin._collect(plugin.get_tree().root, "CodeEdit", "")
print("[probe] code edits ", edits.size(), " focus owner ", plugin.get_viewport().gui_get_focus_owner())
''')]
steps += type_code(PIECES[0], 'l15_piece1', ['TestTile'], first=True)
steps += type_code(PIECES[1], 'l15_piece2_untextured', ['TestTile'])
# The texture: TestTile's Shader Parameters > Albedo Texture, by Quick Load.
steps += [{'op': 'select', 'path': 'TestTile'}, unfold_inspector(), {'op': 'wait', 'frames': 20}]
steps += [DISK_PROMPT]
steps += quick_load(TEXTURE, 'grass_detail')
steps += [
    inspector_set(TINT, GREEN),
    show_row(TEXTURE),
    {'op': 'capture', 'name': 'l15_shader_parameters', 'frames': 30},
    *frame('TestTile'),
    {'op': 'capture', 'name': 'l15_piece2', 'frames': 40},
]
# The UV problem: duplicate the tile with Ctrl+D, move and turn the copy, and show the Godot logo on both.
steps += [
    {'op': 'select', 'path': 'TestTile'},
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'D', 'ctrl': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
var copy := editor.get_edited_scene_root().get_node_or_null("TestTile2")
if copy == null:
	return "Ctrl+D made no TestTile2"
'''),
    {'op': 'select', 'path': 'TestTile2'},
    inspector_set('position', 'Vector3(1.4, 0.012, 0.6)'),
    inspector_set('rotation', 'Vector3(0, deg_to_rad(30), 0)'),
    {'op': 'select', 'path': 'TestTile'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
]
steps += [DISK_PROMPT]
steps += quick_load(TEXTURE, 'icon.svg')
steps += [SAVE_SCENE, *frame('TestTile', 'TestTile2'), {'op': 'capture', 'name': 'l15_uv_problem', 'frames': 40}]
steps += type_code(PIECES[2], 'l15_piece3', ['TestTile', 'TestTile2'])
steps += [{'op': 'select', 'path': 'TestTile'}, unfold_inspector(), {'op': 'wait', 'frames': 20}]
steps += [DISK_PROMPT]
steps += quick_load(TEXTURE, 'grass_detail')
steps += [*frame('TestTile', 'TestTile2'), {'op': 'capture', 'name': 'l15_piece3_grass', 'frames': 40}]
steps += type_code(PIECES[3], 'l15_piece4', ['TestTile', 'TestTile2'])
steps += [
    SAVE_SCENE,
    {'op': 'select', 'path': 'TestTile'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    show_row(TEXTURE),
    {'op': 'capture', 'name': 'l15_nested_parameters', 'frames': 30},
    eval_('''
var root := editor.get_edited_scene_root()
var tile := root.get_node("TestTile") as MeshInstance3D
var copy := root.get_node("TestTile2") as MeshInstance3D
var material := (tile.mesh as PlaneMesh).material as ShaderMaterial
print("[probe] tile ", tile.position, " copy ", copy.position, " ", copy.rotation_degrees.snapped(Vector3.ONE * 0.1), " same mesh ", copy.mesh == tile.mesh)
print("[probe] texture ", material.get_shader_parameter("albedo_texture").resource_path, " scale ", material.get_shader_parameter("texture_scale"), " tint ", material.get_shader_parameter("albedo_tint").to_html(false))
print("[probe] saved shader:\\n", FileAccess.get_file_as_string("res://art/ground/ground.gdshader"))
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
