# Lesson 14: paints tileable dirt and sand textures to match the grass, the reader's way. A pebble painted in grays
# (a contact shadow, a chipped stone shape from a polygon selection, a lit rim clipped to the selection) becomes a
# stamp brush; dirt gets blotches, pebbles, and twigs, sand gets damp patches, ripples, pebbles, and shell bits.
# Saves dirt_albedo and sand_albedo as .kra and .png into the workbench.
import math
import os
import random
import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit, QPushButton, QWidget

sys.path.insert(0, os.path.dirname(__file__))
from ground_painting import (close_editor, editor_page, enable_option, layer_eye, layer_select, new_texture,
                             save_and_export, save_preset, set_sensors)

# The reference palette's dirt and sand ramps, from lesson 7: shadow, dark, light, highlight.
DIRT = [(20, 44, 40), (26, 46, 53), (32, 44, 66), (38, 38, 79)]
SAND = [(30, 38, 52), (36, 40, 65), (42, 36, 78), (48, 28, 90)]
SHADOW_GRAY, BODY_GRAY, RIM_GRAY, SHINE_GRAY = (0, 0, 30), (0, 0, 55), (0, 0, 75), (0, 0, 90)


def far(d, name):
    d.action('zoom_to_fit')
    yield 0.5
    for _ in range(2):
        d.action('view_zoom_out')
        yield 0.5
    yield 1
    yield from d.capture(name)
    d.action('zoom_to_fit')
    yield 0.5
    d.action('view_zoom_out')
    yield 1


def click_at(d, painter, point):
    d.enter(painter.canvas, painter.at(*point))
    yield 0.05
    d.mouse(painter.canvas, QEvent.MouseButtonPress, painter.at(*point), Qt.LeftButton)
    yield 0.05
    d.mouse(painter.canvas, QEvent.MouseButtonRelease, painter.at(*point))
    yield 0.15


def pebble_brush(d, document, painter):
    # A pebble in grays on its own layer: shadow, stone, rim, shine. Then the Pebble stamp brush from it.
    d.action('add_new_paint_layer')
    yield 1
    center = (256, 256)
    # The contact shadow: a flat ellipse under the stone's lower half, peeking out below it.
    for tool in ('KisToolSelectElliptical', 'KisToolSelectPolygonal'):
        found = d.Krita.instance().action(tool)
        d.log('TOOL {} {!r} {!r}'.format(tool, found.text(), found.shortcut().toString()))
    d.action('KisToolSelectElliptical')
    yield 0.5
    yield from d.drag(painter.canvas, painter.at(214, 262), painter.at(300, 298))
    yield 0.8
    yield from d.foreground(SHADOW_GRAY)
    d.action('fill_selection_foreground_color')
    yield 0.8
    d.action('deselect')
    yield 0.5
    # The stone: a polygon of seven corners, clicked one by one and closed with Enter, then filled.
    d.action('KisToolSelectPolygonal')
    yield 0.5
    random.seed(4)
    corners = []
    for k in range(7):
        angle = 2 * math.pi * k / 7 + random.uniform(-0.2, 0.2)
        corners.append((center[0] + math.cos(angle) * 44 * random.uniform(0.85, 1.05), center[1] - 6 + math.sin(angle) * 32 * random.uniform(0.85, 1.05)))
    for corner in corners:
        yield from click_at(d, painter, corner)
    d.key(painter.canvas, Qt.Key_Return)
    yield 1
    d.log('PEBBLE SELECTION {}'.format(document.selection() is not None))
    yield from d.foreground(BODY_GRAY)
    d.action('fill_selection_foreground_color')
    yield 0.8
    yield from d.capture('k14_pebble_body')
    # The rim: with the stone still selected, a brush along its upper edge paints only inside the stone.
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 16)
    yield from d.foreground(RIM_GRAY)
    top_edge = [c for c in corners if c[1] < center[1] - 6]
    top_edge.sort(key=lambda c: c[0])
    yield from painter.stroke([(x, y + 3) for x, y in top_edge])
    yield from d.slider(d.toolbar_slider('Size'), 8)
    yield from d.foreground(SHINE_GRAY)
    yield from painter.stroke([(center[0] - 18, center[1] - 26), (center[0] - 4, center[1] - 30)])
    d.action('deselect')
    yield 1
    yield from d.capture('k14_pebble')

    # Hide the layers below, select the pebble with its shadow, and make the stamp, as in lesson 13.
    for name in ('Paint Layer 1', 'Background'):
        yield from layer_eye(d, name)
    d.action('KisToolSelectRectangular')
    yield 0.5
    yield from d.drag(painter.canvas, painter.at(198, 212), painter.at(318, 304))
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
    d.type_text(field, 'Pebble')
    mask = d.find(stamp, QCheckBox, name='colorAsMask')
    if mask.isChecked():
        d.click(mask)
    yield 0.5
    d.click(d.find(stamp, QPushButton, text='&Save'))
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    mode = d.find(editor, QComboBox, name='cmbBrushMode')
    mode.setCurrentIndex(mode.findText('Lightness map'))
    yield 0.5
    spacing = [w for w in d.find(editor, QWidget, name='brushSpacingSelectionWidget').findChildren(QWidget) if w.metaObject().className() == 'KisDoubleSliderSpinBox'][0]
    yield from d.slider(spacing, 5)
    yield from d.capture('k14_pebble_tip', widget=editor)
    # Pebbles lie any way round, at any size from a third to full.
    editor = yield from editor_page(d, 'Rotation')
    enable_option(d, editor, 'Rotation')
    yield 0.5
    set_sensors(d, editor, on=['Fuzzy Dab'], off=['Pressure'])
    yield 0.5
    editor = yield from editor_page(d, 'Size')
    enable_option(d, editor, 'Size')
    yield 0.5
    set_sensors(d, editor, on=['Fuzzy Dab'], off=['Pressure'])
    yield 0.5
    from PyQt5.QtWidgets import QSpinBox
    low = [w for w in d.find(editor, QWidget, name='intOutPlaceholder').findChildren(QSpinBox) if w.isVisible()]
    d.set_number(low[0], 33)
    yield 0.5
    yield from d.capture('k14_pebble_size', widget=editor)
    editor = yield from editor_page(d, 'Scatter')
    enable_option(d, editor, 'Scatter')
    yield 0.5
    yield from save_preset(d, editor, 'Pebble')
    yield from close_editor(d)
    d.action('deselect')
    yield 0.5
    for name in ('Paint Layer 1', 'Background', 'Paint Layer 2'):
        yield from layer_eye(d, name)
    yield from layer_select(d, 'Paint Layer 1')
    yield 1


