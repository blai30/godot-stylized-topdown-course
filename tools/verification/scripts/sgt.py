# The course's verification runner, one script for Windows, macOS, and Linux. It resets the workbench to a lesson's
# snapshot, replays a lesson's steps in Godot, Blender, or Krita, and chains lessons in order. Everything lives in a
# working area under the temp folder (set TEMP to move it), never inside the repository.
#
#   sgt.py reset lesson-06                     restore the workbench to a snapshot
#   sgt.py snapshot lesson-07                  save the workbench as a snapshot
#   sgt.py godot lesson05 [--snapshot lesson-04]
#   sgt.py blender lesson09 [--user lesson-08] [--save-user lesson-09] [--open file.blend]
#   sgt.py krita lesson13 [--user lesson-13] [--save-user lesson-14]
#   sgt.py chain module1|module2|module3 [--from 7] [--to 6]
#
# Setup, once per machine: put a copy of Godot's .NET editor in <temp>/sgt-phase1/godot-sc/ with an empty file named
# ._sc_ beside the executable (settings then stay in that folder, not the user's), and link or copy the lesson
# snapshots to <temp>/sgt-phase1/snapshots. Override the tool paths with SGT_GODOT, SGT_BLENDER, and SGT_KRITA.
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))
verification = os.path.dirname(here)
system = platform.system()
temp = os.environ.get('TEMP', tempfile.gettempdir())
base = os.path.join(temp, 'sgt-phase1')
work = os.path.join(temp, 'sgt-phase2')
workbench = os.path.join(base, 'workbench')
snapshots = os.path.join(base, 'snapshots')
home = os.path.expanduser('~')
FAILURE = re.compile(r'FAILED|TIMED OUT|SCRIPT ERROR|stopped')


def keep_awake():
    # A display that goes to sleep stalls an editor's windows; hold it awake for as long as this process lives.
    if system == 'Darwin':
        subprocess.Popen(['caffeinate', '-dimsu', '-w', str(os.getpid())])


