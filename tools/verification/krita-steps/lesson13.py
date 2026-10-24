# Lesson 13: paints a tileable, hand-painted grass texture in Krita the reader's way. A blade brush that tapers
# without pen pressure, three tufts painted in grays, a stamp brush made from one of them, and stamp passes in the
# grass ramp with wrap-around mode on. Saves grass_albedo.kra and grass_albedo.png into the workbench.
import math
import os
import random
import sys

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit, QPushButton, QWidget

sys.path.insert(0, os.path.dirname(__file__))
from ground_painting import (close_editor, editor_page, enable_option, layer_eye, layer_select, new_texture, pixel,
                             save_and_export, save_preset, set_sensors)

# The reference palette's grass ramp, from lesson 7: shadow, dark, light, highlight as hue, saturation, value.
SHADOW, DARK, LIGHT, HIGHLIGHT = (104, 52, 38), (96, 56, 51), (89, 56, 64), (82, 50, 77)
# The tufts are painted in grays: the stamp brush keeps their light and dark and takes its hue from the color.
BACK_GRAY, FRONT_GRAY, TIP_GRAY = (0, 0, 35), (0, 0, 55), (0, 0, 72)


def blade(painter, root, angle, length, bend):
    # One blade, root to tip; the brush tapers it to a point.
    points = []
    for i in range(13):
        t = i / 12
        points.append((root[0] + math.cos(angle) * length * t + math.cos(angle + math.pi / 2) * bend * t * t,
                       root[1] + math.sin(angle) * length * t + math.sin(angle + math.pi / 2) * bend * t * t))
    return painter.stroke(points)


