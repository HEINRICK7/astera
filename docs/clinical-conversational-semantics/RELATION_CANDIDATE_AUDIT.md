# Relation Candidate Audit

Relations are projected only after endpoint ownership is resolved. The audit checks:

- one source mention ID;
- one target mention ID where the relation has a target;
- a stable relation ID;
- source segment provenance;
- no duplicate `(relation_type, source, target, value)` tuple;
- unresolved or ambiguous attribute attachments do not produce relations.

The deterministic candidate-quality gate generated one owned dose relation with unique endpoints and complete provenance. Relation candidate recall and endpoint accuracy were both 1.00 in the internal fixture suite. The V6 comparison remains a separate final projection measurement and is not used to reinterpret this engineering gate.
