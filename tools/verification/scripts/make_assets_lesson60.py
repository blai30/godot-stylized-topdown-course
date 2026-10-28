# Crops lesson 60's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'copy-the-template')
os.makedirs(folder, exist_ok=True)

# The settings window's right pane, without the section list, whose highlight the test harness does not keep in step.
PANE = (205, 85, 1185, 645)
# The Output panel's last line: the harness adds a line of its own above it.
OUTPUT_LAST = (292, 928, 900, 954)


def save(source, name, box=None, width=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box, width in (
        ('l60_settings', 'settings', PANE, None), ('l60_running', 'running', None, 1000), ('l60_audit', 'audit', OUTPUT_LAST, None)):
    save(source, name, box, width)
