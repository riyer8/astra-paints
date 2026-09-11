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
import re
import imageio

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
        self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost_dollars": 0.0}

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
        resp = client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": [
                {"type": "text", "text": self._prompt()},
                {"type": "image_url", "image_url": {
                    "url": "data:image/png;base64," + self._canvas_png(observation["canvas"])}},
            ]}],
            max_completion_tokens=2000,
        )
        self.calls += 1
        u = resp.usage
        PRICE_IN, PRICE_OUT = 10.0, 50.0 #astra prices :O
        call_cost = (u.prompt_tokens * PRICE_IN + u.completion_tokens * PRICE_OUT) / 1e6
        self.last_usage = {
            "prompt_tokens": u.prompt_tokens,
            "completion_tokens": u.completion_tokens,
            "cost_dollars": round(call_cost, 6),
        }
        self.spent += call_cost
        print(f"call {self.calls}: {u.prompt_tokens}+{u.completion_tokens} tokens, "
            f"${call_cost:.4f} (total ${self.spent:.4f})")


        text = resp.choices[0].message.content
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
        if m:
            text = m.group(1)
        else:
            text = text[text.find("{"):text.rfind("}") + 1]
        data = json.loads(text)

        strokes = [{"color": tuple(s["color"]),
                    "points": [tuple(p) for p in s["points"]]}
                   for s in data["strokes"]]
        return strokes, bool(data.get("done", False))
