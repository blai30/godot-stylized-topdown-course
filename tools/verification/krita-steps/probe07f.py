# Probes color by HSV, the PrintWindow capture, and the native Export dialog through UI Automation.
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton, QTabWidget


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
    d.action('view_grid')
    d.action('select_all')
    yield 1
    yield from d.capture('k07_probe_printwindow')
    d.click(d.of_class(window, 'KoDualColorButton'), QPoint(8, 8))
    yield 2
    picker = d.top('Select a Color')
    d.tab(d.find(picker, QTabWidget, name='tabWidget'), 'HSV')
    yield 0.5
    spins = d.of_class(picker, 'KisSpinboxHSXSelector').findChildren(QAbstractSpinBox)
    for spin, value in zip(spins, (40, 19, 57)):
        d.set_number(spin, value)
    yield 0.5
    d.shot('k07_probe_hsv_typed', picker)
    d.click(d.find(picker, QPushButton, text='&OK'))
    yield 0.5
    d.action('fill_selection_foreground_color')
    yield 1
    data = bytes(d.Krita.instance().activeDocument().activeNode().pixelData(40, 10, 1, 1))
    d.log('PIXEL BGRA {}'.format(list(data)))
    d.action('file_export_file')
    yield 3
    yield from d.capture('k07_probe_export_native', 'Exporting')
    target = d.os.path.join(d.OUT, 'probe_palette.png')
    d.file_dialog('Exporting', target)
    yield 3
    d.log('WINDOWS ' + str([w.windowTitle() for w in d.QApplication.topLevelWidgets() if w.isVisible()]))
    for widget in d.QApplication.topLevelWidgets():
        if widget.isVisible() and widget is not window and widget.windowTitle():
            d.shot('k07_probe_png_options', widget)
            d.dump(widget)
    yield 1
