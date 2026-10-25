# Crops lesson 20's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
INSPECTOR = (1636, 40, 1920, 1080)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    folder = os.path.join(site, 'the-sun')
    os.makedirs(folder, exist_ok=True)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


save('l20_final_wide', None, 'result')
save('l20_final_close', None, 'result-close')
save('l20_default_shadows_wide', None, 'new-light')
save('l20_light_rows', INSPECTOR, 'light-rows')
save('l20_sun_close', None, 'sun')
save('l20_camera_far', INSPECTOR, 'camera-far')
save('l20_shadow_mode_rows', INSPECTOR, 'shadow-mode-rows')
save('l20_orthogonal_close', None, 'orthogonal')
save('l20_bias_rows', INSPECTOR, 'bias-rows')
