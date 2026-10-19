import sys, json
from agent import investigate
q = " ".join(sys.argv[1:]) or "Why is MV Ocean Star delayed, and what should the operations team check next"
print(f"\nQ: {q}\n\n--- AGENT TRACE ---")
ans, ledger = investigate(q, lambda k, m: print(f"[{k}] {m}"))
print("\n--- ANSWER ---\n" + ans)
print("\n--- EVIDENCE TRAIL ---")
for e in ledger: print(f"{e.id} | {e.tool} | {e.graph_path}\n     {json.dumps(e.data)}")
