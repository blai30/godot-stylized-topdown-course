# Probes Blender's Save As file browser: its window, regions, and typing a new folder path.
import bpy


def steps(d):
    yield 2
    d.key('ESC')
    yield 0.5
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    yield 0.3
    d.key('S', ctrl=True, shift=True)
    yield 2
    windows = bpy.context.window_manager.windows
    d.log('WINDOWS {}'.format([(w.x, w.y, w.width, w.height, w.screen.name) for w in windows]))
    browser = windows[-1]
    for item in browser.screen.areas:
        d.log('AREA {} {} {} {} {}'.format(item.type, item.x, item.y, item.width, item.height))
        for region in item.regions:
            d.log('  REGION {} {} {} {} {}'.format(region.type, region.x, region.y, region.width, region.height))
    params = browser.screen.areas[0].spaces.active.params
    d.log('PARAMS dir {} file {}'.format(params.directory, params.filename))
    with bpy.context.temp_override(window=browser):
        bpy.ops.screen.screenshot(filepath=d.OUT + '/l09_probe_browser.png', check_existing=False)
    d.log('shot browser')
