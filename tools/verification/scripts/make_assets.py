# Crops the verified captures into the site's lesson assets. Every image comes from a real tool run in this phase.
import os
from PIL import Image

shots = os.path.join(os.environ['TEMP'], 'sgt-phase1', 'shots')
site = r'C:\Users\Brian\Development\Godot\StylizedGameTemplateCourse\site\src\assets\lessons'
VIEW_WITH_PANEL = (288, 114, 1633, 726)
INSPECTOR = (1636, 40, 1920, 1080)

def save(source, box, lesson, name, scale=None):
    image = Image.open(os.path.join(shots, source)).convert('RGB')
    if box:
        image = image.crop(box)
    if scale:
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    folder = os.path.join(site, lesson)
    os.makedirs(folder, exist_ok=True)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(lesson, name, image.size)

# Lesson 1: download pages and first launch.
for page in ('godot', 'dotnet', 'blender_download', 'krita', 'git', 'rider', 'vscode'):
    save(os.path.join('web', page + '.png'), None, 'install-everything', page.replace('_download', ''))
save('project_manager_first_launch.png', None, 'install-everything', 'project-manager')

# Lesson 9: Blender 5.2 captures, the 3D view without the timeline, and the modifier stack.
BLENDER_VIEW = (0, 24, 1640, 700)
for name in ('start', 'blocked', 'randomized', 'smooth_only', 'front_origin', 'final'):
    save(os.path.join('blender', f'l09_{name}.png'), BLENDER_VIEW, 'model-a-small-rock', name.replace('_', '-'))
save(os.path.join('blender', 'l09_weighted.png'), (1600, 60, 1920, 760), 'model-a-small-rock', 'modifier-stack')
save(os.path.join('blender', 'l09_weighted.png'), (0, 30, 400, 230), 'model-a-small-rock', 'statistics')

# Lesson 15: Godot 4.8 beta1 editor captures.
save('l15_create_node.png', None, 'your-first-shader', 'create-new-node')
save('l15_mesh_menu.png', (1300, 140, 1920, 960), 'your-first-shader', 'mesh-menu')
save('l15_shader_menu.png', (1500, 560, 1920, 1080), 'your-first-shader', 'shader-menu')
save('l15_create_shader.png', None, 'your-first-shader', 'create-shader-dialog')
save('l15_after_create.png', None, 'your-first-shader', 'shader-editor')
save('l15_piece1.png', VIEW_WITH_PANEL, 'your-first-shader', 'piece-1')
save('l15_piece2.png', VIEW_WITH_PANEL, 'your-first-shader', 'piece-2')
save('l15_uv_problem.png', VIEW_WITH_PANEL, 'your-first-shader', 'uv-problem')
save('l15_piece3.png', VIEW_WITH_PANEL, 'your-first-shader', 'world-space-icons')
save('l15_piece3_grass.png', VIEW_WITH_PANEL, 'your-first-shader', 'world-space-grass')
save('l15_nested_parameters.png', INSPECTOR, 'your-first-shader', 'nested-parameters')
