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

# Phase 2, Module 1: Godot 4.8 beta1 captures.
shots = os.path.join(os.environ['TEMP'], 'sgt-phase2', 'shots')
SCENE_DOCK = (0, 40, 286, 556)
FILESYSTEM_DOCK = (0, 560, 286, 900)
DIALOG_PANEL = (200, 80, 1200, 650)

# Lesson 2.
save('pm_create_typed.png', None, 'create-the-project', 'create-new-project')
save('l02_editor_first.png', None, 'create-the-project', 'editor')
save('l02_editor_settings.png', None, 'create-the-project', 'external-editor')
save('l02_create_folder.png', None, 'create-the-project', 'create-folder')
save('l02_folders.png', FILESYSTEM_DOCK, 'create-the-project', 'folders')
save('l02_reopened.png', FILESYSTEM_DOCK, 'create-the-project', 'folders-gdignore')
save('l02_reopened.png', None, 'create-the-project', 'result')
save('pm_listed.png', None, 'create-the-project', 'project-listed')

# Lesson 3. The settings tree's highlight stays on Config when a section is picked by the driver, so the General tab
# shots show only the settings panel.
save('l03_window.png', DIALOG_PANEL, 'project-settings', 'window-size')
save('l03_vsync.png', DIALOG_PANEL, 'project-settings', 'vsync')
save('l03_physics.png', None, 'project-settings', 'physics-interpolation')
save('l03_layers.png', None, 'project-settings', 'layer-names')
save('l03_actions_added.png', None, 'project-settings', 'actions-added')
save('l03_event_key.png', None, 'project-settings', 'event-key')
save('l03_event_stick.png', None, 'project-settings', 'event-stick')
save('l03_event_wheel.png', None, 'project-settings', 'event-wheel')
save('l03_event_shift.png', None, 'project-settings', 'event-shift')
save('l03_input_map.png', None, 'project-settings', 'input-map')

# Lesson 4.
VIEWPORT = (288, 114, 1633, 1032)
INSPECTOR_DOCK = (1636, 40, 1920, 1080)
save('l04_final.png', VIEWPORT, 'a-first-scene', 'result')
save('l04_start.png', SCENE_DOCK, 'a-first-scene', 'create-root-node')
save('l04_save_dialog_levels.png', None, 'a-first-scene', 'save-scene')
save('l04_ground_inspector.png', INSPECTOR_DOCK, 'a-first-scene', 'plane-mesh')
save('l04_ground.png', VIEWPORT, 'a-first-scene', 'ground-preview')
save('l04_ground.png', (288, 74, 1100, 112), 'a-first-scene', 'preview-buttons')
save('l04_environment_added.png', None, 'a-first-scene', 'environment-added')
save('l04_new_sky.png', INSPECTOR_DOCK, 'a-first-scene', 'new-sky')
save('l04_environment_sky.png', INSPECTOR_DOCK, 'a-first-scene', 'procedural-sky')
save('l04_environment_tonemap.png', INSPECTOR_DOCK, 'a-first-scene', 'tonemap')
save('l04_with_environment.png', VIEWPORT, 'a-first-scene', 'with-sky')
save('l04_sun_added.png', VIEWPORT, 'a-first-scene', 'sun-default')
save('l04_sun_rotation.png', INSPECTOR_DOCK, 'a-first-scene', 'sun-rotation')
save('l04_sun_shadow.png', INSPECTOR_DOCK, 'a-first-scene', 'sun-shadow')
save('l04_box_low_sun.png', VIEWPORT, 'a-first-scene', 'low-sun')
save('l04_delete_confirm.png', None, 'a-first-scene', 'delete-confirm')
save('l04_final.png', SCENE_DOCK, 'a-first-scene', 'scene-tree')

# Lesson 5. The workbench has no external editor set, so Godot's own script editor shows in some captures; the lesson
# uses only the parts a reader with Rider or VS Code also sees.
save('l05_game_default.png', None, 'the-camera-rig', 'result')
save('l05_rig_scene.png', None, 'the-camera-rig', 'rig-scene')
save('l04_environment_added.png', (0, 70, 286, 110), 'the-camera-rig', 'attach-button')
save('l05_export_empty.png', (1680, 0, 1920, 40), 'the-camera-rig', 'build-button')
save('l05_camera_inspector.png', INSPECTOR_DOCK, 'the-camera-rig', 'camera-inspector')
save('l05_attach_script.png', None, 'the-camera-rig', 'attach-script')
save('l05_export_empty.png', INSPECTOR_DOCK, 'the-camera-rig', 'export-empty')
save('l05_select_node.png', None, 'the-camera-rig', 'select-node')
save('l05_export_assigned.png', INSPECTOR_DOCK, 'the-camera-rig', 'export-assigned')
save('l05_instantiate.png', None, 'the-camera-rig', 'instantiate')
save('l05_main_scene_dialog.png', None, 'the-camera-rig', 'main-scene-dialog')
save('l05_game_zoom_in.png', None, 'the-camera-rig', 'zoom-in')
save('l05_game_zoom_out.png', None, 'the-camera-rig', 'zoom-out')
save('l05_exports_final.png', INSPECTOR_DOCK, 'the-camera-rig', 'exports-final')

# Lesson 6.
save('l06_game_close.png', None, 'a-player-capsule', 'result')
save('l06_create_root.png', None, 'a-player-capsule', 'create-root')
save('l06_warning.png', (0, 40, 286, 160), 'a-player-capsule', 'warning')
save('l06_capsule_set.png', (1636, 40, 1920, 600), 'a-player-capsule', 'capsule-shape')
save('l06_shape_added.png', (0, 40, 286, 180), 'a-player-capsule', 'shape-added')
save('l06_mesh_menu.png', (900, 74, 1500, 400), 'a-player-capsule', 'mesh-menu')
save('l06_layers.png', INSPECTOR_DOCK, 'a-player-capsule', 'layers')
save('l06_player_scene.png', None, 'a-player-capsule', 'player-scene')
save('l06_attach_script.png', None, 'a-player-capsule', 'attach-script')
save('l06_collision_dialog_set.png', None, 'a-player-capsule', 'collision-dialog')

save('l06_rig_target_empty.png', (1636, 40, 1920, 600), 'a-player-capsule', 'target-empty')
save('l06_select_player.png', None, 'a-player-capsule', 'select-player')
save('l06_game_walk_right.png', None, 'a-player-capsule', 'walk-right')
save('l06_meadow_editor.png', SCENE_DOCK, 'a-player-capsule', 'meadow-tree')

# The game runs embedded in the editor's Game tab, in its own native window that an editor capture shows as gray. The
# game's own frame from the same run is 1217 by 685, the size of that area, and is placed where it sits.
GAME_AREA = (351, 116)

def running(editor_shot, game_shot, lesson, name):
    image = Image.open(os.path.join(shots, editor_shot)).convert('RGB')
    image.paste(Image.open(os.path.join(shots, game_shot)).convert('RGB'), GAME_AREA)
    folder = os.path.join(site, lesson)
    os.makedirs(folder, exist_ok=True)
    image.save(os.path.join(folder, name + '.png'), optimize=True)
    print(lesson, name, image.size)

running('l05_running.png', 'l05_game_first.png', 'the-camera-rig', 'running')
running('l06_running.png', 'l06_game_start.png', 'a-player-capsule', 'running')
