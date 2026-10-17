"""Runnable EVE-003 checks: confirmation gate and structured conversations."""
import tempfile
from pathlib import Path

from app_core import Store

actor = {"id": "emp-004", "role": "employee"}
with tempfile.TemporaryDirectory() as directory:
    storage = Store(Path(directory) / "state.json")
    missing = storage.create_draft("contribution", actor, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative", "situation": "Release risk", "action": "Coordinated fix", "verifier": "PR-18"})
    assert missing["state"] == "needs_clarification" and missing["missing"] == ["result"]
    assert not storage.snapshot()["evidence"]

    contribution = storage.create_draft("contribution", actor, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative", "situation": "Release risk", "action": "Coordinated fix", "result": "Release completed", "verifier": "PR-18"})
    assert contribution["state"] == "ready_for_confirmation"
    assert not storage.snapshot()["evidence"]
    saved = storage.confirm_draft(contribution["draftId"], actor)
    assert saved["state"] == "confirmed" and saved["evidence"]["data"]["result"] == "Release completed"

    feedback = storage.create_draft("feedback", {"id": "peer-001", "role": "peer"}, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration", "behavior": "Shared incident context", "impact": "Team resolved issue", "feedbackType": "recognition", "visibility": "employee_manager_hr"})
    assert feedback["state"] == "ready_for_confirmation"

    checkin = storage.create_draft("checkin", actor, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "adaptability", "progress": "Completed migration", "obstacle": "Vendor delay", "support": "Escalation help", "owner": "manager-001", "dueDate": "2026-12-01", "successEvidence": "Vendor confirmation"})
    assert checkin["state"] == "ready_for_confirmation"
    saved_checkin = storage.confirm_draft(checkin["draftId"], actor)
    row = next(item for item in storage.snapshot()["evidence"] if item["id"] == saved_checkin["evidence"]["id"])
    assert row["data"]["progress"] == "Completed migration"
    assert row["data"]["successEvidence"] == "Vendor confirmation"
    assert row["data"]["rater_role"] == "employee"
print("conversation checks passed")
