"""Guided EvidenceFlow chat; policy is server-side and confirmation gates mutation."""
import uuid
from datetime import UTC, datetime

SYSTEM_PROMPT = """EVIDENCEFLOW assistant asks one question at a time; no invented evidence/quotes/dates/actors; draft not evidence until confirmation; originals immutable; disagreement creates new linked evidence; citations required; manager owns rating, HR audits; AI never decides."""
EVENT_TYPES = {"user_message", "assistant_delta", "clarification_requested", "draft_updated", "evidence_preview", "confirmation_required", "evidence_created", "tool_started", "tool_completed", "knowledge_result", "citation", "manager_decision_required", "error", "turn_completed"}
QUESTIONS = {
    "contribution": [("employeeId", "Which employee should this contribution belong to?"), ("period", "What review period does it cover?"), ("competency", "Which competency does it show?"), ("situation", "What situation happened?"), ("action", "What did you do?"), ("result", "What result or impact can be verified?"), ("verifier", "Who or what can verify it?")],
    "feedback": [("employeeId", "Which employee should receive this feedback?"), ("period", "What review period does it cover?"), ("competency", "Which competency is involved?"), ("behavior", "What behavior did you observe?"), ("impact", "What impact did it have?"), ("feedbackType", "Is this recognition, coaching, or concern?"), ("visibility", "Who may see it: employee_manager_hr, manager_hr, or hr_only?")],
    "checkin": [("employeeId", "Which employee is this check-in for?"), ("period", "What review period does it cover?"), ("competency", "Which competency is involved?"), ("progress", "What progress was made?"), ("obstacle", "What obstacle remains?"), ("support", "What support is needed?"), ("owner", "Who owns next action?"), ("dueDate", "What is due date (YYYY-MM-DD)?"), ("successEvidence", "What evidence will show success?")],
}

def _now(): return datetime.now(UTC).isoformat().replace("+00:00", "Z")
def event(kind, text="", **extra): return {"type": kind, "eventId": f"evt-{uuid.uuid4().hex[:12]}", "at": _now(), "text": text, **extra}

def create_session(store, actor, kind="contribution"):
    if not isinstance(actor, dict) or actor.get("role") not in {"employee", "peer", "manager", "hr"} or not actor.get("id") or kind not in QUESTIONS:
        return None
    data = store._read(); sid = f"thread-{uuid.uuid4().hex[:12]}"
    data.setdefault("chat_sessions", {})[sid] = {"actor": actor, "kind": kind, "answers": {}, "events": [event("assistant_delta", f"I can help with {kind}. Draft stays uncommitted until you confirm it.")], "createdAt": _now()}
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
        session["events"].append(event("tool_started", "Reviewing scoped evidence", source="research", employeeId=employee_id))
        kind = "knowledge_result" if result.get("state") == "answered" else "abstained"
        session["events"].append(event(kind, result.get("answer") or result.get("reason", "No evidence."), result=result))
        session["events"].append(event("tool_completed", "Scoped evidence review complete", resultCount=len(result.get("evidence", []))))
        if result.get("citations"):
            session["events"].append(event("citation", "Citation validated.", citations=result["citations"], evidence=result.get("evidence", [])))
        if result.get("conflict"):
            session["events"].append(event("conflict", "Observed evidence spans multiple rater roles."))
        store._write(data)
        return {"state": "ok", "events": session["events"][-5:], "knowledge": result}
    questions = QUESTIONS[session.get("kind", "contribution")]
    missing = next((key for key, _ in questions if key not in session["answers"]), None)
    if missing:
        session["answers"][missing] = text
    next_item = next(((key, q) for key, q in questions if key not in session["answers"]), None)
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
    if not session or not session["answers"] or len(session["answers"]) < len(QUESTIONS[session.get("kind", "contribution")]): return {"state": "rejected", "reason": "Complete guided questions before confirmation."}
    result = store.create_draft(session.get("kind", "contribution"), session["actor"], session["answers"])
    if result.get("state") != "ready_for_confirmation": return result
    saved = store.confirm_draft(result["draftId"], session["actor"])
    data = store._read(); session = data["chat_sessions"][sid]
    session["events"].append(event("evidence_created", "Evidence created after confirmation.", evidence=saved.get("evidence")))
    session["events"].append(event("done", "Contribution saved.")); store._write(data)
    return saved
