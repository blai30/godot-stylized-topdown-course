# Crops lesson 56's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
godot = os.path.join(temp, 'sgt-phase2', 'shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'performance-and-export')
os.makedirs(folder, exist_ok=True)

# The Debugger's tabs hold a count of the test harness's own warnings, so the figures show the panel's body, below the tabs.
DEBUGGER = (288, 830, 1634, 1040)
BUILD_PROBLEMS = (288, 815, 862, 975)
EXPORT_FAILED = (868, 515, 1450, 560)
EXPORT_DONE = (868, 515, 1340, 550)


def save(source, name, box=None):
    image = Image.open(os.path.join(godot, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, name, box in (
        ('l56_monitors', 'monitors', DEBUGGER), ('l56_templates', 'templates', None), ('l56_preset', 'preset', None),
        ('l56_preset_set', 'preset-set', None), ('l56_msbuild', 'problems', BUILD_PROBLEMS), ('l56_msbuild', 'export-failed', EXPORT_FAILED),
        ('l56_second_result', 'export-done', EXPORT_DONE)):
    save(source, name, box)
