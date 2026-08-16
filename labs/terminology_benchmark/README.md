# Terminology and Clinical Context Benchmark

This is an experimental lab. It is not imported by the Astera bootstrap and
does not promote any provider into the Clinical Runtime.

## Two separate tracks

### Track A — terminology/entity linking

```text
Canonical Evidence → TerminologyPort →
  deterministic baseline | QuickUMLS | MedCAT
                         → TerminologyResult
```

Run the dependency-free baseline:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_baseline
```

QuickUMLS and MedCAT adapters are lazy and require explicit assets. They are
not part of `requirements.txt`:

```bash
pip install -r labs/terminology_benchmark/requirements-optional.txt
```

The operator must provide a prepared QuickUMLS data directory or a MedCAT
model pack and fill the vocabulary/model license metadata before comparing
results.

Explicit provider runs use:

```bash
python -m labs.terminology_benchmark.run_provider \
  --provider quickumls \
  --asset-path /path/to/quickumls-data \
  --vocabulary-version UMLS-RELEASE \
  --data-license "LICENSE-REFERENCE"
```

### Track B — clinical context

```text
Canonical Mention → ClinicalContextPort →
  deterministic PT-BR baseline | medspaCy + NIEDE PT-BR rules
                              → ClinicalContextResult
```

The context harness measures negation, certainty, temporality, experiencer,
laterality, dose and provenance independently of terminology linking. The
current baseline can be invoked from Python with:

```python
from labs.terminology_benchmark.context_harness import print_baseline
print_baseline()
```

Or directly:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_context
```

Run the complete configured evaluation and receive explicit statuses for
providers whose dependencies or licensed assets are absent:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_evaluation \
  --output /tmp/terminology-provider-evaluation.json
```

Add `--quickumls-path`, `--medcat-path` and `--medspacy-model` only when the
operator has prepared and authorized those assets. The runner never downloads
UMLS, SNOMED or model packs automatically.

Asset authorization is controlled by
`labs/terminology_benchmark/data/provider_asset_registry.json`. To execute the
context track once medspaCy is installed, use:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_evaluation \
  --run-medspacy \
  --output /tmp/provider-evaluation.json
```

The runner validates the checksum of the NIEDE PT-BR rules before loading the
adapter.

For the focused hardening corpus, run:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_context_hardening \
  --output /tmp/context-hardening.json
```

This compares raw medspaCy against `HybridClinicalContextAdapter`, where
NIEDE deterministic safety rules have precedence for high-risk fields.

Run the adversarial v3 validation with:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_context_hardening \
  --corpus labs/terminology_benchmark/data/pt_br_clinical_semantics_v3.jsonl \
  --output /tmp/context-v3.json
```

The v3 gate includes `mention_exact_match`: all expected critical attributes
for one mention must be correct together, not merely correct in aggregate.

The unseen v4 validation corpus contains 100 new cases and 134 mentions. It
also enables the stricter composition gate for `relation_exact_match`,
`scope_accuracy` and `cross_mention_isolation`:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_context_hardening \
  --corpus labs/terminology_benchmark/data/pt_br_clinical_semantics_v4.jsonl \
  --output labs/terminology_benchmark/results/context-validation-v4-2026-08-15.json
```

v4 is a frozen unseen validation corpus. The initial run failed as expected;
the subsequent composition repair is recorded in
`results/context-validation-v4-2026-08-15.json`. The gate now passes, but
Shadow Integration and production promotion remain blocked until a new v5
unseen corpus validates generalization.

The v5 generalization corpus contains 120 new cases and 207 mentions. Its
stricter gate uses relation accuracy >= 0.95, scope accuracy >= 0.97 and
cross-mention isolation >= 0.95:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_context_hardening \
  --corpus labs/terminology_benchmark/data/pt_br_clinical_semantics_v5.jsonl \
  --output labs/terminology_benchmark/results/context-validation-v5-2026-08-15.json
```

