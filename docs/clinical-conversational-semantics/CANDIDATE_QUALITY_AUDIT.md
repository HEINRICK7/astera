# Candidate Quality Audit — V6

Date: 2026-08-15  
Corpus: frozen V6 official corpus  
Checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

The audit separates engineering candidate quality from final projection quality. Local semantics produce typed candidates; context resolvers rank and constrain them; projection consumes only resolved semantics.

## Internal engineering gate

The deterministic fixture suite passed every required threshold:

| Metric | Result | Gate |
|---|---:|---:|
| candidate recall | 1.00 | >= 0.95 |
| candidate precision | 1.00 | >= 0.95 |
| antecedent top-1 | 1.00 | >= 0.90 |
| attribute owner accuracy | 1.00 | >= 0.95 |
| relation candidate recall | 1.00 | >= 0.95 |
| provenance completeness | 1.00 | = 1.00 |

The fixtures also prove that ambiguity and unresolved references remain explicit, incompatible attribute owners are rejected, and relation endpoints remain unique. The machine-readable record is [candidate-quality-gate-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/candidate-quality-gate-2026-08-15.json).

## Frozen-corpus observation

The pre-existing normalization layer produced 27 local normalized candidates for 130 segment-linked gold mentions, with a surface-recall observation of 0.1615. This is a diagnostic of local normalizer surface coverage, not a claim about final V6 candidate recall: the benchmark query itself provides the target span and the contextual layer preserves it as a candidate. It is recorded because it identifies a separate lexical-coverage limitation that must not be confused with ownership resolution.

No reserve case was loaded or executed. Holdout evaluation remains `NOT_EXECUTED`.
