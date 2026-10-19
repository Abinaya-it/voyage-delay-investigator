import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from flask import Flask, jsonify, request
from agent import investigate
from kg import build_graph
from reasoning import analyse

ROOT = pathlib.Path(__file__).parent.parent
app = Flask(__name__, static_folder=str(ROOT / "static"), static_url_path="")

@app.get("/")
def home():
    return app.send_static_file("index.html")

@app.get("/api/graph")
def graph():
    g = build_graph()
    nodes = [{"id": n, "label": a["label"], "name": a.get("name") or a.get("type") or n}
             for n, a in g.nodes(data=True)]
    edges = [{"s": s, "t": t, "rel": k["rel"]} for s, t, k in g.edges(data=True)]
    return jsonify(nodes=nodes, edges=edges)

@app.post("/api/investigate")
def run():
    q = (request.json or {}).get("question", "").strip()
    if not q:
        return jsonify(ok=False, message="Ask a question first."), 400
    steps = []
    answer, ledger = investigate(q, lambda kind, text: steps.append({"kind": kind, "text": text}))
    a = analyse(ledger)
    if not a:
        return jsonify(ok=False, message=answer, steps=steps)
    v = a["voyage"].data
    highlight = [v["vessel"], v["id"], v["origin"], v["destination"]]
    highlight += [i["id"] for i, _ in a["confirmed"] + a["unverified"]]
    return jsonify(
        ok=True, answer=answer, steps=steps, highlight=highlight,
        voyage=v, port=a["port"].data if a["port"] else None,
        confirmed=[{**i, "ev": e} for i, e in a["confirmed"]],
        possible=[{**i, "ev": e} for i, e in a["unverified"]],
        congestion_flag=bool(a["contributing"]),
        explained=a["explained"], gap=a["gap"], checks=a["checks"],
        evidence=[{"id": e.id, "tool": e.tool, "path": e.graph_path, "data": e.data} for e in ledger])

if __name__ == "__main__":
    app.run(debug=True, port=5000)
