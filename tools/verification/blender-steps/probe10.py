# Finds the mesh name field on the Data tab.
import bpy


def steps(d):
    yield 2
    d.wake()
    yield 0.5
    yield from d.press(1595, 1080 - 626)
    yield 0.6
    d.move(1760, 80)
    yield 0.3
    d.shot('p10_data_tab')
