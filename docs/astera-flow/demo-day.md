---
document_id: astera-demo-day
title: Astera Demo Day — Primary Care Consultation
category: Product
status: Official
version: 1.1
owner: Astera Product Engineering
depends_on:
  - product-backlog.md
  - clinical-workflows/clinical-workflow-dataset.md
used_by:
  - Médicos avaliadores
  - Product Engineering
last_updated: 2026-08-07
---

# Astera Demo Day — Primary Care Consultation

Status: **Planned**  
Objetivo: demonstrar uma consulta clínica completa para médicos, sem expor a
complexidade interna da plataforma.

## Experiência esperada

```text
Médico inicia a consulta
  ↓
Paciente fala naturalmente
  ↓
Astera organiza o contexto
  ↓
SOAP é apresentado
  ↓
Médico revisa e corrige
  ↓
FHIR e persistência são derivados da revisão
```

## Roteiro da demonstração — dois minutos

1. Abrir o Astera na tela de uma consulta.
2. Iniciar a captura de áudio autorizado.
3. Executar a Golden Consultation 001 sem copiar ou colar texto.
4. Mostrar o transcript e os fatos clínicos reconhecidos.
5. Mostrar o contexto e a documentação SOAP gerada.
6. Permitir que o médico revise e corrija o resultado.
7. Mostrar a confirmação de persistência e o resultado FHIR.
8. Encerrar exibindo o Clinical Replay da consulta.

### Fala do apresentador

> O paciente fala. O Astera entende e organiza. A IA gera um primeiro SOAP. O
> médico revisa e decide.

O apresentador não deve explicar a implementação durante a jornada. Perguntas
sobre Kernel, SDKs ou Providers ficam para uma conversa técnica separada.

## O que o médico deve avaliar

- o sistema acompanhou a fala sem exigir comandos artificiais;
- informações importantes foram preservadas;
- o SOAP é útil como primeiro rascunho clínico;
- correções são possíveis antes da assinatura;
- a experiência reduz trabalho de documentação;
- o resultado é confiável o suficiente para revisão humana.

## O que não faz parte da apresentação

- Kernel, ADRs, SDKs, providers ou detalhes de implementação;
- afirmação de diagnóstico automático;
- uso de dados clínicos sem autorização;
- apresentação de resultado determinístico como se fosse produção;
- certificação clínica baseada apenas na demonstração.

## Critérios de sucesso

- uma consulta percorre o fluxo sem intervenção manual de engenharia;
- o médico consegue revisar o SOAP sem consultar logs técnicos;
- cada saída permanece rastreável ao Clinical Context;
- falhas e limitações são mostradas explicitamente;
- o Demo Day só recebe status concluído após o CPI-001 possuir evidências
  suficientes de Engineering, Medical Validation, CQA e persistência.

## Formulário de avaliação médica

Ao final, cada médico responde de forma independente:

| Pergunta | Registro |
|---|---|
| O transcript representa o que foi dito? | Sim / Parcial / Não |
| Os fatos clínicos importantes foram preservados? | Sim / Parcial / Não |
| O SOAP é útil como primeiro rascunho? | Sim / Parcial / Não |
| O que precisou ser corrigido? | Texto livre |
| Você usaria o fluxo em uma consulta supervisionada? | Sim / Não / Ainda não |

Essas respostas alimentam SOAP Acceptance Rate, Critical Fact Recall e o
registro de limitações. Uma demonstração bem-sucedida não equivale a aprovação
clínica ou prontidão para produção.

## Pré-requisitos

- CPI-001 executável com áudio falado autorizado;
- Clinical Workflow Dataset v1.1 registrado;
- Speech provider real disponível;
- FHIR e persistência durável disponíveis;
- ambiente de demonstração sem dados reais não autorizados.
