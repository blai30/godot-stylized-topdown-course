# Crops lesson 25's verified captures into the site's lesson assets (macOS run), and shows the reference atlas on gray.
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
snapshot = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase1', 'snapshots', 'lesson-25')
folder = os.path.join(site, 'paint-a-leaf-atlas')
os.makedirs(folder, exist_ok=True)

CANVAS = (360, 110, 1345, 610)


def save(source, box, name, directory):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


krita = os.path.join(shots, 'krita')
for source, box, name in (
        ('k25_new_dimensions', None, 'new-dimensions'),
        ('k25_new_content', None, 'new-content'),
        ('k25_grid', (0, 28, 1920, 1080), 'grid'),
        ('k25_leaf_shape', None, 'leaf-shape'),
        ('k25_leaf_body', CANVAS, 'leaf-body'),
        ('k25_leaf', CANVAS, 'leaf'),
        ('k25_stamp', None, 'stamp'),
        ('k25_leaf_tip', None, 'leaf-tip'),
        ('k25_leaf_rotation', None, 'leaf-rotation'),
        ('k25_leaf_size', None, 'leaf-size'),
        ('k25_atlas', (371, 121, 1338, 1080), 'atlas'),
        ('k25_png_options', None, 'png-options')):
    save(source, box, name, krita)
save('l25_atlas_import', (0, 40, 290, 560), 'import-atlas', shots)

# The reference project's atlas, on gray so the transparent parts show.
atlas = Image.open(os.path.join(snapshot, 'art', 'nature', 'tree_oak', 'leaf_atlas.png')).convert('RGBA')
backdrop = Image.new('RGBA', atlas.size, (120, 120, 120, 255))
backdrop.alpha_composite(atlas)
backdrop.convert('RGB').save(os.path.join(folder, 'reference-atlas.png'), optimize=True)
print('reference-atlas', atlas.size)
