"""Runnable checks for EVE-002 shell."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).parent


def boot(port=8765):
    """Start server subprocess for checks; returns (proc, base_url, health)."""
    proc = subprocess.Popen([sys.executable, "server.py"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ, "EVIDENCEFLOW_PORT": str(port)})
    base = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            with urlopen(base + "/health", timeout=0.3) as response:
                health = json.load(response)
            break
        except OSError:
            time.sleep(0.1)
    else:
        proc.terminate()
        raise AssertionError("server did not become healthy")
    return proc, base, health


if __name__ == "__main__":
    proc, base, health = boot()
    try:
        assert health["status"] == "ok" and health["mode"] == "unavailable" and health["aiConfigured"] is False
        assert health["aiState"]["state"] in {"unavailable", "mock", "live", "degraded"}  # REF-003 visibility field
        # REF-004: /tkt3 matrix page renders runner results; /api/tkt3 serves the matrix JSON.
        with urlopen(base + "/tkt3", timeout=1) as response:
            tkt3_page = response.read().decode()
        assert "TKT3-01" in tkt3_page and "TKT3-12" in tkt3_page and "PASS" in tkt3_page
        assert f"{health.get('tkt3', {}).get('passed', 12)}/12" in tkt3_page or "12/12" in tkt3_page
        with urlopen(base + "/api/tkt3", timeout=1) as response:
            matrix = json.load(response)
        assert matrix["totals"]["passed"] == 12 and len(matrix["results"]) == 12
        with urlopen(base + "/", timeout=1) as response:
            page = response.read().decode()
        assert "KerjaKita AI" in page and "app.js" in page
        # Quick-reply labels render client-side from app.js (REF-001), so assert there.
        app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        assert "Add contribution" in app_js and "Confirm" in app_js
        print("shell checks passed")
    finally:
        proc.terminate()
        proc.wait(timeout=3)
        assert proc.returncode is not None
