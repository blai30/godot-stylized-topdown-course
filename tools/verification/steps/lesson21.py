# Lesson 21: the color grade and the day. A canvas shader reads the finished frame and applies FactoryGame's grade; an
# AnimationPlayer's `day` animation then keys the sun, the environment, the sky, and the grade through one minute.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, add_node, new_resource, open_resource,
                   type_shader, game_steps, play, close_bottom_panel, INSPECTOR)
from lesson21_pieces import GRADE_SHADER, BUILD_DAY

SCENE = 'res://world/environment/world_environment.tscn'
SHADER = 'res://world/environment/color_grade.gdshader'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}

PIECES = [GRADE_SHADER, BUILD_DAY]


def game(name, extra):
    return game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', f'game-{name}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 8}, *extra, {'op': 'quit'}])


def run_meadow(name, extra):
    return [{'op': 'open', 'path': 'res://levels/meadow.tscn'}, {'op': 'wait', 'frames': 40}, *play(game(name, extra), 20)]


def edit_scene():
    return [{'op': 'open', 'path': SCENE}, {'op': 'wait', 'frames': 30}]


steps = [
    {'op': 'sleep', 'seconds': 3},
    *edit_scene(),
    {'op': 'select', 'path': '.'},
    *add_node('CanvasLayer', 'Grade'),
    {'op': 'capture', 'name': 'l21_canvas_layer', 'frames': 20},
    *add_node('ColorRect', 'Screen', parent='Grade'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l21_color_rect', 'frames': 20},
    inspector_set('anchors_preset', '15'),
    {'op': 'wait', 'frames': 20},
    inspector_set('mouse_filter', '2'),
    {'op': 'wait', 'frames': 20},
    eval_('''
var rect := editor.get_edited_scene_root().get_node("Grade/Screen") as ColorRect
print("[probe] rect anchors ", rect.anchor_left, rect.anchor_top, rect.anchor_right, rect.anchor_bottom, " offsets ", rect.offset_left, rect.offset_top, rect.offset_right, rect.offset_bottom, " mouse ", rect.mouse_filter, " size ", rect.size)
'''),
    {'op': 'capture', 'name': 'l21_full_rect', 'frames': 20},
    # The material: a ShaderMaterial with a new canvas shader.
    {'op': 'select', 'path': 'Grade/Screen'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *new_resource('material', 'ShaderMaterial'),
    open_resource('material', 'shader'),
    show_row('shader'),
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'shader', 'type': 'Button', 'nth': 0}},
    {'op': 'wait', 'frames': 20},
    {'op': 'popup', 'text': 'New Shader...'},
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title == "Create Shader":
		for option in plugin._collect(window, "OptionButton", ""):
			var items := []
			for i in option.item_count:
				items.append(option.get_item_text(i))
			print("[probe] create shader options ", items, " selected ", option.get_item_text(option.selected))
'''),
    {'op': 'set_text', 'find': {'window': 'Create Shader', 'type': 'LineEdit', 'nth': 0}, 'text': SHADER},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l21_create_shader', 'window': 'Create Shader'},
    {'op': 'press', 'find': {'window': 'Create Shader', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    *type_shader(GRADE_SHADER, SHADER),
    {'op': 'capture', 'name': 'l21_shader_editor', 'frames': 20},
    close_bottom_panel(),
    {'op': 'select', 'path': 'Grade/Screen'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    show_row('shader_parameter/saturation'),
    {'op': 'capture', 'name': 'l21_grade_parameters', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *run_meadow('l21_grade_off', [{'op': 'capture', 'name': 'l21_grade_off', 'frames': 10}]),
    # A dusk grade, set in the Inspector.
    {'op': 'open', 'path': SCENE},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'Grade/Screen'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    inspector_set('shader_parameter/shadow_tint', 'Color("#D999F2")'),
    inspector_set('shader_parameter/highlight_tint', 'Color("#FF8C47")'),
    inspector_set('shader_parameter/strength', '0.3'),
    inspector_set('shader_parameter/saturation', '0.9'),
    show_row('shader_parameter/saturation'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l21_grade_dusk_rows', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *run_meadow('l21_grade_dusk', [{'op': 'capture', 'name': 'l21_grade_dusk', 'frames': 10}]),
    # The grade's math, checked against the formula in Python: the same frame ungraded and graded at full strength.
    *run_meadow('l21_grade_check', [
        {'op': 'eval', 'code': 'var material := (tree.root.get_node("Meadow/WorldEnvironment/Grade/Screen") as ColorRect).material as ShaderMaterial\nmaterial.set_shader_parameter("strength", 0.0)'},
        {'op': 'wait', 'frames': 20},
        {'op': 'capture', 'name': 'l21_check_plain', 'frames': 10},
        {'op': 'eval', 'code': 'var material := (tree.root.get_node("Meadow/WorldEnvironment/Grade/Screen") as ColorRect).material as ShaderMaterial\nmaterial.set_shader_parameter("shadow_tint", Color("#1FADFF"))\nmaterial.set_shader_parameter("highlight_tint", Color("#99BFFF"))\nmaterial.set_shader_parameter("strength", 1.0)\nmaterial.set_shader_parameter("saturation", 0.6)'},
        {'op': 'wait', 'frames': 20},
        {'op': 'capture', 'name': 'l21_check_graded', 'frames': 10},
    ]),
    # Back to a neutral grade for the day.
    {'op': 'open', 'path': SCENE},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'Grade/Screen'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    inspector_set('shader_parameter/shadow_tint', 'Color("#FFFFFF")'),
    inspector_set('shader_parameter/highlight_tint', 'Color("#FFFFFF")'),
    inspector_set('shader_parameter/strength', '0.0'),
    inspector_set('shader_parameter/saturation', '1.0'),
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    eval_('''
var material := (load("res://world/environment/world_environment.tscn").instantiate().get_node("Grade/Screen") as ColorRect).material as ShaderMaterial
print("[probe] grade ", material.get_shader_parameter("shadow_tint"), material.get_shader_parameter("highlight_tint"), material.get_shader_parameter("strength"), material.get_shader_parameter("saturation"))
'''),
]
write(sys.argv[2], steps)
