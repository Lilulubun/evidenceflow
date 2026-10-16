# EVIDENCEFLOW Phase 3 Research Result

Dataset: 960 evidence rows
Queries: 6

## Metrics

- Precision@5: 1.000
- Recall@5: 0.758
- MRR: 0.833
- Abstention accuracy: 1.000
- Entity leakage rate: 0.000

## Finding

Structured constraints eliminate cross-entity leakage and support abstention for unknown entities. Hindsight remains useful for semantic distillation and ranking within a constrained candidate set, but Hindsight-only retrieval is not audit-safe.

## Limitations

- Benchmark labels derive from explicit synthetic-record constraints, not human relevance judgments.
- Hindsight-only exact relevance labels were not available for all returned results.
- Production API integration remains outside this PoC.
