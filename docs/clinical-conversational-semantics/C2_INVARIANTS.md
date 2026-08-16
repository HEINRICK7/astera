# C2 Upstream Signal Invariants

1. A relation-bearing resolved attribute has a non-null owner mention and
   typed owner.
2. A signal carries explicit `current`, `historical` or `unresolved` state.
3. Lifecycle status is current state; event time is separate provenance.
4. A transition has explicit previous and current values.
5. Previous and current transition values cannot be identical.
6. A transition cannot be emitted from mere coexistence of two values.
7. Every relation-ready signal has source segment provenance.
8. Missing owner becomes `UNRESOLVED_OWNER`.
9. Missing state/provenance becomes `UNRESOLVED_STATE`.
10. An ambiguous transition becomes `AMBIGUOUS`.
11. Blocking signals prevent a `RESOLVED` relation input contract.
12. No external clinical knowledge fills owner, state, transition or provenance.
13. The ClinicalRelationCompiler remains unchanged and does not infer signals.
14. D1, D2, D3, V7, policy and gold remain immutable.

## Synthetic gate

The dedicated C2 contract tests cover:

- explicit owner and provenance;
- historical attribute state;
- valid dose transition;
- missing owner transition;
- identical from/to ambiguity;
- aggregate completeness and blocking behavior.

All dedicated and relation regression tests must pass before D4 can be
considered for authorization.
