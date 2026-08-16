# ASTERA-SPR-002 — Clinical Normalization Layer

**Status:** In progress  
**Prioridade:** Crítica  
**Dependência:** ASTERA-SPR-001

## Implementado

- `ClinicalNormalizationPort` explícita.
- Entrada principal por `StreamingTranscriptState` através de
  `normalize_state(...)`.
- Normalização incremental por `segment_id`; o `full_transcript` não é usado
  pela camada semântica.
- Cada ocorrência gera uma `ClinicalMention` independente.
- Nenhuma deduplicação, fusão ou descarte de mentions na Normalization Layer.
- `mention_id` estável para a ocorrência dentro do segmento e revisão preservada.
- Campos de `certainty`: `confirmed`, `suspected`, `possible`, `reported`,
  `unknown`.
- Status de mention: `PARTIAL`, `FINAL`, `REVISED`, `DISCARDED`.
- Negação, temporalidade, speaker e `review_required`.
- Provenance com trace, sessão, segmento, revisão, provider, offsets,
  timestamps, texto de origem e versão do normalizador.
- Contexto local: `segment_before`, `segment_current`, `segment_after`.
- Sinônimos e variações para hipertensão, dor torácica, hematêmese, diabetes,
  pneumonia, medicação não especificada e outros conceitos existentes.
- Normalization Layer não cria Facts, Knowledge, Hypotheses, SOAP, FHIR,
  Presentation ou A2UI.

## Evidência de testes

```text
12 passed — testes focados de normalização, registry e pipeline clínico
```

Os testes cobrem:

- não deduplicação de ocorrências iguais;
- revisão mantendo o mesmo `mention_id`;
- transição `PARTIAL → REVISED → FINAL`;
- sinônimos;
- negação;
- temporalidade passada;
- certainty possível;
- speaker;
- contexto local;
- provenance completa;
- medication “remédio da pressão” com `review_required`.

## Limite arquitetural

A Normalization Layer apenas afirma que uma fala é compatível com um conceito.
Ela não decide que o paciente possui a condição. A promoção para Clinical Fact,
Knowledge ou Hypothesis continua pertencendo às camadas seguintes.

## Pendências antes de Done

- [ ] Executar a suíte completa e manter todos os testes verdes após o restart
  do Runtime.
- [ ] Adicionar testes de performance para consulta de 30 minutos.
- [ ] Adicionar casos de múltiplos speakers no pipeline real do provider xAI.
- [ ] Definir a política de `DISCARDED` no consumidor/Registry; a Normalization
  Layer não deve descartar mentions.
- [ ] Confirmar a versão de ontologia/códigos com o catálogo clínico oficial.
