# 12 — Reality Review

| Campo | Valor |
|---|---|
| **Status** | In Progress |
| **Posição** | Depois de Architecture Review e antes de Medical Validation |
| **Escopo** | Dez consultas públicas, desidentificadas ou anonimizadas |
| **Método** | Anotação humana, sem código, IA ou ADK |
| **Registro de casos** | [Cognitive Validation Lab — Case Registry](../cognitive-validation-lab/case-registry.md) |

## Objetivo

Verificar se a Cognitive Architecture representa consultas médicas reais, e
não apenas um atendimento idealizado. A Reality Review testa perda de
informação, interrupções, retornos, mudança de assunto, valor das perguntas,
momento de consulta ao conhecimento e derivação da documentação.

## O que esta etapa não é

- não é Architecture Review;
- não é Medical Validation;
- não é avaliação de modelo de IA;
- não é benchmark de qualidade diagnóstica;
- não é autorização para implementar código.

Reality Review pergunta: **o modelo consegue representar a consulta?**
Medical Validation perguntará depois: **essa representação está clinicamente
correta?**

## Critérios de admissibilidade da fonte

Cada caso MUST ter:

1. identificação da fonte e versão/data;
2. origem pública ou acesso institucional autorizado;
3. evidência de desidentificação/anonimização ou licença de uso;
4. especialidade e tipo de atendimento;
5. material suficiente para reconstruir a interação clínica, não apenas um
   diagnóstico isolado;
6. registro de restrições, DUA, copyright e finalidade de uso.

MIMIC-IV-Note contém notas clínicas desidentificadas, mas seu acesso exige
credenciamento e acordo de uso. MedDialog é um dataset de diálogos médicos
para pesquisa. Repositórios de transcrições, como MTSamples/MTExamples, são
úteis como material de documentação, mas não devem ser tratados
automaticamente como consultas conversacionais completas.

## Protocolo por caso

### Passo 1 — Leitura cega

Um anotador lê a consulta sem tentar encaixá-la nos conceitos do Astera e
registra: turnos, interrupções, mudanças de assunto, perguntas, confirmações,
correções, exames e decisões.

### Passo 2 — Clinical Facts

Extrair somente facts observados, relatados, medidos ou importados. Cada item
recebe origem, tempo, polaridade, certeza, status e provenance.

**Pergunta:** conseguimos representar tudo sem criar um conceito informal?

### Passo 3 — Clinical Context

Agrupar facts, relações e timeline em versões do Context. Registrar quando o
médico retorna a um tópico, interrompe, corrige ou cria uma nova linha de
investigação.

**Pergunta:** alguma informação desapareceu ao atualizar o Context?

### Passo 4 — Reasoning e Hypotheses

Registrar hipóteses apenas quando a consulta fornecer evidência de raciocínio,
sem inferir diagnóstico retrospectivamente a partir do desfecho.

**Pergunta:** as hipóteses surgem naturalmente ou foram forçadas pelo modelo?

### Passo 5 — Information Gaps e valor da pergunta

Para cada pergunta do médico, registrar hipótese/gap relacionado, informação
esperada e valor retrospectivo: alto, médio ou baixo.

**Pergunta:** o modelo representa perguntas de alto valor sem transformar toda
pergunta em Information Gap?

### Passo 6 — Knowledge Query

Registrar se houve consulta a conhecimento externo, em qual momento, por qual
incerteza e com que hipótese/gap relacionado.

**Pergunta:** a Knowledge Query nasce de necessidade clínica observável ou foi
introduzida artificialmente?

### Passo 7 — Representation

Reconstruir SOAP, FHIR, Timeline ou Summary apenas depois do Context final.

**Pergunta:** a representação é consequência natural ou exige informação que
não existe no Context?

## Métricas qualitativas

| Métrica | Pergunta |
|---|---|
| Fact coverage | Todos os fatos relevantes foram representados? |
| Temporal coverage | Ordem, duração e retorno foram preservados? |
| Context fidelity | Relações e mudanças de assunto sobreviveram? |
| Hypothesis naturalness | Hipóteses são suportadas pela conversa? |
| Gap usefulness | Gaps explicam perguntas reais? |
| Query timing | Knowledge foi consultado no momento justificável? |
| Boundary integrity | Cada etapa tem owner único? |
| Representation derivation | SOAP/FHIR nasce do Context sem forçar dados? |
| Loss severity | Toda perda é classificada como baixa, média ou crítica? |

## Resultado por caso

Cada caso produz um `Reality Case Report` com:

```text
case_id
source_provenance
specialty / encounter_type
facts
context_versions
hypotheses
information_gaps / questions
knowledge_queries
representations
losses
boundary_violations
missing_concepts
verdict: pass | pass_with_gaps | fail
```

## Regra de quebra

Se um caso exigir um conceito inexistente, o anotador MUST registrar um
`missing_concept` e parar a promoção daquele caso. Não é permitido criar uma
entidade silenciosa apenas para fazer o caso caber.

Dez casos não precisam produzir dez modelos diferentes. Se o mesmo gap surgir
em dois ou mais casos, ele deve ser tratado como decisão arquitetural comum.

## Veredicto da fase

Reality Review será `Passed` somente quando os dez casos tiverem relatório,
proveniência e matriz de perdas. `Passed with Open Decisions` permite seguir
para Medical Validation sem esconder lacunas. `Failed` exige retornar à RFC e
às ADRs, sem iniciar implementação.

## Fontes de corpus

- [MIMIC-IV-Note — documentação oficial](https://mimic.mit.edu/docs/IV/modules/note/)
- [MIMIC — requisitos de acesso](https://mimic.mit.edu/docs/faq/how-to-get-access.html)
- [MedDialog — ACL Anthology](https://aclanthology.org/2020.emnlp-main.743/)
- [MTSamples/MTExamples — sample reports](https://www.mtexamples.com/)
- [Oxford Medical Case Reports](https://academic.oup.com/omcr)
