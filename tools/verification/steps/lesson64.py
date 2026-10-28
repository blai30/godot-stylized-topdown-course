# Lesson 64 (bonus), in Godot: tile-snapped movement for farming games. One script that walks the player a cell at a time, replacing
# PlayerMovement on the player, checked by walking in the game: every stop is the middle of a cell, and the pond and the trunks block a step.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, quick_load, game_steps, play, save_code, build, show_row
from lesson64_pieces import TILE_MOVEMENT, PIECES

SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
out_dir = os.path.dirname(sys.argv[2])
CLOCK = 'Meadow/WorldEnvironment/Day'


def clear_script():
    # The Script row's arrow opens its menu, and Clear is in it. The row's field would open the script instead.
    return eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "script")
if row == null:
	return "no row script"
editor.get_inspector().ensure_control_visible(row)
var buttons := plugin._collect(row, "Button", "")
buttons[buttons.size() - 1].pressed.emit()
for attempt in 10:
	await plugin.get_tree().process_frame
	for window in plugin._windows(plugin.get_tree().root):
		if window is PopupMenu and window.visible:
			for i in window.item_count:
				if window.get_item_text(i) == "Clear":
					window.id_pressed.emit(window.get_item_id(i))
					window.hide()
					return ""
			window.hide()
return "no Clear in the script menu"
''')


def sample(label, seconds):
    return [
        {'op': 'sleep', 'seconds': seconds},
        {'op': 'eval', 'code': f'''
var player := tree.root.get_node("Meadow/Player")
print("[game] {label} ", snappedf(player.global_position.x, 0.001), " ", snappedf(player.global_position.z, 0.001), " speed ", snappedf(Vector2(player.velocity.x, player.velocity.z).length(), 0.01), " facing ", snappedf(player.rotation_degrees.y, 0.1))
'''},
    ]


def walk(action, label, samples, gap=0.1, capture_at=None):
    steps = [{'op': 'eval', 'code': f'Input.action_press("{action}")'}]
    for i in range(samples):
        steps += sample(f'{label}{i + 1}', gap)
        if i + 1 == capture_at:
            steps += [{'op': 'capture', 'name': 'l64_walking', 'frames': 2}]
    steps += [{'op': 'eval', 'code': f'Input.action_release("{action}")'}]
    steps += sample(f'{label}_rest', 0.6)
    return steps


game = game_steps(os.path.join(out_dir, 'game-l64.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(8.3, 0.05, 4.2)'},
    {'op': 'wheel', 'steps': 5}, {'op': 'sleep', 'seconds': 1.0},
    *sample('START', 0.1),
    {'op': 'capture', 'name': 'l64_start', 'frames': 5},
    # A short press: the player takes at least one whole step and stops in a cell's middle.
    {'op': 'eval', 'code': 'Input.action_press("move_left")'}, {'op': 'sleep', 'seconds': 0.1},
    {'op': 'eval', 'code': 'Input.action_release("move_left")'},
    *sample('TAP', 0.6),
    # Held: step after step, each ending on a middle.
    *walk('move_left', 'LEFT', 12, capture_at=6),
    # Walk into the pond's bank: the steps stop at the edge.
    {'op': 'eval', 'code': 'Input.action_press("move_forward")'},
    {'op': 'sleep', 'seconds': 2.0},
    {'op': 'eval', 'code': 'Input.action_release("move_forward")'},
    *sample('FORWARD_rest', 0.5),
    {'op': 'eval', 'code': 'var animation_tree: AnimationTree = tree.root.get_node("Meadow/Player").find_child("AnimationTree", true, false)\nprint("[game] BLEND at rest ", animation_tree.get("parameters/blend_position"))'},
    {'op': 'capture', 'name': 'l64_blocked', 'frames': 5},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 5},
    save_code('res://src/Player/TileMovement.cs', TILE_MOVEMENT),
    eval_('editor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 4},
    *build('l64_built'),
    {'op': 'open', 'path': 'res://world/player/player.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': '.'},
    {'op': 'wait', 'frames': 20},
    clear_script(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'TileMovement'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l64_script'},
    eval_('print("[probe] player script ", editor.get_edited_scene_root().get_script())'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *play(game, 40),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
