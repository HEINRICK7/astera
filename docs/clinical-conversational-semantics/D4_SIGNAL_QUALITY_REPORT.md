# D4 Signal Quality Report

Status: **HUMAN GATE**

Offline reanalysis: **performed from persisted traces; resolver rerun = false**
Offline reanalysis: **performed from persisted traces; resolver rerun = false**
D4 was executed once against a frozen, unseen corpus. Gold was created without resolver or runtime predictions.

## Signal metrics

- `relation_input_owner_completeness`: `0.645161`
- `relation_input_state_completeness`: `0.612903`
- `transition_contract_validity`: `0.000000`
- `relation_input_provenance`: `0.451613`
- `unresolved_signal_rate`: `0.235294`
- `ambiguous_signal_rate`: `0.500000`
- `silent_invalid_relation_creation`: `0`

## Downstream metrics

- `relation_exact_match`: `0.520000`
- `relation_materialization`: `0.560000`
- `relation_owner_accuracy`: `0.451613`
- `relation_endpoint_accuracy`: `0.516129`
- `current_vs_historical_accuracy`: `0.560000`
- `transition_compilation_accuracy`: `0.000000`
- `relation_provenance_accuracy`: `0.451613`
- `mention_exact_match`: `0.111111`
- `cross_segment_resolution`: `0.111111`
- `trace_provenance`: `1.000000`

## Safe refusal

UNRESOLVED_OWNER, UNRESOLVED_STATE and AMBIGUOUS are not penalized when the corresponding gold signal is semantically insufficient. Invalid relation creation remains a contract violation.

## Comparison with D3

- D3 owner accuracy: `0.1915`
- D3 current/historical accuracy: `0.2564`
- D3 transition compilation: `0.6250`
- D3 relation materialization: `0.2564`

No repair or rerun is authorized from this report.
