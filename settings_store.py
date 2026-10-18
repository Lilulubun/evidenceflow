"""Server-side AI settings storage. API key masked after save; never returned, never in browser storage."""
import json
import os
from pathlib import Path

MASK = "********"
SECRET_KEYS = {"apiKey"}
ALLOWED_KEYS = {"enabled", "provider", "baseUrl", "chatModel", "embeddingModel", "apiKey", "temperature", "tokenLimit", "reasoningEffort", "fixtureMode"}


def settings_path():
    return Path(os.getenv("EVIDENCEFLOW_AI_SETTINGS_FILE", Path(__file__).parent / "runtime_ai_settings.json"))


def load_settings():
    path = settings_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def masked_settings():
    stored = load_settings()
    view = {key: stored.get(key) for key in sorted(ALLOWED_KEYS) if key in stored}
    if view.get("apiKey"):
        view["apiKey"] = MASK
    return view


def save_settings(payload):
    if not isinstance(payload, dict):
        return {"state": "rejected", "reason": "Settings payload must be an object."}
    unknown = set(payload) - ALLOWED_KEYS
    if unknown:
        return {"state": "rejected", "reason": f"Unsupported setting keys: {sorted(unknown)}."}
    stored = load_settings()
    for key, value in payload.items():
        if key in SECRET_KEYS and value == MASK:
            continue  # masked echo: keep stored secret unchanged
        stored[key] = value
    path = settings_path()
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(stored, indent=2), encoding="utf-8")
    temporary.replace(path)
    os.chmod(path, 0o600)
    return {"state": "saved", "settings": masked_settings()}


def effective_config(env):
    """Merge stored settings over .env defaults; secret stays server-side only."""
    stored = load_settings()
    merged = {
        "enabled": bool(stored.get("enabled", env["enabled"])),
        "baseUrl": stored.get("baseUrl") or env["baseUrl"],
        "chatModel": stored.get("chatModel") or env["chatModel"],
        "apiKey": stored.get("apiKey") or env["apiKey"],
        "provider": stored.get("provider", env.get("provider", "openai-compatible")),
        "reasoningEffort": stored.get("reasoningEffort", env.get("reasoningEffort", "medium")),
        "fixtureMode": bool(stored.get("fixtureMode", env.get("fixtureMode", False))),
        "temperature": float(stored.get("temperature", env["temperature"])),
        "tokenLimit": int(stored.get("tokenLimit", env["tokenLimit"])),
    }
    return merged
