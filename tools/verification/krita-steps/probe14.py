# Probes lesson 14: which part of making the texture image breaks typing a brush size into the toolbar.
from PyQt5.QtWidgets import QAbstractSpinBox, QLineEdit, QPushButton, QTabWidget


def attempt(d, label):
    d.action('KritaShape/KisToolBrush')
    yield 0.5
    yield from d.preset('Basic-2 Opacity')
    try:
        yield from d.slider(d.toolbar_slider('Size'), 90)
        d.log('RESULT {} ok'.format(label))
    except RuntimeError as error:
        d.log('RESULT {} {}'.format(label, error))


def steps(d):
    import os
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from ground_painting import new_texture
    yield 2
    real_shot = d.shot
    d.shot = lambda *args, **kwargs: None
    document, painter = yield from new_texture(d, 'probe_albedo', (26, 46, 53), 'k14_probe')
    d.shot = real_shot
    yield from attempt(d, 'new_texture without shots')
