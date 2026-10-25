# Crops lesson 22's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
INSPECTOR = (1636, 40, 1920, 1080)
folder = os.path.join(site, 'day-clock')
os.makedirs(folder, exist_ok=True)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


save('l22_attach_script', None, 'attach-script')
save('l22_exports', (1636, 140, 1920, 330), 'exports')
save('l22_editor_dusk', (288, 116, 1634, 800), 'editor-dusk')
save('l22_output', (288, 810, 1634, 1000), 'output')
save('l22_dawn', None, 'dawn')
save('l22_dusk', None, 'dusk')
save('l22_moon', None, 'moon')
save('l22_noon', None, 'noon')
