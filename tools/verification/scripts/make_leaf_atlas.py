# Makes the reference project's leaf atlas: four sprays of broad, veined leaves on a stem, one per 512 px cell of a
# 1024 px PNG with alpha. Lesson 25 teaches the reader the basics of painting such an atlas in Krita; this script
# makes the more finished one the reference project ships. Values sit near 0.5, because the foliage shader reads the
# atlas as data and multiplies it by a swatch (lessons 26 and 27). Usage: make_leaf_atlas.py <output.png>
import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2
CELL = 512
MARGIN = 16
COOL = np.array([0.93, 0.98, 1.08])
WARM = np.array([1.09, 1.0, 0.88])


def leaf(length, width, bend, rng, tint, value):
    # One leaf, base at (cx, base_y) pointing up, as float RGBA at supersampled size.
    size = int(length * 1.7)
    cx, base_y = size // 2, int(size * 0.88)
    steps = 40
    phase = rng.uniform(0, 6.28)
    left, right, axis = [], [], []
    for i in range(steps + 1):
        t = i / steps
        axis_x = cx + bend * length * t * t
        axis_y = base_y - length * t
        envelope = math.sin(math.pi * t ** 0.72) ** 0.85 * (1 - 0.12 * t)
        wave = 1 + 0.045 * math.sin(t * math.pi * 6 + phase)
        half = width * envelope * wave
        axis.append((axis_x, axis_y))
        left.append((axis_x - half, axis_y))
        right.append((axis_x + half * 0.95, axis_y))
    outline = left + right[::-1]
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).polygon(outline, fill=255)
    veins = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(veins)
    draw.line(axis[2:-3], fill=255, width=max(2, int(width * 0.05)))
    for k in range(1, 5):
        t = 0.14 + k * 0.17
        ax, ay = axis[int(t * steps)]
        reach = width * (0.85 - 0.5 * t)
        for sign in (-1, 1):
            draw.line([(ax, ay), (ax + sign * reach, ay - reach * 0.75)], fill=255, width=max(1, int(width * 0.025)))
    veins = veins.filter(ImageFilter.GaussianBlur(0.8))
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    t_img = np.clip((base_y - yy) / length, 0, 1)
    axis_x_img = cx + bend * length * t_img ** 2
    side = (xx - axis_x_img) / width
    alpha = np.asarray(mask, np.float32) / 255
    inner = np.asarray(mask.filter(ImageFilter.MinFilter(int(width * 0.09) * 2 + 1)), np.float32) / 255
    rim = alpha - inner
    shade = 1.0 + 0.10 * np.clip(side, -1, 1) * -1 + 0.14 * t_img - 0.07
    shade = shade * (1 + 0.13 * np.asarray(veins, np.float32) / 255) * (1 + 0.08 * rim) * (1 - 0.06 * (1 - t_img) ** 2)
    rgb = np.clip(shade[..., None] * value * tint[None, None, :], 0, 1)
    out = np.zeros((size, size, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = alpha
    return out, cx, base_y


def rotate(image, angle, pivot):
    # Rotates a float RGBA image about a pivot, by angle radians clockwise.
    premultiplied = image.copy()
    premultiplied[..., :3] *= premultiplied[..., 3:4]
    channels = []
    for channel in range(4):
        layer = Image.fromarray(np.ascontiguousarray(premultiplied[..., channel]))
        channels.append(np.asarray(layer.rotate(-math.degrees(angle), resample=Image.BICUBIC, center=pivot), np.float32))
    result = np.stack(channels, axis=-1)
    alpha = np.clip(result[..., 3:4], 0, 1)
    result[..., :3] = np.where(alpha > 1e-4, result[..., :3] / np.maximum(alpha, 1e-4), 0)
    result[..., 3:4] = alpha
    return result


def composite(canvas, sprite, x, y, shadow=True):
    # Source-over of a float RGBA sprite whose top-left is (x, y); the sprite's own soft shadow darkens what is below.
    h, w = sprite.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.shape[1], x + w), min(canvas.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    part = sprite[y0 - y:y1 - y, x0 - x:x1 - x]
    region = canvas[y0:y1, x0:x1]
    if shadow:
        blurred = Image.fromarray((sprite[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * SS))
        offset = np.roll(np.roll(np.asarray(blurred, np.float32) / 255, 4 * SS, axis=0), 3 * SS, axis=1)[y0 - y:y1 - y, x0 - x:x1 - x]
        region[..., :3] *= (1 - 0.38 * offset * region[..., 3])[..., None]
    a = part[..., 3:4]
    region[..., :3] = part[..., :3] * a + region[..., :3] * (1 - a)
    region[..., 3:4] = a + region[..., 3:4] * (1 - a)


def spray(seed):
    rng = random.Random(seed)
    size = CELL * SS
    canvas = np.zeros((size, size, 4), np.float32)
    foot = (size / 2, size * 0.95)
    # The stem and two twigs, dark gray, first, so the leaves cover them.
    stem = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(stem)
    top = (size / 2 + rng.uniform(-12, 12) * SS, size * 0.26)
    draw.line([foot, (size / 2 + 4 * SS, size * 0.62), top], fill=255, width=5 * SS)
    for sign in (-1, 1):
        draw.line([(size / 2, size * 0.7), (size / 2 + sign * 90 * SS, size * 0.56)], fill=255, width=3 * SS)
    stem_alpha = np.asarray(stem.filter(ImageFilter.GaussianBlur(0.7 * SS)), np.float32) / 255
    canvas[..., :3] = 0.24
    canvas[..., 3] = stem_alpha
    centers = []
    for _ in range(2000):
        if len(centers) == 27:
            break
        x = size / 2 + rng.uniform(-170, 170) * SS
        y = size * rng.uniform(0.30, 0.72)
        if ((x - size / 2) / (180 * SS)) ** 2 + ((y - size * 0.5) / (120 * SS)) ** 2 > 1:
            continue
        if any(math.hypot(x - cx, y - cy) < 40 * SS for cx, cy in centers):
            continue
        centers.append((x, y))
    # Higher leaves first, so lower ones lie over them like scales.
    for x, y in sorted(centers, key=lambda center: center[1]):
        length = rng.uniform(105, 150) * SS
        width = length * rng.uniform(0.27, 0.33)
        angle = math.atan2(x - foot[0], foot[1] - y) * 1.1 + rng.uniform(-0.45, 0.45)
        warm = rng.random()
        tint = COOL + (WARM - COOL) * warm
        value = rng.uniform(0.40, 0.62)
        # Keep the whole leaf, tip and widest points, inside the cell's margin.
        reach = length * 0.5 + width
        lowest = MARGIN * SS + 6 * SS
        if not (lowest < x - reach * abs(math.sin(angle)) and x + reach * abs(math.sin(angle)) < size - lowest and lowest < y - reach * abs(math.cos(angle)) * 0.9):
            continue
        image, pivot_x, pivot_y = leaf(length, width, rng.uniform(-0.1, 0.1), rng, tint, value)
        image = rotate(image, angle, (pivot_x, pivot_y))
        dx, dy = math.sin(angle), -math.cos(angle)
        base_x, base_y = x - dx * length * 0.5, y - dy * length * 0.5
        composite(canvas, image, int(base_x - pivot_x), int(base_y - pivot_y))
    return canvas


def downscale(canvas):
    premultiplied = canvas.copy()
    premultiplied[..., :3] *= premultiplied[..., 3:4]
    small = np.stack([np.asarray(Image.fromarray(np.ascontiguousarray(premultiplied[..., c])).resize((CELL, CELL), Image.LANCZOS), np.float32) for c in range(4)], axis=-1)
    alpha = np.clip(small[..., 3:4], 0, 1)
    small[..., :3] = np.where(alpha > 1e-4, small[..., :3] / np.maximum(alpha, 1e-4), 0)
    small[..., 3:4] = alpha
    return np.clip(small, 0, 1)


def main(path):
    atlas = np.zeros((2 * CELL, 2 * CELL, 4), np.float32)
    for cell, seed in enumerate((11, 12, 13, 14)):
        atlas[(cell // 2) * CELL:(cell // 2 + 1) * CELL, (cell % 2) * CELL:(cell % 2 + 1) * CELL] = downscale(spray(seed))
    Image.fromarray((atlas * 255 + 0.5).astype(np.uint8)).save(path)
    for cell in range(4):
        part = atlas[(cell // 2) * CELL:(cell // 2 + 1) * CELL, (cell % 2) * CELL:(cell % 2 + 1) * CELL, 3] > 0.02
        ys, xs = np.where(part)
        print('cell', cell, 'bounds', xs.min(), xs.max(), ys.min(), ys.max())


if __name__ == '__main__':
    main(sys.argv[1])
