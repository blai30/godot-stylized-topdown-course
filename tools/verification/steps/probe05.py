import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_popups, dump_windows

write(sys.argv[2], [
    {'op': 'menu', 'path': ['Scene', 'New Scene']},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': '3D Scene'}},
    {'op': 'wait', 'frames': 30},
    eval_('editor.get_edited_scene_root().name = "CameraRig"'),
    {'op': 'select', 'path': '.'},
    eval_('''
for button in plugin._collect(plugin._find_class(plugin.get_tree().root, "SceneTreeDock"), "Button", ""):
	print("[probe] dock button '", button.text, "' tooltip '", button.tooltip_text.replace("\\n", " | "), "'")
'''),
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Attach a new or existing script'}},
    {'op': 'wait', 'frames': 40},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		for option in plugin._collect(window, "OptionButton", ""):
			var items := []
			for i in option.item_count:
				items.append(option.get_item_text(i))
			print("[probe] option ", items, " selected ", option.text)
'''),
    {'op': 'capture', 'name': 'p05_attach_default', 'window': 'Attach Node Script'},
])
