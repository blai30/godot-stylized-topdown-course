# Probes lesson 13: the wrap-around action's name, the toolbar's size and opacity fields, and how candidate presets look.
import math
import os
import random

from krita import InfoObject, ManagedColor
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton, QToolBar

OUT = os.path.join(os.environ['TEMP'], 'sgt-phase2', 'krita-probe')


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
    view_menu = d.menu('View')
    for item in view_menu.actions():
        if 'Wrap' in item.text():
            d.log('WRAP ITEM {!r} object {!r} shortcut {} checkable {}'.format(item.text(), item.objectName(), item.shortcut().toString(), item.isCheckable()))
    view_menu.close()
    for bar in window.findChildren(QToolBar):
        if bar.isVisible():
            d.log('TOOLBAR {} {}'.format(bar.objectName(), [child.metaObject().className() + ':' + child.objectName() for child in bar.children() if hasattr(child, 'isVisible') and child.isVisible()][:40]))
    for spin in window.findChildren(QAbstractSpinBox):
        if spin.isVisible():
            d.log('SPIN {} {} {} prefix {!r} suffix {!r} value {}'.format(spin.metaObject().className(), spin.objectName(), spin.parent().objectName(), getattr(spin, 'prefix', lambda: '')(), getattr(spin, 'suffix', lambda: '')(), spin.text()))
    view = krita.activeWindow().activeView()
    document = krita.activeDocument()
    canvas = d.of_class(window, 'KisOpenGLCanvas2')
    image = canvas.grab().toImage()
    xs = [x for x in range(0, image.width(), 2) if QColor(image.pixel(x, image.height() // 2)).lightness() > 250]
    ys = [y for y in range(0, image.height(), 2) if QColor(image.pixel(image.width() // 2, y)).lightness() > 250]
    left, top, right, bottom = min(xs), min(ys), max(xs), max(ys)
    scale = (right - left) / 512.0

    def at(x, y):
        return QPoint(int(left + x * scale), int(top + y * scale))

    def color(h, s, v):
        managed = ManagedColor.fromQColor(QColor.fromHsv(h, int(s * 2.55), int(v * 2.55)), view.canvas())
        view.setForeGroundColor(managed)

    # Base: the grass ramp's dark swatch over the whole image.
    color(112, 50, 46)
    d.action('select_all')
    yield 0.5
    d.action('fill_selection_foreground_color')
    yield 0.5
    d.action('deselect')
    yield 0.5
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    presets = krita.resources('preset')
    random.seed(3)
    candidates = ['b) Airbrush Soft', 'f) Bristles-2 Flat Rough', 'h) Chalk Grainy', 'd) Ink-7 Brush Rough']
    for quadrant, name in enumerate(candidates):
        view.setCurrentBrushPreset(presets[name])
        yield 0.3
        x0, y0 = (quadrant % 2) * 256, (quadrant // 2) * 256
        view.setBrushSize(60 if quadrant == 0 else 24)
        for index in range(14):
            color(*random.choice([(120, 44, 33), (104, 48, 59), (96, 40, 72)]))
            x, y = x0 + random.randint(30, 226), y0 + random.randint(30, 226)
            angle = random.uniform(-0.6, 0.6) - math.pi / 2
            length = random.randint(20, 50)
            yield from d.drag(canvas, at(x, y), at(x + length * math.cos(angle), y + length * math.sin(angle)), steps=10)
        d.log('PAINTED ' + name)
    yield 1
    yield from d.capture('k13_probe_brushes')
    document.exportImage(os.path.join(OUT, 'brushes.png'), InfoObject())
    yield 2
    d.log('EXPORTED')
