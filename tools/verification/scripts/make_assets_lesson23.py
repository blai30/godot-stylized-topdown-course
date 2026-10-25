# Crops lesson 23's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
INSPECTOR = (1636, 40, 1920, 1080)
folder = os.path.join(site, 'stylized-lighting')
os.makedirs(folder, exist_ok=True)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


save('l23_before_dusk_close', None, 'dusk-before')
save('l23_dusk_close', None, 'dusk-after')
save('l23_before_noon_close', None, 'noon-before')
save('l23_noon_close', None, 'noon-after')
save('l23_globals', None, 'globals')
save('l23_create_include', None, 'create-include')
save('l23_include_editor', (288, 730, 1634, 1010), 'include-editor')
save('l23_create_palette_shader', None, 'create-palette-shader')
save('l23_rock_material', INSPECTOR, 'rock-material')
save('l23_save_material', None, 'save-material')
save('l23_clock_rim', INSPECTOR, 'clock-rim')

# The day with the rim: dawn, noon, dusk, night.
grid = Image.new('RGB', (1280, 720))
for i, name in enumerate(['dawn', 'noon', 'dusk', 'night']):
    frame = Image.open(os.path.join(shots, f'l23_{name}.png')).convert('RGB').resize((640, 360), Image.LANCZOS)
    grid.paste(frame, ((i % 2) * 640, (i // 2) * 360))
grid.save(os.path.join(folder, 'day.png'), optimize=True)

# A rock's edge at dusk, before and after, enlarged.
box = (760, 0, 960, 160)
rock = Image.new('RGB', (1200, 480))
for i, name in enumerate(['l23_before_dusk_close', 'l23_dusk_close']):
    rock.paste(Image.open(os.path.join(shots, name + '.png')).convert('RGB').crop(box).resize((600, 480), Image.LANCZOS), (i * 600, 0))
rock.save(os.path.join(folder, 'rock-edge.png'), optimize=True)
