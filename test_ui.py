"""REF-001 UI smoke test: static assets + full scenario via the exact endpoints the UI calls.

Also verifies: no traversal past static/, no key material in any UI payload,
AI banner state field present. Run: python3 test_ui.py (exit 0 = pass).
"""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

ROOT = Path(__file__).parent
PORT = 8913
BASE = f"http://127.0.0.1:{PORT}"
EMPLOYEE = {"id": "emp-004", "role": "employee"}
PEER = {"id": "peer-001", "role": "peer"}
MANAGER = {"id": "manager-001", "role": "manager"}
HR = {"id": "hr-001", "role": "hr"}
failures = []


def check(label, condition, detail=""):
    print(f"{'ok  ' if condition else 'FAIL'} {label} {detail}")
    if not condition:
        failures.append(label)


def call(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlrequest.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode("utf-8"), response.headers.get("Content-Type", "")
    except urlerror.HTTPError as error:
        return error.code, error.read().decode("utf-8"), error.headers.get("Content-Type", "")


def jcall(method, path, payload=None):
    status, raw, _ = call(method, path, payload)
    return status, json.loads(raw)


def main():
    with tempfile.TemporaryDirectory() as workdir:
        env = dict(os.environ, EVIDENCEFLOW_PORT=str(PORT), EVIDENCEFLOW_STATE_FILE=str(Path(workdir) / "ui_state.json"))
        server = subprocess.Popen([sys.executable, str(ROOT / "server.py")], env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(50):
                try:
                    call("GET", "/health")
                    break
                except Exception:
                    time.sleep(0.2)

            # Static assets the UI loads.
            status, raw, ctype = call("GET", "/")
            check("index served", status == 200 and "text/html" in ctype and "app.js" in raw)
            status, raw, ctype = call("GET", "/app.js")
            check("app.js served", status == 200 and "text/javascript" in ctype)
            check("no secret in app.js", "sk-" not in raw and "EVIDENCEFLOW_AI_API_KEY" not in raw)
            status, _, ctype = call("GET", "/styles.css")
            check("styles served", status == 200 and "text/css" in ctype)
            for font in ("anton-latin.woff2", "dm-sans-500-latin.woff2"):
                with urlrequest.urlopen(BASE + "/static/" + font) as response:
                    check("self-hosted font " + font, response.status == 200 and response.read(4) == b"wOF2")
            status, raw, _ = call("GET", "/graph?employee=emp-004")
            check("graph accessible inspector and fallback", status == 200 and 'id="detail"' in raw and 'id="node-list"' in raw and 'class="skip"' in raw)
            check("graph labels toggle present and on by default", 'id="labels"' in raw and 'aria-pressed="true"' in raw and ">Hide labels<" in raw)
            check("graph h1 tamed for readability", 'class="page-title"' in raw and 'class="graph-page"' in raw)
            status, raw, _ = call("GET", "/static/../runtime_ai_settings.json")
            check("traversal blocked", status == 404)
            status, raw, _ = call("GET", "/static/runtime_state.json")
            check("outside-static blocked", status == 404)

            # Health carries banner state.
            status, health = jcall("GET", "/health")
            check("health has mode", status == 200 and health["mode"] in {"mock", "real"})
            # REF-003: aiState visible pre-config (mock) with no key material.
            check("health aiState mock", health["aiState"]["state"] in {"mock", "live", "degraded"})
            check("aiState carries no key", "apiKey" not in json.dumps(health["aiState"]))

            # REF-005: hints endpoint used by the feedback form; advisory, never blocks.
            status, hints = jcall("POST", "/api/feedback/hints", {"behavior": "late", "impact": ""})
            check("hints endpoint advisory", status == 200 and hints["advisory"] is True and hints["mode"] == "mock")
            check("hints flag missing rubric", hints["missing"] == ["specific", "impact"] and len(hints["hints"]) == 2)
            status, rich_hints = jcall("POST", "/api/feedback/hints", {
                "behavior": "Kept incident context inside own team", "impact": "Dependent team debugged duplicate issue for a day"})
            check("hints clear when rubric met", rich_hints["hints"] == [] and rich_hints["missing"] == [])

            # Employee: contribution quick-reply → form → confirm (UI flow).
            status, draft = jcall("POST", "/api/conversations/contribution/draft", {
                "actor": EMPLOYEE, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
                "situation": "Onboarding stalled", "action": "Paired onboarding sessions",
                "result": "Two engineers shipped first patch in two weeks", "verifier": "PR-41"}})
            check("contribution draft", status == 201 and draft["state"] == "ready_for_confirmation")
            status, confirmed = jcall("POST", "/api/conversations/x/confirm", {"actor": EMPLOYEE, "draftId": draft["draftId"]})
            check("contribution confirmed", status == 201 and confirmed["state"] == "confirmed")

            # Peer: feedback.
            status, draft = jcall("POST", "/api/conversations/feedback/draft", {
                "actor": PEER, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
                "behavior": "Kept incident context inside own team",
                "impact": "Dependent team debugged duplicate issue for a day",
                "feedbackType": "concern", "visibility": "employee_manager_hr"}})
            _, conflicting = jcall("POST", "/api/conversations/x/confirm", {"actor": PEER, "draftId": draft["draftId"]})
            check("peer feedback confirmed", conflicting["state"] == "confirmed")

            # Missing result → clarification message shown in UI, nothing stored.
            status, missing = jcall("POST", "/api/conversations/contribution/draft", {
                "actor": EMPLOYEE, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative",
                "situation": "No result case", "action": "Work only", "verifier": "X"}})
            check("clarification surfaced", status == 422 and missing["state"] == "needs_clarification" and missing["missing"] == ["result"])

            # Manager review + cited summary draft (banner mode mock).
            _, view = jcall("POST", "/api/review/view", {"employeeId": "emp-004"})
            check("review view for UI", view["raterRoles"] == ["peer", "self"])
            status, summary = jcall("POST", "/api/review/summary-draft", {"employeeId": "emp-004"})
            check("summary for UI", status == 200 and summary["mode"] == "mock" and all(c.get("evidenceId") and c.get("quote") for c in summary["claims"]))
            # REF-003: summary-draft carries aiState so the UI banner/notice can show it.
            check("summary carries aiState", summary["aiState"]["state"] in {"mock", "live", "degraded"})
            status, rating = jcall("POST", "/api/review/rating", {"actor": MANAGER, "employeeId": "emp-004",
                "summary": summary["claims"], "rationale": "UI smoke rationale", "rating": "meets"})
            check("rating recorded", status == 201 and rating["state"] == "recorded")

            # Employee responds (dispute) then manager classifies.
            status, draft = jcall("POST", "/api/responses/draft", {"actor": EMPLOYEE, "payload": {
                "originalEvidenceId": conflicting["evidence"]["id"], "response": "Context was shared in #inc-77.",
                "source": "Slack export", "relationship": "disputed"}})
            _, resp = jcall("POST", "/api/conversations/x/confirm", {"actor": EMPLOYEE, "draftId": draft["draftId"]})
            check("response confirmed", resp["state"] == "confirmed")
            status, classified = jcall("POST", "/api/review/classify-response", {"actor": MANAGER, "employeeId": "emp-004",
                "responseEvidenceId": resp["evidence"]["id"], "classification": "partially_accepted", "reason": "Late but real."})
            check("classify works", status == 201 and classified["state"] == "recorded")

            # Employee finalize → rejected message; manager finalize → ok.
            status, denied = jcall("POST", "/api/review/finalize", {"actor": EMPLOYEE, "employeeId": "emp-004", "rationale": "x"})
            check("employee finalize rejected for UI", status == 403 and denied["state"] == "rejected")
            status, final = jcall("POST", "/api/review/finalize", {"actor": MANAGER, "employeeId": "emp-004", "rationale": "UI smoke final."})
            check("manager finalize", status == 200 and final["state"] == "finalized")

            # HR audit renders data.
            status, audit = jcall("POST", "/api/hr/audit", {"actor": HR, "employeeId": "emp-004"})
            check("hr audit for UI", status == 200 and audit["review"]["finalized"] is True and audit["relations"])

            # Settings save keeps key masked in every response the UI sees.
            _, saved = jcall("POST", "/api/settings", {"apiKey": "sk-ui-secret", "chatModel": "ui-model"})
            _, seen = jcall("GET", "/api/settings")
            check("masked key in UI path", saved["settings"]["apiKey"] == "********" and seen["apiKey"] == "********")
            check("no key echo anywhere", "sk-ui-secret" not in json.dumps([health, view, summary, audit, seen]))
            # Cleanup stored test config so later runs stay mock.
            jcall("POST", "/api/settings", {"enabled": False, "apiKey": "", "chatModel": "", "baseUrl": ""})

            # REF-003 end-to-end: configured-but-failing provider must surface degraded, never silent live.
            jcall("POST", "/api/settings", {"enabled": True, "apiKey": "sk-degraded-test", "baseUrl": "http://127.0.0.1:9/v1", "chatModel": "down-model"})
            _, summary_dg = jcall("POST", "/api/review/summary-draft", {"employeeId": "emp-004"})
            _, health_dg = jcall("GET", "/health")
            check("degraded after provider failure", summary_dg["mode"] == "mock" and health_dg["aiState"]["state"] == "degraded")
            check("degraded detail present", bool(health_dg["aiState"]["detail"]))
            check("no key in degraded state", "sk-degraded-test" not in json.dumps([summary_dg, health_dg]))
            jcall("POST", "/api/settings", {"enabled": False, "apiKey": "", "chatModel": "", "baseUrl": ""})
            _, health_after = jcall("GET", "/health")
            check("back to mock after disable", health_after["aiState"]["state"] == "mock")

            if failures:
                print(f"UI smoke FAILED: {failures}")
                return 1
            print("UI_SMOKE_OK")
            return 0
        finally:
            server.send_signal(signal.SIGTERM)
            server.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
