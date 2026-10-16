# Evidence disagreement resolution

## Question
How does EVIDENCEFLOW resolve disagreement without rewriting history?

## Resolution
Original evidence remains immutable. A clarification conversation creates new evidence linked to the original with a relationship such as `CLARIFIES`, `SUPERSEDES`, or `RESPONDS_TO`. The original receives a visible status: `clarified`, `superseded`, or `disputed`. The new evidence and its source support the resolution. Final rationale references the evidence used for the decision, while the audit trail retains the original claim and every change.

If disagreement remains unresolved, the original remains `disputed`; the manager must acknowledge the unresolved disagreement before finalizing.
