"""Agent contract: plan() turns an observation into strokes. Any agent fits."""
import math
import numpy as np


class Agent:
    def plan(self, observation):
        """Return (strokes, done). A stroke = {"color": (r,g,b), "points": [(x,y), ...]}."""
        raise NotImplementedError


def execute_strokes(world, canvas, strokes, on_step=None):
    """Hands: move the brush through strokes, stamping as it goes."""
    for stroke in strokes:
        color, pts = stroke["color"], stroke["points"]
        # travel to the start with brush UP (no paint)
        s, e = world.ik(*pts[0])
        world.set_targets(s, e, 0.1)
        world.step(200)
        # walk the polyline with brush DOWN, stamping densely (~every 2mm)
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            n = max(2, int(math.hypot(xb - xa, yb - ya) / 0.002))
            for t in np.linspace(0, 1, n):
                x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
                s, e = world.ik(x, y)
                world.set_targets(s, e, 0.0)
                world.step(4)
                tip = world.brush_tip()
                canvas.stamp(tip[0], tip[1], color)
                if on_step:
                    on_step()
        world.set_targets(s, e, 0.1)  # lift at the end
        world.step(100)
