# Crops the captures of Module 3's ground lessons (13 to 17) into the site's lesson assets, from a run of
# `sgt.py chain module3`. The Krita figures of lesson 14 that did not change keep the images already in the site.
import os
import tempfile
from PIL import Image

TEMP = os.environ.get('TEMP', tempfile.gettempdir())
shots = os.path.join(TEMP, 'sgt-phase2', 'shots')
krita = os.path.join(shots, 'krita')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
snapshots = os.path.join(TEMP, 'sgt-phase1', 'snapshots')
VIEW_WITH_PANEL = (288, 114, 1633, 726)
VIEW_WITH_GRIDMAP = (288, 114, 1633, 990)
INSPECTOR = (1636, 40, 1920, 1080)
INSPECTOR_DOCK = (1636, 40, 1920, 1080)
LEFT_DOCK = (0, 40, 286, 560)
TILES_CLOSE = (860, 330, 1520, 650)


def save(source, box, lesson, name, scale=None):
    image = Image.open(source).convert('RGB')
    if box:
        image = image.crop(box)
    if scale:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    folder = os.path.join(site, lesson)
    os.makedirs(folder, exist_ok=True)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(lesson, name, image.size)


def shot(name):
    return os.path.join(shots, name + '.png')


def tiled(path, size, copies):
    image = Image.open(path).convert('RGB')
    sheet = Image.new('RGB', (image.width * copies, image.height * copies))
    for column in range(copies):
        for row in range(copies):
            sheet.paste(image, (column * image.width, row * image.height))
    return sheet.resize((size, size), Image.LANCZOS)


# Lesson 13: the grass detail, drawn by a script in Godot.
lesson = 'generate-grass-detail'
save(shot('l13_new_script'), None, lesson, 'new-script')
save(shot('l13_piece2'), (352, 312, 672, 552), lesson, 'piece-2')
save(shot('l13_piece3'), (0, 0, 512, 512), lesson, 'piece-3')
save(shot('l13_piece4'), (0, 0, 512, 512), lesson, 'piece-4')
save(shot('l13_import_before'), LEFT_DOCK, lesson, 'import-before')
save(shot('l13_import_set'), LEFT_DOCK, lesson, 'import-set')
folder = os.path.join(site, lesson)
os.makedirs(folder, exist_ok=True)
tiled(shot('l13_piece4'), 1024, 2).save(os.path.join(folder, 'result.png'), optimize=True)

# Lesson 14: the new figures; the painting figures keep their images. Krita's captures are the window's pixels.
lesson = 'paint-dirt-and-sand'
save(os.path.join(krita, 'k14_dirt_new_dimensions.png'), None, lesson, 'new-dimensions')
save(os.path.join(krita, 'k14_preset_search.png'), None, lesson, 'preset-search')
save(os.path.join(krita, 'k14_taper_settings.png'), None, lesson, 'taper-settings')
save(os.path.join(krita, 'k14_save_preset.png'), None, lesson, 'save-preset')
save(os.path.join(krita, 'k_dirt_albedo_png_options.png'), None, lesson, 'png-options')
KRITA_CANVAS = (72, 66, 1640, 1036)
PEBBLE = (740, 420, 990, 640)
for source, box, name in (
        ('k14_dirt_blotches', KRITA_CANVAS, 'blotches'),
        ('k14_pebble_body', PEBBLE, 'pebble-body'),
        ('k14_pebble', PEBBLE, 'pebble'),
        ('k14_pebble_tip', None, 'pebble-tip'),
        ('k14_pebble_size', None, 'pebble-size'),
        ('k14_dirt_pebbles', KRITA_CANVAS, 'pebbles'),
        ('k14_dirt_details', KRITA_CANVAS, 'twigs'),
        ('k14_dirt_far', KRITA_CANVAS, 'dirt-far')):
    save(os.path.join(krita, source + '.png'), box, lesson, name)
ground = os.path.join(snapshots, 'lesson-14', 'art', 'ground')
row = Image.new('RGB', (512 * 2 + 16, 512), 'white')
for column, name in enumerate(('dirt', 'sand')):
    row.paste(Image.open(os.path.join(ground, name + '_albedo.png')).convert('RGB'), (column * 528, 0))
row.save(os.path.join(site, lesson, 'result.png'), optimize=True)

# Lesson 15.
lesson = 'your-first-shader'
save(shot('l15_piece1'), VIEW_WITH_PANEL, lesson, 'piece-1')
save(shot('l15_piece2'), VIEW_WITH_PANEL, lesson, 'piece-2')
save(shot('l15_uv_problem'), VIEW_WITH_PANEL, lesson, 'uv-problem')
save(shot('l15_piece3'), VIEW_WITH_PANEL, lesson, 'world-space-icons')
save(shot('l15_piece3_grass'), VIEW_WITH_PANEL, lesson, 'world-space-grass')
save(shot('l15_nested_parameters'), INSPECTOR, lesson, 'nested-parameters')

# Lesson 16.
lesson = 'tiles-and-gridmap'
for source, box, name in (
        ('l16_grass_tile', INSPECTOR_DOCK, 'grass-tile'),
        ('l16_make_unique', INSPECTOR_DOCK, 'make-unique'),
        ('l16_tiles_scene', (0, 40, 1633, 1040), 'tiles-scene'),
        ('l16_selection', VIEW_WITH_GRIDMAP, 'selection'),
        ('l16_grass_filled', VIEW_WITH_GRIDMAP, 'grass-filled'),
        ('l16_painted', VIEW_WITH_GRIDMAP, 'painted'),
        ('l16_game_wide', None, 'result')):
    save(shot(source), box, lesson, name)
# The running game: the game's own window, since the runner plays it outside the editor.
save(shot('l16_game_wide'), None, lesson, 'running')

# Lesson 17.
lesson = 'soft-tile-edges'
for source, box, name in (
        ('l17_grass_mesh', INSPECTOR_DOCK, 'grass-mesh'),
        ('l17_piece1_tiles', TILES_CLOSE, 'piece-1-tiles'),
        ('l17_piece1_meadow', VIEW_WITH_PANEL, 'piece-1-meadow'),
        ('l17_noise_settings', INSPECTOR_DOCK, 'noise-settings'),
        ('l17_piece2_tiles', TILES_CLOSE, 'piece-2-tiles'),
        ('l17_piece2_meadow', VIEW_WITH_PANEL, 'piece-2-meadow'),
        ('l17_msaa', None, 'msaa'),
        ('l17_game_close', None, 'result')):
    save(shot(source), box, lesson, name)
