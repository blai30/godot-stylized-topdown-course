# Captures the menus and panels lesson 8 clicks, opened from their real buttons at Blender's default interface scale.
import bpy


def top(y):
    return 1080 - y


def steps(d):
    yield 2
    d.click(959, top(738))
    yield 1
    d.key('ESC')
    yield 0.5
    viewport = d.area('VIEW_3D')
    yield from d.press(40, top(13))
    yield 0.6
    d.shot('p8_file_menu')
    d.move(100, top(406))
    yield 0.8
    d.shot('p8_defaults')
    d.key('ESC')
    yield 0.3
    d.key('ESC')
    yield 0.4
    yield from d.press(183, top(38))
    yield 0.6
    d.shot('p8_view_menu')
    d.key('ESC')
    yield 0.4
    yield from d.press(1431, top(38))
    yield 0.6
    d.shot('p8_overlays')
    d.key('ESC')
    yield 0.4
    yield from d.press(1595, top(385))
    yield 0.6
    d.move(1760, top(1000))
    yield 0.4
    d.shot('p8_scene_tab')
    d.log('TAB {}'.format(d.area('PROPERTIES').spaces.active.context))
