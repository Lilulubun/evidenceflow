"""OpenAI-compatible AI adapter. Real AI optional; deterministic mock is default and citation-gated.

Contract (PRODUCT_CONTRACT.md): AI may structure evidence and draft source-linked
summaries. It never selects ratings. Every AI citation must match an existing
evidence ID and exact stored quote or it is rejected.
"""
import json
import logging
import re
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)


def _safe_base_url(value):
    """Return provider origin only; never log path, query, or credentials."""
    try:
        parsed = urlsplit(str(value))
        return f"{parsed.scheme}://{parsed.hostname or ''}" + (f":{parsed.port}" if parsed.port else "")
    except (TypeError, ValueError):
        return "<invalid-url>"


def _redact(value):
    """Remove secret-like values from bounded diagnostics."""
    text = str(value)
    text = re.sub(r"(?i)(bearer\\s+)[^\\s,]+", r"\\1<redacted>", text)
    text = re.sub(r"(?i)(api[_-]?key|authorization|token|secret|password)([=:]\\s*)[^,;\\s]+", r"\\1\\2<redacted>", text)
    return text


def _body_classification(raw):
    """Classify provider body without logging body contents."""
    sample = raw[:512].lstrip()
    if not sample:
        return "empty"
    if sample.startswith((b"data:", b"event:")) or b"\nevent:" in sample:
        return "sse"
    if sample.startswith((b"{", b"[")):
        try:
            value = json.loads(raw.decode("utf-8"))
            return f"json-{type(value).__name__}"
        except (UnicodeDecodeError, json.JSONDecodeError):
            return "json-invalid"
    return "non-json"


def _stream_diagnostic(raw):
    events, data_count, invalid = {}, 0, 0
    current = None
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith("event:"):
            current = line[6:].strip()[:80] or "<unnamed>"
            events[current] = events.get(current, 0) + 1
        elif line.startswith("data:") and line[5:].strip() != "[DONE]":
            data_count += 1
            if current is None:
                events["data"] = events.get("data", 0) + 1
            try:
                json.loads(line[5:].lstrip())
            except json.JSONDecodeError:
                invalid += 1
    return "sse events=" + ",".join(f"{k}:{v}" for k, v in sorted(events.items())[:8]) + f" data={data_count} invalid={invalid}"


def _delta_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("text", "") if isinstance(value.get("text", ""), str) else ""
    return ""


def _log_response(config, status, content_type, body, shape="unknown"):
    logger.warning(
        "AI provider response base_url=%s model=%s status=%s content_type=%s shape=%s body=%s",
        _safe_base_url(config.get("baseUrl")), _redact(config.get("chatModel", "")),
        status, _redact(content_type or ""), _redact(shape), _body_classification(body),
    )


