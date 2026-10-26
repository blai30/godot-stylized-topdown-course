# Lesson 29: a pine. Imports the pine's needle atlas and glb, makes its scene (needle and bark materials, a trunk shape,
# the wind phase script), and plants three pines among the oaks.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, instantiate_under, quick_load, new_resource,
                   open_resource, resource_menu, open_in_file_dialog, game_steps, play, view, click_tab, click_file, import_set,
                   show_import_row, REIMPORT)
from lesson28_pieces import PINES

TREE_SCENE = 'res://art/nature/tree_pine/tree_pine.tscn'
ATLAS = 'res://art/nature/tree_pine/pine_atlas.png'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'


def place(name, position, yaw, scale):
    return [
        {'op': 'select', 'path': f'Trees/{name}'},
        unfold_inspector(),
        {'op': 'wait', 'frames': 10},
        inspector_set('position', 'Vector3(%s, %s, %s)' % position),
        inspector_set('rotation', f'Vector3(0, deg_to_rad({yaw}), 0)'),
        inspector_set('scale', f'Vector3({scale}, {scale}, {scale})'),
        {'op': 'wait', 'frames': 10},
    ]


def hour(time, name, wheel=0):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 40}, {'op': 'capture', 'name': f'l29_{name}', 'frames': 10}]
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-l29.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    {'op': 'eval', 'code': 'tree.root.get_node("Meadow/Player").global_position = Vector3(0.0, 0.05, 0.5)'},
    *hour(0.5, 'noon'),
    {'op': 'wheel', 'steps': 5}, *hour(0.5, 'noon_close'),
    *hour(0.8, 'dusk_close'),
    *hour(0.0, 'night_close'),
    {'op': 'eval', 'code': '''
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
player.global_position = Vector3(3.9, 0.05, -3.4)
await tree.process_frame
Input.action_press("move_left")
'''},
    {'op': 'sleep', 'seconds': 1.6},
    {'op': 'eval', 'code': '''
Input.action_release("move_left")
var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
print("[game] WALK stopped at x ", snappedf(player.global_position.x, 0.01), " (pine trunk at 1.2, collision radius 0.3)")
'''},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 8},
    # The needle atlas, imported as the oak's was.
    {'op': 'fs', 'path': ATLAS},
    *click_file('pine_atlas.png'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    import_set('compress/mode', 2),
    {'op': 'wait', 'frames': 20},
    show_import_row('mipmaps/generate'),
    import_set('mipmaps/generate', 'true'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l29_atlas_import'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 4},
    # The pine's scene, from the glb.
    {'op': 'fs', 'path': 'res://art/nature/tree_pine/tree_pine.glb'},
    {'op': 'menu', 'path': ['Scene', 'New Inherited Scene...']},
    {'op': 'wait', 'frames': 40},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'tooltip:Go to parent folder'}},
    {'op': 'wait', 'frames': 20},
    open_in_file_dialog('art', 'nature', 'tree_pine'),
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		for list in plugin._collect(window, "ItemList", ""):
			for i in list.item_count:
				if list.get_item_text(i) == "tree_pine.glb":
					list.select(i)
					list.item_selected.emit(i)
					return ""
return "no tree_pine.glb in the dialog"
'''),
    {'op': 'wait', 'frames': 20},
    {'op': 'press', 'find': {'window': 'Open Base Scene', 'type': 'Button', 'text': 'Open'}},
    {'op': 'wait', 'frames': 60},
    {'op': 'main_screen', 'name': '3D'},
    click_tab('Scene'),
    {'op': 'click', 'find': SCENE_TREE, 'item': 'tree_pine2', 'double': True},
    {'op': 'wait', 'frames': 20},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible:
		for edit in plugin._collect(window, "LineEdit", ""):
			if edit.text == "tree_pine2":
				edit.text = "TreePine"
				edit.text_changed.emit(edit.text)
				edit.text_submitted.emit(edit.text)
				return ""
return "no rename field"
'''),
    {'op': 'wait', 'frames': 20},
    eval_('print("[probe] pine scene children ", editor.get_edited_scene_root().get_children().map(func(n): return n.name))'),
    # The needle material.
    {'op': 'select', 'path': 'needles'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *new_resource('material_override', 'ShaderMaterial'),
    open_resource('material_override', 'shader'),
    *quick_load('shader', 'foliage.gdshader'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('shader_parameter/leaf_atlas', 'pine_atlas.png'),
    inspector_set('shader_parameter/leaf_color', 'Color("#2f7a4c")'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l29_needles_material', 'frames': 20},
    resource_menu('material_override', 'Save As...'),
    {'op': 'wait', 'frames': 30},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_dir = "res://art/nature/tree_pine"
		window.current_file = "needles.tres"
		return ""
return "no Save Resource dialog"
'''),
    {'op': 'capture', 'name': 'l29_save_material', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    # The bark: the oak's bark material, shared.
    {'op': 'select', 'path': 'tree_pine'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('material_override', 'bark.tres'),
    # The trunk shape and the wind phase script, as for the oak.
    {'op': 'select', 'path': '.'},
    *add_node('StaticBody3D', 'Trunk'),
    *add_node('CollisionShape3D', 'TrunkShape', 'Trunk'),
    {'op': 'select', 'path': 'Trunk/TrunkShape'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *new_resource('shape', 'CylinderShape3D', nth=1),
    open_resource('shape', 'radius'),
    inspector_set('radius', '0.3'),
    inspector_set('position', 'Vector3(0, 1.0, 0)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'select', 'path': '.'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 20},
    *quick_load('script', 'WindPhase.cs'),
    {'op': 'wait', 'frames': 40},
    *view('tree_pine', 'needles', dx=0, dy=0, wheel=0),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l29_tree_scene'},
    {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l29_save_scene', 'window': 'Save Scene As'},
    {'op': 'press', 'find': {'window': 'Save Scene As', 'type': 'Button', 'text': 'Save'}},
    {'op': 'wait', 'frames': 40},
    eval_('print("[probe] saved ", editor.get_edited_scene_root().scene_file_path, " nodes ", editor.get_edited_scene_root().get_children().map(func(n): return n.name))'),
    # The pines in the meadow.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
]
for index in range(len(PINES)):
    steps += instantiate_under('Trees', 'tree_pine.tscn', capture='l29_select_scene' if index == 0 else None)
for name, position, yaw, scale in PINES:
    steps += place(name, position, yaw, scale)
steps += [
    eval_('''
var trees := editor.get_edited_scene_root().get_node("Trees")
print("[probe] trees ", trees.get_children().map(func(n): return "%s %s %s" % [n.name, n.position, n.scale.x]))
'''),
    {'op': 'capture', 'name': 'l29_meadow_editor', 'frames': 20},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 30},
    *play(game, 60),
]
write(sys.argv[2], steps)
