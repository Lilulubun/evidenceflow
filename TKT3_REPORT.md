# EVIDENCEFLOW TKT 3 Validation Report

- Run: `tkt3-run-2026-10-15T192134` (UTC timestamp in `tkt3_results.json`)
- Environment: stdlib-only Python (see `tkt3_results.json` `runStartedAt`); no external services, no network AI (mock mode default), no dependencies installed.
- Scope: controlled synthetic scenario per `tkt3_validation_spec.md`.

## Claim boundary (binding)

This run supports ONLY: **"critical prototype functions were demonstrated in a controlled synthetic scenario (synthetic data, single process)."** It does NOT support claims of bias elimination, organizational validity, fairness, production readiness, or improved employee performance.

## Fixture

| Field | Value |
|---|---|
| Employee | Dewi Nugraha (`emp-004`) |
| Period | Q3-2026 → Q4-2026 |
| Rater roles | `self`, `peer`, `manager` (+ `employee`-authored check-in/response rows) |
| Competencies | collaboration, initiative, adaptability, delivery_quality |
| Evidence classes | positive, negative, conflicting, incomplete-result, clarified, check-in |

## Expected-versus-observed

| ID | Function | Expected | Observed | Pass |
|---|---|---|---|---|
| TKT3-01 | Valid contribution | Evidence created only after confirmation | Draft state `ready_for_confirmation`, evidence count unchanged before confirm, +1 after | PASS |
| TKT3-02 | Missing result | Clarification, nothing stored | `needs_clarification`, missing=[result], 0 stored drafts | PASS |
| TKT3-03 | Source-linked summary | All claims cite valid ID+exact quote | `validate_citations` valid; all claim quotes equal stored `evidence_quote` | PASS |
| TKT3-04 | Fabricated citation | Rejected | Wrong quote and unknown ID both `valid: False` | PASS |
| TKT3-05 | Rater separation | self/peer/manager distinguishable | Roles present with correct per-role evidence IDs | PASS |
| TKT3-06 | Entity boundary | No cross-employee leakage | Unknown employee → 0 evidence; query returns only `emp-004` rows | PASS |
| TKT3-07 | Disagreement response | New linked evidence, original immutable | Byte-identical original row; relation `clarified` recorded | PASS |
| TKT3-08 | Response classification | Manager-only, valid enum + reason | Invalid enum rejected, employee rejected, `partially_accepted` recorded | PASS |
| TKT3-09 | Access control | Employee/HR cannot finalize; manager can | Employee + HR finalize `rejected`; manager `finalized` | PASS |
| TKT3-10 | Rating history | Append-only before/after/actor/timestamp/reason | History: None→`meets` provisional, →`meets` final, all fields present | PASS |
| TKT3-11 | Unresolved disagreement | Acknowledgment + rationale required | Finalize without ack `rejected`; with `acknowledge_unresolved` + rationale `finalized` | PASS |
| TKT3-12 | HR audit | Full reconstruction | Evidence+relations+events+review complete; non-HR audit rejected | PASS |

## Acceptance criteria

- 12/12 test cases pass.
- Summary citation validity: 100%.
- Cross-employee evidence leakage: 0.
- Original evidence mutation: 0.
- Unauthorized finalization: 0 successful attempts.
- Every failed/blocked action records an explicit reason (verified per case in `tkt3_results.json`).

## Reproduce

```sh
cd /opt/data/research/evidenceflow-poc
python3 tkt3_runner.py            # 12/12, writes tkt3_results.json + tkt3_logs/
python3 run_checks.py             # shell/query/conversations/responses/governance/settings
python3 test_ai_adapter.py        # citation gate + provider-failure degradation
```

Exit code 0 required from each.

## Evidence retained

- `tkt3_results.json` — full machine-readable results + conversation transcript + fixture IDs.
- `tkt3_logs/tkt3-run-*.json` — timestamped run logs (one per run).
- `research/performance-appraisal-flow.md`, `WAYFINDER_MAP.md`, `tickets/25–26` — decision provenance.

## Known limitations

1. Single-process JSON store (`Store`); not multi-user durable storage.
2. Mock AI only on this host; real provider path proven by contract tests against a local HTTP stub, not a live model.
3. Synthetic fixture only; no real organizational data.
4. UI is a minimal shell page + API; screenshots/demo recording produced in EVE-010.
5. Unresolved-dispute finalization records `acknowledged_unresolved` in the event; no separate HR alert surface.
