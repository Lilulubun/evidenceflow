"""Runnable EVE-004 checks: immutable original and restricted linked response."""
import tempfile
from pathlib import Path

from app_core import Store

employee = {"id": "emp-004", "role": "employee"}
peer = {"id": "peer-001", "role": "peer"}
manager = {"id": "manager-001", "role": "manager"}
with tempfile.TemporaryDirectory() as directory:
    storage = Store(Path(directory) / "state.json")
    original_draft = storage.create_draft("contribution", employee, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative", "situation": "Release risk", "action": "Coordinated fix", "result": "Release completed", "verifier": "PR-18"})
    original = storage.confirm_draft(original_draft["draftId"], employee)["evidence"]
    original_serialized = str(original)

    response_draft = storage.create_response_draft(employee, {"originalEvidenceId": original["id"], "response": "Result happened after vendor confirmation.", "source": "Vendor ticket V-3", "relationship": "clarified"})
    assert response_draft["state"] == "ready_for_confirmation"
    response = storage.confirm_draft(response_draft["draftId"], employee)["evidence"]
    state = storage.snapshot()
    unchanged = next(row for row in state["evidence"] if row["id"] == original["id"])
    assert str(unchanged) == original_serialized
    assert state["relations"] == [{"original_evidence_id": original["id"], "response_evidence_id": response["id"], "relationship": "clarified", "created_at": response["created_at"]}]
    assert response["id"] not in {row["id"] for row in storage.visible_evidence(peer)}
    assert response["id"] in {row["id"] for row in storage.visible_evidence(employee)}
    assert response["id"] in {row["id"] for row in storage.visible_evidence(manager)}
    rejected = storage.create_response_draft(peer, {"originalEvidenceId": original["id"], "response": "No", "source": "None", "relationship": "disputed"})
    assert rejected["state"] == "rejected"
print("response checks passed")
