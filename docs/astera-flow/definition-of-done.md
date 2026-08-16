---
document_id: astera-definition-of-done
title: Definition of Done — Clinical Journeys
category: Product Governance
status: Official
priority: P0
owner: Astera Clinical Product
depends_on:
  - product-backlog.md
  - vision-demo.md
  - clinical-capability-catalog.md
  - clinical-capability-map.md
used_by:
  - Product
  - Product Engineering
  - UX Review
  - Clinical Validation
last_updated: 2026-08-08
---

# Definition of Done — Clinical Journeys

Uma Sprint de Journey não está concluída porque o código foi escrito, o build
passou ou um componente isolado funciona. Ela só está concluída quando entrega
uma capacidade de produto que pode ser usada e avaliada por um profissional de
saúde.

Toda Sprint deve declarar qual `CC-xxx` entrega ou valida. Se não houver uma
Clinical Capability identificável no catálogo, a entrega é trabalho habilitador
e não pode ser apresentada como resultado principal da Sprint.

## Os quatro critérios obrigatórios

### 1. Funciona

A capacidade pode ser executada de ponta a ponta no cenário definido para a
Sprint.

Evidências mínimas:

- fluxo principal executado sem intervenção manual de engenharia;
- estados de sucesso e falha tratados;
- teste reproduzível no ambiente autorizado;
- resultado coerente com o objetivo da Journey.

### 2. Demonstrável

A capacidade pode ser mostrada ao vivo para um médico ou paciente sem
explicações técnicas.

Evidências mínimas:

- sessão ao vivo realizada;
- interface compreensível sem mencionar arquitetura, providers ou código;
- vídeo gravado da demonstração;
- vínculo com uma cena da Vision Demo.

### 3. Observável

A execução deixa evidências suficientes para entender o que aconteceu e
validar o resultado.

Evidências mínimas:

- eventos da jornada registrados;
- logs e erros disponíveis para investigação;
- identificadores de sessão ou consulta rastreáveis;
- métricas ou registros de resultado adequados ao escopo.

Observabilidade não significa expor infraestrutura ao médico. Ela existe para
validação, suporte e melhoria do produto.

### 4. Aprovada

A experiência passou por revisão de UX e faz sentido para um profissional de
saúde.

Evidências mínimas:

- revisão de UX concluída;
- sessão observada por um profissional de saúde quando aplicável;
- limitações, dúvidas e falhas registradas;
- decisão explícita de aprovar, continuar em andamento ou bloquear.

## Checklist de encerramento

- [ ] O problema do médico foi resolvido ou a razão do bloqueio foi registrada.
- [ ] O problema do paciente foi resolvido ou a razão do bloqueio foi registrada.
- [ ] A Clinical Capability (`CC-xxx`) entregue ou validada está registrada no
      Clinical Capability Catalog.
- [ ] O resultado visível da Sprint está documentado.
- [ ] O fluxo funciona do início ao fim.
- [ ] A demonstração ao vivo foi realizada.
- [ ] O vídeo da Sprint foi gravado e associado ao backlog.
- [ ] A execução possui eventos, logs ou métricas verificáveis.
- [ ] A Vision Demo foi atualizada na cena correspondente, quando necessário.
- [ ] UX revisou a experiência.
- [ ] A avaliação de um profissional de saúde foi registrada, quando aplicável.
- [ ] O status da Journey foi atualizado em Clinical Maturity.

Se qualquer item obrigatório estiver pendente, a Journey permanece **In
Progress**, **Clinical Validation** ou **Blocked**. Ela não recebe status
**Completed**, **Certified** ou **Released**.

## Evidência de demonstração

Cada Sprint deve produzir um vídeo com nome previsível:

```text
{journey}-journey-demo.mp4
```

Exemplos:

- `patient-journey-demo.mp4`;
- `doctor-journey-demo.mp4`;
- `communication-journey-demo.mp4`;
- `clinical-journey-demo.mp4`;
- `a2ui-journey-demo.mp4`.

O vídeo deve mostrar uma pessoa usando o Astera Clinical para realizar a
capacidade. Não deve ser uma gravação de terminal, código ou explicação de
arquitetura.

## Gate de Communication Journey

Depois da Communication Journey, a aprovação exige uma sessão real com:

- um notebook;
- um smartphone;
- duas pessoas;
- áudio e vídeo funcionando de forma fluida;
- observação de um médico em uma sessão de aproximadamente 30 minutos.

Até esse gate ser aprovado, não iniciar Speech, IA, Clinical Facts, SOAP ou
A2UI. O objetivo é validar a experiência da consulta antes de adicionar
inteligência.

## Pergunta final

Antes de marcar uma Sprint como concluída, o responsável deve responder:

> **Depois desta Sprint, o que um médico consegue fazer no Astera que ele não
> conseguia fazer antes?**

Se a resposta for apenas uma tecnologia, componente ou camada, a Sprint não
está pronta.
