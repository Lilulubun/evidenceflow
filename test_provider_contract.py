import json
import os
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from ai_adapter import AIUnavailableError, StructuredExtractionError, extract_conversation
from settings_store import effective_config


def test_provider_config_is_system_wide_and_missing_config_fails_closed():
    env = {"enabled": False, "baseUrl": "", "chatModel": "", "apiKey": "", "temperature": 0, "tokenLimit": 1024}
    config = effective_config(env)
    assert config["provider"] == "openai-compatible"
    try:
        extract_conversation(config, "checkin", "progress: done")
    except AIUnavailableError:
        pass
    else:
        raise AssertionError("unconfigured production extraction must fail closed")


def test_provider_structured_extraction_requires_exact_source_anchors():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"choices": [{"message": {"content": json.dumps({"fields": [{"name": "progress", "value": "done", "source": "progress: done"}]})}}]}).encode())
        def log_message(self, *_): pass
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        config = {"enabled": True, "provider": "openai-compatible", "baseUrl": f"http://127.0.0.1:{httpd.server_port}/v1", "chatModel": "test", "apiKey": "test", "temperature": 0, "tokenLimit": 256}
        result = extract_conversation(config, "checkin", "progress: done")
        assert result == {"progress": "done"}
    finally:
        httpd.shutdown()
