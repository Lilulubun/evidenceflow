"""REF-008: read-only, employee-scoped provenance graph; no inferred semantics."""
import re

from app_core import VALID_ROLES, VALID_RELATIONSHIPS
from governance import evidence_quote
from query_layer import load_evidence


def employee_graph(store, body):
    employee = body.get("employeeId")
    actor = body.get("actor")
    source = body.get("source")
    if (not isinstance(employee, str) or not re.fullmatch(r"emp-[0-9]{3}", employee)
            or not isinstance(source, str) or source not in {"research", "runtime"}
            or not isinstance(actor, dict) or not isinstance(actor.get("role"), str) or actor.get("role") not in VALID_ROLES
            or not isinstance(actor.get("id"), str) or not actor["id"].strip()
            or any(not isinstance(body.get(k, ""), str) for k in ("quarter", "competency"))):
        return 422, {"error": "Employee ID, explicit source (research/runtime), valid demo actor and string filters required."}
    if actor["role"] == "employee" and actor["id"] != employee:
        return 403, {"error": "Employees may view only their own evidence graph."}
    rows, relations = [], []
    name = employee
    if source == "research":
        # Scope before construction. Research fixture has no response relations or visibility policy.
        for row in load_evidence():
            if row["person_id"] != employee:
                continue
            name = row["person_name"]
            rows.append({"id": row["id"], "quote": row["quote"], "quarter": row["quarter"],
                         "competency": row["competency"], "raterId": row["rater_id"],
                         "raterRole": row["rater_role"], "date": row["event_time"],
                         "ingestionTime": row["ingestion_time"], "kind": "evidence", "sentiment": row["sentiment"]})
    else:
        state = store.snapshot()
        visible_ids = {r["id"] for r in store.visible_evidence(actor)}
        # Enforce stored visibility too; response inherits original visibility, never exposes hidden originals.
        scoped = {r["id"]: r for r in state["evidence"]
                  if r["id"] in visible_ids and r["data"].get("employee_id") == employee}

        def permitted(row):
            policy = row["data"].get("visibility", "employee_manager_hr")
            return (policy == "employee_manager_hr" or
                    policy == "manager_hr" and actor["role"] in {"manager", "hr"} or
                    policy == "hr_only" and actor["role"] == "hr")

        originals = {key: r for key, r in scoped.items() if r["kind"] != "response" and permitted(r)}
        allowed = dict(originals)
        for key, row in scoped.items():
            if row["kind"] == "response" and row["data"].get("original_evidence_id") in originals and permitted(row):
                allowed[key] = row
        for row in allowed.values():
            data = row["data"]
            original = originals.get(data.get("original_evidence_id"), row)["data"]
            rows.append({"id": row["id"], "quote": evidence_quote(row),
                         "quarter": data.get("period") or original.get("period", ""),
                         "competency": data.get("competency") or original.get("competency", ""),
                         "raterId": row["created_by"]["id"], "raterRole": data.get("rater_role", ""),
                         "date": row["created_at"], "kind": row["kind"], "status": row["status"]})
        relations = state["relations"]
    quarters = sorted({r["quarter"] for r in rows if r["quarter"]})
    competencies = sorted({r["competency"] for r in rows if r["competency"]})
    rows = [r for r in rows if (not body.get("quarter") or r["quarter"] == body["quarter"])
            and (not body.get("competency") or r["competency"] == body["competency"])]
    center = "employee:" + employee
    nodes = {center: {"id": center, "type": "employee", "label": name, "employeeId": employee}}
    links = []

    def link(a, b, kind):
        links.append({"source": a, "target": b, "type": kind})

    for row in rows:
        eid = "evidence:" + row["id"]
        nodes[eid] = {**row, "id": eid, "evidenceId": row["id"], "type": "evidence", "label": row["id"]}
        link(center, eid, "has-evidence")
        if row["competency"]:
            cid = "competency:" + row["competency"]
            nodes[cid] = {"id": cid, "type": "competency", "label": row["competency"]}
            link(eid, cid, "competency")
        rid = "rater:" + row["raterRole"] + ":" + row["raterId"]
        nodes[rid] = {"id": rid, "type": "rater", "label": row["raterId"] + " (" + row["raterRole"] + ")", "raterRole": row["raterRole"]}
        link(eid, rid, "rated-by")
    for relation in relations:
        a, b = "evidence:" + relation["response_evidence_id"], "evidence:" + relation["original_evidence_id"]
        if a in nodes and b in nodes and relation["relationship"] in VALID_RELATIONSHIPS:
            link(a, b, relation["relationship"])
    return 200, {"employeeId": employee, "source": source, "label": "Local evidence graph · synthetic demo",
                 "notice": "Demo actor selector is not production authentication. Not a live Hindsight graph.",
                 "nodes": list(nodes.values()), "links": links, "evidenceCount": len(rows),
                 "filters": {"quarters": quarters, "competencies": competencies}}
