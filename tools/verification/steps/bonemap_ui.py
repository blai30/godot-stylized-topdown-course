# Shared steps for lessons 41 and 42: Advanced Import Settings, the Skeleton3D's Bone Map made new with the humanoid profile.
from steps import eval_

ADVANCED = '''
var advanced = null
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.title.contains("Advanced"):
		advanced = window
'''


def select_node(name):
    return eval_(ADVANCED + f'''
var tree: Tree = plugin._collect(advanced, "Tree", "")[0]
var item: TreeItem = tree.get_root()
while item and item.get_text(0) != "{name}":
	item = item.get_next_in_tree()
if item == null:
	return "no node {name}"
item.select(0)
tree.item_selected.emit()
for i in 4:
	await plugin.get_tree().process_frame
''')


def press_row_button(row, last=True, resource_picker=False):
    target = 'plugin._collect(row, "EditorResourcePicker", "")[0]' if resource_picker else 'row'
    index = 'buttons.size() - 1' if last else '0'
    return eval_(ADVANCED + f'''
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "{row}":
		var buttons := plugin._collect({target}, "Button", "")
		buttons[{index}].pressed.emit()
		for i in 12:
			await plugin.get_tree().process_frame
		return ""
return "no row {row}"
''')


def new_humanoid_bone_map(prefix):
    # Bone Map > New BoneMap, opened, Profile > New SkeletonProfileHumanoid; Godot auto-maps. Captures along the way.
    return [
        press_row_button('retarget/bone_map'),
        {'op': 'capture', 'name': prefix + '_bone_map_menu', 'window': 'Advanced'},
        {'op': 'popup', 'text': 'BoneMap'},
        {'op': 'wait', 'frames': 30},
        press_row_button('retarget/bone_map', last=False, resource_picker=True),
        {'op': 'wait', 'frames': 15},
        {'op': 'capture', 'name': prefix + '_bone_map_new', 'window': 'Advanced'},
        press_row_button('profile'),
        {'op': 'capture', 'name': prefix + '_profile_menu', 'window': 'Advanced'},
        {'op': 'popup', 'text': 'SkeletonProfileHumanoid'},
        {'op': 'wait', 'frames': 90},
        eval_(ADVANCED + '''
var bone_map: BoneMap = null
for row in plugin._collect(advanced, "EditorProperty", ""):
	if str(row.get_edited_property()) == "retarget/bone_map":
		bone_map = row.get_edited_object().get("retarget/bone_map")
var mapped := 0
var empty := []
for i in bone_map.profile.bone_size:
	var name := bone_map.profile.get_bone_name(i)
	if bone_map.get_skeleton_bone_name(name) == &"":
		empty.append(name)
	else:
		mapped += 1
print("[probe] bone map mapped ", mapped, " of ", bone_map.profile.bone_size, " unmapped ", " ".join(empty))
'''),
        {'op': 'capture', 'name': prefix + '_auto_mapped', 'window': 'Advanced'},
    ]
