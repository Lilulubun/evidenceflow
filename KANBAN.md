# EVIDENCEFLOW Product + TKT 3 Kanban

Source maps:
- Wayfinder: `WAYFINDER_MAP.md`
- Validation: `tkt3_validation_spec.md`
- Product research: `research/performance-appraisal-flow.md`
- TKT 3 decisions: `tickets/25-tkt3-proof-of-concept.md`, `tickets/26-tkt3-evidence-package.md`

## Workflow

```text
BACKLOG → READY → IN_PROGRESS → REVIEW → DONE
                         └──────→ BLOCKED
```

Rules:
- One active task only for internal background worker.
- Move task only after acceptance criteria pass.
- Every DONE task records files, command, output, and limitations.
- No API secrets in Git. No production/TKT 3 claims before validation evidence.

## Wayfinder → Kanban map

```text
WAYFINDER_MAP.md (destination: validated TKT 3 MVP)
│
├─ Product contract decisions
│  ├─ tickets/01–04: users, value, MVP output, decision authority
│  ├─ tickets/05–08: review journey, fairness, display, pilot data
│  ├─ tickets/09, 13, 14: MVP boundary, Q3→Q4, self/peer/manager
│  └─ tickets/16–24: triggers, conversations, review, disputes, visibility, HR audit
│
├─ TKT 3 proof
│  ├─ tickets/25: critical functions + pass cases
│  └─ tickets/26: evidence package + claim boundary
│
└─ Execution Kanban
   ├─ EVE-001 contract freeze
   ├─ EVE-002 runnable prototype shell
   ├─ EVE-003 evidence conversations
   ├─ EVE-004 immutable evidence + linked responses
   ├─ EVE-005 manager summary + review
   ├─ EVE-006 HR audit + permissions
   ├─ EVE-007 real AI adapter + citation gate
   ├─ EVE-008 configuration panel + secret handling
   ├─ EVE-009 TKT 3 test runner
   └─ EVE-010 evidence package + demo freeze
```

## Execution board

### BACKLOG (refinement)

_All refinement tasks DONE — see DONE (refinement) below and `ACCEPTANCE.md`._

### EVE-001 execution record

- Status: DONE.
- Files: `PRODUCT_CONTRACT.md`, `KANBAN.md`.
- Commands: `python -m unittest discover -v` (exit 5; no unittest tests discovered); `python test_query_layer.py` (exit 0).
- Output: Contract records roles, scope, immutable evidence, authority, governance, AI boundary, and TKT 3 claim boundary. Existing query checks passed.
- Blockers: no EVE-001 blocker. `unittest discover` remains non-gating because repository uses script-style checks.
- Limitation: contract documentation only; runnable behavior remains EVE-002 onward.

### REVIEW

_None._

### DONE (refinement)

- [x] **REF-009 — Caldera UI refinement**
  - Files: `DESIGN.md`, `static/styles.css`, `static/index.html`, `static/graph.html`, `static/graph.js`, `static/app.js`, `server.py`, `test_ui.py`, self-hosted Anton/DM Sans WOFF2 + OFL licenses, `research/anti-slop/` task-local upstream snapshots + license, `docs/CALDERA_UI.md`, `docs/caldera_ui_checks.txt`, `docs/screenshots/caldera_graph_desktop.png`, `caldera_graph_mobile.png`, `caldera_workspace_desktop.png`, refreshed `tkt3_results.json` + timestamped `tkt3_logs/` runs.
  - Commands: `python3 run_checks.py`, `python3 test_graph.py`, `python3 test_ui.py`, `python3 test_ai_adapter.py`, `python3 tkt3_runner.py`, `python3 demo_scenario.py`, `node --check static/app.js`, `node --check static/graph.js`: all exit 0, final regression after UI fixes. UI smoke 34 checks; demo 13 checks; TKT3 12/12. Exact output in `docs/caldera_ui_checks.txt`.
  - Browser: fresh isolated :8159, 57 saved records. Research 24 evidence/37 nodes/72 links, Q4 collaboration 3/7/9; graph select/list/keyboard/filter/zoom/reset/pan/role/scope-denial/empty states exercised. Capture/discard/confirm, check-in, peer feedback, employee dispute, cited manager draft/edit/remove/rating, unresolved acknowledgment/finalize, HR audit, settings save/test and TKT3 trajectory exercised. Graph/workspace/review/TKT3 widths 320/768/1280 no page horizontal overflow. Screenshot vision inspection found source option clipping and small-graph label omission; fixed, recaptured. Final desktop no blocking clipping/overlap; mobile complete readable inspector/list.
  - Safety: profile scratch TMPDIR/state/settings isolated, original runtime/settings SHA-256 unchanged across regression. No npm installer, dependency, global preference, AGENTS or plugin modification. Fonts self-hosted Latin WOFF2, SIL OFL attribution. Proprietary PP font unavailable; Anton substitute disclosed. Contrast computed (Obsidian/Ember 6.06:1); zero shadows; body/navigation/buttons DM Sans 500.
  - Limits: local synthetic graph, not live Hindsight; demo actor controls not production auth. Dense mobile SVG uses zoom and complete accessible list fallback. No physical keyboard/device or screen-reader/axe audit. Native prompt return stubbed to exercise claim edit; prompt chrome not inspected. Active demo server `proc_96efbfd234ba`, PID 556781, `http://127.0.0.1:8159/graph?employee=emp-004&source=research`, isolated profile scratch. Delivery gate item-by-item and decision reasons in `docs/CALDERA_UI.md`.

