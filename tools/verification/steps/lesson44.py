# Lesson 44, in Godot: the bank kit arrives. The glb imported as a Mesh Library, the bank shader and its material, the material
# swapped in for the glb's own, and a 3 by 3 pond in the meadow edged by the pieces placed by hand.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, unfold_inspector, game_steps, play, quick_load, resource_menu, open_resource, new_resource,
                   inspector_set, click_tab, click_file, import_set, show_import_row, REIMPORT, type_shader, show_row)
from shader_ui import new_shader_file
from lesson44_pieces import BANK, PIECES
from bonemap_ui import ADVANCED, select_node
from steps import open_advanced, add_node, view, build, save_code

GLB = 'res://art/water/bank_kit.glb'
SHADER = 'res://art/shaders/bank.gdshader'
MATERIAL = 'bank.tres'
STOP = os.environ.get('LESSON44_STOP', '')
MEADOW = 'res://levels/meadow.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'

# The pond: 3 by 3 ground cells, taken out of the ground. A bank cell sits on a corner of the ground grid, so 4 by 4 of them
# surround it, and 12 of them hold a piece. Each is (x, z, piece, quarter turns): the pieces' rotation was found by turning
# each piece until the water it faces lies on the right cells (lesson 47 writes this as a table the code reads).
POND = [(x, z) for x in range(-2, 1) for z in range(-4, -1)]
BANK_CELLS = [(-2, -4, 'bank_water_corner_a', 0), (-2, -3, 'bank_straight_a', 1), (-2, -2, 'bank_straight_b', 1),
              (-2, -1, 'bank_water_corner_a', 1), (-1, -4, 'bank_straight_c', 0), (-1, -1, 'bank_straight_a', 2),
              (0, -4, 'bank_straight_b', 0), (0, -1, 'bank_straight_c', 2), (1, -4, 'bank_water_corner_a', 3),
              (1, -3, 'bank_straight_c', 3), (1, -2, 'bank_straight_b', 3), (1, -1, 'bank_water_corner_a', 2)]
out_dir = os.path.dirname(sys.argv[2])

# The Inspector's resource options menu > New Resource..., the type searched, and Create.
NEW_RESOURCE = [
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for menu in plugin._collect(dock, "MenuButton", ""):
	if menu.tooltip_text.begins_with("Extra resource"):
		var popup: PopupMenu = menu.get_popup()
		for i in popup.item_count:
			if popup.get_item_text(i) == "New Resource":
				popup.id_pressed.emit(popup.get_item_id(i))
				return ""
return "no New Resource item"
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "CreateDialog":
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "ShaderMaterial"
		edit.text_changed.emit(edit.text)
		return ""
return "no Create New Resource dialog"
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l44_new_resource', 'window': 'class:CreateDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "CreateDialog":
		window.get_ok_button().pressed.emit()
		return ""
return "no Create New Resource dialog"
'''),
    {'op': 'wait', 'frames': 40},
]


def save_resource_as(path):
    # The Inspector's resource options menu > Save Resource As..., the folder and name typed.
    folder, name = os.path.split(path)
    return [
        eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for menu in plugin._collect(dock, "MenuButton", ""):
	if menu.tooltip_text.begins_with("Extra resource"):
		var popup: PopupMenu = menu.get_popup()
		for i in popup.item_count:
			if popup.get_item_text(i) == "Save Resource As...":
				popup.id_pressed.emit(popup.get_item_id(i))
				return ""
return "no Save Resource As item"
'''),
        {'op': 'wait', 'frames': 30},
        eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "{folder}"
		window.current_file = "{name}"
		return ""
