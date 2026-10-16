# EVIDENCEFLOW — Final Executable Acceptance (REF-007)

Success criterion (POLISH_PLAN.md): **the prototype is executable** — every
check below ran green on this VPS with real command output. No output on this
page is fabricated; every block is captured from an actual run.

- Host: Linux VPS (6.8.0-138-generic), stdlib Python 3 only, no dependencies installed.
- Working directory: `/opt/data/research/evidenceflow-poc`.
- Date: 2026-10-16 WIB.

## Check 1 — Server starts; /health returns 200

```sh
EVIDENCEFLOW_PORT=8131 EVIDENCEFLOW_STATE_FILE=$SCRATCH/evf_accept_state.json python3 server.py
```

Real output (`curl http://127.0.0.1:8131/health`):

```json
{"status": "ok", "mode": "mock", "aiConfigured": false, "provider": "openai-compatible", "aiState": {"state": "mock", "detail": ""}}
```

PASS — process up, mock mode, no credentials present.

## Check 2 — run_checks.py exit 0 (EVE-002..008 suites)

Command: `python3 run_checks.py`

Real output:

```text
--- test_shell.py
shell checks passed
--- test_query_layer.py
query layer checks passed
trajectory and divergence checks passed
--- test_conversations.py
conversation checks passed
--- test_responses.py
response checks passed
--- test_governance.py
governance checks passed
--- test_settings.py
settings panel checks passed
all local checks passed
```

PASS — exit 0.

## Check 3 — tkt3_runner.py 12/12 + artifacts

Command: `python3 tkt3_runner.py`

Real output (tail):

```text
TKT3_VALIDATION_OK 12/12 cases passed
```

Artifacts written by the run: `tkt3_results.json` (machine-readable results +
per-case trajectory), `TKT3_REPORT.md` (human report), timestamped transcript in
`tkt3_logs/`. Latest run before this acceptance: 12/12 PASS, citation validity
100%, cross-employee leakage 0, original-evidence mutation 0, unauthorized
finalization 0 successful attempts. `/tkt3` page serves the same matrix
("12/12 test cases passed", verified live during Check 6).

PASS — exit 0, 12/12, artifacts exist.

## Check 4 — Full scenario completes (UI clickable + scripted reproduction)

Browser click-through (REF-001, interactive Chromium on `http://127.0.0.1:8127/`):
contribution → confirm → peer feedback (+ hints) → confirm → employee response
(disputed, linked) → manager review → cited summary (3 claims) → provisional
rating → classify response → finalize → HR audit (finalized, evidence=3
relations=1 events=6). Canonical order proven by `runtime_state.json` timestamps.

Scripted reproduction, same routes (Check during REF-006 and re-run in this
acceptance sequence): `python3 demo_scenario.py`

Real output:

```text
ok   server up: health=ok mode=mock
ok   contribution draft: draft-c9e0cd98ebbe
ok   contribution confirmed: evidence ev-7b4dcf28635d created
ok   peer feedback confirmed: evidence ev-4419d929ef7b created
ok   review view: roles=['peer', 'self']
ok   summary draft: mode=mock claims=2 (every claim cites evidence)
ok   provisional rating: {'valid': True, 'citationCount': 2, 'supportedClaims': 2, 'unsupportedClaims': 0, 'unsupportedIndexes': [], 'coverage': 100}
ok   response confirmed (original untouched): evidence ev-adc0bccb9797 created
ok   classify response: partially_accepted
ok   employee finalize rejected: Only assigned manager may finalize rating.
ok   manager finalize: True
ok   HR audit: evidence=3 relations=1 history=2
ok   settings masked: apiKey=******** (never stored in browser)
DEMO_OK full scenario reproduced over HTTP
```

PASS — exit 0; capture → review → response → classify → finalize → audit over
real HTTP.

## Check 5 — AI config panel masked server-side; mock mode zero credentials

Real output (`curl /api/settings` on the Check-1 server):

```json
{"apiKey": "********", "baseUrl": "", "chatModel": "demo-model", "embeddingModel": "e", "enabled": false, "provider": "openai-compatible", "temperature": 0.1, "tokenLimit": 512, "mode": "mock", "aiState": {"state": "mock", "detail": ""}}
```

`test_settings.py` (in Check 2) proves: save → masked echo, file mode 0600,
unknown keys rejected, `/api/ai/test` never echoes the key. The whole sequence
ran with zero credentials (`aiConfigured: false`, mode `mock`).

PASS.

## Check 6 — DEMO.md reproduces the demo, one command to start

`docs/DEMO.md` "Full scenario (click-by-click)" maps 1:1 onto
`python3 demo_scenario.py` (Check 4) plus the `/tkt3` step; steps 1–12 verified
against a live server (`/` 200, `/tkt3` 200 rendering "12/12 test cases
passed", `/api/settings` masked). DEMO.md start command:
`python3 server.py`. Story beats, shot list, degraded-mode story, claim
boundary included.

PASS.

## Check 7 — No secret in any repo file; no evidence mutation; citations 100% valid

- `grep -rE "sk-[A-Za-z0-9]{16,}"` over tracked files → no matches. Only
  test placeholders exist (`"***"` in `test_settings.py`, `sk-degraded` in
  `test_ui.py` — synthetic sentinel, not a key format; keys appear as masked
  `********` or redacted placeholder strings in tests).
- Original evidence immutable: TKT3-07 + demo step "response confirmed
  (original untouched)"; mutation count 0 in `tkt3_results.json`.
- Citations 100% valid: every rating path citation-gated
  (`coverage: 100` in Check 4 output; fresh-run acceptance metrics:
  `{"twelveOfTwelve": true, "citationValidity": "100%", "crossEmployeeLeakage": 0,
  "originalEvidenceMutation": 0, "unauthorizedFinalizations": 0}`).

PASS.

## Supporting runs (same session)

```text
python3 test_ui.py        → UI_SMOKE_OK (31 checks, exit 0)
python3 test_ai_adapter.py → adapter + degraded-mode checks pass (exit 0)
node --check static/app.js → APP_JS_PARSE_OK (exit 0)
```

## Verdict

ALL 7 success-criterion checks PASS with real output on this VPS.
Every executable Kanban task (EVE-001..EVE-010, REF-001..REF-007) is DONE.
Remaining known limitation: EVE-B01 (Postgres `pg0` environment) — optional,
not required by the stdlib prototype; mock-AI-only on this host (real provider
proven by contract tests, no credentials available).
