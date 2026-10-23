import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

piece1 = '''shader_type spatial;

void fragment() {
	ALBEDO = vec3(0.4, 0.6, 0.2);
}
'''
piece2 = '''shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;

void fragment() {
	ALBEDO = texture(albedo_texture, UV).rgb;
}
'''
piece3 = '''shader_type spatial;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform float texture_scale = 0.5;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb;
}
'''
piece4 = '''shader_type spatial;

// The ground texture you painted in lesson 13.
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
// How many times the texture repeats per meter: 0.5 is once every 2 meters.
uniform float texture_scale = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.9;

varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ALBEDO = texture(albedo_texture, world_position.xz * texture_scale).rgb;
	ROUGHNESS = roughness;
}
'''


def frame(*paths):
    global FIRST
    first, FIRST = FIRST, False
    # Selects the nodes, frames them with the viewport's Focus and Frame Selection, then clears the selection so no
    # gizmo covers the result.
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
'''), {'op': 'wait', 'frames': 30}, *([{'op': 'orbit', 'dy': 120}, {'op': 'wheel', 'steps': 2}] if first else []), eval_('editor.get_selection().clear()')]


def unfold_inspector():
    return eval_('''
for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
	section.unfold()
''')


def type_code(code, name):
    # Puts the code in the shader editor the reader is typing in, saves it through File > Save, and frames the tile.
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
        eval_('''
for button in plugin._collect(plugin.get_tree().root, "MenuButton", "File"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i) == "Save":
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
return "no File > Save"
'''),
        {'op': 'wait', 'frames': 60},
        *frame(*FRAMED),
        {'op': 'capture', 'name': name, 'frames': 40},
    ]

FRAMED = ['TestTile']
FIRST = True
steps = [
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    eval_('''
var out := []
for button in plugin._collect(plugin.get_tree().root, "MenuButton", ""):
	if button.text in ["File", "Edit", "Search", "Go To"]:
		var popup: PopupMenu = button.get_popup()
		var items := []
		for i in popup.item_count:
			var shortcut = popup.get_item_shortcut(i)
			items.append(popup.get_item_text(i) + ("" if shortcut == null else " [" + shortcut.get_as_text() + "]"))
		out.append(button.text + ": " + str(items))
print("[probe] menus\n", "\n".join(out))
var edits := plugin._collect(plugin.get_tree().root, "CodeEdit", "")
print("[probe] code edits visible: ", edits.size())
'''),
]
steps += type_code(piece1, 'l15_piece1')
steps += type_code(piece2, 'l15_piece2_untextured')
steps += [
    eval_('''
var tile := editor.get_edited_scene_root().get_node("TestTile") as MeshInstance3D
var material := (tile.mesh as PlaneMesh).material as ShaderMaterial
material.set_shader_parameter("albedo_texture", load("res://art/ground/grass_albedo.png"))
editor.edit_resource(material)
'''),
    unfold_inspector(),
    {'op': 'capture', 'name': 'l15_shader_parameters', 'frames': 30},
    *frame('TestTile'),
    {'op': 'capture', 'name': 'l15_piece2', 'frames': 40},
    eval_('''
var root := editor.get_edited_scene_root()
var tile := root.get_node("TestTile") as MeshInstance3D
var copy := tile.duplicate() as MeshInstance3D
copy.name = "TestTile2"
copy.position = Vector3(1.4, 0.012, 0.6)
copy.rotation_degrees = Vector3(0, 30, 0)
root.add_child(copy)
copy.owner = root
var material := (tile.mesh as PlaneMesh).material as ShaderMaterial
material.set_shader_parameter("albedo_texture", load("res://icon.svg"))
'''),
    *frame('TestTile', 'TestTile2'),
    {'op': 'capture', 'name': 'l15_uv_problem', 'frames': 40},
]
FRAMED = ['TestTile', 'TestTile2']
steps += type_code(piece3, 'l15_piece3')
steps += [
    eval_('''
var tile := editor.get_edited_scene_root().get_node("TestTile") as MeshInstance3D
((tile.mesh as PlaneMesh).material as ShaderMaterial).set_shader_parameter("albedo_texture", load("res://art/ground/grass_albedo.png"))
'''),
    {'op': 'capture', 'name': 'l15_piece3_grass', 'frames': 40},
]
steps += type_code(piece4, 'l15_piece4')
steps += [
    eval_('''
var tile := editor.get_edited_scene_root().get_node("TestTile") as MeshInstance3D
editor.edit_resource((tile.mesh as PlaneMesh).material)
'''),
    unfold_inspector(),
    {'op': 'capture', 'name': 'l15_final_parameters', 'frames': 30},
    {'op': 'select', 'path': 'TestTile'},
    {'op': 'wait', 'frames': 20},
    eval_('''
var inspector := editor.get_inspector()
for section in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorInspectorSection", ""):
	section.unfold()
await plugin.get_tree().process_frame
var property = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "shader_parameter/albedo_texture")
if property == null:
	return "no albedo texture row under TestTile"
inspector.ensure_control_visible(property)
'''),
    {'op': 'capture', 'name': 'l15_nested_parameters', 'frames': 30},
    eval_('''
editor.save_scene()
print("[probe] saved shader:\n", FileAccess.get_file_as_string("res://art/ground/ground.gdshader"))
'''),
]
write(sys.argv[2], steps)
