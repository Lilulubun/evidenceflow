"""REF-008 runnable provenance / scope / visibility checks; stdlib only."""
import json
import tempfile
from pathlib import Path
from app_core import Store
from employee_graph import employee_graph


def main():
    with tempfile.TemporaryDirectory() as directory:
        store = Store(Path(directory) / "state.json")
        body = {"employeeId": "emp-004", "source": "research", "actor": {"id": "emp-004", "role": "employee"}}
        def get(**patch):
            return employee_graph(store, {**body, **patch})
        status, graph = get()
        assert status == 200 and graph["evidenceCount"] == 24
        assert all(n.get("employeeId", "emp-004") == "emp-004" for n in graph["nodes"])
        assert get(source=[])[0] == 422
        assert get(actor={"id":"x","role":[]})[0] == 422
        assert get(source="")[0] == 422
        assert get(actor={"id": "emp-003", "role": "employee"})[0] == 403
        assert get(actor={"id": "a", "role": "invalid"})[0] == 422
        assert get(quarter=[])[0] == 422
        assert get(employeeId="emp-999", actor={"id":"hr-001","role":"hr"})[1]["evidenceCount"] == 0
        assert get(quarter="Q4-2026", competency="collaboration")[1]["evidenceCount"] == 3
        def row(id, employee="emp-004", kind="feedback", **data):
            return {"id":id,"kind":kind,"created_at":"2026-10-16","created_by":{"id":"peer-001","role":"peer"},"status":"active","data":{"employee_id":employee,"period":"Q4-2026","competency":"collaboration","rater_role":"peer","impact":"<img src=x onerror=alert(1)>",**data}}
        state=store.snapshot()
        state["evidence"]=[row("public"),row("private",visibility="hr_only"),row("other",employee="emp-003"),row("response",kind="response",original_evidence_id="public",response="Exact response quote"),row("hidden-response",kind="response",original_evidence_id="private",response="secret")]
        state["relations"]=[{"original_evidence_id":"public","response_evidence_id":"response","relationship":"disputed"},{"original_evidence_id":"other","response_evidence_id":"response","relationship":"clarified"}]
        store._write(state)
        before=store.path.read_bytes()
        status,g=get(source="runtime")
        evidence={n["evidenceId"]:n for n in g["nodes"] if n["type"]=="evidence"}
        assert status == 200 and set(evidence)=={"public","response"}
        assert evidence["response"]["quarter"] == "Q4-2026"
        assert evidence["response"]["competency"] == "collaboration"
        assert evidence["public"]["quote"] == "<img src=x onerror=alert(1)>"
        assert sum(l["type"]=="disputed" for l in g["links"]) == 1
        assert all(l["type"]!="clarified" for l in g["links"])
        assert get(source="runtime",actor={"id":"peer-001","role":"peer"})[1]["evidenceCount"] == 1
        assert get(source="runtime",actor={"id":"hr-001","role":"hr"})[1]["evidenceCount"] == 4
        assert get(source="runtime",quarter="Q3-2026")[1]["evidenceCount"] == 0
        assert before == store.path.read_bytes()
        # Exercise real HTTP parser/routes with isolated state and ephemeral port.
        from http.server import ThreadingHTTPServer
        from threading import Thread
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from unittest.mock import patch
        import server
        with patch.object(server, "store", return_value=store):
            http = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
            thread = Thread(target=http.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{http.server_port}"
            try:
                for path in ("/graph?employee=emp-004", "/graph.js", "/styles.css"):
                    with urlopen(base + path) as response:
                        assert response.status == 200
                with urlopen(base + "/graph.js") as response:
                    js = response.read().decode()
                assert 'id="labels"' not in js and "setLabels" in js and "labelsOn" in js
                assert 'NODE_COLORS' in js and 'LINK_COLORS' in js
                assert 'Graph interaction/visual design adapted from vectorize-io/hindsight control-plane constellation (Apache-2.0)' in js
                assert 'const BG = "#f7f6f2"' in js and 'seededLayout' in js
                assert 'devicePixelRatio' in js and 'ResizeObserver' in js
                with urlopen(base + "/graph") as response:
                    html = response.read().decode()
                assert '<canvas id="graph"' in html and 'tabindex="0"' in html
                assert 'id="labels" aria-pressed="true">Hide labels' in html
                payload = {**body, "source":"runtime"}
                req = Request(base+"/api/graph", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
                with urlopen(req) as response:
                    assert json.load(response)["evidenceCount"] == 2
                payload["employeeId"] = "emp-003"
                req.data = json.dumps(payload).encode()
                try:
                    urlopen(req)
                    raise AssertionError("Cross-employee request accepted")
                except HTTPError as error:
                    assert error.code == 403
            finally:
                http.shutdown(); http.server_close(); thread.join()
        assert before == store.path.read_bytes()
        print("GRAPH_HTTP_OK routes, scoped API, cross-employee 403")
        print("GRAPH_CHECKS_OK scope, explicit source, validation, exact quotes, filters, response links, visibility, immutable runtime")

if __name__ == "__main__":
    main()
