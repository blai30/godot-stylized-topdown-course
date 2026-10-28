# Crops lesson 50's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'generating-ground')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 780)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l50_profile', 'profile', INSPECTOR), ('l50_save_as', 'save-as', None), ('l50_floor', 'floor', None),
        ('l50_select_water', 'select-water', None), ('l50_generator', 'generator', None), ('l50_generated', 'generated', None),
        ('l50_wide', 'wide', None), ('l50_north_west', 'lake', None), ('l50_lake', 'lake-east', None), ('l50_shore', 'start', None),
        ('l50_dusk', 'dusk', None)):
    save(source, name, box)