The first frozen-code run and the subsequent immutable-corpus composition
repair are recorded in the v5 result, taxonomy and repair files. The repaired
run passes the v5 laboratory gate; it does not authorize production promotion.

No medspaCy dependency is installed by this milestone. The NIEDE PT-BR rule
asset is versioned locally and is loaded only by the experimental adapter.

## Clinical Language Simulator

The simulator generates LAB-only candidates for future unseen corpora from
historical v3/v4/v5 composition signals. Candidates are provider-neutral,
deterministic for now, disjoint from official corpora and always marked
`PENDING_REVIEW`. They never receive gold automatically and never enter the
Runtime:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_clinical_language_simulator \
  --output labs/terminology_benchmark/results/clinical-language-simulator-v6-candidates-2026-08-15.jsonl
```

See `CLINICAL_LANGUAGE_SIMULATOR.md` for the review boundary and the future
provider contract.

Display the read-only human review queue with:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_review_queue
```

The queue shows candidate text, historical origin, error taxonomy and
provenance. Mentions and relations remain explicitly pending; this command
cannot approve candidates or mutate any official corpus.

Create an editable review worksheet outside the corpus:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_review_queue \
  --output labs/terminology_benchmark/results/v6-human-review-2026-08-15.json
```

Edit only that JSON file. Set each `decision` to `APPROVED` or `REJECTED`,
fill `reviewer`, `review_notes` and `gold`, then validate it with:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_review_validation \
  --review labs/terminology_benchmark/results/v6-human-review-2026-08-15.json
```

The validator does not create the official V6 corpus.

For the final quota gap, generate the small cross-segment micro-expansion:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_micro_expansion
```

It creates four new candidates, `sim-v6-0055` through `sim-v6-0058`, in
`PENDING_REVIEW` with no gold. Their review worksheet is
`results/v6-human-review-micro-expansion-2026-08-15.json`.

Expand the review queue without reusing prior corpora, the V6 draft or the
first 14 candidates:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_simulator_expansion
```

This creates 40 new `PENDING_REVIEW` candidates with no gold, including 6
structured cross-segment conversations. Review them in
`results/v6-human-review-expansion-2026-08-15.json` and validate with:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_review_validation \
  --candidates labs/terminology_benchmark/results/clinical-language-simulator-v6-expansion-2026-08-15.jsonl \
  --review labs/terminology_benchmark/results/v6-human-review-expansion-2026-08-15.json
```

## V6 independent generalization

The V6 draft adds independent cases, realistic/STT-like language and
multi-segment conversations. It is not the official V6 corpus while simulator
candidates remain pending human review. Conversational golds carry explicit
segment ownership plus attribute/relation provenance; the assembler rejects
cases that omit that traceability. The assembler must fail closed if the
planned source proportions are incomplete. See
`V6_INDEPENDENT_GENERALIZATION.md`.

## Metrics and hard gate

Track A reports exact-span entity precision/recall, linking accuracy, false
positives, attribute accuracy, provenance completeness, concept stability,
latency (mean/p50/p95), CPU time, RSS, startup time, asset size and licensing
metadata. The scorecard is:

| Dimension | Weight |
|---|---:|
| Clinical accuracy | 40% |
| PT-BR robustness | 20% |
| CPU/RAM | 15% |
| Operational simplicity | 10% |
| Licensing | 10% |
| Maintainability | 5% |

The hard gate is independent of the weighted score: a provider cannot be
promoted if critical context/provenance preservation fails. A higher F1 does
not override a failure in negation, certainty, dose or provenance.

## Asset and license recording

QuickUMLS uses approximate matching against a prepared UMLS-derived data
directory; record the exact vocabulary release and license. MedCAT code and
model/vocabulary assets are recorded separately. A permissive code license
does not automatically grant rights to redistribute UMLS/SNOMED-derived data.

The benchmark must keep the corpus, provider version, asset checksum, model
card and license metadata alongside every result.

The first authorized context run is recorded in
`results/provider-evaluation-2026-08-15.json`. It is a smoke-benchmark result,
not a production certification.
