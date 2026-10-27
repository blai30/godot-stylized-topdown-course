# Crops lesson 35's verified captures into the site's lesson assets (macOS run): the Krita captures from the run and the
# two exported views of the reference sheet.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots', 'krita')
exported = os.path.join(temp, 'sgt-phase1', 'workbench', 'art_source', 'character')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'design-the-character')
os.makedirs(folder, exist_ok=True)


def save(path, name, box=None, size=None):
    image = Image.open(path).convert('RGB')
    if box:
        image = image.crop(box)
    if size:
        image = image.resize(size, Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name in (('k35_new_dimensions', 'new-dimensions'), ('k35_grid', 'grid'), ('k35_front', 'front-view'),
                     ('k35_sheet', 'sheet'), ('k35_far', 'far')):
    save(os.path.join(shots, source + '.png'), name)
save(os.path.join(exported, 'character_front.png'), 'front', size=(512, 512))
save(os.path.join(exported, 'character_side.png'), 'side', size=(512, 512))
