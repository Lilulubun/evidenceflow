-- EVIDENCEFLOW PoC — custom multi-rater evidence layer (Postgres, no Hindsight dependency).
-- Layer 2 of 10-DECISION.md: rater attribution that Hindsight does not provide natively.
-- Append-only; amendments via supersession, never UPDATE/DELETE of evidence rows.

CREATE TABLE IF NOT EXISTS person (
  id            text PRIMARY KEY,
  full_name     text NOT NULL,
  team          text NOT NULL,
  archetype     text NOT NULL
);

CREATE TABLE IF NOT EXISTS rater (
  id   text PRIMARY KEY,
  kind text NOT NULL CHECK (kind IN ('self','peer','manager'))
);

CREATE TABLE IF NOT EXISTS evidence (
  id              text PRIMARY KEY,
  person_id       text NOT NULL REFERENCES person(id),
  rater_id        text NOT NULL REFERENCES rater(id),
  rater_role      text NOT NULL CHECK (rater_role IN ('self','peer','manager')),
  quarter         text NOT NULL,
  competency      text NOT NULL,
  sentiment       text NOT NULL CHECK (sentiment IN ('pos','neg')),
  quote           text NOT NULL,
  event_time      date NOT NULL,
  ingestion_time  date NOT NULL,
  superseded_by   text REFERENCES evidence(id),
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_evidence_person   ON evidence(person_id, event_time);
CREATE INDEX IF NOT EXISTS idx_evidence_rater    ON evidence(rater_id, rater_role);
CREATE INDEX IF NOT EXISTS idx_evidence_ingest   ON evidence(person_id, ingestion_time);

CREATE OR REPLACE VIEW rater_divergence AS
SELECT person_id, quarter, competency,
       bool_or(sentiment='pos') FILTER (WHERE rater_role='self')    AS self_pos,
       bool_or(sentiment='pos') FILTER (WHERE rater_role='peer')    AS peer_pos,
       bool_or(sentiment='pos') FILTER (WHERE rater_role='manager') AS mgr_pos
FROM evidence
WHERE superseded_by IS NULL
GROUP BY person_id, quarter, competency
HAVING (bool_or(sentiment='pos') FILTER (WHERE rater_role='self')
     <> bool_or(sentiment='pos') FILTER (WHERE rater_role='peer'))
    OR (bool_or(sentiment='pos') FILTER (WHERE rater_role='peer')
     <> bool_or(sentiment='pos') FILTER (WHERE rater_role='manager'));
