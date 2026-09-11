import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from sim.world import PaintingWorld
from sim.canvas import Canvas

RED = (220, 40, 40)

def draw_polyline(world, canvas, points, color, steps_per_seg=150):
    """Walk the brush along points, brush down, stamping continuously."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for t in np.linspace(0, 1, steps_per_seg):
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            shoulder, elbow = world.ik(x, y)
            world.set_targets(shoulder, elbow, 0.0)  # lift 0 = brush DOWN
            world.step(5)
            tip = world.brush_tip()
            canvas.stamp(tip[0], tip[1], color)

os.makedirs("results", exist_ok=True)
w = PaintingWorld()
c = Canvas()
square = [(0.15, -0.1), (0.35, -0.1), (0.35, 0.1), (0.15, 0.1), (0.15, -0.1)]
draw_polyline(w, c, square, RED)
c.save("results/square.png")
print("saved results/square.png")
