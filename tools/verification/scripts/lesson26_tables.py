# Prints the lesson 26 node and link tables as MDX, from the same spec the step script builds, for the lesson page.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blender-steps'))
import leaf_cards_spec as spec

ENUMS = {
    'data_type': {'FLOAT': 'Float', 'FLOAT_VECTOR': 'Vector', 'FLOAT_COLOR': 'Color', 'FLOAT2': '2D Vector', 'INT': 'Integer'},
    'domain': {'POINT': 'Point', 'INSTANCE': 'Instance', 'CORNER': 'Face Corner'},
    'operation': {'GREATER_THAN': 'Greater Than', 'SCALE': 'Scale', 'ADD': 'Add', 'NORMALIZE': 'Normalize'},
    'distribute_method': {'RANDOM': 'Random'},
    'axis': {'Z': 'Z', 'Y': 'Y'},
    'pivot_axis': {'AUTO': 'Auto', 'Z': 'Z'},
    'mode': {'RGB': 'RGB', 'FREE': 'Free'},
}
LABELS = {'data_type': 'type', 'domain': 'domain', 'operation': 'operation', 'distribute_method': 'method', 'axis': 'axis', 'pivot_axis': 'pivot', 'mode': 'mode'}
TITLES = {'Position': 'Position', 'Compare': 'Compare', 'Grid': 'Grid'}


def number(value):
    if isinstance(value, tuple):
        return ', '.join(number(item) for item in value)
    return '%g' % value


def node_title(key, search, settings):
    # The header Blender shows after the settings: Compare reads as its operation, Vector Math too.
    if search == 'Compare':
        return ENUMS['operation'][settings['operation']]
    if search == 'Vector Math':
        return ENUMS['operation'][settings['operation']]
    return search


def describe(search, settings, inputs):
    parts = []
    for name, value in settings.items():
        parts.append('%s **%s**' % (LABELS[name], ENUMS[name][value]))
    for name, value in inputs.items():
        label = name.replace('_001', ' (second)')
        parts.append('%s `%s`' % (label, value if isinstance(value, str) else number(value)))
    return ', '.join(parts) if parts else 'nothing'


def link_row(chapter, keys, link):
    a, output, b, name = link
    names = {key: (search + ('' if search not in ('Vector Math', 'Compare') else '')) for key, search, _, _ in chapter['nodes']}
    return a, output, b, name


for chapter in spec.CHAPTERS:
    print('###', chapter['title'])
    print()
    print('| Node | Settings |')
    print('|---|---|')
    for key, search, settings, inputs in chapter['nodes']:
        print('|', '**%s**, from %s' % (spec.LABELS[key], search), '|', describe(search, settings, inputs), '|')
    print()
    print('| From | To |')
    print('|---|---|')
    for a, output, b, name in chapter['links']:
        print('|', '%s, %s' % (spec.LABELS.get(a, 'Group Input'), output), '|', '%s, %s' % (spec.LABELS.get(b, 'Group Output'), name.replace('_001', ' (second)')), '|')
    print()
