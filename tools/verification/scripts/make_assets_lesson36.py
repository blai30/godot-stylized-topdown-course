# Crops lesson 36's verified captures into the site's lesson assets (macOS run): Blender's captures from the run and the
# game's captures of the blockout beside the capsule.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'sgt-phase2', 'shots', 'blender')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'character-blockout')
os.makedirs(folder, exist_ok=True)

PROPERTIES = (1585, 215, 1915, 720)
VIEWPORT = (0, 55, 1580, 985)
FIGURE = (330, 60, 1250, 985)


def save(directory, source, name, box=None, size=None):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if size:
        image = image.resize(size, Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l36_save_name', 'save-name', None), ('l36_delete_menu', 'delete-menu', VIEWPORT),
        ('l36_ref0_browser', 'reference-browser', None), ('l36_ref0_added', 'reference-added', None),
        ('l36_ref0_located', 'reference-located', None), ('l36_ref0_data', 'reference-data', PROPERTIES),
        ('l36_ref1_added', 'side-added', None), ('l36_references', 'references', None),
        ('l36_new_collection', 'new-collection', (1580, 50, 1915, 215)), ('l36_collection', 'collection', None),
        ('l36_part_head', 'part-head', None), ('l36_part_torso', 'part-torso', None), ('l36_part_arm_L', 'part-arm', None),
        ('l36_front', 'front', FIGURE), ('l36_front_xray', 'front-xray', FIGURE), ('l36_side_xray', 'side-xray', FIGURE),
        ('l36_three_quarter', 'three-quarter', FIGURE), ('l36_exporter_panel', 'exporter-panel', None),
        ('l36_export_name', 'export-name', None)):
    save(blender, source, name, box)
for source, name in (('l36_noon_close', 'meadow-close'), ('l36_noon', 'meadow')):
    save(godot, source, name)
