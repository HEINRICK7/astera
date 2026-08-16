# 01 — Clinical Facts

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Workshop origem** | Workshop 1 — Clinical Facts |
| **ADR** | ADR-004 |
| **Responsável** | Clinical Facts Specialist |

## Objetivo

Definir a menor unidade de informação clínica verificável, contextualizada e
rastreável. Clinical Fact MUST ser independente de SOAP, FHIR, CID, prompt,
LLM e provider.

## Definições

- **Clinical Fact:** observação, relato, medida ou informação importada sobre
  paciente/encounter.
- **Clinical Assertion:** afirmação candidata, ainda sujeita a validação.
- **Clinical Evidence:** suporte que aumenta ou reduz força de hipótese.
- **Provenance:** cadeia que explica origem, transformação e revisão.

## Diagrama

```text
Fonte → Assertion → Clinical Fact Candidate → Validação → Context
```

## Exemplos

`dor torácica`, `nega febre`, `pressão arterial 150/90` e `alergia à
dipirona` são facts distintos, com fontes, polaridade e temporalidade próprias.

## Entidade

```text
ClinicalFact
├── id / type / category / value / unit
├── subject / patient / encounter
├── source / provenance
├── confidence / certainty / polarity
├── observed_at / valid_at
├── status / version
└── metadata
```

## Contrato normativo

```json
{
  "id": "fact-123",
  "category": "symptom",
  "value": "dor torácica",
  "subject": "patient-123",
  "encounter": "enc-456",
  "source": "patient_report",
  "polarity": "positive",
  "certainty": "reported",
  "status": "candidate",
  "observed_at": "2026-08-07T09:00:00-03:00",
  "provenance": {"source_ref": "transcript-segment-8"}
}
```

## Responsabilidades e eventos

O Facts Specialist MAY extrair assertions e MUST preservar origem. O Runtime
MUST validar transições e emitir `clinical.fact.detected`,
`clinical.fact.validated` ou `clinical.fact.updated`.

## Regras e restrições

1. Confidence de extração MUST NOT ser apresentada como verdade clínica.
2. Negação, incerteza e contradição MUST ser explícitas.
3. Atualização MUST criar revisão; não apagar histórico.
4. Fact MUST carregar paciente/encounter quando aplicável.

## Validação

- origem reconstruível até transcript, exame, dispositivo ou documento;
- positivo, negado, incerto e contraditório representáveis;
- fato não contém hipótese, recomendação ou documento final;
- duas fontes conflitantes coexistem sem sobrescrita.

## Questões abertas

Polaridade, níveis de certeza, taxonomia final e terminologia canônica
continuam dependentes da revisão clínica e do Astera Flow.
