# Runtime raw data — encounter-90500cddfc32

Este arquivo preserva os dados técnicos finais recuperados da projeção autenticada do Runtime. Os valores abaixo são apresentados em formato JSON, sem interpretação clínica adicional.

> O payload completo original tem aproximadamente 826 MB (`/tmp/astera-final-review.json`) e não foi embutido neste Markdown para evitar um arquivo impraticável. Este documento contém os blocos brutos relevantes para auditoria e depuração.

## 1. Identificação e estado

```json
{
  "encounter_id": "encounter-90500cddfc32",
  "encounter_status": "in_progress",
  "review_status": "processed",
  "ended_at": null,
  "events": 15192,
  "a2ui_streams": 3056,
  "mentions": 18,
  "facts": 18,
  "hypotheses": 5,
  "first_event_at": "2026-08-11T12:30:08.327705+00:00",
  "last_event_at": "2026-08-11T13:04:41.922066+00:00",
  "source_file": "/tmp/astera-final-review.json"
}
```

## 2. Eventos terminais observados

```json
[
  {
    "type": "speech.stopped",
    "observed": true
  },
  {
    "type": "consultation.pipeline.completed",
    "observed": true
  }
]
```

## 3. Contagem bruta por tipo de evento

```json
{
  "speech.started": 1,
  "consultation.pipeline.started": 1,
  "transcript.created": 1,
  "transcript.partial": 1126,
  "speech.runtime.metrics": 2891,
  "clinical.runtime.status": 2366,
  "clinical.mention.detected": 1650,
  "clinical.fast.context.detected": 569,
  "clinical.fact.detected": 1650,
  "clinical.knowledge.event": 1650,
  "clinical.knowledge.updated": 1650,
  "clinical.fast.symptom.detected": 324,
  "clinical.fast.medication.detected": 63,
  "transcript.done": 114,
  "clinical.deep.context.updated": 44,
  "clinical.deep.reasoning.started": 44,
  "clinical.deep.reasoning.updated": 44,
  "clinical.representation.updated": 132,
  "clinical.fhir.updated": 44,
  "clinical.deep.soap.updated": 44,
  "clinical.soap.updated": 44,
  "clinical.deep.completed": 44,
  "clinical.fast.duration.detected": 205,
  "clinical.fast.severity.detected": 489,
  "speech.stopped": 1,
  "consultation.pipeline.completed": 1
}
```

## 4. Fatos finais — payload normalizado

```json
[
  {
    "category": "Condition",
    "value": "Hipertensão",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "condition.hypertension"
  },
  {
    "category": "Symptom",
    "value": "tontura",
    "polarity": "positive",
    "certainty": "uncertain",
    "confidence": 0.90,
    "code": "symptom.chest_pain"
  },
  {
    "category": "Medication",
    "value": "Losartana",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "medication.losartan"
  },
  {
    "category": "Symptom",
    "value": "Hematêmese",
    "polarity": "positive",
    "certainty": "uncertain",
    "confidence": 0.82,
    "review_required": true,
    "code": "symptom.hematemesis"
  },
  {
    "category": "Symptom",
    "value": "Vômito",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "symptom.vomiting"
  },
  {
    "category": "Lifestyle",
    "value": "Tabagismo",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "lifestyle.smoking"
  },
  {
    "category": "Condition",
    "value": "Hipertensão",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "condition.hypertension"
  },
  {
    "category": "Symptom",
    "value": "Dor torácica",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "symptom.chest_pain"
  },
  {
    "category": "Medication",
    "value": "Losartana",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "medication.losartan"
  },
  {
    "category": "Symptom",
    "value": "Hematêmese",
    "polarity": "negative",
    "certainty": "uncertain",
    "confidence": 0.82,
    "review_required": true,
    "code": "symptom.hematemesis"
  },
  {
    "category": "Symptom",
    "value": "Vômito",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "symptom.vomiting"
  },
  {
    "category": "Condition",
    "value": "Diabetes Mellitus",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "condition.diabetes_mellitus"
  },
  {
    "category": "Duration",
    "value": "20 anos",
    "semantic_value": 20,
    "unit": "anos",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.94,
    "code": "clinical.duration"
  },
  {
    "category": "Lifestyle",
    "value": "Tabagismo",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "lifestyle.smoking"
  },
  {
    "category": "Severity",
    "value": "seis",
    "polarity": "positive",
    "certainty": "uncertain",
    "confidence": 0.72,
    "code": "clinical.severity"
  },
  {
    "category": "Symptom",
    "value": "Febre",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "symptom.fever"
  },
  {
    "category": "Condition",
    "value": "Diabetes Mellitus",
    "polarity": "negative",
    "certainty": "reported",
    "confidence": 0.90,
    "code": "condition.diabetes_mellitus"
  },
  {
    "category": "Condition",
    "value": "Hemorragia Digestiva Alta",
    "polarity": "positive",
    "certainty": "reported",
    "confidence": 0.86,
    "code": "condition.upper_gi_bleeding"
  }
]
```

