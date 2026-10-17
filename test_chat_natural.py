import tempfile
from pathlib import Path
from app_core import Store
from chat import create_session, message

with tempfile.TemporaryDirectory() as d:
    store = Store(Path(d) / "state.json")
    sid = create_session(store, {"id": "emp-004", "role": "employee"}, "contribution")
    result = message(store, sid, "employeeId: emp-004; period: Q4-2026; situation: outage; action: coordinated fix; result: service recovered; verifier: PR-18")
    assert result["complete"] is False
    assert any(e["type"] == "clarification_requested" for e in result["events"])
    result = message(store, sid, "initiative")
    assert result["complete"] is True
    assert any(e["type"] == "confirmation_required" for e in result["events"])
print("natural chat checks passed")
