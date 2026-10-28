# Lesson 61 (bonus), in Godot: a grid cursor for tactics games. A shader that draws a grid and one lit cell, a script that finds the
# cell under the mouse and says when it changes or is clicked, and both added to the meadow as a plane that lies on the ground.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, add_node, new_resource, open_resource, quick_load, game_steps, play,
                   make_folder, save_code, build)
from lesson61_pieces import SHADER, GRID_CURSOR, PIECES

SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
out_dir = os.path.dirname(sys.argv[2])
CLOCK = 'Meadow/WorldEnvironment/Day'
CURSOR = 'Meadow/GridOverlay'


def mouse(kind, x, y, pressed=True):
    # A mouse event sent into the running game, as the operating system sends one.
    if kind == 'motion':
        return {'op': 'eval', 'code': f'var event := InputEventMouseMotion.new()\nevent.position = Vector2({x}, {y})\nInput.parse_input_event(event)'}
    return {'op': 'eval', 'code': f'var event := InputEventMouseButton.new()\nevent.button_index = MOUSE_BUTTON_LEFT\nevent.pressed = {str(pressed).lower()}\nevent.position = Vector2({x}, {y})\nInput.parse_input_event(event)'}


def where(x, y):
    # Where the ground is under a screen point, and where the middle of the cell the game chose lands on the screen.
    return {'op': 'eval', 'code': f'''
var camera := tree.root.get_viewport().get_camera_3d()
var hit = Plane(Vector3.UP, 0.0).intersects_ray(camera.project_ray_origin(Vector2({x}, {y})), camera.project_ray_normal(Vector2({x}, {y})))
print("[game] GROUND under ({x}, {y}) is ", hit)
'''}


game = game_steps(os.path.join(out_dir, 'game-l61.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)\nclock.set("TimeOfDay", 0.5)'},
    {'op': 'eval', 'code': f'''
var cursor := tree.root.get_node("{CURSOR}")
tree.root.set_meta("hovered", [])
tree.root.set_meta("picked", [])
cursor.connect("CellHovered", func(cell): tree.root.get_meta("hovered").append(cell))
cursor.connect("CellPicked", func(cell): tree.root.get_meta("picked").append(cell))
'''},
    {'op': 'wheel', 'steps': 4}, {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l61_no_cursor', 'frames': 5},
    mouse('motion', 960, 600), {'op': 'wait', 'frames': 30},
    where(960, 600),
    {'op': 'capture', 'name': 'l61_cell', 'frames': 5},
    mouse('motion', 962, 602), {'op': 'wait', 'frames': 20},
    mouse('motion', 1180, 520), {'op': 'wait', 'frames': 30},
    where(1180, 520),
    {'op': 'capture', 'name': 'l61_moved', 'frames': 5},
    mouse('button', 1180, 520, True), {'op': 'wait', 'frames': 10}, mouse('button', 1180, 520, False), {'op': 'wait', 'frames': 20},
    {'op': 'eval', 'code': """
print("[game] HOVERED ", tree.root.get_meta("hovered"))
print("[game] PICKED ", tree.root.get_meta("picked"))
var camera := tree.root.get_viewport().get_camera_3d()
for cell in tree.root.get_meta("hovered"):
	print("[game] CELL ", cell, " middle on screen ", camera.unproject_position(Vector3(cell.x + 0.5, 0.0, cell.y + 0.5)))
"""},
    {'op': 'quit'}])

steps = [
    {'op': 'sleep', 'seconds': 5},
    *make_folder('world', 'grid'),
    *make_folder('src', 'Grid'),
    save_code('res://world/grid/grid_overlay.gdshader', SHADER),
    save_code('res://src/Grid/GridCursor.cs', GRID_CURSOR),
    eval_('editor.get_resource_filesystem().scan()'),
    {'op': 'sleep', 'seconds': 4},
    *build('l61_built'),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *add_node('MeshInstance3D', 'GridOverlay'),
    *new_resource('mesh', 'PlaneMesh', nth=-1),
    open_resource('mesh', 'size'),
    inspector_set('size', 'Vector2(40, 40)'),
    {'op': 'wait', 'frames': 20},
    {'op': 'select', 'path': 'GridOverlay'},
    unfold_inspector(),
    *new_resource('material_override', 'ShaderMaterial'),
    open_resource('material_override', 'shader'),
    *quick_load('shader', 'grid_overlay'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l61_material'},
    {'op': 'select', 'path': 'GridOverlay'},
    inspector_set('position', 'Vector3(0, 0.05, 0)'),
    inspector_set('cast_shadow', '0'),
    *quick_load('script', 'GridCursor.cs'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l61_node'},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    *play(game, 40),
    eval_('print("[probe] overlay ", editor.get_edited_scene_root().get_node("GridOverlay").get_script(), " ", editor.get_edited_scene_root().get_node("GridOverlay").mesh, " ", editor.get_edited_scene_root().get_node("GridOverlay").material_override)'),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
