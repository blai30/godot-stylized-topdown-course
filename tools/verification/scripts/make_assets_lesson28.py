# Crops lesson 28's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'plant-a-grove')
os.makedirs(folder, exist_ok=True)

for source, name in (('l28_trunk_shape', 'trunk-shape'), ('l28_tree_scene', 'tree-scene'), ('l28_select_scene', 'select-scene'),
                     ('l28_meadow_editor', 'meadow-editor'), ('l28_grove_noon', 'grove-noon'), ('l28_grove_far', 'grove-far'),
                     ('l28_grove_dusk', 'grove-dusk'), ('l28_grove_close', 'grove-close')):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)
