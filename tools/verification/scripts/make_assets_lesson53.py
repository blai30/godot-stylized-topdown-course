# Crops lesson 53's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'cloud-shadows')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1076)
SHADER_EDITOR = (288, 730, 1632, 1030)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l53_noise', 'noise', INSPECTOR), ('l53_globals', 'globals', None), ('l53_include_editor', 'include-editor', SHADER_EDITOR),
        ('l53_wind_editor', 'wind-editor', SHADER_EDITOR), ('l53_ground_editor', 'ground-editor', SHADER_EDITOR),
        ('l53_water_editor', 'water-editor', SHADER_EDITOR), ('l53_wide_off', 'wide-off', None), ('l53_wide_on', 'wide-on', None),
        ('l53_grove', 'grove', None), ('l53_pond_off', 'pond-off', None), ('l53_pond', 'pond', None), ('l53_dusk', 'dusk', None),
        ('l53_night', 'night', None)):
    save(source, name, box)
