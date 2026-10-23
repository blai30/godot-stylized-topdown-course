import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

write(sys.argv[2], [
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'select', 'path': 'Nose'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Attach a new or existing script'}},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var language: OptionButton = plugin._collect(window, "OptionButton", "")[0]
		language.select(1)
		language.item_selected.emit(1)
'''),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var inherits: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		inherits.text = "CharacterBody3D"
		inherits.text_changed.emit(inherits.text)
		await plugin.get_tree().process_frame
		var template: OptionButton = plugin._collect(window, "OptionButton", "")[1]
		var items := []
		for i in template.item_count:
			items.append(template.get_item_text(i))
		print("[probe] templates for CharacterBody3D ", items, " selected ", template.text)
'''),
])
