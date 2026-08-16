# Relation Writer Retirement Record

## Retired final writers

The following paths no longer write the final projection relation set:

- local safety/context rules;
- cross-segment continuity;
- relation resolver/materializer helpers;
- any post-resolution attribute attachment path.

They may produce candidates, transition evidence or ownership provenance. They
must not assign to `projection["relations"]`, mutate a compiled relation set,
or reconstruct a second authoritative relation graph.

## Compatibility boundary

`ClinicalRelationMaterializer` remains available for historical unit tests and
compatibility callers. It is explicitly legacy and must not be used by the
runtime projection path. New code must call:

```python
relation_set = ClinicalRelationCompiler().compile(resolved_semantics)
```

The only production serialization site is
`AuthoritativeProjectionWriter.materialize`.

## Verification record

The static architecture test verifies one final projection assignment across
the production relation path and zero such assignments in local or
cross-segment modules. Focused compiler, legacy regression and projection
tests are required before the compiler is declared a frozen candidate.

## Forbidden reintroduction

Do not reintroduce relation creation into local rules, cross-segment adapters,
projection post-processors or benchmark-specific code. If a new relation type
is needed, add its semantic signal/contract first and extend the compiler with
an invariant and a synthetic test.