- [x] **REF-008 — Employee provenance graph inspired by Hindsight**
  - Files: `employee_graph.py`, `server.py`, `static/graph.html`, `static/graph.js`, `static/index.html`, `test_graph.py`, `run_checks.py`, `docs/EMPLOYEE_GRAPH.md`, `docs/employee_graph_checks.txt`, `docs/screenshots/employee_graph.png`.
  - Commands: `python3 run_checks.py`, `python3 test_ui.py`, `python3 test_ai_adapter.py`, `python3 tkt3_runner.py`, `python3 demo_scenario.py`, `node --check static/app.js`, `node --check static/graph.js`: all exit 0. TKT3 12/12. Exact output in `docs/employee_graph_checks.txt`.
  - Browser: Chromium :8148 `/graph?employee=emp-004&source=research`: 24 evidence/37 nodes/72 links, filtered 3/7/9; keyboard detail, pan/zoom/reset, runtime empty and cross-employee denial verified. Screenshot saved. REA source-study ID and pinned upstream documented in `docs/EMPLOYEE_GRAPH.md`.
  - Limits: local synthetic provenance only, not live Hindsight or semantic inference. Demo actor selection is not production auth. Existing `test_shell.py` first regression pass appended runtime drafts; evidence unchanged, later regression isolated and runtime hash unchanged. Details/disclosure in graph doc. No dependency installed.

- [x] **REF-006 — Demo packaging**
  - Files: `docs/DEMO.md` (rewritten: current-UI-accurate click-by-click incl. hints/coverage/degraded/`/tkt3`, 11-shot video shot list aligned to research beat structure 0:30 problem → live → safety → limitations, claim boundary verbatim), `README.md` (validate-command block with expected outputs, route list completed: `/tkt3`, conversations/responses/review/hr/hints/settings routes, demo pointer), `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 demo_scenario.py` (exit 0, `DEMO_OK full scenario reproduced over HTTP`; all 13 expect-lines green: server up → contribution → peer feedback → review view → cited summary → provisional rating coverage=100 → response linked, original untouched → classify `partially_accepted` → employee finalize 403 → manager finalize → HR audit evidence=3 relations=1 history=2 → settings masked `********`); live server on :8131 verified DEMO.md steps 1–12: `/` 200, `/tkt3` 200 rendering "12/12 test cases passed", `/api/settings` masked `********`; `python3 run_checks.py` (exit 0); `python3 test_ui.py` (exit 0, `UI_SMOKE_OK`, 31 checks).
  - Output: DEMO.md matches the shipped UI exactly (hints card, coverage %, finalize ack, degraded banner, `/tkt3` step); scripted demo reproduces every documented step over real HTTP without error; README routes list is complete and accurate. Architecture diagram already existed (`docs/architecture.svg`, EVE-010).
  - Limitations: video itself not recorded on this host (no headless Chrome; shot list is the storyboard); classify step in browser flow reachable via review screen per REF-001 click-through. No dependency installed.

