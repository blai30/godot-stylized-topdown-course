# Lesson 29: paints the pine's needle atlas, the reader's way: the Twig brush from lesson 14 makes every needle, as a
# short tapered stroke leaving a twig, in a few cool and warm grays. Saves pine_atlas.kra and pine_atlas.png.
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ground_painting import WORKBENCH
from lesson25 import new_atlas, show_grid

CELL = 512
# Cool and warm grays as hue, saturation, value; needles read darker than leaves, around 0.4.
COLORS = [(215, 14, 52), (210, 18, 44), (222, 10, 60), (34, 18, 56)]
TWIG = (215, 10, 30)


def spray(rng, cell):
    # Short twig strokes up the middle of the cell, and on each, needles that fan out and up from it.
    x0, y0 = (cell % 2) * CELL, (cell // 2) * CELL
    bend = rng.uniform(-14, 14)
    twig = [(x0 + 256, y0 + 480), (x0 + 256 + bend, y0 + 330), (x0 + 256 + bend * 1.6, y0 + 120)]
    needles = []
    for side in (-1, 1):
        for step in range(24):
            t = 0.06 + 0.88 * step / 23
            base_x = x0 + 256 + bend * t * 1.6
            base_y = y0 + 480 - 340 * t
            reach = 210 * (1 - 0.45 * abs(t - 0.4))
            angle = math.radians(rng.uniform(40, 72))
            tip = (base_x + side * math.sin(angle) * reach * rng.uniform(0.8, 1.1), base_y - math.cos(angle) * reach * rng.uniform(0.8, 1.1))
            needles.append(((base_x, base_y), tip))
    return twig, needles


def save_and_export(d, document, name):
    for folder in ('art_source/nature/tree_pine', 'art/nature/tree_pine'):
        os.makedirs(os.path.join(WORKBENCH, folder), exist_ok=True)
    d.action('file_save_as')
    yield 3
    yield from d.file_dialog('Saving As', os.path.join(WORKBENCH, 'art_source', 'nature', 'tree_pine', name + '.kra'))
    yield 4
    d.log('SAVED ' + str(document.fileName()))
    d.action('file_export_file')
    yield 3
    yield from d.file_dialog('Exporting', os.path.join(WORKBENCH, 'art', 'nature', 'tree_pine', name + '.png'))
    yield 3
    options = d.top('PNG image')
    from PyQt5.QtWidgets import QPushButton
    yield from d.capture('k29_png_options', widget=options)
    d.click(d.find(options, QPushButton, text='&OK'))
    yield 3
    d.log('EXPORTED {}'.format(os.path.getsize(os.path.join(WORKBENCH, 'art', 'nature', 'tree_pine', name + '.png'))))


def steps(d):
    yield 2
    rng = random.Random(29)
    document, painter = yield from new_atlas(d)
    yield from show_grid(d)
    sprays = [spray(rng, cell) for cell in range(4)]
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    # The twigs: the Basic-2 Opacity brush, thin and dark.
    yield from d.preset('Basic-2 Opacity')
    yield from d.slider(d.toolbar_slider('Size'), 8)
    yield from d.slider(d.toolbar_slider('Opacity'), 100)
    yield from d.foreground(TWIG)
    for twig, _ in sprays:
        yield from painter.stroke(twig)
    yield from d.capture('k29_twigs')
    # The needles: the Twig brush tapers each stroke to a point.
    yield from d.preset('Twig')
    yield from d.slider(d.toolbar_slider('Size'), 14)
    for index, color in enumerate(COLORS):
        yield from d.foreground(color)
        for _, needles in sprays:
            for number, (start, tip) in enumerate(needles):
                if number % len(COLORS) == index:
                    yield from painter.stroke([start, ((start[0] + tip[0]) / 2, (start[1] + tip[1]) / 2), tip])
        yield from d.capture('k29_color_{}'.format(index))
    yield from d.capture('k29_atlas')
    yield from save_and_export(d, document, 'pine_atlas')
    d.log('DONE')
