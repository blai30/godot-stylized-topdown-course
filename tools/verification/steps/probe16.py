# Probes lesson 16: Scene > Export As > MeshLibrary, the GridMap editor's palette, and painting with the mouse.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_popups, dump_windows

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    eval_('''
var out := []
for button in plugin._collect(plugin.get_tree().root, "MenuBar", ""):
	pass
for menu in plugin._collect(plugin.get_tree().root, "PopupMenu", ""):
	if menu.name.contains("Scene") or menu.title == "Scene":
		for i in menu.item_count:
			out.append(menu.get_item_text(i))
print("[probe] scene menu ", out)
'''),
    # A throwaway tile scene, made by script, only to see the export dialog.
    eval_('''
var root := Node3D.new()
root.name = "ProbeTiles"
var tile := MeshInstance3D.new()
tile.name = "Grass"
tile.mesh = PlaneMesh.new()
root.add_child(tile)
tile.owner = root
var packed := PackedScene.new()
packed.pack(root)
ResourceSaver.save(packed, "res://probe_tiles.tscn")
'''),
    {'op': 'open', 'path': 'res://probe_tiles.tscn'},
    {'op': 'wait', 'frames': 30},
    eval_('''
var bar := plugin._find_menu_bar(EditorInterface.get_base_control())
for i in bar.get_menu_count():
	if bar.get_menu_title(i) == "Scene":
		var popup: PopupMenu = bar.get_menu_popup(i)
		var items := []
		for j in popup.item_count:
			items.append("%s#%d%s" % [popup.get_item_text(j), popup.get_item_id(j), " >" if popup.get_item_submenu_node(j) else ""])
			var sub: PopupMenu = popup.get_item_submenu_node(j)
			if sub:
				var subitems := []
				for k in sub.item_count:
					subitems.append("%s#%d" % [sub.get_item_text(k), sub.get_item_id(k)])
				print("[probe] submenu ", popup.get_item_text(j), " ", subitems, " id ", sub.get_signal_connection_list("id_pressed").size(), " index ", sub.get_signal_connection_list("index_pressed").size())
		print("[probe] Scene menu ", items)
'''),
    {'op': 'menu', 'path': ['Scene', 'Export As...', 'MeshLibrary...']},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    {'op': 'capture', 'name': 'p16_export_dialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is FileDialog:
		print("[probe] export dialog ", window.title, " filters ", window.filters, " dir ", window.current_dir)
		for check in plugin._collect(window, "CheckBox", ""):
			print("[probe] export option ", check.text, " ", check.button_pressed)
		for option in plugin._collect(window, "OptionButton", ""):
			print("[probe] export option button ", option.text)
'''),
]
from steps import add_node, quick_load, inspector_set, unfold_inspector
steps += [
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is FileDialog:
		window.current_file = "probe_tiles.meshlib"
		window.get_ok_button().pressed.emit()
		return ""
return "no export dialog"
'''),
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] meshlib exists ", FileAccess.file_exists("res://probe_tiles.meshlib"), " items ", load("res://probe_tiles.meshlib").get_item_list())'),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 30},
]
steps += add_node('GridMap', 'GroundTiles')
steps += [unfold_inspector(), {'op': 'wait', 'frames': 20}]
steps += quick_load('mesh_library', 'probe_tiles')
steps += [
    inspector_set('cell_center_y', 'false'),
    {'op': 'wait', 'frames': 30},
    eval_('''
var map := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
print("[probe] gridmap library ", map.mesh_library, " cell ", map.cell_size, " center y ", map.cell_center_y)
var panel = plugin._find_class(plugin.get_tree().root, "GridMapEditor")
print("[probe] gridmap editor ", panel, " visible ", panel != null and panel.is_visible_in_tree())
if panel:
	for list in plugin._collect(panel, "ItemList", ""):
		var items := []
		for i in list.item_count:
			items.append(list.get_item_text(i))
		print("[probe] palette ", items)
	for control in plugin._collect(panel, "Button", ""):
		var shortcut: String = control.shortcut.get_as_text() if control.shortcut else ""
		var icon: String = control.icon.resource_name if control.icon else ""
		print("[probe] gridmap button toggle ", control.toggle_mode, " pressed ", control.button_pressed, " shortcut ", shortcut, " icon ", icon, " name ", control.name, " tip ", control.get_tooltip(Vector2.ZERO).left(50))
	for spin in plugin._collect(panel, "SpinBox", ""):
		print("[probe] gridmap spin ", spin.value, " ", spin.tooltip_text.left(40))
'''),
    {'op': 'capture', 'name': 'p16_gridmap_editor', 'frames': 20},
    eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "GridMapEditor")
var list: ItemList = plugin._collect(panel, "ItemList", "")[0]
list.select(0)
list.item_selected.emit(0)
'''),
    {'op': 'wait', 'frames': 10},
    {'op': 'key', 'find': {'type': 'Node3DEditorViewport'}, 'key': 'Kp 7'},
    {'op': 'key', 'find': {'type': 'Node3DEditorViewport'}, 'key': 'E'},
    eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "GridMapEditor")
for control in plugin._collect(panel, "Button", ""):
	if control.shortcut and control.shortcut.get_as_text().begins_with("E "):
		print("[probe] paint pressed after E key ", control.button_pressed)
		if not control.button_pressed:
			control.button_pressed = true
			control.pressed.emit()
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'paint', 'points': [[-3, 0], [-1, 0], [1, 0], [3, 0]]},
    {'op': 'wait', 'frames': 20},
    eval_('''
var map := editor.get_edited_scene_root().get_node("GroundTiles") as GridMap
print("[probe] painted cells ", map.get_used_cells())
'''),
    {'op': 'capture', 'name': 'p16_painted', 'frames': 20},
]
write(sys.argv[2], steps)
