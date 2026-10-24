# Probes lesson 13: a tuft painted in grays with the blade brush, then Brush Tip > Predefined > Stamp from it.
import math
import random

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QAbstractSpinBox, QListView, QPushButton, QWidget


def option(d, editor, label):
    categories = d.of_class(editor, 'KisCategorizedListView')
    model = categories.model()
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if model.data(index) == label:
            d.click(categories.viewport(), categories.visualRect(index).center())
            return
    raise RuntimeError('no option ' + label)


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
    document = krita.activeDocument()
    view = krita.activeWindow().activeView()
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-5 Size')
    d.action('show_brush_editor')
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    option(d, editor, 'Size')
    yield 1
    sensors = d.find(editor, QListView, name='sensorsList')
    smodel = sensors.model()

    def row_of(name):
        return [smodel.index(r, 0) for r in range(smodel.rowCount()) if smodel.data(smodel.index(r, 0)) == name][0]

    for name in ('Fade', 'Pressure'):
        rect = sensors.visualRect(row_of(name))
        d.click(sensors.viewport(), QPoint(rect.left() + 8, rect.center().y()))
        yield 0.5
    rect = sensors.visualRect(row_of('Fade'))
    d.click(sensors.viewport(), QPoint(rect.left() + 40, rect.center().y()))
    yield 1
    d.click(d.find(editor, QPushButton, name='revLinearButton'))
    yield 0.5
    yield from d.slider([w for w in editor.findChildren(QWidget) if w.objectName() == 'spinBoxLength' and w.isVisible()][0], 25)
    d.top('Brush Editor').close()
    yield 1

    canvas = d.of_class(d.window(), 'KisOpenGLCanvas2')
    scale = view.canvas().zoomLevel()
    cx, cy = canvas.width() / 2.0, canvas.height() / 2.0

    def at(x, y):
        return QPoint(int(cx + (x - 256) * scale), int(cy + (y - 256) * scale))

    def stroke(points):
        d.enter(canvas, at(*points[0]))
        yield 0.05
        d.mouse(canvas, QEvent.MouseButtonPress, at(*points[0]), Qt.LeftButton)
        yield 0.05
        for point in points[1:]:
            d.mouse(canvas, QEvent.MouseMove, at(*point), Qt.LeftButton)
            yield 0.02
        d.mouse(canvas, QEvent.MouseButtonRelease, at(*points[-1]))
        yield 0.2

    # A tuft in grays on a new layer: back blades darker, front blades mid gray, tips lighter.
    d.action('add_new_paint_layer')
    yield 1
    yield from d.slider(d.toolbar_slider('Size'), 8)
    random.seed(5)
    root = (256, 300)
    for gray, count in ((90, 3), (128, 3)):
        yield from d.foreground((0, 0, int(gray / 2.55)))
        for k in range(count):
            angle = -math.pi / 2 + (k - (count - 1) / 2) * 0.45 + random.uniform(-0.1, 0.1)
            bend = random.uniform(-0.3, 0.3)
            points = []
            for i in range(13):
                t = i / 12
                points.append((root[0] + math.cos(angle) * 60 * t + bend * 12 * t * t, root[1] + math.sin(angle) * 60 * t))
            yield from stroke(points)
    yield from d.capture('k13_probe_tuft')

    # Select around the tuft, then make a brush tip from it.
    d.action('KisToolSelectRectangular')
    yield 0.5
    yield from d.drag(canvas, at(200, 220), at(312, 312))
    yield 1
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    d.action('show_brush_editor')
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    option(d, editor, 'Brush Tip')
    yield 1
    d.click(d.find(editor, QPushButton.__mro__[1], text='&Predefined'))
    yield 1
    d.click_later(d.find(editor, QPushButton, name='stampButton'))
    yield 2
    tops = [w for w in d.QApplication.topLevelWidgets() if w.isVisible()]
    d.log('TOPS ' + str([(w.metaObject().className(), w.windowTitle()) for w in tops]))
    for widget in tops:
        if widget.metaObject().className() not in ('KisMainWindow', 'QFrame'):
            d.dump(widget, limit=8)
            d.shot('k13_probe_stamp_dialog', widget)
    stamp = d.top('Stamp')
    from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit
    name = d.find(stamp, QLineEdit, name='nameLineEdit')
    name.setFocus()
    d.type_text(name, 'Grass Tuft')
    mask = d.find(stamp, QCheckBox, name='colorAsMask')
    d.click(mask)
    alpha = d.find(stamp, QCheckBox, name='preserveAlpha')
    d.click(alpha)
    yield 0.5
    d.log('STAMP mask {} alpha {}'.format(mask.isChecked(), alpha.isChecked()))
    d.shot('k13_probe_stamp_set', stamp)
    d.click(d.find(stamp, QPushButton, text='&Save'))
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    d.log('TIP ' + d.find(editor, QWidget, name='brushTipNameLabel').text())
    mode = d.find(editor, QComboBox, name='cmbBrushMode')
    d.log('MODES enabled {} {}'.format(mode.isEnabled(), [mode.itemText(i) for i in range(mode.count())]))
    d.shot('k13_probe_tip', editor)
    d.dump(d.find(editor, QWidget, name='grpBrushMode'), limit=4)
    categories = d.of_class(editor, 'KisCategorizedListView')
    cmodel = categories.model()
    for row in range(cmodel.rowCount()):
        index = cmodel.index(row, 0)
        d.log('CAT {} {} check {} flags {}'.format(row, cmodel.data(index), cmodel.data(index, Qt.CheckStateRole), int(cmodel.flags(index))))
    mode.setFocus()
    mode.setCurrentIndex(mode.findText('Lightness map'))
    yield 0.5
    d.log('MODE ' + mode.currentText())

    def check_category(label, nth=0):
        seen = 0
        for row in range(cmodel.rowCount()):
            index = cmodel.index(row, 0)
            if cmodel.data(index) == label:
                if seen == nth:
                    rect = categories.visualRect(index)
                    d.click(categories.viewport(), QPoint(rect.left() + 8, rect.center().y()))
                    d.click(categories.viewport(), QPoint(rect.left() + 60, rect.center().y()))
                    return index
                seen += 1
        raise RuntimeError('no category ' + label)

    def sensor(name):
        sensors = [w for w in editor.findChildren(QListView) if w.objectName() == 'sensorsList' and w.isVisible()][0]
        smodel = sensors.model()
        index = [smodel.index(r, 0) for r in range(smodel.rowCount()) if smodel.data(smodel.index(r, 0)) == name][0]
        rect = sensors.visualRect(index)
        d.click(sensors.viewport(), QPoint(rect.left() + 8, rect.center().y()))
        return smodel, index

    index = check_category('Rotation')
    yield 1
    d.log('ROTATION check {}'.format(cmodel.data(index, Qt.CheckStateRole)))
    for name in ('Drawing angle', 'Fuzzy Dab', 'Pressure'):
        smodel, sindex = sensor(name)
        yield 0.4
        d.log('ROT SENSOR {} {}'.format(name, smodel.data(sindex, Qt.CheckStateRole)))
    d.shot('k13_probe_rotation', editor)
    index = check_category('Scatter')
    yield 1
    d.log('SCATTER check {}'.format(cmodel.data(index, Qt.CheckStateRole)))
    stack = [w for w in editor.findChildren(QWidget) if w.metaObject().className() == 'QStackedWidget' and w.isVisible()]
    d.dump(stack[0].currentWidget(), limit=6)
    d.shot('k13_probe_scatter', editor)
    d.top('Brush Editor').close()
    yield 1

    # Test: a green base under the tuft layer, then stamp strokes on the tuft layer in three greens.
    d.action('deselect')
    yield 0.5
    yield from d.slider(d.toolbar_slider('Size'), 60)
    for value, y in ((51, 150), (64, 250), (77, 350)):
        yield from d.foreground((96 if value != 77 else 82, 56, value))
        yield from stroke([(60 + i * 40, y + 15 * math.sin(i)) for i in range(11)])
    yield 1
    yield from d.capture('k13_probe_stamped')
