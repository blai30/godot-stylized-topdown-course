# Crops lesson 26's verified captures into the site's lesson assets (macOS run).
import os
from PIL import Image

shots = os.path.join(os.environ.get('TEMP', '/tmp'), 'sgt-phase2', 'shots')
blender = os.path.join(shots, 'blender')
site = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'site', 'src', 'assets', 'lessons')
folder = os.path.join(site, 'leaf-cards')
os.makedirs(folder, exist_ok=True)

VIEW3D = (0, 28, 1578, 980)
PANEL = (1579, 225, 1920, 720)


def save(source, box, name, directory=blender):
    image = Image.open(os.path.join(directory, source + '.png')).convert('RGB')
    if box:
        image = image.crop(box)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(name, image.size)


for source, box, name in (
        ('l26_crown', VIEW3D, 'crown'),
        ('l26_add_search', VIEW3D, 'add-sphere'),
        ('l26_envelope', VIEW3D, 'envelope'),
        ('l26_new_group', None, 'new-group'),
        ('l26_node_menu', (0, 60, 1920, 1050), 'node-menu'),
        ('l26_node_search', (0, 60, 1920, 1050), 'node-search'),
        ('l26_clumps_linked', (0, 60, 1920, 1050), 'clumps-nodes'),
        ('l26_clumps_view', None, 'clumps-view'),
        ('l26_spheres_linked', (0, 60, 1920, 1050), 'spheres-nodes'),
        ('l26_spheres_view', None, 'spheres-view'),
        ('l26_cards_linked', (0, 60, 1920, 1050), 'cards-nodes'),
        ('l26_cards_view', None, 'cards-view'),
        ('l26_data_linked', (0, 60, 1920, 1050), 'data-nodes'),
        ('l26_shading_linked', (0, 60, 1920, 1050), 'shading-nodes'),
        ('l26_shading_view', None, 'shading-view'),
        ('l26_color_attributes', PANEL, 'color-attributes'),
        ('l26_color_attribute_dialog', (1579, 380, 1920, 600), 'color-dialog'),
        ('l26_color_attribute_added', PANEL, 'color-added'),
        ('l26_vertex_color_settings', PANEL, 'exporter-colors')):
    save(source, box, name)
save('l26_tree_scene', None, 'tree-scene', shots)
