# Context Lifetime Policy

Context validity is deterministic and multi-factor:

- candidate must precede the target turn;
- entity type must be compatible;
- topic transitions invalidate implicit carry-over;
- resolved/discontinued candidates require an explicit reference to be reused;
- speaker changes are allowed but affect candidate score;
- explicit references can reopen otherwise stale candidates.

This policy is intentionally not a fixed turn timeout. It is tested independently from the reference resolver.
