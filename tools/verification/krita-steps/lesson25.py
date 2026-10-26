# Lesson 25: paints the oak's leaf atlas, the reader's way. One leaf from three strokes becomes a stamp brush that
# turns to follow the stroke and varies in size; four sprays of leaves are stamped into the cells of a 1024 pixel
# image, each leaf in one of a few warm or cool grays. Saves leaf_atlas.kra and leaf_atlas.png into the workbench.
import math
import os
import random
import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QAbstractSpinBox, QCheckBox, QComboBox, QLineEdit, QPushButton, QSpinBox, QTabWidget, QWidget

sys.path.insert(0, os.path.dirname(__file__))
import ground_painting
from ground_painting import (WORKBENCH, Painter, close_editor, editor_page, enable_option, layer_eye, save_preset,
                             set_sensors)

ATLAS = 1024
CELL = 512
MARGIN = 16
# The leaf stamp is about 290 px tall, and used at this size, so a leaf is about 135 px long in the atlas.
LEAF_SIZE = 215
FADE = 22
# Warm and cool grays as hue, saturation, value: each leaf takes one, so a spray is a mix of both.
COLORS = [(215, 14, 56), (210, 18, 48), (222, 10, 64), (38, 22, 52), (34, 18, 62), (30, 14, 46)]


def new_atlas(d):
    # File > New at 1024 by 1024 with one layer, then everything on it cleared to transparent.
    d.action('file_new')
    yield 2
    dialog = d.top('Create new document')
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleWidth'), ATLAS)
    d.set_number(d.find(dialog, QAbstractSpinBox, name='doubleHeight'), ATLAS)
    yield 0.5
    yield from d.capture('k25_new_dimensions', widget=dialog)
    d.tab(d.find(dialog, QTabWidget, name='tabWidget'), 'Content')
    yield 0.5
    d.set_number(d.find(dialog, QAbstractSpinBox, name='intNumLayers'), 1)
    field = d.find(dialog, QLineEdit, name='txtName')
    field.setFocus()
    field.selectAll()
    d.type_text(field, 'leaf_atlas')
    yield 0.5
    yield from d.capture('k25_new_content', widget=dialog)
    d.click(d.find(dialog, QPushButton, text='&Create'))
    yield 3
    document = d.Krita.instance().activeDocument()
    d.log('DOCUMENT {} {}x{} layers {}'.format(document.name(), document.width(), document.height(), [n.name() for n in document.topLevelNodes()]))
    d.action('select_all')
    yield 0.5
    d.action('clear')
    yield 0.5
    d.action('deselect')
    yield 0.5
    document.refreshProjection()
    d.log('CLEARED alpha {}'.format(bytes(document.activeNode().pixelData(5, 5, 1, 1))[3]))
    d.action('zoom_to_fit')
    yield 1
    return document, Painter(d, ATLAS)


def show_grid(d):
    # Settings > Dockers > Grid and Guides: a 512 px grid, shown, so the four cells are visible.
    from PyQt5.QtWidgets import QDockWidget
    opened = d.menu('Settings')
    item = d.menu_item(opened, 'Dockers')
    sub = item.menu()
    entry = d.menu_item(sub, 'Grid and Guides')
    d.QApplication.activePopupWidget() and d.QApplication.activePopupWidget().close()
    entry.trigger()
    yield 1
    grid = [dock for dock in d.window().findChildren(QDockWidget) if dock.objectName() == 'GridDocker'][0]
    d.set_number(d.find(grid, QAbstractSpinBox, name='intHSpacing'), CELL)
    d.set_number(d.find(grid, QAbstractSpinBox, name='intSubdivision'), 1)
    d.click(d.find(grid, QWidget, name='chkShowGrid'))
    yield 1
    d.log('GRID {} / {} show {}'.format(d.find(grid, QAbstractSpinBox, name='intHSpacing').text(), d.find(grid, QAbstractSpinBox, name='intVSpacing').text(), d.find(grid, QWidget, name='chkShowGrid').isChecked()))
    yield from d.capture('k25_grid')


