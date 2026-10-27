# Crops lesson 41's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'import-with-a-bonemap')
os.makedirs(folder, exist_ok=True)
for name in os.listdir(folder):
    os.remove(os.path.join(folder, name))


def save(directory, source, name, box=None, width=None):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name in (('l41_exporter', 'exporter'), ('l41_animation_off', 'animation-off'), ('l41_exported', 'exported')):
    save(os.path.join(shots, 'blender'), source, name)
for source, name in (('l41_import_dock', 'import-dock'), ('l41_advanced', 'advanced'), ('l41_skeleton_selected', 'skeleton-selected'),
                     ('l41_bone_map_menu', 'bone-map-menu'), ('l41_bone_map_new', 'bone-map-new'), ('l41_profile_menu', 'profile-menu'),
                     ('l41_auto_mapped', 'auto-mapped'), ('l41_bone_map_save_menu', 'bone-map-save-menu'),
                     ('l41_bone_map_save', 'bone-map-save'), ('l41_bone_map_saved', 'bone-map-saved'),
                     ('l41_inherit_dialog', 'inherit-dialog'), ('l41_inherited', 'inherited'), ('l41_material', 'material'),
                     ('l41_material_save', 'material-save'), ('l41_character_scene', 'character-scene'),
                     ('l41_player_before', 'player-before'), ('l41_select_scene', 'select-scene'), ('l41_player_after', 'player-after'),
                     ('l41_noon_close', 'noon-close'), ('l41_turned', 'turned')):
    save(shots, source, name, width=1400)
