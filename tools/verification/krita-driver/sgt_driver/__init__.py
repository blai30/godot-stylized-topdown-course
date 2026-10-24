# Replays a lesson's steps inside Krita. The step script (KRITA_STEPS) defines steps(driver), a generator that
# yields the seconds to wait before its next step. Input is synthetic Qt events sent to Krita's own widgets, never
# to the system mouse or keyboard. Captures come from QWidget.grab(), so nothing outside Krita is recorded.
import os
import traceback

from krita import Krita
from PyQt5.QtCore import QEvent, QPointF, QTimer, Qt
from PyQt5.QtGui import QContextMenuEvent, QEnterEvent, QFocusEvent, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMenuBar, QWidget

OUT = os.environ.get('KRITA_OUT', '')
LOG = os.environ.get('KRITA_LOG', '')
STEPS = os.environ.get('KRITA_STEPS', '')
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(STEPS)), 'scripts')
WIDTH, HEIGHT = 1920, 1080


def log(message):
    with open(LOG, 'a', encoding='utf-8') as file:
        file.write(str(message) + '\n')


def window():
    return Krita.instance().activeWindow().qwindow()


def run_script(name, *arguments):
    # Runs a PowerShell helper from tools/verification/scripts without blocking Krita's event loop, as a generator
    # the step script yields from. Returns the helper's output.
    import subprocess
    script = os.path.join(SCRIPTS, name)
    # Output goes to a file: a pipe nobody reads until the end fills up and stalls a long listing.
    output_path = LOG + '.script'
    with open(output_path, 'wb') as output_file:
        process = subprocess.Popen(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script] + [str(item) for item in arguments],
                                   stdout=output_file, stderr=subprocess.STDOUT, creationflags=0x08000000)
        while process.poll() is None:
            yield 0.2
    with open(output_path, 'rb') as output_file:
        output = output_file.read().decode('utf-8', 'replace').strip()
    if process.returncode != 0:
        raise RuntimeError('{} failed: {}'.format(name, output))
    return output


def capture(name, title=None, widget=None):
    # Saves a top-level window as the desktop compositor shows it, overlays included (QWidget.grab() leaves out the
    # canvas's grid and selection outline, and grabbing a dialog leaves Krita's slider fields committing after one
    # key). Without a title or widget it captures the main window.
    path = os.path.join(OUT, name + '.png')
    if widget is not None:
        yield from run_script('capture-window.ps1', '-Handle', int(widget.window().winId()), '-Out', path)
    elif title is None:
        yield from run_script('capture-window.ps1', '-Handle', int(window().winId()), '-Out', path)
    else:
        yield from run_script('capture-window.ps1', '-ProcessId', os.getpid(), '-Title', title, '-Out', path)
    log('shot ' + name)


def automate(*arguments):
    # Drives a native dialog of Krita's (the Windows file dialogs) through UI Automation.
    output = yield from run_script('uia.ps1', '-ProcessId', os.getpid(), *arguments)
    return output


def file_dialog(title, path):
    # Fills a native Windows file dialog's File name box and presses its default button (Save or Open) with window
    # messages to the dialog itself. The box is the Edit (id 0x3E9) in the ComboBox below the dialog's view.
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    user32.FindWindowW.restype = wintypes.HWND
    user32.GetParent.restype = wintypes.HWND
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPCWSTR]
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    dialog = user32.FindWindowW('#32770', title)
    if not dialog:
        raise RuntimeError('no file dialog ' + title)

    def class_of(hwnd):
        name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, name, 256)
        return name.value

    found = []
    visitor = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd, _):
        parent = user32.GetParent(hwnd)
        if class_of(hwnd) == 'Edit' and user32.GetDlgCtrlID(hwnd) == 0x3E9 and class_of(parent) == 'ComboBox' \
                and class_of(user32.GetParent(parent)) == 'FloatNotifySink':
            found.append(hwnd)
        return True

    user32.EnumChildWindows(dialog, visitor(visit), 0)
    if not found:
        raise RuntimeError('no File name box in ' + title)
    # WM_SETTEXT, then WM_COMMAND IDOK, posted so the dialog closes after this step returns.
    user32.SendMessageW(found[0], 0x000C, 0, path)
    user32.PostMessageW(dialog, 0x0111, 1, 0)