def remove(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.lexists(path):
        os.remove(path)


def copy(source, target):
    if os.path.isdir(source):
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def read(path):
    return open(path, encoding='utf-8', errors='replace').read() if os.path.exists(path) else ''


# Workbench and snapshots.

def reset(snapshot):
    # Restores the workbench to a snapshot, keeping Godot's import cache. The editor remembers each scene's camera
    # and docks under .godot/editor; a reader opening the scene starts fresh.
    os.makedirs(workbench, exist_ok=True)
    for name in os.listdir(workbench):
        if name not in ('.godot', '.capture'):
            remove(os.path.join(workbench, name))
    source = os.path.join(snapshots, snapshot)
    for name in os.listdir(source):
        if name not in ('.godot', '.capture'):
            copy(os.path.join(source, name), os.path.join(workbench, name))
    remove(os.path.join(workbench, '.godot', 'editor'))
    return ['reset to ' + snapshot]


def snapshot(name):
    target = os.path.join(snapshots, name)
    remove(target)
    os.makedirs(target)
    for item in os.listdir(workbench):
        if item not in ('.godot', '.capture'):
            copy(os.path.join(workbench, item), os.path.join(target, item))
    return ['saved ' + name]


# Godot.

def godot_executable():
    if os.environ.get('SGT_GODOT'):
        return os.environ['SGT_GODOT']
    folder = os.path.join(base, 'godot-sc')
    if system == 'Windows':
        return os.path.join(folder, 'Godot_v4.8-beta1_mono_win64_console.exe')
    if system == 'Darwin':
        return os.path.join(folder, 'Godot_mono.app', 'Contents', 'MacOS', 'Godot')
    return next((os.path.join(folder, name) for name in sorted(os.listdir(folder)) if name.startswith('Godot') and os.access(os.path.join(folder, name), os.X_OK) and os.path.isfile(os.path.join(folder, name))), 'godot')


def editor_settings():
    # The self-contained editor runs at 100% scale and plays the game in its own window, at the project's size, so
    # game captures are full resolution and not the embedded Game tab's smaller view.
    path = os.path.join(base, 'godot-sc', 'editor_data', 'editor_settings-4.8.tres')
    text = read(path)
    if not text:
        return
    for name, value in (('interface/editor/appearance/display_scale', 2), ('run/window_placement/game_embed_mode', -1)):
        if re.search(r'^' + re.escape(name) + r' = ', text, re.M):
            text = re.sub(r'^(' + re.escape(name) + r' = ).*$', lambda match: match.group(1) + str(value), text, flags=re.M)
    open(path, 'w', encoding='utf-8', newline='\n').write(text)


def run_steps(steps, out, timeout=300):
    # Opens the workbench in the self-contained editor and replays a steps file; returns the driver's step log and any
    # script errors. Probe output stays in the editor log, editor.log.
    os.makedirs(out, exist_ok=True)
    editor_settings()
    log = os.path.join(base, 'editor.log')
    steps_log = os.path.join(base, 'steps.log')
    remove(log)
    remove(steps_log)
    environment = dict(os.environ, CAPTURE_STEPS=steps, CAPTURE_OUT=out, CAPTURE_LOG=steps_log, TEMP=temp)
    process = subprocess.Popen([godot_executable(), '--editor', '--path', workbench, '--resolution', '1920x1080', '--log-file', log],
                               env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + timeout
    # The driver logs "[capture] done" after the last step; the editor does not always quit by itself after a game run.
    while process.poll() is None and time.time() < deadline:
        time.sleep(2)
        if re.search(r'^\[capture\] done', read(steps_log), re.M):
            time.sleep(3)
            break
    lines = []
    if process.poll() is None:
        if time.time() >= deadline:
            lines.append('TIMED OUT')
        process.kill()
        process.wait()
    lines += read(steps_log).splitlines()
    lines += [line for line in read(log).splitlines() if 'SCRIPT ERROR' in line or line.startswith('ERROR:')]
    return lines


def godot(script, snapshot=None, out=None, timeout=300):
    # Resets the workbench to a snapshot (if given), compiles a step script, and replays it in the editor.
    out = out or os.path.join(work, 'shots')
    if snapshot:
        reset(snapshot)
    capture = os.path.join(workbench, '.capture')
    os.makedirs(capture, exist_ok=True)
    for name in os.listdir(os.path.join(verification, 'godot-driver')):
        shutil.copy2(os.path.join(verification, 'godot-driver', name), capture)
    # The drivers are registered in the workbench only, never in a snapshot, so every run has both.
    project = os.path.join(workbench, 'project.godot')
    text = read(project).replace('\r\n', '\n')
    if 'res://.capture/plugin.cfg' not in text:
        text += '\n[editor_plugins]\n\nenabled=PackedStringArray("res://.capture/plugin.cfg")\n'
    if 'GameDriver=' not in text:
        text += '\n[autoload]\n\nGameDriver="*res://.capture/game_driver.gd"\n'
    open(project, 'w', encoding='utf-8', newline='\n').write(text)
    steps = os.path.join(base, 'steps-' + script + '.jsonl')
    subprocess.run([sys.executable, os.path.join(verification, 'steps', script + '.py'), os.path.join(verification, 'steps'), steps],
                   check=True, env=dict(os.environ, TEMP=temp))
    lines = run_steps(steps, out, timeout)
    return [line for line in lines if re.search(r'FAILED|stopped|TIMED OUT|\[probe\]|SCRIPT ERROR', line)]


# Blender.

def blender(script, user='fresh', save_user=None, open_file=None, timeout=600):
    # Blender's user folder (preferences and startup file) lives in the working area, not the user's; a run starts
    # from a saved folder, or from none (a first launch), and can save the folder it leaves for the next lesson.
    executable = os.environ.get('SGT_BLENDER') or {'Windows': r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
                                                    'Darwin': '/Applications/Blender.app/Contents/MacOS/Blender'}.get(system, 'blender')
    users = os.path.join(work, 'blender-users')
    resources = os.path.join(work, 'blender-user')
    out = os.path.join(work, 'shots', 'blender')
    log = os.path.join(work, 'blender-steps.log')
    os.makedirs(out, exist_ok=True)
    os.makedirs(users, exist_ok=True)
    remove(resources)
    remove(log)
    if user != 'fresh':
        copy(os.path.join(users, user), resources)
    # Each folder is set, and made, as well: for a missing one Blender falls back to the user's own Blender folder and
    # reads their preferences and recent files.
    folders = {name: os.path.join(resources, sub) for name, sub in (('CONFIG', 'config'), ('SCRIPTS', 'scripts'), ('DATAFILES', 'datafiles'), ('EXTENSIONS', 'extensions'))}
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    environment = dict(os.environ, TEMP=temp, BLENDER_USER_RESOURCES=resources, BLENDER_STEPS=os.path.join(verification, 'blender-steps', script + '.py'),
                       BLENDER_OUT=out, BLENDER_LOG=log, **{'BLENDER_USER_' + name: folder for name, folder in folders.items()})
    # The window is 1920 by 1080 pixels; macOS sizes windows in points, and a Retina screen has two pixels to a point.
    geometry = ['0', '0', '960', '540'] if system == 'Darwin' else ['0', '0', '1920', '1080']
    command = [executable] + ([open_file] if open_file else []) + ['--window-geometry'] + geometry + ['--enable-event-simulate', '--python', os.path.join(verification, 'blender-steps', 'driver.py')]
    lines = []
    with open(os.path.join(work, 'blender-out.txt'), 'wb') as stdout, open(os.path.join(work, 'blender-err.txt'), 'wb') as stderr:
        process = subprocess.Popen(command, env=environment, stdout=stdout, stderr=stderr)
        try:
            process.wait(timeout)
        except subprocess.TimeoutExpired:
            lines.append('TIMED OUT')
            process.kill()
    lines += read(log).splitlines()
    if save_user and not any(line.startswith('FAILED') for line in lines) and os.path.exists(log):
        remove(os.path.join(users, save_user))
        copy(resources, os.path.join(users, save_user))
        lines.append('saved user folder ' + save_user)
    return lines


# Krita.

def krita(script, user=None, save_user=None, out=None, timeout=300):
    # Krita keeps its settings in fixed places, so the existing ones are moved aside first and put back afterward, and
    # everything the run created is removed. A lesson that builds on an earlier one's brushes starts from Krita's
    # settings as that lesson left them.
    out = out or os.path.join(work, 'shots', 'krita')
    if system == 'Windows':
        local, roaming = os.environ['LOCALAPPDATA'], os.environ['APPDATA']
        items = [os.path.join(local, name) for name in ('kritarc', 'kritadisplayrc', 'krita', 'krita.log', 'krita-sysinfo.log')] + [os.path.join(roaming, 'krita')]
        plugins, rc = os.path.join(roaming, 'krita', 'pykrita'), os.path.join(local, 'kritarc')
        executable = r'C:\Program Files\Krita (x64)\bin\krita.com'
    elif system == 'Darwin':
        items = [os.path.join(home, 'Library', 'Preferences', name) for name in ('kritarc', 'kritadisplayrc')] + [os.path.join(home, 'Library', 'Application Support', 'krita')]
        plugins, rc = os.path.join(home, 'Library', 'Application Support', 'krita', 'pykrita'), os.path.join(home, 'Library', 'Preferences', 'kritarc')
        executable = '/Applications/krita.app/Contents/MacOS/krita'
    else:
        items = [os.path.join(home, '.config', name) for name in ('kritarc', 'kritadisplayrc')] + [os.path.join(home, '.local', 'share', 'krita')]
        plugins, rc = os.path.join(home, '.local', 'share', 'krita', 'pykrita'), os.path.join(home, '.config', 'kritarc')
        executable = shutil.which('krita') or 'krita'
    executable = os.environ.get('SGT_KRITA') or executable
    backup, users, log = os.path.join(work, 'krita-backup'), os.path.join(work, 'krita-users'), os.path.join(work, 'krita-steps.log')
    stored = lambda item: item.replace(os.sep, '_').replace(':', '_')
    # A leftover backup means an earlier run never restored; restore it by hand before running again.
    if os.path.exists(backup):
        raise SystemExit('Backup folder {} exists; restore it before running.'.format(backup))
    os.makedirs(backup)
    os.makedirs(out, exist_ok=True)
    moved = []
    for item in items:
        if os.path.lexists(item):
            saved = os.path.join(backup, stored(item))
            shutil.move(item, saved)
            moved.append((item, saved))
    lines = []
    try:
        if user:
            for item in items:
                saved = os.path.join(users, user, stored(item))
                if os.path.lexists(saved):
                    os.makedirs(os.path.dirname(item), exist_ok=True)
                    copy(saved, item)
        os.makedirs(os.path.dirname(plugins), exist_ok=True)
        shutil.copytree(os.path.join(verification, 'krita-driver'), plugins, dirs_exist_ok=True)
        if not user:
            os.makedirs(os.path.dirname(rc), exist_ok=True)
            # Krita's own file dialog, not the system's, so the driver fills it the same way on every platform.
            open(rc, 'w', encoding='utf-8', newline='\n').write('[File Dialogs]\nDontUseNativeFileDialog=true\n\n[python]\nenable_sgt_driver=true\n')
        # Krita's window is 1920 by 1080 in its own units; a Retina laptop screen has fewer points than that, so its
        # interface is scaled to 75 percent on screen, and layout and captures keep their size on every platform.
        scale = {'QT_SCALE_FACTOR': '0.75'} if system == 'Darwin' else {}
        environment = dict(os.environ, **scale, KRITA_STEPS=os.path.join(verification, 'krita-steps', script + '.py'), KRITA_OUT=out, KRITA_LOG=log, TEMP=temp)
        remove(log)
        with open(os.path.join(work, 'krita-out.txt'), 'wb') as stdout, open(os.path.join(work, 'krita-err.txt'), 'wb') as stderr:
            process = subprocess.Popen([executable, '--nosplash'], env=environment, stdout=stdout, stderr=stderr)
            deadline = time.time() + timeout
            while process.poll() is None and time.time() < deadline:
                time.sleep(2)
                if '[krita] done' in read(log):
                    break
            if time.time() >= deadline:
                lines.append('TIMED OUT')
            if process.poll() is None:
                process.kill()
                process.wait()
                time.sleep(2)
        lines += read(log).splitlines()
        if save_user:
            target = os.path.join(users, save_user)
            remove(target)
            os.makedirs(target)
            for item in items:
                if os.path.lexists(item):
                    copy(item, os.path.join(target, stored(item)))
    finally:
        for item in items:
            remove(item)
        for item, saved in moved:
            shutil.move(saved, item)
        shutil.rmtree(backup)
    return lines


# Chains: each lesson starts from the snapshot the one before saved, and the chain stops at the first failure.

def check(lines, label):
    failed = [line for line in lines if FAILURE.search(line)]
    for line in failed:
        print(line)
    if failed:
        raise SystemExit('chain stopped at ' + label)


def say(lines):
    for line in lines:
        print(line)


def chain_module1(first=2, last=6):
    for lesson in range(first, last + 1):
        script, previous, target = 'lesson%02d' % lesson, 'lesson-%02d' % (lesson - 1), 'lesson-%02d' % lesson
        print('== {} from {}'.format(script, previous))
        lines = godot(script, previous, timeout=590)
        say([line for line in lines if not line.endswith(' ok')])
        for name in ('steps', 'editor'):
            if os.path.exists(os.path.join(base, name + '.log')):
                shutil.copy2(os.path.join(base, name + '.log'), os.path.join(base, '{}-{}.log'.format(name, script)))
        check(lines, target + ' not saved')
        say(snapshot(target))


def chain_module2(first=7):
    blend = os.path.join(workbench, 'art_source', 'nature', 'rock_small', 'rock_small.blend')
    save_user = lambda name: (remove(os.path.join(work, 'blender-users', name)), copy(os.path.join(work, 'blender-user'), os.path.join(work, 'blender-users', name)))
    if first <= 7:
        reset('lesson-06')
        check(krita('lesson07', timeout=600), 'lesson 7')
        say(snapshot('lesson-07'))
    if first <= 8:
        reset('lesson-07')
        check(blender('lesson08', save_user='lesson-08', timeout=300), 'lesson 8')
        say(snapshot('lesson-08'))
    if first <= 9:
        reset('lesson-08')
        check(blender('lesson09', user='lesson-08', timeout=300), 'lesson 9')
        save_user('lesson-09')
        say(snapshot('lesson-09'))
    if first <= 10:
        reset('lesson-09')
        check(blender('lesson10', user='lesson-09', open_file=blend, timeout=300), 'lesson 10')
        save_user('lesson-10')
        say(snapshot('lesson-10'))
    if first <= 11:
        check(godot('lesson11', 'lesson-10', timeout=400), 'lesson 11')
        say([line for line in read(os.path.join(base, 'game-l11.log')).splitlines() if 'player' in line])
        say(snapshot('lesson-11'))
    if first <= 12:
        reset('lesson-11')
        check(blender('lesson12', user='lesson-10', open_file=blend, timeout=300), 'lesson 12 in Blender')
        save_user('lesson-12')
        say(snapshot('lesson-12a'))
        check(godot('lesson12', 'lesson-12a', timeout=400), 'lesson 12 in Godot')
        say([line for line in read(os.path.join(base, 'game-l12.log')).splitlines() if 'player' in line])
        say(snapshot('lesson-12'))


def chain_module3(first=13):
    editor_log = os.path.join(base, 'editor.log')
    probes = lambda pattern: say([line for line in read(editor_log).splitlines() if re.search(pattern, line)])
    if first <= 13:
        # Lesson 13 draws the grass detail with a C# tool script, all in Godot.
        reset('lesson-12')
        check(godot('lesson13', timeout=900), 'lesson 13')
        probes(r'\[probe\] (piece|grass)')
        say(snapshot('lesson-13'))
    if first <= 14:
        if first == 14:
            reset('lesson-13')
        lines = krita('lesson14', save_user='lesson-14', timeout=2400)
        open(os.path.join(work, 'krita-lesson14.log'), 'w', encoding='utf-8').write('\n'.join(lines))
        check(lines, 'lesson 14 in Krita')
        check(godot('lesson14', timeout=300), 'lesson 14 in Godot')
        probes(r'\[probe\] (dirt|sand)')
        say(snapshot('lesson-14'))
    for lesson, timeout, game, pattern in ((15, 400, None, r'\[probe\] (tile|texture|newer on disk)'), (16, 500, 'l16', None), (17, 600, 'l17', None), (18, 600, 'l18', None)):
        if first <= lesson:
            check(godot('lesson%d' % lesson, 'lesson-%d' % (lesson - 1), timeout=timeout), 'lesson %d' % lesson)
            if pattern:
                probes(pattern)
            if game:
                say([line for line in read(os.path.join(base, 'game-{}.log'.format(game))).splitlines() if re.search(r'player|tile ', line)])
            say(snapshot('lesson-%d' % lesson))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('reset').add_argument('snapshot')
    commands.add_parser('snapshot').add_argument('name')
    one = commands.add_parser('godot')
    one.add_argument('script')
    one.add_argument('--snapshot')
    one.add_argument('--out')
    one.add_argument('--timeout', type=int, default=300)
    other = commands.add_parser('blender')
    other.add_argument('script')
    other.add_argument('--user', default='fresh')
    other.add_argument('--save-user')
    other.add_argument('--open')
    other.add_argument('--timeout', type=int, default=600)
    paint = commands.add_parser('krita')
    paint.add_argument('script')
    paint.add_argument('--user')
    paint.add_argument('--save-user')
    paint.add_argument('--out')
    paint.add_argument('--timeout', type=int, default=300)
    many = commands.add_parser('chain')
    many.add_argument('module', choices=('module1', 'module2', 'module3'))
    many.add_argument('--from', dest='first', type=int)
    many.add_argument('--to', dest='last', type=int)
    arguments = parser.parse_args()
    keep_awake()
    if arguments.command == 'reset':
        say(reset(arguments.snapshot))
    elif arguments.command == 'snapshot':
        say(snapshot(arguments.name))
    elif arguments.command == 'godot':
        say(godot(arguments.script, arguments.snapshot, arguments.out, arguments.timeout))
    elif arguments.command == 'blender':
        say(blender(arguments.script, arguments.user, arguments.save_user, arguments.open, arguments.timeout))
    elif arguments.command == 'krita':
        say(krita(arguments.script, arguments.user, arguments.save_user, arguments.out, arguments.timeout))
    elif arguments.module == 'module1':
        chain_module1(arguments.first or 2, arguments.last or 6)
    elif arguments.module == 'module2':
        chain_module2(arguments.first or 7)
    else:
        chain_module3(arguments.first or 13)
    print('done')


if __name__ == '__main__':
    main()
