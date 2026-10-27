# Crops lesson 37's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'sgt-phase2', 'shots', 'blender')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'refine-the-character')
os.makedirs(folder, exist_ok=True)
for name in os.listdir(folder):
    os.remove(os.path.join(folder, name))

VIEWPORT = (0, 55, 1580, 985)
FIGURE = (330, 60, 1250, 985)


def save(directory, source, name, box=None):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l37_select_search', 'select-search', None), ('l37_delete', 'delete', VIEWPORT), ('l37_half_hips', 'half-hips', None),
        ('l37_delete_face_menu', 'delete-face', None), ('l37_mirror', 'mirror', None), ('l37_torso', 'torso', None),
        ('l37_arm_face', 'arm-face', None), ('l37_arm', 'arm', None), ('l37_legs', 'legs', None), ('l37_head', 'head', None),
        ('l37_head_side', 'head-side', None), ('l37_fringe', 'fringe', None), ('l37_applied', 'applied', None),
        ('l37_interior', 'interior', None), ('l37_front', 'front', FIGURE), ('l37_side', 'side', FIGURE),
        ('l37_back', 'back', FIGURE), ('l37_top', 'top', FIGURE), ('l37_three_quarter', 'three-quarter', None),
        ('l37_export_name', 'export-name', None)):
    save(blender, source, name, box)
save(godot, 'l37_meadow', 'meadow')
