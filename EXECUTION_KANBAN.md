# EvidenceFlow Real-AI Execution Kanban

Maps implementation tasks to decisions in `WAYFINDER_MAP.md`. Synthetic data remains knowledge-graph seed only.

## Phase 1 — Boundaries

- [x] EXE-001 — Define Hermes-style provider contract and system-wide configuration. Verified `test_provider_contract.py` (2/2).
- [x] EXE-002 — Replace production mock fallback with fail-closed `AI_UNAVAILABLE` behavior. Verified `test_provider_contract.py` (2/2).
- [x] EXE-003 — Define typed extraction schemas with source anchors for all conversation kinds. Verified `test_provider_contract.py` (2/2).
- [x] EXE-007 — Replace regex-only conversational extraction with real-provider structured extraction. Verified `test_provider_contract.py` (2/2).

## Phase 2 — Persistence and graph

- [ ] EXE-004 — Migrate JSON runtime store to SQLite without changing graph domain concepts.
- [ ] EXE-005 — Implement append-only evidence, relations, graph projection, and audit transaction.
- [ ] EXE-006 — Implement actor-scoped allowlisted graph lookup with plain-language citations.

## Phase 3 — Conversational AI

- [ ] EXE-007 — Replace regex-only conversational extraction with real-provider structured extraction.
- [ ] EXE-008 — Add provider failure, malformed output, source-anchor, timeout, and retry events.
- [ ] EXE-009 — Add neutral conflict presentation and linked clarification evidence.

## Phase 4 — Review and UI

- [ ] EXE-010 — Enforce role-based conversation ownership and graph visibility.
- [ ] EXE-011 — Enforce manager unresolved-conflict acknowledgement and rationale at finalization.
- [ ] EXE-012 — Render manager/HR evidence summary, conflicts, decisions, and audit trail.

## Phase 5 — Verification and deployment

- [ ] EXE-013 — Add tests proving provider failure never creates mock output or mutates evidence.
- [ ] EXE-014 — Preserve synthetic knowledge-graph seed and update TKT3 fixtures.
- [ ] EXE-015 — Run live-provider E2E; require `aiState=live`, no degraded/mock path.
- [ ] EXE-016 — Update docs, deployment config, and acceptance evidence.

## Gates

- No production mock AI.
- No original evidence mutation.
- No graph write before confirmation.
- No unauthorized graph context disclosure.
- No AI rating/finalization.
- `run_checks.py`, TKT3 tests, and live-provider E2E pass.
