# 10 — Architecture Review

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Escopo** | RFC-001 e documentos 01–09 |
| **Método** | Revisão conceitual, sem código, IA ou ADK |
| **Próximo estágio** | Reality Review |

## Objetivo

Tentar quebrar a Cognitive Architecture antes da implementação, verificando
consistência, fluxo, fronteiras, responsabilidades, dados, eventos e
lifecycle. Esta revisão não aprova código e não cria novos conceitos fora da
RFC.

## Review 1 — Consistência

| Pergunta | Resultado | Achado |
|---|---|---|
| Existem conceitos duplicados? | Corrigido | `Knowledge` foi normalizado para Medical Knowledge Layer; `Evidence` é suporte, não mundo paralelo |
| Existem responsabilidades repetidas? | Corrigido | Reasoning formula hipótese; Knowledge fornece conhecimento; Documentation projeta |
| Alguma entidade faz duas coisas? | Condicional | Context mantém estado; Runtime versiona; Recommendation foi formalizada no contrato 06 |
| Há ambiguidade? | Aberto | Clinical Assertion → Clinical Fact ainda precisa de política de validação clínica |

### Decisão de consistência

- Clinical Fact representa estado observado ou informado.
- Clinical Evidence representa suporte de uma hipótese/recomendação.
- Clinical Context representa o estado composto do paciente.
- Hypothesis representa explicação provisória.
- Medical Knowledge representa conhecimento externo.
- Recommendation representa proposta derivada e revisável.
- Clinical Representation representa saída documental/interoperável.

Não há duas entidades com o mesmo dono conceitual. A decisão foi consolidada
no baseline aprovado pelo Astera Flow.

## Review 2 — Fluxo Cognitivo

```text
Paciente → Speech → Transcript → Clinical Fact
        → Clinical Context → Reasoning → Hypothesis
        → Knowledge Query → Knowledge Objects
        → Information Gap → Question → Novo Fact
        → Context Enrichment → Recommendation
        → Documentation → Reality Review → Medical Validation → SOAP/FHIR
```

### Resultado

O fluxo fecha sem lacuna conceitual. O retorno de `Novo Fact` para `Context
Enrichment` é um ciclo explícito do Clinical Reasoning Loop, não uma volta
silenciosa no pipeline.

### Lacunas encontradas

1. Resposta do médico à representação precisava de evento e lifecycle: coberta
   por `medical.validation.requested`, `medical.validation.completed` e
   `representation.reviewed`.
2. Recommendation não tinha contrato próprio: coberta no documento 06.
3. Os nomes dos eventos estavam divergentes: normalizados no documento 07.

## Review 3 — Boundary Review

| Fronteira | Termina | Começa | Dono |
|---|---|---|---|
| Speech / Facts | Transcript e provenance da fala | Assertion clínica candidata | Speech / Clinical Facts Specialists |
| Facts / Context | Facts individualizados | Relações, timeline e snapshot | Context Specialist / Runtime |
| Context / Reasoning | Estado contextual | Hipóteses, suporte, conflitos e gaps | Reasoning Specialist |
| Reasoning / Knowledge | Hipótese ou gap | Query, objetos e referências médicas | Knowledge Specialist |
| Knowledge / Documentation | Conhecimento referenciado | Projeção documental do Context | Documentation Specialist |
| Specialist / Runtime | Proposta de enriquecimento | Validação, versionamento e persistência | Runtime |
| Agent/ADK / Clinical Authority | Coordenação técnica | Validação do raciocínio clínico | Runtime / Medical Validator |

Nenhum Specialist cruza outra fronteira por comunicação direta.

## Review 4 — Responsibility Review

| Ação | Único responsável | Não responsável |
|---|---|---|
| Transcrever áudio | Speech Specialist | Reasoning, Knowledge |
| Extrair Clinical Fact | Clinical Facts Specialist | Speech, Documentation |
| Criar relação/timeline | Context Specialist | Knowledge |
| Criar hipótese | Reasoning Specialist | Knowledge, ADK |
| Formular Knowledge Query | Knowledge Specialist | Speech, Documentation |
| Detectar Information Gap | Gap Detection/Reasoning Specialist | Knowledge |
| Propor pergunta | Gap Detection Specialist | Documentation |
| Anexar evidência médica | Knowledge Specialist | Reasoning sozinho |
| Criar Recommendation | Reasoning/Knowledge após evidência | Speech, ADK |
| Gerar SOAP/FHIR | Documentation Specialist | Reasoning, ADK |
| Validar/assinar | Medical Validator | Qualquer Specialist |
| Versionar Context | Runtime | Specialist, ADK |

O dono único é normativo. Colaboração ocorre por Context e Events, nunca por
chamada direta entre Specialists.

## Review 5 — Data Flow Review

```text
Audio
  ↓
Transcript
  ↓
Facts
  ↓
Context vN
  ↓
Hypothesis / Gap
  ↓
Knowledge Query / Question
  ↓
Knowledge / New Fact
  ↓
Context vN+1
  ↓
Recommendation
  ↓
Representation
```

O fluxo tem um ciclo legítimo: `Question → New Fact → Context vN+1 →
Reasoning`. O ciclo MUST criar nova versão e eventos; não pode mutar Context
anterior. Não há outro retorno implícito identificado.

## Review 6 — Event Review

O catálogo canônico está em [07 — Cognitive Events](07-cognitive-events.md).
Ele cobre criação, atualização, conflito, rejeição, conclusão, referências,
recomendação, invocation, revisão e publicação. Os aliases divergentes foram
removidos da especificação normativa.

### Verificação mínima

- Fact: detected → validated → updated/superseded/resolved → archived.
- Hypothesis: created → supported/weakened/contradicted → confirmed/rejected →
  closed.
- Context: created → enriched → conflict detected → completed/archived.
- Knowledge: snapshot published → query → object retrieved → reference attached.
- Representation: manifest created → reviewed → published.

## Review 7 — Lifecycle Review

| Entidade | Lifecycle normativo |
|---|---|
| Clinical Fact | Detected → Validated → Enriched → Superseded/Resolved → Archived |
| Hypothesis | Candidate → Supported/Weakened/Contradicted → Confirmed/Rejected → Closed |
| Clinical Context | Opened → Growing → Stable → Completed → Archived |
| Knowledge Object | Draft → Published → Superseded/Withdrawn |
| Recommendation | Proposed → Reviewed → Accepted/Rejected → Expired |
| Representation | Draft → Reviewed → Published → Archived |
| Specialist Invocation | Started → Completed/Rejected |
| Medical Validation | Requested → In Progress → Completed |

Lifecycle não apaga versões anteriores. Uma transição clínica relevante MUST
ter evento, provenance e responsável.

## Resultado da Architecture Review

**Veredicto:** `Conditionally Consistent`.

A arquitetura permanece coerente após a normalização de eventos, boundaries,
owners, Recommendation Contract e lifecycles. A revisão não encontrou uma
contradição estrutural, mas deixa três pontos para a Reality Review e Medical Validation:

1. política de aceitação de Clinical Assertion como Clinical Fact;
2. autoridade clínica para confirmar hipótese e aceitar Recommendation;
3. cobertura do cenário com mudança de assunto e discordância do médico.

## Próxima etapa

Reality Review e Medical Validation são as próximas etapas. Nenhum contrato de código ou
implementação da Fase D é criado por esta revisão.
