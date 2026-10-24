# Proves the driver: captures the start screen, opens File > New, and dumps the dialog and the main menus.
from PyQt5.QtWidgets import QWidget, QAbstractButton, QLineEdit, QAbstractSpinBox, QComboBox, QLabel, QTabWidget, QListWidget


def dump(d, widget, depth=0, limit=14):
    if depth > limit or not widget.isVisible():
        return
    text = ''
    for getter in ('text', 'currentText', 'title'):
        if hasattr(widget, getter):
            try:
                text = getter + '=' + repr(getattr(widget, getter)())
                break
            except TypeError:
                pass
    value = ''
    if isinstance(widget, QAbstractSpinBox):
        value = ' value=' + widget.text()
    d.log('  ' * depth + type(widget).__name__ + ' #' + widget.objectName() + ' ' + text + value)
    for child in widget.children():
        if isinstance(child, QWidget):
            dump(d, child, depth + 1, limit)


def steps(d):
    yield 2
    d.shot('k07_probe_start')
    for title in ():
        opened = d.menu(title)
        yield 0.5
        d.log('MENU ' + title + ': ' + ' | '.join(d.labels(opened)))
        opened.hide()
        yield 0.3
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.shot('k07_probe_new', dialog)
    dump(d, dialog)
    content = d.find(dialog, QTabWidget, name='tabWidget')
    d.tab(content, 'Content')
    yield 0.5
    d.shot('k07_probe_new_content', dialog)
    dump(d, content.currentWidget())
    dialog.reject()
    yield 1
