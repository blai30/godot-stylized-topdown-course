# Crops lesson 21's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
INSPECTOR = (1636, 40, 1920, 1080)
PANEL = (288, 805, 1634, 1040)
folder = os.path.join(site, 'keyframing-the-day')
os.makedirs(folder, exist_ok=True)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


save('l21_canvas_layer', (0, 40, 290, 300), 'canvas-layer')
save('l21_full_rect', INSPECTOR, 'full-rect')
save('l21_create_shader', None, 'create-shader')
save('l21_shader_editor', (288, 730, 1634, 1010), 'shader-editor')
save('l21_grade_parameters', INSPECTOR, 'grade-parameters')
save('l21_grade_off', None, 'grade-off')
save('l21_grade_dusk_rows', INSPECTOR, 'grade-dusk-rows')
save('l21_grade_dusk', None, 'grade-dusk')
save('l21_animation_panel', PANEL, 'animation-panel')
save('l21_new_animation', None, 'new-animation')
save('l21_animation_rows', INSPECTOR, 'animation-rows')
save('l21_ambient_keyed', PANEL, 'ambient-keyed')
save('l21_panel_noon', PANEL, 'tracks')

# The day in six frames: midnight, early morning, noon, afternoon-to-dusk, late sunset, sunset.
names = ['000', '120', '300', '438', '480', '510']
grid = Image.new('RGB', (960, 360))
for i, name in enumerate(names):
    frame = Image.open(os.path.join(shots, f'l21_day_{name}.png')).convert('RGB').resize((320, 180), Image.LANCZOS)
    grid.paste(frame, ((i % 3) * 320, (i // 3) * 180))
grid.save(os.path.join(folder, 'day.png'), optimize=True)
save('l21_day_300', None, 'noon')
save('l21_day_480', None, 'late-sunset')
save('l21_day_000', None, 'midnight')
