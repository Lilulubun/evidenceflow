"""Regenerate release_manifest.json: sha256 of shipped artifacts (no runtime/secret files)."""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent
INCLUDE = [
    "PRODUCT_CONTRACT.md", "KANBAN.md", "WAYFINDER_MAP.md", "tkt3_validation_spec.md",
    "README.md", ".env.example", "demo_scenario.py", "take_screenshots.py",
    "server.py", "app_core.py", "governance.py", "ai_adapter.py", "settings_store.py",
    "query_layer.py", "run_checks.py", "tkt3_runner.py",
    "test_shell.py", "test_query_layer.py", "test_conversations.py", "test_responses.py",
    "test_governance.py", "test_settings.py", "test_ai_adapter.py",
    "docs/DEMO.md", "docs/architecture.svg",
]


def main():
    manifest = {"generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "artifactCount": 0, "sha256": {}}
    for name in INCLUDE:
        path = ROOT / name
        if not path.exists():
            print(f"missing: {name}")
            continue
        manifest["sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest["artifactCount"] = len(manifest["sha256"])
    manifest["claim"] = ("Controlled synthetic TKT 3 proof only. Not production-ready; "
                         "no fairness or organizational-validity claim.")
    out = ROOT / "release_manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {out} ({manifest['artifactCount']} artifacts)")


if __name__ == "__main__":
    main()
