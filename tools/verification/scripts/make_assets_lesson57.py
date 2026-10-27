# Crops lesson 57's verified captures into the site's lesson assets (macOS run). Shots are in the phase 2 shots folder.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'bonus-autumn-leaves')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1640, 150, 1910, 1075)
RAMP_EDITOR = (1640, 280, 1910, 840)
SHADER_PARAMS = (1640, 290, 1910, 780)
TREE_VALUE = (1640, 150, 1910, 240)


def save(source, box, name, scale=1.0):
    image = Image.open(os.path.join(shots, 'l57_' + source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if scale != 1.0:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name in (
        ('multiply', None, 'multiply'), ('turned', None, 'turned'), ('grove', None, 'grove'),
        ('grove_close', None, 'grove-close'), ('grove_dusk', None, 'grove-dusk'),
        ('shader_editor', None, 'shader-editor'), ('ramp_default', RAMP_EDITOR, 'ramp-default'),
        ('ramp', RAMP_EDITOR, 'ramp'), ('inspector', None, 'inspector'), ('tree_scene', None, 'tree-scene')):
    save(source, box, name)
