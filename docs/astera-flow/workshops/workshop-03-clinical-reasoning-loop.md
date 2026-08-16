# Workshop 3 — Clinical Reasoning Loop

| Campo | Valor |
|---|---|
| **Fase** | C.5 — Cognitive Architecture |
| **Workshop** | 3 — Clinical Reasoning Model |
| **Status** | Proposed Decision |
| **ADR** | ADR-006 |
| **Pré-requisitos** | Clinical Fact / Clinical Context |
| **Pergunta central** | Como nasce uma hipótese clínica? |

## Princípio de trabalho

Clinical Facts não são diagnósticos. Dor torácica, dispneia, hipertensão e
histórico familiar formam um contexto. O raciocínio clínico relaciona esse
contexto a múltiplas possibilidades, explicita o que sustenta cada uma e
identifica o que ainda falta descobrir.

```text
Clinical Context
        ↓
Clinical Reasoning
        ↓
Hipóteses concorrentes
        ↓
Information Gaps
        ↓
Perguntas
        ↓
Novos Clinical Facts
        ↓
Contexto atualizado
        ↓
Refinamento das hipóteses
```

## Decisão proposta

O núcleo cognitivo do Astera será um **Clinical Reasoning Loop (CRL)**, não uma
chamada linear de LLM nem um workflow que termina na primeira resposta.

```text
Observe
  ↓
Interpret
  ↓
Hypothesize
  ↓
Ask
  ↓
Observe again
  ↓
Update Context
  ↓
Refine Hypotheses
  ↺
```

O loop produz estado clínico evolutivo. SOAP, FHIR, Timeline, encaminhamentos e
recomendações são consequências posteriores e revisáveis.

## Clinical Hypothesis

`Clinical Hypothesis` é uma entidade diferente de `Clinical Fact`:

```text
Clinical Hypothesis
├── id
├── name
├── confidence
├── supporting_facts
├── missing_facts
├── conflicting_facts
├── status
├── created_at
├── updated_at
└── provenance
```

### Exemplo

```text
Hipótese: Síndrome Coronariana Aguda
Confidence: 0.62

Supporting Facts
  ✔ Dor torácica
  ✔ Dispneia
  ✔ Hipertensão
  ✔ Histórico familiar

Missing Facts
  ? Troponina
  ? ECG
  ? Dor irradiada

Conflicting Facts
  Nenhum
```

Confidence é uma medida do modelo e não deve ser apresentada como diagnóstico
confirmado nem como probabilidade clínica calibrada sem validação específica.

## Status da hipótese

```text
Candidate
   ↓
Active
   ├── Supported
   ├── Weakened
   ├── Contradicted
   └── Confirmed by clinician
   ↓
Resolved / Rejected / Archived
```

Uma hipótese pode continuar ativa mesmo quando outra ganha prioridade. O
contexto deve preservar hipóteses concorrentes e suas justificativas.

## Information Gap

`Information Gap` representa o que precisa ser descoberto para avaliar uma
hipótese:

```text
Information Gap
├── id
├── hypothesis_id
├── missing_fact_type
├── importance
├── question
├── acquisition_method
├── status
└── provenance
```

### Exemplo

```text
Hypothesis: Síndrome Coronariana Aguda
Gap: Característica da dor
Question: A dor piora ao esforço ou irradia para o braço esquerdo?
Acquisition: Pergunta ao paciente
```

A pergunta nasce da lacuna identificada pela hipótese. Ela não deve ser uma
invenção desconectada do Clinical Context.

## O que o loop faz

1. Observa novos fatos da conversa, exame, dispositivo ou fonte importada.
2. Interpreta fatos dentro do Clinical Context.
3. Gera hipóteses concorrentes com suporte e lacunas explícitas.
4. Prioriza Information Gaps relevantes.
5. Planeja perguntas ou aquisições de informação.
6. Incorpora novos fatos ao contexto.
7. Reavalia hipóteses e preserva a evolução histórica.

## Papel do ADK e dos agentes

```text
Clinical Context
        ↓
Clinical Reasoning Loop
        ↓
Agent coordination / ADK
        ├── coletar informação
        ├── consultar Knowledge
        ├── estruturar hipóteses
        └── planejar próxima ação
```

O ADK coordena o ciclo. Ele não recebe apenas transcript para produzir SOAP e
não deve ser tratado como autoridade clínica autônoma.

## Limites de segurança e semântica

- Hipótese não é diagnóstico.
- Confidence não é certeza clínica.
- Missing Fact não é evidência de ausência.
- Pergunta proposta não é ordem médica.
- Recommendation só pode ser derivada após validação e regras clínicas
  apropriadas.
- O loop precisa conservar provenance de cada atualização.

## Decisões abertas

- Como calibrar confidence por categoria e fonte?
- Como priorizar gaps sem criar viés de confirmação?
- Como representar hipóteses incompatíveis?
- Quando o loop solicita revisão humana?
- Quais ações são perguntas, exames, consulta à Knowledge ou espera?
- Como separar Clinical Reasoning de Clinical Recommendation?

## Resultado do Workshop 3

**Proposed Decision:** o Astera deve operar por um `Clinical Reasoning Loop`
que transforma contexto em hipóteses, hipóteses em lacunas e lacunas em novas
observações. A proposta aguarda ADR-006 e aprovação explícita do Astera Flow.
