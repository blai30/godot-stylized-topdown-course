# Crops lesson 31's verified captures into the site's lesson assets (macOS run). The Godot captures were copied out of
# the shots folder by the run, to /tmp/g31_shots.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'g31_shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'the-grass-shader')
os.makedirs(folder, exist_ok=True)

PREVIEW = (380, 340, 900, 500)
INSPECTOR = (1636, 40, 1920, 1080)


def save(source, box, name, scale=1.0):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if scale != 1.0:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name, scale in (
        ('l31_noon', None, 'noon', 1.0), ('l31_noon_close', PREVIEW, 'noon-close', 2.0), ('l31_dusk_close', PREVIEW, 'dusk', 2.0),
        ('l31_night_close', PREVIEW, 'night', 2.0), ('l31_ground_color_editor', None, 'ground-color-editor', 1.0),
        ('l31_ground_editor', None, 'ground-editor', 1.0), ('l31_wind_editor', None, 'wind-editor', 1.0),
        ('l31_grass_editor', None, 'grass-editor', 1.0), ('l31_flower_editor', None, 'flower-editor', 1.0),
        ('l31_inherit_dialog', None, 'inherit-dialog', 1.0), ('l31_grass_material', INSPECTOR, 'grass-material', 1.0),
        ('l31_flower_material', INSPECTOR, 'flower-material', 1.0), ('l31_preview_scene', None, 'preview-scene', 1.0),
        ('l31_save_scene', None, 'save-scene', 1.0), ('l31_preview_inspector', None, 'preview-inspector', 1.0)):
    save(source, box, name, scale)

# The wind: the same few blades six half-seconds apart, in a grid.
crop = (540, 380, 780, 470)
tiles = [Image.open(os.path.join(shots, 'l31_wind_{}.png'.format(index))).convert('RGB').crop(crop).resize((720, 270), Image.LANCZOS) for index in range(6)]
sheet = Image.new('RGB', (1440, 810))
for index, tile in enumerate(tiles):
    sheet.paste(tile, ((index % 2) * 720, (index // 2) * 270))
sheet.save(os.path.join(folder, 'wind.png'), optimize=True)
print('wind', sheet.size)
