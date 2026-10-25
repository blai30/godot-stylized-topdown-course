# Lesson 24, extra captures: the Object menu over the finished tree (opened from the saved file, never saved).
def top(y, height=1080):
    return height - y


def steps(d):
    yield 2
    d.click(1400, 5)
    yield 0.5
    yield from d.press(312, top(38))
    yield 0.5
    d.move(330, top(60))
    yield 0.8
    d.shot('l24b_object_menu')
    d.key('ESC')
    yield 0.5
    # Mesh > Transform > Skin Resize, in Edit Mode.
    d.move(800, top(500))
    d.key('TAB')
    yield 0.6
    yield from d.press(356, top(38))
    yield 0.5
    d.move(370, top(50))
    yield 0.5
    d.move(393, top(60))
    yield 0.8
    d.move(420, top(60))
    yield 0.4
    d.shot('l24b_transform_menu')
    d.key('ESC')
    yield 0.4
