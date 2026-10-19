def render(a):
    v = a["voyage"].data
    L = [f"## Why is {v['vessel_name']} delayed?",
         f"**Voyage {v['id']}**: {v['origin_name']} -> {v['destination_name']}. Original ETA {v['original_eta']}, revised ETA {v['revised_eta']}. Recorded delay: **{v['recorded_delay_hours']}h** [{a['voyage'].id}]", "",
         "### Confirmed causes (supported by a verified record)"]
    if a["confirmed"]:
        for i, e in a["confirmed"]:
            L.append(f"- {i['type']} ({i['id']}, {i['severity']}) - {i['attributed_delay_hours']}h attributed; source: {i['source']} [{e}]")
    else: L.append("- None confirmed in the data.")
    L.append(f"- Confirmed causes explain **{a['explained']}h of {v['recorded_delay_hours']}h**.")
    L += ["", "### Possible contributing factors (NOT confirmed)"]
    p = a["port"]
    if a["contributing"]:
        L.append(f"- {p.data['name']} congestion is **{p.data['congestion']}** (avg wait {p.data['avg_wait_hours']}h, {p.data['vessels_at_anchor']} vessels at anchor, recorded {p.data['recorded_at']}) [{p.id}]. Port-wide figure; not proven to apply to this vessel.")
    for i, e in a["unverified"]:
        L.append(f"- {i['type']} ({i['id']}) - status '{i['status']}', source: {i['source']} [{e}]")
    if not a["contributing"] and not a["unverified"]: L.append("- None found.")
    L += ["", "### What the operations team should check next"] + [f"{n}. {c}" for n, c in enumerate(a["checks"], 1)]
    L += ["", "_Every statement above is traceable to the evidence IDs shown (see evidence trail)._"]
    return "\n".join(L)
