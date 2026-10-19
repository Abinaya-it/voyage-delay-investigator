
import json, pathlib
import networkx as nx

SEED = pathlib.Path(__file__).parent.parent / "data" / "seed.json"

def build_graph(path=SEED) -> nx.MultiDiGraph:
    d = json.loads(pathlib.Path(path).read_text())
    g = nx.MultiDiGraph()
    for v in d["vessels"]:   g.add_node(v["id"], label="Vessel", **v)
    for p in d["ports"]:     g.add_node(p["id"], label="Port", **p)
    for i in d["incidents"]: g.add_node(i["id"], label="Incident", **i)
    for y in d["voyages"]:
        g.add_node(y["id"], label="Voyage", **y)
        g.add_edge(y["vessel"], y["id"], rel="OPERATES")
        g.add_edge(y["id"], y["origin"], rel="DEPARTED_FROM")
        g.add_edge(y["id"], y["destination"], rel="ARRIVES_AT")
    for i in d["incidents"]:
        g.add_edge(i["voyage"], i["id"], rel="AFFECTED_BY")
    return g

def neighbors(g, node, rel, label=None):
    return [(n, g.nodes[n]) for _, n, k in g.out_edges(node, data=True)
            if k["rel"] == rel and (label is None or g.nodes[n]["label"] == label)]
