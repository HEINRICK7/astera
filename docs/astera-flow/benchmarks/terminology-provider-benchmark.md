# Terminology Provider Benchmark

Status: evaluation runner ready. The local run executes the deterministic
baselines; QuickUMLS, MedCAT and medspaCy remain `not_configured` until their
dependencies and authorized assets are supplied. No provider is promoted to
the Clinical Runtime.

## Tracks

The benchmark is intentionally split:

1. **Terminology/entity linking:** deterministic baseline, QuickUMLS and
   MedCAT.
2. **Clinical context:** deterministic baseline versus medspaCy plus NIEDE
   PT-BR rules.

QuickUMLS is evaluated as approximate concept matching. Its official project
documents CUI, similarity and semantic types in its matcher output and is
licensed under MIT for code; the prepared UMLS data directory is a separate
asset that must be identified and licensed. See the
[QuickUMLS repository](https://github.com/Georgetown-IR-Lab/QuickUMLS).

MedCAT is evaluated through its current `CAT.get_entities` API and supplied
model pack. The active project is
[CogStack/cogstack-nlp](https://github.com/CogStack/cogstack-nlp/); its docs
describe MedCAT v2 and model loading. The code repository is Apache-2.0, but
model/vocabulary licensing is recorded separately. The official documentation
explicitly notes that some model assets rely on UMLS/SNOMED licensing; see
[MedCAT model documentation](https://docs.cogstack.org/projects/nlp/en/latest/)
and the [UMLS/SNOMED license agreement](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/2021AB/license_agreement_snomed.html).

For the context track, medspaCy's official project describes ConText support
for negation and uncertainty and currently reports no Portuguese ConText rules
in its language table. The benchmark therefore treats NIEDE PT-BR rules as an
explicit asset, not as an assumed feature. See the
[medspaCy repository](https://github.com/medspacy/medspacy).

## Corpus

`labs/terminology_benchmark/data/pt_br_terminology_v1.jsonl` contains difficult
Brazilian Portuguese examples covering negation, uncertainty, family
experiencer, temporality, dose, abbreviations, allergy and laterality. Gold
annotations are versioned and include provenance-relevant spans.

The current ten cases are a smoke benchmark. They validate the harness and
must be expanded to a larger reviewed corpus before a production decision.

The first authorized context run measured medspaCy 1.3.1 plus the NIEDE
`niede-pt-br-context-v1` rules. Certainty improved to `0.917` and experiencer
to `1.000`, while negation measured `0.833` and dose remained `0.000`; the
hard gate therefore correctly remained closed. The run is recorded in
`labs/terminology_benchmark/results/provider-evaluation-2026-08-15.json`.

The subsequent hardening run introduced `HybridClinicalContextAdapter` and a
focused 21-case corpus. The hybrid reached `1.000` negation, `0.957`
certainty, `0.957` temporality, `1.000` experiencer, `1.000` dose and
`1.000` provenance. Its lab hard gate passed; this is not a production
certification. See
`labs/terminology_benchmark/results/context-hardening-2026-08-15.json`.

The adversarial v3 corpus now contains 80 compositional cases. The hybrid
achieved `0.905` negation, `0.884` certainty, `0.895` temporality, `0.886`
dose and `0.589` mention-exact-match. The gate correctly failed, exposing
interaction errors that aggregate attribute scores hide. See
`labs/terminology_benchmark/results/context-validation-v3-2026-08-15.json`.

## Promotion rule

The weighted score is advisory. A provider that loses negation, certainty,
dose or provenance cannot enter the clinical path, regardless of F1 or
latency. Every run must record provider version, corpus version, vocabulary or
model checksum, startup, CPU/RAM, latency and code/data/model licenses.
