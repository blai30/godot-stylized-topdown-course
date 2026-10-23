# Writes lesson 15's code pieces, exactly as the editor run typed them, for the site to import.
import importlib.util
import os
import sys

spec = importlib.util.spec_from_file_location('lesson15b', sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[1], os.path.join(os.environ['TEMP'], 'sgt-phase1', 'tools'), os.devnull, sys.argv[2]]
spec.loader.exec_module(module)
for number in range(1, 5):
    path = os.path.join(sys.argv[3], f'piece-{number}.gdshader')
    open(path, 'w', encoding='utf-8', newline='\n').write(getattr(module, f'piece{number}'))
    print('wrote', path)
