# Crops lesson 49's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'noise')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 780)
PREVIEW = (1646, 310, 1900, 462)
GAP = 8


def load(source):
    return Image.open(os.path.join(godot, source + '.png')).convert('RGB')


def save(image, name):
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


def row(sources, box):
    # Crops the same box from several captures and puts the crops side by side.
    crops = [load(source).crop(box) for source in sources]
    sheet = Image.new('RGB', (sum(crop.width for crop in crops) + GAP * (len(crops) - 1), crops[0].height), (24, 24, 24))
    x = 0
    for crop in crops:
        sheet.paste(crop, (x, 0))
        x += crop.width + GAP
    return sheet


save(load('l49_new_texture'), 'new-texture')
save(load('l49_default').crop(INSPECTOR), 'default')
save(row(['l49_frequency_low', 'l49_frequency_high', 'l49_frequency'], PREVIEW), 'frequency')
save(row(['l49_octaves_one', 'l49_octaves_three'], PREVIEW), 'octaves')
save(row(['l49_seed_back', 'l49_seed'], PREVIEW), 'seed')
save(load('l49_save_terrain'), 'save-terrain')
save(load('l49_forest').crop(INSPECTOR), 'forest')
save(load('l49_new_profile').crop(INSPECTOR), 'new-profile')
save(load('l49_profile').crop(INSPECTOR), 'profile')
