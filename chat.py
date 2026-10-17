"""Guided EvidenceFlow chat; policy is server-side and confirmation gates mutation."""
import uuid
from datetime import UTC, datetime

SYSTEM_PROMPT = """EVIDENCEFLOW assistant asks one question at a time; no invented evidence/quotes/dates/actors; draft not evidence until confirmation; originals immutable; disagreement creates new linked evidence; citations required; manager owns rating, HR audits; AI never decides."""
EVENT_TYPES = {"user_message", "assistant_delta", "clarification_requested", "draft_updated", "evidence_preview", "confirmation_required", "evidence_created", "tool_status", "knowledge_query_started", "knowledge_result", "citations", "conflict", "abstained", "error", "done"}
QUESTIONS = [("employeeId", "Which employee should this contribution belong to?"), ("period", "What review period does it cover?"), ("competency", "Which competency does it show? (collaboration, initiative, adaptability, delivery_quality)"), ("situation", "What situation happened?"), ("action", "What did you do?"), ("result", "What result or impact can be verified?"), ("verifier", "Who or what can verify it?")]

def _now(): return datetime.now(UTC).isoformat().replace("+00:00", "Z")
def event(kind, text="", **extra): return {"type": kind, "eventId": f"evt-{uuid.uuid4().hex[:12]}", "at": _now(), "text": text, **extra}

def create_session(store, actor):
    if not isinstance(actor, dict) or actor.get("role") not in {"employee", "peer", "manager", "hr"} or not actor.get("id"):
        return None
    data = store._read(); sid = f"thread-{uuid.uuid4().hex[:12]}"
    data.setdefault("chat_sessions", {})[sid] = {"actor": actor, "kind": "contribution", "answers": {}, "events": [event("assistant_delta", "I can help capture one contribution. Draft stays uncommitted until you confirm it.")], "createdAt": _now()}
    store._write(data); return sid

def get_session(store, sid): return store._read().get("chat_sessions", {}).get(sid)

def message(store, sid, text):
    data = store._read(); session = data.get("chat_sessions", {}).get(sid)
    if not session: return None
    text = text.strip() if isinstance(text, str) else ""
    if not text: return {"state": "error", "reason": "message must be non-empty"}
    session["events"].append(event("user_message", text))
    factual = any(word in text.lower() for word in ("how did", "what evidence", "evidence", "perform", "performance"))
    if factual:
        from knowledge import search_employee_knowledge
        employee_id = session["actor"].get("id") if session["actor"].get("role") == "employee" else None
        result = search_employee_knowledge(store, session["actor"], text, employee_id=employee_id, source="research")
        session["events"].append(event("knowledge_query_started", "Read-only research evidence lookup.", source="research", employeeId=employee_id))
        kind = "knowledge_result" if result.get("state") == "answered" else "abstained"
        session["events"].append(event(kind, result.get("answer") or result.get("reason", "No evidence."), result=result))
        if result.get("citations"):
            session["events"].append(event("citations", "Citations validated.", citations=result["citations"], evidence=result.get("evidence", [])))
        if result.get("conflict"):
            session["events"].append(event("conflict", "Observed evidence spans multiple rater roles."))
        store._write(data)
        return {"state": "ok", "events": session["events"][-5:], "knowledge": result}
    missing = next((key for key, _ in QUESTIONS if key not in session["answers"]), None)
    if missing:
        session["answers"][missing] = text
    next_item = next(((key, q) for key, q in QUESTIONS if key not in session["answers"]), None)
    if next_item:
        session["events"].append(event("clarification_requested", next_item[1], field=next_item[0]))
    else:
        preview = dict(session["answers"]); preview["rater_role"] = "self" if session["actor"]["role"] == "employee" else session["actor"]["role"]
        session["events"].append(event("draft_updated", "Draft updated. Review before saving.", draft=preview))
        session["events"].append(event("evidence_preview", "Evidence preview", preview=preview))
        session["events"].append(event("confirmation_required", "Confirm to create immutable evidence.", preview=preview))
    store._write(data)
    return {"state": "ok", "events": session["events"][-3:], "complete": not next_item}

def confirm(store, sid):
    session = get_session(store, sid)
    if not session or not session["answers"] or len(session["answers"]) < len(QUESTIONS): return {"state": "rejected", "reason": "Complete guided questions before confirmation."}
    result = store.create_draft("contribution", session["actor"], session["answers"])
    if result.get("state") != "ready_for_confirmation": return result
    saved = store.confirm_draft(result["draftId"], session["actor"])
    data = store._read(); session = data["chat_sessions"][sid]
    session["events"].append(event("evidence_created", "Evidence created after confirmation.", evidence=saved.get("evidence")))
    session["events"].append(event("done", "Contribution saved.")); store._write(data)
    return saved
