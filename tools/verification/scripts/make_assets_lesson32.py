# Crops lesson 32's verified captures into the site's lesson assets (macOS run). The captures were copied out of the
# shots folder by the run, to /tmp/g32_shots.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'g32_shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'scatter-grass')
os.makedirs(folder, exist_ok=True)

for source, name in (('l32_flower_density', 'flower-density'), ('l32_grass_node', 'grass-node'), ('l32_scattered', 'scattered'),
                     ('l32_noon', 'noon'), ('l32_mid', 'mid'), ('l32_close', 'close'), ('l32_dusk', 'dusk'), ('l32_night', 'night'),
                     ('l32_built', 'built')):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)
