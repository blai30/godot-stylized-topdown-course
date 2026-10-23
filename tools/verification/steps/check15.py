import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

def set_code(code):
    return eval_(f'''
var edit: CodeEdit = plugin._collect(plugin.get_tree().root, "CodeEdit", "")[0]
edit.text = {code!r}
edit.text_changed.emit()
''')

write(sys.argv[2], [
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'open', 'path': 'res://art/ground/ground.gdshader'},
    {'op': 'select', 'path': 'TestTile'},
    eval_('''
var viewport = plugin._collect(plugin.get_tree().root, "Node3DEditorViewport", "")[0]
for button in plugin._collect(viewport, "MenuButton", "Perspective"):
	var popup: PopupMenu = button.get_popup()
	for i in popup.item_count:
		if popup.get_item_text(i) == "Focus and Frame Selection":
			popup.id_pressed.emit(popup.get_item_id(i))
'''),
    {'op': 'orbit', 'dy': 120},
    {'op': 'wheel', 'steps': 2},
    eval_('editor.get_selection().clear()'),
    set_code('shader_type spatial;\n\nvoid fragment() {\n\tALBEDO = vec3(0.9, 0.2, 0.2);\n}\n'),
    {'op': 'sleep', 'seconds': 3},
    {'op': 'capture', 'name': 'check_live_unsaved'},
    set_code('shader_type spatial;\n\nvoid fragment() {\n\tALBEDO = vec3(0.9, 0.2, 0.2)\n}\n'),
    {'op': 'sleep', 'seconds': 3},
    {'op': 'capture', 'name': 'check_error'},
    eval_('print("[probe] file on disk starts: ", FileAccess.get_file_as_string("res://art/ground/ground.gdshader").substr(0, 60).replace("\n", " | "))'),
])
