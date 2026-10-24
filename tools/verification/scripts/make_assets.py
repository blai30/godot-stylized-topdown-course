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

# Lesson 9 moved to the Module 2 section below: it was recaptured in Phase 2, the reader's way.

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

# Phase 2, Module 2. Lesson 7: Krita 5.3.4.1. Window captures are PrintWindow images, 1922 by 1112, title bar
# included; dialogs are grabbed from Krita itself.
krita = os.path.join(shots, 'krita')
CANVAS_CORNER = (370, 88, 990, 430)
SWATCH_ROWS = (375, 112, 1335, 485)
save(os.path.join(krita, 'k07_new_dimensions.png'), None, 'choose-your-palette', 'new-dimensions')
save(os.path.join(krita, 'k07_new_content.png'), None, 'choose-your-palette', 'new-content')
save(os.path.join(krita, 'k07_grid.png'), None, 'choose-your-palette', 'grid')
save(os.path.join(krita, 'k07_grid.png'), (1660, 752, 1922, 1035), 'choose-your-palette', 'grid-docker')
save(os.path.join(krita, 'k07_first_selection.png'), CANVAS_CORNER, 'choose-your-palette', 'first-selection')
save(os.path.join(krita, 'k07_first_selection.png'), (0, 52, 700, 88), 'choose-your-palette', 'toolbar')
save(os.path.join(krita, 'k07_color_hsv.png'), None, 'choose-your-palette', 'color-hsv')
save(os.path.join(krita, 'k07_first_swatch.png'), CANVAS_CORNER, 'choose-your-palette', 'first-swatch')
save(os.path.join(krita, 'k07_ramps.png'), SWATCH_ROWS, 'choose-your-palette', 'ramps')
save(os.path.join(krita, 'k07_filter_desaturate.png'), None, 'choose-your-palette', 'filter-layer')
save(os.path.join(krita, 'k07_value_check.png'), SWATCH_ROWS, 'choose-your-palette', 'value-check')
save(os.path.join(krita, 'k07_layers_hidden.png'), (1655, 250, 1922, 400), 'choose-your-palette', 'layers-hidden')
# Only the bottom of the Windows dialog: its folder view shows the computer's own drives and folders.
save(os.path.join(krita, 'k07_export_dialog.png'), (0, 630, 1186, 793), 'choose-your-palette', 'export-dialog')
save(os.path.join(krita, 'k07_png_options.png'), None, 'choose-your-palette', 'png-options')
palette = Image.open(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'snapshots', 'lesson-07', 'art', 'palette', 'palette.png')).convert('RGB')
palette.resize((512, 512), Image.NEAREST).save(os.path.join(site, 'choose-your-palette', 'palette.png'), optimize=True)

# Lesson 8: Blender 5.2.0 captures from Blender's own screenshot operator, 1920 by 1080.
blender = os.path.join(shots, 'blender')
for source, box, name in (
        ('l08_quick_setup', (700, 300, 1220, 780), 'quick-setup'),
        ('l08_layout', None, 'layout'),
        ('l08_view_pie', (560, 340, 1040, 660), 'view-pie'),
        ('l08_viewpoint_menu', (150, 20, 780, 500), 'viewpoint-menu'),
        ('l08_units', (1580, 220, 1920, 800), 'units'),
        ('l08_sidebar', (1250, 60, 1580, 520), 'sidebar'),
        ('l08_front', (0, 60, 1580, 980), 'front-view'),
        ('l08_selected_camera_light', (1580, 55, 1920, 160), 'outliner-selected'),
        ('l08_statistics_on', (1150, 20, 1590, 320), 'statistics'),
        ('l08_defaults_menu', (0, 0, 450, 450), 'defaults-menu'),
        ('l08_save_startup', (800, 482, 1116, 598), 'overwrite'),
        ('l08_new_menu', (642, 462, 766, 612), 'new-menu'),
        ('l08_save_changes', (740, 486, 1180, 594), 'save-changes'),
        ('l08_new_general', None, 'result')):
    save(os.path.join(blender, source + '.png'), box, 'blender-for-godot', name)

