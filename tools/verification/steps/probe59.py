# Probe: moving and renaming files through the FileSystem dock as the reader does (drag, F2), and deleting with the key.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, make_folder

FIND_ITEM = '''
var dock = plugin._find_class(plugin.get_tree().root, "FileSystemDock")
var tree: Tree = plugin._collect(dock, "Tree", "")[0]
var items := {}
var stack := [tree.get_root()]
while not stack.is_empty():
	var current: TreeItem = stack.pop_back()
	if current == null:
		continue
	items[str(current.get_metadata(0))] = current
	var child := current.get_first_child()
	while child != null:
		stack.append(child)
		child = child.get_next()
'''


def drag(source, target):
    return eval_(FIND_ITEM + f'''
var from_item = items.get("{source}")
var to_item = items.get("{target}")
if from_item == null or to_item == null:
	return "missing item " + str(from_item) + " " + str(to_item)
tree.scroll_to_item(from_item)
await plugin.get_tree().process_frame
var from_rect := tree.get_item_area_rect(from_item, 0)
var origin := tree.get_global_transform_with_canvas().origin
var start := origin + from_rect.get_center()
var press := InputEventMouseButton.new()
press.button_index = MOUSE_BUTTON_LEFT
press.pressed = true
press.position = start
press.global_position = start
Input.parse_input_event(press)
await plugin.get_tree().process_frame
tree.scroll_to_item(to_item)
await plugin.get_tree().process_frame
var to_rect := tree.get_item_area_rect(to_item, 0)
var end := origin + to_rect.get_center()
for step in 12:
	var motion := InputEventMouseMotion.new()
	motion.position = start.lerp(end, (step + 1) / 12.0)
	motion.global_position = motion.position
	motion.button_mask = MOUSE_BUTTON_MASK_LEFT
	Input.parse_input_event(motion)
	await plugin.get_tree().process_frame
var release := InputEventMouseButton.new()
release.button_index = MOUSE_BUTTON_LEFT
release.pressed = false
release.position = end
release.global_position = end
Input.parse_input_event(release)
await plugin.get_tree().process_frame
''')


steps = [
    {'op': 'sleep', 'seconds': 5},
    *make_folder('world', 'ground'),
    {'op': 'fs', 'path': 'res://art/ground/ground_tile_set.tres'},
    {'op': 'wait', 'frames': 30},
    eval_(FIND_ITEM + '''
print("[probe] dock items ", items.keys())
'''),
    {'op': 'capture', 'name': 'probe59_before'},
    eval_(FIND_ITEM + '''
for path in items:
	var item: TreeItem = items[path]
	if path.ends_with("/") and path != "res://" and path != "res://art/" and path != "res://art/ground/" and path != "res://world/" and item.get_parent() != null:
		item.collapsed = true
await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
    drag('res://art/ground/ground_tile_set.tres', 'res://world/ground/'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'probe59_drag'},
    eval_('''
print("[probe] moved ", FileAccess.file_exists("res://world/ground/ground_tile_set.tres"), " old ", FileAccess.file_exists("res://art/ground/ground_tile_set.tres"))
print("[probe] meadow ref ", FileAccess.get_file_as_string("res://levels/meadow.tscn").substr(0, 900))
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
