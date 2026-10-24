# Probes one swatch end to end: 32 px grid, snapped selection, color by HSV and hex, fill, and the export dialogs.
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton, QDockWidget, QApplication, QLineEdit, QTabWidget


def image_rect(canvas):
    image = canvas.grab().toImage()
    xs, ys = [], []
    for y in range(0, image.height(), 2):
        for x in range(0, image.width(), 2):
            if QColor(image.pixel(x, y)).lightness() > 250:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs) + 2, max(ys) + 2


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
    canvas = d.of_class(window, 'KisOpenGLCanvas2')
    left, top, right, bottom = image_rect(canvas)
    scale = (right - left) / 256.0
    d.log('IMAGE {},{} {},{} scale {:.3f}'.format(left, top, right, bottom, scale))
    grid = [dock for dock in window.findChildren(QDockWidget) if dock.objectName() == 'GridDocker'][0]
    grid.show()
    yield 1
    d.set_number(d.find(grid, QAbstractSpinBox, name='intHSpacing'), 32)
    yield 0.5
    d.log('SPACING H {} V {}'.format(d.find(grid, QAbstractSpinBox, name='intHSpacing').text(), d.find(grid, QAbstractSpinBox, name='intVSpacing').text()))
    d.click(d.find(grid, d.QWidget, name='chkShowGrid'))
    d.click(d.find(grid, d.QWidget, name='chkSnapToGrid'))
    yield 1
    d.action('KisToolSelectRectangular')
    yield 1
    def at(x, y):
        return QPoint(int(left + x * scale), int(top + y * scale))
    yield from d.drag(canvas, at(33, 1), at(63, 31))
    yield 1
    selection = d.Krita.instance().activeDocument().selection()
    d.log('SELECTION ' + ('none' if selection is None else '{},{} {}x{}'.format(selection.x(), selection.y(), selection.width(), selection.height())))
    d.shot('k07_probe_grid_selection')
    d.click(d.of_class(window, 'KoDualColorButton'), QPoint(8, 8))
    yield 2
    picker = d.top('Select a Color')
    d.tab(d.find(picker, QTabWidget, name='tabWidget'), 'HSV')
    yield 0.5
    d.dump(d.find(picker, QTabWidget, name='tabWidget'))
    d.shot('k07_probe_color_hsv', picker)
    hex_field = [edit for edit in d.of_class(picker, 'KisHexColorInput').findChildren(QLineEdit)][0]
    hex_field.setFocus()
    hex_field.selectAll()
    d.type_text(hex_field, '928976')
    d.key(hex_field, Qt.Key_Return)
    yield 0.5
    d.log('PICKER VISIBLE AFTER ENTER {}'.format(picker.isVisible()))
    if picker.isVisible():
        d.click(d.find(picker, QPushButton, text='&OK'))
    yield 0.5
    d.action('fill_selection_foreground_color')
    yield 1
    document = d.Krita.instance().activeDocument()
    data = bytes(document.activeNode().pixelData(40, 10, 1, 1))
    d.log('PIXEL BGRA {}'.format(list(data)))
    d.action('deselect')
    yield 1
    d.shot('k07_probe_filled')
    d.action('file_export_file')
    yield 3
    exporter = d.top('Exporting')
    d.shot('k07_probe_export', exporter)
    d.dump(exporter)
    exporter.reject()
    yield 1
