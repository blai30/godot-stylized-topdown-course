# Reference art for lesson 13: a seamless painterly grass texture, 512 px for 2 m. Labeled as the agent's reference,
# standing in for what the reader paints in Krita.
import sys
import numpy as np
from PIL import Image, ImageDraw

size = 512
rng = np.random.default_rng(13)

def periodic_noise(scale):
    # White noise low-passed in frequency space tiles seamlessly by construction.
    spectrum = np.fft.fft2(rng.standard_normal((size, size)))
    fx = np.fft.fftfreq(size)[None, :]
    fy = np.fft.fftfreq(size)[:, None]
    noise = np.real(np.fft.ifft2(spectrum * np.exp(-(fx * fx + fy * fy) * scale)))
    return (noise - noise.min()) / (noise.max() - noise.min())

def hex_color(value):
    return np.array([int(value[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)

base, variation, light, shade = (hex_color(c) for c in ('#699041', '#7ea44e', '#94c257', '#4f7a3c'))
large, medium = periodic_noise(4000), periodic_noise(400)
blend = np.clip((large - 0.35) * 2.0, 0, 1)[..., None]
color = base * (1 - blend) + variation * blend
color *= (0.92 + 0.16 * medium)[..., None]
image = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8))

# Short tapered strokes, drawn three times over so strokes crossing an edge continue on the other side.
draw = ImageDraw.Draw(image, 'RGBA')
for i in range(2600):
    x, y = rng.uniform(0, size, 2)
    angle = rng.uniform(-0.6, 0.6) - np.pi / 2
    length = rng.uniform(5, 13)
    tone = light if rng.random() < 0.55 else shade
    alpha = int(rng.uniform(70, 150))
    tip = (x + np.cos(angle) * length, y + np.sin(angle) * length)
    for dx in (-size, 0, size):
        for dy in (-size, 0, size):
            draw.line([(x + dx, y + dy), (tip[0] + dx, tip[1] + dy)], fill=(*tone.astype(int), alpha), width=2)
image.save(sys.argv[1])

# Seam check: the wrapped edge differs no more than neighboring pixels inside the image do.
pixels = np.asarray(image, dtype=float)
edge = np.abs(pixels[:, 0] - pixels[:, -1]).mean()
inner = np.abs(pixels[:, 1:] - pixels[:, :-1]).mean()
print(f'wrap seam {edge:.1f} vs inner {inner:.1f}')
