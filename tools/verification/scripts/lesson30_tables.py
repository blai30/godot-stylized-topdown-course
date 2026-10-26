# Prints the lesson 30 node and link tables as MDX, from the same spec the step script builds, for the lesson page.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blender-steps'))
import grass_clump_spec as spec

ENUMS = {
    'data_type': {'FLOAT': 'Float', 'FLOAT_VECTOR': 'Vector', 'FLOAT_COLOR': 'Color', 'INT': 'Integer'},
    'domain': {'POINT': 'Point'},
    'operation': {'NORMALIZE': 'Normalize', 'ADD': 'Add', 'DIVIDE': 'Divide'},
    'distribute_method': {'RANDOM': 'Random'},
    'axis': {'Y': 'Y'},
    'pivot_axis': {'Z': 'Z'},
    'mode': {'RGB': 'RGB'},
    'transform_space': {'RELATIVE': 'Relative'},
    'use_clamp': {True: 'on'},
}
LABELS = {'data_type': 'type', 'domain': 'domain', 'operation': 'operation', 'distribute_method': 'method', 'axis': 'axis', 'pivot_axis': 'pivot', 'mode': 'mode', 'transform_space': 'space', 'use_clamp': 'Clamp'}


def number(value):
    if isinstance(value, tuple):
        return ', '.join(number(item) for item in value)
    return '%g' % value


def describe(settings, inputs):
    parts = []
    for name, value in settings.items():
        parts.append('%s **%s**' % (LABELS[name], ENUMS[name][value]))
    for name, value in inputs.items():
        label = name.replace('_001', ' (second)')
        if isinstance(value, bool):
            parts.append('**%s** checked' % label)
        elif isinstance(value, str):
            parts.append('%s `%s`' % (label, value) if name != 'Collection' else '%s **%s**' % (label, value))
        else:
            parts.append('%s `%s`' % (label, number(value)))
    return ', '.join(parts) if parts else 'nothing'


chapters = list(spec.CHAPTERS) + ([spec.PAINT_CHAPTER] if 'paint' in sys.argv[1:] else [])
for chapter in chapters:
    print('###', chapter['title'])
    print()
    print('| Node | Settings |')
    print('|---|---|')
    for key, search, settings, inputs in chapter['nodes']:
        print('|', '**%s**, from %s' % (spec.LABELS[key], search), '|', describe(settings, inputs), '|')
    print()
    print('| From | To |')
    print('|---|---|')
    for a, output, b, name in chapter['links']:
        print('|', '%s, %s' % (spec.LABELS.get(a, 'Group Input'), output), '|', '%s, %s' % (spec.LABELS.get(b, 'Group Output'), name.replace('_001', ' (second)')), '|')
    print()
