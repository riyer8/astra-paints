"""ScriptedAgent: hardcoded strokes. Proves the pipeline before any AI."""
import numpy as np
from .base import Agent

ORANGE = (200, 70, 40)


def _line(a, b, n=20):
    return [(a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)
            for t in np.linspace(0, 1, n)]


class ScriptedAgent(Agent):
    def plan(self, observation):
        strokes = []
        C = ORANGE
        # deck
        strokes.append({"color": C, "points": _line((0.08, -0.06), (0.42, -0.06))})
        # towers
        strokes.append({"color": C, "points": _line((0.17, -0.06), (0.17, 0.16))})
        strokes.append({"color": C, "points": _line((0.33, -0.06), (0.33, 0.16))})
        # main cable: side spans straight, middle span a parabola dipping to y=0
        cable = _line((0.08, 0.0), (0.17, 0.16), n=10)
        cable += [(0.17 + 0.16*t, 0.16*(1 - 4*t*(1-t)))
                  for t in np.linspace(0, 1, 40)[1:]]
        cable += _line((0.33, 0.16), (0.42, 0.0), n=10)[1:]
        strokes.append({"color": C, "points": cable})
        # suspenders: short verticals from cable down to deck
        for fx in (0.20, 0.23, 0.27, 0.30):
            t = (fx - 0.17) / 0.16
            cable_y = 0.16 * (1 - 4*t*(1-t))
            strokes.append({"color": C, "points": _line((fx, cable_y), (fx, -0.06), n=8)})
        return strokes, True