# Lesson 9, recaptured the reader's way on Blender 5.2.0 from lesson 8's startup file. The file browser shows the
# computer's own folders, so only its path field, file name field, and the folder prompt are kept.
VIEW3D = (0, 28, 1578, 980)
for source, box, name in (
        ('l09_start', VIEW3D, 'start'),
        ('l09_rename_field', (634, 455, 943, 527), 'rename'),
        ('l09_path_typed', (239, 0, 1060, 40), 'save-path'),
        ('l09_create_folder', (468, 4, 691, 73), 'create-folder'),
        ('l09_file_name', (239, 558, 1060, 600), 'save-name'),
        ('l09_dimensions', (1290, 55, 1578, 480), 'dimensions'),
        ('l09_apply_menu', (608, 458, 835, 818), 'apply-menu'),
        ('l09_loopcut_preview', VIEW3D, 'loop-cut'),
        ('l09_box_drag', VIEW3D, 'box-select'),
        ('l09_blocked', VIEW3D, 'blocked'),
        ('l09_transform_menu', (273, 27, 909, 364), 'transform-menu'),
        ('l09_randomized', (55, 853, 345, 989), 'randomize-panel'),
        ('l09_randomized', VIEW3D, 'randomized'),
        ('l09_object_menu', (280, 27, 495, 550), 'object-menu'),
        ('l09_smooth_only', VIEW3D, 'smooth-only'),
        ('l09_generate_menu', (1447, 237, 1829, 609), 'generate-menu'),
        ('l09_normals_menu', (1447, 218, 1829, 482), 'normals-menu'),
        ('l09_weighted', (1610, 237, 1920, 764), 'modifier-stack'),
        ('l09_final', (0, 82, 382, 227), 'statistics'),
        ('l09_front_origin', VIEW3D, 'front-origin'),
        ('l09_final', VIEW3D, 'final')):
    save(os.path.join(blender, source + '.png'), box, 'model-a-small-rock', name)

# Lesson 10, Blender 5.2.0 at the default scale. The status bar is left out: after the export it shows the full path.
for source, box, name in (
        ('l10_texture_solid', VIEW3D, 'before-uvs'),
        ('l10_mesh_name', (1580, 220, 1920, 420), 'mesh-name'),
        ('l10_material_tab', (1580, 220, 1920, 600), 'material-tab'),
        ('l10_base_color_menu', (1100, 480, 1920, 790), 'base-color-menu'),
        ('l10_image_texture', (1580, 440, 1920, 700), 'image-texture'),
        ('l10_open_list', (239, 0, 1060, 120), 'open-image'),
        ('l10_open_image', (239, 558, 1060, 600), 'open-image-button'),
        ('l10_interpolation_menu', (1580, 480, 1920, 780), 'interpolation'),
        ('l10_shading_popover', (1420, 30, 1740, 560), 'shading-popover'),
        ('l10_uv_workspace', None, 'uv-workspace'),
        ('l10_sync_off', (0, 26, 400, 80), 'sync-off'),
        ('l10_uv_sides', (0, 28, 788, 700), 'uv-collapsed'),
        ('l10_select_top', (791, 28, 1576, 980), 'select-top'),
        ('l10_colored', VIEW3D, 'colored'),
        ('l10_rename_collection', (1580, 40, 1920, 140), 'rename-collection'),
        ('l10_add_exporter', (1500, 560, 1920, 800), 'add-exporter'),
        ('l10_exporter_panel', (1600, 570, 1920, 940), 'exporter-panel'),
        ('l10_export_folder', (468, 4, 691, 73), 'export-folder'),
        ('l10_export_name', (239, 558, 1060, 600), 'export-name'),
        ('l10_images_menu', (1600, 720, 1920, 900), 'images-menu'),
        ('l10_exporter_settings', (1600, 220, 1920, 1060), 'exporter-settings'),
        ('l10_exported', VIEW3D, 'result')):
    save(os.path.join(blender, source + '.png'), box, 'color-and-export-the-rock', name)

# Lesson 11: Godot 4.8 beta1. The Advanced Import Settings window is captured at 3072 by 1280.
LEFT_DOCK = (0, 40, 286, 560)
for source, box, name, scale in (
        ('l11_palette_detect_before', LEFT_DOCK, 'palette-import', None),
        ('l11_palette_import_set', LEFT_DOCK, 'palette-detect-disabled', None),
        ('l11_glb_import_set', LEFT_DOCK, 'rock-extract', None),
        ('l11_material_before', INSPECTOR_DOCK, 'material-before', None),
        ('l11_quick_load', None, 'quick-load', None),
        ('l11_material_albedo', INSPECTOR_DOCK, 'material-albedo', None),
        ('l11_material_roughness', INSPECTOR_DOCK, 'material-roughness', None),
        ('l11_material_filter', INSPECTOR_DOCK, 'material-filter', None),
        ('l11_advanced', None, 'advanced', 0.5),
        ('l11_advanced_convex', None, 'advanced-convex', 0.5),
        ('l11_extract_folder', None, 'extract-folder', None),
        ('l11_color_white', None, 'color-picker', None),
        ('l11_advanced_convex', (2760, 40, 3072, 1000), 'advanced-physics', None),
        ('l11_inherit_dialog', None, 'inherit-dialog', None),
        ('l11_renamed_root', SCENE_DOCK, 'renamed-root', None),
        ('l11_save_scene', None, 'save-scene', None),
        ('l11_select_scene', None, 'select-scene', None),
        ('l11_rock_inspector', INSPECTOR_DOCK, 'rock-inspector', None),
        ('l11_meadow_rocks', None, 'meadow-rocks', None),
        ('l11_game_close', None, 'result', None)):
    save(source + '.png', box, 'import-the-rock', name, scale)
