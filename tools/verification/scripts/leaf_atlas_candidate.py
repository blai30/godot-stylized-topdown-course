# Candidate 3, after research: simple clump shapes (bunches, not single leaves), a few soft flat values, holes for sky,
# and the Ghibli look carried by form shading (a canopy sphere's normals through a color ramp), previewed here.
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

SS = 3
CELL = 512
S = CELL * SS

def leaf_poly(cx, cy, length, width, angle):
    pts = []
    n = 20
    for i in range(n + 1):
        t = i / n
        w = width * math.sin(math.pi * t ** 0.8)
        pts.append((w, -length * t))
    pts = pts + [(-x, y) for x, y in reversed(pts[1:-1])]
    c, s = math.cos(angle), math.sin(angle)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]

def shift(m, dx, dy):
    return ImageChops.offset(m, int(dx), int(dy))

def leaf_layer(length, width, angle, bend, value, rng, tint=(1, 1, 1)):
    # A pointed leaf with a bent midrib, darker at the base, lighter at the tip and one side, a faint midrib.
    size = int(length * 2.0)
    ox, oy = size / 2, size * 0.85
    n = 26
    left, right, axis = [], [], []
    for i in range(n + 1):
        t = i / n
        cx = ox + bend * length * t * t
        cy = oy - length * t
        w = width * math.sin(math.pi * t ** 0.62) ** 0.9 * (1 - 0.45 * t ** 1.5)
        axis.append((cx, cy, t, w))
    poly = [(cx - w, cy) for cx, cy, t, w in axis] + [(cx + w * 0.9, cy) for cx, cy, t, w in reversed(axis)]
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    yy, xx = np.mgrid[0:size, 0:size]
    t = np.clip((oy - yy) / length, 0, 1)
    axis_x = ox + bend * length * t * t
    side = (xx - axis_x) / max(width, 1)
    shade = 0.66 + 0.34 * np.clip(t * 1.2, 0, 1) - 0.07 * np.clip(side, -1, 1)
    m_arr = np.array(mask, np.float32) / 255
    soft = np.zeros_like(m_arr)
    for k, wgt in ((0.06, 0.5), (0.13, 0.5)):
        inner = mask.filter(ImageFilter.MinFilter(max(3, int(width * k * 2) | 1)))
        soft += wgt * (m_arr - np.array(inner, np.float32) / 255)
    shade = shade * (1 + 0.30 * soft)
    midrib = (np.abs(xx - axis_x) < max(2.0, width * 0.06)) & (t > 0.06) & (t < 0.92)
    shade = shade * np.where(midrib, 1.22, 1.0)
    v = np.clip(shade * value, 0, 1)
    arr = np.zeros((size, size, 4), np.float32)
    arr[..., 0] = v * tint[0] * 255; arr[..., 1] = v * tint[1] * 255; arr[..., 2] = v * tint[2] * 255
    arr[..., 3] = np.array(mask, np.float32)
    img = Image.fromarray(arr.astype(np.uint8)).rotate(-math.degrees(angle), resample=Image.BICUBIC, center=(ox, oy))
    return img, ox, oy

