# EVIDENCEFLOW Refinement Plan (post-core polish)

Trigger: if core EVE-001..EVE-010 finish before 09:00 WIB, worker continues with REF tasks below.

## SUCCESS CRITERION (single, authoritative)

**The prototype is executable.**

Executable means ALL of these run green on this VPS, verified by real commands, not claims:

1. `python3 server.py` starts; `/health` returns 200.
2. `python3 run_checks.py` → exit 0, all checks pass.
3. `python3 tkt3_run.py` → exit 0, 12/12 pass, artifacts written (`tkt3_results.json`, `TKT3_REPORT.md`).
4. Browser UI opens at `http://127.0.0.1:8000/` and a full scenario completes by clicking only: contribution → evidence → manager summary (cited) → employee response → finalize → HR audit.
5. AI config panel saves masked key server-side; mock mode works with zero credentials.
6. `DEMO.md` steps reproduce the demo exactly, one command to start.
7. No secret in any repo file; no evidence mutation; citations 100% valid.

"Code written" ≠ done. A REF task is DONE only when its executable check passes on this machine.

## Research basis

See `research/refinement-research.md` (citation faithfulness paper, agent-eval practice, judge criteria, conversation UX, no-build chat UI pattern, LLM-as-judge caveats).

## REF tasks

### REF-001 — Browser demo UI (executable via clicks)

- Serves static `index.html`/`app.js`/`styles.css` from `server.py`; vanilla JS, no build step, no new dependency.
- Quick-reply conversation flows, confirmation card before evidence creation, clickable evidence chips (who/role/when/quote).
- Done when: full scenario completes in browser by clicking only (check 4 above); scripted UI smoke test (fetch endpoints the UI uses) passes.

### REF-002 — Citation coverage gate

- Every summary claim must map to ≥1 valid evidence; uncited claims flagged `unsupported`, coverage % shown to manager before finalize.
- Basis: arXiv:2412.18004 (57% unfaithful citations finding).
- Done when: `test_governance.py` covers uncited-claim rejection/flag; run_checks passes.

### REF-003 — Degraded-mode visibility

- UI banner + API field showing AI state: `mock` / `live` / `degraded`; provider failure never silently passes as live.
- Done when: UI shows state, endpoint test passes, README documents it.

### REF-004 — TKT3 trajectory evidence + results view

- Runner logs request/response per test case (inputs, outputs, verdicts) to auditable trajectory file; `/tkt3` results page renders 12/12 matrix.
- Done when: `tkt3_results.json` + trajectory log exist and page renders them.

### REF-005 — AI-assisted feedback hints (advisory only)

- Rubric hints on feedback drafts (specific? behavioral? impact stated?); advisory, never gating, never a rating; deterministic in mock mode.
- Done when: endpoint returns hints, tests pass, UI shows them as non-blocking suggestions.

### REF-006 — Demo packaging polish

- `DEMO.md` step-by-step script matching judge flow (problem 30s → live scenario → safety/fallback story → limitations), video storyboard per winning structure, README polish, architecture diagram.
- Done when: DEMO.md steps executed once end-to-end on this machine without error.

### REF-007 — Final executable acceptance run

- Runs every success-criterion check in sequence, records command + output into `ACCEPTANCE.md`.
- Done when: ACCEPTANCE.md shows all green with real outputs; otherwise lists exact failing check.

## Order

```text
EVE-008 → EVE-009 → EVE-010 → REF-001 → REF-002 → REF-003 → REF-004 → REF-005 → REF-006 → REF-007
```

Worker continues automatically via existing persistent worker + 15-min monitor cron.
