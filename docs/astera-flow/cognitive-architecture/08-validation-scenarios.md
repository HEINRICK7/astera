# 08 — Validation Scenarios

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Workshop origem** | Workshop 6 — End-to-End Clinical Encounter |
| **Objetivo** | Validar os cinco workshops em um atendimento completo |
| **Dependências** | Documentos 01–07 |

## Pergunta

Como um atendimento evolui do primeiro “Olá” até a assinatura final do médico
usando somente os conceitos normativos da Cognitive Architecture?

## Definições sob teste

Clinical Fact, Clinical Context, Clinical Hypothesis, Information Gap,
Knowledge Query, Knowledge Object, Specialist, Context Enrichment, Cognitive
Event e Clinical Representation são os conceitos necessários ao cenário.

## Entidades e contrato de validação

O cenário recebe uma Conversation e deve produzir versões do Clinical Context,
eventos reconstruíveis e representações derivadas. MUST falhar se precisar
criar uma entidade cognitiva não especificada.

## Cenário clínico

Paciente de 68 anos, hipertenso e tabagista, relata dor torácica e dispneia.
Durante o atendimento, a dor aumenta, uma pergunta identifica irradiação e um
exame fornece nova evidência. O caso é ilustrativo: não define conduta médica.

## Linha do tempo normativa

```text
09:00  Olá + áudio
       Speech Specialist → Transcript
       Facts Specialist → Clinical Fact: dor torácica
       Context v1

09:05  Fact: dispneia + hipertensão + tabagismo
       Context v2: facts + timeline

09:10  Reasoning Specialist
       Context v3: hipóteses concorrentes + supporting/missing/conflicting facts

09:12  Gap Detection Specialist
       Context v4: gap “característica da dor” + pergunta proposta

09:15  Nova resposta: dor piora ao esforço / irradia
       Facts + Context Specialist
       Context v5: novo fact + relação temporal

09:18  Knowledge Specialist
       Query ligada à hipótese
       Context v6: Knowledge References + snapshot + contraindicações

09:25  Medication / Reasoning Specialists
       Context v7: refinamento, conflitos e recomendações referenciadas

09:40  Documentation Specialist
       Context v8: Representation Manifest
       Projeções: SOAP, FHIR, Timeline e Summary em draft

09:45  Medical Validation
       Médico revisa, corrige e assina a representação
       Context v9: review provenance + status published
```

## Critérios de aceitação

1. Nenhum transcript vira SOAP diretamente.
2. Cada fact aponta para origem, tempo, certeza e status.
3. Hipóteses surgem apenas no Reasoning Loop e permanecem concorrentes.
4. Perguntas são rastreáveis a Information Gaps.
5. Knowledge Query nasce de hipótese/gap e identifica snapshot.
6. Specialists compartilham versões do mesmo Clinical Context.
7. Events permitem reconstruir v1…v9.
8. SOAP/FHIR/Timeline são regeneráveis e não canônicos.
9. A assinatura médica é uma revisão explícita, não uma inferência do agente.

## Falhas que devem ser detectadas

- hipótese persistida como diagnosis fact;
- Knowledge Layer contaminado com paciente;
- Specialist comunicando-se fora do Context;
- pergunta sem gap ou hipótese;
- recomendação sem fonte ou versão;
- representação sem contexto de origem;
- evento sem provenance ou versionamento;
- atualização que apaga histórico.

## Resultado

Este cenário é o sexto workshop e o teste definitivo de consistência antes da
Fase D. Se um passo exigir conceito ausente, ele gera uma questão de revisão;
não autoriza criar código ou inventar uma entidade silenciosamente.
