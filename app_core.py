"""Immutable-by-default local state for controlled EVIDENCEFLOW scenarios."""
import json
import uuid
from datetime import UTC, datetime, date
from pathlib import Path

VALID_ROLES = {"employee", "peer", "manager", "hr"}
VALID_COMPETENCIES = {"collaboration", "initiative", "adaptability", "delivery_quality"}
VALID_FEEDBACK_TYPES = {"recognition", "coaching", "concern"}
VALID_VISIBILITY = {"employee_manager_hr", "manager_hr", "hr_only"}
VALID_RELATIONSHIPS = {"clarified", "superseded", "disputed"}


def now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def require_text(payload, key, errors):
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(key)
        return None
    return value.strip()


class Store:
    """Small JSON store; ponytail: single-process TKT 3 only, replace with DB transactions for multi-user use."""

    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            self._write({"drafts": {}, "evidence": [], "relations": [], "events": [], "reviews": {}})

    def _read(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def create_draft(self, kind, actor, payload):
        if actor.get("role") not in VALID_ROLES or not actor.get("id"):
            return {"state": "rejected", "reason": "Actor id and valid role are required."}
        preview = build_preview(kind, actor, payload)
        if preview["state"] != "ready_for_confirmation":
            return preview
        data = self._read()
        draft_id = f"draft-{uuid.uuid4().hex[:12]}"
        data["drafts"][draft_id] = {"kind": kind, "actor": actor, "preview": preview["preview"], "created_at": now()}
        self._write(data)
        return {"state": "ready_for_confirmation", "draftId": draft_id, "preview": preview["preview"]}

    def create_response_draft(self, actor, payload):
        if actor.get("role") != "employee" or not actor.get("id"):
            return {"state": "rejected", "reason": "Only an employee may create an employee response."}
        if not isinstance(payload, dict):
            return {"state": "rejected", "reason": "Payload must be an object."}
        data = self._read()
        original_id = payload.get("originalEvidenceId")
        original = next((item for item in data["evidence"] if item["id"] == original_id), None)
        if not original:
            return {"state": "rejected", "reason": "Original evidence does not exist."}
        if original["data"].get("employee_id") != actor["id"]:
            return {"state": "rejected", "reason": "Employee may respond only to own evidence."}
        errors = []
        response = require_text(payload, "response", errors)
        source = require_text(payload, "source", errors)
        relationship = require_text(payload, "relationship", errors)
        if relationship and relationship not in VALID_RELATIONSHIPS:
            errors.append("relationship must be clarified, superseded, or disputed")
        if errors:
            return {"state": "needs_clarification", "reason": "Response source and relationship are required.", "missing": errors}
        preview = {"employee_id": actor["id"], "original_evidence_id": original_id, "response": response, "source": source, "relationship": relationship, "rater_role": "employee"}
        draft_id = f"draft-{uuid.uuid4().hex[:12]}"
        data["drafts"][draft_id] = {"kind": "response", "actor": actor, "preview": preview, "created_at": now()}
        self._write(data)
        return {"state": "ready_for_confirmation", "draftId": draft_id, "preview": preview}

    def confirm_draft(self, draft_id, actor):
        data = self._read()
        draft = data["drafts"].get(draft_id)
        if not draft:
            return {"state": "rejected", "reason": "Draft does not exist or was already confirmed."}
        if actor != draft["actor"]:
            return {"state": "rejected", "reason": "Only draft creator may confirm evidence."}
        evidence = {"id": f"ev-{uuid.uuid4().hex[:12]}", "kind": draft["kind"], "created_at": now(), "created_by": actor, "status": "active", "data": draft["preview"]}
        data["evidence"].append(evidence)
        if draft["kind"] == "response":
            data["relations"].append({"original_evidence_id": draft["preview"]["original_evidence_id"], "response_evidence_id": evidence["id"], "relationship": draft["preview"]["relationship"], "created_at": evidence["created_at"]})
        data["events"].append({"type": "evidence_created", "actor": actor, "evidence_id": evidence["id"], "at": evidence["created_at"]})
        del data["drafts"][draft_id]
        self._write(data)
        return {"state": "confirmed", "evidence": evidence}

    def visible_evidence(self, actor):
        data = self._read()
        if actor.get("role") == "hr":
            return data["evidence"]
        visible = []
        for item in data["evidence"]:
            response = item["kind"] == "response"
            employee = item["data"].get("employee_id")
            if response and actor.get("role") == "peer":
                continue
            if actor.get("role") == "employee" and actor.get("id") != employee:
                continue
            visible.append(item)
        return visible

    def snapshot(self):
        return self._read()


def build_preview(kind, actor, payload):
    if not isinstance(payload, dict):
        return {"state": "rejected", "reason": "Payload must be an object."}
    errors = []
    employee_id = require_text(payload, "employeeId", errors)
    period = require_text(payload, "period", errors)
    competency = require_text(payload, "competency", errors)
    if competency and competency not in VALID_COMPETENCIES:
        errors.append("competency must be supported")
    if kind == "contribution":
        fields = {key: require_text(payload, key, errors) for key in ("situation", "action", "result", "verifier")}
        if "result" in errors:
            return {"state": "needs_clarification", "reason": "Result or impact is required; unsupported result was not saved.", "missing": ["result"]}
        preview = {"employee_id": employee_id, "period": period, "competency": competency, **fields, "rater_role": "self" if actor["role"] == "employee" else actor["role"]}
    elif kind == "feedback":
        fields = {key: require_text(payload, key, errors) for key in ("behavior", "impact", "feedbackType", "visibility")}
        if fields["feedbackType"] and fields["feedbackType"] not in VALID_FEEDBACK_TYPES:
            errors.append("feedbackType must be recognition, coaching, or concern")
        if fields["visibility"] and fields["visibility"] not in VALID_VISIBILITY:
            errors.append("visibility policy is invalid")
        preview = {"employee_id": employee_id, "period": period, "competency": competency, **fields, "rater_role": actor["role"]}
    elif kind == "checkin":
        fields = {key: require_text(payload, key, errors) for key in ("progress", "obstacle", "support", "owner", "dueDate", "successEvidence")}
        if fields["dueDate"]:
            try:
                date.fromisoformat(fields["dueDate"])
            except ValueError:
                errors.append("dueDate must use YYYY-MM-DD")
        preview = {"employee_id": employee_id, "period": period, "competency": competency, **fields, "rater_role": actor["role"]}
    else:
        return {"state": "rejected", "reason": "Unsupported conversation type."}
    if payload.get("source"):
        preview["source"] = payload["source"]
    if payload.get("provenance"):
        preview["provenance"] = payload["provenance"]
    if errors:
        return {"state": "needs_clarification", "reason": "Required or valid fields missing.", "missing": errors}
    return {"state": "ready_for_confirmation", "preview": preview}
