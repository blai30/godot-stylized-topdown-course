# Lesson 11: imports the palette and the rock, extracts the shared palette material, generates collision on import,
# makes the rock's inherited scene, and places rocks in the meadow.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (open_advanced, write, eval_, dump_windows, dump_popups, click_tab, click_file, open_in_file_dialog, inspector_set, show_row,
                   option_items, unfold_inspector, INSPECTOR, add_node, view, game_steps, play, DUMP_IMPORT, import_set,
                   show_import_row, REIMPORT, instantiate_under)

steps = [
    {'op': 'sleep', 'seconds': 3},
    # The palette: keep its colors exact when a 3D material uses it.
    {'op': 'fs', 'path': 'res://art/palette/palette.png'},
    *click_file('palette.png'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l11_palette_import_before'},
    show_import_row('detect_3d/compress_to'),
    {'op': 'wait', 'frames': 10},
    {'op': 'capture', 'name': 'l11_palette_detect_before'},
    import_set('detect_3d/compress_to', 0),
    {'op': 'wait', 'frames': 20},
    show_import_row('detect_3d/compress_to'),
    {'op': 'capture', 'name': 'l11_palette_import_set'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 3},
    eval_('''
var cfg := ConfigFile.new()
cfg.load("res://art/palette/palette.png.import")
print("[probe] palette import compress ", cfg.get_value("params", "compress/mode"), " mipmaps ", cfg.get_value("params", "mipmaps/generate"), " detect3d ", cfg.get_value("params", "detect_3d/compress_to"))
'''),
    # The rock: extract its material once into the palette folder.
    {'op': 'fs', 'path': 'res://art/nature/rock_small/rock_small.glb'},
    *click_file('rock_small.glb'),
    {'op': 'wait', 'frames': 30},
    show_import_row('materials/extract'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l11_glb_import_before'},
    import_set('materials/extract', 1),
    # Extract Path: the folder button, then into art and palette, then Select Current Folder.
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "materials/extract_path":
		plugin._collect(row, "Button", "")[0].pressed.emit()
		return ""
return "no Extract Path row"
'''),
    {'op': 'wait', 'frames': 40},
    open_in_file_dialog('art', 'palette'),
    {'op': 'capture', 'name': 'l11_extract_folder', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for button in plugin._collect(window, "Button", "Select Current Folder"):
			button.pressed.emit()
			return ""
return "no Select Current Folder button"
'''),
    {'op': 'wait', 'frames': 30},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	if str(row.get_edited_property()) == "materials/extract_path":
		print("[probe] extract path now ", row.get_edited_object().get("materials/extract_path"))
'''),
    {'op': 'wait', 'frames': 20},
    show_import_row('materials/extract_path'),
    {'op': 'capture', 'name': 'l11_glb_import_set'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 4},
    eval_('''
print("[probe] palette folder ", DirAccess.get_files_at("res://art/palette"))
var material = load("res://art/palette/palette.tres")
if material == null:
	return "no extracted palette material"
print("[probe] extracted ", material.get_class(), " albedo ", material.albedo_color, " texture ", material.albedo_texture, " roughness ", material.roughness, " metallic ", material.metallic, " cull ", material.cull_mode, " filter ", material.texture_filter)
var cfg := ConfigFile.new()
cfg.load("res://art/nature/rock_small/rock_small.glb.import")
print("[probe] glb subresources ", cfg.get_value("params", "_subresources"))
'''),
]
# The shared material: open palette.tres from the FileSystem dock and fix what glTF carried over.
steps += [
    {'op': 'fs', 'path': 'res://art/palette/palette.tres'},
    {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': 'palette.tres', 'double': True},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] inspector edits ", editor.get_inspector().get_edited_object())'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l11_material_before'},
    show_row('albedo_texture'),
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'albedo_texture', 'type': 'Button', 'nth': 0}},
    {'op': 'wait', 'frames': 20},
    dump_popups(),
    {'op': 'capture', 'name': 'l11_texture_menu'},
    {'op': 'popup', 'text': 'Quick Load...'},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Texture2D"):
		print("[probe] load dialog title ", window.title)
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "palette"
		edit.text_changed.emit(edit.text)
		return ""
return "no Quick Load dialog"
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l11_quick_load', 'window': 'Texture2D'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Texture2D"):
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.grab_focus()
		for pressed in [true, false]:
			var event := InputEventKey.new()
			event.keycode = KEY_ENTER
			event.pressed = pressed
			window.push_input(event)
			await plugin.get_tree().process_frame
		return ""
return "no Quick Load dialog"
'''),
    {'op': 'wait', 'frames': 30},
    option_items('cull_mode'),
    option_items('texture_filter'),
    # Albedo Color: click the swatch, type the hex value in the picker, press Enter.
    show_row('albedo_color'),
    # The swatch's synthetic click does not reach it, so the step opens the picker as the button's press does: the
    # button's own popup, below the button, showing the button's color.
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "albedo_color")
var button: ColorPickerButton = plugin._collect(row, "ColorPickerButton", "")[0]
button.get_picker().color = button.color
var popup := button.get_popup()
popup.position = Vector2i(button.get_screen_position() + Vector2(0, button.size.y))
popup.popup()
'''),
    {'op': 'wait', 'frames': 30},
    eval_('''
