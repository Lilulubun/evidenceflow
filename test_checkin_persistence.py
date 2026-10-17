"""EVE-008 regression: check-in persistence with provenance, chat confirmation, read-back."""
import json
import tempfile
from pathlib import Path

from app_core import Store
from chat import confirm as chat_confirm, create_session, message as chat_message
from server import Handler

actor = {"id": "emp-004", "role": "employee"}


def store():
    s = Store(Path(tempfile.mkdtemp()) / "state.json")
    return s


def test_checkin_persists_fields_and_provenance():
    s = store()
    draft = s.create_draft("checkin", actor, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "adaptability",
        "progress": "Completed migration", "obstacle": "Vendor delay", "support": "Escalation help",
        "owner": "manager-001", "dueDate": "2026-12-01", "successEvidence": "Vendor confirmation",
        "source": "conversation", "provenance": {"source": "conversation", "sessionId": "thread-x", "actor": actor}})
    assert draft["state"] == "ready_for_confirmation"
    saved = s.confirm_draft(draft["draftId"], actor)
    assert saved["state"] == "confirmed" and saved["evidence"]["kind"] == "checkin"
    # Read back by ID through the same store the query layer and UI read from.
    row = next(item for item in s.snapshot()["evidence"] if item["id"] == saved["evidence"]["id"])
    for field, value in (("progress", "Completed migration"), ("obstacle", "Vendor delay"), ("support", "Escalation help"),
                         ("owner", "manager-001"), ("dueDate", "2026-12-01"), ("successEvidence", "Vendor confirmation"),
                         ("rater_role", "employee"), ("employee_id", "emp-004"), ("period", "Q4-2026"),
                         ("competency", "adaptability"), ("source", "conversation")):
        assert row["data"][field] == value, (field, row["data"].get(field))
    assert row["data"]["provenance"]["sessionId"] == "thread-x"
    assert row["status"] == "active" and row["created_by"] == actor


def test_chat_confirm_creates_and_returns_evidence_with_events():
    s = store()
    sid = create_session(s, actor, "checkin")
    answers = "employeeId: emp-004; period: Q4-2026; competency: adaptability; progress: Migration done; obstacle: Vendor wait; support: Escalation; owner: manager-001; dueDate: 2026-12-01; successEvidence: Vendor confirms cutover"
    result = chat_message(s, sid, answers)
    assert result["complete"] is True
    saved = chat_confirm(s, sid)
    assert saved["state"] == "confirmed" and saved["evidence"]["kind"] == "checkin"
    assert saved["evidence"]["data"]["progress"] == "Migration done"
    assert saved["evidence"]["data"]["provenance"]["sessionId"] == sid
    # evidence_created event was appended to the session transcript.
    kinds = [e["type"] for e in s._read()["chat_sessions"][sid]["events"]]
    assert "evidence_created" in kinds
    assert any(e.get("evidence", {}).get("id") == saved["evidence"]["id"] for e in s._read()["chat_sessions"][sid]["events"])


def test_chat_confirm_unknown_session_is_rejected_not_crash():
    s = store()
    result = chat_confirm(s, "thread-does-not-exist")
    assert result["state"] == "rejected"


def test_health_and_readback_have_no_secrets():
    s = store()
    draft = s.create_draft("checkin", actor, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "adaptability",
        "progress": "p", "obstacle": "o", "support": "s", "owner": "manager-001", "dueDate": "2026-12-01",
        "successEvidence": "e", "source": "conversation"})
    saved = s.confirm_draft(draft["draftId"], actor)
    raw = json.dumps(saved)
    assert "sk-" not in raw and "apiKey" not in raw


if __name__ == "__main__":
    test_checkin_persists_fields_and_provenance()
    test_chat_confirm_creates_and_returns_evidence_with_events()
    test_chat_confirm_unknown_session_is_rejected_not_crash()
    test_health_and_readback_have_no_secrets()
    print("checkin persistence checks passed")
