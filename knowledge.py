"""Read-only, explicitly sourced employee knowledge lookup."""
import re
from query_layer import query, load_evidence
from governance import validate_citations

ROLES = {"employee", "peer", "manager", "hr"}

def search_employee_knowledge(store, actor, text, *, employee_id=None, source="research", quarter=None, competency=None, rater_roles=None, limit=8):
    if not isinstance(actor, dict) or actor.get("role") not in ROLES or not actor.get("id"):
        return {"state": "error", "reason": "valid actor required"}
    if source not in {"research", "runtime"}:
        return {"state": "error", "reason": "source must be research or runtime"}
    employee_id = employee_id or (actor["id"] if actor["role"] == "employee" else None)
    if not employee_id or not re.fullmatch(r"emp-[0-9]{3}", employee_id):
        return {"state": "abstained", "reason": "Employee scope required; specify employeeId."}
    if actor["role"] == "employee" and actor["id"] != employee_id:
        return {"state": "error", "reason": "Employees may query only their own evidence."}
    if source == "research":
        rows = load_evidence()
        result = query(text, person_id=employee_id, rater_roles=rater_roles, quarter=quarter, competency=competency, limit=limit, data=rows)
        evidence = [{**r, "rater_id": r.get("rater_id", "")} for r in result["evidence"]]
    else:
        visible = store.visible_evidence(actor)
        rows = []
        for item in visible:
            data = item["data"]
            if data.get("employee_id") != employee_id: continue
            policy = data.get("visibility", "employee_manager_hr")
            if policy == "manager_hr" and actor["role"] not in {"manager", "hr"}: continue
            if policy == "hr_only" and actor["role"] != "hr": continue
            rows.append({"id": item["id"], "person_id": employee_id, "person_name": employee_id,
                         "rater_id": item["created_by"]["id"], "rater_role": data.get("rater_role", ""),
                         "quarter": data.get("period", ""), "competency": data.get("competency", ""),
                         "sentiment": "pos", "quote": data.get("result") or data.get("impact") or data.get("progress") or "",
                         "event_time": item["created_at"], "ingestion_time": item["created_at"]})
        result = query(text, person_id=employee_id, rater_roles=rater_roles, quarter=quarter, competency=competency, limit=limit, data=rows)
        evidence = [{**r, "rater_id": r.get("rater_id", "")} for r in result["evidence"]]
    claims = [] if not evidence else [{"text": f"{r['rater_role']} evidence: {r['quote']}", "evidenceId": r["id"], "quote": r["quote"]} for r in evidence]
    citations = validate_citations(claims, evidence) if claims else {"valid": False, "reason": "No evidence matches scoped query."}
    return {"state": "abstained" if not evidence else "answered", "source": source, "employeeId": employee_id,
            "answer": None if not evidence else f"Observed evidence: {len(evidence)} record(s).", "evidence": evidence,
            "claims": claims, "citations": citations, "missing": not evidence, "conflict": len({r['rater_role'] for r in evidence}) > 1}
