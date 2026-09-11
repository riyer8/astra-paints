"""AstraPaintAgent: the AI painter. STUB - needs OPENAI_API_KEY to run.

Same contract as ScriptedAgent: plan() -> (strokes, done).
One API call per plan() - not per brush movement - so a painting costs
a handful of calls, not thousands. That's what keeps it inside your
50-requests-a-day tier.
"""
import base64
import io
import json
import os

import imageio
import numpy as np

from .base import Agent


class OverBudget(Exception):
    pass


class AstraPaintAgent(Agent):
    def __init__(self, subject, budget_dollars=2.0, model="gpt-6-astra"):
        self.subject = subject
        self.budget = budget_dollars
        self.model = model
        self.spent = 0.0
        self.calls = 0
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def _canvas_png(self, pixels):
        buf = io.BytesIO()
        imageio.imwrite(buf, pixels, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def _prompt(self):
        return (
            f"You are a robot arm painting '{self.subject}' on a canvas.\n"
            "Canvas coordinates in meters: x in [0.0, 0.5] (left to right), "
            "y in [-0.25, 0.25] (bottom to top).\n"
            "The attached image is the current canvas. Plan the NEXT strokes only.\n"
            'Reply with JSON only: {"strokes": [{"color": [r, g, b], '
            '"points": [[x, y], ...]}], "done": false}.\n'
            "Rules: points inside canvas bounds; short deliberate strokes; "
            "3-8 strokes per reply; done=true when the painting is finished."
        )

    def plan(self, observation):
        if self.spent >= self.budget:
            raise OverBudget(f"spent ${self.spent:.2f} >= ${self.budget:.2f}")
        if not self.api_key:
            raise RuntimeError("Set OPENAI_API_KEY to use the Astra painter.")
        from openai import OpenAI  # lazy: scripted runs need no API package
        client = OpenAI(api_key=self.api_key)
        # NOTE: exact model name/params are placeholders - adapt to the live API.
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": self._prompt()},
                {"type": "image_url", "image_url": {
                    "url": "data:image/png;base64," + self._canvas_png(observation["canvas"])}},
            ]}],
            max_tokens=2000,
        )
        self.calls += 1
        # TODO: real cost from resp.usage once model pricing is known
        data = json.loads(resp.choices[0].message.content)
        strokes = [{"color": tuple(s["color"]),
                    "points": [tuple(p) for p in s["points"]]}
                   for s in data["strokes"]]
        return strokes, bool(data.get("done", False))