def _text_values(value):
    """Yield message text from common OpenAI and Responses API shapes."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _text_values(item)
    elif isinstance(value, dict):
        for key in ("content", "text", "output_text"):
            if key in value:
                yield from _text_values(value[key])
        for key in ("choices", "delta", "message", "output", "response"):
            if key in value:
                yield from _text_values(value[key])


def _sse_completion_content(raw, config, status, content_type):
    """Consume complete SSE stream; return visible text only."""
    parts, saw_event = [], False
    for line in raw.decode("utf-8", "replace").splitlines():
        if not line.startswith("data:"):
            continue
        data = line[5:].lstrip()
        if data == "[DONE]":
            continue
        saw_event = True
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            continue
        if isinstance(chunk, dict) and chunk.get("type") == "response.output_text.delta":
            parts.append(_delta_text(chunk.get("delta")))
        for choice in chunk.get("choices", []) if isinstance(chunk, dict) else []:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta", {})
            if isinstance(delta, dict):
                parts.append(_delta_text(delta.get("content")))
    text = "".join(parts).strip()
    if text:
        return text
    _log_response(config, status, content_type, raw, _stream_diagnostic(raw) if saw_event else "unknown")
    raise AIError("Provider stream contained no message content (text output absent; reasoning/tool calls only or unsupported SSE shape).")


def _response_completion_content(body, config, status, content_type):
    """Extract text from Responses API JSON without exposing response body."""
    parts = list(_text_values(body))
    text = "".join(parts).strip()
    if text:
        return text
    keys = sorted(str(key) for key in body)[:20] if isinstance(body, dict) else []
    _log_response(config, status, content_type, json.dumps(body).encode(), "json keys=" + ",".join(keys))
    raise AIError("Provider response contained no message content (reasoning/tool calls only or unsupported response shape).")


def _completion_content(body, config, status, content_type):
    """Extract text from chat completions and Responses API JSON."""
    if isinstance(body, dict) and ("choices" not in body or "output" in body or "output_text" in body):
        return _response_completion_content(body, config, status, content_type)
    choices = body.get("choices") if isinstance(body, dict) else None
    if not isinstance(choices, list) or not choices:
        raise AIError("Provider response missing choices.")
    text = "".join(_text_values(choices[0])).strip()
    if text:
        return text
    _log_response(config, status, content_type, json.dumps(body).encode(), "json choices-no-text")
    raise AIError("Provider response missing message content (reasoning/tool calls only or unsupported shape).")

from governance import evidence_quote


class AIError(Exception):
    """Base typed provider error."""
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class AIUnavailableError(AIError):
    pass


class StructuredExtractionError(AIError):
    pass


def extract_conversation(config, kind, text):
    """Extract schema fields only when provider returns exact source anchors."""
    if not ai_config(config):
        raise AIUnavailableError("AI provider is not configured.")
    prompt = {"role": "user", "content": "Extract JSON fields for " + kind + ". Every field must include exact source text. Source: " + text}
    try:
        content = call_chat(config, [prompt])
        parsed = json.loads(re.search(r"\\{.*\\}", content, re.DOTALL).group(0))
        fields = parsed.get("fields")
        if not isinstance(fields, list):
            raise ValueError
        result = {}
        for field in fields:
            if not isinstance(field, dict) or not isinstance(field.get("name"), str) or not isinstance(field.get("value"), str) or not isinstance(field.get("source"), str) or field["source"] not in text:
                raise ValueError
            result[field["name"]] = field["value"]
        return result
    except AIError:
        raise
    except (AttributeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise StructuredExtractionError("Provider output failed schema/source-anchor validation.") from error


# REF-003: last AI call outcome surfaced via /health; degraded means configured
# provider failed and mock output was served instead. Single-process demo scope.
_LAST = {"state": "unavailable", "detail": "AI provider is not configured."}


def last_state():
    return dict(_LAST)


def reset_state():
    """Settings changed: clear stale degraded/live state until the next AI call (REF-003)."""
    global _LAST
    _LAST = {"state": "mock", "detail": ""}


def ai_config(config):
    enabled = bool(config.get("enabled"))
    has_key = bool(config.get("apiKey"))
    ready = enabled and has_key and bool(config.get("baseUrl")) and bool(config.get("chatModel"))
    return ready


def _provider_message(raw):
    try:
        value = json.loads(raw.decode("utf-8", "replace"))
        if isinstance(value, dict):
            error = value.get("error")
            if isinstance(error, dict) and isinstance(error.get("message"), str):
                return _redact(error["message"])[:240]
            if isinstance(value.get("message"), str):
                return _redact(value["message"])[:240]
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    return ""


def discover_models(config, timeout=8):
    """Read OpenAI-compatible /models; return IDs and safe diagnostics only."""
    if not ai_config(config):
        return {"ok": False, "models": [], "reason": "AI provider is not configured."}
    req = urlrequest.Request(config["baseUrl"].rstrip("/") + "/models", headers={"Authorization": f"Bearer {config['apiKey']}"})
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            raw = response.read(65536)
            status, content_type = response.status, response.headers.get("Content-Type", "")
        body = json.loads(raw.decode("utf-8"))
        models = body.get("data") if isinstance(body, dict) else None
        if not isinstance(models, list):
            return {"ok": False, "models": [], "status": status, "reason": "Provider /models response missing data."}
        ids = sorted({item.get("id") for item in models if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")})
        return {"ok": True, "models": ids, "status": status, "contentType": content_type.split(";", 1)[0]}
    except urlerror.HTTPError as error:
        raw = error.read(4096)
        return {"ok": False, "models": [], "status": error.code, "reason": _provider_message(raw) or f"Provider returned HTTP {error.code}."}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"ok": False, "models": [], "status": status if "status" in locals() else None, "reason": "Provider /models response was not valid JSON."}
    except Exception as error:
        return {"ok": False, "models": [], "reason": f"Provider models request failed: {type(error).__name__}"}


def call_chat(config, messages, timeout=15):
    """Blocking OpenAI-compatible /chat/completions call; raises AIError on any failure."""
    if not ai_config(config):
        raise AIError("AI provider is not configured.")
    payload = json.dumps({
        "model": config["chatModel"],
        "messages": messages,
        "temperature": float(config.get("temperature", 0)),
        "max_tokens": int(config.get("tokenLimit", 1024)),
        "stream": True,
        "stream_options": {"include_usage": True},
        "reasoning_effort": config.get("reasoningEffort", "medium"),
    }).encode("utf-8")
    req = urlrequest.Request(
        config["baseUrl"].rstrip("/") + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {config['apiKey']}", "User-Agent": f"EvidenceFlow/{config.get('version', '0.1')}"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            status = response.status
            content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type.lower() or raw.lstrip().startswith(b"data:"):
            return _sse_completion_content(raw, config, status, content_type)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            _log_response(config, status, content_type, raw)
            raise AIError("Provider response was not valid JSON.") from error
        return _completion_content(body, config, status, content_type)
    except urlerror.HTTPError as error:
        raw = error.read(4096)
        _log_response(config, error.code, error.headers.get("Content-Type", ""), raw)
        raise AIError(f"Provider returned HTTP {error.code}.") from error
    except AIError:
        raise
    except Exception as error:  # network failures degrade to mock
        logger.warning("AI provider request failed base_url=%s model=%s error=%s", _safe_base_url(config.get("baseUrl")), _redact(config.get("chatModel", "")), _redact(type(error).__name__))
        raise AIError(f"Provider call failed: {type(error).__name__}") from error


def mock_summary(evidence_rows):
    """Deterministic draft claims; identical validation as real output."""
    claims = []
    for row in evidence_rows[:3]:
        quote = evidence_quote(row)
        if quote:
            claims.append({"text": f"{row['data'].get('rater_role')} evidence: {quote}", "evidenceId": row["id"], "quote": quote})
    return claims


def parse_real_summary(content, evidence_rows):
    """Parse provider JSON claims; malformed or uncited output raises AIError."""
    try:
        parsed = json.loads(re.search(r"\{.*\}|\[.*\]", content, re.DOTALL).group(0))
    except (AttributeError, json.JSONDecodeError, ValueError):
        raise AIError("Provider output was not parsable JSON claims.")
    if isinstance(parsed, dict):
        parsed = parsed.get("claims", [])
    if not isinstance(parsed, list) or not parsed:
        raise AIError("Provider returned no claims.")
    allowed = {row["id"]: evidence_quote(row) for row in evidence_rows}
    claims = []
    for item in parsed:
        if not isinstance(item, dict):
            raise AIError("Provider claim was not an object.")
        evidence_id, quote, text = item.get("evidenceId"), item.get("quote"), item.get("text")
        if evidence_id not in allowed or quote != allowed[evidence_id] or not isinstance(text, str) or not text.strip():
            raise AIError("Provider produced invalid or fabricated citation; rejected by citation gate.")
        claims.append({"text": text, "evidenceId": evidence_id, "quote": quote})
    return claims


def draft_summary(config, evidence_rows):
    """Real provider when configured; deterministic mock otherwise or on failure."""
    global _LAST
    if config.get("fixtureMode"):
        _LAST = {"state": "mock", "detail": "explicit fixture mode"}
        return mock_summary(evidence_rows), "mock"
    if not ai_config(config):
        _LAST = {"state": "unavailable", "detail": "AI provider is not configured."}
        raise AIUnavailableError("AI provider is not configured.")
    if ai_config(config):
        catalog = [{"evidenceId": row["id"], "quote": evidence_quote(row), "raterRole": row["data"].get("rater_role")} for row in evidence_rows]
        instruction = (
            "Draft 1-3 summary claims strictly grounded in the provided evidence catalog. "
            "Respond with JSON: {\"claims\": [{\"text\": str, \"evidenceId\": str, \"quote\": str}]}. "
            "Copy quote exactly from the catalog. Do not rate or recommend decisions. Catalog: "
            + json.dumps(catalog, ensure_ascii=False)
        )
        try:
            content = call_chat(config, [{"role": "user", "content": instruction}])
            _LAST = {"state": "live", "detail": ""}
            return parse_real_summary(content, evidence_rows), "real"
        except AIError as error:
            # REF-003: fail closed; configured provider failure never serves mock output.
            _LAST = {"state": "unavailable", "detail": error.reason}
            raise AIUnavailableError(error.reason) from error
    raise AIUnavailableError("AI provider is not configured.")


def test_connection(config):
    """Connection test returns reachable/model info; never echoes the key."""
    global _LAST
    if not ai_config(config):
        return {"ok": False, "reason": "AI provider is not configured."}
    try:
        content = call_chat(config, [{"role": "user", "content": "Reply with the single word: ok"}], timeout=8)
        _LAST = {"state": "live", "detail": ""}
        return {"ok": True, "model": config["chatModel"], "sample": content.strip()[:40]}
    except AIError as error:
        # REF-003: an explicitly configured provider that fails is degraded, not mock.
        _LAST = {"state": "degraded", "detail": error.reason}
        return {"ok": False, "reason": error.reason}


# REF-005: advisory rubric for feedback quality. Hints never gate, never rate.
_HINT_RUBRIC = [
    ("specific", "Add a concrete situation or artifact (what exactly happened, where)."),
    ("behavioral", "Describe the observed behavior itself, not a personality trait."),
    ("impact", "State the impact: what changed for the team, sprint, or deliverable."),
]


def _mock_hints(payload):
    """Deterministic rubric hints from the draft fields; no randomness, no ratings."""
    behavior = " ".join(str(payload.get(key, "")) for key in ("behavior", "action", "situation")).strip()
    impact = str(payload.get("impact", "")).strip()
    missing, hints = [], []
    words = len(behavior.split())
    if not behavior:
        missing.extend(("specific", "behavioral"))
        hints.extend((_HINT_RUBRIC[0][1], _HINT_RUBRIC[1][1]))
    elif words < 4:
        missing.append("specific")
        hints.append(_HINT_RUBRIC[0][1])
    if len(impact.split()) < 3:
        missing.append("impact")
        hints.append(_HINT_RUBRIC[2][1])
    return {"missing": missing, "hints": hints, "advisory": True}


def feedback_hints(config, payload):
    """Advisory feedback-quality hints. Real provider when configured; mock otherwise or on failure."""
    global _LAST
    fallback = _mock_hints(payload)
    if not ai_config(config):
        _LAST = {"state": "mock", "detail": ""}
        return fallback, "mock"
    instruction = (
        "You are a writing coach. For this workplace feedback draft, check three rubric points: "
        "specific (concrete situation), behavioral (describes behavior not trait), impact (states impact). "
        "Respond with JSON only: {\"missing\": [\"specific\"|\"behavioral\"|\"impact\"], \"hints\": [str]}. "
        "Hints are advisory suggestions for the author. Draft: " + json.dumps(payload, ensure_ascii=False)
    )
    try:
        content = call_chat(config, [{"role": "user", "content": instruction}])
        parsed = json.loads(re.search(r"\{.*\}", content, re.DOTALL).group(0))
        missing = [m for m in parsed.get("missing", []) if m in {"specific", "behavioral", "impact"}]
        hints = [str(h) for h in parsed.get("hints", []) if str(h).strip()][:5]
        _LAST = {"state": "live", "detail": ""}
        return {"missing": missing, "hints": hints, "advisory": True}, "real"
    except (AIError, AttributeError, json.JSONDecodeError, ValueError):
        # Hints are advisory: provider failure degrades to deterministic mock hints, never blocks.
        _LAST = {"state": "degraded", "detail": "hints provider failed; mock hints served"}
        return fallback, "mock"
