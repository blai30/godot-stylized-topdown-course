# Crops lesson 27's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'the-foliage-shader')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1080)
EDITOR = (288, 730, 1634, 1010)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name in (
        ('l27_globals', None, 'globals'),
        ('l27_create_include', None, 'create-include'),
        ('l27_create_foliage', None, 'create-foliage'),
        ('l27_create_bark', None, 'create-bark'),
        ('l27_wind_editor', EDITOR, 'wind-editor'),
        ('l27_foliage_editor', EDITOR, 'foliage-editor'),
        ('l27_leaves_material', INSPECTOR, 'leaves-material'),
        ('l27_leaves_material_save', None, 'save-material'),
        ('l27_bark_material', INSPECTOR, 'bark-material'),
        ('l27_tree_scene', None, 'tree-scene'),
        ('l27_noon_close', None, 'noon'),
        ('l27_dusk_close', None, 'dusk'),
        ('l27_night_close', None, 'night')):
    save(source, box, name)

# The crown in the wind: three of the six frames, half a second apart, cropped to the tree.
box = (360, 90, 640, 340)
strip = Image.new('RGB', (box[2] - box[0]) * 3 and ((box[2] - box[0]) * 3, box[3] - box[1]))
for i, frame in enumerate((0, 1, 2)):
    strip.paste(Image.open(os.path.join(shots, 'l27_wind_%d.png' % frame)).convert('RGB').crop(box), (i * (box[2] - box[0]), 0))
strip.save(os.path.join(folder, 'wind.png'), optimize=True)
print('wind', strip.size)
