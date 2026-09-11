"""python run.py --agent scripted --subject bridge"""
import argparse
import os
from sim.world import PaintingWorld
from sim.canvas import Canvas
from agents.base import execute_strokes
from agents.scripted import ScriptedAgent
from sim.viz import Timelapse


def get_agent(name, subject):
    if name == "scripted":
        return ScriptedAgent()
    if name == "astra":
        from agents.astra_agent import AstraPaintAgent
        return AstraPaintAgent(subject=subject)
    raise ValueError(name)


def main():
    ap = argparse.ArgumentParser(description="Robot painting timelapse")
    ap.add_argument("--agent", default="scripted", choices=["scripted", "astra"])
    ap.add_argument("--subject", default="bridge")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    world, canvas = PaintingWorld(), Canvas()
    tl = Timelapse(world, canvas, every=15)
    agent = get_agent(args.agent, args.subject)

    done, rounds = False, 0
    while not done and rounds < 8:
        strokes, done = agent.plan({"canvas": canvas.pixels})
        print(f"round {rounds}: {len(strokes)} strokes (done={done})")
        execute_strokes(world, canvas, strokes, on_step=tl.on_step)
        rounds += 1

    tl.save(f"{args.out}/{args.subject}.mp4")
    canvas.save(f"{args.out}/{args.subject}.png")


if __name__ == "__main__":
    main()
