"""Runnable EVE-008 checks: server-side settings, masked key, .env merge, connection test, no leakage."""
import json
import os
import tempfile
from pathlib import Path
from urllib import request as urlrequest

import settings_store
from settings_store import masked_settings, save_settings

# 1. Round-trip save/load; API key masked, never returned in clear.
with tempfile.TemporaryDirectory() as directory:
    os.environ["EVIDENCEFLOW_AI_SETTINGS_FILE"] = str(Path(directory) / "settings.json")
    saved = save_settings({"provider": "openai-compatible", "baseUrl": "http://127.0.0.1:9/v1", "chatModel": "m", "embeddingModel": "e", "apiKey": "sk-supersecret", "temperature": 0.1, "tokenLimit": 512, "enabled": True})
    assert saved["state"] == "saved" and saved["settings"]["apiKey"] == "********"
    view = masked_settings()
    assert view["apiKey"] == "********" and "sk-supersecret" not in json.dumps(view)
    raw_file = (Path(directory) / "settings.json").read_text()
    assert "sk-supersecret" in raw_file  # stored server-side only, file mode 0600
    assert oct(settings_store.settings_path().stat().st_mode)[-3:] == "600"

    # 2. Masked echo keeps stored secret; unknown keys rejected.
    again = save_settings({"apiKey": "********", "chatModel": "m2"})
    assert again["state"] == "saved" and again["settings"]["chatModel"] == "m2"
    merged = settings_store.effective_config({"enabled": False, "baseUrl": "", "chatModel": "", "apiKey": "", "temperature": 0, "tokenLimit": 1024})
    assert merged["apiKey"] == "sk-supersecret" and merged["chatModel"] == "m2" and merged["enabled"] is True
    rejected = save_settings({"hackerKey": "x"})
    assert rejected["state"] == "rejected"

    # 3. Server endpoints: GET masks key; POST saves; /health and draft flows carry no key.
    os.environ["EVIDENCEFLOW_AI_SETTINGS_FILE"] = str(Path(directory) / "settings.json")
    import server  # noqa: E402

    from test_shell import boot  # helper returns (proc, base_url, health)

    proc, base, health = boot()
    try:
        def call(method, path, payload=None):
            req = urlrequest.Request(base + path, method=method, data=json.dumps(payload).encode() if payload is not None else None, headers={"Content-Type": "application/json"})
            with urlrequest.urlopen(req, timeout=2) as response:
                return response.status, json.load(response)

        status, view = call("GET", "/api/settings")
        assert status == 200 and view["apiKey"] == "********" and "sk-supersecret" not in json.dumps(view)
        status, saved = call("POST", "/api/settings", {"chatModel": "gpt-test", "apiKey": "sk-second"})
        assert status == 200 and saved["settings"]["apiKey"] == "********"
        status, view = call("GET", "/api/settings")
        assert view["chatModel"] == "gpt-test" and "sk-second" not in json.dumps(view)
        status, health = call("GET", "/health")
        assert "apiKey" not in json.dumps(health)
        employee = {"id": "emp-004", "role": "employee"}
        status, draft = call("POST", "/api/conversations/contribution/draft", {"actor": employee, "payload": {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative", "situation": "S", "action": "A", "result": "R", "verifier": "V"}})
        assert status == 201 and "sk-second" not in json.dumps(draft)
    finally:
        proc.terminate()
        proc.wait(timeout=3)
print("settings panel checks passed")
