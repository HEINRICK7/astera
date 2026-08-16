# Clinical Language Simulator Foundation

Status: LAB only. Candidate generation does not modify the Runtime or any
official corpus.

```text
historical v3/v4/v5 signals
            ↓
ClinicalLanguageSimulator
            ↓
candidate JSONL
            ↓
human review + gold annotation
            ↓
future v6 corpus
            ↓
Clinical Harness
```

The simulator has a provider-neutral `ClinicalLanguageGenerator` boundary.
The current implementation is deterministic and auditable. A future model-
backed generator may implement that protocol, but it cannot create gold or
write to the official corpus through this API.

Run it with:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_clinical_language_simulator \
  --output labs/terminology_benchmark/results/clinical-language-simulator-v6-candidates-2026-08-15.jsonl
```

Each record is `PENDING_REVIEW`, has no gold annotation, and includes source
error types, source case IDs and provenance. The generated artifact is a
review queue, not `pt_br_clinical_semantics_v6.jsonl`.

The current candidate set is based on historical signals for:

- multi-mention collision;
- dose and frequency attachment;
- temporal and negation scope;
- family-versus-patient experiencer;
- laterality attachment;
- status conflicts;
- generic attribute binding.

The initial-run manifest is explicitly labelled as a historical summary. It
does not replace the repaired v3/v4/v5 taxonomy reports or claim that repaired
cases are still failures.
