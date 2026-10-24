# Probes lesson 13: how the toolbar's Size slider enters typing mode.
from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton


def steps(d):
    yield 2
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    window = d.window()
    d.action('KritaShape/KisToolBrush')
    yield 1
    spins = [spin for spin in window.findChildren(QAbstractSpinBox) if spin.isVisible() and spin.parent().objectName() != 'WdgLayerBox']
    size = [spin for spin in spins if 'Size' in spin.prefix()][0]
    edit = size.lineEdit()
    point = QPoint(size.width() // 2, size.height() // 2)

    def state(label):
        d.log('{}: focus {} readOnly {} text {!r} edit focus {} focused widget {}'.format(label, size.hasFocus(), edit.isReadOnly(), edit.text(), edit.hasFocus(),
                                                                                          d.QApplication.focusWidget().metaObject().className() if d.QApplication.focusWidget() else None))

    state('before')
    d.enter(size, point)
    yield 0.3
    for kind, buttons in ((QEvent.MouseButtonPress, Qt.RightButton), (QEvent.MouseButtonRelease, Qt.NoButton)):
        event = QMouseEvent(kind, QPointF(point), QPointF(point), QPointF(size.mapToGlobal(point)), Qt.RightButton, buttons, Qt.NoModifier)
        d.QApplication.instance().notify(size, d.spontaneous(event))
        yield 0.15
    yield 0.5
    state('right click')
    for code, text in ((Qt.Key_1, '1'), (Qt.Key_6, '6'), (Qt.Key_0, '0')):
        d.key(size, code, Qt.NoModifier, text)
        yield 0.2
    state('typed 160')
    d.key(size, Qt.Key_Return)
    yield 0.5
    state('after Return')
