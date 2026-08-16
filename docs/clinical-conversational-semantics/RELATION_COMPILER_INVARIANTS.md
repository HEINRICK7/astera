# Clinical Relation Compiler — Invariants

These invariants define the R2 architecture boundary. They are enforced by
focused synthetic tests and should remain true for every future relation change.

## Authority and immutability

1. `ClinicalRelationCompiler` is the only component that creates the final
   `ClinicalRelationSet`.
2. `AuthoritativeProjectionWriter` serializes that set exactly once.
3. No post-compiler code may append, remove, rewrite or normalize a relation.
4. The final relation container is a tuple and its relation provenance is
   immutable.
5. Duplicate keys `(relation_type, source, target, value)` are rejected.

## Ownership

6. A derived attribute relation is emitted only when the attribute owner is a
   compatible clinical entity type.
7. The relation source is the attribute owner mention, never the nearest
   unrelated mention.
8. Attribute provenance is copied from the owning evidence and is not replaced
   by compiler-local evidence.
9. An explicit relation contract may provide its own endpoints; otherwise
   compiler-derived relations use the resolved owner.

## Current state and transitions

10. Current dose/frequency values produce `HAS_DOSE`/`HAS_FREQUENCY` for the
    current value only.
11. A previous value produces `CHANGED_FROM` (or another explicit transition
    relation), never a second current-value relation.
12. `status=discontinued` produces `DISCONTINUED_AT` only for medication or
    treatment owners and only when the status is resolved.

## Provenance and unresolved states

13. Every compiler-created relation carries the attribute or transition source
    segment IDs that supported it.
14. `AMBIGUOUS` and `UNRESOLVED` resolutions are not forced into a new
    contextual relation decision.
15. The compiler never uses `case_id`, benchmark gold, provider output or a
    V6/V7-specific exception.

## Architecture fitness gates

The cutover gate is PASS only if all of the following hold:

```text
final relation writer count       = 1
post-compiler mutation sites      = 0
duplicate relation authorities    = 0
focused compiler tests            = PASS
regression tests                   = PASS
compileall                         = PASS
git diff --check                   = PASS
```
