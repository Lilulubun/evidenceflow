"""Stdlib-only EVIDENCEFLOW controlled-scenario server."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ai_adapter import AIError, discover_models, draft_summary as ai_draft_summary
from ai_adapter import feedback_hints, last_state, test_connection
from app_core import Store
from chat import create_session, get_session, message as chat_message, confirm as chat_confirm, SYSTEM_PROMPT
from employee_graph import employee_graph
from governance import classify_response, create_or_update_review, draft_summary, finalize_review, hr_audit, review_view
from query_layer import query
from settings_store import effective_config, masked_settings, save_settings
from ai_adapter import reset_state as ai_reset_state

ROOT = Path(__file__).parent


def load_env(path=ROOT / ".env"):
    """Load local key=value configuration; .env never leaves this process."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key and not key.startswith("#"):
            os.environ.setdefault(key, value)


def settings():
    load_env()
    enabled = os.getenv("EVIDENCEFLOW_AI_ENABLED", "false").lower() == "true"
    has_key = bool(os.getenv("EVIDENCEFLOW_AI_API_KEY"))
    return {"mode": "real" if enabled and has_key else "unavailable", "aiConfigured": enabled and has_key, "provider": os.getenv("EVIDENCEFLOW_AI_PROVIDER", "openai-compatible")}


def read_ai_config():
    """Stored server-side settings override .env defaults; secret never leaves the server."""
    load_env()
    env_defaults = {
        "enabled": os.getenv("EVIDENCEFLOW_AI_ENABLED", "false").lower() == "true",
        "baseUrl": os.getenv("EVIDENCEFLOW_AI_BASE_URL", ""),
        "chatModel": os.getenv("EVIDENCEFLOW_AI_CHAT_MODEL", ""),
        "apiKey": os.getenv("EVIDENCEFLOW_AI_API_KEY", ""),
        "temperature": float(os.getenv("EVIDENCEFLOW_AI_TEMPERATURE", "0")),
        "tokenLimit": int(os.getenv("EVIDENCEFLOW_AI_TOKEN_LIMIT", "1024")),
        "fixtureMode": False,
    }
    return effective_config(env_defaults)


