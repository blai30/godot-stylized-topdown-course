# Lesson 60's command-line part, run between the two editor sessions (lesson60a, then this, then lesson60b): the workbench holds the
# template with the rename script in it, and this runs the script on it as a reader does, with Godot closed. A dry run first, then
# the real one, then a search for any file that still carries the old name. Output goes to <temp>/sgt-phase2/l60_*.txt.
import os
import subprocess
import sys
import tempfile

temp = os.environ.get('TEMP', tempfile.gettempdir())
workbench = os.path.join(temp, 'sgt-phase1', 'workbench')
executable = os.environ.get('SGT_GODOT') or os.path.join(temp, 'sgt-phase1', 'godot-sc', 'Godot_mono.app', 'Contents', 'MacOS', 'Godot')
studio = sys.argv[1] if len(sys.argv) > 1 else 'Moon Studio'
game = sys.argv[2] if len(sys.argv) > 2 else 'MoonQuest'
out = os.path.join(temp, 'sgt-phase2')
os.makedirs(out, exist_ok=True)


def run(name, *extra):
    command = [executable, '--headless', '--path', workbench, '--script', 'res://tools/rename_project.gd', '--', studio, game, *extra]
    result = subprocess.run(command, capture_output=True, text=True)
    text = '\n'.join(line for line in (result.stdout + result.stderr).splitlines() if not line.startswith('Godot Engine'))
    open(os.path.join(out, f'l60_{name}.txt'), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
    print(f'--- {name} (exit {result.returncode})\n{text.strip()}')
    return result.returncode


run('dry_run', '--dry-run')
code = run('rename')
leftovers = []
for folder, names, files in os.walk(workbench):
    names[:] = [name for name in names if name not in ('.godot', '.git', '.capture')]
    for file in files:
        path = os.path.join(folder, file)
        try:
            text = open(path, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        if 'TopDownTemplate' in text or 'topdowntemplate' in text or 'TopDownTemplate' in file:
            leftovers.append(os.path.relpath(path, workbench))
print('--- files that still carry the old name:', leftovers or 'none')
sys.exit(code)
