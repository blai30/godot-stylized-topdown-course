# Drives Blender's node editor through the simulated mouse and keys, as the reader does: Shift+A and a search to add a
# node, a click and typing to set a field, a drag from one socket to another to link. Where a socket or field is on
# the screen is read from a screenshot of the node, because Blender's Python API does not say.
import os

import bpy
import numpy as np


class NodeUI:
    def __init__(self, d, tree):
        self.d = d
        self.tree = tree
        self.out = os.environ['BLENDER_OUT']

    # Geometry of the view.

    def editor(self):
        return self.d.area('NODE_EDITOR')

    def region(self):
        return self.d.region(self.editor())

    def scale(self):
        view = self.region().view2d
        return (view.view_to_region(100, 0, clip=False)[0] - view.view_to_region(0, 0, clip=False)[0]) / 100.0

    def to_screen(self, x, y):
        # Node space to window coordinates (origin at the bottom left).
        region = self.region()
        local = region.view2d.view_to_region(x, y, clip=False)
        return region.x + local[0], region.y + local[1]

    def bounds(self, node):
        # Window coordinates of a node: left, right, bottom, top.
        scale = self.scale()
        left, top = self.to_screen(node.location.x, node.location.y)
        return left, left + node.dimensions.x * scale, top - node.dimensions.y * scale, top

    def frame(self, nodes):
        # View > Frame Selected on the given nodes.
        for node in self.tree.nodes:
            node.select = node in nodes
        self.redraw()
        with self.d.override('NODE_EDITOR'):
            bpy.ops.node.view_selected()
        self.redraw()

    def redraw(self):
        # Blender draws only when something asks it to: after a change made from a script, ask.
        self.editor().tag_redraw()
        with bpy.context.temp_override(window=self.d.window(), screen=self.d.window().screen):
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    # Reading the screen.

    def grab(self):
        path = os.path.join(self.out, '_detect.png')
        with bpy.context.temp_override(window=self.d.window()):
            bpy.ops.screen.screenshot(filepath=path, check_existing=False)
        image = bpy.data.images.load(path)
        width, height = image.size
        pixels = np.empty(width * height * 4, np.float32)
        image.pixels.foreach_get(pixels)
        bpy.data.images.remove(image)
        os.remove(path)
        return pixels.reshape(height, width, 4)[..., :3]

    def blobs(self, image, x, y_low, y_high):
        # Rows along column x, between y_low and y_high, where the pixel is unlike the node's body color: socket glyphs.
        column = np.median(image[int(y_low):int(y_high), int(x) - 1:int(x) + 2], axis=1)
        body = np.median(column, axis=0)
        different = np.abs(column - body).max(axis=1) > 0.12
        found, start = [], None
        for row, flag in enumerate(different):
            if flag and start is None:
                start = row
            if not flag and start is not None:
                if row - start >= 2:
                    found.append(y_low + (start + row - 1) / 2.0)
                start = None
        if start is not None and len(different) - start >= 2:
            found.append(y_low + (start + len(different) - 1) / 2.0)
        return found

    def merged(self, image, x, y_low, y_high):
        # Glyphs found along a few columns around the node's edge, as one list, top to bottom.
        rows = []
        for shift in range(-3, 4):
            rows += self.blobs(image, x + shift, y_low, y_high)
        rows.sort(reverse=True)
        merged = []
        for row in rows:
            if merged and merged[-1][-1] - row < 5:
                merged[-1].append(row)
            else:
                merged.append([row])
        return [sum(group) / len(group) for group in merged]

    def sockets(self, node):
        # {'in': [y of each drawn input socket, top to bottom], 'out': [...]} in window coordinates, plus the x of each edge.
        for other in self.tree.nodes:
            other.select = False
        self.redraw()
        yield 0.4
        image = self.grab()
        left, right, bottom, top = self.bounds(node)
        scale = self.scale()
        header = 24 * scale
        ins = self.merged(image, left, bottom + 3, top - header)
        outs = self.merged(image, right, bottom + 3, top - header)
        return {'in': ins, 'out': outs, 'left': left, 'right': right}

    # Doing things.

    def place(self, search, x, y, shot=None):
        # Shift+A over the editor, type the node's name, Enter, and click where it should go (node space x, y).
        d = self.d
        screen_x, screen_y = [int(round(v)) for v in self.to_screen(x, y)]
        d.move(screen_x, screen_y)
        d.key('A', shift=True)
        yield 0.5
        if shot:
            d.shot(shot + '_menu')
        d.type_text(search.lower())
        yield 0.6
        if shot:
            d.shot(shot + '_search')
        d.key('RET')
        yield 0.4
        d.click(screen_x, screen_y)
        yield 0.5
        node = self.tree.nodes[-1]
        return node

    def type_into(self, x, y, text):
        d = self.d
        x, y = int(round(x)), int(round(y))
        yield from d.press(x, y)
        yield 0.2
        d.key('A', ctrl=True)
        d.type_text(text)
        d.key('RET')
        yield 0.3

    def link(self, start, end):
        yield from self.d.drag((int(round(start[0])), int(round(start[1]))), (int(round(end[0])), int(round(end[1]))), steps=14)
        yield 0.3

    # Socket bookkeeping.

    @staticmethod
    def drawn(node, output):
        return [item for item in (node.outputs if output else node.inputs) if item.enabled and not item.hide]

    def index_of(self, node, name, output):
        # Position of a named socket among the drawn ones; 'Vector_001' is the second socket called Vector.
        position = 0
        if name.endswith('_001'):
            name, position = name[:-4], 1
        matches = [index for index, item in enumerate(self.drawn(node, output)) if item.name == name]
        return matches[position]

    def input_y(self, node, name, found):
        # The y of a named input among the detected socket glyphs. An unlinked vector input also draws glyph-like
        # rows for its three fields, so the detected list can be longer than the drawn sockets: sockets after the
        # first such input count from the bottom.
        drawn = self.drawn(node, False)
        index = self.index_of(node, name, False)
        detected = found['in']
        if len(detected) == len(drawn):
            return detected[index]
        first = next((position for position, item in enumerate(drawn) if item.type in ('VECTOR', 'ROTATION') and not item.is_linked and not item.hide_value), len(drawn))
        return detected[index] if index <= first else detected[index - len(drawn)]

    @staticmethod
    def matches(socket, value):
        got = socket.default_value
        if isinstance(value, str):
            return got == value
        if isinstance(value, tuple):
            return all(abs(a - b) < 1e-4 for a, b in zip(got, value))
        return abs(got - value) < 1e-4

    def set_value(self, node, name, value, found):
        if name == 'Collection':
            # A collection is picked from its dropdown; the lesson names it, and the step sets it directly.
            self.drawn(node, False)[self.index_of(node, name, False)].default_value = bpy.data.collections[value]
            return
        if isinstance(value, bool):
            yield from self.set_checkbox(node, name, value, found)
            return
        # Clicks the socket's field and types; a vector's three fields are typed one after another with Tab. Typing
        # can miss (a keystroke lands before the field is editing), so a wrong value is typed again, up to three times.
        index = self.index_of(node, name, False)
        socket = self.drawn(node, False)[index]
        for attempt in range(3):
            yield from self.type_value(socket, value, found, index)
            if self.matches(socket, value):
                return
            self.d.log('RETYPE {} {} got {}'.format(node.name, name, socket.default_value))
        raise RuntimeError('field {}.{} stays {}'.format(node.name, name, socket.default_value))

    def set_checkbox(self, node, name, value, found):
        # A boolean input is a checkbox at the row's left; click it when it differs from the wanted state.
        index = self.index_of(node, name, False)
        socket = self.drawn(node, False)[index]
        if socket.default_value == value:
            return
        scale = self.scale()
        yield from self.d.press(int(round(found['left'] + 22 * scale)), int(round(found['in'][index])))
        yield 0.3
        if socket.default_value != value:
            raise RuntimeError('checkbox {}.{} stays {}'.format(node.name, name, socket.default_value))

    def type_value(self, socket, value, found, index):
        y = found['in'][index]
        x = (found['left'] + found['right']) / 2.0
        scale = self.scale()
        if socket.type == 'VECTOR':
            y = y - 22.4 * scale
            numbers = [str(number) for number in value]
            yield from self.d.press(int(round(x)), int(round(y)))
            yield 0.2
            for position, number in enumerate(numbers):
                self.d.key('A', ctrl=True)
                self.d.type_text(number)
                if position < 2:
                    self.d.key('TAB')
                    yield 0.1
            self.d.key('RET')
            yield 0.3
        else:
            yield from self.type_into(x, y, str(value))
