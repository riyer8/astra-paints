import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agents.astra_agent import AstraPaintAgent

agent = AstraPaintAgent(
    subject="golden gate bridge",
    budget_dollars=0.50,
    model="gpt-6-astra",
)
blank = np.full((256, 256, 3), 255, dtype=np.uint8)
strokes, done = agent.plan({"canvas": blank})
print(f"{len(strokes)} strokes, done={done}, calls={agent.calls}")
for s in strokes[:3]:
    print("color", s["color"], "-", len(s["points"]), "points, first:", s["points"][0])
