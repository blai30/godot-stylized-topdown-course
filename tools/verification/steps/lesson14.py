# Lesson 14: imports the dirt and sand textures with the grass texture's settings.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab, click_file, import_set, show_import_row, REIMPORT

steps = [{'op': 'sleep', 'seconds': 3}]
for name in ('dirt_albedo', 'sand_albedo'):
    steps += [
        {'op': 'fs', 'path': f'res://art/ground/{name}.png'},
        *click_file(f'{name}.png'),
        click_tab('Import'),
        {'op': 'wait', 'frames': 30},
        import_set('compress/mode', 2),
        {'op': 'wait', 'frames': 20},
        show_import_row('mipmaps/generate'),
        import_set('mipmaps/generate', 'true'),
        {'op': 'wait', 'frames': 20},
        {'op': 'capture', 'name': f'l14_{name}_import'},
        REIMPORT,
        {'op': 'sleep', 'seconds': 3},
        eval_(f'''
var cfg := ConfigFile.new()
cfg.load("res://art/ground/{name}.png.import")
var texture: Texture2D = load("res://art/ground/{name}.png")
print("[probe] {name.split('_')[0]} import compress ", cfg.get_value("params", "compress/mode"), " mipmaps ", cfg.get_value("params", "mipmaps/generate"), " size ", texture.get_size())
'''),
    ]
steps += [{'op': 'wait', 'frames': 30}, {'op': 'quit'}]
write(sys.argv[2], steps)