def shot(name, widget=None):
    target = widget or window()
    path = os.path.join(OUT, name + '.png')
    if not target.grab().save(path):
        raise RuntimeError('could not save ' + path)
    log('shot ' + name)


def action(name):
    found = Krita.instance().action(name)
    if found is None:
        raise RuntimeError('no action ' + name)
    # Deferred, so a modal dialog the action opens runs its own loop while the steps keep ticking.
    QTimer.singleShot(0, found.trigger)


def top(title):
    for widget in QApplication.topLevelWidgets():
        if widget.isVisible() and title in widget.windowTitle():
            return widget
    shown = [widget.windowTitle() for widget in QApplication.topLevelWidgets() if widget.isVisible()]
    raise RuntimeError('no window titled {}; visible: {}'.format(title, shown))


def popup():
    widget = QApplication.activePopupWidget()
    if widget is None:
        raise RuntimeError('no open menu')
    return widget


def find(parent, kind, text=None, name=None):
    for child in parent.findChildren(kind):
        if not child.isVisible():
            continue
        if name is not None and child.objectName() != name:
            continue
        if text is not None and getattr(child, 'text', lambda: None)() != text:
            continue
        return child
    raise RuntimeError('no {} text={} name={} in {}'.format(kind.__name__, text, name, parent.objectName()))


def of_class(parent, class_name):
    # Krita's own widget classes are not wrapped in Python, so they are found by their C++ class name.
    for child in parent.findChildren(QWidget):
        if child.isVisible() and child.metaObject().className() == class_name:
            return child
    raise RuntimeError('no visible ' + class_name)


def spontaneous(event):
    # Marks an event as coming from the system. Krita's shape and selection tools cancel a shape whose release is not
    # spontaneous. Qt 5 keeps the flag in the bit field after QEvent's vtable, private pointer, and 16-bit type.
    import ctypes
    import sip
    address = sip.unwrapinstance(event) + 18
    flags = ctypes.c_ushort.from_address(address)
    flags.value |= 0x2
    assert event.spontaneous()
    return event


def mouse(widget, kind, point, buttons=Qt.NoButton):
    button = Qt.LeftButton if kind in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease) else Qt.NoButton
    event = QMouseEvent(kind, QPointF(point), QPointF(point), QPointF(widget.mapToGlobal(point)), button, buttons, Qt.NoModifier)
    # sendEvent() clears the spontaneous flag; notify() delivers through the same event filters and keeps it.
    QApplication.instance().notify(widget, spontaneous(event))


def enter(widget, point):
    # Krita's canvas ignores the mouse until it has focus and the pointer enters it. Focus is sent as an event, so
    # Krita need not be the active window on the desktop.
    QApplication.sendEvent(widget, QFocusEvent(QEvent.FocusIn, Qt.OtherFocusReason))
    QApplication.sendEvent(widget, QEnterEvent(QPointF(point), QPointF(point), QPointF(widget.mapToGlobal(point))))
    mouse(widget, QEvent.MouseMove, point)


def drag(widget, start, end, steps=8):
    # A left-button drag in widget coordinates, as a generator: the step script yields its delays, so the moves are
    # spread over time as a real drag's are.
    enter(widget, start)
    yield 0.1
    mouse(widget, QEvent.MouseButtonPress, start, Qt.LeftButton)
    yield 0.1
    for index in range(1, steps + 1):
        mouse(widget, QEvent.MouseMove, start + (end - start) * index / steps, Qt.LeftButton)
        yield 0.05
    mouse(widget, QEvent.MouseButtonRelease, end)
    yield 0.3


def click(widget, position=None, double=False):
    point = QPointF(position or widget.rect().center())
    kinds = [QEvent.MouseButtonPress, QEvent.MouseButtonRelease]
    if double:
        kinds += [QEvent.MouseButtonDblClick, QEvent.MouseButtonRelease]
    for kind in kinds:
        buttons = Qt.NoButton if kind == QEvent.MouseButtonRelease else Qt.LeftButton
        QApplication.sendEvent(widget, QMouseEvent(kind, point, Qt.LeftButton, buttons, Qt.NoModifier))


def click_later(widget, position=None):
    # A click on a button that opens a modal dialog: deferred, so the dialog runs its own loop while the steps keep
    # ticking, as action() does.
    QTimer.singleShot(0, lambda: click(widget, position))


def key(widget, code, modifiers=Qt.NoModifier, text=''):
    for kind in (QEvent.KeyPress, QEvent.KeyRelease):
        QApplication.sendEvent(widget, QKeyEvent(kind, code, modifiers, text))