var out := []
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window != plugin.get_window():
		out.append(window.get_class() + " '" + window.title + "' " + str(plugin._collect(window, "ColorPicker", "").size()))
print("[probe] after color click ", out)
'''),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is PopupPanel:
		for edit in plugin._collect(window, "LineEdit", ""):
			print("[probe] picker field ", edit.text, " placeholder ", edit.placeholder_text)
'''),
    {'op': 'capture', 'name': 'l11_color_picker', 'window': 'class:PopupPanel'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is PopupPanel:
		for edit in plugin._collect(window, "LineEdit", ""):
			var text := str(edit.text).trim_prefix("#")
			if text.is_valid_hex_number() and text.length() >= 6:
				edit.text = "ffffff"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no hex field in the color picker"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l11_color_white', 'window': 'class:PopupPanel'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is PopupPanel:
		window.hide()
'''),
    {'op': 'wait', 'frames': 20},
    inspector_set('roughness', 1.0),
    inspector_set('cull_mode', 0),
    inspector_set('texture_filter', 0),
    {'op': 'wait', 'frames': 20},
    eval_('''
var material = editor.get_inspector().get_edited_object()
print("[probe] material now albedo ", material.albedo_color, " texture ", material.albedo_texture.resource_path if material.albedo_texture else null, " roughness ", material.roughness, " cull ", material.cull_mode, " filter ", material.texture_filter)
'''),
    show_row('albedo_texture'),
    {'op': 'capture', 'name': 'l11_material_albedo'},
    show_row('roughness'),
    {'op': 'capture', 'name': 'l11_material_roughness'},
    show_row('texture_filter'),
    {'op': 'capture', 'name': 'l11_material_filter'},
    {'op': 'press', 'find': {'class': 'InspectorDock', 'type': 'Button', 'text': 'tooltip:Save the currently edited resource.'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var text := FileAccess.get_file_as_string("res://art/palette/palette.tres")
print("[probe] palette.tres\n", text)
'''),
    # Collision, generated on import: Advanced Import Settings, the rock_small node, Physics.
    {'op': 'fs', 'path': 'res://art/nature/rock_small/rock_small.glb'},
    *click_file('rock_small.glb'),
    open_advanced(),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l11_advanced', 'window': 'Advanced'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		var item: TreeItem = tree.get_root()
		while item and item.get_text(0) != "rock_small":
			item = item.get_next_in_tree()
		item.select(0)
		tree.item_selected.emit()
		await plugin.get_tree().process_frame
		for row in plugin._collect(window, "EditorProperty", ""):
			if str(row.get_edited_property()) == "generate/physics":
				row.emit_changed("generate/physics", true)
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		var out := []
		for row in plugin._collect(window, "EditorProperty", ""):
			if row.is_visible_in_tree() and row.get_edited_object():
				var options := []
				for option in plugin._collect(row, "OptionButton", ""):
					for i in option.item_count:
						options.append(option.get_item_text(i))
				out.append("%s (%s) = %s %s" % [row.label, row.get_edited_property(), row.get_edited_object().get(row.get_edited_property()), options])
		print("[probe] physics rows\n", "\n".join(out))
		return ""
return "no Advanced Import Settings"
'''),
    {'op': 'capture', 'name': 'l11_advanced_physics', 'window': 'Advanced'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		for row in plugin._collect(window, "EditorProperty", ""):
			if str(row.get_edited_property()) == "physics/shape_type":
				row.emit_changed("physics/shape_type", 1)
				return ""
return "no Shape Type row"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l11_advanced_convex', 'window': 'Advanced'},
    {'op': 'press', 'find': {'window': 'Advanced', 'type': 'Button', 'text': 'Reimport'}},
    {'op': 'sleep', 'seconds': 4},
    eval_('''
var scene: PackedScene = load("res://art/nature/rock_small/rock_small.glb")
var root := scene.instantiate()
var out := []
for node in root.find_children("*", "", true, false):
	var extra := ""
	if node is CollisionShape3D:
		extra = " shape " + node.shape.get_class() + " points " + str(node.shape.points.size() if node.shape is ConvexPolygonShape3D else 0)
	if node is CollisionObject3D:
		extra = " layer %d mask %d" % [node.collision_layer, node.collision_mask]
	if node is MeshInstance3D:
		extra = " material " + str(node.mesh.surface_get_material(0).resource_path)
	out.append(str(root.get_path_to(node)) + " <" + node.get_class() + ">" + extra)
