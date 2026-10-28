# Crops lesson 61's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'bonus-grid-cursor')
os.makedirs(folder, exist_ok=True)

# The Scene dock with GridOverlay selected.
SCENE_DOCK = (4, 115, 285, 555)


def save(source, name, box=None, width=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box, width in (
        ('l61_node', 'scene-dock', SCENE_DOCK, None), ('l61_no_cursor', 'no-cursor', None, 1000),
        ('l61_cell', 'cell', None, 1000), ('l61_moved', 'moved', None, 1000)):
    save(source, name, box, width)