running('l11_running.png', 'l11_game_start.png', 'import-the-rock', 'running')

# Lesson 12: Blender 5.2.0 at the default scale, then Godot 4.8 beta1.
for source, box, name in (
        ('l12_renamed', (1580, 40, 1920, 140), 'renamed'),
        ('l12_dimensions', (1290, 55, 1578, 480), 'dimensions'),
        ('l12_bevel', (1600, 240, 1920, 560), 'bevel'),
        ('l12_shading_flat', (1420, 30, 1740, 420), 'shading-flat'),
        ('l12_silhouette_before', VIEW3D, 'silhouette-before'),
        ('l12_reshaped', VIEW3D, 'reshaped'),
        ('l12_silhouette_after', VIEW3D, 'silhouette-after'),
        ('l12_uv_moved', (0, 28, 788, 700), 'uv-moved'),
        ('l12_colored', VIEW3D, 'colored'),
        ('l12_exporter_path', (1600, 570, 1920, 800), 'exporter-path')):
    save(os.path.join(blender, source + '.png'), box, 'a-large-rock-and-variants', name)
for source, box, name, scale in (
        ('l12_extract', LEFT_DOCK, 'extract', None),
        ('l12_advanced', None, 'advanced', 0.5),
        ('l12_select_scene', None, 'select-scene', None),
        ('l12_rock_inspector', INSPECTOR_DOCK, 'rock-inspector', None),
        ('l12_meadow_editor', None, 'meadow-editor', None),
        ('l12_game_close', None, 'result', None)):
    save(source + '.png', box, 'a-large-rock-and-variants', name, scale)
running('l12_running.png', 'l12_game_wide.png', 'a-large-rock-and-variants', 'running')

# Lesson 13: Krita 5.3.4.1, then Godot 4.8 beta1. The result is the exported texture repeated three by three.
KRITA_CANVAS = (74, 118, 1640, 1066)
# The Brush Editor's middle: the option list and the shown option's settings. Its captures include the title bar.
EDITOR_OPTIONS = (301, 121, 1061, 641)
EDITOR_TIP = (481, 126, 1046, 591)
for source, box, name in (
        ('k13_new_dimensions', None, 'new-dimensions'),
        ('k13_color_base', None, 'color-shadow'),
        ('k13_blade_settings', EDITOR_OPTIONS, 'blade-settings'),
        ('k13_blade_settings', (1191, 36, 1346, 101), 'save-new-preset'),
        ('k13_save_preset', None, 'save-preset'),
        ('k13_tufts_alone', KRITA_CANVAS, 'tufts'),
        ('k13_stamp', None, 'stamp'),
        ('k13_tuft_tip', EDITOR_TIP, 'tuft-tip'),
        ('k13_tuft_rotation', EDITOR_OPTIONS, 'tuft-rotation'),
        ('k13_tuft_size', EDITOR_OPTIONS, 'tuft-size'),
        ('k13_tuft_scatter', EDITOR_OPTIONS, 'tuft-scatter'),
        ('k13_pass_dark', KRITA_CANVAS, 'pass-dark'),
        ('k13_pass_light', KRITA_CANVAS, 'pass-light'),
        ('k13_pass_highlight', KRITA_CANVAS, 'pass-highlight'),
        ('k13_pass_dark', (690, 52, 1040, 88), 'toolbar-sliders'),
        ('k13_pass_dark', (1660, 684, 1922, 1080), 'preset-search'),
        ('k13_far', KRITA_CANVAS, 'far'),
        ('k_grass_albedo_png_options', None, 'png-options')):
    save(os.path.join(krita, source + '.png'), box, 'paint-a-grass-texture', name)
for source, box, name in (
        ('l13_import_before', LEFT_DOCK, 'import-before'),
        ('l13_import_set', LEFT_DOCK, 'import-set')):
    save(source + '.png', box, 'paint-a-grass-texture', name)
