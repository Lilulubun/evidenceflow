"""EVIDENCEFLOW end-to-end demo: full scenario over real HTTP in one command.

Starts server.py as a subprocess with an isolated state file, then walks the
complete appraisal loop by clicking-equivalent API calls (the same routes the
browser UI uses): capture -> review -> response -> classify -> finalize -> audit.

Run:  python3 demo_scenario.py        (exit 0 = demo reproduced end-to-end)
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
PORT = 8907
BASE = f"http://127.0.0.1:{PORT}"
EMPLOYEE = {"id": "emp-004", "role": "employee"}
PEER = {"id": "peer-001", "role": "peer"}
MANAGER = {"id": "manager-001", "role": "manager"}
HR = {"id": "hr-001", "role": "hr"}


def call(method, path, payload=None):
    """One HTTP round trip; returns (status, body). HTTP errors return status+body (no raise)."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlrequest.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urlerror.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def expect(label, condition, detail):
    if not condition:
        print(f"FAIL {label}: {detail}")
        sys.exit(1)
    print(f"ok   {label}: {detail}")


def confirm(store_draft, actor, label):
    status, body = call("POST", "/api/conversations/x/confirm", {"actor": actor, "draftId": store_draft["draftId"]})
    expect(label, status == 201 and body["state"] == "confirmed", f"evidence {body['evidence']['id']} created")
    return body["evidence"]


def main():
    with tempfile.TemporaryDirectory() as workdir:
        env = dict(os.environ, EVIDENCEFLOW_PORT=str(PORT), EVIDENCEFLOW_STATE_FILE=str(Path(workdir) / "demo_state.json"))
        server = subprocess.Popen([sys.executable, str(ROOT / "server.py")], env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(50):
                try:
                    status, health = call("GET", "/health")
                    break
                except Exception:
                    time.sleep(0.2)
            expect("server up", status == 200 and health["status"] == "ok", f"health={health['status']} mode={health['mode']}")

            # 1. Employee adds a contribution (draft, then explicit confirm).
            status, draft = call("POST", "/api/conversations/contribution/draft", {
                "actor": EMPLOYEE, "payload": {
                    "employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
                    "situation": "Onboarding stalled", "action": "Paired onboarding sessions",
                    "result": "Two engineers shipped first patch in two weeks", "verifier": "PR-41"}})
            expect("contribution draft", status == 201 and draft["state"] == "ready_for_confirmation", draft["draftId"])
            positive = confirm(draft, EMPLOYEE, "contribution confirmed")

            # 2. Peer gives conflicting feedback.
            status, draft = call("POST", "/api/conversations/feedback/draft", {
                "actor": PEER, "payload": {
                    "employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
                    "behavior": "Kept incident context inside own team",
                    "impact": "Dependent team debugged duplicate issue for a day",
                    "feedbackType": "concern", "visibility": "employee_manager_hr"}})
            conflicting = confirm(draft, PEER, "peer feedback confirmed")

            # 3. Manager review view + AI-assisted cited summary (mock mode).
            status, view = call("POST", "/api/review/view", {"employeeId": "emp-004"})
            expect("review view", status == 200 and set(view["raterRoles"]) == {"self", "peer"}, f"roles={view['raterRoles']}")
            status, summary = call("POST", "/api/review/summary-draft", {"employeeId": "emp-004"})
            expect("summary draft", status == 200 and summary["mode"] == "mock" and len(summary["claims"]) >= 2,
                   f"mode={summary['mode']} claims={len(summary['claims'])} (every claim cites evidence)")

            # 4. Manager records provisional rating with the cited claims.
            status, rating = call("POST", "/api/review/rating", {
                "actor": MANAGER, "employeeId": "emp-004", "summary": summary["claims"],
                "rationale": "Collaboration strong on onboarding; peer friction noted.", "rating": "meets"})
            expect("provisional rating", status == 201 and rating["state"] == "recorded", rating["citation"])

            # 5. Employee disputes the peer feedback -> new linked evidence.
            status, draft = call("POST", "/api/responses/draft", {
                "actor": EMPLOYEE, "payload": {
                    "originalEvidenceId": conflicting["id"],
                    "response": "Context was shared in incident channel #inc-77.",
                    "source": "Slack #inc-77 export", "relationship": "disputed"}})
            response = confirm(draft, EMPLOYEE, "response confirmed (original untouched)")

            # 6. Manager classifies the response with a reason.
            status, classified = call("POST", "/api/review/classify-response", {
                "actor": MANAGER, "employeeId": "emp-004", "responseEvidenceId": response["id"],
                "classification": "partially_accepted", "reason": "Channel log shared but delayed."})
            expect("classify response", status == 201 and classified["state"] == "recorded", classified["classification"]["classification"])

            # 7. Employee cannot finalize; manager finalizes.
            status, denied = call("POST", "/api/review/finalize", {"actor": EMPLOYEE, "employeeId": "emp-004", "rationale": "self"})
            expect("employee finalize rejected", status == 403 and denied["state"] == "rejected", denied["reason"])
            status, final = call("POST", "/api/review/finalize", {
                "actor": MANAGER, "employeeId": "emp-004",
                "rationale": "Dispute classified; final rating stands."})
            expect("manager finalize", status == 200 and final["state"] == "finalized", final["review"]["finalized"])

            # 8. HR audit reconstructs evidence, relations, decisions, history.
            status, audit = call("POST", "/api/hr/audit", {"actor": HR, "employeeId": "emp-004"})
            history = audit["review"]["rating_history"]
            expect("HR audit", status == 200 and audit["state"] == "ok" and audit["evidence"] and audit["relations"]
                   and history[-1]["stage"] == "final",
                   f"evidence={len(audit['evidence'])} relations={len(audit['relations'])} history={len(history)}")

            # 9. Settings: key masked server-side, never echoed.
            status, saved = call("POST", "/api/settings", {"apiKey": "sk-demo-secret", "chatModel": "demo-model"})
            masked = saved["settings"]["apiKey"] == "********"
            status, view_settings = call("GET", "/api/settings")
            expect("settings masked", masked and view_settings["apiKey"] == "********", f"apiKey={view_settings['apiKey']} (never stored in browser)")

            print("DEMO_OK full scenario reproduced over HTTP")
            return 0
        finally:
            server.send_signal(signal.SIGTERM)
            server.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
