# Crops the bonus lesson's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
shots = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'bonus-any-character')
os.makedirs(folder, exist_ok=True)
for name in os.listdir(folder):
    os.remove(os.path.join(folder, name))
for source, name in (('l63_advanced', 'advanced'), ('l63_skeleton', 'skeleton'), ('l63_bone_map_new', 'bone-map-new'),
                     ('l63_auto_mapped', 'auto-mapped'), ('l63_walk_pose', 'walk-pose')):
    image = Image.open(os.path.join(shots, source + '.png')).convert('RGB')
    if image.width > 1400:
        image = image.resize((1400, round(image.height * 1400 / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)
