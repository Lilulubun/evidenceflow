"""Runnable EVE-005/006 checks: citation gate, rating history, authorization, audit."""
import tempfile
from pathlib import Path

from app_core import Store
from governance import classify_response, create_or_update_review, draft_summary, finalize_review, hr_audit, review_view, validate_citations

employee = {"id": "emp-004", "role": "employee"}
manager = {"id": "manager-001", "role": "manager"}
peer = {"id": "peer-001", "role": "peer"}
hr = {"id": "hr-001", "role": "hr"}
with tempfile.TemporaryDirectory() as directory:
    storage = Store(Path(directory) / "state.json")
    original_draft = storage.create_draft("contribution", employee, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative", "situation": "Release risk", "action": "Coordinated fix", "result": "Release completed", "verifier": "PR-18"})
    original = storage.confirm_draft(original_draft["draftId"], employee)["evidence"]

    view = review_view(storage, "emp-004")
    assert view["raterRoles"] == ["self"]
    claims = draft_summary(view)
    assert claims and all(claim["evidenceId"] == original["id"] for claim in claims)

    fabricated = [{"text": "Fake", "evidenceId": original["id"], "quote": "Not the stored quote"}]
    assert validate_citations(fabricated, view["evidence"])["valid"] is False
    assert validate_citations([{"text": "Fake", "evidenceId": "ev-missing", "quote": "x"}], view["evidence"])["valid"] is False

    # REF-002 citation coverage gate: missing-citation claim is flagged unsupported, not fabricated.
    mixed = claims + [{"text": "Overall impression without a specific quote"}]
    coverage = validate_citations(mixed, view["evidence"])
    assert coverage["valid"] is True
    assert coverage["supportedClaims"] == len(claims) and coverage["unsupportedClaims"] == 1
    assert coverage["unsupportedIndexes"] == [len(mixed) - 1]
    assert coverage["coverage"] == round(100 * len(claims) / len(mixed))
    uncited_rating = create_or_update_review(storage, manager, "emp-004", mixed, "Mixed coverage", "meets")
    assert uncited_rating["state"] == "recorded" and uncited_rating["citation"]["unsupportedClaims"] == 1
    assert "coverage" in uncited_rating["citation"]["notice"]
    assert uncited_rating["review"]["citation_coverage"] < 100
    # Finalizing below 100% coverage without acknowledgment is rejected; with acknowledgment it passes.
    gate = finalize_review(storage, manager, "emp-004", "Skip acknowledgment")
    assert gate["state"] == "rejected" and "Citation coverage" in gate["reason"]
    # Restore fully-cited summary so later finalize path stays the unresolved-response scenario.
    restore = create_or_update_review(storage, manager, "emp-004", claims, "Back to fully cited summary", "meets")
    assert restore["state"] == "recorded" and restore["review"]["citation_coverage"] == 100

    rejected = create_or_update_review(storage, employee, "emp-004", claims, "Employee view", "meets")
    assert rejected["state"] == "rejected" and "manager" in rejected["reason"]

    provisional = create_or_update_review(storage, manager, "emp-004", claims, "Strong initiative evidence", "meets")
    assert provisional["state"] == "recorded"
    bad_rating = create_or_update_review(storage, manager, "emp-004", fabricated, "Bad citation", "meets")
    assert bad_rating["state"] == "rejected" and "invalid citation" in bad_rating["reason"]

    response_draft = storage.create_response_draft(employee, {"originalEvidenceId": original["id"], "response": "Vendor confirmed later delivery.", "source": "Vendor ticket V-3", "relationship": "clarified"})
    response = storage.confirm_draft(response_draft["draftId"], employee)["evidence"]
    early = finalize_review(storage, manager, "emp-004", "Closing without acknowledgment")
    assert early["state"] == "rejected" and "Unresolved" in early["reason"]
    unclassified = classify_response(storage, manager, "emp-004", response["id"], "maybe", "No reason")
    assert unclassified["state"] == "rejected"
    classified = classify_response(storage, manager, "emp-004", response["id"], "accepted", "Vendor ticket confirms")
    assert classified["state"] == "recorded"

    finalized = finalize_review(storage, manager, "emp-004", "Acknowledged clarification; final stands.")
    assert finalized["state"] == "finalized"
    employee_finalize = finalize_review(storage, employee, "emp-004", "Self finalize")
    assert employee_finalize["state"] == "rejected" and "manager" in employee_finalize["reason"]

    audit = hr_audit(storage, hr, "emp-004")
    assert audit["state"] == "ok"
    history = audit["review"]["rating_history"]
    assert history[0]["before"] is None and history[0]["after"] == "meets"
    assert history[-1]["stage"] == "final" and history[-1]["before"] == "meets"
    assert all(entry["actor"] and entry["timestamp"] and entry["reason"] for entry in history)
    assert any(event["type"] == "response_classified" for event in audit["events"])
    hr_finalize_rejected = finalize_review(storage, hr, "emp-004", "HR override")
    assert hr_finalize_rejected["state"] == "rejected"
    assert hr_audit(storage, manager, "emp-004")["state"] == "rejected"
print("governance checks passed")