def type_text(widget, text):
    for character in text:
        key(widget, 0, Qt.NoModifier, character)


def tab(widget, label):
    # Clicks a tab by its label, as a reader does.
    bar = widget.tabBar()
    for index in range(bar.count()):
        if bar.tabText(index).replace('&', '') == label:
            click(bar, bar.tabRect(index).center())
            return
    raise RuntimeError('no tab ' + label)


def set_number(spin, value):
    # Types a number into a spin box as a reader does: select its text, type, and Tab away.
    edit = spin.lineEdit()
    edit.setFocus()
    edit.selectAll()
    type_text(edit, str(value))
    key(edit, Qt.Key_Tab)


def slider(spin, value):
    # Types into one of Krita's slider fields (brush Size, Opacity) the way its manual says: right-click it, type
    # the number, and press Enter. A generator: the field drops keys sent while it switches into typing.
    point = spin.rect().center()
    # The field's text box covers it, so a real click lands on the text box, which the field watches. Without the
    # field typing yet, Krita takes a digit as a shortcut (1 resets the zoom, 4 to 6 turn the canvas), so check the
    # value and type again if it went wrong.
    target = spin.lineEdit()
    for attempt in range(2):
        enter(target, point)
        yield 0.2
        for kind, buttons in ((QEvent.MouseButtonPress, Qt.RightButton), (QEvent.MouseButtonRelease, Qt.NoButton)):
            event = QMouseEvent(kind, QPointF(point), QPointF(point), QPointF(target.mapToGlobal(point)), Qt.RightButton, buttons, Qt.NoModifier)
            QApplication.instance().notify(target, spontaneous(event))
            yield 0.15
        # The field selects its text a moment after it starts typing, and a key before that is overwritten: wait
        # until the text shows selected, as a reader sees it.
        for _ in range(30):
            yield 0.1
            if target.hasSelectedText():
                break
        yield 0.2
        log('SLIDER typing {} text {!r} selected {!r}'.format(not target.isReadOnly(), target.text(), target.selectedText()))
        # Krita need not be the active window on the desktop, so tell the field it has the keyboard; otherwise it
        # takes the first key as its last and commits.
        QApplication.sendEvent(target, QFocusEvent(QEvent.FocusIn, Qt.OtherFocusReason))
        yield 0.1
        for character in str(value):
            code = Qt.Key_Period if character == '.' else Qt.Key_0 + int(character)
            key(target, code, Qt.NoModifier, character)
            yield 0.2
            log('SLIDER key {!r} text {!r} selected {!r} readonly {}'.format(character, target.text(), target.selectedText(), target.isReadOnly()))
        key(target, Qt.Key_Return)
        yield 0.3
        log('SLIDER {}{}'.format(spin.prefix(), spin.text()))
        if abs(spin.value() - float(value)) < 0.01:
            return
    # The field commits after one key when Krita is not the active window on the desktop, which the driver must not
    # change. Typing is verified in the runs where Krita had focus; here the value is set directly, and logged.
    # The toolbar's Size and Opacity are set on the brush itself, since setting the field alone does not always
    # reach the brush.
    view = Krita.instance().activeWindow().activeView()
    if spin.prefix().startswith('Size'):
        view.setBrushSize(float(value))
    elif spin.prefix().startswith('Opacity'):
        view.setPaintingOpacity(float(value) / 100)
    else:
        spin.setValue(float(value))
    yield 0.3
    log('SLIDER SET DIRECTLY {}{} brush size {} opacity {}'.format(spin.prefix(), spin.text(), view.brushSize(), view.paintingOpacity()))
    if abs(spin.value() - float(value)) >= 0.01:
        raise RuntimeError('{} is {}, not {}'.format(spin.prefix(), spin.value(), value))


def toolbar_slider(label):
    # The toolbar's Size or Opacity field; the Layers docker has an Opacity field of its own.
    from PyQt5.QtWidgets import QAbstractSpinBox
    for spin in window().findChildren(QAbstractSpinBox):
        if spin.isVisible() and spin.parent().objectName() != 'WdgLayerBox' and getattr(spin, 'prefix', lambda: '')().startswith(label):
            return spin
    raise RuntimeError('no toolbar field ' + label)


