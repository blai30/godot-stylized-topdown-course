# Lesson 7: builds the palette in Krita the reader's way and saves palette.kra and palette.png into the workbench.
import os
import tempfile

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QAbstractSpinBox, QDockWidget, QLineEdit, QPushButton, QRadioButton, QTabWidget

WORKBENCH = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), 'sgt-phase1', 'workbench')
CELL = 32

# The reference palette: rows of two ramps, each four swatches from dark to light, as hue, saturation, value.
RAMPS = [
    [(28, 14, 40), (34, 18, 53), (40, 17, 66), (46, 12, 79)],
    [(225, 12, 38), (218, 16, 51), (211, 15, 64), (204, 10, 77)],
    [(104, 52, 38), (96, 56, 51), (89, 56, 64), (82, 50, 77)],
    [(125, 46, 30), (118, 50, 43), (111, 48, 56), (104, 42, 69)],
    [(20, 44, 40), (26, 46, 53), (32, 44, 66), (38, 38, 79)],
    [(30, 38, 52), (36, 40, 65), (42, 36, 78), (48, 28, 90)],
]


def image_rect(canvas):
    # The white image on the canvas's gray surround maps image pixels to widget pixels.
    image = canvas.grab().toImage()
    xs, ys = [], []
    for y in range(0, image.height(), 2):
        for x in range(0, image.width(), 2):
            if QColor(image.pixel(x, y)).lightness() > 250:
                xs.append(x)
                ys.append(y)
    # A high-density screen grabs more pixels than the widget has; the rectangle is in the widget's own units.
    ratio = image.devicePixelRatio()
    return min(xs) / ratio, min(ys) / ratio, (max(xs) + 2) / ratio, (max(ys) + 2) / ratio


def menu_path(d, *labels):
    # Opens a main menu and walks its submenus, returning the last item.
    opened = d.menu(labels[0])
    item = None
    for label in labels[1:]:
        item = d.menu_item(opened, label)
        if item.menu() is not None:
            opened = item.menu()
    return item


