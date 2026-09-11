"""compare.py - side-by-side finals with judge scores.
Usage: python compare.py results/<run1> results/<run2>
"""
import json, os, sys
from PIL import Image, ImageDraw

def load(run_dir):
    im = Image.open(os.path.join(run_dir, "final.png")).convert("RGB")
    im.thumbnail((480, 480))
    try:
        j = json.load(open(os.path.join(run_dir, "judge.json")))
        cap = f"{os.path.basename(run_dir)} | judge: '{j['verdict']}' {'PASS' if j['score'] else 'FAIL'}"
    except FileNotFoundError:
        cap = os.path.basename(run_dir)
    return im, cap

ims, caps = zip(*[load(d) for d in sys.argv[1:3]])
label_h, (w, h) = 30, ims[0].size
sheet = Image.new("RGB", (w * len(ims), h + label_h), "white")
d = ImageDraw.Draw(sheet)
for i, (im, cap) in enumerate(zip(ims, caps)):
    sheet.paste(im, (i * w, label_h))
    d.text((i * w + 8, 8), cap, fill="black")
sheet.save("compare.png")
print("saved compare.png")
