# Crops lesson 55's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'theme-and-pause-panel')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1076)
EDITOR = (0, 40, 1640, 1076)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l55_new_theme', 'new-theme', None), ('l55_save_theme', 'save-theme', None), ('l55_theme_editor', 'theme-editor', None),
        ('l55_type_added', 'type-added', None), ('l55_panel_style', 'panel-style', None), ('l55_button_normal', 'button-normal', None),
        ('l55_theme_saved', 'theme-saved', None), ('l55_new_scene', 'new-scene', EDITOR), ('l55_panel_scene', 'panel-scene', EDITOR),
        ('l55_save_scene', 'save-scene', None), ('l55_select_scene', 'select-scene', None), ('l55_exports', 'exports', None),
        ('l55_running', 'running', None), ('l55_paused', 'paused', None), ('l55_dusk', 'dusk', None), ('l55_no_shadows', 'no-shadows', None)):
    save(source, name, box)
