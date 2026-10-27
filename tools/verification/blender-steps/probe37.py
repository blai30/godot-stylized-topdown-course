import os, sys, bpy
sys.path.insert(0, os.path.dirname(__file__))
from lesson30 import slow_click, top
def steps(d):
    yield 2
    d.wake()
    yield 0.5
    d.key('ESC')
    viewport = d.area('VIEW_3D')
    d.move(*d.center(viewport))
    d.move(228, top(38)); yield 0.6
    d.window().event_simulate('LEFTMOUSE', 'PRESS', x=228, y=top(38))
    d.window().event_simulate('LEFTMOUSE', 'RELEASE', x=228, y=top(38))
    yield 1.5
    d.move(231, top(41)); yield 0.8
    d.shot('p37_select_menu')
    for y in range(80, 330, 15):
        d.move(250, top(y))
        yield 0.12
    d.shot('p37_select_menu2')