- [x] **REF-002 — Citation coverage gate**
  - Files: `governance.py` (`validate_citations` coverage semantics, coverage persisted, finalize gate), `test_governance.py` (7 new assertions), `static/app.js` (coverage shown post-record), `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_governance.py` (exit 0); `python3 run_checks.py` (exit 0); `python3 test_ui.py` (exit 0, `UI_SMOKE_OK`); `python3 tkt3_runner.py` (exit 0, 12/12); `node --check static/app.js` (exit 0).
  - Output: claims with neither `evidenceId` nor `quote` are flagged `unsupported` (indexes reported) with coverage % — fabricated citations (wrong quote / unknown ID) still hard-rejected. Coverage stored on review record (`citation_coverage`, `unsupported_claims`); manager response carries notice; UI shows `citation coverage: N%`; finalizing below 100% coverage requires explicit acknowledgment. Tests cover uncited-claim flag + gate rejection.
  - Limitations: coverage is per-claim citation presence, not semantic faithfulness (noted in LIMITATIONS). No dependency installed.

- [x] **REF-001 — Browser demo UI**
  - Files: `static/index.html`, `static/app.js`, `static/styles.css`, `server.py` (static routes), `test_ui.py`, `test_shell.py` (updated for client-rendered shell), `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_ui.py` (exit 0, `UI_SMOKE_OK`, 21 checks); `node --check static/app.js` (`APP_JS_PARSE_OK`); `python3 run_checks.py` (exit 0, all checks); live browser click-through on `http://127.0.0.1:8123/` (Chromium via browser tool): contribution → confirm → peer feedback → confirm → employee response (disputed, linked) → manager review → cited summary (3 claims) → provisional rating → classify response → finalize → HR audit (finalized, evidence=3 relations=1 events=6).
  - Output: full scenario completes in real browser by clicking only; canonical order verified by `runtime_state.json` timestamps (response 19:45:06 < provisional 19:45:07 < final 19:45:18). Fixed real bug found by browser run: `static/app.js` line 242 contained corrupted `apiKey: screen...lue` (would crash page at parse time; HTTP smoke test could not catch it) — repaired, `node --check` green. Fixed provenance wart: role switch now syncs demo actor ID per role (`DEFAULT_IDS`), so audit history records manager-001/hr-001, not stale emp-004. HR audit with non-HR actor correctly shows rejection message.
  - Limitations: single-page demo flow, no routing; role/actor switch resets capture form. No dependency installed.

### BLOCKED

- [ ] **EVE-B01 — Fresh DB validation**
  - Blocker: missing `pg0` dependency/environment.
  - Rule: do not install blindly; resolve only if required by final prototype.

### DONE

- [x] Research-backed appraisal flow saved in `research/performance-appraisal-flow.md`.
- [x] Wayfinder business decisions recorded in `WAYFINDER_MAP.md` and `tickets/01–26`.
- [x] Structured evidence/query PoC and tests exist.
- [x] `tkt3_validation_spec.md` created.
- [x] **EVE-001 — Freeze product contract** — `PRODUCT_CONTRACT.md` created; contract acceptance criteria recorded above.
- [x] **EVE-002 — Create runnable prototype shell**
  - Files: `server.py`, `README.md`, `.env.example`, `.gitignore`, `test_shell.py`, `worker_status.md`, `KANBAN.md`.
  - Commands: `python3 test_shell.py` (exit 0); `python3 test_query_layer.py` (exit 0); `python3 -m py_compile server.py query_layer.py test_shell.py` (exit 0); `python3 -m unittest discover -v` (exit 5, 0 discovered tests).
  - Output: stdlib server starts via `python3 server.py`; mock mode works with no credentials; `/health` returns non-secret mock state; shell and existing query checks pass.
  - Limitations: browser page is a workflow shell; capture/review operations start EVE-003. `unittest discover` is non-gating because checks are executable script files, not unittest cases. No dependency installed.
- [x] **EVE-003 — Build conversational evidence capture**
  - Files: `app_core.py`, `server.py`, `test_conversations.py`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_conversations.py && python3 test_shell.py && python3 test_query_layer.py && python3 -m py_compile app_core.py server.py test_conversations.py test_shell.py` (exit 0).
  - Output: contribution, feedback, and check-in drafts validate structured fields, require confirmation before evidence creation, preserve actor provenance, and require owner/due date/success evidence for check-ins. Missing contribution result returns clarification without evidence save.
  - Limitations: local JSON state is single-process controlled-scenario storage; response workflow starts EVE-004. No dependency installed.
- [x] **EVE-004 — Build immutable evidence and linked responses**
  - Files: `app_core.py`, `server.py`, `test_responses.py`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_responses.py && python3 test_conversations.py && python3 test_shell.py && python3 test_query_layer.py && python3 -m py_compile app_core.py server.py test_responses.py` (exit 0).
  - Output: employee responses become confirmed linked evidence; original remains unchanged; relationship retained; peer cannot see response; employee and manager can. Unauthorized peer response rejected.
  - Limitations: response manager classification starts EVE-005. No dependency installed.
