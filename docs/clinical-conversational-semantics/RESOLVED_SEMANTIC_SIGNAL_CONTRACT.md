# Resolved Semantic Signal Contract

Status: C2 upstream hardening implemented; D4 remains blocked.

This boundary sits between semantic resolution and relation compilation:

```text
local evidence / reference / conversation state
        ↓
ResolvedAttributeSignal / ResolvedTransitionSignal
        ↓
RelationInputContractReport
        ↓
ClinicalRelationCompiler
```

The compiler remains unchanged and receives only signals that have either
passed the contract or have been explicitly marked unresolved. An unresolved
signal never becomes a relation by default.

## Attribute signal

Every relation-bearing attribute has:

- `attribute_type`;
- `value`;
- `owner_mention_id`;
- `owner_type`;
- `state`: `current`, `historical` or explicit `unresolved`;
- `provenance.source_segment_ids`;
- confidence and evidence metadata.

The relation-bearing attributes are `dose`, `frequency`, `route`,
`laterality` and lifecycle `status`.

`owner_mention_id` and `owner_type` are mandatory for a resolved signal. A
missing owner produces `UNRESOLVED_OWNER`; it does not select a nearby owner.

## Transition signal

Every resolved transition has:

- attribute type and typed owner;
- distinct `previous_value` and `current_value`;
- explicit `transition_type`;
- optional temporal anchor;
- source provenance;
- state and confidence.

Missing `from`, `to`, owner or provenance produces an explicit unresolved or
ambiguous status. Mere coexistence of two values cannot create `CHANGED_FROM`.

## State semantics

Lifecycle status is a current state. The time of the event that caused a
discontinuation belongs to event/transition provenance and must not turn
`status=discontinued` into a historical entity state.

Historical dose/frequency values remain historical signals. A current value and
its transition evidence are represented separately.

## Contract gate

The contract reports four structural gates:

```text
relation_input_owner_completeness
relation_input_state_completeness
transition_contract_validity
relation_input_provenance
```

Valid resolved signals must score `1.00` on the applicable gate. The system may
return `UNRESOLVED_OWNER`, `UNRESOLVED_STATE` or `AMBIGUOUS`; that is a valid
outcome and is not converted into fabricated certainty.
