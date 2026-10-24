# Probes lesson 13: choosing a preset by the docker's search, typing size and opacity in the toolbar, and a full
# grass recipe with wrap-around on, exported for a tiled look check.
import math
import os
import random

from krita import InfoObject, ManagedColor
from PyQt5.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QAbstractSpinBox, QDockWidget, QLineEdit, QPushButton

OUT = os.path.join(os.environ['TEMP'], 'sgt-phase2', 'krita-probe')
SHADOW, DARK, LIGHT, HIGHLIGHT = (120, 44, 33), (112, 50, 46), (104, 48, 59), (96, 40, 72)


def steps(d):
    yield 2
    krita = d.Krita.instance()
    os.makedirs(OUT, exist_ok=True)
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), 512)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), 512)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    window = d.window()
    view = krita.activeWindow().activeView()
    document = krita.activeDocument()
    canvas = d.of_class(window, 'KisOpenGLCanvas2')

    def color(hsv):
        h, s, v = hsv
        view.setForeGroundColor(ManagedColor.fromQColor(QColor.fromHsv(h, int(s * 2.55), int(v * 2.55)), view.canvas()))

    color(DARK)
    d.action('select_all')
    yield 0.3
    d.action('fill_selection_foreground_color')
    yield 0.3
    d.action('deselect')
    yield 0.3

    # The preset docker's search box, then a click on the one item left.
    dock = [dock for dock in window.findChildren(QDockWidget) if dock.objectName() == 'PresetDocker'][0]
    edits = [edit for edit in dock.findChildren(QLineEdit) if edit.isVisible()]
    d.log('PRESET EDITS ' + str([(edit.objectName(), edit.placeholderText(), edit.parent().metaObject().className()) for edit in edits]))
    search = [edit for edit in edits if edit.parent().metaObject().className() != 'KisTagFilterWidget'] or edits

    def choose(name):
        box = search[-1]
        box.setFocus()
        box.selectAll()
        d.type_text(box, name)
        yield 1
        items = [view_ for view_ in dock.findChildren(QAbstractItemView) if view_.isVisible()][0]
        model = items.model()
        d.log('SEARCH {!r} rows {} first {}'.format(name, model.rowCount(), model.data(model.index(0, 0), Qt.DisplayRole) if model.rowCount() else None))
        d.click(items.viewport(), items.visualRect(model.index(0, 0)).center())
        yield 0.5
        d.log('PRESET NOW ' + view.currentBrushPreset().name())

    spins = [spin for spin in window.findChildren(QAbstractSpinBox) if spin.isVisible() and spin.parent().objectName() != 'WdgLayerBox']
    size = [spin for spin in spins if 'Size' in getattr(spin, 'prefix', lambda: '')()][0]
    opacity = [spin for spin in spins if 'Opacity' in getattr(spin, 'prefix', lambda: '')()][0]

    def set_slider(spin, value):
        # Right-click the field, type the number, and press Enter, as Krita's manual says.
        point = QPoint(spin.width() // 2, spin.height() // 2)
        d.enter(spin, point)
        yield 0.2
        for kind, buttons in ((QEvent.MouseButtonPress, Qt.RightButton), (QEvent.MouseButtonRelease, Qt.NoButton)):
            event = QMouseEvent(kind, QPointF(point), QPointF(point), QPointF(spin.mapToGlobal(point)), Qt.RightButton, buttons, Qt.NoModifier)
            d.QApplication.instance().notify(spin, d.spontaneous(event))
            yield 0.15
        for character in str(value):
            d.key(spin, Qt.Key_0 + int(character), Qt.NoModifier, character)
            yield 0.2
        d.key(spin, Qt.Key_Return)
        yield 0.3
        d.log('SLIDER {} now {}'.format(spin.prefix(), spin.text()))

    yield from choose('Airbrush Soft')
    yield from set_slider(size, 160)
    yield from set_slider(opacity, 40)
    d.log('BRUSH size {} opacity {}'.format(view.brushSize(), view.paintingOpacity()))

    view_menu = d.menu('View')
    d.menu_item(view_menu, 'Wrap Around Mode').trigger()
    view_menu.close()
    yield 1
    d.action('zoom_to_fit')
    yield 1
    image = canvas.grab().toImage()
    d.log('WRAP {}'.format(krita.action('wrap_around_mode').isChecked()))
    yield from d.capture('k13_probe_wrap_on')

    # Map image pixels to the canvas from the fit view: the image is centered and fills the shorter side.
    zoom = view.canvas().zoomLevel()
    d.log('ZOOM {}'.format(zoom))
    cx, cy = canvas.width() / 2.0, canvas.height() / 2.0
    scale = min(canvas.width(), canvas.height()) / 512.0
    d.log('SCALE guess {}'.format(scale))

    def at(x, y):
        return QPoint(int(cx + (x - 256) * scale), int(cy + (y - 256) * scale))

    random.seed(7)
    # Big soft clumps of shadow and light, some across the edges; remember which is which for the flicks.
    clumps = []
    yield from set_slider(size, 220)
    yield from set_slider(opacity, 35)
    for index in range(18):
        tone = SHADOW if index % 2 == 0 else LIGHT
        color(tone)
        x, y = random.uniform(0, 512), random.uniform(0, 512)
        clumps.append((x, y, tone))
        angle = random.uniform(0, math.pi)
        yield from d.drag(canvas, at(x, y), at(x + 50 * math.cos(angle), y + 30 * math.sin(angle)), steps=8)
    yield from d.capture('k13_probe_clumps')
    # Short upward flicks grouped on the clumps: lighter flicks on light clumps, darker ones in the shadows. Left half
    # with Basic-1, right half with Chalk Grainy, to compare.
    for half, (preset, brush_size, brush_opacity) in enumerate((('Basic-1', 4, 60), ('Chalk Grainy', 10, 45))):
        yield from choose(preset)
        yield from set_slider(size, brush_size)
        yield from set_slider(opacity, brush_opacity)
        for x0, y0, tone in clumps:
            if (x0 < 256) != (half == 0):
                continue
            for index in range(14):
                if tone == LIGHT:
                    color(random.choice([LIGHT, HIGHLIGHT, LIGHT]))
                else:
                    color(random.choice([SHADOW, SHADOW, DARK]))
                x, y = x0 + random.gauss(0, 45), y0 + random.gauss(0, 45)
                angle = -math.pi / 2 + random.uniform(-0.45, 0.45)
                length = random.uniform(14, 28)
                bend = random.uniform(-6, 6)
                middle = (x + length / 2 * math.cos(angle) + bend, y + length / 2 * math.sin(angle))
                end = (x + length * math.cos(angle) + bend * 1.6, y + length * math.sin(angle))
                d.enter(canvas, at(x, y))
                yield 0.05
                d.mouse(canvas, QEvent.MouseButtonPress, at(x, y), Qt.LeftButton)
                yield 0.05
                for px, py in (middle, end):
                    d.mouse(canvas, QEvent.MouseMove, at(px, py), Qt.LeftButton)
                    yield 0.04
                d.mouse(canvas, QEvent.MouseButtonRelease, at(*end))
                yield 0.05
    yield from d.capture('k13_probe_strokes')
    document.setBatchmode(True)
    document.exportImage(os.path.join(OUT, 'grass.png'), InfoObject())
    yield 2
    d.log('EXPORTED')
