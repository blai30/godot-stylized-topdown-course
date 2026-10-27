# Crops lesson 42's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'import-ual')
os.makedirs(folder, exist_ok=True)
for name in os.listdir(folder):
    os.remove(os.path.join(folder, name))


def save(source, name, box=None, width=1400):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name in (('l42_import_dock', 'import-dock'), ('l42_library_dock', 'library-dock'), ('l42_advanced', 'advanced'),
                     ('l42_skeleton', 'skeleton'), ('l42_bone_map_new', 'bone-map-new'), ('l42_auto_mapped', 'auto-mapped'),
                     ('l42_walk', 'walk'), ('l42_loop_walk', 'loop-walk'), ('l42_player_added', 'player-added'),
                     ('l42_player_library', 'player-library'), ('l42_walk_pose', 'walk-pose')):
    save(source, name)
for index in range(3):
    save('l42_walk_%d' % index, 'walk-%d' % index, box=(440, 140, 840, 540), width=None)
save('l42_run', 'run', box=(440, 140, 840, 540), width=None)
save('l42_idle', 'idle', box=(440, 140, 840, 540), width=None)
