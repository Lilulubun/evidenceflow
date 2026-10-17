# EVIDENCEFLOW TKT 3 PoC

Controlled synthetic proof-of-concept for evidence-grounded 360° performance appraisal. Manager decides. AI assists source-linked structure and summaries only. Not production-ready. No fairness or organizational-validity claim.

## Run

```sh
python3 server.py
```

Open `http://127.0.0.1:8000`. Health and runtime-safe setting status: `GET /health`.

## Deploy controlled demo

[Dokploy Application + Dockerfile setup](docs/DEPLOY_DOKPLOY.md) — one non-root container,
persistent named volume, internal port 8000. External access gate required before
publishing: demo roles and settings endpoints are not authentication.

## Validate

```sh
python3 run_checks.py      # EVE-002..008 check scripts
python3 tkt3_runner.py     # TKT 3 validation: 12/12 spec test cases + trajectory log
python3 demo_scenario.py   # full scenario over real HTTP (capture→…→audit→settings)
python3 test_ui.py         # UI smoke test against a live server
python3 test_ai_adapter.py # adapter + degraded-mode checks
```

Expected output ends with:

```text
all local checks passed
TKT3_VALIDATION_OK 12/12 cases passed
DEMO_OK full scenario reproduced over HTTP
```

## Demo

Judges: follow `docs/DEMO.md` — story beats, click-by-click scenario, shot list,
degraded-mode story, and the claim boundary to state verbatim. The browser UI
(`static/`, vanilla JS, no build) walks capture → review → response → classify →
finalize → audit → settings; `/tkt3` renders the validation matrix.

## Configuration

```sh
cp .env.example .env
```

Mock mode is default. No credentials needed. AI state is visible in `GET /health`
(`aiState.state`: `mock` / `live` / `degraded`) and in the UI banner: `live` only
after a real provider answered; a configured provider that fails degrades to
mock and the banner shows `degraded` with the reason — never silent live. Feedback
forms show advisory rubric hints (`POST /api/feedback/hints`: specific / behavioral /
impact); hints never block submission and never rate. `.env` is ignored and is
loaded only by server process. API keys never appear in the browser, endpoint response, fixture, or logs. Real AI fields exist for EVE-007/EVE-008; provider calls are not enabled yet.

## Current routes

- `GET /` — runnable proof shell (browser demo UI).
- `GET /tkt3` — TKT 3 validation matrix (12 test cases, per-case trajectory); 404 until `python3 tkt3_runner.py` has run.
- `GET /health` — process status and non-secret mode.
- `GET /api/settings` — non-secret runtime setting status (masked).
- `POST /evidence/query` — structured existing-evidence retrieval.
- `POST /api/conversations/{kind}/draft` + `POST /api/conversations/x/confirm` — conversational evidence capture.
- `POST /api/responses/draft` — employee response to evidence (new linked evidence, original immutable).
- `POST /api/review/view` / `summary-draft` / `rating` / `classify-response` / `finalize` — manager review flow.
- `POST /api/hr/audit` — HR full reconstruction view.
- `POST /api/feedback/hints` — advisory rubric hints (never gating, never rating).
- `POST /api/settings`, `POST /api/ai/test` — server-side AI config; masked key echo.

## Existing structured evidence baseline

- `evidence.json` — deterministic synthetic evidence dataset.
- `query_layer.py` — entity/rater/period/competency constrained retrieval.
- `schema.sql`, `db_poc.py` — earlier Postgres-compatible experiment; optional dependency environment unavailable, not required by runnable stdlib proof.

## Security boundary

Do not put secrets in source, fixtures, test output, or browser storage. Original evidence and linked-response workflows arrive in EVE-003/EVE-004. No endpoint selects ratings, promotions, or compensation.

## Documentation

Product decisions, research, TKT 3 evidence, and demo materials live in the separate documentation repository:

https://github.com/Lilulubun/evidenceflow-docs

The deployment guide remains in this repository at `docs/DEPLOY_DOKPLOY.md` because it belongs to the executable code release.

## Historical research artifacts

Phase 1–3 retrieval artifacts are maintained in the documentation repository. Current executable checks remain in this repository.
