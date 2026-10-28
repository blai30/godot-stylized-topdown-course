# Crops lesson 52's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'runtime-and-editor')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 780)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l52_generator', 'generator', (1636, 40, 1920, 1000)), ('l52_on_ready', 'on-ready', (1636, 40, 1920, 1000)), ('l52_hand', 'hand', None),
        ('l52_wide', 'wide', None), ('l52_new_a', 'new-a', None), ('l52_new_b', 'new-b', None), ('l52_new_a_hand', 'new-hand', None)):
    save(source, name, box)
