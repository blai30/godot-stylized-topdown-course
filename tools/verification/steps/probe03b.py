import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows
from probe03 import settings_section, WINDOW

write(sys.argv[2], [
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    {'op': 'press', 'find': {'window': WINDOW, 'type': 'CheckButton', 'text': 'Advanced Settings'}},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		var button: CheckButton = plugin._collect(window, "CheckButton", "Advanced Settings")[0]
		button.button_pressed = true
'''),
    {'op': 'wait', 'frames': 30},
    settings_section(['Physics', 'Common']),
    {'op': 'capture', 'name': 'p03_physics_advanced', 'window': WINDOW},
    # Input Map tab.
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and "{WINDOW}" in window.title:
		var tabs: TabContainer = plugin._collect(window, "TabContainer", "")[0]
		tabs.current_tab = 1
'''),
    {'op': 'wait', 'frames': 30},
    dump_windows(),
    {'op': 'capture', 'name': 'p03_input_map', 'window': WINDOW},
])
