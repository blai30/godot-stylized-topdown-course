# Probes lesson 13: brush presets, the wrap-around action, and whether a driven stroke paints, also across an edge.
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractSpinBox, QDockWidget, QPushButton


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
    window = d.window()
    presets = sorted(krita.resources('preset').keys())
    d.log('PRESETS {} {}'.format(len(presets), presets))
    for name in ('wrap_all_layers', 'KritaShape/KisToolBrush', 'zoom_to_fit', 'view_zoom_out', 'increase_brush_size', 'decrease_brush_size', 'fill_selection_foreground_color', 'edit_fill_foreground', 'reset_fg_bg'):
        found = krita.action(name)
        d.log('ACTION {} {}'.format(name, None if found is None else (found.text(), found.shortcut().toString(), found.isCheckable())))
    view_menu = d.menu('View')
    d.log('VIEW MENU ' + str([item.text() for item in view_menu.actions()]))
    view_menu.close()
    docks = [dock.objectName() + ':' + dock.windowTitle() + ':' + str(dock.isVisible()) for dock in window.findChildren(QDockWidget)]
    d.log('DOCKS ' + str(docks))
    preset_dock = [dock for dock in window.findChildren(QDockWidget) if 'Preset' in dock.objectName()]
    for dock in preset_dock:
        d.dump(dock)
    d.action('KritaShape/KisToolBrush')
    yield 1
    view = krita.activeWindow().activeView()
    d.log('CURRENT PRESET ' + view.currentBrushPreset().name() + ' size ' + str(view.brushSize()))
    canvas = d.of_class(window, 'KisOpenGLCanvas2')
    d.log('CANVAS {}'.format(canvas.size()))
    image = canvas.grab().toImage()
    xs = [x for x in range(0, image.width(), 2) if QColor(image.pixel(x, image.height() // 2)).lightness() > 250]
    ys = [y for y in range(0, image.height(), 2) if QColor(image.pixel(image.width() // 2, y)).lightness() > 250]
    left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
    d.log('IMAGE ON CANVAS {} {} {} {}'.format(left, top, right, bottom))
    yield from d.drag(canvas, QPoint(left + 40, top + 40), QPoint(right - 40, bottom - 40), steps=30)
    yield 1
    document = krita.activeDocument()
    document.refreshProjection()
    node = document.activeNode()
    d.log('NODE ' + node.name())
    middle = bytes(node.pixelData(256, 256, 1, 1))
    d.log('PIXEL CENTER after stroke {}'.format(list(middle)))
    yield from d.capture('k13_probe_stroke')
    d.action('wrap_all_layers')
    yield 1
    d.log('WRAP checked {}'.format(krita.action('wrap_all_layers').isChecked()))
    yield from d.capture('k13_probe_wrap')
    # A horizontal stroke across the right edge should reappear at the left.
    yield from d.drag(canvas, QPoint(right - 30, top + 100), QPoint(right + 30, top + 100), steps=20)
    yield 1
    width = right - left
    d.log('PIXEL right edge {} left edge {}'.format(list(bytes(node.pixelData(510, int(100 * 512 / width), 1, 1))), list(bytes(node.pixelData(2, int(100 * 512 / width), 1, 1)))))
    yield from d.capture('k13_probe_wrap_stroke')
