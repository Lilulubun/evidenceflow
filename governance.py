"""Review, citation, and audit rules. Human manager owns rating decisions."""
from app_core import now

VALID_CLASSIFICATIONS = {"accepted", "partially_accepted", "not_accepted", "needs_investigation"}


def evidence_quote(item):
    data = item["data"]
    return data.get("result") or data.get("impact") or data.get("response") or data.get("progress") or ""


def review_view(store, employee_id):
    state = store.snapshot()
    evidence = [row for row in state["evidence"] if row["data"].get("employee_id") == employee_id]
    rows = []
    for row in evidence:
        data = row["data"]
        rows.append({"id": row["id"], "period": data.get("period"), "competency": data.get("competency"), "raterRole": data.get("rater_role"), "kind": row["kind"], "quote": evidence_quote(row), "status": row["status"]})
    roles = {row["raterRole"] for row in rows}
    conflicts = [row for row in rows if row["kind"] == "response" or row["status"] == "disputed"]
    required = {"collaboration", "initiative", "adaptability"}
    return {"employeeId": employee_id, "evidence": rows, "raterRoles": sorted(roles), "supporting": [row for row in rows if row not in conflicts], "conflicting": conflicts, "missingCompetencies": sorted(required - {row["competency"] for row in rows if row["competency"]}), "periods": sorted({row["period"] for row in rows if row["period"]})}


def validate_citations(summary, evidence):
    """Fabricated citations are rejected outright; claims missing a citation are flagged
    `unsupported` and summarized as coverage % (REF-002, arXiv:2412.18004)."""
    if not isinstance(summary, list) or not summary:
        return {"valid": False, "reason": "Summary requires at least one cited claim."}
    allowed = {row["id"]: row["quote"] for row in evidence}
    supported = 0
    flagged = []
    for index, claim in enumerate(summary):
        if not isinstance(claim, dict) or not isinstance(claim.get("text"), str) or not claim["text"].strip():
            return {"valid": False, "reason": f"Claim {index} needs text."}
        evidence_id, quote = claim.get("evidenceId"), claim.get("quote")
        if evidence_id is None and quote is None:
            flagged.append(index)
            continue
        if evidence_id not in allowed or quote != allowed[evidence_id]:
            return {"valid": False, "reason": f"Claim {index} has invalid citation."}
        supported += 1
    coverage = round(100 * supported / len(summary))
    return {"valid": True, "citationCount": supported, "supportedClaims": supported,
            "unsupportedClaims": len(flagged), "unsupportedIndexes": flagged,
            "coverage": coverage}


def draft_summary(view):
    claims = []
    for row in view["supporting"][:3]:
        if row["quote"]:
            claims.append({"text": f"{row['raterRole']} evidence: {row['quote']}", "evidenceId": row["id"], "quote": row["quote"]})
    return claims


def create_or_update_review(store, actor, employee_id, summary, rationale, rating, provisional=True):
    if actor.get("role") != "manager":
        return {"state": "rejected", "reason": "Only manager may record review."}
    view = review_view(store, employee_id)
    citations = validate_citations(summary, view["evidence"])
    if not citations["valid"]:
        return {"state": "rejected", "reason": citations["reason"]}
    # REF-002: keep flagged claims visible on the review record; manager sees coverage before finalize.
    if citations["unsupportedClaims"]:
        citations["notice"] = f"{citations['unsupportedClaims']} claim(s) lack evidence citation; coverage {citations['coverage']}%."
    if not isinstance(rationale, str) or not rationale.strip() or not isinstance(rating, str) or not rating.strip():
        return {"state": "rejected", "reason": "Rationale and human-selected rating required."}
    data = store._read()
    review = data["reviews"].setdefault(employee_id, {"employee_id": employee_id, "rating_history": [], "response_classifications": [], "finalized": False})
    before = review["rating_history"][-1]["after"] if review["rating_history"] else None
    entry = {"before": before, "after": rating, "actor": actor, "timestamp": now(), "reason": rationale, "stage": "provisional" if provisional else "final"}
    review["summary"] = summary
    review["rationale"] = rationale
    review["citation_coverage"] = citations["coverage"]
    review["unsupported_claims"] = citations["unsupportedClaims"]
    review["rating_history"].append(entry)
    data["events"].append({"type": "rating_recorded", "employee_id": employee_id, **entry})
    store._write(data)
    return {"state": "recorded", "review": review, "citation": citations}


