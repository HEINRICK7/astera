# V5 Composition Repair

Status: complete in laboratory; production promotion blocked.

The v5 corpus was kept immutable throughout the repair. The implementation
was corrected in the following order:

1. isolated coordinated negation and contrastive clauses;
2. attached dose and frequency to the owning mention;
3. added explicit local temporal ownership and restart precedence;
4. separated family experiencer from patient scope;
5. restricted medication status to relevant targets.

Final result on 120 cases and 207 mentions:

- mention exact match: `1.000`
- relation exact match: `1.000`
- scope accuracy: `1.000`
- cross-mention isolation: `1.000`
- provenance: `1.000`
- hard gate: `PASS`

The adapters remain experimental. No provider is connected to the production
Clinical Runtime, and Shadow Integration remains blocked pending v6 unseen
validation.
