# Crops lesson 51's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'scattering-props')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 780)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l51_rules_empty', 'rules-empty', INSPECTOR), ('l51_rules', 'rules', (1636, 40, 1920, 1080)), ('l51_select_trees', 'select-trees', None),
        ('l51_generator', 'generator', None), ('l51_generated', 'generated', None), ('l51_wide', 'wide', None), ('l51_grove', 'grove', None),
        ('l51_shore', 'shore', None), ('l51_start', 'start', None), ('l51_dusk', 'dusk', None)):
    save(source, name, box)
