# Writes a lesson's code pieces, exactly as the editor run typed them, and its checkpoint files, copied from the
# lesson's verified snapshot, for the site to import. Nothing is retyped, so the site cannot drift from what was run.
# Usage: export_pieces.py <lesson number> [snapshot files...]
#   export_pieces.py 6 src/Player/PlayerMovement.cs src/Camera/CameraRig.cs
import importlib.util
import os
import re
import sys

STEPS = {15: 'lesson15b', 5: 'lesson05', 6: 'lesson06'}
EXTENSIONS = {15: '.gdshader', 5: '.cs', 6: '.cs'}
verification = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
site = os.path.join(os.path.dirname(os.path.dirname(verification)), 'site', 'src', 'checkpoints')
lesson = int(sys.argv[1])
files = sys.argv[2:]
target = os.path.join(site, f'{lesson:02d}' if lesson < 10 else str(lesson))

if lesson in STEPS:
    path = os.path.join(verification, 'steps', STEPS[lesson] + '.py')
    spec = importlib.util.spec_from_file_location(STEPS[lesson], path)
    module = importlib.util.module_from_spec(spec)
    # Step scripts read their output path from argv; they write their steps there, which is discarded.
    saved, sys.argv = sys.argv, [path, os.path.join(verification, 'steps'), os.path.join(os.environ['TEMP'], 'export-discard.jsonl')]
    sys.path.insert(0, os.path.join(verification, 'steps'))
    spec.loader.exec_module(module)
    sys.argv = saved
    pieces = getattr(module, 'PIECES', None) or [getattr(module, f'piece{i}') for i in range(1, 10) if hasattr(module, f'piece{i}')]
    os.makedirs(os.path.join(target, 'pieces'), exist_ok=True)
    for number, code in enumerate(pieces, 1):
        out = os.path.join(target, 'pieces', f'piece-{number}{EXTENSIONS[lesson]}')
        open(out, 'w', encoding='utf-8', newline='\n').write(code)
        print('wrote', out)

snapshot = os.path.join(os.environ['TEMP'], 'sgt-phase1', 'snapshots', f'lesson-{lesson:02d}')
for name in files:
    text = open(os.path.join(snapshot, name), encoding='utf-8-sig').read().replace('\r\n', '\n')
    if name == 'project.godot':
        # The workbench's capture drivers are not part of the reader's project.
        text = re.sub(r'\n\[editor_plugins\]\n\nenabled=PackedStringArray\("res://\.capture/plugin\.cfg"\)\n', '', text)
        text = re.sub(r'\n\[autoload\]\n\nGameDriver="\*res://\.capture/game_driver\.gd"\n', '', text)
    out = os.path.join(target, 'files', name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote', out)
