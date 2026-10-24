# Checks whether synthetic canvas input reaches tools: a brush stroke, read back from the layer's pixels.
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton


def steps(d):
    yield 2
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), 256)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), 256)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    document = d.Krita.instance().activeDocument()
    d.action('select_all')
    yield 1
    d.log('AFTER SELECT ALL: {}'.format(document.selection()))
    d.action('deselect')
    yield 1
    canvas = d.of_class(d.window(), 'KisOpenGLCanvas2')
    d.log('canvas focus policy {} hasFocus {} active {}'.format(canvas.focusPolicy(), canvas.hasFocus(), d.window().isActiveWindow()))
    d.action('KritaShape/KisToolBrush')
    yield 1
    yield from d.drag(canvas, QPoint(400, 200), QPoint(900, 600), steps=20)
    yield 2
    node = document.activeNode()
    data = bytes(node.pixelData(0, 0, 256, 256))
    painted = sum(1 for i in range(3, len(data), 4) if data[i] > 0)
    d.log('PAINTED PIXELS {}'.format(painted))
    d.action('KisToolSelectRectangular')
    yield 1
    yield from d.drag(canvas, QPoint(400, 200), QPoint(900, 600), steps=20)
    yield 2
    d.log('SELECTION {}'.format(document.selection()))
    d.shot('k07_probe_stroke')
