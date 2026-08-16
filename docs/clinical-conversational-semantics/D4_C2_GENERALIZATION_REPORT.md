# D4 C2 Generalization Report

Gate: **FAIL**

Relation metadata metrics were corrected offline from serialized provenance; no D4 rerun occurred.
Relation metadata metrics were corrected offline from serialized provenance; no D4 rerun occurred.
C2 validation requires unseen owner/state correctness >= 0.90, transition validity >= 0.90, provenance = 1.00, zero silent invalid relation creation, and clear downstream improvement versus D3.

## Required gate

- `relation_input_owner_completeness`: `0.645161`
- `relation_input_state_completeness`: `0.612903`
- `transition_contract_validity`: `0.000000`
- `relation_input_provenance`: `0.451613`
- `silent_invalid_relation_creation`: `0`

## Downstream result

- `relation_exact_match`: `0.520000`
- `relation_materialization`: `0.560000`
- `relation_owner_accuracy`: `0.451613`
- `relation_endpoint_accuracy`: `0.516129`
- `current_vs_historical_accuracy`: `0.560000`
- `transition_compilation_accuracy`: `0.000000`
- `relation_provenance_accuracy`: `0.451613`

Historical D3 comparison: owner `0.1915`, current/historical `0.2564`, transition `0.6250`, materialization `0.2564`. The D4 relation metrics are not a clean pass because transition and signal-contract quality remain below the gate.

## Decision

C2 upstream signal hardening is not promoted beyond the HUMAN GATE by this artifact. No C2.1, repair, rerun or benchmark mutation is authorized.
