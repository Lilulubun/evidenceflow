# EVIDENCEFLOW TKT 3 Validation Specification

## Purpose

Prove critical EVIDENCEFLOW functions in a controlled synthetic scenario. This validates proof of concept, not organizational effectiveness, fairness, or production readiness.

## Fixture

- Employee: Dewi Nugraha (`emp-004`)
- Period: Q3–Q4 2026
- Rater roles: `self`, `peer`, `manager`
- Competencies: collaboration, initiative, adaptability
- Required evidence: positive, negative, conflicting, incomplete-result, and clarified records

## Test cases

| ID | Function | Expected result |
|---|---|---|
| TKT3-01 | Valid contribution conversation | Structured evidence is created only after user confirmation. |
| TKT3-02 | Missing result | System asks clarification; unsupported result is not stored as fact. |
| TKT3-03 | Source-linked summary | Every summary claim links to a valid source quote and evidence ID. |
| TKT3-04 | Fabricated citation | Invalid quote is rejected; fabricated evidence is not presented as valid. |
| TKT3-05 | Rater separation | Self, peer, and manager evidence remain distinguishable. |
| TKT3-06 | Entity boundary | Query for unknown/wrong employee returns no evidence from another employee. |
| TKT3-07 | Disagreement response | Employee response creates new linked evidence; original remains unchanged. |
| TKT3-08 | Response classification | Manager records accepted, partially accepted, not accepted, or needs investigation with reason. |
| TKT3-09 | Access control | Employee cannot finalize rating; manager can finalize assigned review. |
| TKT3-10 | Rating history | Provisional/final changes preserve before, after, actor, timestamp, and reason. |
| TKT3-11 | Unresolved disagreement | Finalization requires manager acknowledgment and rationale. |
| TKT3-12 | HR audit | HR can reconstruct evidence, responses, decisions, and access history. |

## Acceptance criteria

- 12/12 test cases pass.
- Summary citation validity: 100%.
- Cross-employee evidence leakage: 0.
- Original evidence mutation: 0.
- Unauthorized finalization: 0 successful attempts.
- Every failed/blocked action records an explicit reason.

## Evidence to retain

- Fixture dataset and IDs.
- Conversation transcripts.
- Structured evidence output.
- Summary and citation verification output.
- Test run logs.
- Expected-versus-observed results.
- Screenshots or demo recording.
- Known limitations and environment versions.

## Claim boundary

Successful tests support: "critical prototype functions were demonstrated in a controlled synthetic scenario." They do not support claims of bias elimination, organizational validity, production readiness, or improved employee performance.
