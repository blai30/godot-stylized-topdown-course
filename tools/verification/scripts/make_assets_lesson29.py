# Crops lesson 29's verified captures into the site's lesson assets (macOS run). The Krita and Blender captures were
# copied out of the shots folder by the run, to /tmp/k29_shots and /tmp/b29_shots.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
krita = os.path.join(temp, 'k29_shots')
blender = os.path.join(temp, 'b29_shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'a-pine')
os.makedirs(folder, exist_ok=True)

VIEW3D = (0, 28, 1578, 980)
NODES = (0, 60, 1920, 1050)
CANVAS = (371, 121, 1338, 1080)


def save(source, box, name, directory):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name, directory in (
        ('k29_twigs', CANVAS, 'twigs', krita), ('k29_atlas', CANVAS, 'atlas', krita),
        ('l29_skeleton_framed', VIEW3D, 'skeleton', blender), ('l29_colored', VIEW3D, 'trunk', blender),
        ('l26_tiers_linked', NODES, 'tiers-nodes', blender), ('l26_tiers_view', None, 'tiers-view', blender),
        ('l26_cards_linked', NODES, 'cards-nodes', blender), ('l26_cards_view', None, 'cards-view', blender),
        ('l26_data_linked', NODES, 'data-nodes', blender), ('l26_shading_linked', NODES, 'shading-nodes', blender),
        ('l29_crown', VIEW3D, 'crown', blender),
        ('l29_needles_material', (1636, 40, 1920, 1080), 'needles-material', shots), ('l29_tree_scene', None, 'tree-scene', shots),
        ('l29_meadow_editor', None, 'meadow-editor', shots), ('l29_noon', None, 'noon', shots),
        ('l29_noon_close', None, 'noon-close', shots), ('l29_dusk_close', None, 'dusk', shots), ('l29_night_close', None, 'night', shots)):
    save(source, box, name, directory)
