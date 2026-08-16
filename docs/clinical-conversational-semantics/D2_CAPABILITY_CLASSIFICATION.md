# D2 Capability Classification

Status: **HUMAN GATE**

## Classification

- `G1`: `14`
- `G2`: `0`
- `G3`: `0`
- `G4`: `0`
- `INDETERMINATE`: `14`

## Boundary result

- Trace v2 cases: `36/36` valid.
- First divergence at `generated_relations`: `14`.
- First divergence at `prediction`: `14`.
- Relation exact: `0.133333`.
- Relation materialization: `0.235294`.
- Relation provenance: `0.235294`.
- Overall provenance: `1.000000`.

Compared with historical D1, mention and cross-segment scores improved in
this sample, while relation exact decreased from `0.176471` to `0.133333`.
This is not evidence that the relation repair generalized; it is a signal for
the next human review.

G3 and G4 are not inferred from low scores. This run does not authorize repair, D1/V7 rerun, provider introduction, Shadow Integration, or Production.

## Recommended next milestone

Review the v2 first-divergence matrix and authorize only a focused change supported by preserved evidence.
