# Probes lesson 13: the brush editor, its Size option's sensors (Fade), and saving a new preset.
from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton, QWidget


def steps(d):
    yield 2
    krita = d.Krita.instance()
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-5 Size')
    for name in ('show_brush_editor', 'show_brush_presets'):
        found = krita.action(name)
        d.log('ACTION {} {}'.format(name, None if found is None else (found.text(), found.shortcut().toString())))
    d.action('show_brush_editor')
    yield 2
    popups = [w for w in d.QApplication.topLevelWidgets() if w.isVisible()]
    d.log('TOP ' + str([(w.metaObject().className(), w.objectName(), w.windowTitle()) for w in popups]))
    for widget in popups:
        if widget.metaObject().className() not in ('KisMainWindow',):
            d.dump(widget, limit=9)
            d.shot('k13_probe_editor', widget)
    yield from d.capture('k13_probe_editor_full')
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    categories = d.of_class(editor, 'KisCategorizedListView')
    model = categories.model()

    def open_option(label):
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            if model.data(index) == label:
                d.click(categories.viewport(), categories.visualRect(index).center())
                return
        raise RuntimeError('no option ' + label)

    d.log('OPTIONS ' + str([model.data(model.index(row, 0)) for row in range(model.rowCount())]))
    for label in ('Size', 'Rotation'):
        open_option(label)
        yield 1
        stack = [w for w in editor.findChildren(QWidget) if w.metaObject().className() == 'QStackedWidget' and w.isVisible()]
        d.log('--- ' + label)
        d.dump(stack[0].currentWidget(), limit=8)
        d.shot('k13_probe_option_' + label.lower(), editor)
    open_option('Brush Tip')
    yield 1
    d.click(d.find(editor, QPushButton.__mro__[1], text='&Predefined'))
    yield 1
    stack = [w for w in editor.findChildren(QWidget) if w.metaObject().className() == 'QStackedWidget' and w.isVisible()]
    d.log('--- Predefined')
    d.dump(stack[0].currentWidget(), limit=9)
    d.shot('k13_probe_predefined', editor)
