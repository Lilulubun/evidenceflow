# REF-008 — Employee provenance graph

## Run

`EVIDENCEFLOW_PORT=8148 python3 server.py`

Open `/graph?employee=emp-004`, choose source explicitly. Or use `/graph?employee=emp-004&source=research` for explicit research source. Existing workspace links to graph. Research fixture has 960 records across employees; emp-004 has 24 records, 37 nodes, 72 links. Runtime currently has no confirmed evidence, so empty state is expected; drafts do not appear.

`POST /api/graph` accepts `{ "employeeId":"emp-004", "source":"research", "actor":{"id":"emp-004","role":"employee"}, "quarter":"", "competency":"" }`. Source is mandatory, never merged. Runtime source reads confirmed evidence and actual stored response relationships. Response quarter/competency inherit original metadata when absent, without writing original state.

## Hindsight source study / REA evidence

Upstream: https://github.com/vectorize-io/hindsight/tree/9a499b1759084a86598eff8af30ed59f7354e76c

Local snapshot: `/opt/data/profiles/code-assistant/cache/scratch/hindsight-graph-source`.
REA `analyze_javascript_application` evidence ID: `ev_152d6f2fdba8d7f36fcb1528f91554b4056c5357eb340186b25baf07525b5420` (parent analysis). Four JS/TS files parsed, zero parse failures. Static evidence only; unresolved semantic relationships are not runtime proof.

- `graph-data.ts`: framework-independent nodes/links; converts API `nodes[].data`, `edges[].data`, joins `table_rows` metadata by ID. Header explicitly says former Cytoscape Graph removed.
- `constellation.tsx`: custom Canvas constellation with pan/zoom, type colors, hover/selection, highlighted links, metadata details.
- `entities-view.tsx`: entity-oriented exploration sharing graph model.
- `route.ts`: server proxy to `/v1/default/banks/{bankId}/graph`, forwards scope/filter params and backend errors.

Adapted concepts, not giant React component: local stdlib API, SVG concentric layout, employee center, evidence/competency/rater types, selection details, hover links, pan/zoom/reset, keyboard nodes and native button fallback. No new dependency, no Hindsight call, no remote modification. Hindsight converter's default semantic edge is deliberately NOT copied. Only has-evidence, competency, rated-by and original stored clarified/disputed/superseded relationships exist.

## Visibility and boundaries

Employee actor can request only own employee ID. Runtime starts from `Store.visible_evidence`, scopes employee before graph construction, additionally enforces stored visibility (`manager_hr`, `hr_only`). Peer sees no response; response requires visible same-employee original. Links require both visible endpoints. All untrusted details rendered with `textContent`/DOM attributes, never HTML insertion. Invalid source/actor/filter types return 422; cross-employee employee request returns 403.

**Demo role/identity controls are not authentication.** Manager/HR visibility inherits broad demo authority; no assignment registry or production authorization exists. Do not expose to untrusted users. Research synthetic records have no visibility policies or stored response links. Graph is local provenance, not semantic knowledge inference, contradiction detection, live Hindsight integration, or production security proof. Dense graphs use filters/list fallback; Canvas needed at larger scale.

## Verification

Full exact command output: `docs/employee_graph_checks.txt`. Seven commands exit 0: `python3 run_checks.py` (includes new graph HTTP + unit assertions), `python3 test_ui.py` (`UI_SMOKE_OK`, 31 checks), `python3 test_ai_adapter.py`, `python3 tkt3_runner.py` (12/12), `python3 demo_scenario.py`, `node --check static/app.js`, `node --check static/graph.js`.

Final regression run uses temporary `EVIDENCEFLOW_STATE_FILE`, runtime hash unchanged. Earlier first regression pass used inherited project state: existing `test_shell.py` created demo drafts in runtime_state.json (confirmed evidence, relations, events remained empty); not graph writes. Existing regression settings tests also reset demo AI settings. Runtime evidence was never edited. No prior snapshot available to safely undo draft side effect; disclosed rather than deleting guessed records.

Real Chromium session `employee-graph`, port 8148: 24 evidence / 37 nodes / 72 links; Q4-2026 + collaboration yields 3 evidence / 7 nodes / 9 links; node keyboard Enter selects exact quote/date/rater; zoom produces scale(1.2), reset restores scale(1); pointer pan changes translation; runtime empty message; employee cross-scope denied. Widths 320/768/1024/1440 checked; mobile overflow found and fixed (final width 320, scrollWidth 305, no overflowing element). Screenshot `docs/screenshots/employee_graph.png` shows evidence ev-00037 detail. Browser screenshot CDP timeout needed retry; native SVG `.click()` unsupported, event dispatch used. No automated screen-reader/axe audit or live Hindsight runtime test.
