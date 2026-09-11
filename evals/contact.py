"""contact.py - one-glance progression sheet for a run dir.
Usage: python contact.py results/bridge_astra_20260911_160847
"""
import glob, os, sys
from PIL import Image, ImageDraw

run_dir = sys.argv[1]
paths = sorted(glob.glob(os.path.join(run_dir, "round_*.png")))
thumbs = []
for p in paths:
    im = Image.open(p).convert("RGB")
    im.thumbnail((320, 320))
    thumbs.append(im)

label_h, (w, h) = 24, thumbs[0].size
sheet = Image.new("RGB", (w * len(thumbs), h + label_h), "white")
d = ImageDraw.Draw(sheet)
for i, t in enumerate(thumbs):
    sheet.paste(t, (i * w, label_h))
    d.text((i * w + 8, 6), f"round {i}", fill="black")
out = os.path.join(run_dir, "contact.png")
sheet.save(out)
print("saved", out)
