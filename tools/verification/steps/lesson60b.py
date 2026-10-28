# Lesson 60, part B, in Godot: the renamed copy opens, builds, and runs. Reads back the names, runs the audit and the game, and exports
# a build named for the new game.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, build, run_tool_script, game_steps, play, open_bottom_panel, close_bottom_panel

GAME = os.environ.get('SGT_NEW_GAME', 'MoonQuest')
WINDOW = 'Project Settings'
out_dir = os.path.dirname(sys.argv[2])
FIND_WINDOW = f'''
var window: Window = null
for candidate in plugin._windows(plugin.get_tree().root):
	if candidate.visible and "{WINDOW}" in candidate.title:
		window = candidate
if window == null:
	return "no {WINDOW} window"
'''

game = game_steps(os.path.join(out_dir, 'game-l60.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': '''
print("[game] NAMES ", ProjectSettings.get_setting("application/config/name"), " | ", ProjectSettings.get_setting("dotnet/project/assembly_name"), " | ", ProjectSettings.get_setting("application/config/custom_user_dir_name"), " | ", OS.get_user_data_dir())
var player := tree.root.get_node("Meadow/Player")
print("[game] PLAYER script ", player.get_script().resource_path, " class ", player.get_script().get_global_name())
'''},
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(5.5, 0.05, 0.5)\nInput.action_press("move_left")'},
    {'op': 'sleep', 'seconds': 0.8},
    {'op': 'eval', 'code': 'var player := tree.root.get_node("Meadow/Player")\nprint("[game] WALK velocity ", player.velocity)\nInput.action_release("move_left")'},
    {'op': 'capture', 'name': 'l60_running', 'frames': 10},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 8},
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    eval_(FIND_WINDOW + '''
plugin._collect(window, "CheckButton", "Advanced Settings")[0].button_pressed = true
'''),
    {'op': 'wait', 'frames': 30},
    eval_(FIND_WINDOW + '''
var tree: Tree = plugin._collect(window, "Tree", "")[0]
var item: TreeItem = tree.get_root()
for part in ["Application", "Config"]:
	for child in item.get_children():
		if child.get_text(0) == part:
			item = child
tree.set_selected(item, 0)
tree.item_selected.emit()
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l60_settings', 'window': WINDOW},
    eval_(FIND_WINDOW + '''
plugin._collect(window, "CheckButton", "Advanced Settings")[0].button_pressed = false
'''),
    {'op': 'press', 'find': {'window': WINDOW, 'type': 'Button', 'text': 'Close'}},
    {'op': 'wait', 'frames': 30},
    *build('l60_built'),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(game, 40),
    *run_tool_script('res://tools/audit_project.gd'),
    open_bottom_panel('Output'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l60_audit'},
    close_bottom_panel(),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
