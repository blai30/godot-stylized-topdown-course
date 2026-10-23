# Copies the workbench into the course repository's reference/ folder: no capture driver, no .godot cache, no driver
# entry in project.godot, and LF line endings for text files.
import os
import re
import shutil
import sys

source, target = sys.argv[1], sys.argv[2]
skip_dirs = {'.godot', '.capture'}
text_suffixes = {'.godot', '.tscn', '.tres', '.gdshader', '.gdshaderinc', '.cs', '.csproj', '.sln', '.import', '.svg', '.cfg', '.md', '.uid', '.gitignore', '.gitattributes', '.editorconfig', '.gdignore'}

if os.path.exists(target):
    shutil.rmtree(target)
for root, dirs, files in os.walk(source):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for name in files:
        if name.endswith('.blend1'):
            continue
        src = os.path.join(root, name)
        dst = os.path.join(target, os.path.relpath(src, source))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        suffix = os.path.splitext(name)[1] or name
        if suffix in text_suffixes:
            text = open(src, encoding='utf-8-sig' if name.endswith('.sln') else 'utf-8').read().replace('\r\n', '\n')
            if name == 'project.godot':
                text = re.sub(r'\n\[editor_plugins\]\n\nenabled=PackedStringArray\("res://\.capture/plugin\.cfg"\)\n', '\n', text)
            open(dst, 'w', encoding='utf-8', newline='\n').write(text)
        else:
            shutil.copy2(src, dst)
print('synced', sum(len(f) for _, _, f in os.walk(target)), 'files')
