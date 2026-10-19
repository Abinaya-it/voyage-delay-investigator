# Voyage Delay Investigator

Built for the SolversMind assignment. The question it answers:
**"Why is MV Ocean Star delayed, and what should the operations team check next?"**

The rule I built around: the agent has to fetch evidence before it says anything.
A confident-sounding guess is worse than useless in operations.

## How it works
1. Data (`data/seed.json`) is loaded into a knowledge graph (vessel, voyage, port, incident).
2. The agent calls three tools: voyage details, port congestion, voyage incidents.
3. Every tool result is saved with an ID (E1, E2, E3) and the graph path it came from.
4. `reasoning.py` sorts findings: only incidents with status "Confirmed" count as causes.
   Congestion and unverified reports are listed as possible factors.
5. The report also shows how many delay hours no confirmed cause explains.

If no evidence is found (unknown vessel), the agent says so instead of guessing.

## Run it
    pip install -r requirements.txt
    python src/app.py        # then open http://localhost:5000
    python src/main.py       
    pytest -q

Set `ANTHROPIC_API_KEY` to let Claude pick the tool calls. Without it, a fixed
planner runs the same three tools.

## Notes
- The sample data is invented. Distractors are in there on purpose (an incident
  on another vessel, an unverified weather report).
- Congestion is a port-wide average, so I treat it as a hint, not a proven cause.
- Next: Neo4j instead of networkx, live AIS/port data, search over incident reports.
