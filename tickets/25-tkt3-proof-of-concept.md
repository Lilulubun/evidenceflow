# TKT 3 proof-of-concept

## Question
What must the prototype prove to support a TKT 3 claim?

## Resolution
The prototype must experimentally prove critical functions: conversational evidence capture, structured evidence creation after confirmation, source-linked summary with exact citation verification, multi-rater/entity separation, disagreement resolution through linked immutable evidence, manager finalization, and HR audit. Data may be synthetic and controlled. UI screenshots alone are insufficient.

## Test cases

- valid contribution creates evidence after confirmation
- missing result triggers clarification and no unsupported result
- fabricated citation is rejected
- wrong employee produces no evidence
- self/peer/manager roles remain separated
- employee response creates linked evidence
- original evidence remains immutable
- unauthorized finalization is rejected
- manager finalization records append-only decision
- rating changes record before/after and reason
- unresolved dispute requires manager acknowledgment
- HR can inspect complete history
