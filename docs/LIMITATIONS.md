# EVIDENCEFLOW release — limitations (TKT 3 boundary)

Binding claim: **"Critical prototype functions were demonstrated in a controlled
synthetic scenario."** Nothing else is claimed. Not claimed: bias elimination,
organizational validity, fairness, production readiness, improved employee
performance.

## Limitations

1. **Single-process JSON store.** `app_core.Store` is one file, one process,
   no locking across processes, no durable multi-user concurrency. Multi-user
   deployment needs a transactional DB (schema.sql sketches the Postgres shape;
   `pg0` environment unavailable — EVE-B01).
2. **Mock AI only on this host.** Real provider path proven by contract tests
   against a local HTTP stub (valid + malformed + failing responses). No live
   model run; no quality claim about real-model output.
3. **Synthetic data only.** Fixture: emp-004 Dewi Nugraha, Q3–Q4 2026,
   self/peer/manager, generated scenarios. No real organizational data touched.
4. **Authorization is role-level, not assignment-level.** Any `manager` actor
   can review any employee; production needs manager↔employee assignment.
5. **No authentication.** Actors are plain `{id, role}` objects on requests.
   Real deployment needs SSO/session auth; this PoC isolates authorization
   logic, not identity.
6. **Citation gate is exact-quote.** Paraphrase-correct citations fail the gate
   (safe direction), and unfaithful-but-exact quotes still pass; coverage gate
   (REF-002) reduces uncited-claim risk.
7. **Unresolved-dispute handling** records `acknowledged_unresolved` in the
   event trail; no separate HR alerting surface.
8. **Rater role is provenance labeling.** Employee-authored rows (check-ins,
   responses) carry role `employee`; TKT3-05 treats this as designed behavior.
9. **Screenshots/video** depend on a browser-capable host; on this VPS the
   scripted HTTP demo (`demo_scenario.py`, exit 0) is the executable proof.
10. **No i18n, no a11y audit, no load testing.** Out of TKT 3 scope.

## Environment

- Python 3.14.7, stdlib only; zero runtime dependencies installed.
- Linux 6.8.0-138-generic VPS, 4 GB RAM.
- Reproduce: `python3 demo_scenario.py` (exit 0) — full scenario over HTTP.
