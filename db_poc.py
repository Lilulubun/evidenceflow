"""EVIDENCEFLOW PoC — Phase 1: standalone Postgres evidence layer.

pg0-embedded Postgres (same engine Hindsight embeds), schema.sql applied,
evidence.json loaded, 10-DECISION.md validation checks executed.
Hindsight itself NOT started (no LLM key) — this validates the custom
multi-rater layer that Hindsight does not provide natively.
"""
import json, sys, pathlib
from pg0 import Pg0

ROOT = pathlib.Path("/opt/data/research/evidenceflow-poc")

def main():
    pg = Pg0(name="evidenceflow", database="evidenceflow")
    pg.start()
    print("pg0 uri:", pg.uri)
    try:
        # multi-statement: run via psql bridge; single statements via pg.execute
        import psycopg2  # hindsight-api-slim dependency, already in venv
        conn = psycopg2.connect(pg.uri)
        cur = conn.cursor()
        cur.execute(pathlib.Path(ROOT/"schema.sql").read_text())
        conn.commit()
        print("schema applied")

        data = json.loads((ROOT/"evidence.json").read_text())
        persons, raters = {}, {}
        for e in data:
            persons[e["person_id"]] = (e["person_id"], e["person_name"], e["team"], "synthetic")
            raters.setdefault(e["rater_id"], e["rater_role"])
        from psycopg2.extras import execute_values
        cur.execute("TRUNCATE person, rater, evidence")
        execute_values(cur, "INSERT INTO person VALUES %s", list(persons.values()))
        execute_values(cur, "INSERT INTO rater VALUES %s", list(raters.items()))
        execute_values(cur,
            """INSERT INTO evidence (id,person_id,rater_id,rater_role,quarter,competency,
               sentiment,quote,event_time,ingestion_time,superseded_by) VALUES %s""",
            [(e["id"], e["person_id"], e["rater_id"], e["rater_role"], e["quarter"],
              e["competency"], e["sentiment"], e["quote"], e["event_time"], e["ingestion_time"], None)
             for e in data])
        conn.commit()
        print(f"loaded: {len(persons)} persons, {len(raters)} raters, {len(data)} evidence rows")

        # ===== validation checks (10-DECISION.md) =====
        cur.execute("SELECT count(*) FROM evidence"); n = cur.fetchone()[0]
        assert n == 960, f"expected 960 got {n}"
        print("check 1 (volume): 960 OK")

        cur.execute("SELECT count(*), min(quote) FROM evidence WHERE person_id='emp-004'")
        n4, q4 = cur.fetchone()
        assert n4 == 24, n4
        print(f"check 2 (traceability): emp-004 {n4} rows; sample: {q4[:55]!r}")

        cur.execute("""SELECT rater_role, count(*) FROM evidence
                       WHERE person_id='emp-004' AND quarter='Q3-2026'
                       GROUP BY rater_role ORDER BY rater_role""")
        got = dict(cur.fetchall())
        assert got == {'manager': 4, 'peer': 5, 'self': 3}, got
        print("check 3 (multi-rater): emp-004 Q3 self/peer/manager = 3/5/4, distinct")

        cur.execute("SELECT count(*) FROM rater_divergence")
        d = cur.fetchone()[0]
        assert d > 0, "no divergence detected"
        print(f"check 4 (divergence): {d} person-quarter-competency divergences")

        cur.execute("SELECT count(*) FROM evidence WHERE ingestion_time - event_time > 7")
        late = cur.fetchone()[0]
        assert late > 0
        print(f"check 5 (T vs T'): {late} records arrive >7d after event")

        cur.execute("""SELECT quarter, round(100.0*sum((sentiment='pos')::int)/count(*))
                       FROM evidence WHERE person_id='emp-004' GROUP BY quarter ORDER BY quarter""")
        flip = dict(cur.fetchall())
        assert flip['Q3-2026'] > flip['Q4-2026'], flip
        print(f"check 6 (trajectory): emp-004 volatile, pos% Q3>Q4 = {flip} (declining as designed)")

        conn.close()
        print("\nALL CHECKS PASSED")
    finally:
        pg.stop()

if __name__ == "__main__":
    sys.exit(main())
