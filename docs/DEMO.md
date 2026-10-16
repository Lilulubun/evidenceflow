# EVIDENCEFLOW demo script (judge flow)

One command to start:

```sh
python3 server.py
```

Then open `http://127.0.0.1:8000/`. Fully scripted equivalent (used for the
recorded run): `python3 demo_scenario.py` — exits 0 when every step below passes.

## Story beats

- 0:00–0:30 Problem — performance reviews run on memory and influence. Evidence
  exists (commits, tickets, peer notes) but never reaches the review in
  structured, attributable form. Ratings become narrative, not evidence.
- 0:30–2:30 Live scenario (the full loop below, in the browser UI).
- 2:30–4:00 Safety story — immutable evidence, 100% citation gate, AI never
  decides, manager owns the rating, HR sees everything.
- 4:00–5:00 Limitations and roadmap — synthetic single-process PoC; multi-user
  store, real-model pilot, and integrations are next.

## Video shot list (5:00, single screen recording + voiceover)

| # | Time | Screen | Action | Narration beat |
|---|------|--------|--------|----------------|
| 1 | 0:00–0:30 | `/` shell, employee role | none (title overlay) | Problem: reviews run on memory; evidence never reaches the review. |
| 2 | 0:30–0:50 | Capture → Add contribution | fill situation/action/result/verifier → Review draft → Confirm & save | Structured capture; evidence `ev-…` created only after confirm; immutable from now. |
| 3 | 0:50–1:15 | Capture → Give feedback | type thin draft → advisory hints appear → submit → confirm | Peer evidence; AI hints are advisory rubric nudges, never a gate or a rating. |
| 4 | 1:15–1:50 | Manager → Review emp-004 | timeline + conflict chip + missing competencies → Draft cited summary | Manager sees self+peer split, conflicts flagged; AI drafts claims each citing `evidenceId` + exact quote. |
| 5 | 1:50–2:15 | Summary draft card | record provisional rating `meets` with rationale | Citation gate verifies every cite before rating accepted; coverage % shown. |
| 6 | 2:15–2:30 | Employee → Respond to evidence | pick peer row → dispute + source → confirm | Disagreement creates NEW linked evidence; original row untouched. |
| 7 | 2:30–3:10 | Manager → Finalize | employee attempt rejected (403) → manager finalizes | Human owns the decision; append-only history shows before/after/actor/reason. |
| 8 | 3:10–3:40 | HR → Audit emp-004 | full reconstruction: evidence, relations, decisions, events | HR audits everything; provenance preserved end to end. |
| 9 | 3:40–4:00 | AI settings | save key → only `********` echoed; banner shows mock | Secrets stay server-side (file 0600); mock mode needs zero credentials. |
| 10 | 4:00–4:30 | `/tkt3` | show 12/12 matrix + one trajectory expansion | Validated against 12 spec test cases; per-case trajectory auditable. |
| 11 | 4:30–5:00 | closing overlay | claim boundary text verbatim | Claim boundary (below), limitations, roadmap. |

## Full scenario (click-by-click)

1. Employee (Dewi, emp-004) clicks **Add contribution**: situation, action,
   result, verifier → confirmation card → evidence created (`ev-…`).
2. Peer clicks **Give feedback**: concern-type feedback on the same employee →
   advisory rubric hints shown (non-blocking) → confirmed evidence, rater role
   `peer`.
3. Manager opens **Review emp-004**: timeline shows self + peer evidence,
   supporting vs conflicting split, missing competencies flagged.
4. Manager clicks **Draft summary**: AI (mock mode, deterministic) returns
   claims where every claim carries `evidenceId` + exact stored quote.
5. Manager records **provisional rating** `meets` with rationale; claims are
   citation-verified before the rating is accepted; the result shows
   `citation coverage: 100%`.
6. Employee opens the peer feedback and clicks **Respond** (dispute):
   creates NEW linked evidence; original row is byte-identical.
7. Manager **classifies** the response `partially_accepted` with reason
   (classify card appears on the review screen flow).
8. Employee clicks **Finalize** → rejected with explicit reason (403).
9. Manager clicks **Finalize** → final rating recorded; append-only history
   shows before/after/actor/timestamp/reason.
10. HR clicks **Audit emp-004**: full reconstruction — evidence, relations,
    decisions, event history, finalized flag.
11. **AI settings**: saving an API key stores it server-side only (file 0600);
    the UI and every API response show `********`. Key stays masked; *Enabled*
    selects live provider mode; a failing provider flips the banner to
    `degraded` (never silently live).
12. Open `http://127.0.0.1:8000/tkt3`: 12/12 validation matrix with
    per-case trajectory (inputs → expected → observed → verdict).

## Degraded-mode story (tell while showing)

- No credentials → mock mode banner (deterministic, same citation gate).
- Provider failure mid-run → AI degrades to mock; raw evidence stays usable;
  banner shows `degraded` (REF-003).
- Fabricated citation attempt → rejected; nothing enters the summary.
- Uncited summary claim → flagged `unsupported`; finalizing below 100%
  coverage requires explicit acknowledgment (REF-002).

## Claim boundary (must be spoken verbatim at the end)

"This proves critical prototype functions in a controlled synthetic scenario.
It does not prove bias elimination, organizational validity, fairness, or
production readiness."