print("[probe] imported rock ", root.name, " <", root.get_class(), ">\n", "\n".join(out))
root.free()
'''),
    # The prop scene: Scene > New Inherited Scene from the .glb, saved beside it.
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    # It opens in the last folder used; go up one folder, then into art, nature, rock_small.
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'nature', 'rock_small'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "rock_small.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no rock_small.glb in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l11_inherit_dialog', 'window': 'Open Base Scene'},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    eval_('''
var root := editor.get_edited_scene_root()
print("[probe] inherited scene root ", root.name, " <", root.get_class(), "> file '", root.scene_file_path, "' children ", root.get_children().map(func(n): return n.name))
'''),
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'capture', 'name': 'l11_inherited_scene'},
    # Rename the root by double-clicking it in the Scene dock.
    click_tab('Scene'),
    {'op': 'click', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'item': 'rock_small2', 'double': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible:
		for edit in plugin._collect(window, "LineEdit", ""):
			if edit.text == "rock_small2":
				edit.text = "RockSmall"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no rename field"
'''),
    {'op': 'wait', 'frames': 20},
    eval_('print("[probe] root now ", editor.get_edited_scene_root().name)'),
    {'op': 'capture', 'name': 'l11_renamed_root'},
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		print("[probe] save dialog ", window.title, " at ", window.current_dir, " file ", window.current_file)
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l11_save_scene', 'window': 'Save Scene As'},
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path)'),
]

# One possible layout: a lone rock in the player's way, and two small groups.
ROCKS = [
    ('RockSmall', 'Vector3(3, 0, 0)', 'Vector3(0, 0, 0)', 'Vector3(1, 1, 1)'),
    ('RockSmall2', 'Vector3(-3.5, 0, 2)', 'Vector3(0, deg_to_rad(35), 0)', 'Vector3(1.3, 1.3, 1.3)'),
    ('RockSmall3', 'Vector3(1.5, 0, -4)', 'Vector3(0, deg_to_rad(-60), 0)', 'Vector3(0.8, 0.8, 0.8)'),
    ('RockSmall4', 'Vector3(0.6, 0, -4.6)', 'Vector3(0, deg_to_rad(120), 0)', 'Vector3(1, 1, 1)'),
]
steps += [
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
]
steps += add_node('Node3D', 'Rocks')
for number, (name, position, rotation, scale) in enumerate(ROCKS):
    steps += instantiate_under('Rocks', 'rock_small.tscn', capture='l11_select_scene' if number == 0 else None)
    steps += [
        eval_(f'''
var rocks := editor.get_edited_scene_root().get_node("Rocks")
print("[probe] rocks children ", rocks.get_children().map(func(n): return n.name))
if rocks.get_node_or_null("{name}") == null:
	return "no {name}"
'''),
        {'op': 'select', 'path': f'Rocks/{name}'},
        inspector_set('position', position),
        inspector_set('rotation', rotation),
        inspector_set('scale', scale),
    ]
steps += [
    {'op': 'select', 'path': 'Rocks/RockSmall2'},
    {'op': 'capture', 'name': 'l11_rock_inspector', 'frames': 20},
    *view('Rocks', dx=0, dy=0, wheel=-1),
    {'op': 'sleep', 'seconds': 2},
    {'op': 'menu', 'path': ['Scene', 'Save Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l11_meadow_rocks', 'frames': 20},
]

POSITION = '''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] player ", label, " position ", player.global_position.snapped(Vector3.ONE * 0.01), " collisions ", player.get_slide_collision_count())'''


def report(label):
    return {'op': 'eval', 'code': f'var label := "{label}"\n' + POSITION}


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l11.jsonl'), [
    {'op': 'wait', 'frames': 60},
    # Long enough for the editor to capture the game running in its Game tab.
    {'op': 'sleep', 'seconds': 8},
    report('start'),
    {'op': 'capture', 'name': 'l11_game_start'},
    {'op': 'key', 'key': 'D', 'pressed': True},
    {'op': 'sleep', 'seconds': 1.5},
    report('walking into the rock'),
    {'op': 'capture', 'name': 'l11_game_blocked'},
    {'op': 'key', 'key': 'D', 'pressed': False},
    {'op': 'wait', 'frames': 20},
    {'op': 'wheel', 'steps': 4},
    {'op': 'capture', 'name': 'l11_game_close', 'frames': 10},
    {'op': 'quit'},
])
steps += play(game, 33, capture_running='l11_running')
write(sys.argv[2], steps)
