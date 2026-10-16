"""OpenAI-compatible AI adapter. Real AI optional; deterministic mock is default and citation-gated.

Contract (PRODUCT_CONTRACT.md): AI may structure evidence and draft source-linked
summaries. It never selects ratings. Every AI citation must match an existing
evidence ID and exact stored quote or it is rejected.
"""
import json
import re
from urllib import request as urlrequest

from governance import evidence_quote


class AIError(Exception):
    """Raised when the configured provider cannot be reached or answers invalid JSON."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# REF-003: last AI call outcome surfaced via /health; degraded means configured
# provider failed and mock output was served instead. Single-process demo scope.
_LAST = {"state": "mock", "detail": ""}


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


def call_chat(config, messages, timeout=15):
    """Blocking OpenAI-compatible /chat/completions call; raises AIError on any failure."""
    if not ai_config(config):
        raise AIError("AI provider is not configured.")
    payload = json.dumps({
        "model": config["chatModel"],
        "messages": messages,
        "temperature": float(config.get("temperature", 0)),
        "max_tokens": int(config.get("tokenLimit", 1024)),
    }).encode("utf-8")
    req = urlrequest.Request(
        config["baseUrl"].rstrip("/") + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {config['apiKey']}"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise AIError("Provider returned empty completion.")
        return content
    except AIError:
        raise
    except Exception as error:  # network, HTTP, JSON, schema failures all degrade to mock
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
            # REF-003: never pass degraded output off as live; remember why for /health.
            _LAST = {"state": "degraded", "detail": error.reason}
    else:
        _LAST = {"state": "mock", "detail": ""}
    return mock_summary(evidence_rows), "mock"


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