def classify_response(store, actor, employee_id, response_id, classification, reason):
    if actor.get("role") != "manager":
        return {"state": "rejected", "reason": "Only manager may classify response."}
    if classification not in VALID_CLASSIFICATIONS or not isinstance(reason, str) or not reason.strip():
        return {"state": "rejected", "reason": "Valid classification and reason required."}
    data = store._read()
    review = data["reviews"].setdefault(employee_id, {"employee_id": employee_id, "rating_history": [], "response_classifications": [], "finalized": False})
    item = next((row for row in data["evidence"] if row["id"] == response_id and row["kind"] == "response"), None)
    if not item or item["data"].get("employee_id") != employee_id:
        return {"state": "rejected", "reason": "Linked employee response not found."}
    event = {"response_evidence_id": response_id, "classification": classification, "reason": reason, "actor": actor, "timestamp": now()}
    review["response_classifications"].append(event)
    data["events"].append({"type": "response_classified", "employee_id": employee_id, **event})
    store._write(data)
    return {"state": "recorded", "classification": event}


def finalize_review(store, actor, employee_id, rationale, acknowledge_unresolved=False):
    if actor.get("role") != "manager":
        return {"state": "rejected", "reason": "Only assigned manager may finalize rating."}
    data = store._read()
    review = data["reviews"].get(employee_id)
    if not review or not review["rating_history"]:
        return {"state": "rejected", "reason": "Provisional rating required before finalization."}
    # REF-002: finalizing a summary below 100% citation coverage is an explicit, audited choice.
    coverage = review.get("citation_coverage", 100)
    if coverage < 100 and not acknowledge_unresolved:
        return {"state": "rejected", "reason": f"Citation coverage {coverage}% is below 100%; acknowledgment required to finalize."}
    linked_response_ids = {relation["response_evidence_id"] for relation in data["relations"]}
    classified = {item["response_evidence_id"] for item in review["response_classifications"]}
    unresolved = linked_response_ids - classified
    if unresolved and not (acknowledge_unresolved and isinstance(rationale, str) and rationale.strip()):
        return {"state": "rejected", "reason": "Unresolved disagreement requires explicit acknowledgment and rationale."}
    if not isinstance(rationale, str) or not rationale.strip():
        return {"state": "rejected", "reason": "Finalization rationale required."}
    prior = review["rating_history"][-1]
    entry = {"before": prior["after"], "after": prior["after"], "actor": actor, "timestamp": now(), "reason": rationale, "stage": "final"}
    review["rating_history"].append(entry)
    review["finalized"] = True
    review["finalized_at"] = entry["timestamp"]
    data["events"].append({"type": "review_finalized", "employee_id": employee_id, "acknowledged_unresolved": bool(unresolved), **entry})
    store._write(data)
    return {"state": "finalized", "review": review}


def hr_audit(store, actor, employee_id):
    if actor.get("role") != "hr":
        return {"state": "rejected", "reason": "HR role required for audit."}
    data = store.snapshot()
    return {"state": "ok", "evidence": [row for row in data["evidence"] if row["data"].get("employee_id") == employee_id], "relations": data["relations"], "review": data["reviews"].get(employee_id), "events": [row for row in data["events"] if row.get("employee_id") == employee_id or row.get("evidence_id") in {e["id"] for e in data["evidence"] if e["data"].get("employee_id") == employee_id}]}
