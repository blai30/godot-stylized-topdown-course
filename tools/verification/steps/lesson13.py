# Lesson 13: imports the painted grass texture with the settings a repeating 3D texture needs.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, DUMP_IMPORT, import_set, show_import_row, REIMPORT

steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': 'res://art/ground/grass_albedo.png'},
    *click_file('grass_albedo.png'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    DUMP_IMPORT,
    {'op': 'capture', 'name': 'l13_import_before'},
    # VRAM Compressed: the graphics card keeps it compressed, a quarter of the memory or less.
    import_set('compress/mode', 2),
    {'op': 'wait', 'frames': 20},
    show_import_row('mipmaps/generate'),
    import_set('mipmaps/generate', 'true'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l13_import_set'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 3},
    eval_('''
var cfg := ConfigFile.new()
cfg.load("res://art/ground/grass_albedo.png.import")
var texture: Texture2D = load("res://art/ground/grass_albedo.png")
print("[probe] grass import compress ", cfg.get_value("params", "compress/mode"), " mipmaps ", cfg.get_value("params", "mipmaps/generate"), " size ", texture.get_size(), " format ", texture.get_image().get_format(), " mipmaps ", texture.get_image().has_mipmaps())
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l13_import_after'},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
