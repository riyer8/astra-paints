"""plots.py - coverage / cost curves from run.json.
Usage: python plots.py results/<run_dir>
"""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

run_dir = sys.argv[1]
with open(os.path.join(run_dir, "run.json")) as f:
    run = json.load(f)
rounds = run["rounds"]
xs = [r["round"] for r in rounds]
cov = [r["coverage"] for r in rounds]
marginal = [c - (cov[i - 1] if i else 0) for i, c in enumerate(cov)]

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4))
a.plot(xs, cov, marker="o", label="total coverage")
a.plot(xs, marginal, marker="x", label="new paint this round")
a.set_title("coverage per round"); a.set_xlabel("round")
a.legend(); a.grid(True)
b.bar(xs, [r["cost_dollars"] for r in rounds])
b.set_title("cost per round"); b.set_xlabel("round"); b.set_ylabel("$")
b.grid(True)
fig.tight_layout()
out = os.path.join(run_dir, "curves.png")
fig.savefig(out, dpi=100)
print("saved", out)
