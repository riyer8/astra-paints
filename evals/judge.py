"""judge.py - blind recognition judge for a painting run.

The honest eval metric: not "does it look nice to me" but
"does it read as the subject to a stranger who wasn't told?"

Usage:
    python judge.py results/bridge_astra_20260911_160847 --expect bridge
"""
import argparse
import base64
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="Blind painting judge")
    ap.add_argument("run_dir", help="run folder containing final.png")
    ap.add_argument("--expect", required=True,
                    help="keyword the verdict should contain, e.g. 'bull'")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    img_path = os.path.join(args.run_dir, "final.png")
    if not os.path.exists(img_path):
        sys.exit(f"no final.png in {args.run_dir}")

    model = args.model or os.environ.get("ASTRA_MODEL", "gpt-6-astra")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Set OPENAI_API_KEY")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": [
            {"type": "text", "text":
             "What single object, animal, or scene does this painting depict? "
             "Reply with one to three words only, no explanation."},
            {"type": "image_url", "image_url": {
                "url": "data:image/png;base64," + b64}},
        ]}],
        max_completion_tokens=500,
    )
    verdict = resp.choices[0].message.content.strip().lower()
    score = 1 if args.expect.lower() in verdict else 0

    u = resp.usage
    cost = (u.prompt_tokens * 10.0 + u.completion_tokens * 50.0) / 1e6  # astra prices

    result = {
        "run_dir": args.run_dir,
        "expected": args.expect,
        "verdict": verdict,
        "score": score,
        "prompt_tokens": u.prompt_tokens,
        "completion_tokens": u.completion_tokens,
        "cost_dollars": round(cost, 6),
        "model": model,
    }
    out = os.path.join(args.run_dir, "judge.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)

    print(f"verdict: '{verdict}' (expected '{args.expect}') -> "
          f"{'PASS' if score else 'FAIL'}")
    print(f"cost ${cost:.4f}, saved to {out}")


if __name__ == "__main__":
    main()
