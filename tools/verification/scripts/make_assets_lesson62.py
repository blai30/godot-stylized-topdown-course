# Crops lesson 62's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'bonus-click-to-move')
os.makedirs(folder, exist_ok=True)

GROUPS_DOCK = (1640, 40, 1915, 200)
NAVMESH_SETTINGS = (1640, 150, 1915, 720)
AGENT_SETTINGS = (1640, 150, 1915, 460)


def save(source, name, box=None, width=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box, width in (
        ('l62_new_group', 'new-group', None, None), ('l62_groups', 'groups', GROUPS_DOCK, None),
        ('l62_navmesh_settings', 'navmesh-settings', NAVMESH_SETTINGS, None), ('l62_baked', 'baked', None, 1400),
        ('l62_agent_settings', 'agent-settings', AGENT_SETTINGS, None), ('l62_midway', 'path', None, 1400)):
    save(source, name, box, width)
