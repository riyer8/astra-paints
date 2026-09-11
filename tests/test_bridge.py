import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sim.world import PaintingWorld
from sim.canvas import Canvas
from agents.base import execute_strokes
from agents.scripted import ScriptedAgent

os.makedirs("results", exist_ok=True)
w, c = PaintingWorld(), Canvas()
strokes, done = ScriptedAgent().plan({"canvas": c.pixels})
print(f"{len(strokes)} strokes planned")
execute_strokes(w, c, strokes)
c.save("results/bridge.png")
print("saved results/bridge.png")
