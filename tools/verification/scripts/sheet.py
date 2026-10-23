import os, sys
from PIL import Image, ImageDraw
out, cols, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
width = 640
tiles = []
for p in paths:
    im = Image.open(p).convert('RGB')
    im = im.resize((width, int(im.height * width / im.width)))
    ImageDraw.Draw(im).text((6, 4), os.path.basename(p), fill=(255, 255, 0))
    tiles.append(im)
rows = (len(tiles) + cols - 1) // cols
h = tiles[0].height
sheet = Image.new('RGB', (cols * width, rows * h))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * width, (i // cols) * h))
sheet.save(out)
