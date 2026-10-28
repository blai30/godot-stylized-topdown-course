# Crops lesson 54's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'bushes')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1076)
DOCKS = (0, 40, 1920, 1076)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l54_inherit_dialog', 'inherit-dialog', None), ('l54_crown', 'crown', None), ('l54_bush_scene', 'bush-scene', None),
        ('l54_save_scene', 'save-scene', None), ('l54_select_scene', 'select-scene', None), ('l54_meadow_editor', 'meadow-editor', DOCKS),
        ('l54_meadow', 'meadow', None), ('l54_meadow_wide', 'meadow-wide', None), ('l54_meadow_dusk', 'meadow-dusk', None),
        ('l54_rule', 'rule', INSPECTOR), ('l54_generated', 'generated', None), ('l54_gen_grove', 'gen-grove', None),
        ('l54_gen_wide', 'gen-wide', None), ('l54_gen_dusk', 'gen-dusk', None)):
    save(source, name, box)
