# Crops lesson 59's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'clean-up')
os.makedirs(folder, exist_ok=True)

# The Output panel's body, and its last line alone for the clean run (the harness adds a line of its own above it).
OUTPUT = (292, 812, 1630, 1000)
OUTPUT_LAST = (292, 830, 900, 860)
INSPECTOR_SCRIPT = (1640, 430, 1915, 470)
FILESYSTEM = (4, 600, 285, 1075)
BUILD_PROBLEMS = (288, 815, 1634, 1040)


def save(source, name, box=None, width=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box, width in (
        ('l59_audit_before', 'audit-before', OUTPUT, None), ('l59_audit_after', 'audit-after', OUTPUT_LAST, None),
        ('l59_script_cleared', 'script-cleared', INSPECTOR_SCRIPT, None), ('l59_delete_dialog', 'delete-dialog', None, None),
        ('l59_player_animation', 'player-animation', None, 1400), ('l59_moved', 'moved', FILESYSTEM, None),
        ('l59_style_error', 'style-error', BUILD_PROBLEMS, None)):
    save(source, name, box, width)
