# Crops lesson 45's verified captures into the site's lesson assets (macOS run): the editor's and the game's captures of the
# lake bed tile and the water's three steps.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'water-depth')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1080)
POND = (360, 150, 920, 570)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l45_create_lake_bed', 'create-lake-bed', None), ('l45_lake_bed_shader', 'lake-bed-shader', None),
        ('l45_water_tile', 'water-tile', None), ('l45_tile_set', 'tile-set', None),
        ('l45_delete_bed', 'delete-bed', None), ('l45_create_water', 'create-water', None),
        ('l45_water_material', 'water-material', INSPECTOR), ('l45_save_water_scene', 'save-scene', None),
        ('l45_water_in_meadow', 'water-in-meadow', None),
        ('l45_flat_pond', 'flat', POND), ('l45_thickness_pond', 'thickness', POND), ('l45_color_pond', 'color', POND),
        ('l45_color_dusk', 'dusk', POND), ('l45_color_night', 'night', POND), ('l45_color_wide', 'wide', None),
        ('l45_color_editor', 'shader-editor', None)):
    save(source, name, box)
