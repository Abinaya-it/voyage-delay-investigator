def analyse(ledger):
    by = {e.tool: e for e in ledger}
    voy, port, inc = (by.get(k) for k in ("get_voyage_details","get_port_congestion","get_voyage_incidents"))
    if not (voy and "error" not in voy.data): return None
    v = voy.data; confirmed, contributing, unverified = [], [], []
    for i in (inc.data["incidents"] if inc else []):
        (confirmed if i["status"] == "Confirmed" else unverified).append((i, inc.id))
    if port and port.data.get("congestion") in ("High", "Severe"):
        contributing.append(("congestion", port))
    explained = sum(i["attributed_delay_hours"] or 0 for i, _ in confirmed)
    gap = v["recorded_delay_hours"] - explained
    checks = []
    for i, _ in unverified:
        checks.append(f"Verify {i['id']} ({i['type']}): status is '{i['status']}', source: {i['source']}. Get noon reports / AIS track / agent confirmation.")
    if port and contributing:
        checks.append(f"Pull {v['vessel_name']}'s own anchorage/berth-wait timestamps at {v['destination_name']} - the {port.data['avg_wait_hours']}h figure is a port-wide average, not this vessel's actual wait.")
    if gap > 0:
        checks.append(f"{gap}h of the {v['recorded_delay_hours']}h delay is not attributed to any confirmed cause - reconcile against AIS speed/position logs.")
    return dict(voyage=voy, port=port, incidents=inc, confirmed=confirmed, contributing=contributing,
                unverified=unverified, explained=explained, gap=gap, checks=checks)
