# Crops lesson 38's verified captures into the site's lesson assets (macOS run): Blender's and Krita's captures from the
# runs, the game's capture of the textured character, and two Blender viewport renders of the textured model
# (f38_face and f38_back, made by a headless Blender script from the saved file and texture).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'character-uvs-and-painting')
os.makedirs(folder, exist_ok=True)


def save(path, name, box=None):
    image = Image.open(path).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name in (('l38_workspace', 'workspace'), ('l38_all_selected', 'all-selected'), ('l38_tunic', 'tunic'),
                     ('l38_bodies', 'bodies'), ('l38_pieces', 'pieces'), ('l38_project_search', 'project-search'),
                     ('l38_projected', 'projected'), ('l38_head_uv', 'head-uv')):
    save(os.path.join(shots, 'blender', source + '.png'), name)
for source, name in (('k38_new_dimensions', 'new-dimensions'), ('k38_grid', 'grid'), ('k38_cells', 'cells'),
                     ('k38_patch', 'patch'), ('k38_features', 'features'), ('k38_texture', 'texture'),
                     ('k38_png_options', 'png-options')):
    save(os.path.join(shots, 'krita', source + '.png'), name)
save(os.path.join(shots, 'l38_meadow.png'), 'meadow')
save(os.path.join(shots, 'l38_close.png'), 'close')
save(os.path.join(temp, 'f38_face.png'), 'face')
save(os.path.join(temp, 'f38_back.png'), 'back')
save(os.path.join(temp, 'sgt-phase1', 'workbench', 'art', 'character', 'character_texture.png'), 'texture-file')
