# EVIDENCEFLOW Product Contract

## Purpose

EVIDENCEFLOW is a controlled MVP for evidence-grounded 360° performance appraisal. It collects attributable evidence, retrieves it by employee and context, and produces source-linked summaries for human review.

## Roles and authority

| Role | Allowed actions | Forbidden actions |
|---|---|---|
| Employee | Contribute evidence; respond to evidence; clarify, dispute, or add evidence | Finalize manager rating |
| Peer | Submit permitted feedback | View restricted employee responses or finalize rating |
| Manager | Review assigned employee; compare Q3–Q4 evidence; edit cited summary; record rationale; finalize rating | Delegate final decision to AI |
| HR/People Operations | Administer process; inspect immutable history, responses, decisions, and access logs; audit changes | Automatically approve every rating; alter original evidence |
| AI | Assist evidence extraction, retrieval, and summarization | Decide rating, promotion, compensation, or finalize appraisal |

Manager owns final appraisal decision. HR owns governance and audit.

## MVP scope

Included:

- Explicit manual actions: `Add contribution`, `Give feedback`, `Start check-in`.
- 360° evidence from `self`, `peer`, and `manager` perspectives.
- Individual employee review using Q3–Q4 comparison.
- Evidence timeline and multi-rater comparison.
- Cited summary with visible supporting, conflicting, and missing evidence.
- Manager rationale, provisional/final rating, employee response, and HR audit trail.
- Synthetic data for validation until approved anonymized real data exists.

Excluded:

- Automatic rating, promotion, or compensation recommendation.
- Employee ranking or bias-elimination claims.
- HRIS integration before MVP validation.
- Automatic external triggers; integrations remain future work.

## Evidence contract

Structured evidence layer is source of truth. A contribution records situation, personal action, result, timing, competency, verifier, rater, employee, and confirmation state. Feedback records direct behavior, impact, competency, feedback type, visibility, rater, and employee. Check-ins record progress, obstacle, support, owner, due date, and success evidence.

Evidence is saved only after user confirmation. Missing results trigger clarification; unsupported results never become facts. Original evidence is immutable. Clarification, dispute, or response creates new linked evidence and labels the relationship (`clarified`, `superseded`, or `disputed`). Every summary claim must cite an existing evidence ID and exact source quote. Invalid or fabricated citations are rejected.

Every evidence query enforces employee/entity boundary, preserves rater-role separation, and exposes period and competency provenance. Unknown employees return no evidence from another employee.

## Review and governance contract

Manager reviews evidence by competency, period, and rater; edits AI summary; records rationale and provisional rating; receives employee response; then finalizes. Unresolved disagreement requires explicit manager acknowledgment and rationale before finalization.

Rating changes are append-only and retain before value, after value, actor, timestamp, and reason. HR can reconstruct evidence, linked responses, decisions, and access history. Unauthorized finalization is rejected and records reason.

## AI mode boundary

Mock mode is default when no provider credentials exist. Mock output is deterministic and must pass the same citation and entity validation as real output. Real AI is optional, configurable per environment, and assists only extraction, retrieval, and summarization. AI failure leaves raw structured evidence usable. No API key or provider secret may enter Git, frontend storage, logs, fixtures, or response payloads.

## Validation claim boundary

TKT 3 validation supports only: "critical prototype functions were demonstrated in a controlled synthetic scenario." It does not support claims of bias elimination, organizational validity, production readiness, or improved employee performance.
