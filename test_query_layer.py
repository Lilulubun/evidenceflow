from query_layer import query

r = query("weaknesses", person_id="emp-004", rater_roles=["manager", "peer"], quarter="Q4-2026")
assert r["abstained"] is False and r["evidence"]
assert all(x["person_id"] == "emp-004" and x["rater_role"] in {"manager", "peer"} and x["quarter"] == "Q4-2026" for x in r["evidence"])
r = query("performance", person_id="emp-999")
assert r["abstained"] is True and not r["evidence"]
print("query layer checks passed")

from query_layer import trajectory, divergence
t = trajectory("emp-004")
assert "Q3-2026" in t and "Q4-2026" in t
d = divergence("emp-004", "Q4-2026", "delivery_quality")
assert len(d) > 0 and {x["rater_role"] for x in d} == {"self", "peer"}
print("trajectory and divergence checks passed")
