# Lesson 60, part A, in Godot: the rename script and the README's instructions are written in the template. The editor closes
# afterward: the rename itself runs from the command line (prepare_lesson60.py), because it renames the C# project Godot has open.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, save_code, build, run_tool_script
from lesson60_pieces import RENAME, README_SECTION

steps = [
    {'op': 'sleep', 'seconds': 5},
    eval_('DirAccess.make_dir_recursive_absolute("res://tools")'),
    save_code('res://tools/rename_project.gd', RENAME),
    eval_(f'''
var text := FileAccess.get_file_as_string("res://README.md")
var file := FileAccess.open("res://README.md", FileAccess.WRITE)
file.store_string(text.replace("## Requirements", {README_SECTION!r} + "## Requirements"))
file.close()
editor.get_resource_filesystem().scan()
'''),
    {'op': 'sleep', 'seconds': 4},
    {'op': 'main_screen', 'name': 'Script'},
    eval_('editor.edit_script(load("res://tools/rename_project.gd"))'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l60_script'},
    *build('l60_built'),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
