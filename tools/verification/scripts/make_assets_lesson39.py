# Crops lesson 39's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'sgt-phase2', 'shots', 'blender')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'the-armature')
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


for source, name in (('l39_start', 'start'), ('l39_first_bone', 'first-bone'), ('l39_bone_tab', 'bone-tab'), ('l39_spine', 'spine'),
                     ('l39_relations_panel', 'relations'), ('l39_parent_list', 'parent'), ('l39_arm', 'arm'), ('l39_leg', 'leg'),
                     ('l39_symmetrize_search', 'symmetrize-search'), ('l39_symmetrized', 'symmetrized'),
                     ('l39_viewport_display', 'display'), ('l39_side', 'side')):
    save(source, name)
