# Crops lesson 48's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'sgt-phase2', 'shots', 'blender')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'water-collision')
os.makedirs(folder, exist_ok=True)

VIEWPORT = (0, 55, 1580, 985)
ROW = (420, 300, 1160, 700)


def save(directory, source, name, box=None):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (('l48_first_box', 'first-box', VIEWPORT), ('l48_boxes', 'boxes', ROW), ('l48_exporter', 'exporter', None)):
    save(blender, source, name, box)
for source, name in (('l48_before', 'before'), ('l48_stopped', 'stopped'), ('l48_shapes', 'shapes')):
    save(godot, source, name)