def leaf_stamp(d, document, painter):
    # A leaf on its own layer from three strokes: a light outline, the body, a midrib. Then the Leaf brush from it.
    d.action('add_new_paint_layer')
    yield 1
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    # The Twig brush tapers over 45 dabs, too long for a leaf: a copy that tapers over 26 makes a plump point.
    yield from d.preset('Twig')
    editor = yield from editor_page(d, 'Size')
    sensors, rows = set_sensors(d, editor, on=['Fade'], off=[])
    rect = sensors.visualRect(rows['Fade'])
    d.click(sensors.viewport(), QPoint(rect.left() + 40, rect.center().y()))
    yield 0.8
    yield from d.slider([w for w in editor.findChildren(QWidget) if w.objectName() == 'spinBoxLength' and w.isVisible()][0], FADE)
    yield from d.capture('k25_leaf_shape', widget=editor)
    yield from save_preset(d, editor, 'Leaf Shape')
    yield from close_editor(d)
    # A leaf is two tapered strokes from its widest point, one up to the tip and one down to the stalk. Alpha lock
    # then keeps the next paint inside the leaf: a gentle gradient, then the veins.
    yield from d.foreground((0, 0, 50))
    yield from d.slider(d.toolbar_slider('Size'), 130)
    yield from painter.stroke([(256, 320), (256, 245), (256, 170)])
    yield from painter.stroke([(256, 320), (256, 365), (256, 410)])
    d.action('toggle_layer_alpha_lock')
    yield 0.5
    yield from d.foreground((0, 0, 60))
    d.action('toggle_fg_bg')
    yield 0.5
    yield from d.foreground((0, 0, 44))
    d.action('KritaFill/KisToolGradient')
    yield 0.5
    yield from d.drag(painter.canvas, painter.at(225, 390), painter.at(290, 200), steps=12)
    yield 1
    yield from d.capture('k25_leaf_body')
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 4)
    yield from d.slider(d.toolbar_slider('Opacity'), 100)
    yield from d.foreground((0, 0, 58))
    yield from painter.stroke([(256, 400), (256, 320), (256, 210)])
    for y in (355, 315, 275, 240):
        yield from painter.stroke([(256, y + 8), (256 - 36, y - 24)])
        yield from painter.stroke([(256, y + 8), (256 + 36, y - 24)])
    yield from d.capture('k25_leaf')
    # Select the leaf and make the stamp, as in lesson 14.
    for name in ('Background',):
        yield from layer_eye(d, name)
    d.action('KisToolSelectRectangular')
    yield 0.5
    yield from d.drag(painter.canvas, painter.at(170, 120), painter.at(342, 450))
    yield 1
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-2 Opacity')
    editor = yield from editor_page(d, 'Brush Tip')
    d.click(d.find(editor, QPushButton.__mro__[1], text='&Predefined'))
    yield 1
    d.click_later(d.find(editor, QPushButton, name='stampButton'))
    yield 2
    stamp = d.top('Stamp')
    field = d.find(stamp, QLineEdit, name='nameLineEdit')
    field.setFocus()
    d.type_text(field, 'Leaf')
    mask = d.find(stamp, QCheckBox, name='colorAsMask')
    if mask.isChecked():
        d.click(mask)
    yield 0.5
    yield from d.capture('k25_stamp', widget=stamp)
    d.click(d.find(stamp, QPushButton, text='&Save'))
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    mode = d.find(editor, QComboBox, name='cmbBrushMode')
    mode.setCurrentIndex(mode.findText('Lightness map'))
    yield 0.5
    for box in editor.findChildren(QCheckBox):
        if box.isVisible() and 'Auto' in box.text():
            d.log('AUTO box {} {} checked {}'.format(box.objectName(), box.text(), box.isChecked()))
    yield from d.capture('k25_leaf_tip', widget=editor)
    # The leaf turns to follow the stroke, and each one is a little smaller or larger.
    editor = yield from editor_page(d, 'Rotation')
    enable_option(d, editor, 'Rotation')
    yield 0.5
    set_sensors(d, editor, on=['Drawing angle'], off=['Pressure'])
    yield 0.5
    yield from d.capture('k25_leaf_rotation', widget=editor)
    editor = yield from editor_page(d, 'Size')
    enable_option(d, editor, 'Size')
    yield 0.5
    set_sensors(d, editor, on=['Fuzzy Dab'], off=['Pressure'])
    yield 0.5
    low = [w for w in d.find(editor, QWidget, name='intOutPlaceholder').findChildren(QSpinBox) if w.isVisible()]
    d.set_number(low[0], 55)
    yield 0.5
    yield from d.capture('k25_leaf_size', widget=editor)
    yield from save_preset(d, editor, 'Leaf')
    yield from close_editor(d)
    d.action('deselect')
    yield 0.5
    # Back to the atlas: delete the leaf's layer and show the background again.
    d.action('remove_layer')
    yield 1
    yield from layer_eye(d, 'Background')
    d.log('LAYERS {}'.format([n.name() for n in document.topLevelNodes()]))


