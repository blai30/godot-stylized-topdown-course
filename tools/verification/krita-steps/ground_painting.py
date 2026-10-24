# Shared steps for the ground texture lessons (13 and 14): a new 512 px texture with its base color and wrap-around
# mode, strokes placed in image pixels, and Save As plus Export into the workbench.
import os

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QAbstractSpinBox, QLineEdit, QPushButton, QTabWidget

WORKBENCH = os.path.join(os.environ['TEMP'], 'sgt-phase1', 'workbench')
SIZE = 512


def pixel(document, x, y):
    document.refreshProjection()
    blue, green, red, _ = bytes(document.activeNode().pixelData(x, y, 1, 1))
    return red, green, blue


class Painter:
    # Maps image pixels to the canvas for the current view and paints strokes there, as mouse drags.
    def __init__(self, d):
        self.d = d
        view = d.Krita.instance().activeWindow().activeView()
        self.canvas = d.of_class(d.window(), 'KisOpenGLCanvas2')
        self.scale = view.canvas().zoomLevel()
        self.center = (self.canvas.width() / 2.0, self.canvas.height() / 2.0)

    def at(self, x, y):
        return QPoint(int(self.center[0] + (x - SIZE / 2) * self.scale), int(self.center[1] + (y - SIZE / 2) * self.scale))

    def stroke(self, points):
        # Fills in points between the given ones, as a real mouse sends many moves along a stroke.
        smooth = [points[0]]
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            smooth += [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * i / 4) for i in range(1, 5)]
        d, canvas = self.d, self.canvas
        d.enter(canvas, self.at(*smooth[0]))
        yield 0.05
        d.mouse(canvas, QEvent.MouseButtonPress, self.at(*smooth[0]), Qt.LeftButton)
        yield 0.05
        for point in smooth[1:]:
            d.mouse(canvas, QEvent.MouseMove, self.at(*point), Qt.LeftButton)
            yield 0.02
        d.mouse(canvas, QEvent.MouseButtonRelease, self.at(*smooth[-1]))
        yield 0.08


