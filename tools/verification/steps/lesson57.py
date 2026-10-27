# Lesson 57 (bonus): autumn leaf color. A flat multiply tried first, then a gradient map in the foliage shader, a ramp
# resource, an instance uniform set per tree by a small script, and the grove with each oak at its own point in autumn.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, save_code, build, game_steps, play, quick_load,
                   new_resource, open_resource, show_row, type_shader, open_bottom_panel, close_bottom_panel)
from lesson57_pieces import SHADER, AUTUMN_TREE, GROVE_AUTUMN, RAMP

SCRIPT = 'res://src/World/AutumnTree.cs'
SHADER_FILE = 'res://art/shaders/foliage.gdshader'
TREE = 'res://art/nature/tree_oak/tree_oak.tscn'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'
PIECES = [SHADER, AUTUMN_TREE]
ORANGE = 'Color(0.9, 0.45, 0.12)'
GREEN = 'Color(0.408, 0.765, 0.263)'


def open_shader(path, name):
    return [{'op': 'fs', 'path': path}, {'op': 'click', 'find': {'class': 'FileSystemDock', 'type': 'Tree'}, 'item': name, 'double': True},
            {'op': 'wait', 'frames': 40}]


def leaves_material():
    return [
        {'op': 'select', 'path': 'leaves'},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        # Clicking the material's picture opens the saved material, leaves.tres, in the Inspector.
        eval_('editor.edit_resource(editor.get_edited_scene_root().get_node("leaves").material_override)'),
        {'op': 'wait', 'frames': 30},
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
    ]


def noon(name, wheel=4):
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
            {'op': 'wheel', 'steps': wheel}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l57_{name}', 'frames': 10}]


out_dir = os.path.dirname(sys.argv[2])
multiply_game = game_steps(os.path.join(out_dir, 'game-l57a.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4}, *noon('multiply', 6), {'op': 'quit'}])
final_game = game_steps(os.path.join(out_dir, 'game-l57b.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': '''
var report := []
for node in tree.root.get_node("Meadow/Trees").get_children():
	if node.name.begins_with("TreeOak"):
		var leaves := node.get_node("leaves") as GeometryInstance3D
		report.append("%s autumn %s phase %s" % [node.name, snappedf(leaves.get_instance_shader_parameter("autumn"), 0.001), snappedf(leaves.get_instance_shader_parameter("tree_phase"), 0.001)])
print("[game] AUTUMN ", "\\n".join(report))
'''},
    *noon('grove', 0),
    {'op': 'wheel', 'steps': 6}, {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l57_grove_close', 'frames': 10},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.8)'},
    {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l57_grove_dusk', 'frames': 10},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': 'for node in tree.root.get_node("Meadow/Trees").get_children():\n\tif node.name.begins_with("TreeOak"):\n\t\tnode.get_node("leaves").set_instance_shader_parameter("autumn", 1.0)'},
    {'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': 'l57_turned', 'frames': 10},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 3},
    # First, what a flat multiply does: the material's Leaf Color set to orange.
    {'op': 'open', 'path': TREE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *leaves_material(),
    inspector_set('shader_parameter/leaf_color', ORANGE),
    {'op': 'wait', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(multiply_game, 40),
    {'op': 'open', 'path': TREE},
    {'op': 'wait', 'frames': 40},
    *leaves_material(),
    inspector_set('shader_parameter/leaf_color', GREEN),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # The shader.
    *open_shader(SHADER_FILE, 'foliage.gdshader'),
    *type_shader(SHADER, SHADER_FILE),
    {'op': 'capture', 'name': 'l57_shader_editor', 'frames': 20},
    close_bottom_panel(),
    # The ramp, on the leaves material.
    {'op': 'open', 'path': TREE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *leaves_material(),
    *new_resource('shader_parameter/autumn_ramp', 'GradientTexture1D'),
    open_resource('shader_parameter/autumn_ramp', 'gradient'),
    # Clicking the Gradient's picture opens its editor below it.
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "gradient")
plugin._collect(plugin._collect(row, "EditorResourcePicker", "")[0], "Button", "")[0].pressed.emit()
for attempt in 20:
	await plugin.get_tree().process_frame
'''),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    show_row('gradient'),
    {'op': 'capture', 'name': 'l57_ramp_default', 'frames': 20},
    # A click on the gradient bar adds a stop there: one at 45% and one at 75% of the way across.
    *[eval_(f'''
var dock = plugin._find_class(plugin.get_tree().root, "InspectorDock")
var bar: Control = plugin._collect(dock, "GradientEdit", "")[0]
# The bar leaves a margin of 4 px at its left and the selected stop's swatch, 73 px, at its right.
var at := bar.get_global_rect().position + Vector2(4.0 + {fraction} * (bar.size.x - 73.0), bar.size.y * 0.5)
for pressed in [true, false]:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	event.position = at
	event.global_position = at
	bar.get_viewport().push_input(event)
	await plugin.get_tree().process_frame
''') for fraction in (0.45, 0.75)],
    {'op': 'wait', 'frames': 30},
    eval_(f'''
var material := editor.get_edited_scene_root().get_node("leaves").material_override as ShaderMaterial
var gradient := (material.get_shader_parameter("autumn_ramp") as GradientTexture1D).gradient
print("[probe] stops after clicks ", gradient.offsets)
if gradient.offsets.size() != 4:
	return "the bar has %d stops, wanted 4" % gradient.offsets.size()
# Each stop's color, typed in its color picker as a hex code.
gradient.colors = PackedColorArray([{', '.join(f'Color.html("{color}")' for _, color in RAMP)}])
print("[probe] ramp ", gradient.offsets, " ", gradient.colors)
'''),
    {'op': 'wait', 'frames': 30},
    show_row('shader_parameter/autumn_ramp'),
    {'op': 'capture', 'name': 'l57_ramp', 'frames': 20},
    # The script, on the tree's root.
    save_code(SCRIPT, AUTUMN_TREE),
    *build('l57_built'),
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    eval_('editor.get_edited_scene_root().set_script(load("res://src/World/AutumnTree.cs"))'),
    {'op': 'wait', 'frames': 40},
    show_row('Autumn'),
    {'op': 'capture', 'name': 'l57_tree_scene', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    # Each oak of the grove.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
]
names = ['TreeOak'] + [f'TreeOak{index}' for index in range(2, 8)]
for index, (name, value) in enumerate(zip(names, GROVE_AUTUMN)):
    steps += [{'op': 'select', 'path': f'Trees/{name}'}, unfold_inspector(), {'op': 'wait', 'frames': 10},
              inspector_set('Autumn', str(value)), {'op': 'wait', 'frames': 10}]
    if index == 3:
        steps += [show_row('Autumn'), {'op': 'capture', 'name': 'l57_inspector', 'frames': 20}]
steps += [
    eval_('''
var trees := editor.get_edited_scene_root().get_node("Trees")
print("[probe] autumn ", trees.get_children().filter(func(n): return n.name.begins_with("TreeOak")).map(func(n): return "%s %s" % [n.name, n.get("Autumn")]))
'''),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    *play(final_game, 60),
]
write(sys.argv[2], steps)
