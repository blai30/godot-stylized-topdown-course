# Crops lesson 43's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'animation-tree')
os.makedirs(folder, exist_ok=True)
for name in os.listdir(folder):
    os.remove(os.path.join(folder, name))


def save(source, name, box=None, width=1400):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name in (('l43_tree_added', 'tree-added'), ('l43_tree_root', 'tree-root')):
    save(source, name)
for source, name in (('l43_idle', 'idle'), ('l43_walk_0', 'walk-0'), ('l43_walk_1', 'walk-1'), ('l43_run_0', 'run-0'),
                     ('l43_run_1', 'run-1'), ('l43_stopped', 'stopped')):
    save(source, name, box=(440, 140, 840, 540), width=None)
