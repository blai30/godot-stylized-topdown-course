# Crops lesson 24's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
blender = os.path.join(shots, 'blender')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'model-a-trunk')
os.makedirs(folder, exist_ok=True)

VIEW3D = (0, 28, 1578, 980)
WITH_PANEL = (480, 100, 1920, 1000)


def save(source, box, name, directory=shots):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name in (
        ('l24_colored', VIEW3D, 'final'),
        ('l24_trunk', VIEW3D, 'trunk'),
        ('l24_plan_10', VIEW3D, 'limbs'),
        ('l24_skeleton_framed', VIEW3D, 'skeleton'),
        ('l24_add_modifier_menu', (1600, 250, 1920, 560), 'add-modifier'),
        ('l24_skin_thick', (400, 28, 1920, 980), 'skin-thick'),
        ('l24_transform_menu', (273, 27, 909, 364), 'skin-transform'),
        ('l24_skin_radii', VIEW3D, 'radii'),
        ('l24_subsurf', WITH_PANEL, 'subdivision'),
        ('l24b_object_menu', (280, 27, 700, 560), 'object-menu'),
        ('l24_applied', WITH_PANEL, 'applied'),
        ('l24_file_menu2', (0, 0, 520, 500), 'file-menu'),
        ('l24_append_selected', None, 'append-selected'),
        ('l24_material_search', (1580, 230, 1920, 700), 'material-search'),
        ('l24_uv_added', (1580, 610, 1920, 720), 'uv-maps'),
        ('l24_uv_collapsed', (0, 28, 788, 700), 'uv-collapsed'),
        ('l24_exporter_settings', (1600, 220, 1920, 1060), 'exporter-settings')):
    save(source, box, name, blender)

for source, box, name in (
        ('l24_tree_scene', None, 'tree-scene'),
        ('l24_meadow_tree', None, 'meadow-editor'),
        ('l24_game_close', None, 'result')):
    save(source, box, name)
