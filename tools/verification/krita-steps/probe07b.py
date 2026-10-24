# Creates the palette document through File > New, then reads the workspace: dockers, tools, grid, color dialog.
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAbstractSpinBox, QDockWidget, QToolButton, QPushButton

exec(open(__file__.replace('probe07b', 'probe07'), encoding='utf-8').read().split('def steps')[0])


def set_number(d, spin, value):
    edit = spin.lineEdit()
    edit.setFocus()
    edit.selectAll()
    d.type_text(edit, str(value))
    d.key(edit, Qt.Key_Tab)


def steps(d):
    yield 2
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    set_number(d, d.find(dialog, QAbstractSpinBox, name='doubleWidth'), 256)
    set_number(d, d.find(dialog, QAbstractSpinBox, name='doubleHeight'), 256)
    yield 0.5
    d.shot('k07_probe_new_256', dialog)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    d.shot('k07_probe_canvas')
    window = d.window()
    for dock in window.findChildren(QDockWidget):
        d.log('DOCK {} #{} visible={}'.format(dock.windowTitle(), dock.objectName(), dock.isVisible()))
    for button in window.findChildren(QToolButton):
        if button.isVisible() and button.objectName():
            d.log('TOOL #{} tip={!r}'.format(button.objectName(), button.toolTip()))
    opened = d.menu('View')
    yield 0.5
    snap = d.menu_item(opened, 'Snap To').menu()
    d.log('SNAP: ' + ' | '.join(d.labels(snap)))
    opened.hide()
    yield 0.3
    for name in ('view_grid', 'view_snap_to_grid', 'fill_selection_foreground_color', 'KisToolSelectRectangular', 'file_export_file', 'edit_fill_selection_foreground', 'fill_selection_foreground'):
        found = d.Krita.instance().action(name) if hasattr(d, 'Krita') else None
        d.log('ACTION {} -> {}'.format(name, None if found is None else (found.text(), found.shortcut().toString())))