def spray(rng, cell):
    # The leaves of one spray: a dome above the stem, each leaf leaning away from the stem's foot, not too close to
    # another. Sorted from the top down, so lower leaves are painted over the higher ones, like scales.
    x0, y0 = (cell % 2) * CELL, (cell // 2) * CELL
    foot = (x0 + CELL / 2, y0 + 470)
    leaves = []
    for _ in range(800):
        if len(leaves) == 20:
            break
        x = x0 + CELL / 2 + rng.uniform(-165, 165)
        y = y0 + rng.uniform(170, 380)
        if ((x - foot[0]) / 190) ** 2 + ((y - y0 - 300) / 130) ** 2 > 1 or any(math.hypot(x - other[0], y - other[1]) < 46 for other in leaves):
            continue
        leaves.append((x, y, math.atan2(x - foot[0], foot[1] - y) * 1.15 + rng.uniform(-0.4, 0.4)))
    return sorted(leaves, key=lambda leaf: leaf[1])


def save_and_export(d, document, name):
    # File > Save As into art_source/nature/tree_oak, then File > Export into art/nature/tree_oak.
    for folder in ('art_source/nature/tree_oak', 'art/nature/tree_oak'):
        os.makedirs(os.path.join(WORKBENCH, folder), exist_ok=True)
    d.action('file_save_as')
    yield 3
    yield from d.file_dialog('Saving As', os.path.join(WORKBENCH, 'art_source', 'nature', 'tree_oak', name + '.kra'))
    yield 4
    d.log('SAVED ' + str(document.fileName()))
    d.action('file_export_file')
    yield 3
    yield from d.file_dialog('Exporting', os.path.join(WORKBENCH, 'art', 'nature', 'tree_oak', name + '.png'))
    yield 3
    options = d.top('PNG image')
    yield from d.capture('k25_png_options', widget=options)
    d.click(d.find(options, QPushButton, text='&OK'))
    yield 3
    path = os.path.join(WORKBENCH, 'art', 'nature', 'tree_oak', name + '.png')
    d.log('EXPORTED {} {}'.format(path, os.path.getsize(path)))


def steps(d):
    yield 2
    random.seed(25)
    rng = random.Random(25)
    document, painter = yield from new_atlas(d)
    yield from show_grid(d)
    yield from leaf_stamp(d, document, painter)
    # The Leaf brush: pick a gray, then drag a short stroke where each leaf goes, in the direction it points.
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Leaf')
    yield from d.slider(d.toolbar_slider('Size'), LEAF_SIZE)
    yield from d.slider(d.toolbar_slider('Opacity'), 100)
    # A stem in each cell first, a thin dark stroke from the foot of the spray up through its middle.
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 8)
    yield from d.foreground((215, 10, 30))
    for cell in range(4):
        x0, y0 = (cell % 2) * CELL, (cell // 2) * CELL
        yield from painter.stroke([(x0 + 256, y0 + 480), (x0 + 256, y0 + 380), (x0 + 258, y0 + 270)])
    yield from d.preset('Leaf')
    yield from d.slider(d.toolbar_slider('Size'), LEAF_SIZE)
    yield from d.slider(d.toolbar_slider('Opacity'), 100)
    leaves = []
    for cell in range(4):
        leaves.append(spray(rng, cell))
    current = None
    # Each cell is painted from its top leaves down; a leaf's gray is picked when it changes.
    for row in range(max(len(spray_leaves) for spray_leaves in leaves)):
        for cell_leaves in leaves:
            if row >= len(cell_leaves):
                continue
            x, y, angle = cell_leaves[row]
            color = rng.randrange(len(COLORS))
            if color != current:
                yield from d.foreground(COLORS[color])
                current = color
            # The stamp is turned by the stroke's direction, so a stroke along (cos, sin) points the tip at `angle`.
            dx, dy = math.cos(angle), math.sin(angle)
            yield from painter.stroke([(x - dx * 3, y - dy * 3), (x + dx * 3, y + dy * 3)])
    yield 1
    yield from d.capture('k25_atlas')
    yield from save_and_export(d, document, 'leaf_atlas')
    d.log('DONE')
