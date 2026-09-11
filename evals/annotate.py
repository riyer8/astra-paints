"""annotate.py - captioned progression video from round PNGs + run.json.
Usage: python annotate.py results/<run_dir>
"""
import glob, json, os, sys
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw

run_dir = sys.argv[1]
run = json.load(open(os.path.join(run_dir, "run.json")))
by_round = {r["round"]: r for r in run["rounds"]}
paths = sorted(glob.glob(os.path.join(run_dir, "round_*.png")))

out = os.path.join(run_dir, "progression.mp4")
writer = imageio.get_writer(out, fps=1)
for i, p in enumerate(paths):
    im = Image.open(p).convert("RGB")
    r = by_round.get(i, {})
    bar = Image.new("RGB", (im.width, 36), "black")
    ImageDraw.Draw(bar).text(
        (10, 10),
        f"round {i} | {r.get('strokes', '?')} strokes | "
        f"${r.get('cost_dollars', 0):.4f} | coverage {r.get('coverage', 0):.0%}",
        fill="white")
    frame = Image.new("RGB", (im.width, im.height + 36), "black")
    frame.paste(im, (0, 0))
    frame.paste(bar, (0, im.height))
    writer.append_data(np.asarray(frame))
writer.close()
print("saved", out)
