# Conversational audit

## Findings

- Prior chat stored each turn as one answer, so multi-fact messages became one wrong field.
- First prompt described guided capture, reinforcing form behavior.
- Chat events lacked assistant message/turn completion semantics.

## Fixes

- Added deterministic extraction for labelled natural facts in one message.
- Added reflection, missing-only clarification, correction (`correct field: value`), and skip handling.
- Added `assistant_message` and `turn_completed` events.
- Kept server-side validation and explicit confirmation gate unchanged.
- Updated workspace copy to describe natural storytelling.

## Verification

Focused `test_chat_natural.py`, existing conversation/governance/query/response/settings/AI/graph/UI checks, `run_checks.py`, `tkt3_runner.py` (12/12), `demo_scenario.py`, Python compilation, and Node syntax checks pass.

Live deployment/browser: not exercised in this worker because Basic Auth credentials were unavailable; no credentials requested or guessed.
