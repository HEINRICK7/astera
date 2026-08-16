# V6 Resolved Semantics vs Gold Failure Analysis

Status: **HUMAN GATE**

After the projection integrity gate passed, the frozen V6 was reexecuted once. The result remained unchanged:

| Metric | Result |
|---|---:|
| mention exact | 0.7485 |
| relation exact | 0.8140 |
| cross-segment resolution | 0.5323 |
| cross-mention isolation | 0.5766 |
| provenance | 1.0000 |

Projection preservation, relation preservation, ownership preservation, and evaluation preservation were all 1.0000 in the end-to-end trace. Therefore the remaining failure is not a writer/materialization loss.

The candidate-quality gate is an engineering fixture gate and is not sufficient evidence of V6 semantic accuracy. The real V6 trace shows the remaining gap is between resolved semantics and gold semantics, plus relation comparison/normalization mismatches in the evaluation contract.

The reported 162 authority overwrites are repeated instrumentation across three V3 harness passes. The trace found 54 unique local-to-resolved field changes, all preserved by projection.

No V6 corpus data was changed. Holdouts, V7, Shadow Integration, and provider work remain blocked.
