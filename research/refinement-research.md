# EVIDENCEFLOW Refinement Research Notes

Research done 2026-10-16 (before polish plan). Sources and what we take from each.

## 1. Citation faithfulness (arXiv:2412.18004, "Correctness is not Faithfulness in RAG Attributions")

- Finding: up to 57% of citations in attributed RAG answers are not faithful; checking "cited doc exists and is relevant" is not enough.
- Gap in our prototype: citation gate verifies evidence ID + exact quote, but does NOT detect summary sentences that carry NO citation at all (uncited claims slip through).
- Take: add citation-coverage check — every summary claim must map to evidence; uncited claims flagged `unsupported` and counted. Report coverage % in review + TKT3 report.

## 2. Anthropic "Demystifying Evals for AI Agents" + eval-harness practices

- Take: verification belongs inside the workflow loop, not only post-hoc. Our TKT3 runner already does this; extend it with trajectory evidence (request/response logs per test) so results are auditable, not just pass/fail booleans.

## 3. What hackathon judges check (dev.to judge rubrics, lablab.ai winning guide, Agora rubric)

- Working demo with live input — not curl. → need real browser chat UI.
- "How does it fail?" — visible fallback when AI wrong/slow/off. → show mock/degraded mode banner in UI.
- "Did they evaluate anything?" — show test matrix + which cases failed. → TKT3 results rendered as readable report page.
- "Where does the data go?" — secret/privacy story. → already built (settings store, masked keys); surface it in UI + README.
- Demo understandable in 30 seconds. → evidence-backed summary as first screen.
- Video structure: 0:00–0:30 problem, 0:30–2:30 live demo, 2:30–4:00 business case, 4:00–5:00 roadmap.
- Judges reward deliberate scope trade-offs; state them.

## 4. Conversation UX (Microsoft Power Platform well-architected conversation design, 2025)

- Structured dialogue beats free chat for business process execution: quick replies, progress indicator, explicit confirmation steps, clear error recovery.
- Take: UI uses quick-reply buttons for conversation flows (Add contribution / Give feedback / Start check-in), confirmation card before evidence is created, clickable evidence chips showing source (who/when/role).

## 5. Vanilla chat UI repos (no-build static chat apps)

- Confirmed pattern: single `index.html` + `app.js` + `styles.css`, no build step, fetch-based.
- Take: serve UI from `server.py` as static files; zero new dependencies.

## 6. LLM-as-judge rubrics (Langfuse, rubric articles)

- Judge = instrument, needs anchors + calibration; use only as assist, human decides.
- Take: optional AI-assisted quality hints on feedback drafts (rubric: specific? behavioral? impact stated?), always advisory, never gating, never rating. Mock mode generates deterministic hints.

## Scope guard

- No new runtime dependencies. Stdlib + vanilla JS only.
- No new product decisions: refinement stays inside locked Wayfinder decisions (tickets 01–26).
- Fairness/production claims still forbidden; claims stay "controlled synthetic TKT 3 proof".
