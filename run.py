"""python run.py --agent scripted --subject bridge"""
import argparse
import json
import os
import time
from sim.world import PaintingWorld
from sim.canvas import Canvas
from agents.base import execute_strokes
from agents.scripted_agent import ScriptedAgent
from sim.viz import Timelapse
import datetime


def get_agent(name, subject):
    if name == "scripted":
        return ScriptedAgent()
    if name == "astra":
        from agents.astra_agent import AstraPaintAgent
        return AstraPaintAgent(subject=subject,
                       model=os.environ.get("ASTRA_MODEL", "gpt-6-astra"))
    # should create an agent file in agents/
    raise ValueError(name)


def coverage(canvas):
    # fraction of pixels touched (assumes white background)
    return float((canvas.pixels != 255).any(axis=-1).mean())


def main():
    ap = argparse.ArgumentParser(description="Robot painting timelapse")
    ap.add_argument("--agent", default="scripted", choices=["scripted", "astra"])
    ap.add_argument("--subject", default="bridge")
    ap.add_argument("--out", default="results")
    ap.add_argument("--rounds", type=int, default=8)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    world, canvas = PaintingWorld(), Canvas()
    tl = Timelapse(world, canvas, every=15)
    agent = get_agent(args.agent, args.subject)

    subject_slug = args.subject.replace(" ", "_")
    run_dir = os.path.join(args.out, subject_slug,
        f"{subject_slug}-{args.agent}-{datetime.datetime.now():%Y%m%d_%H%M%S}")
    os.makedirs(run_dir, exist_ok=True)
    print("saving to", run_dir)


    summary = {
        "subject": args.subject,
        "agent": args.agent,
        "model": getattr(agent, "model", None),
        "started_at": datetime.datetime.now().isoformat(),
        "rounds": [],
    }

    done, rounds = False, 0
    while not done and rounds < args.rounds:
        t0 = time.time()
        strokes, done = agent.plan({"canvas": canvas.pixels})
        plan_s = time.time() - t0
        usage = getattr(agent, "last_usage",
                        {"prompt_tokens": 0, "completion_tokens": 0, "cost_dollars": 0.0})
        print(f"round {rounds}: {len(strokes)} strokes (done={done})")
        execute_strokes(world, canvas, strokes, on_step=tl.on_step)
        plan_data = {"strokes": [{"color": list(s["color"]),
                                "points": [list(p) for p in s["points"]]}
                                for s in strokes],
                    "done": bool(done)}
        with open(os.path.join(run_dir, f"plan_{rounds:02d}.json"), "w") as f:
            json.dump(plan_data, f)

        exec_s = time.time() - t0 - plan_s
        canvas.save(os.path.join(run_dir, f"round_{rounds:02d}.png"))
        summary["rounds"].append({
            "round": rounds,
            "strokes": len(strokes),
            "done": bool(done),
            "plan_seconds": round(plan_s, 2),
            "exec_seconds": round(exec_s, 2),
            "coverage": round(coverage(canvas), 4),
            **usage,
        })
        rounds += 1

    tl.save(os.path.join(run_dir, "timelapse.mp4"))
    canvas.save(os.path.join(run_dir, "final.png"))

    summary["finished_at"] = datetime.datetime.now().isoformat()
    summary["total_strokes"] = sum(r["strokes"] for r in summary["rounds"])
    summary["total_prompt_tokens"] = sum(r["prompt_tokens"] for r in summary["rounds"])
    summary["total_completion_tokens"] = sum(r["completion_tokens"] for r in summary["rounds"])
    summary["total_cost_dollars"] = round(sum(r["cost_dollars"] for r in summary["rounds"]), 4)
    summary["total_plan_seconds"] = round(sum(r["plan_seconds"] for r in summary["rounds"]), 1)
    summary["total_exec_seconds"] = round(sum(r["exec_seconds"] for r in summary["rounds"]), 1)
    summary["final_coverage"] = summary["rounds"][-1]["coverage"] if summary["rounds"] else 0.0
    with open(os.path.join(run_dir, "run.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("saved to", run_dir)
    print(f"total: {summary['total_strokes']} strokes, "
          f"${summary['total_cost_dollars']:.4f}, "
          f"{summary['total_plan_seconds'] + summary['total_exec_seconds']:.1f}s")


if __name__ == "__main__":
    main()