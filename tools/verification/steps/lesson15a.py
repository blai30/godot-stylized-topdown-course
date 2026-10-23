import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_popups, dump_windows

def option_items(window, nth):
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{window}" in window.title:
		var option: OptionButton = plugin._collect(window, "OptionButton", "")[{nth}]
		var items := []
		for i in option.item_count:
			items.append(option.get_item_text(i))
		print("[probe] options {window} {nth} ", items)
''')

write(sys.argv[2], [
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'select', 'path': '.'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Add/Create a New Node'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'set_text', 'find': {'window': 'Create New Node', 'type': 'LineEdit', 'nth': 0}, 'text': 'MeshInstance3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l15_create_node', 'window': 'Create New Node'},
    {'op': 'press', 'find': {'window': 'Create New Node', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 30},
    eval_('''
var root := editor.get_edited_scene_root()
var tile := root.get_node_or_null("MeshInstance3D")
if tile == null:
	return "no MeshInstance3D was added"
tile.name = "TestTile"
# Lifted 1 cm so it never fights the placeholder ground for the same pixels.
tile.position.y = 0.01
'''),
    {'op': 'select', 'path': 'TestTile'},
    {'op': 'capture', 'name': 'l15_default_box'},
    {'op': 'press', 'find': {'class': 'InspectorDock', 'property': 'mesh', 'type': 'Button', 'nth': -1}},
    {'op': 'capture', 'name': 'l15_mesh_menu'},
    dump_popups(),
    {'op': 'popup', 'text': 'PlaneMesh'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l15_plane_mesh'},
    {'op': 'press', 'find': {'class': 'InspectorDock', 'property': 'material', 'type': 'Button', 'nth': 0}},
    dump_popups(),
    {'op': 'popup', 'text': 'ShaderMaterial'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l15_shader_material'},
    {'op': 'press', 'find': {'class': 'InspectorDock', 'property': 'shader', 'type': 'Button', 'nth': 0}},
    {'op': 'capture', 'name': 'l15_shader_menu'},
    {'op': 'popup', 'text': 'New Shader...'},
    {'op': 'wait', 'frames': 30},
    option_items('Create Shader', 0),
    option_items('Create Shader', 1),
    option_items('Create Shader', 2),
    {'op': 'set_text', 'find': {'window': 'Create Shader', 'type': 'LineEdit', 'nth': 0}, 'text': 'res://art/ground/ground.gdshader'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l15_create_shader', 'window': 'Create Shader'},
    {'op': 'press', 'find': {'window': 'Create Shader', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    {'op': 'capture', 'name': 'l15_after_create'},
])
