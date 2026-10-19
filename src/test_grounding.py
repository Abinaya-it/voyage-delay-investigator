import sys, os; sys.path.insert(0, "src"); os.environ["OFFLINE"] = "1"
from agent import investigate
def test_evidence_before_answer():
    ans, led = investigate("Why is MV Ocean Star delayed?")
    assert len(led) >= 3 and "[E1]" in ans
def test_confirmed_vs_contributing():
    ans, _ = investigate("Why is MV Ocean Star delayed?")
    a, b = ans.split("Possible contributing")
    assert "INC-201" in a and "INC-202" in b and "INC-300" not in ans
def test_unknown_vessel_refuses():
    ans, led = investigate("Why is MV Ghost delayed?")
    assert "cannot answer" in ans and not led
