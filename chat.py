"""Conversational evidence capture; server validates every final mutation."""
import re
import uuid
from datetime import UTC, datetime

SYSTEM_PROMPT = """Be conversational and concise. Extract multiple facts from each message, reflect them, ask only for missing or ambiguous facts. Never invent evidence. Draft stays uncommitted until explicit confirmation. AI never rates or finalizes."""
EVENT_TYPES = {"user_message", "assistant_delta", "assistant_message", "clarification_requested", "draft_updated", "evidence_preview", "confirmation_required", "evidence_created", "tool_started", "tool_completed", "knowledge_result", "citation", "manager_decision_required", "error", "turn_completed"}
QUESTIONS = {
    "contribution": [("employeeId", "Which employee should this contribution belong to?"), ("period", "What review period does it cover?"), ("competency", "Which competency does it show?"), ("situation", "What situation happened?"), ("action", "What did you do?"), ("result", "What result or impact can be verified?"), ("verifier", "Who or what can verify it?")],
    "feedback": [("employeeId", "Which employee should receive this feedback?"), ("period", "What review period does it cover?"), ("competency", "Which competency is involved?"), ("behavior", "What behavior did you observe?"), ("impact", "What impact did it have?"), ("feedbackType", "Is this recognition, coaching, or concern?"), ("visibility", "Who may see it: employee_manager_hr, manager_hr, or hr_only?")],
    "checkin": [("employeeId", "Which employee is this check-in for?"), ("period", "What review period does it cover?"), ("competency", "Which competency is involved?"), ("progress", "What progress was made?"), ("obstacle", "What obstacle remains?"), ("support", "What support is needed?"), ("owner", "Who owns next action?"), ("dueDate", "What is due date (YYYY-MM-DD)?"), ("successEvidence", "What evidence will show success?")],
}

def _now(): return datetime.now(UTC).isoformat().replace("+00:00", "Z")
def event(kind, text="", **extra): return {"type": kind, "eventId": f"evt-{uuid.uuid4().hex[:12]}", "at": _now(), "text": text, **extra}

def create_session(store, actor, kind="contribution"):
    if not isinstance(actor, dict) or actor.get("role") not in {"employee", "peer", "manager", "hr"} or not actor.get("id") or kind not in QUESTIONS: return None
    data = store._read(); sid = f"thread-{uuid.uuid4().hex[:12]}"
    events = [event("assistant_message", f"I can help with {kind}. Tell me what happened in your own words; include several details if you have them.")]
    data.setdefault("chat_sessions", {})[sid] = {"actor": actor, "kind": kind, "answers": {}, "events": events, "createdAt": _now()}
    store._write(data); return sid

def get_session(store, sid): return store._read().get("chat_sessions", {}).get(sid)

def _extract(text, questions):
    found = {}
    # Accept natural labelled facts in one turn: "action: ...; result: ...".
    for key, _ in questions:
        match = re.search(r"(?:^|[;\n])\s*(?:" + re.escape(key) + r"|" + re.escape(key.lower()) + r")\s*[:=]\s*([^;\n]+)", text, re.I)
        if match: found[key] = match.group(1).strip()
    return found

def message(store, sid, text):
    data = store._read(); session = data.get("chat_sessions", {}).get(sid)
    if not session: return None
    text = text.strip() if isinstance(text, str) else ""
    if not text: return {"state": "error", "reason": "message must be non-empty"}
    session["events"].append(event("user_message", text)); questions = QUESTIONS[session["kind"]]
    lower = text.lower()
    if lower in {"skip", "skip this", "pass"}:
        key = next((k for k, _ in questions if k not in session["answers"]), None)
        if key: session["answers"][key] = "Not provided"
    elif lower.startswith("correct "):
        match = re.match(r"correct\s+(\w+)\s*(?:to|=|:)\s*(.+)", text, re.I)
        if match and any(k == match.group(1) for k, _ in questions): session["answers"][match.group(1)] = match.group(2).strip()
    else:
        extracted = _extract(text, questions)
        if extracted: session["answers"].update(extracted)
        else:
            key = next((k for k, _ in questions if k not in session["answers"]), None)
            if key: session["answers"][key] = text
    missing = next(((k, q) for k, q in questions if k not in session["answers"]), None)
    if missing:
        summary = ", ".join(f"{k}={v}" for k, v in session["answers"].items())
        session["events"].append(event("assistant_message", f"Got it{(': ' + summary) if summary else ''}."))
        session["events"].append(event("clarification_requested", missing[1], field=missing[0], progress=f"{len(session['answers'])}/{len(questions)}"))
    else:
        preview = dict(session["answers"]); preview["rater_role"] = "self" if session["actor"]["role"] == "employee" else session["actor"]["role"]
        preview["source"] = "conversation"
        preview["provenance"] = {"source": "conversation", "sessionId": sid, "actor": session["actor"]}
        session["events"] += [event("assistant_message", "I captured all required details. Please review this draft before saving."), event("draft_updated", "I captured all required details. Please review this draft.", draft=preview), event("evidence_preview", "Evidence preview", preview=preview), event("confirmation_required", "Confirm to create immutable evidence.", preview=preview)]
    session["events"].append(event("turn_completed", "Turn complete")); store._write(data)
    return {"state": "ok", "events": session["events"][-6:], "complete": not missing}

def confirm(store, sid):
    session = get_session(store, sid)
    if not session or len(session["answers"]) < len(QUESTIONS[session.get("kind", "contribution")]): return {"state": "rejected", "reason": "Complete conversation before confirmation."}
    payload = dict(session["answers"])
    payload["source"] = "conversation"
    payload["provenance"] = {"source": "conversation", "sessionId": sid, "actor": session["actor"]}
    result = store.create_draft(session["kind"], session["actor"], payload)
    if result.get("state") != "ready_for_confirmation": return result
    saved = store.confirm_draft(result["draftId"], session["actor"])
    data = store._read(); data["chat_sessions"][sid]["events"].append(event("evidence_created", "Evidence created after confirmation.", evidence=saved.get("evidence"))); store._write(data)
    saved["events"] = data["chat_sessions"][sid]["events"][-2:]
    return saved
