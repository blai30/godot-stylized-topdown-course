# Crops lesson 46's verified captures into the site's lesson assets (macOS run): the wave noise and the water's five steps.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'water-waves')
os.makedirs(folder, exist_ok=True)

INSPECTOR = (1636, 40, 1920, 1080)
POND = (360, 150, 920, 570)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l46_new_noise', 'new-noise', None), ('l46_wave_noise', 'wave-noise', INSPECTOR), ('l46_save_noise', 'save-noise', None),
        ('l46_light_pond', 'light', POND), ('l46_light_editor', 'light-editor', None),
        ('l46_wave_param', 'wave-param', INSPECTOR), ('l46_waves_pond', 'waves', POND), ('l46_waves_close', 'waves-close', None),
        ('l46_refraction_wall', 'refraction-wall', None), ('l46_refraction_close', 'refraction-close', None),
        ('l46_reflection_pond', 'reflection', POND), ('l46_reflection_wall', 'reflection-wall', None),
        ('l46_lake_bed_param', 'lake-bed-param', None), ('l46_final_pond', 'final', POND), ('l46_final_close', 'final-close', None),
        ('l46_final_wall', 'final-wall', None), ('l46_final_dusk', 'dusk', POND), ('l46_final_night', 'night', POND),
        ('l46_final_wide', 'wide', None), ('l46_final_editor', 'shader-editor', None)):
    save(source, name, box)
