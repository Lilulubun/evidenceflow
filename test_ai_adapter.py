"""Runnable EVE-007 checks: mock default, citation gate on real-shaped output, failure degradation."""
import json
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import request as urlrequest

from ai_adapter import AIError, ai_config, discover_models, draft_summary, mock_summary, parse_real_summary, test_connection
from app_core import Store

employee = {"id": "emp-004", "role": "employee"}
with tempfile.TemporaryDirectory() as directory:
    storage = Store(Path(directory) / "state.json")
    original_draft = storage.create_draft("contribution", employee, {"employeeId": "emp-004", "period": "Q4-2026", "competency": "initiative", "situation": "Release risk", "action": "Coordinated fix", "result": "Release completed", "verifier": "PR-18"})
    original = storage.confirm_draft(original_draft["draftId"], employee)["evidence"]
    rows = [row for row in storage.snapshot()["evidence"] if row["data"].get("employee_id") == "emp-004"]

    # Mock default without credentials.
    assert ai_config({}) is False
    assert discover_models({})["reason"] == "AI provider is not configured."
    claims, mode = draft_summary({}, rows)
    assert mode == "mock" and claims == mock_summary(rows)

    # Real-shaped valid output passes identical gate.
    valid = json.dumps({"claims": [{"text": "Claim", "evidenceId": original["id"], "quote": "Release completed"}]})
    parsed = parse_real_summary(valid, rows)
    assert parsed[0]["evidenceId"] == original["id"]

    # OpenAI-compatible content arrays accepted.
    array_content = {"choices": [{"message": {"content": [{"type": "text", "text": "part one"}, {"text": " part two"}]}}]}
    from ai_adapter import _completion_content, _sse_completion_content
    assert _completion_content(array_content, {"baseUrl": "https://router.example/v1", "chatModel": "model"}, 200, "application/json") == "part one part two"
    assert _completion_content({"output_text": "response text"}, {}, 200, "application/json") == "response text"
    assert _completion_content({"output": [{"content": [{"text": "output text"}]}]}, {}, 200, "application/json") == "output text"
    event_sse = b'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"event text"}\n\ndata: [DONE]\n'
    assert _sse_completion_content(event_sse, {}, 200, "text/event-stream") == "event text"
    try:
        _completion_content({"output": [{"type": "function_call", "name": "tool"}]}, {}, 200, "application/json")
        raise AssertionError("tool-only response accepted")
    except AIError as error:
        assert "reasoning/tool calls only" in str(error)

    # SSE chunks accumulate delta, message, and legacy text content.
    from ai_adapter import _sse_completion_content
    sse = b"data: {\"choices\":[{\"delta\":{\"content\":\"part \"}}]}\n\ndata: {\"choices\":[{\"message\":{\"content\":\"two\"}}]}\n\ndata: {\"choices\":[{\"text\":\"!\"}]}\n\ndata: [DONE]\n"
    assert _sse_completion_content(sse, {"baseUrl": "https://router.example", "chatModel": "model"}, 200, "text/event-stream") == "part two!"
    try:
        _sse_completion_content(b"data: not-json\ndata: [DONE]\n", {"baseUrl": "https://router.example", "chatModel": "model"}, 200, "text/event-stream")
        raise AssertionError("malformed stream accepted")
    except AIError as error:
        assert "Provider stream contained no message content" in str(error)

    # Fabricated citation rejected.
    for bad in (
        json.dumps({"claims": [{"text": "Claim", "evidenceId": original["id"], "quote": "Fabricated"}]}),
        json.dumps({"claims": [{"text": "Claim", "evidenceId": "ev-missing", "quote": "Release completed"}]}),
        "not json at all",
        json.dumps({"claims": []}),
    ):
        try:
            parse_real_summary(bad, rows)
            raise AssertionError("fabricated output accepted")
        except AIError:
            pass

    # Provider failure degrades to mock; raw evidence untouched.
    class FakeHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", "0")))
            self.send_response(500)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    failing_config = {"enabled": True, "apiKey": "secret", "baseUrl": f"http://127.0.0.1:{server.server_port}", "chatModel": "test-model", "temperature": 0, "tokenLimit": 64}
    degraded, degraded_mode = draft_summary(failing_config, rows)
    assert degraded_mode == "mock" and degraded == mock_summary(rows)
    connection = test_connection(failing_config)
    assert connection["ok"] is False and "secret" not in json.dumps(connection)
    server.shutdown()

    # REF-003: degraded state recorded and visible; detail never contains the key.
    from ai_adapter import last_state
    state = last_state()
    assert state["state"] == "degraded" and state["detail"] and "secret" not in state["detail"]
    # Successful real-shaped provider call records live state.
    class OkHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            claim = json.loads(body)["messages"][0]["content"]
            catalog = json.loads(claim.split("Catalog: ", 1)[1])
            row = catalog[0]
            payload = json.dumps({"choices": [{"message": {"content": json.dumps({"claims": [
                {"text": "Live claim", "evidenceId": row["evidenceId"], "quote": row["quote"]}]})}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_):
            pass

    ok_server = ThreadingHTTPServer(("127.0.0.1", 0), OkHandler)
    threading.Thread(target=ok_server.serve_forever, daemon=True).start()
    live_config = {**failing_config, "baseUrl": f"http://127.0.0.1:{ok_server.server_port}"}
    live_claims, live_mode = draft_summary(live_config, rows)
    assert live_mode == "real" and last_state()["state"] == "live"
    ok_server.shutdown()

    # REF-005: feedback hints — advisory, deterministic in mock, never gating/rating.
    from ai_adapter import feedback_hints
    thin = {"behavior": "late", "impact": ""}
    hints, hints_mode = feedback_hints({}, thin)
    assert hints_mode == "mock" and hints["advisory"] is True
    assert hints["missing"] == ["specific", "impact"]  # one-word behavior: specific; empty impact
    assert hints == feedback_hints({}, thin)[0]  # deterministic in mock
    empty = {"behavior": "", "impact": ""}
    assert feedback_hints({}, empty)[0]["missing"] == ["specific", "behavioral", "impact"]
    rich = {"behavior": "Rejected schema change without escalation on sprint 12", "impact": "Migration slipped five days"}
    good_hints, good_mode = feedback_hints({}, rich)
    assert good_mode == "mock" and good_hints["hints"] == []
    # Provider failure: hints degrade to deterministic mock, advisory stays true.
    fail_hints, fail_mode = feedback_hints(failing_config, thin)
    assert fail_mode == "mock" and fail_hints == hints and fail_hints["advisory"] is True
    # Live provider returning valid hints JSON is used; malformed JSON degrades to mock.
    class HintHandler(BaseHTTPRequestHandler):
        content = ""
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.dumps({"choices": [{"message": {"content": HintHandler.content}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        def log_message(self, *_):
            pass
    hint_server = ThreadingHTTPServer(("127.0.0.1", 0), HintHandler)
    threading.Thread(target=hint_server.serve_forever, daemon=True).start()
    hint_config = {**failing_config, "baseUrl": f"http://127.0.0.1:{hint_server.server_port}"}
    HintHandler.content = json.dumps({"missing": ["impact"], "hints": ["Say what slipped."]})
    live_hints, live_hint_mode = feedback_hints(hint_config, thin)
    assert live_hint_mode == "real" and live_hints["missing"] == ["impact"] and live_hints["advisory"] is True
    HintHandler.content = "total nonsense"
    junk_hints, junk_mode = feedback_hints(hint_config, thin)
    assert junk_mode == "mock" and junk_hints == hints
    hint_server.shutdown()
print("ai adapter checks passed")
