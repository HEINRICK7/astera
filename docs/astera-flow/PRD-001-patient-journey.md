---
document_id: astera-prd-001-patient-journey
title: PRD-001 — Patient Journey
category: Product
status: In Progress
priority: P0
owner: Astera Clinical Product
depends_on:
  - product-backlog.md
  - clinical-workflows/clinical-workflow-dataset.md
  - ../adrs/ADR-011-platform-complete.md
---

# PRD-001 — Patient Journey

**Implementação:** em andamento no Astera Workbench.  
**Capability:** `CC-001 — Paciente consegue entrar na consulta`.

## Objetivo

Permitir que um paciente receba um convite, entre na consulta e fique pronto
para ser atendido pelo médico, com clareza, segurança e o mínimo de fricção.

A pergunta desta Sprint é:

> **O paciente consegue entrar na consulta?**

Este documento descreve a experiência do paciente. Não define novos Managers,
Engines, States, Providers ou outras abstrações arquiteturais.

## Princípios do produto

- Toda a experiência visível ao paciente deve estar em Português (Brasil).
- O paciente deve saber onde está, o que precisa fazer e o que acontecerá em
  seguida.
- A consulta só começa depois que o paciente estiver conectado e o
  consentimento necessário tiver sido tratado.
- Falhas de câmera, microfone ou conexão devem ser explicadas em linguagem
  humana, com uma ação clara para recuperação.
- Privacidade e consentimento devem aparecer antes da ativação da comunicação.
- O produto deve parecer um consultório digital calmo, não uma ferramenta de
  desenvolvimento.

## Jornada do paciente

```text
Convite recebido
      ↓
Identificação da consulta
      ↓
Entrada na sala de espera
      ↓
Consentimento
      ↓
Permissão de câmera e microfone
      ↓
Teste de conexão e dispositivos
      ↓
Aguardando o médico
      ↓
Paciente pronto para a consulta
```

## O que o paciente vê

### 1. Convite

O paciente recebe uma chamada para a consulta contendo, no mínimo:

- nome do serviço Astera Clínica;
- nome do médico ou serviço de atendimento;
- data e horário da consulta;
- ação clara para entrar;
- orientação para usar um dispositivo com câmera, microfone e conexão.

### 2. Entrada

Ao abrir o convite, o paciente vê uma tela simples de confirmação:

```text
Consulta com Dr(a). [nome]
[data] · [horário]

Entrar na consulta
```

Não devem aparecer termos como Runtime, Provider, Workspace, Galène ou
Engineering.

### 3. Consentimento

Antes da comunicação, o paciente vê de forma resumida:

- que a consulta utilizará áudio e vídeo, quando aplicável;
- como os dados da consulta serão tratados;
- que a inteligência artificial pode acompanhar a consulta, quando aplicável;
- que o médico continua responsável pelas decisões clínicas;
- ações para aceitar ou recusar.

O paciente não fica preso em uma tela sem explicação. Em caso de recusa, o
produto informa o próximo passo e preserva a decisão.

### 4. Dispositivos

O paciente pode permitir e testar câmera e microfone antes de aguardar o
médico. Cada falha deve indicar uma ação concreta, por exemplo:

- “Permita o acesso ao microfone no navegador.”
- “Escolha uma câmera disponível.”
- “Verifique sua conexão e tente novamente.”

### 5. Sala de espera

Depois de pronto, o paciente vê:

```text
Você está na sala de espera

Estamos avisando o médico.
Permaneça nesta tela; a consulta começará quando ele entrar.
```

O estado da conexão e os dispositivos podem ser consultados sem ocupar o
centro da experiência.

### 5.1 Início pelo médico

Quando o paciente concluir o consentimento e o teste dos equipamentos, o
médico vê o estado **Paciente pronto para iniciar** e pode clicar em
**Iniciar consulta**. O paciente recebe a mudança de estado sem recarregar a
página, sai da espera e vê claramente:

```text
O médico iniciou a consulta
Você já está na consulta. Sua câmera e seu microfone estão ativos.
```

Nesta Sprint, a ativação local de câmera e microfone é demonstrada no celular.
A transmissão de mídia entre os participantes permanece na Communication
Journey.

### 6. Médico conectado

Quando o médico entrar, o paciente recebe uma confirmação clara e a
comunicação é apresentada. A transição não deve exigir recarregar a página nem
repetir o consentimento já aceito.

## Estados visíveis da jornada

| Estado | Mensagem principal | Ação do paciente |
|---|---|---|
| Convite recebido | “Sua consulta está marcada” | Entrar |
| Identificação | “Confirme sua consulta” | Continuar |
| Consentimento pendente | “Antes de começar, precisamos da sua autorização” | Aceitar ou recusar |
| Permissões pendentes | “Autorize câmera e microfone” | Permitir e testar |
| Aguardando médico | “Você está na sala de espera” | Aguardar |
| Médico conectado | “O médico entrou na consulta” | Iniciar conversa |
| Falha recuperável | Explicação em linguagem simples | Corrigir e tentar novamente |
| Consulta encerrada | “A consulta foi encerrada” | Sair ou consultar orientação |

## Critérios de aceite

### Jornada principal

- [ ] Um paciente consegue abrir um convite de consulta válido.
- [ ] O paciente identifica médico, data e horário antes de entrar.
- [ ] O paciente consegue registrar consentimento ou recusa de forma explícita.
- [ ] O paciente consegue conceder e testar câmera e microfone.
- [ ] O paciente entra em uma sala de espera compreensível.
- [ ] O médico é informado de que o paciente entrou.
- [ ] O paciente recebe uma indicação clara quando o médico se conecta.
- [ ] A consulta não começa enquanto os requisitos definidos para a sessão não
      estiverem atendidos.
- [ ] Uma falha de permissão ou conexão apresenta recuperação orientada.
- [ ] A jornada funciona em dois dispositivos autorizados para teste.

### Segurança e confiança

- [ ] O consentimento é rastreável na sessão.
- [ ] O paciente sabe quando câmera, microfone ou gravação estão ativos.
- [ ] Não são exibidas informações clínicas de outro paciente.
- [ ] O texto não promete diagnóstico, decisão automática ou sigilo além do
      que a política aprovada garante.

### Validação do produto

- [ ] Um teste acompanhado por produto e validação clínica percorre a jornada
      completa.
- [ ] O resultado é registrado no Dashboard de Produto do CPI-001.
- [ ] A aprovação desta Sprint é baseada na jornada observada, não em testes
      isolados de componentes.

## Fora de escopo

- implementação de Galène ou de outro provider de produção;
- criação de novas abstrações arquiteturais;
- Clinical Facts, Reasoning, SOAP ou FHIR;
- redesenho do Clinical Runtime;
- portal completo do paciente;
- pagamentos, agenda ou prontuário administrativo.

## Próxima pergunta

Depois que esta jornada estiver validada, a próxima Sprint deve responder:

> **O que o médico vê e consegue fazer quando o paciente está pronto?**

Essa pergunta inicia o **Doctor Journey** sem reabrir a arquitetura congelada.
