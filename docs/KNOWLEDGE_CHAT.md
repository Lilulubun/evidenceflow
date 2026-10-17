# Knowledge chat contract

Factual employee questions use `search_employee_knowledge` with explicit `source` (`research` or `runtime`). Research reads local synthetic `evidence.json`; runtime reads visible local store evidence. Sources never mix.

Employee scope is mandatory. Employees query own evidence only. Manager and HR have demo scoped access; peer visibility follows stored visibility policy. Demo actor selector is not production authentication.

Lookup is read-only. Structured filtering runs first. Answers contain exact quotes and evidence IDs; `governance.validate_citations` rejects invalid citations. Empty or unsupported queries abstain. Runtime Hindsight adapter remains future work.
