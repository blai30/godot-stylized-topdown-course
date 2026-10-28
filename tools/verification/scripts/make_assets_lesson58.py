# Crops lesson 58's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'scaffold-the-project-settings')
os.makedirs(folder, exist_ok=True)

# The settings window's right pane, without the section list, whose highlight the test harness does not keep in step.
PANE = (205, 85, 1185, 645)

# The Inspector's Collision section: the Layer and Mask pickers.
PLAYER_COLLISION = (1640, 890, 1910, 1080)
TERRAIN_COLLISION = (1640, 575, 1910, 765)


def save(source, name, box=None, width=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box, width in (
        ('l58_splash', 'splash', PANE, None), ('l58_user_dir', 'user-dir', PANE, None), ('l58_window', 'window', PANE, None),
        ('l58_physics_3d', 'physics', PANE, None), ('l58_physics_layers', 'physics-layers', PANE, None),
        ('l58_render_layers', 'render-layers', PANE, None), ('l58_player_mask_set', 'player-collision', PLAYER_COLLISION, None),
        ('l58_terrain_layer', 'terrain-collision', TERRAIN_COLLISION, None),
        ('l58_meadow_16x9', 'ratio-16x9', None, 1000), ('l58_meadow_16x10', 'ratio-16x10', None, 1000),
        ('l58_meadow_21x9', 'ratio-21x9', None, 1000), ('l58_meadow_32x9', 'ratio-32x9', None, 1000)):
    save(source, name, box, width)
