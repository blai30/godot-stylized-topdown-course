# Proves the Blender driver: the first-launch splash, simulated mouse and keys, and screenshots.
import bpy


def steps(d):
    yield 2
    d.click(958, 1080 - 756)
    yield 1.5
    d.shot('l08_probe_after_continue')
    d.log('USERPREF saved? {}'.format(bpy.context.preferences.is_dirty))
    # Esc closes the second splash.
    d.key('ESC')
    yield 0.5
    d.shot('l08_probe_splash_closed')
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    yield 0.3
    d.key('N')
    yield 1
    d.shot('l08_probe_sidebar')
    d.log('SIDEBAR visible {}'.format(viewport.spaces.active.show_region_ui))
