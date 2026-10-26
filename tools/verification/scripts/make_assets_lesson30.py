# Crops lesson 30's verified captures into the site's lesson assets (macOS run). The Blender and Godot captures were
# copied out of the shots folders by the run, to /tmp/b30_shots and /tmp/g30_shots.
import os
from PIL import Image

temp = os.environ.get('TEMP', '/tmp')
blender = os.path.join(temp, 'b30_shots')
godot = os.path.join(temp, 'g30_shots')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'model-grass-and-flowers')
os.makedirs(folder, exist_ok=True)

VIEW3D = (0, 28, 1578, 980)
NODES = (0, 60, 1920, 1050)
PROPS = (1580, 225, 1920, 1060)
OUTLINER = (1580, 50, 1920, 215)


def save(source, box, name, directory, scale=1.0):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    if scale != 1.0:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)
    return image


for source, box, name, directory, scale in (
        ('l30_quad', VIEW3D, 'quad', blender, 1.0), ('l30_tip_row', VIEW3D, 'tip-row', blender, 1.0), ('l30_blade_object', VIEW3D, 'blade', blender, 1.0),
        ('l30_three_blades', VIEW3D, 'three-blades', blender, 1.0), ('l30_bends_together', VIEW3D, 'bends', blender, 1.0), ('l30_collections_ready', OUTLINER, 'collections', blender, 2.0),
        ('l30_footprint', VIEW3D, 'footprint', blender, 1.0), ('l30_new_group', None, 'new-group', blender, 1.0),
        ('l30_feet_linked', NODES, 'feet-nodes', blender, 1.0), ('l30_blades_linked', NODES, 'blades-nodes', blender, 1.0),
        ('l30_blades_view', VIEW3D, 'blades-view', blender, 1.0), ('l30_colors_linked', NODES, 'colors-nodes', blender, 1.0),
        ('l30_seed', (1580, 225, 1920, 520), 'seed', blender, 2.0), ('l30_three_clumps', VIEW3D, 'three-clumps', blender, 1.0),
        ('l30_apply_menu', (480, 380, 1040, 900), 'apply-menu', blender, 1.0),
        ('l30_daisy_parts', VIEW3D, 'daisy-parts', blender, 1.0), ('l30_paint_linked', NODES, 'paint-nodes', blender, 1.0),
        ('l30_paint_stem', (1580, 225, 1920, 520), 'paint-modifier', blender, 2.0), ('l30_link_menu', (280, 30, 700, 860), 'link-menu', blender, 1.0),
        ('l30_flowers_built', VIEW3D, 'flowers-built', blender, 1.0), ('l30_convert_menu', (280, 30, 700, 760), 'convert-menu', blender, 1.0),
        ('l30_flowers_view', VIEW3D, 'flowers-view', blender, 1.0), ('l30_clumps_view', VIEW3D, 'clumps-view', blender, 1.0),
        ('l30_exporter_path', PROPS, 'exporter', blender, 1.0), ('l30_vertex_colors', PROPS, 'vertex-colors', blender, 1.0),
        ('l30_import_lods_off', None, 'import-lods-off', godot, 1.0), ('l30_advanced', None, 'advanced', godot, 0.6)):
    save(source, box, name, directory, scale)

