# Crops lesson 18's verified captures into the site's lesson assets (macOS run; make_assets.py holds the other lessons).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
INSPECTOR = (1636, 40, 1920, 1080)
GROUND_ROW = (1636, 140, 1920, 320)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    folder = os.path.join(site, 'ground-tile-resources')
    os.makedirs(folder, exist_ok=True)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


save('l18_new_script', None, 'new-script')
save('l18_tiles_filled', INSPECTOR, 'tiles-filled')
save('l18_save_set', None, 'save-set')
save('l18_ground_assigned', GROUND_ROW, 'ground-assigned')
save('l18_game', None, 'result')
