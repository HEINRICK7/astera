# D1 First Divergence Report

Status: **HUMAN GATE**

The report was produced from saved D1 traces after the one-shot run. No resolver was invoked by the analyzer.

## First divergence stages

- `prediction`: `16`
- `generated_relations`: `15`

## D1 metrics

- `mention_exact_match`: `0.139535`
- `relation_exact_match`: `0.176471`
- `cross_segment_resolution`: `0.125000`
- `cross_mention_isolation`: `0.138889`
- `provenance`: `1.000000`

## Findings

- `D1-002` — `generated_relations` / `relations`: `[]` → `[{'confidence': 1.0, 'provenance': {'attribute': 'frequency', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s3']}, 'relation_id': 'context:s1:HAS_FREQUENCY:frequency', 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s3'], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'à noite'}]`; confidence `0.86`; class `G1`
- `D1-003` — `prediction` / `temporality`: `past` → `current`; confidence `0.55`; class `UNDETERMINED`
- `D1-004` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-005` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'todas as noites'}]` → `[]`; confidence `0.86`; class `G1`
- `D1-006` — `prediction` / `experiencer`: `family` → `patient`; confidence `0.55`; class `UNDETERMINED`
- `D1-008` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-010` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '25 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '12,5 mg'}]` → `[{'confidence': 1.0, 'provenance': {'rule': 'ptbr-dose'}, 'relation_id': None, 'relation_type': 'HAS_DOSE', 'source': 'context:s1:10:20', 'source_mention_id': 'context:s1:10:20', 'source_segment_ids': [], 'target': 'dose', 'target_mention_id': 'dose', 'value': '25 mg'}]`; confidence `0.86`; class `G1`
- `D1-011` — `generated_relations` / `relations`: `[{'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}, {'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}]` → `[]`; confidence `0.86`; class `G1`
- `D1-012` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-013` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '300 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '400 mg'}]` → `[{'confidence': 1.0, 'provenance': {'rule': 'ptbr-dose'}, 'relation_id': None, 'relation_type': 'HAS_DOSE', 'source': 'context:s1:2:13', 'source_mention_id': 'context:s1:2:13', 'source_segment_ids': [], 'target': 'dose', 'target_mention_id': 'dose', 'value': '300 mg'}]`; confidence `0.86`; class `G1`
- `D1-014` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '14 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '7 mg'}]` → `[{'confidence': 1.0, 'provenance': {'rule': 'ptbr-dose'}, 'relation_id': None, 'relation_type': 'HAS_DOSE', 'source': 'context:s1:2:21', 'source_mention_id': 'context:s1:2:21', 'source_segment_ids': [], 'target': 'dose', 'target_mention_id': 'dose', 'value': '14 mg'}, {'confidence': 1.0, 'provenance': {'source_segment_ids': ['s1']}, 'relation_id': 'context:s1:11:30:CHANGED_FROM:dose:14 mg', 'relation_type': 'CHANGED_FROM', 'source': 'context:s1:11:30', 'source_mention_id': 'context:s1:11:30', 'source_segment_ids': ['s1'], 'target': 'dose', 'target_mention_id': 'dose', 'value': '14 mg'}]`; confidence `0.86`; class `G1`
- `D1-015` — `prediction` / `status`: `active` → `None`; confidence `0.55`; class `UNDETERMINED`
- `D1-016` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'duas vezes ao dia'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'uma vez ao dia'}]` → `[{'confidence': 1.0, 'provenance': {'rule': 'ptbr-frequency'}, 'relation_id': None, 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1:11:19', 'source_mention_id': 'context:s1:11:19', 'source_segment_ids': [], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'duas vezes ao dia'}]`; confidence `0.86`; class `G1`
- `D1-017` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'pela manhã'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}]` → `[{'confidence': 1.0, 'provenance': {'attribute': 'frequency', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s3']}, 'relation_id': 'context:s1:HAS_FREQUENCY:frequency', 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s3'], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'depois do jantar'}]`; confidence `0.86`; class `G1`
- `D1-018` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'dias alternados'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'todos os dias'}]` → `[]`; confidence `0.86`; class `G1`
- `D1-019` — `generated_relations` / `relations`: `[]` → `[{'confidence': 1.0, 'provenance': {'attribute': 'frequency', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s3']}, 'relation_id': 'context:s1:HAS_FREQUENCY:frequency', 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s3'], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'pela manhã'}]`; confidence `0.86`; class `G1`
- `D1-020` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-021` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-022` — `prediction` / `temporality`: `current` → `past`; confidence `0.55`; class `UNDETERMINED`
- `D1-023` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-024` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-025` — `generated_relations` / `relations`: `[]` → `[{'confidence': 1.0, 'provenance': {'attribute': 'frequency', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s2']}, 'relation_id': 'context:s1:HAS_FREQUENCY:frequency', 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s2'], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'depois do café'}]`; confidence `0.86`; class `G1`
- `D1-027` — `generated_relations` / `relations`: `[]` → `[{'confidence': 1.0, 'provenance': {'attribute': 'frequency', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s2']}, 'relation_id': 'context:s1:HAS_FREQUENCY:frequency', 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s2'], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'à noite'}]`; confidence `0.86`; class `G1`
- `D1-028` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '40 mg'}]` → `[]`; confidence `0.86`; class `G1`
- `D1-030` — `prediction` / `temporality`: `current` → `past`; confidence `0.55`; class `UNDETERMINED`
- `D1-031` — `prediction` / `certainty`: `possible` → `confirmed`; confidence `0.55`; class `UNDETERMINED`
- `D1-032` — `prediction` / `temporality`: `past` → `current`; confidence `0.55`; class `UNDETERMINED`
- `D1-033` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'left'}]` → `[{'confidence': 1.0, 'provenance': {'rule': 'ptbr-nearest-laterality'}, 'relation_id': None, 'relation_type': 'HAS_LATERALITY', 'source': 'context:s1:2:7', 'source_mention_id': 'context:s1:2:7', 'source_segment_ids': [], 'target': 'laterality', 'target_mention_id': 'laterality', 'value': 'right'}, {'confidence': 1.0, 'provenance': {'attribute': 'laterality', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s2']}, 'relation_id': 'context:s1:HAS_LATERALITY:laterality', 'relation_type': 'HAS_LATERALITY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s2'], 'target': 'laterality', 'target_mention_id': 'laterality', 'value': 'left'}]`; confidence `0.86`; class `G1`
- `D1-034` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `UNDETERMINED`
- `D1-035` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'à noite'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'de manhã'}]` → `[{'confidence': 1.0, 'provenance': {'attribute': 'frequency', 'rule': 'resolved-attribute-materialization', 'source_segment_ids': ['s2']}, 'relation_id': 'context:s1:HAS_FREQUENCY:frequency', 'relation_type': 'HAS_FREQUENCY', 'source': 'context:s1', 'source_mention_id': 'context:s1', 'source_segment_ids': ['s2'], 'target': 'frequency', 'target_mention_id': 'frequency', 'value': 'de manhã'}]`; confidence `0.86`; class `G1`
- `D1-036` — `prediction` / `certainty`: `possible` → `confirmed`; confidence `0.55`; class `UNDETERMINED`

G3 and G4 are not inferred automatically. A low score or an unresolved finding is not evidence by itself of a missing capability or LLM requirement.
