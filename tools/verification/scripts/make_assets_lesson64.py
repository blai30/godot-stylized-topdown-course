# Crops lesson 64's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'bonus-tile-movement')
os.makedirs(folder, exist_ok=True)

# The Inspector's bottom: the Script row, and the exported values above it.
INSPECTOR = (1640, 150, 1915, 520)


def save(source, name, box=None, width=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box, width in (
        ('l64_script', 'script', None, 1400), ('l64_walking', 'walking', None, 1000), ('l64_blocked', 'blocked', None, 1000)):
    save(source, name, box, width)
