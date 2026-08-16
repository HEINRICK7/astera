# V6 Candidate Ownership Failure Analysis

Status: **HUMAN GATE — do not continue automatically**

Repair V3 failed the unchanged V6 thresholds. The failure is not a provenance failure and is not primarily a relation-generation failure. The regression is concentrated in mention composition and cross-segment resolution.

## Evidence

- mention exact: `0.7754 → 0.7485` versus Authoritative Cutover;
- cross-segment resolution: `0.6048 → 0.5323`;
- cross-mention isolation: `0.6204 → 0.5766`;
- relation exact: `0.8140 → 0.8140`;
- provenance: `1.0000 → 1.0000`;
- resolver overwrites: `84 → 162` compared with the previous authoritative run;
- legacy fallback: `0`;
- forced ambiguous resolutions: `0`.

## Leading structural hypothesis

The new question-answer binding is being applied before ownership is proven for every candidate. A preceding question can generate a valid typed answer candidate, but the V3 projection path must not materialize that candidate unless its owner is uniquely resolved. The current regression pattern is consistent with a candidate being applied to a target result when multiple compatible antecedents exist, or when a segment is interpreted as an answer without a sufficiently strong question boundary.

The next investigation must inspect `candidate_trace` alongside the 162 overwritten decisions and classify each as:

- uniquely owned and preserved;
- ambiguous owner incorrectly applied;
- unresolved owner incorrectly applied;
- question context incorrectly bound;
- legitimate authoritative change.

This classification is required before any further resolver change. Do not create V4/V7, execute holdouts, or enable shadow/production integration from this state.
