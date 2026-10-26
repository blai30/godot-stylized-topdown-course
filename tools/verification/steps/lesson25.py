# Lesson 25: imports the leaf atlas with the settings a 3D texture with alpha needs: VRAM compression and mipmaps.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, import_set, show_import_row, REIMPORT

PATH = 'res://art/nature/tree_oak/leaf_atlas.png'
steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'fs', 'path': PATH},
    *click_file('leaf_atlas.png'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l25_atlas_selected'},
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    import_set('compress/mode', 2),
    {'op': 'wait', 'frames': 20},
    show_import_row('mipmaps/generate'),
    import_set('mipmaps/generate', 'true'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l25_atlas_import'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 4},
    eval_(f'''
var cfg := ConfigFile.new()
cfg.load("{PATH}.import")
var texture: Texture2D = load("{PATH}")
var image := texture.get_image()
print("[probe] atlas import compress ", cfg.get_value("params", "compress/mode"), " mipmaps ", cfg.get_value("params", "mipmaps/generate"), " fix_alpha_border ", cfg.get_value("params", "process/fix_alpha_border"), " size ", texture.get_size(), " format ", image.get_format(), " has_mipmaps ", image.has_mipmaps())
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