- [x] **EVE-005 — Build manager review and cited summary**
  - Files: `governance.py`, `server.py`, `test_governance.py`, `run_checks.py`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 run_checks.py && python3 -m py_compile app_core.py governance.py server.py` (exit 0).
  - Output: cited summary claims validate against stored evidence IDs and exact quotes; fabricated or missing citations rejected; manager-only rating recording; provisional rating history append-only with before/after/actor/timestamp/reason; employee response classification recorded with reason.
  - Limitations: finalization authorization rules completed in EVE-006. No dependency installed.
- [x] **EVE-006 — Build HR audit and authorization**
  - Files: `governance.py`, `server.py`, `test_governance.py`, `run_checks.py`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 run_checks.py && python3 -m py_compile app_core.py governance.py server.py` (exit 0).
  - Output: employee and HR cannot finalize; manager finalization requires prior provisional rating, rationale, and explicit acknowledgment plus rationale when unresolved disagreement exists; HR audit view returns evidence, relations, review, and event history; rating history preserves before/after/actor/timestamp/reason.
  - Limitations: unresolved-dispute finalization records `acknowledged_unresolved` flag but no separate HR alert surface. No dependency installed.
- [x] **EVE-007 — Add real AI adapter and citation gate**
  - Files: `ai_adapter.py`, `server.py`, `test_ai_adapter.py`, `run_checks.py`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_ai_adapter.py && python3 run_checks.py && python3 -m py_compile ai_adapter.py server.py test_ai_adapter.py` (exit 0).
  - Output: stdlib urllib OpenAI-compatible adapter; deterministic mock default with identical citation validation; real output parsed and citation-gated (wrong quote, missing evidence ID, non-JSON, empty claims all rejected); provider failure degrades to mock leaving raw evidence usable; connection test never echoes the key.
  - Limitations: no live provider run on this host (no credentials); adapter proven against local failing/mocked HTTP server. No dependency installed.
- [x] **EVE-008 — Add configuration panel**
  - Files: `settings_store.py`, `server.py`, `test_settings.py`, `test_shell.py`, `run_checks.py`, `.gitignore`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 run_checks.py` (exit 0; all seven check scripts pass) ; `python3 -m py_compile app_core.py governance.py server.py settings_store.py ai_adapter.py test_settings.py test_shell.py` (exit 0).
  - Output: server-side settings at `POST /api/settings` (provider, baseUrl, chatModel, embeddingModel, apiKey, temperature, tokenLimit, enabled); `GET /api/settings` returns masked view (`apiKey: "********"`); masked echo keeps stored secret; file persisted `0600` (gitignored `runtime_*.json`); stored settings override `.env` defaults via `effective_config`; `/api/ai/test` uses merged config and never echoes key; `/health` and conversation flows verified free of key material; unknown setting keys rejected.
  - Limitations: panel is API + shell-page note (no rich browser form UI); no live provider test on this host. No dependency installed.
