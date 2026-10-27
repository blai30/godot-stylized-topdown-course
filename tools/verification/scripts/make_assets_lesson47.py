# Crops lesson 47's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'update-shore')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1080)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l47_select_ground', 'select-ground', None), ('l47_bank_map', 'bank-map', None), ('l47_updated', 'updated', None),
        ('l47_pond', 'pond', None), ('l47_close', 'close', None), ('l47_diagonal', 'diagonal', None), ('l47_dusk', 'dusk', None)):
    save(source, name, box)
