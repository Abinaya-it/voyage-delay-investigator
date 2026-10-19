
import os, json
from kg import build_graph
from tools import Toolbox, SCHEMAS
from reasoning import analyse
from report import render

SYSTEM = ("You are a maritime operations investigator. You MUST call tools to retrieve evidence "
 "before answering: voyage details, then destination port congestion, then voyage incidents. "
 "Never state a fact not returned by a tool. Cite evidence IDs like [E1]. Separate CONFIRMED causes "
 "(incident status 'Confirmed') from POSSIBLE contributing factors, state any unexplained delay hours, "
 "and finish with concrete next checks.")

def run_offline(question, tb, trace):
    name = None
    for n, a in tb.g.nodes(data=True):
        if a["label"] == "Vessel" and a["name"].lower().replace("mv ", "") in question.lower(): name = a["name"]
    if not name:
        trace("PLAN", "no known vessel named in question"); return None
    trace("PLAN", "1) voyage -> 2) destination port congestion -> 3) incidents -> 4) classify -> 5) report")
    e1 = tb.get_voyage_details(name); trace("TOOL", f"get_voyage_details -> {e1.id}: {e1.graph_path}")
    if "error" in e1.data: return None
    e2 = tb.get_port_congestion(e1.data["destination_id"]); trace("TOOL", f"get_port_congestion -> {e2.id}: {e2.graph_path}")
    e3 = tb.get_voyage_incidents(e1.data["id"]); trace("TOOL", f"get_voyage_incidents -> {e3.id}: {len(e3.data['incidents'])} incident(s)")
    return render(analyse(tb.ledger))

def run_llm(question, tb, trace):
    import anthropic
    c, model = anthropic.Anthropic(), os.getenv("MODEL", "claude-sonnet-5-5")
    msgs = [{"role": "user", "content": question}]
    for _ in range(8):
        r = c.messages.create(model=model, max_tokens=1500, system=SYSTEM, tools=SCHEMAS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})
        calls = [b for b in r.content if b.type == "tool_use"]
        if not calls:
            if not tb.ledger: raise RuntimeError("Guardrail: model answered without retrieving evidence")
            return "".join(b.text for b in r.content if b.type == "text")
        out = []
        for b in calls:
            e = getattr(tb, b.name)(**b.input); trace("TOOL", f"{b.name}({b.input}) -> {e.id}")
            out.append({"type": "tool_result", "tool_use_id": b.id, "content": f"[{e.id}] {json.dumps(e.data)}"})
        msgs.append({"role": "user", "content": out})

def investigate(question, trace=lambda *a: None):
    tb = Toolbox(build_graph())
    use_llm = bool(os.getenv("ANTHROPIC_API_KEY")) and not os.getenv("OFFLINE")
    ans = (run_llm if use_llm else run_offline)(question, tb, trace)
    return ans or "No evidence found for that vessel - cannot answer.", tb.ledger