def preset(name):
    # Types into the Brush Presets docker's search box and clicks the one preset left, as a reader does.
    from PyQt5.QtWidgets import QAbstractItemView, QDockWidget, QLineEdit
    dock = [dock for dock in window().findChildren(QDockWidget) if dock.objectName() == 'PresetDocker'][0]
    search = find(dock, QLineEdit)
    search.setFocus()
    search.selectAll()
    type_text(search, name)
    yield 1
    items = [view for view in dock.findChildren(QAbstractItemView) if view.isVisible()][0]
    model = items.model()
    # A name can be the start of another ("Basic-5 Size" and "Basic-5 Size Opacity"): click each match until the
    # chosen preset's name ends with the exact name, as a reader picks by its tooltip.
    chosen = ''
    for row in range(model.rowCount()):
        click(items.viewport(), items.visualRect(model.index(row, 0)).center())
        yield 0.5
        chosen = Krita.instance().activeWindow().activeView().currentBrushPreset().name()
        if chosen.endswith(') ' + name) or chosen == name:
            break
    log('PRESET ' + chosen)
    if not chosen.endswith(name):
        raise RuntimeError('preset is ' + chosen)


def foreground(hsv, shot_name=None):
    # Sets the foreground color by its HSV numbers in the Select a Color dialog, as lesson 7 teaches.
    from PyQt5.QtWidgets import QAbstractSpinBox, QPushButton, QTabWidget
    from PyQt5.QtCore import QPoint
    click(of_class(window(), 'KoDualColorButton'), QPoint(8, 8))
    yield 1
    picker = top('Select a Color')
    tab(find(picker, QTabWidget, name='tabWidget'), 'HSV')
    yield 0.3
    for spin, value in zip(of_class(picker, 'KisSpinboxHSXSelector').findChildren(QAbstractSpinBox), hsv):
        set_number(spin, value)
    yield 0.3
    if shot_name:
        yield from capture(shot_name, widget=picker)
    click(find(picker, QPushButton, text='&OK'))
    yield 0.3


def dump(widget, depth=0, limit=14):
    # Logs a widget tree with each widget's class, object name, and text, to find controls and read labels.
    if depth > limit or not widget.isVisible():
        return
    text = ''
    for getter in ('text', 'currentText', 'title', 'windowTitle'):
        if hasattr(widget, getter):
            try:
                value = getattr(widget, getter)()
            except TypeError:
                continue
            if value:
                text = getter + '=' + repr(value)
                break
    log('  ' * depth + widget.metaObject().className() + ' #' + widget.objectName() + ' ' + text)
    for child in widget.children():
        if isinstance(child, QWidget):
            dump(child, depth + 1, limit)


def menu(title):
    # Opens a main menu the way a click on the menu bar does, and returns the open menu.
    bar = window().findChild(QMenuBar)
    for item in bar.actions():
        if item.text().replace('&', '') == title:
            bar.setActiveAction(item)
            return item.menu()
    raise RuntimeError('no menu ' + title)


def menu_item(menu_widget, text):
    for item in menu_widget.actions():
        if item.text().replace('&', '') == text:
            return item
    raise RuntimeError('no menu item ' + text)


def labels(widget):
    return [item.text().replace('&', '') for item in widget.actions()]


class Runner:
    def __init__(self):
        self.queue = None

    def start(self):
        try:
            self.load()
        except Exception:
            log('FAILED\n' + traceback.format_exc())
            log('[krita] done')

    def load(self):
        qwindow = window()
        qwindow.showNormal()
        qwindow.move(0, 0)
        qwindow.resize(WIDTH, HEIGHT)
        namespace = {'__file__': STEPS}
        with open(STEPS, encoding='utf-8') as file:
            exec(compile(file.read(), STEPS, 'exec'), namespace)
        self.queue = namespace['steps'](__import__(__name__))
        QTimer.singleShot(2000, self.tick)

    def tick(self):
        try:
            delay = next(self.queue)
        except StopIteration:
            delay = None
        except Exception:
            log('FAILED\n' + traceback.format_exc())
            delay = None
        if delay is None:
            log('[krita] done')
            return
        QTimer.singleShot(int(delay * 1000), self.tick)


RUNNER = Runner()

if STEPS:
    log('[krita] driver loaded, Krita ' + Krita.instance().version())
    Krita.instance().notifier().windowCreated.connect(lambda: QTimer.singleShot(3000, RUNNER.start))