def steps(d):
    yield 2
    yield from d.capture('k07_welcome')
    window = d.window()

    # File > New: a 256 by 256 image named palette.
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), 256)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), 256)
    yield 0.5
    d.shot('k07_new_dimensions', dialog)
    d.tab(d.find(dialog, QTabWidget, name='tabWidget'), 'Content')
    yield 0.5
    name = d.find(dialog, QLineEdit, name='txtName')
    name.setFocus()
    name.selectAll()
    d.type_text(name, 'palette')
    yield 0.5
    d.shot('k07_new_content', dialog)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    d.log('DOCUMENT {} {}x{}'.format(d.Krita.instance().activeDocument().name(), d.Krita.instance().activeDocument().width(), d.Krita.instance().activeDocument().height()))

    # Settings > Dockers > Grid and Guides, a 32 px grid, shown and snapping.
    item = menu_path(d, 'Settings', 'Dockers', 'Grid and Guides')
    d.QApplication.activePopupWidget() and d.QApplication.activePopupWidget().close()
    item.trigger()
    yield 1
    grid = [dock for dock in window.findChildren(QDockWidget) if dock.objectName() == 'GridDocker'][0]
    d.log('GRID DOCK visible {}'.format(grid.isVisible()))
    d.set_number(d.find(grid, QAbstractSpinBox, name='intHSpacing'), CELL)
    d.set_number(d.find(grid, QAbstractSpinBox, name='intSubdivision'), 1)
    d.click(d.find(grid, d.QWidget, name='chkShowGrid'))
    d.click(d.find(grid, d.QWidget, name='chkSnapToGrid'))
    yield 1
    d.log('GRID {} / {} subdivision {} show {} snap {}'.format(d.find(grid, QAbstractSpinBox, name='intHSpacing').text(), d.find(grid, QAbstractSpinBox, name='intVSpacing').text(), d.find(grid, QAbstractSpinBox, name='intSubdivision').text(),
                                              d.find(grid, d.QWidget, name='chkShowGrid').isChecked(), d.find(grid, d.QWidget, name='chkSnapToGrid').isChecked()))
    yield from d.capture('k07_grid')

    d.action('KisToolSelectRectangular')
    yield 1
    canvas = d.of_class(window, 'KisOpenGLCanvas2')
    left, top, right, bottom = image_rect(canvas)
    scale = (right - left) / 256.0

    def at(x, y):
        return QPoint(int(left + x * scale), int(top + y * scale))

    document = d.Krita.instance().activeDocument()
    for row, pair in enumerate(zip(RAMPS[0::2], RAMPS[1::2])):
        for column, color in enumerate(pair[0] + pair[1]):
            x, y = column * CELL, row * CELL
            # Start and end a little inside the cell's corners; snapping pulls the selection onto the grid. Krita reads
            # the real keyboard's modifiers during a drag, so a key held on this computer can spoil one; retry it.
            bounds = None
            for attempt in range(3):
                yield from d.drag(canvas, at(x + 1, y + 1), at(x + CELL - 1, y + CELL - 1))
                # Krita applies a selection asynchronously.
                for _ in range(20):
                    yield 0.1
                    selection = document.selection()
                    if selection is not None:
                        bounds = (selection.x(), selection.y(), selection.width(), selection.height())
                        break
                if bounds == (x, y, CELL, CELL):
                    break
                d.log('RETRY cell {},{} got {}'.format(x, y, bounds))
                d.action('deselect')
                while document.selection() is not None:
                    yield 0.1
                yield 0.5
            if bounds != (x, y, CELL, CELL):
                raise RuntimeError('selection {} is not cell {},{}'.format(bounds, x, y))
            if row == 0 and column == 0:
                yield from d.capture('k07_first_selection')
            d.click(d.of_class(window, 'KoDualColorButton'), QPoint(8, 8))
            yield 1
            picker = d.top('Select a Color')
            d.tab(d.find(picker, QTabWidget, name='tabWidget'), 'HSV')
            yield 0.3
            spins = d.of_class(picker, 'KisSpinboxHSXSelector').findChildren(QAbstractSpinBox)
            for spin, value in zip(spins, color):
                d.set_number(spin, value)
            yield 0.3
            if row == 0 and column == 0:
                d.shot('k07_color_hsv', picker)
            d.click(d.find(picker, QPushButton, text='&OK'))
            yield 0.3
            d.action('fill_selection_foreground_color')
            yield 0.5
            if row == 0 and column == 0:
                yield from d.capture('k07_first_swatch')
                found = d.Krita.instance().action('deselect')
                d.log('DESELECT {} {}'.format(found.text(), found.shortcut().toString()))
            # A drag that starts on the old selection's outline moves it, so deselect first.
            d.action('deselect')
            # Deselect is asynchronous too; a drag that starts before it lands moves the old selection.
            while document.selection() is not None:
                yield 0.1
            yield 0.3
    d.action('deselect')
    yield 1
    yield from d.capture('k07_ramps')

    # Value check: a Desaturate filter layer over the swatches.
    d.action('add_new_adjustment_layer')
    yield 2
    filters = d.top('New Filter Layer')
    tree = d.of_class(filters, 'KisFilterTree')
    model = tree.model()
    found = model.match(model.index(0, 0), Qt.DisplayRole, 'Desaturate', 1, Qt.MatchExactly | Qt.MatchRecursive)
    rect = tree.visualRect(found[0])
    d.click(tree.viewport(), rect.center())
    yield 1
    d.dump(d.find(filters, d.QWidget, name='scrollAreaWidgetContents'))
    d.log('LAYER NAME ' + d.find(filters, QLineEdit, name='layerName').text())
    d.log('DESATURATE CHECKED ' + str([radio.text() for radio in filters.findChildren(QRadioButton) if radio.isChecked()]))
    d.find(filters, QRadioButton, name='radioLuminosityBT709').click()
    yield 0.5
    d.log('DESATURATE NOW ' + str([radio.text() for radio in filters.findChildren(QRadioButton) if radio.isChecked()]))
    d.shot('k07_filter_desaturate', filters)
    d.click(d.find(filters, QPushButton, text='&OK'))
    yield 2
    yield from d.capture('k07_value_check')

    # Hide the filter layer with its eye icon before exporting.
    layer_dock = [dock for dock in window.findChildren(QDockWidget) if dock.objectName() == 'KisLayerBox'][0]
    view = [child for child in layer_dock.findChildren(QAbstractItemView) if child.isVisible()][0]
    d.log('LAYER VIEW ' + view.metaObject().className())
    index = view.model().index(0, 0)
    row = view.visualRect(index)
    d.log('LAYER ROW {} {}'.format(view.model().data(index), row))
    # The eye sits at the row's left edge, before the first column's rectangle.
    d.click(view.viewport(), QPoint(12, row.center().y()))
    yield 1
    filter_layer = [node for node in document.topLevelNodes() if node.name().startswith('Filter Layer')][0]
    d.log('FILTER LAYER {} visible {}'.format(filter_layer.name(), filter_layer.visible()))
    if filter_layer.visible():
        raise RuntimeError('the eye click did not hide the filter layer')
    yield from d.capture('k07_layers_hidden')

    # File > Save As into art_source/palette, then File > Export into art/palette.
    for folder in ('art_source/palette', 'art/palette'):
        os.makedirs(os.path.join(WORKBENCH, folder), exist_ok=True)
    d.action('file_save_as')
    yield 3
    d.log('SAVE WINDOWS ' + str([w.windowTitle() for w in d.QApplication.topLevelWidgets() if w.isVisible()]))
    yield from d.file_dialog('Saving As', os.path.join(WORKBENCH, 'art_source', 'palette', 'palette.kra'))
    yield 4
    d.log('SAVED ' + str(document.fileName()))
    d.action('file_export_file')
    yield 3
    yield from d.capture('k07_export_dialog', 'Exporting')
    yield from d.file_dialog('Exporting', os.path.join(WORKBENCH, 'art', 'palette', 'palette.png'))
    yield 3
    options = d.top('PNG image')
    d.shot('k07_png_options', options)
    d.click(d.find(options, QPushButton, text='&OK'))
    yield 3
    path = os.path.join(WORKBENCH, 'art', 'palette', 'palette.png')
    d.log('EXPORTED {} {}'.format(path, os.path.getsize(path)))