- [x] **EVE-009 — Run TKT 3 validation**
  - Files: `tkt3_runner.py`, `tkt3_results.json`, `TKT3_REPORT.md`, `tkt3_logs/tkt3-run-2026-10-15T192134.json`, `tkt3_logs/tkt3-run-2026-10-15T192210.json`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 tkt3_runner.py` (exit 0, 12/12 PASS); full pass `python3 tkt3_runner.py && python3 run_checks.py && python3 test_ai_adapter.py && python3 -m py_compile tkt3_runner.py server.py settings_store.py app_core.py governance.py ai_adapter.py` (exit 0, FULL_VALIDATION_OK).
  - Output: all 12 spec test cases pass against controlled synthetic fixture (emp-004 Dewi Nugraha, Q3–Q4 2026, self/peer/manager). Acceptance: 12/12; citation validity 100%; cross-employee leakage 0; original evidence mutation 0; unauthorized finalization 0 successful attempts. Machine-readable results + transcript in `tkt3_results.json`; human report `TKT3_REPORT.md`.
  - Limitations: single-process JSON store; mock AI only on this host (real provider proven by stubbed HTTP contract tests); synthetic data only; TKT3-05 observed that employee-authored check-in/response rows carry rater role `employee` — recorded as designed provenance labeling.
- [x] **EVE-010 — Package demo and freeze release**
  - Files: `demo_scenario.py`, `docs/DEMO.md`, `docs/architecture.svg`, `docs/LIMITATIONS.md`, `gen_manifest.py`, `release_manifest.json`, `take_screenshots.py`, `server.py` (bug fix), `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 demo_scenario.py` (exit 0, `DEMO_OK full scenario reproduced over HTTP`); `python3 run_checks.py` (exit 0); `python3 gen_manifest.py` (25 artifacts sha256); `python3 take_screenshots.py` (exit 0, SKIP: no Chrome on host).
  - Output: one-command full-scenario demo over real HTTP (capture→review→response→classify→finalize→audit→masked settings); judge-flow demo script; SVG architecture diagram; limitations doc; sha256 manifest with binding claim line. Fixed live bug found by demo run: `server.py` missing `effective_config` import crashed `/api/review/summary-draft` (RemoteDisconnected) — imported, route now returns cited claims.
  - Limitations: no headless Chrome on this VPS — `take_screenshots.py` skips gracefully; browser screenshots fall to REF-001 UI work with the interactive browser tool. No dependency installed.

### DONE (refinement, cont.)

- [x] **REF-009 — Caldera UI refinement**
  - Files: `DESIGN.md`, `static/styles.css`, `static/index.html`, `static/graph.html`, `static/graph.js`, `static/app.js`, `server.py`, `test_ui.py`, self-hosted Anton/DM Sans WOFF2 + OFL licenses, `research/anti-slop/` task-local upstream snapshots + license, `docs/CALDERA_UI.md`, `docs/caldera_ui_checks.txt`, `docs/screenshots/caldera_graph_desktop.png`, `caldera_graph_mobile.png`, `caldera_workspace_desktop.png`, refreshed `tkt3_results.json` + timestamped `tkt3_logs/` runs.
  - Commands: `python3 run_checks.py`, `python3 test_graph.py`, `python3 test_ui.py`, `python3 test_ai_adapter.py`, `python3 tkt3_runner.py`, `python3 demo_scenario.py`, `node --check static/app.js`, `node --check static/graph.js`: all exit 0, final regression after UI fixes. UI smoke 34 checks; demo 13 checks; TKT3 12/12. Exact output in `docs/caldera_ui_checks.txt`.
  - Browser: fresh isolated :8159, 57 saved records. Research 24 evidence/37 nodes/72 links, Q4 collaboration 3/7/9; graph select/list/keyboard/filter/zoom/reset/pan/role/scope-denial/empty states exercised. Capture/discard/confirm, check-in, peer feedback, employee dispute, cited manager draft/edit/remove/rating, unresolved acknowledgment/finalize, HR audit, settings save/test and TKT3 trajectory exercised. Graph/workspace/review/TKT3 widths 320/768/1280 no page horizontal overflow. Screenshot vision inspection found source option clipping and small-graph label omission; fixed, recaptured. Final desktop no blocking clipping/overlap; mobile complete readable inspector/list.
  - Safety: profile scratch TMPDIR/state/settings isolated, original runtime/settings SHA-256 unchanged across regression. No npm installer, dependency, global preference, AGENTS or plugin modification. Fonts self-hosted Latin WOFF2, SIL OFL attribution. Proprietary PP font unavailable; Anton substitute disclosed. Contrast computed (Obsidian/Ember 6.06:1); zero shadows; body/navigation/buttons DM Sans 500.
  - Limits: local synthetic graph, not live Hindsight; demo actor controls not production auth. Dense mobile SVG uses zoom and complete accessible list fallback. No physical keyboard/device or screen-reader/axe audit. Native prompt return stubbed to exercise claim edit; prompt chrome not inspected. Active demo server `proc_96efbfd234ba`, PID 556781, `http://127.0.0.1:8159/graph?employee=emp-004&source=research`, isolated profile scratch. Delivery gate item-by-item and decision reasons in `docs/CALDERA_UI.md`.

