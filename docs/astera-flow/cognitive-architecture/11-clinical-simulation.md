# 11 — Clinical Simulation

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Tipo** | Simulação conceitual ponta a ponta |
| **Dependência** | Architecture Review |
| **Execução** | Sem código, IA ou ADK |

## Objetivo

Testar se um atendimento completo pode ser representado apenas com Clinical
Facts, Clinical Context, Hypotheses, Knowledge, Specialists, Contracts e Events.

O caso abaixo é sintético e anonimizado para validação arquitetural. Ele não
é uma recomendação médica nem substitui uma consulta real.

## Atendimento minuto a minuto

### 09:00 — Abertura e fala

Paciente: “Tenho dor no peito.”

Speech Specialist cria Transcript. Clinical Facts Specialist propõe:

```text
Fact F1: dor torácica
source=patient_report · certainty=reported · status=candidate
```

Evento: `clinical.fact.detected`. Runtime cria Context v1.

### 09:03 — Histórico

Paciente relata dispneia, hipertensão, tabagismo e pai com infarto aos 52.
Context v2 recebe F2–F5 e timeline. Nenhum diagnóstico é criado.

### 09:06 — Raciocínio

Reasoning Specialist produz:

```text
H1: Síndrome Coronariana Aguda — candidate
H2: Angina Estável — candidate
H3: Refluxo — candidate
```

Cada hipótese possui suporte, conflitos vazios e gaps. Eventos de hipótese são
emitidos; o Context v3 permanece com hipóteses concorrentes.

### 09:09 — Pergunta orientada por gap

Gap Detection identifica `característica da dor` e propõe: “A dor piora com
esforço ou irradia para o braço?” Evento `clinical.question.proposed`.

### 09:12 — Novo fato

Paciente responde que a dor piora ao esforço e irradia. Facts Specialist cria
F6–F7; Context Specialist cria relações temporais. Context v4 é enriquecido.

### 09:15 — Knowledge Query

Knowledge Specialist formula Query para H1, com hipótese, jurisdição,
população, data e nível de evidência. O snapshot retorna objetos estruturados,
referências e contraindicações. Context v5 recebe somente referências e
enriquecimentos; Knowledge Layer não recebe paciente.

### 09:20 — Mudança de assunto

Paciente interrompe: “Também estou preocupado com uma dor nas costas antiga.”
Facts Specialist registra F8 como novo fact e Context v6 abre uma trilha
temporal separada, sem apagar o raciocínio torácico.

### 09:24 — Contradição

Um resultado observado contradiz parte do suporte de H1. Runtime registra
conflito; Reasoning Specialist reduz suporte de H1 e mantém H2. Nenhum fato
original é apagado. Context v7 é criado.

### 09:30 — Diretriz atualizada

Knowledge Layer publica snapshot v2. A query original permanece ligada ao
snapshot v1; uma nova Query pode consultar v2. O passado continua auditável.

### 09:35 — Discordância clínica

O médico discorda de uma Recommendation. Medical Validation registra a decisão
como rejeitada, com motivo e autor. O Specialist não reabre a decisão por
conta própria. Context v8 preserva Recommendation e revisão.

### 09:40 — Documentação

Documentation Specialist gera manifesto a partir do Context v8 e projeta SOAP,
FHIR, Timeline e Summary em `draft`. Eventos de representação são emitidos.

### 09:45 — Assinatura

O médico revisa, corrige e assina a representação. Context v9 recebe provenance
da revisão e status `published`. A assinatura não é inferida pelo modelo.

## Matriz de cobertura

| Pergunta | Conceito que responde | Resultado |
|---|---|---|
| De onde veio a fala? | Transcript + Provenance | Coberto |
| O que sabemos do paciente? | Clinical Fact + Context | Coberto |
| O que pode explicar os fatos? | Hypothesis | Coberto |
| O que falta saber? | Information Gap | Coberto |
| Como perguntar? | Question + Event | Coberto |
| O que a medicina recomenda? | Knowledge Query/Object | Coberto |
| Como lidar com mudança de assunto? | Timeline + Context version | Coberto |
| Como lidar com contradição? | Conflict + Hypothesis lifecycle | Coberto |
| Como lidar com diretriz nova? | Snapshot version | Coberto |
| Como lidar com discordância? | Medical Validation lifecycle | Coberto |
| Como documentar? | Clinical Representation | Coberto |

## Critérios de falha

A simulação falha se qualquer etapa exigir:

- diagnóstico automático;
- escrita de paciente no Medical Knowledge Layer;
- comunicação direta entre Specialists;
- alteração destrutiva do Context;
- recomendação sem referência;
- evento sem owner, versão ou provenance;
- assinatura automática do médico.

## Veredicto da simulação

**Resultado preliminar:** `Representable with Open Clinical Decisions`.

O atendimento cabe nos conceitos definidos. Os pontos que ainda exigem
Medical Validation são política de confirmação clínica, aceitação de facts,
contradições e revisão de Recommendations. Não foi identificada lacuna que
exija uma nova entidade cognitiva.