def steps(d):
    yield 2
    document, painter = yield from new_texture(d, 'grass_albedo', SHADOW, 'k13')
    yield from d.capture('k13_base')

    # The blade brush: Basic-5 Size, with Fade instead of Pressure driving the size, on a falling curve.
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-5 Size')
    editor = yield from editor_page(d, 'Size')
    # Krita keeps changes to a built-in brush for the session unless this is off; off, every brush you pick is as
    # it came, and your changes live only in the brushes you save.
    tweaks = d.find(editor, QCheckBox, name='dirtyPresetCheckBox')
    if tweaks.isChecked():
        d.click(tweaks)
    yield 0.3
    d.log('TEMPORARILY SAVE TWEAKS {}'.format(tweaks.isChecked()))
    if tweaks.isChecked():
        raise RuntimeError('could not uncheck Temporarily Save Tweaks To Presets')
    sensors, rows = set_sensors(d, editor, on=['Fade'], off=['Pressure'])
    rect = sensors.visualRect(rows['Fade'])
    d.click(sensors.viewport(), QPoint(rect.left() + 40, rect.center().y()))
    yield 0.8
    d.click(d.find(editor, QPushButton, name='revLinearButton'))
    yield 0.5
    yield from d.slider([w for w in editor.findChildren(QWidget) if w.objectName() == 'spinBoxLength' and w.isVisible()][0], 45)
    yield from d.capture('k13_blade_settings', widget=editor)
    yield from save_preset(d, editor, 'Grass Blade', 'k13_save_preset')
    yield from close_editor(d)
    yield 1

    # Three tufts in grays on a new layer, away from each other: back blades dark, front blades mid, tips light.
    found = d.Krita.instance().action('add_new_paint_layer')
    d.log('ADD PAINT LAYER {!r} {}'.format(found.text(), found.shortcut().toString()))
    layer_menu = d.menu('Layer')
    new_menu = d.menu_item(layer_menu, 'New').menu()
    d.log('LAYER NEW ' + str(d.labels(new_menu)))
    layer_menu.close()
    view_menu = d.menu('View')
    zoom_menu = d.menu_item(view_menu, 'Zoom, Rotate, and Mirror').menu()
    d.log('VIEW ZOOM ' + str(d.labels(zoom_menu)))
    view_menu.close()
    d.action('add_new_paint_layer')
    yield 1
    yield from d.slider(d.toolbar_slider('Size'), 15)
    random.seed(13)
    # Far enough apart that one tuft can be selected alone; blades fan up to about 60 degrees each side.
    roots = [(130, 230), (380, 230), (256, 470)]
    for gray, count, spread in ((BACK_GRAY, 3, 0.6), (FRONT_GRAY, 4, 0.5)):
        yield from d.foreground(gray)
        for root in roots:
            for k in range(count):
                angle = -math.pi / 2 + (k - (count - 1) / 2) * spread / max(count - 1, 1) * 2 + random.uniform(-0.1, 0.1)
                yield from blade(painter, (root[0] + random.uniform(-4, 4), root[1]), angle, 100 * random.uniform(0.85, 1.1), random.uniform(-18, 18))
    # Tips: a thin light stroke over the outer half of two front blades of each tuft.
    yield from d.slider(d.toolbar_slider('Size'), 9)
    yield from d.foreground(TIP_GRAY)
    for root in roots:
        for k in (1, 2):
            angle = -math.pi / 2 + (k - 1.5) * 0.5 / 1.5 * 2
            start_point = (root[0] + math.cos(angle) * 35, root[1] + math.sin(angle) * 35)
            yield from blade(painter, start_point, angle, 55, random.uniform(-8, 8))
    yield 1
    yield from d.capture('k13_tufts')

    # Stamp copies what the image shows, so hide the layers under the tufts: only the tufts on transparency remain.
    for name in ('Paint Layer 1', 'Background'):
        yield from layer_eye(d, name)
    yield 1
    d.log('HIDDEN ' + str([(node.name(), node.visible()) for node in document.topLevelNodes()]))
    yield from d.capture('k13_tufts_alone')

    # The stamp brush: select the middle tuft, start from Basic-2 Opacity, a plain Pixel Engine brush, and make a brush tip from the selection.
    d.action('KisToolSelectRectangular')
    yield 0.5
    yield from d.drag(painter.canvas, painter.at(166, 360), painter.at(346, 486))
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
    d.type_text(field, 'Grass Tuft')
    mask = d.find(stamp, QCheckBox, name='colorAsMask')
    if mask.isChecked():
        d.click(mask)
    yield 0.5
    yield from d.capture('k13_stamp', widget=stamp)
    d.click(d.find(stamp, QPushButton, text='&Save'))
    yield 2
    editor = d.of_class(d.top('Brush Editor'), 'KisPaintOpPresetsEditor')
    mode = d.find(editor, QComboBox, name='cmbBrushMode')
    mode.setCurrentIndex(mode.findText('Lightness map'))
    yield 0.5
    spacing = [w for w in d.find(editor, QWidget, name='brushSpacingSelectionWidget').findChildren(QWidget) if w.metaObject().className() == 'KisDoubleSliderSpinBox'][0]
    yield from d.slider(spacing, 0.6)
    d.log('TUFT TIP {} mode {}'.format(d.find(editor, QWidget, name='brushTipNameLabel').text(), mode.currentText()))
    yield from d.capture('k13_tuft_tip', widget=editor)
    editor = yield from editor_page(d, 'Rotation')
    enable_option(d, editor, 'Rotation')
    yield 0.5
    set_sensors(d, editor, on=['Drawing angle'], off=['Pressure'])
    yield 0.5
    yield from d.capture('k13_tuft_rotation', widget=editor)
    # Size: a random size for each tuft, from half to full, so they do not line up in rows.
    editor = yield from editor_page(d, 'Size')
    enable_option(d, editor, 'Size')
    yield 0.5
    set_sensors(d, editor, on=['Fuzzy Dab'], off=['Pressure'])
    yield 0.5
    from PyQt5.QtWidgets import QSpinBox
    low = [w for w in d.find(editor, QWidget, name='intOutPlaceholder').findChildren(QSpinBox) if w.isVisible()]
    d.log('SIZE MIN fields ' + str([w.text() for w in low]))
    d.set_number(low[0], 50)
    yield 0.5
    d.log('SIZE MIN now ' + low[0].text())
    yield from d.capture('k13_tuft_size', widget=editor)
    editor = yield from editor_page(d, 'Scatter')
    enable_option(d, editor, 'Scatter')
    yield 0.5
    yield from d.capture('k13_tuft_scatter', widget=editor)
    yield from save_preset(d, editor, 'Grass Tuft')
    yield from close_editor(d)
    yield 1

    # Show the hidden layers again, hide the tufts layer, select the base layer, and stamp in three passes: dark, light, then a few highlights.
    d.action('deselect')
    yield 0.5
    for name in ('Paint Layer 1', 'Background', 'Paint Layer 2'):
        yield from layer_eye(d, name)
    yield from layer_select(d, 'Paint Layer 1')
    yield 1
    d.log('LAYERS ' + str([(node.name(), node.visible()) for node in document.topLevelNodes()]))
    d.log('ACTIVE ' + document.activeNode().name())
    yield from d.slider(d.toolbar_slider('Size'), 110)
    random.seed(31)

    def wander(count, length, centers=None, reach=0):
        # Strokes that wander, from anywhere or from near the given centers.
        for index in range(count):
            if centers:
                cx, cy = random.choice(centers)
                x, y = cx + random.uniform(-reach, reach), cy + random.uniform(-reach, reach)
            else:
                x, y = random.uniform(0, 512), random.uniform(0, 512)
            heading = random.uniform(0, 2 * math.pi)
            points = [(x, y)]
            for step in range(int(length / 20)):
                heading += random.uniform(-0.6, 0.6)
                x, y = x + 20 * math.cos(heading), y + 20 * math.sin(heading)
                points.append((x, y))
            yield from painter.stroke(points)

    # Dark everywhere, leaving small gaps; light in a few broad patches; highlights only in the patches' middles.
    patches = [(random.uniform(0, 512), random.uniform(0, 512)) for _ in range(5)]
    yield from d.foreground(DARK)
    yield from wander(12, 320)
    yield from d.capture('k13_pass_dark')
    yield from d.foreground(LIGHT)
    yield from wander(12, 160, patches, 70)
    yield from d.capture('k13_pass_light')
    yield from d.foreground(HIGHLIGHT)
    yield from wander(7, 60, patches, 25)
    yield 1
    yield from d.capture('k13_pass_highlight')
    d.action('zoom_to_fit')
    yield 0.5
    for _ in range(2):
        d.action('view_zoom_out')
        yield 0.5
    yield 1
    yield from d.capture('k13_far')
    yield from save_and_export(d, document, 'grass_albedo')