def new_texture(d, name, base, prefix):
    # File > New at 512 by 512 named <name>, the base color filled over the layer, wrap-around on, zoomed out a step.
    # Returns the document and a Painter for the view.
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), SIZE)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), SIZE)
    yield 0.5
    yield from d.capture(prefix + '_new_dimensions', widget=dialog)
    d.tab(d.find(dialog, QTabWidget, name='tabWidget'), 'Content')
    yield 0.5
    field = d.find(dialog, QLineEdit, name='txtName')
    field.setFocus()
    field.selectAll()
    d.type_text(field, name)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    krita = d.Krita.instance()
    document = krita.activeDocument()
    d.log('DOCUMENT {} {}x{}'.format(document.name(), document.width(), document.height()))
    yield from d.foreground(base, prefix + '_color_base')
    d.action('fill_selection_foreground_color')
    yield 1
    corners = [pixel(document, x, y) for x, y in ((0, 0), (SIZE - 1, SIZE - 1), (SIZE // 2, SIZE // 2))]
    d.log('BASE ' + str(corners))
    if len(set(corners)) != 1 or corners[0] == (255, 255, 255):
        raise RuntimeError('the fill did not cover the layer: {}'.format(corners))
    view_menu = d.menu('View')
    item = d.menu_item(view_menu, 'Wrap Around Mode')
    view_menu.close()
    if not item.isChecked():
        item.trigger()
    yield 1
    d.action('zoom_to_fit')
    yield 0.5
    d.action('view_zoom_out')
    yield 1
    d.log('WRAP {} zoom {}'.format(item.isChecked(), krita.activeWindow().activeView().canvas().zoomLevel()))
    return document, Painter(d)


def brush(d, preset, size, opacity):
    yield from d.preset(preset)
    yield from d.slider(d.toolbar_slider('Size'), size)
    yield from d.slider(d.toolbar_slider('Opacity'), opacity)


def save_and_export(d, document, name):
    # File > Save As into art_source/ground, then File > Export into art/ground, through Windows' dialogs.
    for folder in ('art_source/ground', 'art/ground'):
        os.makedirs(os.path.join(WORKBENCH, folder), exist_ok=True)
    d.action('file_save_as')
    yield 3
    d.file_dialog('Saving As', os.path.join(WORKBENCH, 'art_source', 'ground', name + '.kra'))
    yield 4
    d.log('SAVED ' + str(document.fileName()))
    d.action('file_export_file')
    yield 3
    d.file_dialog('Exporting', os.path.join(WORKBENCH, 'art', 'ground', name + '.png'))
    yield 3
    options = d.top('PNG image')
    yield from d.capture('k_' + name + '_png_options', widget=options)
    d.click(d.find(options, QPushButton, text='&OK'))
    yield 3
    path = os.path.join(WORKBENCH, 'art', 'ground', name + '.png')
    d.log('EXPORTED {} {}'.format(path, os.path.getsize(path)))


def editor_page(d, label, nth=0):
    # Opens the Brush Editor (F5) if needed and clicks an option's name in its list; returns the editor.
    from PyQt5.QtWidgets import QApplication
    if not [w for w in QApplication.topLevelWidgets() if w.isVisible() and w.windowTitle() == 'Brush Editor']:
        d.action('show_brush_editor')
        yield 1.5
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    categories = d.of_class(editor, 'KisCategorizedListView')
    model = categories.model()
    seen = 0
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if model.data(index) == label:
            if seen == nth:
                d.click(categories.viewport(), categories.visualRect(index).center())
                yield 0.8
                return editor
            seen += 1
    d.log('OPTIONS SHOWN ' + str([model.data(model.index(r, 0)) for r in range(model.rowCount())]) + ' visible ' + str(editor.isVisible()))
    raise RuntimeError('no brush option ' + label)


def enable_option(d, editor, label):
    # Ticks an option's checkbox at the left of its name in the Brush Editor's list.
    categories = d.of_class(editor, 'KisCategorizedListView')
    model = categories.model()
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if model.data(index) == label:
            if model.data(index, Qt.CheckStateRole) != Qt.Checked:
                rect = categories.visualRect(index)
                d.click(categories.viewport(), QPoint(rect.left() + 8, rect.center().y()))
            if model.data(index, Qt.CheckStateRole) != Qt.Checked:
                raise RuntimeError('could not enable ' + label)
            return
    raise RuntimeError('no brush option ' + label)


def set_sensors(d, editor, on, off):
    # Ticks the sensors in on and unticks those in off, in the shown option's sensor list.
    from PyQt5.QtWidgets import QListView
    sensors = [w for w in editor.findChildren(QListView) if w.objectName() == 'sensorsList' and w.isVisible()][0]
    model = sensors.model()
    rows = {model.data(model.index(r, 0)): model.index(r, 0) for r in range(model.rowCount())}
    # Ticking first, so the list never has no sensor ticked, which it refuses.
    for name, wanted in [(name, True) for name in on] + [(name, False) for name in off]:
        index = rows[name]
        if (model.data(index, Qt.CheckStateRole) == Qt.Checked) != wanted:
            rect = sensors.visualRect(index)
            d.click(sensors.viewport(), QPoint(rect.left() + 8, rect.center().y()))
        if (model.data(index, Qt.CheckStateRole) == Qt.Checked) != wanted:
            raise RuntimeError('sensor {} not {}'.format(name, wanted))
    return sensors, rows


def save_preset(d, editor, name, shot=None):
    # Save New Brush Preset: type the name and save.
    from PyQt5.QtWidgets import QLineEdit
    d.click_later(d.find(editor, QPushButton, name='saveNewBrushPresetButton'))
    yield 2
    dialog = d.top('Save New Brush Preset')
    field = [edit for edit in dialog.findChildren(QLineEdit) if edit.isVisible()][0]
    field.setFocus()
    field.selectAll()
    d.type_text(field, name)
    yield 0.5
    if shot:
        yield from d.capture(shot, widget=dialog)
    buttons = [button for button in dialog.findChildren(QPushButton) if button.isVisible() and button.text().replace('&', '') in ('Save', 'OK')]
    d.log('SAVE PRESET buttons ' + str([b.text() for b in dialog.findChildren(QPushButton) if b.isVisible()]))
    d.click(buttons[0])
    yield 2
    d.log('PRESET SAVED ' + d.Krita.instance().activeWindow().activeView().currentBrushPreset().name())


def layer_row(d, name):
    from PyQt5.QtWidgets import QAbstractItemView, QDockWidget
    dock = [dock for dock in d.window().findChildren(QDockWidget) if dock.objectName() == 'KisLayerBox'][0]
    view = [child for child in dock.findChildren(QAbstractItemView) if child.isVisible()][0]
    model = view.model()
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if model.data(index) == name:
            return view, view.visualRect(index)
    raise RuntimeError('no layer ' + name)


def layer_eye(d, name):
    # Clicks the eye at the left of a layer's row in the Layers docker, as in lesson 7.
    view, rect = layer_row(d, name)
    d.click(view.viewport(), QPoint(12, rect.center().y()))
    yield 0.5


def layer_select(d, name):
    view, rect = layer_row(d, name)
    d.click(view.viewport(), QPoint(rect.center().x(), rect.center().y()))
    yield 0.5


def close_editor(d):
    # F5 again closes the Brush Editor, as the lesson says.
    d.action('show_brush_editor')
    yield 1
    shown = [w for w in d.QApplication.topLevelWidgets() if w.isVisible() and w.windowTitle() == 'Brush Editor']
    if shown:
        raise RuntimeError('F5 did not close the Brush Editor')
