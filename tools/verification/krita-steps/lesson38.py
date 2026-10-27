# Lesson 38: paints the character's texture, the reader's way. A 512 pixel image with the face patch above and eight flat
# color cells below, each cell and the face's features drawn with selections and filled. Saves character_texture.kra and
# character_texture.png.
import os
import sys

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QAbstractSpinBox, QLineEdit, QPushButton, QTabWidget

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'blender-steps'))
from ground_painting import WORKBENCH, Painter, pixel
from character_uv_data import SWATCHES, CELL, FACE_FEATURES, EYE, EYE_SHINE, BLUSH, MOUTH, EYE_COLOR, SHINE_COLOR, BLUSH_COLOR, MOUTH_COLOR

SIZE = 512
FOLDER = os.path.join(WORKBENCH, 'art_source', 'character')
EXPORT = os.path.join(WORKBENCH, 'art', 'character')


def new_texture(d):
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), SIZE)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), SIZE)
    yield 0.5
    yield from d.capture('k38_new_dimensions', widget=dialog)
    d.tab(d.find(dialog, QTabWidget, name='tabWidget'), 'Content')
    yield 0.5
    field = d.find(dialog, QLineEdit, name='txtName')
    field.setFocus()
    field.selectAll()
    d.type_text(field, 'character_texture')
    yield 0.5
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    document = d.Krita.instance().activeDocument()
    d.log('DOCUMENT {} {}x{}'.format(document.name(), document.width(), document.height()))
    d.action('zoom_to_fit')
    yield 1
    return document, Painter(d, SIZE)


def show_grid(d):
    from PyQt5.QtWidgets import QDockWidget, QWidget
    opened = d.menu('Settings')
    item = d.menu_item(opened, 'Dockers')
    entry = d.menu_item(item.menu(), 'Grid and Guides')
    d.QApplication.activePopupWidget() and d.QApplication.activePopupWidget().close()
    entry.trigger()
    yield 1
    grid = [dock for dock in d.window().findChildren(QDockWidget) if dock.objectName() == 'GridDocker'][0]
    d.set_number(d.find(grid, QAbstractSpinBox, name='intHSpacing'), 128)
    d.set_number(d.find(grid, QAbstractSpinBox, name='intSubdivision'), 1)
    d.click(d.find(grid, QWidget, name='chkShowGrid'))
    yield 1
    yield from d.capture('k38_grid')
    return grid


def fill(d, painter, tool, first, second, color):
    # Drag the selection, read where it really landed, and if the view has drifted, move the view's center by the
    # difference and drag again.
    document = d.Krita.instance().activeDocument()
    for attempt in range(4):
        d.action('deselect')
        yield 0.4
        d.action(tool)
        yield 0.4
        yield from d.drag(painter.canvas, painter.at(*first), painter.at(*second), steps=12)
        yield 0.6
        selection = document.selection()
        wanted = (min(first[0], second[0]), min(first[1], second[1]))
        error = (selection.x() - wanted[0], selection.y() - wanted[1])
        if abs(error[0]) <= 3 and abs(error[1]) <= 3:
            break
        d.log('DRIFT {} {} on {}'.format(error[0], error[1], color))
        painter.center = (painter.center[0] - error[0] * painter.scale, painter.center[1] - error[1] * painter.scale)
    else:
        raise RuntimeError('the selection would not land')
    yield from d.foreground(color)
    d.action('fill_selection_foreground_color')
    yield 0.5


def ellipse(d, painter, center, size, color):
    x, y = center
    width, height = size
    yield from fill(d, painter, 'KisToolSelectElliptical', (x - width / 2, y - height / 2), (x + width / 2, y + height / 2), color)


def steps(d):
    yield 2
    os.makedirs(FOLDER, exist_ok=True)
    os.makedirs(EXPORT, exist_ok=True)
    for folder in (FOLDER, EXPORT):
        for name in os.listdir(folder):
            if name.startswith('character_texture'):
                os.remove(os.path.join(folder, name))
    document, painter = yield from new_texture(d)
    grid = yield from show_grid(d)
    # The docker changed the canvas's size: fit the picture again and measure the view again.
    d.action('zoom_to_fit')
    yield 1
    painter = Painter(d, SIZE)
    # Measure where a selection really lands, and shift the view's center by the difference.
    d.action('KisToolSelectRectangular')
    yield 0.4
    yield from d.drag(painter.canvas, painter.at(100, 100), painter.at(200, 200))
    yield 0.6
    selection = document.selection()
    d.log('CALIBRATION selection at {} {} size {} {}'.format(selection.x(), selection.y(), selection.width(), selection.height()))
    painter.center = (painter.center[0] - (selection.x() - 100) * painter.scale, painter.center[1] - (selection.y() - 100) * painter.scale)
    d.action('deselect')
    yield 0.4
    # The cells: eight flat colors in the bottom half.
    for name, (column, row, color) in SWATCHES.items():
        x0, y0 = column * CELL * SIZE, (1 - (row + 1) * CELL) * SIZE
        yield from fill(d, painter, 'KisToolSelectRectangular', (x0, y0), (x0 + CELL * SIZE, y0 + CELL * SIZE), color)
    yield from d.capture('k38_cells')
    # The face patch: skin over the top half, then, with snapping off, eyes, their shine, blush, and a mouth.
    skin = SWATCHES['skin'][2]
    yield from fill(d, painter, 'KisToolSelectRectangular', (0, 0), (SIZE, SIZE / 2), skin)
    yield from d.capture('k38_patch')
    for name in ('eye_left', 'eye_right'):
        yield from ellipse(d, painter, FACE_FEATURES[name], EYE, EYE_COLOR)
    for name in ('blush_left', 'blush_right'):
        yield from ellipse(d, painter, FACE_FEATURES[name], BLUSH, BLUSH_COLOR)
    yield from ellipse(d, painter, FACE_FEATURES['mouth'], MOUTH, MOUTH_COLOR)
    yield from d.capture('k38_features')
    for name in ('eye_left', 'eye_right'):
        x, y = FACE_FEATURES[name]
        yield from ellipse(d, painter, (x - 6, y - 12), EYE_SHINE, SHINE_COLOR)
    d.action('deselect')
    yield 0.6
    document.refreshProjection()
    d.log('PIXELS skin {} eye {} shine {} tunic {}'.format(pixel(document, 100, 20), pixel(document, int(FACE_FEATURES['eye_left'][0]), int(FACE_FEATURES['eye_left'][1]) + 10), pixel(document, int(FACE_FEATURES['eye_left'][0]) - 6, int(FACE_FEATURES['eye_left'][1]) - 12), pixel(document, 300, 300)))
    yield from d.capture('k38_texture')
    d.action('file_save_as')
    yield 3
    yield from d.file_dialog('Saving As', os.path.join(FOLDER, 'character_texture.kra'))
    yield 4
    d.log('SAVED ' + str(document.fileName()))
    d.action('file_export_file')
    yield 3
    yield from d.file_dialog('Exporting', os.path.join(EXPORT, 'character_texture.png'))
    yield 3
    options = d.top('PNG image')
    yield from d.capture('k38_png_options', widget=options)
    d.click(d.find(options, QPushButton, text='&OK'))
    yield 3
    d.log('EXPORTED {}'.format(os.path.getsize(os.path.join(EXPORT, 'character_texture.png'))))
