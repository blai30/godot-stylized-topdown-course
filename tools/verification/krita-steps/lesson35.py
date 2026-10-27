# Lesson 35: draws the character's reference sheet, the reader's way. A 2048 by 1024 canvas with a grid of one head unit,
# the front and side views built from rectangles, ellipses, and polygons filled with the design's colors, then each
# half copied into a new image and exported as the front and side images Blender uses in lesson 36.
import os
import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QAbstractSpinBox, QLineEdit, QPushButton, QTabWidget, QWidget

sys.path.insert(0, os.path.dirname(__file__))
from ground_painting import WORKBENCH
from lesson14 import click_at
from character_sheet_data import COLORS, FRONT, FRONT_X, GROUND, HEAD, SIDE, SIDE_X, pixel

WIDTH, HEIGHT = 2048, 1024
FOLDER = os.path.join(WORKBENCH, 'art_source', 'character')


class Sheet:
    # Maps sheet pixels to the canvas for the current view, like lesson 25's Painter for a canvas that is not square.
    def __init__(self, d):
        self.d = d
        view = d.Krita.instance().activeWindow().activeView()
        self.canvas = d.of_class(d.window(), 'KisOpenGLCanvas2')
        self.scale = view.canvas().zoomLevel() / self.canvas.devicePixelRatioF()
        self.center = (self.canvas.width() / 2.0, self.canvas.height() / 2.0)

    def at(self, x, y):
        return QPoint(int(self.center[0] + (x - WIDTH / 2) * self.scale), int(self.center[1] + (y - HEIGHT / 2) * self.scale))


def new_sheet(d):
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), WIDTH)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), HEIGHT)
    yield 0.5
    yield from d.capture('k35_new_dimensions', widget=dialog)
    d.tab(d.find(dialog, QTabWidget, name='tabWidget'), 'Content')
    yield 0.5
    field = d.find(dialog, QLineEdit, name='txtName')
    field.setFocus()
    field.selectAll()
    d.type_text(field, 'character_sheet')
    yield 0.5
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    document = d.Krita.instance().activeDocument()
    d.log('DOCUMENT {} {}x{}'.format(document.name(), document.width(), document.height()))
    # A light gray paper: the sheet is opaque, so each half exports at its full size.
    yield from d.foreground((0, 0, 94))
    d.action('select_all')
    yield 0.5
    d.action('fill_selection_foreground_color')
    yield 1
    d.action('deselect')
    yield 0.5
    d.action('zoom_to_fit')
    yield 1
    return document, Sheet(d)


def show_grid(d):
    # Settings > Dockers > Grid and Guides: one head unit, shown.
    from PyQt5.QtWidgets import QDockWidget
    opened = d.menu('Settings')
    item = d.menu_item(opened, 'Dockers')
    entry = d.menu_item(item.menu(), 'Grid and Guides')
    d.QApplication.activePopupWidget() and d.QApplication.activePopupWidget().close()
    entry.trigger()
    yield 1
    grid = [dock for dock in d.window().findChildren(QDockWidget) if dock.objectName() == 'GridDocker'][0]
    d.set_number(d.find(grid, QAbstractSpinBox, name='intHSpacing'), HEAD)
    d.set_number(d.find(grid, QAbstractSpinBox, name='intVSpacing'), HEAD)
    d.set_number(d.find(grid, QAbstractSpinBox, name='intSubdivision'), 1)
    d.click(d.find(grid, QWidget, name='chkShowGrid'))
    yield 1
    d.log('GRID {} / {} show {}'.format(d.find(grid, QAbstractSpinBox, name='intHSpacing').text(), d.find(grid, QAbstractSpinBox, name='intVSpacing').text(), d.find(grid, QWidget, name='chkShowGrid').isChecked()))
    yield from d.capture('k35_grid')


def draw(d, sheet, view_x, shapes):
    tools = {'rect': 'KisToolSelectRectangular', 'ellipse': 'KisToolSelectElliptical', 'poly': 'KisToolSelectPolygonal'}
    current = None
    for kind, color, points, mirror in shapes:
        for sign in ((1, -1) if mirror else (1,)):
            if tools[kind] != current:
                d.action(tools[kind])
                current = tools[kind]
                yield 0.5
            # A drag that starts at an old selection's edge would resize it, so each shape starts from none.
            d.action('deselect')
            yield 0.4
            mapped = [pixel(view_x, (sign * x, z)) for x, z in points]
            if kind == 'poly':
                for point in mapped:
                    yield from click_at(d, sheet, point)
                d.key(sheet.canvas, Qt.Key_Return)
                yield 0.8
            else:
                yield from d.drag(sheet.canvas, sheet.at(*mapped[0]), sheet.at(*mapped[1]))
                yield 0.8
            yield from d.foreground(COLORS[color])
            d.action('fill_selection_foreground_color')
            yield 0.6
    d.action('deselect')
    yield 0.5


def export_half(d, sheet, left, name):
    # Select one view's half of the sheet, copy it, paste it into a new image, and export that image as a PNG.
    from PyQt5.QtWidgets import QMessageBox
    d.action('KisToolSelectRectangular')
    yield 0.5
    x0 = 0 if left else WIDTH // 2
    yield from d.drag(sheet.canvas, sheet.at(x0, 0), sheet.at(x0 + WIDTH // 2, HEIGHT))
    yield 1
    d.action('edit_copy')
    yield 1
    d.action('paste_new')
    yield 3
    document = d.Krita.instance().activeDocument()
    d.log('HALF {} {}x{}'.format(name, document.width(), document.height()))
    d.action('file_export_file')
    yield 3
    yield from d.file_dialog('Exporting', os.path.join(FOLDER, name + '.png'))
    yield 3
    options = d.top('PNG image')
    d.click(d.find(options, QPushButton, text='&OK'))
    yield 3
    d.log('EXPORTED {} {}'.format(name, os.path.getsize(os.path.join(FOLDER, name + '.png'))))
    document.setModified(False)
    d.action('file_close')
    yield 2
    d.log('ACTIVE {}'.format(d.Krita.instance().activeDocument().name()))
    d.action('deselect')
    yield 0.5


def steps(d):
    yield 2
    os.makedirs(FOLDER, exist_ok=True)
    for name in os.listdir(FOLDER):
        os.remove(os.path.join(FOLDER, name))
    document, sheet = yield from new_sheet(d)
    yield from show_grid(d)
    # The ground line and the figure's top: nothing to draw, the grid is the guide. Front view, then side view.
    yield from draw(d, sheet, FRONT_X, FRONT)
    yield from d.capture('k35_front')
    yield from draw(d, sheet, SIDE_X, SIDE)
    yield from d.capture('k35_sheet')
    # The squint test: zoomed far out, the figure should still read as a person.
    for _ in range(3):
        d.action('view_zoom_out')
        yield 0.5
    yield 1
    yield from d.capture('k35_far')
    d.action('zoom_to_fit')
    yield 1
    d.action('file_save_as')
    yield 3
    yield from d.file_dialog('Saving As', os.path.join(FOLDER, 'character_sheet.kra'))
    yield 4
    d.log('SAVED ' + str(document.fileName()))
    sheet = Sheet(d)
    yield from export_half(d, sheet, True, 'character_front')
    sheet = Sheet(d)
    yield from export_half(d, sheet, False, 'character_side')
