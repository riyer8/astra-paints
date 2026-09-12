import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sim.world import PaintingWorld
from sim.canvas import Canvas
from agents.base import execute_strokes
from agents.scripted_agent import ScriptedAgent
from sim.viz import Timelapse

os.makedirs("results", exist_ok=True)
w, c = PaintingWorld(), Canvas()
tl = Timelapse(w, c, every=15)
strokes, _ = ScriptedAgent().plan({"canvas": c.pixels})
execute_strokes(w, c, strokes, on_step=tl.on_step)
tl.save("results/bridge.mp4")
c.save("results/bridge.png")