def store():
    return Store(os.getenv("EVIDENCEFLOW_STATE_FILE", str(ROOT / "runtime_state.json")))


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, body):
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
            self.send_json(415, {"error": {"code": "UNSUPPORTED_MEDIA_TYPE", "message": "Content-Type must be application/json"}})
            return None
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": {"code": "INVALID_JSON", "message": "Request body must be JSON"}})
            return None
        if not isinstance(payload, dict):
            self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "Request body must be an object"}})
            return None
        return payload

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/graph":
            self._send_static("graph.html", "text/html; charset=utf-8")
        elif path == "/graph.js":
            self._send_static("graph.js", "text/javascript; charset=utf-8")
        elif path == "/":
            self._send_static("index.html", "text/html; charset=utf-8")
        elif path.startswith("/static/"):
            self._send_static(path[len("/static/"):], None)
        elif path == "/app.js":
            self._send_static("app.js", "text/javascript; charset=utf-8")
        elif path == "/styles.css":
            self._send_static("styles.css", "text/css; charset=utf-8")
        elif path == "/tkt3":
            self._send_tkt3()
        elif path == "/api/tkt3":
            self._api_tkt3()
        elif path == "/health":
            self.send_json(200, {"status": "ok", **settings(), "aiState": last_state()})
        elif path.startswith("/api/chat/session/"):
            sid = path.rsplit("/", 1)[-1]; session = get_session(store(), sid)
            self.send_json(200, {"sessionId": sid, "events": session["events"]} if session else {"error": {"code": "NOT_FOUND", "message": "Unknown session"}})
        elif path == "/api/chat/policy":
            self.send_json(200, {"systemPrompt": SYSTEM_PROMPT, "eventTypes": sorted(__import__('chat').EVENT_TYPES)})
        elif path == "/api/settings":
            view = masked_settings()
            view["mode"] = settings()["mode"]
            view["aiState"] = last_state()
            self.send_json(200, view)
        else:
            self.send_json(404, {"error": {"code": "NOT_FOUND", "message": "Unknown route"}})

    def _load_tkt3(self):
        """REF-004: load the latest TKT3 results; never expose secrets (none stored)."""
        path = ROOT / "tkt3_results.json"
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _api_tkt3(self):
        data = self._load_tkt3()
        if data is None:
            self.send_json(404, {"error": {"code": "NOT_FOUND", "message": "No TKT3 results; run python3 tkt3_runner.py"}})
            return
        totals = data.get("totals", {})
        self.send_json(200, {
            "runStartedAt": data.get("runStartedAt"),
            "runFinishedAt": data.get("runFinishedAt"),
            "fixture": data.get("fixture"),
            "totals": totals,
            "acceptance": data.get("acceptance"),
            "results": data.get("results", []),
        })

    def _send_tkt3(self):
        """REF-004: server-rendered /tkt3 matrix page (stdlib html assembly only)."""
        data = self._load_tkt3()
        if data is None:
            self.send_json(404, {"error": {"code": "NOT_FOUND", "message": "No TKT3 results; run python3 tkt3_runner.py"}})
            return
        import html as html_mod

        def esc(value):
            return html_mod.escape(str(value), quote=True)

        rows = []
        for result in data.get("results", []):
            pill = "ok" if result.get("pass") else "bad"
            verdict = "PASS" if result.get("pass") else "FAIL"
            observed = json.dumps(result.get("observed", {}), ensure_ascii=False)
            traj = data.get("trajectory", {}).get(result["id"], {})
            inputs = json.dumps(traj.get("inputs", []), ensure_ascii=False)
            detail_id = f"detail-{esc(result['id'])}"
            rows.append(
                f"<tr><td><code>{esc(result['id'])}</code></td>"
                f"<td>{esc(result.get('function', ''))}</td>"
                f"<td><span class='pill {pill}'>{verdict}</span></td>"
                f"<td><button onclick=\"var d=document.getElementById('{detail_id}');d.hidden=!d.hidden;\">trajectory</button></td></tr>"
                f"<tr id='{detail_id}' hidden><td colspan='4'><div class='claim'><div><b>expected:</b> {esc(result.get('expected', ''))}</div>"
                f"<div><b>inputs:</b> <code>{esc(inputs)}</code></div>"
                f"<div><b>observed:</b> <code>{esc(observed)}</code></div></div></td></tr>"
            )
        totals = data.get("totals", {})
        acceptance = data.get("acceptance", {})
        acc_items = "".join(f"<span class='chip'>{esc(key)}: {esc(value)}</span>" for key, value in acceptance.items())
        page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EVIDENCEFLOW TKT3 results</title>
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header><a class="brand" href="/">EVIDENCEFLOW</a><nav aria-label="Pages"><a href="/">Workspace</a><a href="/graph?employee=emp-004">Employee graph</a></nav><span class="banner mock">Controlled synthetic scenario</span></header>
<main>
<div class="page-intro"><div><h1>TKT 3 validation</h1><p>Critical functions, recorded outcomes.</p></div><div class="signature" aria-hidden="true"></div></div>
<p class="muted">Run {esc(data.get("runStartedAt", "?"))} → {esc(data.get("runFinishedAt", "?"))}.
Fixture: {esc(data.get("fixture", {}).get("employee", "?"))} ({esc(data.get("fixture", {}).get("employeeId", "?"))}),
periods {esc(", ".join(data.get("fixture", {}).get("periods", [])))}. Synthetic data only.</p>
<div class="card">
<h2>{esc(totals.get("passed", 0))}/{esc(totals.get("total", 0))} test cases passed</h2>
<p>{acc_items}</p>
<table>
<tr><th>Case</th><th>Function</th><th>Verdict</th><th>Trajectory</th></tr>
{''.join(rows)}
</table>
</div>
<p class="muted">{esc(data.get("claimBoundary", ""))}</p>
</main>
</body>
</html>"""
        raw = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_static(self, name, content_type):
        """Serve static/ files only; no traversal, no secrets (runtime files live outside static/)."""
        target = (ROOT / "static" / name).resolve()
        if target.parent != (ROOT / "static").resolve() or not target.is_file():
            self.send_json(404, {"error": {"code": "NOT_FOUND", "message": "Unknown route"}})
            return
        raw = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_json()
        if body is None:
            return
        if path == "/api/chat/session":
            sid = create_session(store(), body.get("actor"), body.get("kind", "contribution"))
            self.send_json(201 if sid else 422, {"sessionId": sid, "events": get_session(store(), sid)["events"]} if sid else {"error": {"code": "VALIDATION_ERROR", "message": "valid actor required"}})
            return
        if path == "/api/chat/message":
            result = chat_message(store(), body.get("sessionId"), body.get("message"))
            self.send_json(200 if result and result.get("state") != "error" else 422, result or {"error": {"code": "NOT_FOUND", "message": "Unknown session"}})
            return
        if path == "/api/chat/confirm":
            result = chat_confirm(store(), body.get("sessionId"))
            self.send_json(201 if result.get("state") == "confirmed" else 403, result)
            return
        if path == "/api/graph":
            status, result = employee_graph(store(), body)
            self.send_json(status, result)
            return
        if path == "/evidence/query":
            if not isinstance(body.get("query"), str) or not body["query"].strip():
                self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "query must be non-empty string"}})
                return
            try:
                self.send_json(200, query(body["query"], person_id=body.get("personId"), rater_roles=body.get("raterRoles"), quarter=body.get("quarter"), competency=body.get("competency"), limit=body.get("limit", 5)))
            except Exception:
                self.send_json(500, {"error": {"code": "INTERNAL_ERROR", "message": "Query failed"}})
            return
        parts = path.strip("/").split("/")
        actor = body.get("actor") if isinstance(body.get("actor"), dict) else None
        if path == "/api/review/view":
            if not isinstance(body.get("employeeId"), str):
                self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "employeeId required"}})
                return
            self.send_json(200, review_view(store(), body["employeeId"]))
            return
        if path == "/api/review/summary-draft":
            if not isinstance(body.get("employeeId"), str):
                self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "employeeId required"}})
                return
            view = review_view(store(), body["employeeId"])
            evidence_rows = [row for row in store().snapshot()["evidence"] if row["data"].get("employee_id") == body["employeeId"]]
            try:
                claims, mode = ai_draft_summary(read_ai_config(), evidence_rows)
            except AIError as error:
                self.send_json(503, {"error": {"code": "AI_UNAVAILABLE", "message": error.reason}, "aiState": last_state()})
                return
            self.send_json(200, {"claims": claims, "mode": mode, "aiState": last_state(), "notice": "AI-assisted draft; manager must edit and own the rating."})
            return
        if path == "/api/settings":
            result = save_settings(body)
            if result["state"] == "saved":
                ai_reset_state()  # config changed: stale degraded/live flag no longer meaningful
            self.send_json(200 if result["state"] == "saved" else 422, result)
            return
        if path == "/api/ai/test":
            self.send_json(200, test_connection(read_ai_config()))
            return
        if path == "/api/ai/models":
            self.send_json(200, discover_models(read_ai_config()))
            return
        if path == "/api/feedback/hints":
            # REF-005: advisory hints only; never gates the draft, never rates.
            hints, mode = feedback_hints(read_ai_config(), body if isinstance(body, dict) else {})
            self.send_json(200, {**hints, "mode": mode})
            return
        if path == "/api/review/rating":
            if not actor:
                self.send_json(403, {"error": {"code": "FORBIDDEN", "message": "actor required"}})
                return
            result = create_or_update_review(store(), actor, body.get("employeeId"), body.get("summary"), body.get("rationale"), body.get("rating"), provisional=body.get("provisional", True))
            self.send_json(201 if result["state"] == "recorded" else 403, result)
            return
        if path == "/api/review/classify-response":
            if not actor:
                self.send_json(403, {"error": {"code": "FORBIDDEN", "message": "actor required"}})
                return
            result = classify_response(store(), actor, body.get("employeeId"), body.get("responseEvidenceId"), body.get("classification"), body.get("reason"))
            self.send_json(201 if result["state"] == "recorded" else 403, result)
            return
        if path == "/api/review/finalize":
            if not actor:
                self.send_json(403, {"error": {"code": "FORBIDDEN", "message": "actor required"}})
                return
            result = finalize_review(store(), actor, body.get("employeeId"), body.get("rationale"), acknowledge_unresolved=bool(body.get("acknowledgeUnresolved")))
            self.send_json(200 if result["state"] == "finalized" else 403, result)
            return
        if path == "/api/hr/audit":
            if not actor:
                self.send_json(403, {"error": {"code": "FORBIDDEN", "message": "actor required"}})
                return
            result = hr_audit(store(), actor, body.get("employeeId"))
            self.send_json(200 if result["state"] == "ok" else 403, result)
            return
        if len(parts) == 4 and parts[:2] == ["api", "conversations"] and parts[3] == "draft":
            actor, payload = body.get("actor"), body.get("payload")
            if not isinstance(actor, dict):
                self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "actor object required"}})
                return
            result = store().create_draft(parts[2], actor, payload)
            self.send_json(201 if result["state"] == "ready_for_confirmation" else 422, result)
            return
        if len(parts) == 3 and parts == ["api", "responses", "draft"]:
            actor, payload = body.get("actor"), body.get("payload")
            if not isinstance(actor, dict):
                self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "actor object required"}})
                return
            result = store().create_response_draft(actor, payload)
            self.send_json(201 if result["state"] == "ready_for_confirmation" else 422, result)
            return
        if len(parts) == 4 and parts[:2] == ["api", "conversations"] and parts[3] == "confirm":
            actor = body.get("actor")
            if not isinstance(actor, dict) or not isinstance(body.get("draftId"), str):
                self.send_json(422, {"error": {"code": "VALIDATION_ERROR", "message": "actor and draftId required"}})
                return
            result = store().confirm_draft(body["draftId"], actor)
            self.send_json(201 if result["state"] == "confirmed" else 403, result)
            return
        self.send_json(404, {"error": {"code": "NOT_FOUND", "message": "Unknown route"}})

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    host = os.getenv("EVIDENCEFLOW_HOST", "127.0.0.1")
    port = int(os.getenv("EVIDENCEFLOW_PORT", "8000"))
    print(f"EVIDENCEFLOW listening on http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
