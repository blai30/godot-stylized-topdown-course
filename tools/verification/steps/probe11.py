# Probes lesson 11's import UI: the Import dock for the palette and the rock, the Advanced Import Settings dialog and
# its Actions menu, and the Scene menu.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows, click_tab, click_file

DUMP_IMPORT = eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
var out := []
for row in plugin._collect(dock, "EditorProperty", ""):
	var value = row.get_edited_object().get(row.get_edited_property()) if row.get_edited_object() else null
	out.append("%s (%s) = %s" % [row.label, row.get_edited_property(), value])
for button in plugin._collect(dock, "Button", ""):
	if button.is_visible_in_tree() and button.text != "":
		out.append("button " + button.text)
print("[probe] import dock\\n", "\\n".join(out))
''')

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': 'res://art/palette/palette.png'},
    *click_file('palette.png'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    DUMP_IMPORT,
    {'op': 'capture', 'name': 'p11_palette_import'},
    {'op': 'fs', 'path': 'res://art/nature/rock_small/rock_small.glb'},
    *click_file('rock_small.glb'),
    {'op': 'wait', 'frames': 30},
    DUMP_IMPORT,
    {'op': 'capture', 'name': 'p11_glb_import'},
    eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "ImportDock")
for row in plugin._collect(dock, "EditorProperty", ""):
	var prop := str(row.get_edited_property())
	if prop.begins_with("materials/") or prop.begins_with("gltf/") or prop.begins_with("meshes/light"):
		for option in plugin._collect(row, "OptionButton", ""):
			var items := []
			for i in option.item_count:
				items.append(option.get_item_text(i))
			print("[probe] option ", prop, " ", items)
	print("[probe] tooltip ", prop, ": ", row.tooltip_text.left(300).replace("\n", " "))
'''),
    {'op': 'press', 'find': {'class': 'ImportDock', 'type': 'Button', 'text': 'Advanced...'}},
    {'op': 'wait', 'frames': 60},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		print("[probe] advanced title ", window.title, " size ", window.size)
		for tree in plugin._collect(window, "Tree", ""):
			var items := []
			var item: TreeItem = tree.get_root()
			while item:
				items.append(item.get_text(0))
				item = item.get_next_in_tree()
			print("[probe] tree ", items)
		for button in plugin._collect(window, "MenuButton", ""):
			var popup: PopupMenu = button.get_popup()
			var entries := []
			for i in popup.item_count:
				entries.append(popup.get_item_text(i))
			print("[probe] menu button ", button.text, " ", entries)
'''),
    {'op': 'capture', 'name': 'p11_advanced', 'window': 'Advanced'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		var tree: Tree = plugin._collect(window, "Tree", "")[0]
		for name in ["rock_small_rock_small", "palette", "rock_small"]:
			var item: TreeItem = tree.get_root()
			while item and item.get_text(0) != name:
				item = item.get_next_in_tree()
			item.select(0)
			tree.item_selected.emit()
			await plugin.get_tree().process_frame
			await plugin.get_tree().process_frame
			var out := []
			for row in plugin._collect(window, "EditorProperty", ""):
				if row.is_visible_in_tree() and row.get_edited_object():
					out.append("%s (%s) = %s" % [row.label, row.get_edited_property(), row.get_edited_object().get(row.get_edited_property())])
			print("[probe] advanced ", name, "\n", "\n".join(out))
'''),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		window.hide()
'''),
    eval_('''
var menus := []
for button in plugin._collect(plugin.get_tree().root, "MenuButton", "Scene"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		menus.append(popup.get_item_text(i))
print("[probe] scene menu ", menus)
'''),
]
write(sys.argv[2], steps)
