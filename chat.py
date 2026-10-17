"""Conversational evidence capture; server validates every final mutation."""
import json
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

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

def _people():
    try:
        rows = json.loads((Path(__file__).parent / "evidence.json").read_text())
        return {r.get("person_name", "").lower(): (r.get("person_id"), r.get("person_name")) for r in rows if r.get("person_name")}
    except (OSError, json.JSONDecodeError): return {}

def _extract(text, kind):
    found = {}
    labelled = {"dueDate": r"(?:due\s*date|due_date)", "successEvidence": r"(?:success\s*evidence|success_evidence)"}
    for key, pattern in labelled.items():
        m = re.search(pattern + r"\s*[:=]\s*([^;\n]+)", text, re.I)
        if m: found[key] = m.group(1).strip()
    people = _people()
    for name, (pid, display) in people.items():
        parts = name.split()
        pattern = r"\b" + r"\s+".join(re.escape(part) for part in parts) + r"\b"
        if re.search(pattern, text, re.I) or (re.search(r"\b" + re.escape(parts[0]) + r"\b", text, re.I) and sum(1 for n in people if n.split()[0] == parts[0]) == 1): found.update(employeeId=pid, employeeName=display); break
    if kind == "checkin":
        patterns = [("progress", r"\b(.+?)\s+(?:completed|finished|delivered|made progress on)\s+(.+?)(?:,|\s+but\b|\.)"), ("obstacle", r"(?:but|however)\s+(.+?)(?:\.|;|$)"), ("support", r"needs?\s+(.+?)(?:;|\.|$)"), ("successEvidence", r"success means?\s+(.+?)(?:\s+by\s+\d{4}-\d{2}-\d{2}|\.|$)"), ("dueDate", r"\b(\d{4}-\d{2}-\d{2})\b")]
        for key, pattern in patterns:
            m = re.search(pattern, text, re.I)
            if m:
                value = m.group(1).strip() if key not in {"dueDate"} else m.group(1)
                if key == "progress": value = f"completed {m.group(2).strip()}"
                found.setdefault(key, value)
        if "support" in found and "manager escalation" in found["support"].lower(): found["support"] = "manager escalation"
        found.setdefault("owner", "manager" if re.search(r"manager\s+escalation", text, re.I) else None)
        if found.get("owner") is None: found.pop("owner", None)
        if re.search(r"\b2026\b", text): found.setdefault("period", "Q4-2026")
    for key, _ in QUESTIONS[kind]:
        m = re.search(r"(?:^|[;\n])\s*" + re.escape(key) + r"\s*[:=]\s*([^;\n]+)", text, re.I)
        if m: found[key] = m.group(1).strip()
    return found

def message(store, sid, text):
    data = store._read(); session = data.get("chat_sessions", {}).get(sid)
    if not session: return None
    text = text.strip() if isinstance(text, str) else ""
    if not text: return {"state": "error", "reason": "message must be non-empty"}
    session["events"].append(event("user_message", text)); session["events"].append(event("tool_started", "Extracting structured facts.")); questions = QUESTIONS[session["kind"]]; lower = text.lower()
    if lower in {"skip", "skip this", "pass"}:
        key = next((k for k, _ in questions if k not in session["answers"]), None)
        if key: session["answers"][key] = "Not provided"
    elif lower.startswith("correct "):
        m = re.match(r"correct\s+(\w+)\s*(?:to|=|:)\s*(.+)", text, re.I)
        if m and any(k == m.group(1) for k, _ in questions): session["answers"][m.group(1)] = m.group(2).strip()
    else:
        extracted = _extract(text, session["kind"])
        session["answers"].update({k: v for k, v in extracted.items() if v is not None})
        session.setdefault("raw_message", text)
        if not extracted:
            key = next((k for k, _ in questions if k not in session["answers"]), None)
            if key: session["answers"][key] = text
    missing = next(((k, q) for k, q in questions if k not in session["answers"]), None)
    if missing:
        summary = ", ".join(f"{k}={v}" for k, v in session["answers"].items())
        session["events"].append(event("assistant_message", f"Got it{(': ' + summary) if summary else ''}.")); session["events"].append(event("clarification_requested", missing[1], field=missing[0], progress=f"{len(session['answers'])}/{len(questions)}"))
    else:
        preview = dict(session["answers"]); preview["rater_role"] = "self" if session["actor"]["role"] == "employee" else session["actor"]["role"]; preview["source"] = "conversation"; preview["raw_message"] = session.get("raw_message", text); preview["provenance"] = {"source": "conversation", "sessionId": sid, "actor": session["actor"], "person_name": preview.get("employeeName", "")}
        session["events"] += [event("assistant_message", "I captured all required details. Please review this draft before saving."), event("draft_updated", "I captured all required details. Please review this draft.", draft=preview), event("evidence_preview", "Evidence preview", preview=preview), event("confirmation_required", "Confirm to create immutable evidence.", preview=preview)]
    session["events"].append(event("turn_completed", "Turn complete")); store._write(data); return {"state": "ok", "events": session["events"][-6:], "complete": not missing}

def confirm(store, sid):
    session = get_session(store, sid)
    if not session or len(session["answers"]) < len(QUESTIONS[session.get("kind", "contribution")]): return {"state": "rejected", "reason": "Complete conversation before confirmation."}
    payload = dict(session["answers"]); payload.update(source="conversation", raw_message=session.get("raw_message", ""), provenance={"source": "conversation", "sessionId": sid, "actor": session["actor"], "person_name": session["answers"].get("employeeName", "")})
    result = store.create_draft(session["kind"], session["actor"], payload)
    if result.get("state") != "ready_for_confirmation": return result
    saved = store.confirm_draft(result["draftId"], session["actor"]); data = store._read(); data["chat_sessions"][sid]["events"].append(event("evidence_created", "Evidence created after confirmation.", evidence=saved.get("evidence"), read_back=saved.get("evidence"))); store._write(data); saved["events"] = data["chat_sessions"][sid]["events"][-2:]; return saved
