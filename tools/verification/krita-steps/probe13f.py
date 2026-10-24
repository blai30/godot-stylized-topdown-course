# Probes lesson 13: a tapered blade brush from Basic-5 Size, with Fade driving the size, and how it paints.
import math

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QAbstractSpinBox, QListView, QPushButton, QWidget


def steps(d):
    yield 2
    krita = d.Krita.instance()
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), 512)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), 512)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-5 Size')
    d.action('show_brush_editor')
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    categories = d.of_class(editor, 'KisCategorizedListView')
    model = categories.model()
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if model.data(index) == 'Size':
            d.click(categories.viewport(), categories.visualRect(index).center())
            break
    yield 1
    sensors = d.find(editor, QListView, name='sensorsList')
    smodel = sensors.model()
    for row in range(smodel.rowCount()):
        index = smodel.index(row, 0)
        d.log('SENSOR {} {} checked {}'.format(row, smodel.data(index), smodel.data(index, Qt.CheckStateRole)))

    def sensor_row(name):
        for row in range(smodel.rowCount()):
            if smodel.data(smodel.index(row, 0)) == name:
                return smodel.index(row, 0)
        raise RuntimeError('no sensor ' + name)

    # A reader clicks the checkbox at the row's left edge.
    for name in ('Fade', 'Pressure'):
        rect = sensors.visualRect(sensor_row(name))
        d.click(sensors.viewport(), QPoint(rect.left() + 8, rect.center().y()))
        yield 0.5
        d.log('AFTER CLICK {} checked {}'.format(name, smodel.data(sensor_row(name), Qt.CheckStateRole)))
    # Selecting the Fade row's label shows its settings.
    rect = sensors.visualRect(sensor_row('Fade'))
    d.click(sensors.viewport(), QPoint(rect.left() + 40, rect.center().y()))
    yield 1
    d.click(d.find(editor, QPushButton, name='revLinearButton'))
    yield 1
    window = d.window()
    canvas = d.of_class(window, 'KisOpenGLCanvas2')
    view = krita.activeWindow().activeView()
    scale = view.canvas().zoomLevel()
    cx, cy = canvas.width() / 2.0, canvas.height() / 2.0

    def at(x, y):
        return QPoint(int(cx + (x - 256) * scale), int(cy + (y - 256) * scale))

    for band, fade_length in enumerate((40, 80, 150)):
        editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
        length_spin = [w for w in editor.findChildren(QWidget) if w.objectName() == 'spinBoxLength' and w.isVisible()][0]
        yield from d.slider(length_spin, fade_length)
        d.shot('k13_probe_fade_{}'.format(fade_length), editor)
        d.top('Brush Editor').close()
        yield 1
        yield from d.slider(d.toolbar_slider('Size'), 10)
        for index, length in enumerate((20, 35, 50, 70, 100)):
            x0, y0 = 50 + index * 95, 150 + band * 150
            points = [(x0 + 8 * math.sin(t / 10 * 1.2), y0 - length * t / 10) for t in range(11)]
            d.enter(canvas, at(*points[0]))
            yield 0.05
            d.mouse(canvas, QEvent.MouseButtonPress, at(*points[0]), Qt.LeftButton)
            yield 0.05
            for point in points[1:]:
                d.mouse(canvas, QEvent.MouseMove, at(*point), Qt.LeftButton)
                yield 0.03
            d.mouse(canvas, QEvent.MouseButtonRelease, at(*points[-1]))
            yield 0.3
        d.action('show_brush_editor')
        yield 1.5
    yield from d.capture('k13_probe_blades')
    d.action('show_brush_editor')
    yield 1
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    d.click(d.find(editor, QPushButton, name='saveNewBrushPresetButton'))
    yield 2
    tops = [w for w in d.QApplication.topLevelWidgets() if w.isVisible()]
    d.log('TOPS ' + str([(w.metaObject().className(), w.windowTitle()) for w in tops]))
    for widget in tops:
        if 'Save' in widget.windowTitle() or widget.metaObject().className().startswith('KisPresetSaveWidget'):
            d.dump(widget, limit=8)
            d.shot('k13_probe_save_preset', widget)
