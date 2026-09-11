"""Timelapse: capture frames while painting, stitch into an mp4."""
import matplotlib
matplotlib.use("Agg")  # headless: no window pops up
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import imageio
import math


class Timelapse:
    def __init__(self, world, canvas, every=10):
        self.world = world
        self.canvas = canvas
        self.every = every
        self.frames = []
        self._count = 0
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))

    def on_step(self):
        self._count += 1
        if self._count % self.every == 0:
            self.frames.append(self._render())

    def _render(self):
        self.ax1.clear(); self.ax2.clear()
        self.ax1.imshow(self.canvas.pixels)
        self.ax1.axis("off")
        self.ax1.set_title("canvas")
        # top-down arm doodle
        s, e = self.world.joint_angles()[:2]
        L1, L2 = self.world.L1, self.world.L2
        x1, y1 = L1*math.cos(s), L1*math.sin(s)
        x2, y2 = x1 + L2*math.cos(s+e), y1 + L2*math.sin(s+e)
        x0, x1r = self.canvas.x_range; y0, y1r = self.canvas.y_range
        self.ax2.add_patch(Rectangle((x0, y0), x1r-x0, y1r-y0,
                                     fill=False, linestyle="--", alpha=0.5))
        self.ax2.plot([0, x1], [0, y1], "o-", lw=8, color="darkorange")
        self.ax2.plot([x1, x2], [y1, y2], "o-", lw=6, color="darkorange")
        self.ax2.plot(x2, y2, "ko", ms=10)
        self.ax2.set_xlim(-0.15, 0.65); self.ax2.set_ylim(-0.4, 0.4)
        self.ax2.set_aspect("equal"); self.ax2.axis("off")
        self.ax2.set_title("arm (top view)")
        self.fig.canvas.draw()
        buf = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
        return buf.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))

    def save(self, path, fps=30):
        imageio.mimsave(path, self.frames, fps=fps)
        print(f"saved {path} ({len(self.frames)} frames)")