## 5. Knowledge Runtime

```json
{
  "version": 1650,
  "facts": 18,
  "graph_nodes": 18,
  "graph_edges": 4,
  "timeline_items": 18,
  "history_items": 1650,
  "edges": [
    {
      "relation": "HAS_MEDICATION",
      "source": "condition.hypertension",
      "target": "medication.losartan"
    },
    {
      "relation": "HAS_MEDICATION",
      "source": "condition.hypertension",
      "target": "medication.losartan"
    },
    {
      "relation": "HAS_DURATION",
      "source": "clinical.context",
      "target": "clinical.duration"
    },
    {
      "relation": "HAS_SEVERITY",
      "source": "clinical.context",
      "target": "clinical.severity"
    }
  ]
}
```

## 6. Reasoning Runtime — hipóteses

```json
[
  {
    "label": "Hemorragia digestiva alta",
    "confidence": 0.55,
    "status": "candidate_contradictory_evidence",
    "supporting_facts": [
      "Hemorragia Digestiva Alta",
      "Hematêmese",
      "Vômito"
    ],
    "missing": [
      "confirmação do sangue",
      "volume",
      "cor",
      "frequência",
      "melena",
      "instabilidade",
      "AINEs/anticoagulantes",
      "úlcera",
      "hemoglobina/hematócrito",
      "endoscopia"
    ],
    "conflicts": [
      "Hematêmese negativa",
      "Vômito negativo"
    ]
  },
  {
    "label": "Diabetes mellitus histórico relatado",
    "confidence": 0.48,
    "status": "candidate_needs_disambiguation",
    "supporting_facts": [
      "Diabetes Mellitus",
      "duração possivelmente associada de 2 anos"
    ],
    "missing": [
      "tipo",
      "tratamento",
      "controle",
      "complicações",
      "glicemia",
      "HbA1c"
    ],
    "conflicts": [
      "Diabetes Mellitus negativa"
    ]
  },
  {
    "label": "Hipertensão arterial",
    "confidence": 0.40,
    "status": "candidate_contradictory_evidence",
    "supporting_facts": [
      "Hipertensão",
      "Losartana"
    ],
    "missing": [
      "pressão arterial",
      "dose",
      "frequência",
      "adesão",
      "duração"
    ],
    "conflicts": [
      "Hipertensão negativa",
      "Losartana negativa"
    ]
  },
  {
    "label": "Dor torácica em esclarecimento",
    "confidence": 0.35,
    "status": "candidate_contradictory_evidence",
    "supporting_facts": [
      "Dor torácica inicial",
      "Tabagismo"
    ],
    "missing": [
      "caráter",
      "irradiação",
      "gatilhos",
      "dispneia",
      "sudorese",
      "duração",
      "ECG",
      "troponina"
    ],
    "conflicts": [
      "Dor torácica negativa",
      "Tabagismo negativo"
    ]
  },
  {
    "label": "Processo infeccioso sistêmico agudo menos provável no momento",
    "confidence": 0.22,
    "status": "low_likelihood",
    "supporting_facts": [],
    "missing": [],
    "conflicts": [
      "Febre negativa"
    ]
  }
]
```