def wander(painter, count, length, step=20, turn=0.5, start=None):
    for index in range(count):
        x, y = start() if start else (random.uniform(0, 512), random.uniform(0, 512))
        heading = random.uniform(0, 2 * math.pi)
        points = [(x, y)]
        for _ in range(int(length / step)):
            heading += random.uniform(-turn, turn)
            x, y = x + step * math.cos(heading), y + step * math.sin(heading)
            points.append((x, y))
        yield from painter.stroke(points)


def steps(d):
    yield 2
    random.seed(14)

    # Dirt: the dark swatch as the base.
    shadow, dark, light, highlight = DIRT
    document, painter = yield from new_texture(d, 'dirt_albedo', dark, 'k14_dirt')
    # Blotches: a hard round brush, see-through, so overlapping dabs build flat, painted shapes.
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 90)
    yield from d.slider(d.toolbar_slider('Opacity'), 25)
    for tone, count in ((shadow, 6), (light, 6)):
        yield from d.foreground(tone)
        yield from wander(painter, count, 120, step=15, turn=0.8)
    yield from d.capture('k14_dirt_blotches')
    yield from pebble_brush(d, document, painter)
    # Pebbles: the light swatch, scattered; a few in the highlight color.
    yield from d.slider(d.toolbar_slider('Size'), 60)
    yield from d.slider(d.toolbar_slider('Opacity'), 100)
    yield from d.foreground(light)
    yield from wander(painter, 5, 260, turn=0.9)
    yield from d.foreground(highlight)
    yield from wander(painter, 2, 160, turn=0.9)
    yield from d.capture('k14_dirt_pebbles')
    # Twigs and cracks: the Grass Blade brush from lesson 13, thin and dark.
    yield from d.preset('Grass Blade')
    yield from d.slider(d.toolbar_slider('Size'), 7)
    yield from d.foreground(shadow)
    for index in range(10):
        x, y = random.uniform(0, 512), random.uniform(0, 512)
        angle = random.uniform(0, 2 * math.pi)
        bend = random.uniform(-0.4, 0.4)
        points = [(x + math.cos(angle + bend * t / 6) * 9 * t, y + math.sin(angle + bend * t / 6) * 9 * t) for t in range(7)]
        yield from painter.stroke(points)
    yield 1
    yield from d.capture('k14_dirt_details')
    yield from far(d, 'k14_dirt_far')
    yield from save_and_export(d, document, 'dirt_albedo')
    # File > Close, so the next image is the only one open.
    found = d.Krita.instance().action('file_close')
    d.log('CLOSE {!r} {}'.format(found.text(), found.shortcut().toString()))
    d.action('file_close')
    yield 2
    d.log('OPEN DOCUMENTS ' + str([doc.name() for doc in d.Krita.instance().documents()]))

    # Sand: the light swatch as the base, damp patches, ripples, then a few pebbles and shell bits.
    shadow, dark, light, highlight = SAND
    document, painter = yield from new_texture(d, 'sand_albedo', light, 'k14_sand')
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 110)
    yield from d.slider(d.toolbar_slider('Opacity'), 20)
    yield from d.foreground(dark)
    yield from wander(painter, 5, 120, step=15, turn=0.8)
    yield from d.capture('k14_sand_damp')
    # A ripple is a long, gentle wave: a darker line, then a lighter one just above it.
    yield from d.slider(d.toolbar_slider('Size'), 5)
    yield from d.slider(d.toolbar_slider('Opacity'), 60)
    ripples = []
    for row in range(16):
        y0 = row * 32 + random.uniform(-6, 6)
        x0 = random.uniform(0, 512)
        length = random.uniform(240, 420)
        phase = random.uniform(0, 2 * math.pi)
        ripples.append([(x0 + length * i / 16, y0 + 6 * math.sin(phase + i * 0.6)) for i in range(17)])
    yield from d.foreground(dark)
    for ripple in ripples:
        yield from painter.stroke(ripple)
    yield from d.foreground(highlight)
    for ripple in ripples:
        yield from painter.stroke([(x, y - 4) for x, y in ripple])
    yield from d.capture('k14_sand_ripples')
    yield from d.preset('Pebble')
    yield from d.slider(d.toolbar_slider('Size'), 40)
    yield from d.slider(d.toolbar_slider('Opacity'), 100)
    yield from d.foreground(dark)
    yield from wander(painter, 4, 200, turn=0.9)
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 6)
    yield from d.foreground(highlight)
    for index in range(25):
        x, y = random.uniform(0, 512), random.uniform(0, 512)
        yield from painter.stroke([(x, y), (x + 2, y + 1)])
    yield 1
    yield from d.capture('k14_sand_details')
    yield from far(d, 'k14_sand_far')
    yield from save_and_export(d, document, 'sand_albedo')
