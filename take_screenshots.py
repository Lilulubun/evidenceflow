"""EVE-010: render demo screenshots from the running server via headless Chrome.

Produces docs/screenshots/*.png. Skips itself gracefully (prints SKIP reason)
when no Chrome/Chromium binary is available; demo_scenario.py remains the
authoritative executable proof.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib import request as urlrequest

ROOT = Path(__file__).parent
PORT = 8911
BASE = f"http://127.0.0.1:{PORT}"
OUT = ROOT / "docs" / "screenshots"
EMPLOYEE = {"id": "emp-004", "role": "employee"}
PEER = {"id": "peer-001", "role": "peer"}
MANAGER = {"id": "manager-001", "role": "manager"}


def chrome_bin():
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    return None


def call(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlrequest.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urlerror.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def confirm(draft, actor):
    call("POST", "/api/conversations/x/confirm", {"actor": actor, "draftId": draft["draftId"]})


def seed_scenario():
    """Seed the same evidence the demo narrative uses (via the public API)."""
    call("POST", "/api/conversations/contribution/draft", {
        "actor": EMPLOYEE, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
        "situation": "Onboarding stalled", "action": "Paired onboarding sessions",
        "result": "Two engineers shipped first patch in two weeks", "verifier": "PR-41"}})
    draft, _ = call("POST", "/api/conversations/contribution/draft", {
        "actor": EMPLOYEE, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
        "situation": "Onboarding stalled", "action": "Paired onboarding sessions",
        "result": "Two engineers shipped first patch in two weeks", "verifier": "PR-41"}})
    confirm(draft, EMPLOYEE)
    draft, _ = call("POST", "/api/conversations/feedback/draft", {
        "actor": PEER, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
        "behavior": "Kept incident context inside own team",
        "impact": "Dependent team debugged duplicate issue for a day",
        "feedbackType": "concern", "visibility": "employee_manager_hr"}})
    confirm(draft, PEER)


def main():
    chrome = chrome_bin()
    if not chrome:
        print("SKIP: no Chrome/Chromium binary on this host; demo_scenario.py remains executable proof")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as workdir:
        env = dict(os.environ, EVIDENCEFLOW_PORT=str(PORT),
                   EVIDENCEFLOW_STATE_FILE=str(Path(workdir) / "shot_state.json"))
        server = subprocess.Popen([sys.executable, str(ROOT / "server.py")], env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(50):
                try:
                    call("GET", "/health")
                    break
                except Exception:
                    time.sleep(0.2)
            seed_scenario()
            shots = [
                ("01-home", "/", "EVIDENCEFLOW home"),
                ("02-review", f"/#review:{BASE}/api/review/view", "Manager review"),
            ]
            # Render pages headless; the REF-001 UI adds real screens later.
            for name, url, _label in shots:
                target = f"{BASE}/" if url == "/" else url
                subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu",
                                "--screenshot", str(OUT / f"{name}.png"),
                                "--window-size=1280,900", "--virtual-time-budget=4000", target],
                               check=True, timeout=60,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"shot {name}.png")
            return 0
        finally:
            server.send_signal(subprocess.signal.SIGTERM)
            server.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