- [x] **REF-011 — Hindsight constellation nodes/links, light Caldera graph area**
  - Files: `static/graph.js`, `static/graph.html`, `static/styles.css`, `test_graph.py`, `docs/CALDERA_UI.md`, `KANBAN.md`, `docs/screenshots/graph_constellation_desktop.png`, `docs/screenshots/graph_constellation_mobile.png`; refreshed `tkt3_results.json` and timestamped `tkt3_logs/` runs.
  - Design correction honored: Limestone light canvas/card, not dark; Hindsight dot/link design only. Seeded frozen force layout, pinned Ember employee, Obsidian evidence, outlined Sulfur competency, warm-gray rater; per-stored-type neutral curves, Plasma responses only; subtle static glow, hover/selection feedback, no idle animation. Apache-2.0 adaptation attribution in JS, upstream pinned commit in UI doc.
  - Commands, isolated `EVIDENCEFLOW_STATE_FILE`/`EVIDENCEFLOW_AI_SETTINGS_FILE`/`TMPDIR` under profile scratch `evidenceflow-ref011`: `node --check static/graph.js` exit 0; `python3 test_graph.py` exit 0 (`GRAPH_HTTP_OK`, `GRAPH_CHECKS_OK`, served canvas/light BG/toggle/attribution/DPR/seed assertions); `python3 run_checks.py` exit 0 (`all local checks passed`); `python3 test_ui.py` exit 0 (`UI_SMOKE_OK`, 36 checks); `python3 tkt3_runner.py` exit 0 (`Total: 12/12 passed`, final log `tkt3-run-2026-10-16T072953.json`). Runtime state/settings SHA-256 unchanged: `fac8537efeaffb1e3c3470fa7f22deb9ad683fe34332f30033d55e34bf612ef3`, `f467feabc83ae2f46af71b77e7f4a71571eed06374f29b167d968b99a63e1acb`.
  - Real browser :8167: 24 evidence/37 nodes/72 links; default labels on, desktop 37 shown; toggle 37→13→37; hover highlight, click exact quote/date/rater inspector, canvas arrow/Enter/Space selection; zoom buttons/wheel, drag pan, reset, deterministic layout repeat and DPR=2 backing store verified. Filter Q4-2026 collaboration 3 evidence/7 nodes/9 links/7 labels. Widths 320/768/1280 no document horizontal overflow. No captured JS error events. Screenshots vision-verified light card, colored dots, no blocking clipping.
  - Limits: synthetic only, not live Hindsight; demo identity controls not production auth. Dense overview has some label-to-node ambiguity; 320px deconfliction shows 19/37 labels, zoom/full node list preserves access. No screen-reader/physical-device/axe audit; contextual faint links not WCAG certified. No dependency added. Loopback demo launch: `EVIDENCEFLOW_PORT=8167 EVIDENCEFLOW_STATE_FILE=/opt/data/profiles/code-assistant/cache/scratch/evidenceflow-ref011/browser-state.json EVIDENCEFLOW_AI_SETTINGS_FILE=/opt/data/profiles/code-assistant/cache/scratch/evidenceflow-ref011/browser-settings.json python3 server.py` from repo. Background process `proc_64fd4e0106dc` (session lifetime only).

