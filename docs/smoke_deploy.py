"""Native startup/persistence smoke of Dockerfile runtime files; no Docker substitute.

Run from repository root: python3 docs/smoke_deploy.py
Uses TMPDIR (set it to a writable scratch directory); never reads local .env/state.
"""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory(prefix="evidenceflow-deploy-") as temporary:
    work = Path(temporary)
    app, data = work / "app", work / "data"
    app.mkdir()
    data.mkdir(mode=0o700)
    # Test exact runtime file list copied by Dockerfile, not whole checkout.
    dockerfile = (ROOT / "Dockerfile").read_text()
    runtime = next(line.split()[1:-1] for line in dockerfile.splitlines()
                   if line.startswith("COPY server.py "))
    for name in runtime:
        shutil.copy2(ROOT / name, app / name)
    shutil.copytree(ROOT / "static", app / "static")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("EVIDENCEFLOW_")}
    env.update(EVIDENCEFLOW_HOST="0.0.0.0", EVIDENCEFLOW_PORT=str(port),
               EVIDENCEFLOW_STATE_FILE=str(data / "runtime_state.json"),
               EVIDENCEFLOW_AI_SETTINGS_FILE=str(data / "runtime_ai_settings.json"),
               PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    base = f"http://127.0.0.1:{port}"

    def call(path, payload=None):
        raw = None if payload is None else json.dumps(payload).encode()
        req = Request(base + path, data=raw,
                      headers={} if raw is None else {"Content-Type": "application/json"})
        with urlopen(req, timeout=5) as response:
            body = response.read()
            assert response.status == 200 or response.status == 201
            return json.loads(body) if "application/json" in response.headers["Content-Type"] else body

    def start():
        proc = subprocess.Popen([sys.executable, "server.py"], cwd=app, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        assert proc.stderr is not None
        for _ in range(100):
            if proc.poll() is not None:
                raise RuntimeError(proc.stderr.read().decode())
            try:
                assert call("/health")["status"] == "ok"
                return proc
            except OSError:
                time.sleep(0.05)
        proc.terminate()
        proc.wait(timeout=10)
        raise RuntimeError("Server health timeout")

    def stop(proc):
        proc.terminate()
        proc.wait(timeout=10)
        proc.stderr.close()

    actor = {"id": "emp-004", "role": "employee"}
    graph = {"employeeId": "emp-004", "actor": actor, "source": "runtime"}
    proc = start()
    try:
        assert call("/health")["aiState"]["state"] == "mock"
        for route in ("/", "/app.js", "/styles.css", "/static/dm-sans-500-latin.woff2",
                      "/graph?employee=emp-004", "/graph.js", "/tkt3"):
            assert call(route), route
        assert call("/api/tkt3")["totals"]["total"] == 12
        assert call("/api/settings")["mode"] == "mock"
        assert call("/api/graph", graph)["evidenceCount"] == 0
        assert call("/api/graph", {**graph, "source": "research"})["evidenceCount"] > 0
        print("PASS health/workspace/static/graph/settings/tkt3; runtime empty, research fixture present")
        draft = call("/api/conversations/contribution/draft", {"actor": actor, "payload": {
            "employeeId": "emp-004", "period": "Q4-2026", "competency": "collaboration",
            "situation": "Controlled deployment smoke", "action": "Checked persistence",
            "result": "Synthetic capture survives restart", "verifier": "deployment-smoke"}})
        confirmed = call("/api/conversations/x/confirm", {"actor": actor, "draftId": draft["draftId"]})
        assert confirmed["state"] == "confirmed"
        evidence_id = confirmed["evidence"]["id"]
        assert call("/api/settings", {"enabled": False, "chatModel": "smoke-only"})["state"] == "saved"
        assert (data / "runtime_ai_settings.json").stat().st_mode & 0o777 == 0o600
    finally:
        stop(proc)
    proc = start()
    try:
        view = call("/api/graph", graph)
        assert view["evidenceCount"] == 1
        assert any(node.get("evidenceId") == evidence_id for node in view["nodes"])
        assert call("/api/settings")["chatModel"] == "smoke-only"
        assert len(json.loads((data / "runtime_state.json").read_text())["evidence"]) == 1
        print("PASS confirmed synthetic evidence + AI settings survive process restart; settings mode 0600")
    finally:
        stop(proc)
print("DEPLOY_SMOKE_OK native Python; container build/UID/volume/proxy still require Docker host")
