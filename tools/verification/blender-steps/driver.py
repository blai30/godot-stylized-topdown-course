# Replays a lesson's steps in Blender's real interface. The step script (BLENDER_STEPS) defines steps(driver), a
# generator that yields the seconds to wait before its next step. Blender runs with --enable-event-simulate, so the
# steps press keys and move the mouse through Window.event_simulate while input from the system is ignored: nothing
# touches the system mouse or keyboard, and nobody at the computer can disturb a run. Captures come from Blender's
# own screenshot operator.
import os
import traceback
import types

import bpy

OUT = os.environ['BLENDER_OUT']
LOG = os.environ['BLENDER_LOG']
STEPS = os.environ['BLENDER_STEPS']
WORKBENCH = os.path.join(os.environ['TEMP'], 'sgt-phase1', 'workbench')
pointer = [0, 0]


def log(message):
    with open(LOG, 'a', encoding='utf-8') as file:
        file.write(str(message) + '\n')


def window():
    return bpy.context.window_manager.windows[0]


def area(kind, index=0):
    found = [item for item in window().screen.areas if item.type == kind]
    if not found:
        raise RuntimeError('no area ' + kind)
    return found[index]


def region(area_item, kind='WINDOW'):
    return [item for item in area_item.regions if item.type == kind][0]


def center(area_item, kind='WINDOW'):
    # Window coordinates of a region's center; Blender's origin is the bottom left.
    found = region(area_item, kind)
    return found.x + found.width // 2, found.y + found.height // 2


def shot(name, target=None):
    # target is another Blender window, such as the file browser.
    with bpy.context.temp_override(window=target or window()):
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT, name + '.png'), check_existing=False)
    log('shot ' + name)


def browser():
    # The file browser Blender opens in its own window for Save As and Open.
    return bpy.context.window_manager.windows[-1]


def move(x, y):
    pointer[:] = [x, y]
    window().event_simulate('MOUSEMOVE', 'NOTHING', x=x, y=y)


def key(name, ctrl=False, shift=False, alt=False, text=None, target=None):
    # A key press and release at the pointer, as Blender's keymaps act on the area under the mouse. target is another
    # Blender window, such as the file browser.
    x, y = pointer
    for value in ('PRESS', 'RELEASE'):
        (target or window()).event_simulate(name, value, unicode=text if value == 'PRESS' else None, x=x, y=y, ctrl=ctrl, shift=shift, alt=alt)


def type_text(text, target=None):
    names = {'.': ('PERIOD', False), '-': ('MINUS', False), ' ': ('SPACE', False), '_': ('MINUS', True), '/': ('SLASH', False),
             ':': ('SEMI_COLON', True), '\\': ('BACK_SLASH', False)}
    for character in text:
        if character.isdigit():
            name, shift = 'ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE'.split()[int(character)], False
        elif character.isalpha():
            name, shift = character.upper(), character.isupper()
        else:
            name, shift = names[character]
        key(name, shift=shift, text=character, target=target)


def click(x, y, button='LEFTMOUSE', ctrl=False, shift=False, alt=False, target=None):
    # Simulated events carry no timing, so Blender never sees two of them as a double-click.
    pointer[:] = [x, y]
    target = target or window()
    target.event_simulate('MOUSEMOVE', 'NOTHING', x=x, y=y)
    for value in ('PRESS', 'RELEASE'):
        target.event_simulate(button, value, x=x, y=y, ctrl=ctrl, shift=shift, alt=alt)


def press(x, y, target=None, ctrl=False, shift=False):
    # A click on a button, as a generator: Blender highlights a button when the pointer arrives and only takes the
    # click after it has redrawn, as it always has by the time a person clicks.
    target = target or window()
    pointer[:] = [x, y]
    target.event_simulate('MOUSEMOVE', 'NOTHING', x=x, y=y)
    yield 0.2
    for value in ('PRESS', 'RELEASE'):
        target.event_simulate('LEFTMOUSE', value, x=x, y=y, ctrl=ctrl, shift=shift)
    yield 0.2


def wake():
    # After a file loads, Blender drops simulated keys until the window is clicked once; a reader's first click does
    # the same. A click on the status bar at the bottom changes nothing.
    click(1000, 5)


def drag(start, end, steps=10, button='LEFTMOUSE'):
    # A generator: the step script yields from it so the moves are spread over time.
    move(*start)
    window().event_simulate(button, 'PRESS', x=start[0], y=start[1])
    yield 0.05
    for index in range(1, steps + 1):
        move(start[0] + (end[0] - start[0]) * index // steps, start[1] + (end[1] - start[1]) * index // steps)
        yield 0.03
    window().event_simulate(button, 'RELEASE', x=end[0], y=end[1])
    yield 0.2


def override(kind='VIEW_3D'):
    # Context for an operator the step runs directly, in the given area's main region.
    found = area(kind)
    return bpy.context.temp_override(window=window(), screen=window().screen, area=found, region=region(found))


class Runner:
    def __init__(self):
        self.queue = None

    def start(self):
        try:
            namespace = {'__file__': STEPS}
            with open(STEPS, encoding='utf-8') as file:
                exec(compile(file.read(), STEPS, 'exec'), namespace)
            # Run with --python, this file is not an importable module, so the steps get its functions as a namespace.
            self.queue = namespace['steps'](types.SimpleNamespace(**globals()))
        except Exception:
            log('FAILED\n' + traceback.format_exc())
            return self.finish()
        return 0.5

    def tick(self):
        if self.queue is None:
            return self.start()
        try:
            delay = next(self.queue)
        except StopIteration:
            delay = None
        except Exception:
            log('FAILED\n' + traceback.format_exc())
            delay = None
        if delay is None:
            return self.finish()
        return delay

    def finish(self):
        log('[blender] done')
        bpy.ops.wm.quit_blender()
        return None


RUNNER = Runner()
log('[blender] driver loaded, Blender ' + bpy.app.version_string)
bpy.app.timers.register(RUNNER.tick, first_interval=3.0, persistent=True)