- [x] **REF-010 — Graph readability pass (labels + calm canvas)**
  - Files: `static/graph.js`, `static/graph.html`, `static/styles.css`, `test_graph.py`, `test_ui.py`, `KANBAN.md`, `docs/CALDERA_UI.md`, `docs/screenshots/graph_readability_desktop.png`, `docs/screenshots/graph_readability_mobile.png`.
  - Commands (isolated env: `EVIDENCEFLOW_STATE_FILE`/`EVIDENCEFLOW_AI_SETTINGS_FILE`/`TMPDIR` in profile scratch `evidenceflow-ref010`): `node --check static/graph.js` exit 0; `python3 test_graph.py` exit 0 (`GRAPH_HTTP_OK`, `GRAPH_CHECKS_OK`, now asserts served graph.js keeps `setLabels`/`labelsOn`/`STYLES`/`BASE_EDGE`); `python3 test_ui.py` exit 0, `UI_SMOKE_OK` 36 checks (2 new: toggle present/on by default, h1 tamed); `python3 run_checks.py` exit 0 `all local checks passed`; `python3 tkt3_runner.py` exit 0 12/12; runtime files SHA-256 unchanged across full suite (`runtime_state.json` `fac8537…`, `runtime_ai_settings.json` `f467feab…`).
  - Browser (Chromium :8161, isolated): 24 evidence/37 nodes/72 labels all visible by default; global `#labels` toggle → "Show labels" hides evidence labels only, non-evidence stay, aria-pressed honest, selection keeps Ember fill; keyboard Enter selects; hover exit no longer hides labels; selection dims unrelated nodes (opacity .55) with softened focus edges (#54524d 1.5 / dim #d5d3cf); 3-evidence filter (Q4-2026+collaboration) 7 nodes/7 labels; runtime empty-state intact; widths 320/768/1280 no horizontal overflow; two vision screenshot passes caught + fixed: rater label collision (upper-half label flip), inspector `angle:`/`row:` debug leak, oversized inspector heading, black 24-spoke wheel, faint dimmed labels.
  - Limits: SVG labels 12–14px; at 320px native they are small (zoom + global toggle + complete node list are fallbacks; no per-node auto-hiding by design). Loopback server dies with session; relaunch: `cd /opt/data/research/evidenceflow-poc && EVIDENCEFLOW_PORT=8161 EVIDENCEFLOW_STATE_FILE=<scratch>/state.json EVIDENCEFLOW_AI_SETTINGS_FILE=<scratch>/ai_settings.json python3 server.py`. Synthetic events, not native keyboard chrome.

### DONE (refinement, cont.)

- [x] **REF-007 — Final executable acceptance**
  - Files: `ACCEPTANCE.md`, `tkt3_results.json` (fresh run), `tkt3_logs/tkt3-run-2026-10-15T203100.json`, `KANBAN.md`, `worker_status.md`.
  - Commands (all exit 0 unless noted): `python3 server.py` on :8131 (`/health` 200 `mode=mock`); `python3 run_checks.py`; `python3 tkt3_runner.py` (fresh 12/12, `TKT3_VALIDATION_OK`); `python3 demo_scenario.py` (13 ok-lines, `DEMO_OK`); `python3 test_ui.py` (31 checks, `UI_SMOKE_OK`); `python3 test_ai_adapter.py`; `node --check static/app.js`; secret scan `grep -rE "sk-[A-Za-z0-9]{16,}"` → no matches (only test placeholders `"***"`, `sk-degraded`).
  - Output: `ACCEPTANCE.md` records all 7 POLISH_PLAN success criteria green with real captured output: server+health 200; run_checks all suites; TKT3 12/12 with acceptance metrics `citationValidity 100%`, `crossEmployeeLeakage 0`, `originalEvidenceMutation 0`, `unauthorizedFinalizations 0`; full browser click-through + scripted HTTP reproduction; masked settings with zero credentials; DEMO.md 1:1 reproducible; no secrets, no mutation, citations 100%.
  - Limitations: unchanged from component tasks — single-process JSON store, mock AI on this host (provider proven by contract tests, no credentials), synthetic data; EVE-B01 (pg0) remains optional/blocked, not required.

- [x] **REF-005 — AI-assisted feedback hints (advisory only)**
  - Files: `ai_adapter.py` (`feedback_hints`, `_mock_hints`, rubric), `server.py` (`POST /api/feedback/hints`), `static/app.js` (hints render on feedback form AND travel onto confirmation card as `#c-hints`; submission never blocked), `test_ai_adapter.py` (mock determinism, thin/empty/rich rubric, provider failure → mock, live valid JSON, malformed JSON → mock), `test_ui.py` (3 endpoint checks in UI smoke), `README.md`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_ai_adapter.py` (exit 0); `python3 test_ui.py` (exit 0, `UI_SMOKE_OK`, hints checks green); `python3 run_checks.py` (exit 0); `python3 demo_scenario.py` (exit 0, `DEMO_OK`); `python3 tkt3_runner.py` (exit 0, 12/12); `node --check static/app.js` (exit 0); live browser click-through on `http://127.0.0.1:8127/` (peer → Give feedback thin draft → hints visible on confirm card → Confirm & save → evidence `ev-0cdd72f1809a` created; rich draft → "Rubric looks good (advisory).").
  - Output: rubric hints (specific / behavioral / impact) advisory only; deterministic in mock; provider failure degrades to mock hints with degraded state; never gates the draft, never rates. Live browser run caught real bug: hints were written to `#f-msg` then wiped when the confirmation card replaced the form — fixed by carrying `hintText` into `showConfirmation` (`#c-hints`).
  - Limitations: mock hints are heuristic (word-count + field presence), not semantic. No dependency installed.

- [x] **REF-004 — TKT3 trajectory + results view**
  - Files: `tkt3_runner.py` (per-case `case_input` inputs, verdict markers, `trajectory()` grouping), `server.py` (`/tkt3` page, `/api/tkt3` matrix JSON, 404 guidance when results absent), `test_shell.py` (matrix page + API assertions), `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 tkt3_runner.py` (exit 0, 12/12, trajectory in `tkt3_results.json` + `tkt3_logs/tkt3-run-2026-10-15T201535.json`); `python3 test_shell.py` (exit 0); `python3 run_checks.py` (exit 0); `python3 test_ui.py` (exit 0, UI_SMOKE_OK); `python3 -m py_compile server.py tkt3_runner.py test_shell.py` (exit 0); 404 probe with results file moved aside (`/tkt3` + `/api/tkt3` → 404 "No TKT3 results; run python3 tkt3_runner.py", restored after); live browser check `http://127.0.0.1:8124/tkt3` (12/12 matrix, acceptance chips, trajectory toggle expands expected/inputs/observed).
  - Output: every test case carries auditable trajectory (inputs, expected, observed, verdict) grouped by case in `tkt3_results.json.trajectory`; `/tkt3` renders 12/12 matrix with per-case trajectory expansion; `/api/tkt3` exposes the same matrix as JSON. No dependency installed.
  - Limitations: trajectory captures runner-driven inputs (not raw HTTP); page is server-rendered from latest run only.

- [x] **REF-003 — Degraded-mode visibility**
  - Files: `ai_adapter.py` (last_state/reset_state), `server.py` (`aiState` in `/health`, `/api/settings`, summary-draft; reset on settings save), `static/app.js` (live banner), `static/styles.css` (banner states), `static/index.html`, `test_ui.py` (degraded E2E assertions), `README.md`, `KANBAN.md`, `worker_status.md`.
  - Commands: `python3 test_ui.py` (exit 0, UI_SMOKE_OK; includes "degraded after provider failure", "degraded detail present", "no key in degraded state", "back to mock after disable"); `python3 run_checks.py` (exit 0).
  - Output: `/health` carries `aiState {state, detail}`; UI banner shows mock/live/degraded, refreshes every 5s; configured-but-failing provider (baseUrl http://127.0.0.1:9/v1) surfaces `degraded` with reason, mode stays mock, no key material anywhere; disabling AI returns banner to mock. Provider success only sets `live`.
  - Limitations: single-process demo scope; state resets on settings change by design. No dependency installed.


## Refinement (post-core)

Source: `POLISH_PLAN.md`, research: `research/refinement-research.md`.
Success criterion for the whole prototype process: **executable** — every REF task DONE only when its executable check passes on this VPS.

### BACKLOG (refinement)

- [x] REF-001 Browser demo UI — vanilla JS served by server.py; full scenario clickable; DONE when UI smoke test passes.
- [x] REF-002 Citation coverage gate — uncited summary claims flagged, coverage % shown; DONE when governance tests cover it.
- [x] REF-003 Degraded-mode visibility — AI state mock/live/degraded shown in UI+API; DONE when endpoint test passes.
- [x] REF-004 TKT3 trajectory + results view — auditable per-test logs, /tkt3 matrix page; DONE when artifacts exist and page renders.
- [x] REF-005 AI-assisted feedback hints — advisory only, deterministic in mock; DONE when tests pass.
- [x] REF-006 Demo packaging — DEMO.md executed end-to-end, video storyboard, README polish; DONE when demo runs without error.
- [x] REF-007 Final executable acceptance — all success-criterion checks in sequence into ACCEPTANCE.md; DONE when all green with real outputs.

## Dependency graph

```text
EVE-001
  ↓
EVE-002
  ↓
EVE-003 → EVE-004 → EVE-005 → EVE-006
                              ↓
                         EVE-007 → EVE-008
                                      ↓
                                 EVE-009 → EVE-010
```

After EVE-010: REF-001 → REF-002 → REF-003 → REF-004 → REF-005 → REF-006 → REF-007.

## Stop conditions

Stop and mark BLOCKED when:
- product role or evidence semantics conflict with locked Wayfinder decisions;
- a secret would be exposed or persisted insecurely;
- citation verification cannot be made deterministic;
- a test fails and root cause is unknown;
- external AI provider is unavailable (use mock mode, do not weaken evidence rules).