return "no Save Resource dialog"
'''),
        {'op': 'wait', 'frames': 20},
        {'op': 'capture', 'name': 'l44_save_material', 'window': 'class:EditorFileDialog'},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
        {'op': 'wait', 'frames': 40},
    ]



def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def look(name, x, z, size, time=0.5):
    # The camera follows the player, so the hidden player stands on the spot.
    return [{'op': 'eval', 'code': f'var player := tree.root.get_node("Meadow/Player")\nplayer.global_position = Vector3({x}, 0.0, {z})\nplayer.visible = false'},
            {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'},
            zoom(size), {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'l44_{name}', 'frames': 10}]


game = game_steps(os.path.join(out_dir, 'game-l44.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *look('pond', -0.25, -1.25, 6.0), *look('pond_close', -0.25, -1.25, 3.2), *look('pond_wall', -0.25, -1.9, 1.4),
    *look('pond_dusk', -0.25, -1.25, 3.2, 0.78), *look('pond_night', -0.25, -1.25, 3.2, 0.0),
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    # The glb is imported as a Mesh Library, with the nodes' names for its items and no LODs.
    {'op': 'fs', 'path': GLB},
    *click_file('bank_kit.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l44_import_scene'},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for button in plugin._collect(dock, "OptionButton", ""):
	if button.get_item_text(1) == "Mesh Library":
		button.select(1)
		button.item_selected.emit(1)
'''),
    {'op': 'wait', 'frames': 40},
    import_set('mesh_library/use_node_names_as_mesh_names', 'true'),
    import_set('meshes/generate_lods', 'false'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l44_import_library'},
    REIMPORT,
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'sleep', 'seconds': 6},
    eval_(f'''
var library = load("{GLB}")
var names := []
for id in library.get_item_list():
	names.append(library.get_item_name(id))
names.sort()
print("[probe] library ", library.get_class(), " items ", names)
'''),
    # The bank shader.
    *new_shader_file('New Shader...', SHADER, 'l44_create_shader'),
    *type_shader(BANK, SHADER),
    {'op': 'capture', 'name': 'l44_shader', 'frames': 20},
    # The material: a new ShaderMaterial in the Inspector, the shader, the ground's textures, and two noise textures.
    *NEW_RESOURCE,
    unfold_inspector(),
    *quick_load('shader', 'bank.gdshader'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    # The ground's own textures and tint, so the top of a piece is the ground's color.
    *quick_load('shader_parameter/albedo_texture', 'grass_detail.png'),
    *quick_load('shader_parameter/edge_noise', 'edge_noise.tres'),
    inspector_set('shader_parameter/albedo_tint', 'Color(0.584, 0.8, 0.353)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l44_material_ground'},
    # The clods: one FastNoiseLite, shown by a height texture and a normal-map texture.
    *new_resource('shader_parameter/clod_height', 'NoiseTexture2D'),
    open_resource('shader_parameter/clod_height', 'seamless'),
    inspector_set('width', '256'),
    inspector_set('height', '256'),
    inspector_set('seamless', 'true'),
    resource_menu('noise', 'FastNoiseLite'),
    {'op': 'wait', 'frames': 30},
    open_resource('noise', 'frequency'),
    inspector_set('noise_type', '1'),
    inspector_set('frequency', '0.03'),
    inspector_set('fractal_octaves', '3'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l44_clod_noise'},
    # The noise as a file of its own, so the normal map can share it.
    resource_menu('noise', 'Save As...'),
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/water"
		window.current_file = "clod_noise.tres"
		return ""
return "no Save Resource dialog"
'''),
    {'op': 'capture', 'name': 'l44_save_noise', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    *new_resource('shader_parameter/clod_normals', 'NoiseTexture2D'),
    open_resource('shader_parameter/clod_normals', 'as_normal_map'),
    inspector_set('as_normal_map', 'true'),
    inspector_set('bump_strength', '5.0'),
    inspector_set('width', '256'),
    inspector_set('height', '256'),
    inspector_set('seamless', 'true'),
    *quick_load('noise', 'clod_noise.tres'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l44_clod_normals'},
    *save_resource_as('res://art/water/' + MATERIAL),
    eval_(f'''
var material = load("res://art/water/{MATERIAL}")
print("[probe] material ", material.get_class(), " shader ", material.shader.resource_path, " params ", material.get_shader_parameter("albedo_tint"), " ", material.get_shader_parameter("clod_height"), " ", material.get_shader_parameter("clod_normals"), " ", material.get_shader_parameter("edge_noise"))
var normals: NoiseTexture2D = material.get_shader_parameter("clod_normals")
var height: NoiseTexture2D = material.get_shader_parameter("clod_height")
print("[probe] clods ", normals.as_normal_map, " ", normals.noise == height.noise, " ", height.noise.resource_path, " ", height.noise.noise_type, " ", height.noise.frequency, " ", height.noise.fractal_octaves, " ", height.seamless)
'''),
    # Advanced Import Settings > Materials > bank_earth > Use External: the glb's own material is replaced by bank.tres.
    {'op': 'fs', 'path': GLB},
    *click_file('bank_kit.glb'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 40},
    open_advanced(),
    {'op': 'wait', 'frames': 40},
    eval_(ADVANCED + '''
for tabs in plugin._collect(advanced, "TabBar", ""):
	for i in tabs.tab_count:
		if tabs.get_tab_title(i) == "Materials":
			tabs.current_tab = i
			tabs.tab_changed.emit(i)
for i in 6:
	await plugin.get_tree().process_frame
'''),
    select_node('bank_earth'),
    {'op': 'wait', 'frames': 20},
    eval_(ADVANCED + '''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "use_external/enabled":
		row.emit_changed("use_external/enabled", true)
for i in 6:
	await plugin.get_tree().process_frame
for row in plugin._collect(advanced, "EditorProperty", ""):
	print("[probe] row ", row.label, " ", row.get_edited_property())
'''),
    {'op': 'capture', 'name': 'l44_use_external', 'window': 'Advanced'},
    eval_(ADVANCED + f'''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "use_external/path":
		row.emit_changed("use_external/path", "res://art/water/{MATERIAL}")
for i in 6:
	await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l44_external_path', 'window': 'Advanced'},
    {'op': 'press', 'find': {'window': 'Advanced', 'type': 'Button', 'text': 'Reimport'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'sleep', 'seconds': 6},
    eval_(f'''
var library: MeshLibrary = load("{GLB}")
var found := []
for id in library.get_item_list():
	var material := library.get_item_mesh(id).surface_get_material(0)
	found.append("%s=%s" % [library.get_item_name(id), material.resource_path if material else "none"])
print("[probe] item materials ", found)
print("[probe] import file ", FileAccess.get_file_as_string("{GLB}.import").split("_subresources")[1].left(200))
'''),
    # The pond in the meadow: nine ground cells erased, a bed under them for now, and a GridMap of bank pieces.
    click_tab('Scene'),
    {'op': 'open', 'path': MEADOW},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    eval_(f'''
var ground: GridMap = editor.get_edited_scene_root().get_node("GroundTiles")
for cell in {[list(c) for c in POND]!r}:
	ground.set_cell_item(Vector3i(cell[0], 0, cell[1]), -1)
print("[probe] ground cells ", ground.get_used_cells().size())
'''),
    *add_node('GridMap', 'Bank'),
    {'op': 'select', 'path': 'Bank'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('mesh_library', 'bank_kit.glb'),
    inspector_set('cell_size', 'Vector3(0.5, 0.5, 0.5)'),
    inspector_set('cell_center_y', 'false'),
    inspector_set('position', 'Vector3(-0.25, 0.0, -0.25)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l44_bank_node'},
    eval_(f'''
var bank: GridMap = editor.get_edited_scene_root().get_node("Bank")
for cell in {[list(c) for c in BANK_CELLS]!r}:
	var item := bank.mesh_library.find_item_by_name(cell[2])
	var orientation := bank.get_orthogonal_index_from_basis(Basis(Vector3.UP, cell[3] * PI / 2.0))
	bank.set_cell_item(Vector3i(cell[0], 0, cell[1]), item, orientation)
print("[probe] bank cells ", bank.get_used_cells().size())
# Each piece's wall foot, turned and placed, must lie inside the pond (x from -1.0 to 0.5, z from -2.0 to -0.5).
var inside := 0
for cell in bank.get_used_cells():
	var mesh: Mesh = bank.mesh_library.get_item_mesh(bank.get_cell_item(cell))
	var basis := bank.get_cell_item_basis(cell)
	var sum := Vector3.ZERO
	var count := 0
	for vertex in mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]:
		if vertex.y < -0.7:
			sum += vertex
			count += 1
	var foot: Vector3 = bank.to_global(bank.map_to_local(cell) + basis * (sum / count))
	if foot.x > -1.0 and foot.x < 0.5 and foot.z > -2.0 and foot.z < -0.5:
		inside += 1
print("[probe] walls inside the pond ", inside, " of ", bank.get_used_cells().size())
'''),
    # A bed under the pond, until the water tile of lesson 45.
    *add_node('MeshInstance3D', 'PondBed'),
    eval_('''
var bed := editor.get_edited_scene_root().get_node("PondBed") as MeshInstance3D
var plane := PlaneMesh.new()
plane.size = Vector2(1.6, 1.6)
var material := StandardMaterial3D.new()
material.albedo_color = Color(0.42, 0.34, 0.24)
material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
plane.material = material
bed.mesh = plane
bed.position = Vector3(-0.25, -0.75, -1.25)
'''),
    {'op': 'select', 'path': 'Grass'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for button in plugin._collect(dock, "Button", ""):
	if str(button.text) == "Scatter":
		editor.get_inspector().ensure_control_visible(button)
		button.pressed.emit()
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		return ""
return "no Scatter button"
'''),
    {'op': 'sleep', 'seconds': 2},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *play(game, 60, capture_output='l44_output'),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
