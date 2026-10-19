
from dataclasses import dataclass
from kg import neighbors

@dataclass
class Evidence:
    id: str; tool: str; query: str; graph_path: str; data: dict

class Toolbox:
    def __init__(self, g):
        self.g, self.ledger = g, []
    def _log(self, tool, query, path, data):
        e = Evidence(f"E{len(self.ledger)+1}", tool, query, path, data)
        self.ledger.append(e); return e

    def get_voyage_details(self, vessel_name):
        for n, a in self.g.nodes(data=True):
            if a["label"] == "Vessel" and vessel_name.lower() in a["name"].lower():
                vs = neighbors(self.g, n, "OPERATES", "Voyage")
                if not vs: break
                vid, v = sorted(vs, key=lambda x: x[1]["departed"])[-1]
                o = neighbors(self.g, vid, "DEPARTED_FROM")[0][1]["name"]
                d = neighbors(self.g, vid, "ARRIVES_AT")[0]
                data = {**v, "vessel_name": a["name"], "origin_name": o,
                        "destination_id": d[0], "destination_name": d[1]["name"]}
                return self._log("get_voyage_details", vessel_name,
                                 f"({n})-[OPERATES]->({vid})-[ARRIVES_AT]->({d[0]})", data)
        return self._log("get_voyage_details", vessel_name, "no match", {"error": "vessel or voyage not found"})

    def get_port_congestion(self, port_id):
        p = self.g.nodes.get(port_id)
        if not p: return self._log("get_port_congestion", port_id, "no match", {"error": "port not found"})
        return self._log("get_port_congestion", port_id, f"({port_id}:Port)", {
            k: p[k] for k in ("name","congestion","avg_wait_hours","vessels_at_anchor","recorded_at","source")})

    def get_voyage_incidents(self, voyage_id):
        inc = neighbors(self.g, voyage_id, "AFFECTED_BY", "Incident")
        return self._log("get_voyage_incidents", voyage_id, f"({voyage_id})-[AFFECTED_BY]->(Incident)",
                         {"incidents": [a for _, a in inc]})

SCHEMAS = [
 {"name":"get_voyage_details","description":"Get the latest voyage for a vessel (route, ETAs, recorded delay).",
  "input_schema":{"type":"object","properties":{"vessel_name":{"type":"string"}},"required":["vessel_name"]}},
 {"name":"get_port_congestion","description":"Get recorded congestion for a port id (e.g. P002).",
  "input_schema":{"type":"object","properties":{"port_id":{"type":"string"}},"required":["port_id"]}},
 {"name":"get_voyage_incidents","description":"List incidents linked to a voyage id.",
  "input_schema":{"type":"object","properties":{"voyage_id":{"type":"string"}},"required":["voyage_id"]}}]
