import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sim.world import PaintingWorld

w = PaintingWorld()

# 1. raw servo: order the shoulder to 0.5 rad, check it obeyed
w.set_targets(0.5, 0.0, 0.1)
w.step(1000)
print("shoulder:", round(w.joint_angles()[0], 3), "(target 0.5)")

# 2. IK round-trip: ask for the brush at (0.4, 0.1), read where it really is
w.reset()
tip = w.move_brush(0.4, 0.1)
print("asked (0.4, 0.1) -> tip at", tuple(round(v, 3) for v in tip[:2]))
