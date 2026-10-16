"""Run EVE-002..008 checks in one pass with the standard library only."""
for check in ["test_shell.py", "test_query_layer.py", "test_conversations.py", "test_responses.py", "test_governance.py", "test_settings.py", "test_graph.py"]:
    print(f"--- {check}")
    with open(check, encoding="utf-8") as handle:
        source = handle.read()
    exec(compile(source, check, "exec"), {"__name__": "__main__", "__file__": check})
print("all local checks passed")
