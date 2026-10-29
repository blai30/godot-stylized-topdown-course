# Counts the scatter's clumps, flowers, pebbles and mushrooms with and without the dirt patches, from the lesson-34 snapshot.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

COUNT = '''
var scatter := editor.get_edited_scene_root().get_node("Grass")
var counts := {}
for child in scatter.get_children():
	if child is MultiMeshInstance3D:
		var kind := str(child.name).split("_")[0]
		counts[kind] = counts.get(kind, 0) + child.multimesh.instance_count
print("[probe] {tag} ", counts)
'''

PRESS_SCATTER = eval_('''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
for button in plugin._collect(dock, "Button", ""):
	if str(button.text) == "Scatter":
		editor.get_inspector().ensure_control_visible(button)
		button.pressed.emit()
		await plugin.get_tree().process_frame
		await plugin.get_tree().process_frame
		return ""
return "no Scatter button"
''')

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 60},
    {'op': 'select', 'path': 'Grass'},
    {'op': 'wait', 'frames': 20},
    eval_(COUNT.replace('{tag}', 'saved')),
    eval_('var scatter := editor.get_edited_scene_root().get_node("Grass")\nprint("[probe] patches ", scatter.get("Patches"))\nscatter.set("Patches", NodePath(""))'),
    PRESS_SCATTER,
    {'op': 'sleep', 'seconds': 2},
    eval_(COUNT.replace('{tag}', 'without patches')),
    eval_('var scatter := editor.get_edited_scene_root().get_node("Grass")\nscatter.set("Patches", NodePath("../Patches"))'),
    PRESS_SCATTER,
    {'op': 'sleep', 'seconds': 2},
    eval_(COUNT.replace('{tag}', 'with patches')),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
