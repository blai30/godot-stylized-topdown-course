# Crops lesson 33's verified captures into the site's lesson assets (macOS run). The captures were copied out of the
# shots folder by the run, to /tmp/g33_shots. The before and after pair is lesson33_shots.py's: the capsule hidden, the wind off.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'g33_shots')
pair = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'grass-that-parts')
os.makedirs(folder, exist_ok=True)

FEET = (520, 250, 760, 410)


def save(source, box, name, scale=1.0):
    image = Image.open(os.path.join(pair if source.startswith('l33p_') else shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if scale != 1.0:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name, scale in (
        ('l33p_before', FEET, 'before', 3.0), ('l33p_after', FEET, 'after', 3.0), ('l33_parted', None, 'parted', 1.0),
        ('l33_globals', None, 'globals', 1.0), ('l33_include_editor', None, 'include-editor', 1.0),
        ('l33_grass_editor', None, 'grass-editor', 1.0), ('l33_flower_editor', None, 'flower-editor', 1.0),
        ('l33_player_scene', None, 'player-scene', 1.0), ('l33_built', None, 'built', 1.0),
        ('l33_walk_0', None, 'walk-0', 1.0), ('l33_walk_1', None, 'walk-1', 1.0), ('l33_walk_2', None, 'walk-2', 1.0)):
    save(source, box, name, scale)
