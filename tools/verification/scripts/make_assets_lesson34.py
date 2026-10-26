# Crops lesson 34's verified captures into the site's lesson assets (macOS run). The Blender and Godot captures were
# copied out of the shots folders by the run, to /tmp/b34_shots and /tmp/g34_shots.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'b34_shots')
godot = os.path.join(temp, 'g34_shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'decoratives')
os.makedirs(folder, exist_ok=True)

VIEW3D = (0, 28, 1578, 980)
MODIFIER = (1580, 225, 1920, 520)
MENU = (280, 30, 700, 760)
INSPECTOR = (1636, 40, 1920, 1080)
FEET = (330, 200, 1000, 560)


def save(source, box, name, directory, scale=1.0):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if scale != 1.0:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name, directory, scale in (
        ('l34_pebble_a', (330, 380, 1010, 600), 'pebble-a', blender, 1.8), ('l34_boxes', (330, 380, 1250, 600), 'boxes', blender, 1.4),
        ('l34_group_list', MODIFIER, 'group-list', blender, 2.0), ('l34_paint_values', MODIFIER, 'paint-values', blender, 2.0),
        ('l34_convert_menu', MENU, 'convert-menu', blender, 1.0), ('l34_cleared', VIEW3D, 'cleared', blender, 1.0),
        ('l34_collection_tab', None, 'collection-tab', blender, 1.0),
        ('l34_preview_scene', None, 'preview-scene', godot, 1.0), ('l34_tile_0', INSPECTOR, 'tile-0', godot, 1.0),
        ('l34_tile_2', INSPECTOR, 'tile-2', godot, 1.0), ('l34_props', None, 'props', godot, 1.0),
        ('l34_decal_inspector', None, 'decal-inspector', godot, 1.0), ('l34_save_texture', None, 'save-texture', godot, 1.0),
        ('l34_grass_patches', None, 'grass-patches', godot, 1.0), ('l34_patches', None, 'patches', godot, 1.0),
        ('l34_mid', None, 'mid', godot, 1.0), ('l34_close', None, 'close', godot, 1.0),
        ('l34_mushroom_close', None, 'mushroom-close', godot, 1.0), ('l34_pebble_close', None, 'pebble-close', godot, 1.0),
        ('l34_dusk', None, 'dusk', godot, 1.0), ('l34_night', None, 'night', godot, 1.0)):
    save(source, box, name, directory, scale)
