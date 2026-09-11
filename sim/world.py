"""The world: holds the sim, steps physics, translates brush <-> joints."""
import math
import mujoco  # pyright: ignore[reportMissingImports]
import numpy as np


class PaintingWorld:
    L1 = 0.30  # must match arm.xml: link2's pos along link1
    L2 = 0.26  # must match arm.xml: brush_mount's pos along link2

    def __init__(self, xml_path="sim/arm.xml"):
        self.model = mujoco.MjModel.from_xml_path(xml_path)
        self.data = mujoco.MjData(self.model)
        self._tip_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_SITE, "brush_tip")
        self.reset()

    def reset(self):
        mujoco.mj_resetData(self.model, self.data)
        self.data.ctrl[:] = (0.0, 0.0, 0.1)  # park: joints at 0, brush up
        mujoco.mj_forward(self.model, self.data)

    # ---- speak joint angles ----
    def set_targets(self, shoulder, elbow, lift):
        self.data.ctrl[:] = (shoulder, elbow, lift)

    def step(self, n=1):
        for _ in range(n):
            mujoco.mj_step(self.model, self.data)

    def joint_angles(self):
        return tuple(self.data.qpos[:3])

    def brush_tip(self):
        # forward kinematics, free from MuJoCo: where is the bristle tip?
        return tuple(self.data.site_xpos[self._tip_id])

    # ---- speak brush positions ----
    def ik(self, x, y):
        """(x, y) -> (shoulder, elbow). Two sticks, one triangle."""
        d = math.hypot(x, y)
        d = min(max(d, abs(self.L1 - self.L2) + 1e-6), self.L1 + self.L2 - 1e-6)
        cos_elbow = (d*d - self.L1**2 - self.L2**2) / (2*self.L1*self.L2)
        elbow = -math.acos(max(-1.0, min(1.0, cos_elbow)))
        shoulder = math.atan2(y, x) - math.atan2(
            self.L2*math.sin(elbow), self.L1 + self.L2*math.cos(elbow))
        return shoulder, elbow

    def move_brush(self, x, y, lift=0.1, settle_steps=500):
        shoulder, elbow = self.ik(x, y)
        self.set_targets(shoulder, elbow, lift)
        self.step(settle_steps)
        return self.brush_tip()
