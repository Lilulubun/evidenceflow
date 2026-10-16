"""Audit-safe structured retrieval baseline for EVIDENCEFLOW appraisal evidence."""
import json, re
from pathlib import Path

DATA_PATH = Path(__file__).with_name("evidence.json")

def load_evidence(path=DATA_PATH):
    return json.loads(Path(path).read_text())

def query(text, *, person_id=None, rater_roles=None, quarter=None, competency=None, limit=5, data=None):
    """Filter before ranking; never return cross-entity or unknown-person evidence."""
    rows = data if data is not None else load_evidence()
    roles = set(rater_roles or ())
    rows = [r for r in rows if (not person_id or r["person_id"] == person_id)
            and (not roles or r["rater_role"] in roles)
            and (not quarter or r["quarter"] == quarter)
            and (not competency or r["competency"] == competency)]
    if not rows:
        return {"answer": None, "evidence": [], "abstained": True, "reason": "No evidence matches structured constraints."}
    terms = set(re.findall(r"[a-z_]+", text.lower()))
    def rank(r):
        hay = f"{r['quote']} {r['competency']} {r['sentiment']}".lower()
        return (sum(t in hay for t in terms) + (2 if r["sentiment"] == "neg" else 0), r["event_time"])
    picked = sorted(rows, key=rank, reverse=True)[:max(1, limit)]
    return {"answer": f"Found {len(picked)} evidence record(s).", "abstained": False,
            "evidence": [{k: r[k] for k in ("id","person_id","person_name","rater_role","quarter","competency","sentiment","quote","event_time","ingestion_time")} for r in picked]}


def trajectory(person_id, data=None):
    rows = [r for r in (data if data is not None else load_evidence()) if r["person_id"] == person_id]
    by_q = {}
    for r in rows:
        by_q.setdefault(r["quarter"], []).append(r)
    return {q: {"positive": sum(r["sentiment"] == "pos" for r in rs), "negative": sum(r["sentiment"] == "neg" for r in rs), "total": len(rs)} for q, rs in sorted(by_q.items())}

def divergence(person_id, quarter, competency, data=None):
    rows = [r for r in (data if data is not None else load_evidence()) if r["person_id"] == person_id and r["quarter"] == quarter and r["competency"] == competency]
    return [{"evidence_id": r["id"], "rater_role": r["rater_role"], "sentiment": r["sentiment"], "quote": r["quote"], "event_time": r["event_time"]} for r in rows]
