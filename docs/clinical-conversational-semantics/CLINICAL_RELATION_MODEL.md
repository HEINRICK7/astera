# Clinical Relation Model

Relations are projected as first-class values with relation ID, type, source mention, target mention/value, source segment IDs, confidence and provenance.

The current vocabulary preserves existing names and supports `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_ROUTE`, `HAS_LATERALITY`, `HAS_STATUS`, `EXPERIENCER_OF`, `CHANGED_FROM`, `CHANGED_TO` and `REFERS_TO`. Existing `DISCONTINUED_AT` remains supported for compatibility with the current contract.

Repair V2 improved transition relations but failed the relation gate at `0.8140`. No holdout was run.
