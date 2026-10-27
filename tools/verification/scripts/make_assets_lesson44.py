# Crops lesson 44's verified captures into the site's lesson assets (macOS run): Blender's captures from the run and the
# editor's and the game's captures of the bank kit.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'sgt-phase2', 'shots', 'blender')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'model-the-bank-kit')
os.makedirs(folder, exist_ok=True)

PROPERTIES = (1585, 215, 1915, 720)
VIEWPORT = (0, 55, 1580, 985)
PIECE = (330, 60, 1250, 985)
ROW = (420, 330, 1160, 640)
FLAT = (420, 440, 1160, 570)
INSPECTOR = (1636, 40, 1920, 1080)
IMPORT_DOCK = (0, 40, 290, 560)
ADVANCED_PANEL = (2560, 40, 2880, 200)


def save(directory, source, name, box=None, size=None):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if size:
        image = image.resize(size, Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l44_save_name', 'save-name', None), ('l44_collection', 'collection', None), ('l44_plane', 'plane', VIEWPORT),
        ('l44_front_selected', 'front-selected', VIEWPORT), ('l44_top', 'top', VIEWPORT),
        ('l44_subdivided', 'subdivided', VIEWPORT), ('l44_wall_front', 'wall', VIEWPORT),
        ('l44_group', 'group', VIEWPORT), ('l44_displace', 'displace', None),
        ('l44_displace_view', 'displace-view', ROW), ('l44_lip_selected', 'lip-selected', VIEWPORT),
        ('l44_lip_flat', 'lip-flat', VIEWPORT), ('l44_land_bevel', 'land-bevel', VIEWPORT),
        ('l44_water_corner', 'water-corner', None), ('l44_diagonal', 'diagonal', None),
        ('l44_pieces', 'pieces', FLAT), ('l44_kit', 'kit', ROW), ('l44_material', 'material', None),
        ('l44_exporter_panel', 'exporter-panel', None), ('l44_export_name', 'export-name', None)):
    save(blender, source, name, box)
for source, name, box in (
        ('l44_import_scene', 'import-scene', IMPORT_DOCK), ('l44_import_library', 'import-library', IMPORT_DOCK),
        ('l44_create_shader', 'create-shader', None), ('l44_shader', 'shader', None),
        ('l44_new_resource', 'new-resource', None), ('l44_material_ground', 'material-ground', INSPECTOR),
        ('l44_clod_noise', 'clod-noise', INSPECTOR), ('l44_clod_normals', 'clod-normals', INSPECTOR),
        ('l44_save_material', 'save-material', None), ('l44_use_external', 'use-external', ADVANCED_PANEL),
        ('l44_external_path', 'external-path', ADVANCED_PANEL), ('l44_bank_node', 'bank-node', None),
        ('l44_pond', 'pond', None), ('l44_pond_close', 'pond-close', None), ('l44_pond_wall', 'pond-wall', None),
        ('l44_pond_dusk', 'pond-dusk', None), ('l44_pond_night', 'pond-night', None)):
    save(godot, source, name, box)