grass = Image.open(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'snapshots', 'lesson-13', 'art', 'ground', 'grass_albedo.png')).convert('RGB')
tiled = Image.new('RGB', (grass.width * 3, grass.height * 3))
for column in range(3):
    for row in range(3):
        tiled.paste(grass, (column * grass.width, row * grass.height))
tiled.resize((1152, 1152), Image.LANCZOS).save(os.path.join(site, 'paint-a-grass-texture', 'result.png'), optimize=True)

# Lesson 14: Krita 5.3.4.1, then Godot 4.8 beta1. The result is the three ground textures side by side.
PEBBLE = (700, 470, 1015, 690)
for source, box, name in (
        ('k14_dirt_blotches', KRITA_CANVAS, 'blotches'),
        ('k14_pebble_body', PEBBLE, 'pebble-body'),
        ('k14_pebble', PEBBLE, 'pebble'),
        ('k14_pebble_tip', EDITOR_TIP, 'pebble-tip'),
        ('k14_pebble_size', EDITOR_OPTIONS, 'pebble-size'),
        ('k14_dirt_pebbles', KRITA_CANVAS, 'pebbles'),
        ('k14_dirt_details', KRITA_CANVAS, 'twigs'),
        ('k14_dirt_far', KRITA_CANVAS, 'dirt-far'),
        ('k14_sand_damp', KRITA_CANVAS, 'damp'),
        ('k14_sand_ripples', KRITA_CANVAS, 'ripples'),
        ('k14_sand_details', KRITA_CANVAS, 'sand-details'),
        ('k14_sand_far', KRITA_CANVAS, 'sand-far')):
    save(os.path.join(krita, source + '.png'), box, 'paint-dirt-and-sand', name)
save('l14_sand_albedo_import.png', LEFT_DOCK, 'paint-dirt-and-sand', 'import-sand')
ground = os.path.join(os.environ['TEMP'], 'sgt-phase1', 'snapshots', 'lesson-14', 'art', 'ground')
row = Image.new('RGB', (512 * 3 + 32, 512), 'white')
for column, name in enumerate(('grass', 'dirt', 'sand')):
    row.paste(Image.open(os.path.join(ground, name + '_albedo.png')).convert('RGB'), (column * 528, 0))
row.save(os.path.join(site, 'paint-dirt-and-sand', 'result.png'), optimize=True)

# Lesson 15: Godot 4.8 beta1, rebuilt on top of lesson 14.
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

# Lesson 16: Godot 4.8 beta1. With the GridMap panel open, the 3D view ends above it at y 830.
VIEW_WITH_GRIDMAP = (288, 114, 1633, 990)
for source, box, name in (
        ('l16_delete_confirm', None, 'delete-confirm'),
        ('l16_grass_tile', INSPECTOR_DOCK, 'grass-tile'),
        ('l16_make_unique', INSPECTOR_DOCK, 'make-unique'),
        ('l16_tiles_scene', (0, 40, 1633, 1040), 'tiles-scene'),
        ('l16_save_tiles', None, 'save-tiles'),
        ('l16_export', None, 'export'),
        ('l16_gridmap_inspector', INSPECTOR_DOCK, 'gridmap-inspector'),
        ('l16_selection', VIEW_WITH_GRIDMAP, 'selection'),
        ('l16_grass_filled', VIEW_WITH_GRIDMAP, 'grass-filled'),
        ('l16_painted', VIEW_WITH_GRIDMAP, 'painted'),
        ('l16_game_wide', None, 'result')):
    save(source + '.png', box, 'tiles-and-gridmap', name)
running('l16_running.png', 'l16_game_wide.png', 'tiles-and-gridmap', 'running')

# Lesson 17: Godot 4.8 beta1.
TILES_CLOSE = (860, 330, 1520, 650)
for source, box, name in (
        ('l17_grass_mesh', INSPECTOR_DOCK, 'grass-mesh'),
        ('l17_piece1_tiles', TILES_CLOSE, 'piece-1-tiles'),
        ('l17_piece1_meadow', VIEW_WITH_PANEL, 'piece-1-meadow'),
        ('l17_noise_settings', INSPECTOR_DOCK, 'noise-settings'),
        ('l17_save_noise', None, 'save-noise'),
        ('l17_piece2_tiles', TILES_CLOSE, 'piece-2-tiles'),
        ('l17_piece2_meadow', VIEW_WITH_PANEL, 'piece-2-meadow'),
        ('l17_game_close', None, 'result')):
    save(source + '.png', box, 'soft-tile-edges', name)