def cluster(seed):
    rng = random.Random(seed)
    layer = np.zeros((S, S, 4), np.float32)
    focus = (S / 2, S * 1.15)
    pts = []
    for i in range(26):
        while True:
            px, py = rng.uniform(-1, 1), rng.uniform(-1, 0.3)
            if px * px + py * py <= 1:
                break
        x, y = S / 2 + px * S * 0.31, S * 0.80 + py * S * 0.30
        pts.append((y, math.hypot(px, py), x, y))
    pts.sort()
    for _, depth, x, y in pts:
        a = math.atan2(x - focus[0], focus[1] - y) + rng.uniform(-0.7, 0.7)
        length = rng.uniform(0.2, 0.28) * S
        warm = rng.random()
        tint = (1.0 + 0.10 * warm - 0.06 * (1 - warm), 1.0, 1.0 - 0.14 * warm + 0.08 * (1 - warm))
        value = (0.40 + 0.28 * rng.random()) * (0.72 + 0.28 * (1 - depth))
        img, ox, oy = leaf_layer(length, length * rng.uniform(0.24, 0.30), a, rng.uniform(-0.14, 0.14), value, rng, tint)
        x0, y0 = int(x - ox), int(y - oy)
        sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(S, x0 + img.width), min(S, y0 + img.height)
        if sx1 <= sx0 or sy1 <= sy0:
            continue
        t = np.array(img, np.float32)[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] / 255
        region = layer[sy0:sy1, sx0:sx1]
        al = t[..., 3:4]
        halo = np.array(Image.fromarray((al[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17)), np.float32)[..., None] / 255
        region[..., :3] *= 1 - 0.16 * (halo - al).clip(0, 1) * (region[..., 3:4] > 0.5)
        region[..., :3] = t[..., :3] * 255 * al + region[..., :3] * (1 - al)
        region[..., 3:4] = al + region[..., 3:4] * (1 - al)
    layer[..., 3] *= 255
    return Image.fromarray(np.clip(layer, 0, 255).astype(np.uint8)).resize((CELL, CELL), Image.LANCZOS)

clusters = [cluster(s) for s in (31, 32, 33, 34)]
atlas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
for i, c in enumerate(clusters):
    atlas.alpha_composite(c, ((i % 2) * CELL, (i // 2) * CELL))
atlas.save('atlas_s.png')
atlas.save('atlas_v6.png')

# Preview: the atlas through the canopy ramp, on a plain meadow color.
SH = np.array([56, 122, 106]); MI = np.array([98, 172, 78]); LI = np.array([184, 216, 108])
light = np.array([-0.55, -0.6, 0.58]); light /= np.linalg.norm(light)
def ramp(t):
    t = np.clip(t, 0, 1)
    if t < 0.5:
        return SH + (MI - SH) * (t / 0.5)
    return MI + (LI - MI) * ((t - 0.5) / 0.5)

def canopy(path, ncards=70, W=900, H=700, seed=5, bgcolor=(150, 196, 110)):
    rng = random.Random(seed)
    canvas = Image.new('RGBA', (W, H), bgcolor + (255,))
    cx, cy, R = W / 2, H * 0.47, 255
    cards = []
    for i in range(ncards):
        # points on a flattened sphere, upper-biased
        u = rng.uniform(0, 2 * math.pi); v = math.acos(rng.uniform(-0.55, 1.0))
        r0 = rng.random() ** 0.35
        nx, ny, nz = math.sin(v) * math.cos(u) * r0, -math.cos(v) * r0, math.sin(v) * math.sin(u) * r0   # y up in screen
        x, y = cx + nx * R * 1.15, cy + ny * R * 0.95
        cards.append((nz, x, y, (nx, ny * 0.9, nz * 0.9 + 0.2)))
    cards.sort(key=lambda c: c[0])
    for _, x, y, n in cards:
        nn = np.array(n) / np.linalg.norm(n)
        ndl = float(np.dot(nn, np.array([-0.5, 0.65, 0.58])))
        t = 0.5 + 0.5 * ndl                               # wrapped
        t = t ** 0.9
        col = ramp(t)
        k = rng.randrange(4)
        base = np.array(clusters[k], np.float32) / 255
        arr = np.zeros(base.shape, np.float32)
        arr[..., :3] = np.clip(base[..., :3] * col * 1.18, 0, 255)
        arr[..., 3] = base[..., 3] * 255
        card = Image.fromarray(arr.astype(np.uint8))
        sc = rng.uniform(0.7, 0.9)
        card = card.resize((int(512 * sc), int(512 * sc)), Image.LANCZOS)
        card = card.rotate(math.degrees(math.atan2(n[0], n[1]) * 0.6) + rng.uniform(-14, 14), resample=Image.BICUBIC, expand=True)
        canvas.alpha_composite(card, (int(x - card.width / 2), int(y - card.height * 0.55)))
    canvas.convert('RGB').save(path)

canopy('canopy_s.png', ncards=120)
bg = Image.new('RGBA', (1024, 1024), (150, 196, 110, 255))
tinted = np.array(atlas, np.float32) / 255
tinted[..., :3] = np.clip(tinted[..., :3] * MI * 1.18, 0, 255) / 255
t = Image.fromarray((tinted * 255).astype(np.uint8))
bg.alpha_composite(t); bg.convert('RGB').save('atlas_s_view.png')
