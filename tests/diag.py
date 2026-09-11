import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mujoco
from sim.world import PaintingWorld

w = PaintingWorld()

# 1. verify ctrl[0] really drives the shoulder (actuator wiring)
for i in range(w.model.nu):
    aname = mujoco.mj_id2name(w.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    jid = w.model.actuator_trnid[i, 0]
    jname = mujoco.mj_id2name(w.model, mujoco.mjtObj.mjOBJ_JOINT, jid)
    print(f"ctrl[{i}] ({aname}) -> joint {jname}")

# 2. watch the shoulder over time: converging, oscillating, or stuck?
w.set_targets(0.5, 0.0, 0.1)
for i in range(10):
    w.step(100)
    print(i, [round(a, 3) for a in w.joint_angles()])
