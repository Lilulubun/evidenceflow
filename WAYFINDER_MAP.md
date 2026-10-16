# Wayfinder Map — EVIDENCEFLOW MVP

## Destination

A validated MVP for evidence-grounded 360° performance appraisal. HR administers the system; managers use it to review employees. The MVP produces traceable performance summaries and exposes evidence that supports fairer, auditable decisions. Manager decides, with HR oversight.

## Notes

- Hackathon topic: Conversational AI for Business Process Execution.
- Primary product user: manager.
- Governance user: HR/People Operations.
- Core value: conversational evidence collection plus fairer, auditable appraisal.
- AI assists retrieval and summarization; it never decides rating, promotion, or compensation.
- Structured evidence layer remains source of truth.
- Use current research artifacts and synthetic data until approved real data exists.

## Decisions so far

- [Target users](tickets/01-target-users.md): HR administers; managers perform reviews; HR oversees.
- [Product value](tickets/02-product-value.md): combine fairer appraisal with auditable evidence.
- [MVP output](tickets/03-mvp-output.md): evidence-backed employee performance summary.
- [Decision authority](tickets/04-decision-authority.md): manager decides with HR oversight.
- [Primary review journey](tickets/05-manager-review-workflow.md): manager reviews one employee before appraisal.
- [Fairness definition](tickets/06-fairness-definition.md): traceable claims, separate rater perspectives, and visible missing/conflicting evidence.
- [First-screen experience](tickets/07-evidence-display.md): short summary with key evidence and disagreement flags.
- [Pilot data](tickets/08-pilot-validation.md): synthetic data first; approved anonymized real data later.
- [MVP boundary](tickets/09-mvp-boundary.md): evidence collection, Q3–Q4 review, rater comparison, cited summary, flags, manager rationale, rating, and HR audit trail; no automatic HR decisions or HRIS integration.
- [Demo period](tickets/13-demo-period.md): compare Q3 to Q4.
- [Demo perspectives](tickets/14-demo-perspectives.md): self, peer, and manager.
- [Evidence capture trigger](tickets/16-evidence-capture-trigger.md): MVP uses manual actions; integrations remain future extensions.
- [Contribution conversation](tickets/17-contribution-conversation.md): capture situation, personal action, result, timing, competency, verifier, then confirm before saving.
- [Feedback conversation](tickets/18-feedback-conversation.md): selected observer submits direct behavior, impact, competency, feedback type, and visibility choice.
- [Check-in conversation](tickets/19-check-in-conversation.md): recent evidence leads to progress, obstacle, support, and an owned follow-up commitment.
- [Manager review](tickets/20-manager-review.md): manager reviews Q3–Q4 evidence by competency and rater, edits cited AI summary, records provisional rationale/rating, receives employee response, then finalizes.
- [Evidence disagreement resolution](tickets/21-evidence-disagreement-resolution.md): original evidence remains immutable; clarification becomes linked new evidence and labels original as clarified, superseded, or disputed.
- [Employee response](tickets/22-employee-response.md): employee can clarify, dispute, or add evidence; original remains immutable; manager classifies response with reason.
- [Response visibility](tickets/23-response-visibility.md): employee, manager, and HR see response according to role; peers see nothing unless policy permits.
- [HR audit](tickets/24-hr-audit.md): HR reviews immutable evidence history, linked responses, status, rating changes, missing support, disputes, and access logs; changes require recorded action.
- [Business outcome](tickets/10-business-outcome.md): faster evidence review, valid source-linked claims, zero cross-employee leakage, visible disagreement, explainable manager decision, auditable HR history.

## Open tickets

- [Validation protocol](tickets/11-validation-protocol.md) — define manager tasks and success thresholds.
- [Product narrative](tickets/12-product-narrative.md) — turn decisions into proposal/demo message.
- [TKT 3 proof-of-concept](tickets/25-tkt3-proof-of-concept.md) — prove critical functions experimentally, not only through UI.
- [Prototype shape](tickets/15-prototype-shape.md) — define functional demo screens and interaction sequence.
- [TKT 3 evidence package](tickets/26-tkt3-evidence-package.md) — define reproducible test records and submission evidence.

## Not yet specified

- Approved real-world pilot organization and data governance.
- Pricing, deployment model, and HRIS integration after MVP validation.
- Long-term bias and performance-impact study design.

## Out of scope

- Automatic promotion or compensation decisions.
- Fully automatic employee rating.
- Claims that the system eliminates bias.
- Production HRIS integration before MVP validation.
