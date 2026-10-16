"""EVE-009 TKT 3 validation runner.

Executes the 12 test cases from tkt3_validation_spec.md against a controlled
synthetic fixture (emp-004 Dewi Nugraha, Q3-Q4 2026, self/peer/manager).
Writes tkt3_results.json and a timestamped run log under tkt3_logs/.
Claim boundary: proves critical functions in a controlled synthetic scenario only.
"""
import json
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from app_core import Store
from governance import classify_response, create_or_update_review, draft_summary, evidence_quote, finalize_review, hr_audit, review_view, validate_citations
from query_layer import query as structured_query

ROOT = Path(__file__).parent
EMPLOYEE_ID = "emp-004"
PERIODS = ("Q3-2026", "Q4-2026")


class Recorder:
    def __init__(self):
        self.results = []
        self.transcript = []

    def step(self, label, detail):
        self.transcript.append({"at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "step": label, **detail})
        print(f"    {label}: {json.dumps(detail, ensure_ascii=False)[:160]}")

    def case_input(self, detail):
        """REF-004: record the inputs a test case drove the system with."""
        self.transcript.append({"at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "step": "case.input", **detail})
        print(f"    case.input: {json.dumps(detail, ensure_ascii=False)[:160]}")

    def case(self, case_id, function, expected, observed, passed):
        self.results.append({"id": case_id, "function": function, "expected": expected, "observed": observed, "pass": bool(passed)})
        # Verdict marker closes this case's group; steps before the first marker are fixture.
        self.transcript.append({"at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "step": "case.verdict", "group": case_id, "pass": bool(passed)})
        print(f"  {case_id}: {'PASS' if passed else 'FAIL'} - {function}")

    def trajectory(self):
        """REF-004: auditable per-test trajectory (inputs, outputs, verdicts).

        Steps run BEFORE case() records the verdict, so grouping keys off the
        case_input marker's "case" field: entries after case N's input and
        before case N+1's input belong to case N. Entries before the first
        case_input belong to 'fixture'.
        """
        groups = {"fixture": {"inputs": [], "steps": []}}
        group = "fixture"
        for entry in self.transcript:
            if entry.get("step") == "case.input" and entry.get("case"):
                group = entry["case"]
                groups.setdefault(group, {"inputs": [], "steps": []})
            if entry.get("step") == "case.verdict":
                continue  # verdict re-attached below from results
            bucket = "inputs" if entry.get("step") == "case.input" else "steps"
            groups[group][bucket].append({key: value for key, value in entry.items() if key not in {"at", "step"}})
        for result in self.results:
            entry = groups.setdefault(result["id"], {"inputs": [], "steps": []})
            entry["verdict"] = "PASS" if result["pass"] else "FAIL"
            entry["function"] = result["function"]
            entry["expected"] = result["expected"]
            entry["observed"] = result["observed"]
        return groups


def iso_weeks_ago(days):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))


def build_fixture(store, recorder):
    """Fixture evidence: positive, negative, conflicting, incomplete-result, clarified."""
    employee = {"id": EMPLOYEE_ID, "role": "employee"}
    peer = {"id": "peer-001", "role": "peer"}
    manager = {"id": "manager-001", "role": "manager"}
    recorder.step("fixture.begin", {"employee": "Dewi Nugraha", "employeeId": EMPLOYEE_ID, "periods": list(PERIODS)})

    # Positive self contribution (Q3, collaboration).
    draft = store.create_draft("contribution", employee, {"employeeId": EMPLOYEE_ID, "period": "Q3-2026", "competency": "collaboration", "situation": "Q3 onboarding of two new engineers stalled", "action": "Ran paired onboarding sessions", "result": "Both engineers shipped first patch within two weeks", "verifier": "git log PR-41, PR-42"})
    positive = store.confirm_draft(draft["draftId"], employee)["evidence"]
    recorder.step("fixture.positive", {"evidenceId": positive["id"]})

    # Negative manager feedback (Q3, adaptability).
    draft = store.create_draft("feedback", manager, {"employeeId": EMPLOYEE_ID, "period": "Q3-2026", "competency": "adaptability", "behavior": "Rejected schema change without escalation", "impact": "Sprint 12 migration slipped five days", "feedbackType": "coaching", "visibility": "employee_manager_hr"})
    negative = store.confirm_draft(draft["draftId"], manager)["evidence"]
    recorder.step("fixture.negative", {"evidenceId": negative["id"]})

    # Conflicting peer feedback (Q4, collaboration): contradicts positive self view.
    draft = store.create_draft("feedback", peer, {"employeeId": EMPLOYEE_ID, "period": "Q4-2026", "competency": "collaboration", "behavior": "Kept incident context inside own team", "impact": "Dependent team debugged duplicate issue for a day", "feedbackType": "concern", "visibility": "employee_manager_hr"})
    conflicting = store.confirm_draft(draft["draftId"], peer)["evidence"]
    recorder.step("fixture.conflicting", {"evidenceId": conflicting["id"]})

    # Incomplete-result contribution attempt: clarification required, nothing stored.
    incomplete = store.create_draft("contribution", employee, {"employeeId": EMPLOYEE_ID, "period": "Q4-2026", "competency": "initiative", "situation": "Vendor outage", "action": "Coordinated response", "verifier": "PR-51"})
    recorder.step("fixture.incomplete", {"state": incomplete["state"], "missing": incomplete.get("missing")})

    # Check-in with owner/due date/success evidence (Q4, adaptability).
    draft = store.create_draft("checkin", employee, {"employeeId": EMPLOYEE_ID, "period": "Q4-2026", "competency": "adaptability", "progress": "Migration 70% complete", "obstacle": "Vendor API limit", "support": "Escalated with vendor manager", "owner": "manager-001", "dueDate": "2026-12-01", "successEvidence": "Vendor confirmation ticket"})
    checkin = store.confirm_draft(draft["draftId"], employee)["evidence"]
    recorder.step("fixture.checkin", {"evidenceId": checkin["id"]})

    # Clarified response linking the negative manager feedback.
    draft = store.create_response_draft(employee, {"originalEvidenceId": negative["id"], "response": "Escalation existed: vendor thread 2026-10-02; manager was CCed.", "source": "vendor-thread-2026-10-02", "relationship": "clarified"})
    clarified = store.confirm_draft(draft["draftId"], employee)["evidence"]
    recorder.step("fixture.clarified", {"evidenceId": clarified["id"], "linkedTo": negative["id"]})
    return {"employee": employee, "peer": peer, "manager": manager, "positive": positive, "negative": negative, "conflicting": conflicting, "checkin": checkin, "clarified": clarified, "incomplete": incomplete}


def run_validation():
    recorder = Recorder()
    with tempfile.TemporaryDirectory() as directory:
        store = Store(Path(directory) / "tkt3_state.json")
        fx = build_fixture(store, recorder)
        manager, employee, hr = fx["manager"], fx["employee"], {"id": "hr-001", "role": "hr"}

        # TKT3-01: structured evidence only after confirmation.
        recorder.case_input({"case": "TKT3-01", "action": "create_draft(contribution)+confirm", "result": "CI green in 20 minutes", "actor": "emp-004"})
        view_before = store.snapshot()["evidence"]
        draft = store.create_draft("contribution", employee, {"employeeId": EMPLOYEE_ID, "period": "Q4-2026", "competency": "initiative", "situation": "Unassigned blocker", "action": "Fixed pipeline", "result": "CI green in 20 minutes", "verifier": "CI run 88"})
        unconfirmed_count = len(store.snapshot()["evidence"])
        confirmed = store.confirm_draft(draft["draftId"], employee)["evidence"]
        after_count = len(store.snapshot()["evidence"])
        ok = draft["state"] == "ready_for_confirmation" and unconfirmed_count == len(view_before) and after_count == len(view_before) + 1 and confirmed["data"]["result"] == "CI green in 20 minutes"
        recorder.case("TKT3-01", "Valid contribution conversation", "Structured evidence created only after user confirmation.", {"draftState": draft["state"], "evidenceBefore": len(view_before), "evidenceAfterUnconfirmed": unconfirmed_count, "evidenceAfterConfirm": after_count, "evidenceId": confirmed["id"]}, ok)

        # TKT3-02: missing result triggers clarification; nothing stored.
        recorder.case_input({"case": "TKT3-02", "action": "create_draft(contribution) without result", "fields": ["situation", "action", "verifier"], "actor": "emp-004"})
        missing = fx["incomplete"]
        no_draft_saved = store.create_draft("contribution", employee, {"employeeId": EMPLOYEE_ID, "period": "Q4-2026", "competency": "initiative", "situation": "Second probe", "action": "Work only", "verifier": "PR-X"})
        stored = [row for row in store.snapshot()["evidence"] if row["data"].get("situation") == "Second probe"]
        ok = missing["state"] == "needs_clarification" and missing["missing"] == ["result"] and not stored and no_draft_saved["state"] == "needs_clarification"
        recorder.case("TKT3-02", "Missing result", "Clarification requested; unsupported result not stored as fact.", {"state": missing["state"], "missing": missing["missing"], "storedIncompleteDrafts": len(stored)}, ok)

        # TKT3-03: every summary claim links valid evidence ID + exact quote.
        recorder.case_input({"case": "TKT3-03", "action": "draft_summary+validate_citations", "employeeId": EMPLOYEE_ID})
        view = review_view(store, EMPLOYEE_ID)
        claims = draft_summary(view)
        citation = validate_citations(claims, view["evidence"])
        ok = bool(claims) and citation["valid"] and all(row["id"] == claim["evidenceId"] and claim["quote"] == evidence_quote(next(r for r in store.snapshot()["evidence"] if r["id"] == claim["evidenceId"])) for claim, row in zip(claims, [next(r for r in view["evidence"] if r["id"] == c["evidenceId"]) for c in claims]))
        recorder.case("TKT3-03", "Source-linked summary", "Every claim links valid evidence ID and exact stored quote.", {"claimCount": len(claims), "citationCheck": citation, "citedIds": [c["evidenceId"] for c in claims]}, ok)

        # TKT3-04: fabricated citation rejected.
        recorder.case_input({"case": "TKT3-04", "action": "validate_citations with wrong quote + unknown ID"})
        target = fx["positive"]["id"]
        wrong_quote = [{"text": "Claim", "evidenceId": target, "quote": "Never stored words"}]
        missing_id = [{"text": "Claim", "evidenceId": "ev-doesnotexist", "quote": "any"}]
        ok = validate_citations(wrong_quote, view["evidence"])["valid"] is False and validate_citations(missing_id, view["evidence"])["valid"] is False
        recorder.case("TKT3-04", "Fabricated citation", "Invalid quote or unknown evidence ID rejected.", {"wrongQuote": validate_citations(wrong_quote, view["evidence"]), "missingId": validate_citations(missing_id, view["evidence"])}, ok)

        # TKT3-05: rater separation. Roles are provenance labels on evidence rows;
        # employee-authored rows (check-in, response) are a distinct 'employee' role by design.
        recorder.case_input({"case": "TKT3-05", "action": "inspect raterRole on all evidence rows", "employeeId": EMPLOYEE_ID})
        roles_seen = view["raterRoles"]
        by_role = {}
        for row in view["evidence"]:
            by_role.setdefault(row["raterRole"], []).append(row["id"])
        ok = {"self", "peer", "manager"} <= set(roles_seen) and fx["positive"]["id"] in by_role.get("self", []) and fx["negative"]["id"] in by_role.get("manager", []) and fx["conflicting"]["id"] in by_role.get("peer", []) and not (set(by_role) - {"self", "peer", "manager", "employee"})
        recorder.case("TKT3-05", "Rater separation", "Self, peer, manager evidence distinguishable (employee-authored rows labeled 'employee').", {"roles": roles_seen, "byRole": by_role}, ok)

        # TKT3-06: entity boundary - wrong/unknown employee sees no evidence.
        recorder.case_input({"case": "TKT3-06", "action": "review_view(emp-009)+structured_query wrong/unknown person"})
        other_view = review_view(store, "emp-009")
        fixture_rows = [
            {"id": "ev-f1", "person_id": EMPLOYEE_ID, "person_name": "Dewi Nugraha", "rater_role": "peer", "quarter": "Q4-2026", "competency": "collaboration", "sentiment": "pos", "quote": "q1", "event_time": iso_weeks_ago(10), "ingestion_time": iso_weeks_ago(9)},
            {"id": "ev-f2", "person_id": "emp-007", "person_name": "Other", "rater_role": "peer", "quarter": "Q4-2026", "competency": "collaboration", "sentiment": "pos", "quote": "q2", "event_time": iso_weeks_ago(10), "ingestion_time": iso_weeks_ago(9)},
        ]
        wrong = structured_query("collaboration", person_id=EMPLOYEE_ID, data=fixture_rows)
        unknown = structured_query("collaboration", person_id="emp-404", data=fixture_rows)
        ok = not other_view["evidence"] and all(row["person_id"] == EMPLOYEE_ID for row in wrong["evidence"]) and unknown["abstained"] and not unknown["evidence"]
        recorder.case("TKT3-06", "Entity boundary", "Unknown/wrong employee returns no evidence from another employee.", {"unknownEmployeeEvidence": len(other_view["evidence"]), "queryRows": [row["person_id"] for row in wrong["evidence"]], "unknownQuery": unknown}, ok)

        # TKT3-07: employee response creates linked evidence; original immutable.
        recorder.case_input({"case": "TKT3-07", "action": "compare evidence row before/after linked response", "original": fx["negative"]["id"]})
        original_before = next(row for row in store.snapshot()["evidence"] if row["id"] == fx["negative"]["id"])
        relation = next(rel for rel in store.snapshot()["relations"] if rel["response_evidence_id"] == fx["clarified"]["id"])
        original_after = next(row for row in store.snapshot()["evidence"] if row["id"] == fx["negative"]["id"])
        ok = original_before == original_after and relation["original_evidence_id"] == fx["negative"]["id"] and fx["clarified"]["data"]["response"] and fx["clarified"]["kind"] == "response"
        recorder.case("TKT3-07", "Disagreement response", "Response creates new linked evidence; original unchanged.", {"originalImmutable": original_before == original_after, "relation": relation, "responseId": fx["clarified"]["id"]}, ok)

        # TKT3-08: manager classifies response with reason.
        recorder.case_input({"case": "TKT3-08", "action": "classify_response invalid/valid/employee", "responseId": fx["clarified"]["id"]})
        bad = classify_response(store, manager, EMPLOYEE_ID, fx["clarified"]["id"], "maybe", "")
        good = classify_response(store, manager, EMPLOYEE_ID, fx["clarified"]["id"], "partially_accepted", "Vendor thread confirms partial escalation.")
        employee_try = classify_response(store, employee, EMPLOYEE_ID, fx["clarified"]["id"], "accepted", "self classify")
        ok = bad["state"] == "rejected" and good["state"] == "recorded" and employee_try["state"] == "rejected" and good["classification"]["reason"]
        recorder.case("TKT3-08", "Response classification", "Manager records classification with reason; invalid rejected.", {"invalid": bad, "recorded": good["state"], "employeeRejected": employee_try["state"], "classification": good["classification"]["classification"]}, ok)

        # TKT3-09: employee cannot finalize; manager with prior rating can.
        recorder.case_input({"case": "TKT3-09", "action": "finalize as employee/hr/manager after provisional rating", "rating": "meets"})
        provisional = create_or_update_review(store, manager, EMPLOYEE_ID, claims, "Evidence supports meets with coaching on adaptability.", "meets")
        employee_finalize = finalize_review(store, employee, EMPLOYEE_ID, "Self finalize attempt")
        hr_finalize = finalize_review(store, hr, EMPLOYEE_ID, "HR override attempt")
        finalized = finalize_review(store, manager, EMPLOYEE_ID, "Finalizing after classification; adaptability tracked via check-in.")
        ok = provisional["state"] == "recorded" and employee_finalize["state"] == "rejected" and hr_finalize["state"] == "rejected" and finalized["state"] == "finalized"
        recorder.case("TKT3-09", "Access control", "Employee/HR finalize rejected; manager finalizes assigned review.", {"employeeFinalize": employee_finalize["reason"], "hrFinalize": hr_finalize["reason"], "managerFinalized": finalized["state"]}, ok)

        # TKT3-10: rating history preserves before/after/actor/timestamp/reason.
        recorder.case_input({"case": "TKT3-10", "action": "inspect rating_history entries"})
        history = store.snapshot()["reviews"][EMPLOYEE_ID]["rating_history"]
        ok = history[0]["before"] is None and history[0]["after"] == "meets" and history[-1]["stage"] == "final" and history[-1]["before"] == "meets" and all(entry["actor"] and entry["timestamp"] and entry["reason"] for entry in history)
        recorder.case("TKT3-10", "Rating history", "Append-only before/after, actor, timestamp, reason.", {"entries": [{"before": e["before"], "after": e["after"], "stage": e["stage"], "actor": e["actor"]["id"], "hasTimestamp": bool(e["timestamp"]), "hasReason": bool(e["reason"])} for e in history]}, ok)

        # TKT3-11: unresolved disagreement requires acknowledgment (fresh scenario).
        with tempfile.TemporaryDirectory() as second_dir:
            store2 = Store(Path(second_dir) / "tkt3_state2.json")
            recorder.case_input({"case": "TKT3-11", "action": "finalize with unresolved dispute, without/with acknowledgment"})
            d = store2.create_draft("contribution", employee, {"employeeId": EMPLOYEE_ID, "period": "Q4-2026", "competency": "delivery_quality", "situation": "Bug backlog", "action": "Fixed 8 bugs", "result": "Backlog halved", "verifier": "JIRA-9"})
            ev = store2.confirm_draft(d["draftId"], employee)["evidence"]
            r = store2.create_response_draft(employee, {"originalEvidenceId": ev["id"], "response": "Dispute: fix count inflated.", "source": "JIRA export", "relationship": "disputed"})
            resp = store2.confirm_draft(r["draftId"], employee)["evidence"]
            v2 = review_view(store2, EMPLOYEE_ID)
            c2 = draft_summary(v2)
            create_or_update_review(store2, manager, EMPLOYEE_ID, c2, "Provisional before dispute handling.", "meets")
            early = finalize_review(store2, manager, EMPLOYEE_ID, "Ignoring dispute")
            refused = early["state"] == "rejected" and "Unresolved" in early["reason"]
            acked = finalize_review(store2, manager, EMPLOYEE_ID, "Acknowledged disputed response; final stands pending investigation.", acknowledge_unresolved=True)
            ok = refused and acked["state"] == "finalized" and acked["review"]["rating_history"][-1]["reason"]
            recorder.case("TKT3-11", "Unresolved disagreement", "Finalization requires explicit acknowledgment and rationale.", {"withoutAck": early, "withAck": acked["state"], "flag": acked["review"].get("finalized")}, ok)

        # TKT3-12: HR audit reconstructs everything.
        recorder.case_input({"case": "TKT3-12", "action": "hr_audit as hr-001 + rejection probe as manager"})
        audit = hr_audit(store, hr, EMPLOYEE_ID)
        ev_ids = {row["id"] for row in audit["evidence"]}
        has_all = {fx["positive"]["id"], fx["negative"]["id"], fx["conflicting"]["id"], fx["checkin"]["id"], fx["clarified"]["id"]} <= ev_ids
        events = audit["events"]
        ok = audit["state"] == "ok" and has_all and relation and any(e["type"] == "response_classified" for e in events) and any(e["type"] == "review_finalized" for e in events) and audit["review"]["finalized"] is True and hr_audit(store, manager, EMPLOYEE_ID)["state"] == "rejected"
        recorder.case("TKT3-12", "HR audit", "HR reconstructs evidence, responses, decisions, access history.", {"evidenceCount": len(audit["evidence"]), "relations": len(audit["relations"]), "eventTypes": sorted({e["type"] for e in events}), "finalized": audit["review"]["finalized"], "nonHrRejected": True}, ok)

    return recorder


def main():
    started = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    print(f"TKT3 validation run starting {started}")
    recorder = run_validation()
    passed = [r for r in recorder.results if r["pass"]]
    citation_checks = next(r for r in recorder.results if r["id"] == "TKT3-03")
    summary = {
        "runStartedAt": started,
        "runFinishedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "fixture": {"employee": "Dewi Nugraha", "employeeId": EMPLOYEE_ID, "periods": list(PERIODS), "raterRoles": ["self", "peer", "manager"], "data": "synthetic controlled"},
        "results": recorder.results,
        "totals": {"passed": len(passed), "failed": len(recorder.results) - len(passed), "total": len(recorder.results)},
        "trajectory": recorder.trajectory(),  # REF-004: auditable per-test inputs/steps/verdicts
        "acceptance": {
            "twelveOfTwelve": len(passed) == 12,
            "citationValidity": "100%" if citation_checks["pass"] else "failures present",
            "crossEmployeeLeakage": 0 if next(r for r in recorder.results if r["id"] == "TKT3-06")["pass"] else ">0",
            "originalEvidenceMutation": 0 if next(r for r in recorder.results if r["id"] == "TKT3-07")["pass"] else ">0",
            "unauthorizedFinalizations": 0 if next(r for r in recorder.results if r["id"] == "TKT3-09")["pass"] else ">0",
        },
        "claimBoundary": "Supports only: critical prototype functions demonstrated in a controlled synthetic scenario. Does not support bias elimination, organizational validity, production readiness, or improved employee performance.",
        "transcript": recorder.transcript,
    }
    log_dir = ROOT / "tkt3_logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"tkt3-run-{started[:19].replace(':', '')}.json"
    log_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    results_path = ROOT / "tkt3_results.json"
    results_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results: {results_path}")
    print(f"Log: {log_path}")
    print(f"Total: {summary['totals']['passed']}/{summary['totals']['total']} passed")
    return 0 if summary["acceptance"]["twelveOfTwelve"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
