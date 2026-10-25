# Crops lesson 19's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
INSPECTOR = (1636, 40, 1920, 1080)
VIEW = (288, 116, 1634, 1032)
GAME_WORLD = (0, 0, 1280, 720)


def save(source, box, name):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    folder = os.path.join(site, 'the-environment')
    os.makedirs(folder, exist_ok=True)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


save('l19_game_after', None, 'result')
save('l19_game_before', None, 'game-before')
save('l19_create_root', None, 'create-root')
save('l19_new_environment', INSPECTOR, 'new-environment')
save('l19_save_scene', None, 'save-scene')
save('l19_instantiate', (0, 0, 780, 100), 'instantiate')
save('l19_empty', VIEW, 'empty')
save('l19_create_shader', None, 'create-shader')
save('l19_shader_editor', (288, 730, 1634, 1010), 'shader-editor')
save('l19_sky_parameters', INSPECTOR, 'sky-parameters')
save('l19_sky', VIEW, 'sky')
save('l19_ambient_rows', INSPECTOR, 'ambient-rows')
save('l19_ambient', VIEW, 'ambient')
save('l19_tonemap_rows', INSPECTOR, 'tonemap-rows')
save('l19_tonemap', VIEW, 'tonemap')
save('l19_ssao_rows', INSPECTOR, 'ssao-rows')
save('l19_ssao_off', (560, 380, 1260, 800), 'ssao-off')
save('l19_ssao_on', (560, 380, 1260, 800), 'ssao-on')
save('l19_glow_rows', INSPECTOR, 'glow-rows')
save('l19_fog_rows', INSPECTOR, 'fog-rows')
save('l19_game_fog_default', None, 'fog-default')
save('l19_fog_density_rows', INSPECTOR, 'fog-density-rows')
save('l19_game_close', None, 'result-close')