## 7. Perguntas e lacunas finais

```json
[
  {
    "priority": "critical",
    "question": "Houve vômito com sangue vivo ou em borra de café? Quantas vezes, volume estimado e há melena?"
  },
  {
    "priority": "critical",
    "question": "Quais são PA, FC, sinais de hipovolemia e hemoglobina atual?"
  },
  {
    "priority": "high",
    "question": "O paciente confirma ou nega hipertensão e uso atual de losartana? Houve correção de relato anterior?"
  },
  {
    "priority": "high",
    "question": "Há diagnóstico de diabetes? Se sim, há quantos anos, tipo e tratamento?"
  },
  {
    "priority": "high",
    "question": "A dor torácica está presente agora? Qual início, qualidade, relação com esforço/refeição e sintomas associados?"
  },
  {
    "priority": "moderate",
    "question": "Fuma atualmente? Carga tabágica (maços-ano) ou cessou quando?"
  },
  {
    "priority": "moderate",
    "question": "O valor ‘seis’ refere-se a escala de dor 0–10 ou a outro parâmetro?"
  }
]
```

## 8. SOAP bruto retornado

```json
{
  "subjective": {
    "chief_complaint": "Dor torácica",
    "status": "documented",
    "narrative": "Paciente relata Dor torácica. Os demais fatos permanecem vinculados à sua evidência e aguardam revisão clínica."
  },
  "objective": {
    "status": "not_documented",
    "findings": [],
    "narrative": "Nenhum sinal vital, exame físico ou resultado objetivo foi documentado."
  },
  "assessment": {
    "status": "pending_clinician_review",
    "candidate_hypotheses": 5,
    "narrative": "Há hipóteses candidatas para revisão clínica; nenhum diagnóstico definitivo foi gerado."
  },
  "plan": {
    "status": "pending_clinician_review",
    "documented_next_steps": [],
    "open_questions": 7,
    "narrative": "Revisar os dados, completar o exame clínico e definir a conduta."
  }
}
```

## 9. Representações geradas

```json
{
  "soap": true,
  "fhir": {
    "resourceType": "DocumentReference",
    "generated": true
  },
  "clinical_graph": true,
  "presentation_objects": true
}
```

## 10. A2UI bruto — operações e componentes

```json
{
  "stream_count": 3056,
  "operation_counts": {
    "state": 1,
    "patch": 7011,
    "create": 655,
    "archive": 624
  },
  "component_counts": {
    "ClinicalHistoryCard": 5,
    "TimelineCard": 1,
    "ClinicalProblemCard": 7,
    "MedicationProfileCard": 2,
    "QuestionCard": 331,
    "HypothesisCard": 219,
    "ClinicalSummaryCard": 44,
    "SOAPProgressCard": 44,
    "ObservationCard": 2,
    "state_entries_or_fallback": 7636
  }
}
```

## 11. Transcript bruto

O transcript final bruto está preservado na projeção original e possui:

```json
{
  "character_count": 31469,
  "final_segment_count": 114,
  "partial_segment_count": 1126,
  "transcript_available": true,
  "raw_source": "/tmp/astera-final-review.json"
}
```

O payload original contém segmentos repetidos e sobrepostos. Para manter este arquivo legível, os 31.469 caracteres não foram duplicados aqui; o arquivo fonte acima é a referência bruta integral.

## 12. Diagnóstico técnico do payload

```json
{
  "review_terminal": true,
  "encounter_terminal": false,
  "presentation_empty": false,
  "duplicate_or_amplified_event_volume": true,
  "polarity_conflicts_present": true,
  "normalization_error_present": true,
  "clinical_values_without_context": true,
  "objective_measurements_present_in_soap": false
}
```

## 13. Reprodução da coleta

O JSON completo utilizado como origem desta documentação está em:

```text
/tmp/astera-final-review.json
```

Para auditoria local, consultar o endpoint autenticado de Clinical Review da sessão `encounter-90500cddfc32` e comparar com os campos acima. Este Markdown é um extrato técnico estático do snapshot final recuperado em 11/08/2026.
