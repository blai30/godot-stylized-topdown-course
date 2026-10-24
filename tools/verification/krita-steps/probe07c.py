# Probes the palette workflow: grid docker, snapping, rectangular selection, the color dialog, fill, and export.
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QAbstractSpinBox, QDockWidget, QPushButton, QApplication



def image_rect(canvas):
    # The canvas shows the white image on a gray surround; its bounds map image pixels to widget pixels.
    image = canvas.grab().toImage()
    xs, ys = [], []
    for y in range(0, image.height(), 4):
        for x in range(0, image.width(), 4):
            if QColor(image.pixel(x, y)).lightness() > 250:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def visible_titles():
    return [w.windowTitle() + '<' + w.metaObject().className() + '>' for w in QApplication.topLevelWidgets() if w.isVisible()]


def steps(d):
    yield 2
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), 256)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), 256)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    window = d.window()
    grid = [dock for dock in window.findChildren(QDockWidget) if dock.objectName() == 'GridDocker'][0]
    grid.show()
    yield 1
    d.dump(grid)
    d.shot('k07_probe_grid_docker', grid)
    d.action('view_grid')
    d.action('view_snap_to_grid')
    d.action('KisToolSelectRectangular')
    yield 1
    canvas = d.of_class(window, 'KisOpenGLCanvas2')
    left, top, right, bottom = image_rect(canvas)
    d.log('CANVAS widget {}x{} image at {},{} to {},{}'.format(canvas.width(), canvas.height(), left, top, right, bottom))
    scale = (right - left + 4) / 256.0
    start = QPoint(int(left + 2 * scale), int(top + 3 * scale))
    end = QPoint(int(left + 30 * scale), int(top + 29 * scale))
    d.drag(canvas, start, end)
    yield 1
    selection = d.Krita.instance().activeDocument().selection()
    d.log('SELECTION ' + ('none' if selection is None else '{},{} {}x{}'.format(selection.x(), selection.y(), selection.width(), selection.height())))
    d.shot('k07_probe_selected')
    canvas.update()
    yield 1
    d.shot('k07_probe_selected2')
