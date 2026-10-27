# Crops lesson 40's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'sgt-phase2', 'shots', 'blender')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'skinning')
os.makedirs(folder, exist_ok=True)
for name in os.listdir(folder):
    os.remove(os.path.join(folder, name))
FIGURE = (330, 60, 1250, 985)


def save(source, name, box=None):
    image = Image.open(os.path.join(blender, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name in (('l40_start', 'start'), ('l40_selected', 'selected'), ('l40_parent_menu', 'parent-menu'), ('l40_parented', 'parented'),
                     ('l40_groups', 'groups'), ('l40_weights_arm', 'weights-arm'), ('l40_weights_leg', 'weights-leg'),
                     ('l40_weights_hips', 'weights-hips'), ('l40_pose_automatic', 'pose-automatic'), ('l40_limited', 'limited'),
                     ('l40_rigid', 'rigid'), ('l40_pose_final', 'pose-final')):
    save(source, name)
