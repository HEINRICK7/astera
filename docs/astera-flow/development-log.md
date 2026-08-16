---
document_id: astera-development-log
title: Diário de Desenvolvimento do Astera
category: Engineering
status: Official
version: 1.1
owner: Astera Engineering
depends_on:
  - AGENTS.md
  - ASTERA_INDEX.md
  - agent-execution-plan.md
used_by:
  - Agentes de Engenharia
last_updated: 2026-08-08
---

# Diário de Desenvolvimento do Astera

Este documento registra a continuidade da implementação do Astera Runtime.
Cada entrada possui data, hora local de Fortaleza, escopo, arquivos alterados e
validação executada.

## 2026-08-08 00:00:00 -03:00

### Architecture Freeze — Clinical Workspace Engine

Status: 🟢 Frozen  
Phase: Astera Clinical Workspace  
Module: Consultation Workspace / Consultation Canvas  
Architecture: ConsultationSession → ClinicalWorkspaceState → SceneManager → LayerManager → ConsultationCanvas → Canvas Layers  
Validation: Astera Workbench build passed

O Workbench deixou de tratar o Consultation Mode como uma tela de vídeo. A
arquitetura congelada define um Clinical Workspace Engine: Runtime, Replay,
Golden Consultation, Mock, Benchmark e A2UI alimentam um
`ClinicalWorkspaceState`; Scenes selecionam a experiência; o LayerManager
decide as camadas; e o ConsultationCanvas apenas compõe as camadas resultantes.

`ConsultationSession` é o aggregate root da experiência clínica; sua Timeline
registra eventos de negócio e sua `CommunicationProvider` é a boundary
temporária para MediaDevices. O VideoLayer representa apenas a primeira camada.
ClinicalLayer representa Clinical Entities, não uma forma visual fixa como Card.
O A2UI permanece compatível com o Canvas, mas não renderiza componentes clínicos
nesta Sprint.

A regra adicional congelada é **UI First, Domain Driven**: o domínio clínico é
o dono da informação; a interface apenas materializa `ClinicalWorkspaceState`.
Nenhuma Layer pode implementar hipótese, medicamento, SOAP, reasoning ou
Clinical Graph como lógica própria.

Qualquer alteração que atravesse Session, State, SceneManager, LayerManager,
Canvas ou CommunicationProvider boundary exige revisão arquitetural/ADR.

### Architecture Freeze — Consultation Platform / Product First Rule

Status: 🟢 Frozen  
Phase: Astera Clinical Product  
Decision: parar a expansão arquitetural e iniciar Sprints orientadas ao valor
visível para o médico.

A arquitetura base da experiência clínica está congelada. Nenhuma nova camada
de abstração arquitetural deve ser criada sem ADR. Toda Sprint futura deve
explicitar o problema do médico, o resultado visível na interface e a relação
com a primeira consulta clínica completa.

Próxima sequência: Patient Journey, Consultation Workspace, Communication,
Clinical Stream, A2UI Renderer e Clinical Journey.

### UX Rule — Consultório digital brasileiro

Status: 🟢 Frozen  
Decision: o modo clínico é 100% PT-BR e usa a linguagem cotidiana de médicos
brasileiros. A primeira tela prioriza paciente, consulta, conexão e controles;
infraestrutura permanece escondida até ser necessária.

Regra permanente: se um médico perceber primeiro o software em vez do paciente,
a interface falhou. O modo Engenharia é a única exceção explícita para termos
técnicos em inglês ou bilíngues.

### Communication Platform — princípios antes dos providers

Status: 🟢 Sprint autorizada / contrato em definição  
Phase: Astera Clinical Product / Communication Platform  
Module: ConsultationSession / CommunicationProvider  
Document: `astera-workbench/docs/communication-platform-architecture.md`  
Decision: definir a plataforma de comunicação antes de implementar Galène.

A Communication Platform é responsável exclusivamente pelo transporte de
mídia e pelos eventos de comunicação entre os participantes. Ela conhece
participantes, mídia, dispositivos, permissões e qualidade da conexão. Não
conhece Runtime, Speech, Clinical Graph, SOAP, FHIR, A2UI, Clinical Cards ou
IA. Todo conhecimento clínico continua sob responsabilidade exclusiva do
Clinical Runtime.

`ConsultationSession` passa a expor três projeções independentes:

- `Communication State`: presença, áudio, vídeo, dispositivos, permissões,
  qualidade, compartilhamento e gravação;
- `Clinical State`: consulta, transcript, facts, context, reasoning, knowledge,
  SOAP e FHIR;
- `Workspace State`: o que deve ser apresentado ao médico.

O contrato `CommunicationProvider` será único para
`MediaDevicesCommunicationProvider`, `GaleneCommunicationProvider`,
`ReplayCommunicationProvider`, `GoldenConsultationProvider` e
`MockCommunicationProvider`. O Workbench atual permanece usando apenas
`MediaDevicesCommunicationProvider`; nenhum SDK ou implementação Galène foi
introduzido.

Ordem aprovada: Communication Contract → MediaDevices → Patient Journey →
Communication Session → Galène → Golden Consultation → A2UI Live → Clinical
Entities. Galène permanece bloqueado até a aprovação do contrato e da sessão.
Após essa Sprint, novas abstrações arquiteturais exigem ADR e as entregas
devem voltar a ser orientadas ao valor visível para o médico.

### Architecture Freeze — Astera Platform / transição para Experiência Clínica

Status: 🟢 Architecture Frozen  
Phase: Astera Clinical / Clinical Experience  
Decision: encerrar a expansão arquitetural e iniciar entregas orientadas por
jornadas clínicas.

A plataforma passa a ser tratada como **ASTERA PLATFORM — ARCHITECTURE
FROZEN**. Sem ADR aprovada, ficam proibidos novos Managers, Engines, States,
Providers como novos conceitos arquiteturais e novas abstrações. Providers já
previstos só podem ser implementados como trabalho habilitador de uma jornada
de produto.

O backlog deixa de priorizar camadas, boundaries e engines. A pergunta de cada
Sprint passa a ser:

> O que um médico consegue fazer hoje que ontem ainda não conseguia?

O próximo artefato de produto é o [PRD-001 — Patient Journey](PRD-001-patient-journey.md),
que responde se o paciente consegue entrar na consulta. As jornadas seguintes
são Doctor Journey, Communication Journey, Consultation Journey, Clinical
Journey, A2UI Journey, Clinical Review Journey, Deployment Journey e Operations
Journey. O produto passa a
ser apresentado como **Astera Clinical**; Workbench permanece apenas como nome
interno quando necessário.

O novo Dashboard de Produto do CPI-001 acompanha paciente, consentimento,
áudio, vídeo, Speech, Clinical Facts, Reasoning, SOAP, FHIR e consulta completa.
Nenhuma etapa será promovida por evidência de componente isolado; o aceite é a
jornada observada e validada.

### Vision Demo — primeira consulta completa do Astera

Status: 🟢 Official  
Phase: Astera Clinical / Product Vision  
Document: [Vision Demo](vision-demo.md)

Foi criado o filme de referência do produto em 11 cenas: convite, boas-vindas,
consentimento, pré-check, sala de espera, consulta, conversa, conhecimento,
pergunta, final e resultado. A linha do tempo vai das 08:00, quando o médico
abre o Astera, às 08:18, quando a consulta é aprovada, salva e encerrada.

Toda Sprint deverá indicar qual cena dessa demonstração passou a ser possível,
qual capacidade visível foi entregue e o que ainda impede a consulta completa.
Este artefato é de produto e experiência; não reabre a arquitetura congelada.

### Ordem oficial de desenvolvimento do produto

Status: 🟢 Direction Frozen  
Phase: Astera Clinical / Product Development

Com Architecture Freeze, Communication Platform e Vision Demo concluídos, o
desenvolvimento passa a seguir exclusivamente jornadas:

1. Patient Journey — paciente entra pelo smartphone;
2. Doctor Journey — médico vê o paciente conectado e inicia;
3. Communication Journey — notebook e smartphone trocam áudio e vídeo;
4. Consultation Journey — sessão, timeline, status, início e encerramento;
5. Clinical Journey — Speech, Facts, Context, Reasoning e Knowledge;
6. A2UI Journey — eventos clínicos materializam Knowledge Cards;
7. Clinical Review Journey — SOAP, FHIR, revisão, assinatura e aprovação;
8. Deployment Journey — produto disponibilizado em ambiente autorizado;
9. Operations Journey — logs, auditoria, persistência, replay e Golden
   Consultation.

**Sprint atual:** Patient Journey. A próxima entrega deve ser demonstrável no
computador e responder se um paciente consegue entrar na consulta. Nenhuma
capacidade clínica será antecipada antes de médico, paciente e comunicação
estarem funcionando como produto.

### Gate obrigatório — Communication Journey

Depois da Communication Journey, o trabalho de inteligência fica bloqueado até
uma demonstração real com notebook e smartphone, duas pessoas e uma conversa
fluida por áudio e vídeo. A sessão de validação terá aproximadamente 30
minutos com um médico, sem apresentação de IA, Speech ou A2UI. Serão observados
olhar, cliques, hesitações e distrações para validar o palco da consulta antes
de adicionar inteligência.

### Product Delivery Governance — Clinical Capability Maturity e Definition of Done

Status: 🟢 Official  
Phase: Astera Clinical / Product Development  
Documents: [Definition of Done](definition-of-done.md) e Product Backlog

Nenhuma Sprint pode entregar apenas código. Cada Sprint deve entregar uma
capacidade demonstrável por um médico utilizando o sistema e produzir um vídeo
da Journey correspondente. A evolução passa a ser medida por **Clinical
Maturity**, substituindo percentuais genéricos de conclusão.

Uma Journey só pode ser concluída quando atender aos quatro critérios:

1. **Funciona** — execução ponta a ponta;
2. **Demonstrável** — sessão ao vivo sem explicação técnica;
3. **Observável** — eventos, logs ou métricas verificáveis;
4. **Aprovada** — revisão de UX e validação profissional.

Qualquer critério pendente mantém a Journey em andamento. O vídeo deve mostrar
uma pessoa usando o Astera Clinical, nunca código ou terminal. O gate obrigatório
após Communication Journey é a demonstração notebook–smartphone com duas
pessoas, áudio e vídeo fluidos e observação médica de aproximadamente 30
minutos. Até sua aprovação, Speech, IA, Clinical Facts, SOAP e A2UI permanecem
bloqueados.

### Clinical Capability Model — catálogo e mapa de domínio

Status: 🟢 Official  
Phase: Astera Clinical / Product Domain  
Documents: [Clinical Capability Catalog](clinical-capability-catalog.md) e
[Clinical Capability Map](clinical-capability-map.md)

O Astera deixa de medir Features, Stories, Tasks ou percentuais de código como
resultado de produto. O backlog passa a medir `CC-xxx`, capacidades clínicas
observáveis que podem ser usadas em uma consulta real.

O catálogo registra, para cada Capability, descrição, dependências, Journeys,
Clinical Workflows, Clinical Scenarios, critérios de aceite, demonstração e
status. O mapa mostra as capacidades do paciente, médico, comunicação,
inteligência clínica, revisão e continuidade.

O indicador oficial passa a ser **Clinical Capability Maturity**. A primeira
capacidade em desenvolvimento é `CC-001 — Paciente consegue entrar na
consulta`. Nenhuma Sprint existe para implementar uma tecnologia; toda Sprint
deve entregar ou validar uma Clinical Capability.

### Communication Platform — Sprint aprovada para execução

Status: 🟢 Approved for Sprint Execution  
Capability: `CC-003 — Paciente e médico conectam áudio e vídeo`  
Document: `astera-workbench/docs/communication-platform-architecture.md`

Os princípios da Communication Platform foram consolidados: ela conhece apenas
participantes, mídia, dispositivos, permissões, qualidade da conexão e eventos
de comunicação. `ConsultationSession` mantém separadas as projeções
`Communication State`, `Clinical State` e `Workspace State`; todo provider deve
obedecer ao mesmo contrato público.

A aprovação não implementa Galène e não autoriza novas abstrações. O próximo
resultado obrigatório é uma demonstração notebook–smartphone com duas pessoas,
áudio e vídeo fluídos e observação de um médico. Até esse resultado, Speech,
IA, SOAP e Clinical Cards permanecem fora do escopo.

### Sprint 1 — Patient Journey / implementação inicial

Status: 🟡 In Progress  
Capability: `CC-001 — Paciente consegue entrar na consulta`  
Module: Astera Workbench / Patient Journey  
Validation: `npm run build` passou

Implementado no Workbench:

- criação de uma `ConsultationSession` com identificador único;
- persistência local da sessão como snapshot de interface e auditoria;
- sincronização do estado do paciente pelo Runtime para permitir o fluxo real
  entre notebook e smartphone;
- geração, cópia e abertura do link do paciente;
- entrada do paciente por `?mode=patient&session=...`;
- tela de boas-vindas em PT-BR;
- consentimento registrado na sessão;
- permissão e teste de câmera e microfone no smartphone;
- sala de espera com confirmação de consentimento e equipamentos;
- atualização do status do paciente para a tela do médico;
- botão do médico indicando “Paciente pronto para iniciar” sem iniciar
  comunicação nesta Sprint.

Validação adicional da implementação:

- `npm run build` no Astera Workbench passou;
- suíte completa do Runtime: **122 passed**;
- fluxo HTTP compartilhado validado: criar sessão → paciente entra →
  consentimento aceito → câmera e microfone prontos;
- Runtime reiniciado em `0.0.0.0:8001` para teste na rede local;
- Workbench disponível em `http://192.168.1.18:5174/`.

Correção de ambiente para permissões móveis:

- o navegador móvel bloqueava `getUserMedia` no endereço HTTP da rede local;
- foi configurado HTTPS local para o Workbench em `https://192.168.1.18:5175/`;
- o Runtime correspondente está disponível em `https://192.168.1.18:8001`;
- a resolução do Runtime agora acompanha o protocolo HTTPS da página.

Correção de sincronização do médico: a tela do médico deve ser recarregada no
Workbench HTTPS (`5175`) depois da migração; a aba HTTP antiga (`5174`) não
consegue consultar o Runtime HTTPS. O polling do médico consulta o estado
compartilhado da sessão a cada 1,5 segundo e exibe paciente, consentimento e
equipamentos prontos.

Atualização solicitada na demonstração: o botão **Iniciar consulta** agora é
habilitado quando o paciente conclui o checklist. O clique registra
`consultation.started` no Runtime; o celular detecta `in_progress`, sai da sala
de espera e ativa sua câmera/microfone com mensagem explícita. A transmissão
entre dispositivos continua reservada à Communication Journey.

### Communication Journey — Galène adapter / implementação local

Status: 🟡 In Progress  
Capability: `CC-003 — Paciente e médico conectam áudio e vídeo`  
Architecture: `CommunicationProvider` preservada; sem lógica clínica no provider

Implementado no Workbench:

- `GaleneCommunicationProvider` atrás do contrato existente;
- carregamento do cliente oficial Galène sem expor tipos do provider ao Canvas;
- publicação da câmera/microfone do paciente e do médico na sala da consulta;
- recebimento do stream remoto pela camada de comunicação e renderização no
  Canvas;
- câmera do paciente ocupando a área principal durante a consulta;
- status explícito para conexão, vídeo remoto aguardando e vídeo conectado.

Ambiente local de demonstração: Galène em `https://192.168.1.18:8443`,
Workbench em `https://192.168.1.18:5175` e Runtime em
`https://192.168.1.18:8001`. A origem HTTPS do Workbench foi autorizada na
configuração local do Galène (`data/config.json`); sem essa autorização o
WebSocket era rejeitado antes de iniciar a mídia.

Validação automatizada em dois navegadores: paciente conclui o checklist,
médico inicia a consulta, o paciente muda para a tela de atendimento com
câmera/microfone ativos e o médico recebe vídeo remoto e vídeo local (`640×480`)
com `readyState=4`. A aprovação profissional e a gravação
`patient-journey-demo.mp4` continuam pendentes para concluir a Definition of
Done.

Fora do escopo preservado: Galène, WebRTC, comunicação entre dispositivos,
Speech, IA, Clinical Facts, Clinical Graph, Reasoning, Knowledge, A2UI, SOAP e
FHIR. A demonstração `patient-journey-demo.mp4` e a aprovação profissional
continuam pendentes para concluir a Definition of Done.

## 2026-08-07 21:55:00 -03:00

### Clinical Representation Quality Fix — CPI-001

Status: 🟢 Completed  
Phase: Clinical Product Increment 001 — Primary Care Consultation  
Module: Transcript normalization, Clinical Facts, SOAP and interim FHIR  
Author: Agent Runtime  
Architecture: Provider-neutral; Astera Flow decisions preserved  
Validation: 121 Runtime tests passed

### Correções realizadas

- Erros clínicos óbvios de ASR são normalizados na fronteira de Clinical Facts,
  sem sobrescrever o transcript bruto.
- A proveniência registra `raw_value`, `raw_category`, offsets e a versão do
  normalizador; ocorrências semanticamente duplicadas mantêm `source_refs`.
- O SOAP deixou de ser uma lista de frases e passou a organizar queixa
  principal, história da doença atual, antecedentes, medicamentos, alergias,
  dados objetivos, hipóteses candidatas e pendências para revisão clínica.
- Perguntas sem resposta confirmada não são apresentadas como fatos negativos;
  febre, neste caso, permanece `unknown`/`uncertain`.
- O DocumentReference interim deixou de enviar uma lista inválida em
  `Attachment.data`; o SOAP é codificado como JSON base64 e validado pelo
  gateway local.

### Limite arquitetural preservado

O FHIR Bundle completo derivado do Clinical Graph continua pendente de
aprovação do RFC-003 e de validação HAPI FHIR. Esta entrega corrige o contrato
interim do CPI-001 sem antecipar essa decisão.

## 2026-08-07 20:40:00 -03:00

### RFC-002 — Clinical Graph Architecture

Status: 🟡 Proposed  
Phase: Era 4 — Clinical Product  
Module: Clinical Graph / CPI-001 evolution  
Author: Agent Runtime  
Architecture: Clinical domain only; provider-neutral; contracts preserved  
Tests: 116 Runtime tests planned after full regression
Validation: Domain review documented; 116 Runtime tests passed

### Registro

O RFC-002 foi incorporado ao Astera Flow como proposta de alto impacto. O
Clinical Graph organiza Clinical Facts em nós e relacionamentos, mas não os
substitui. Kernel, ADK, Capabilities, Foundation Models, Provider SDKs e
contratos públicos permanecem intocados.

O Sprint 1 foi criado como scaffold isolado em packages/clinical_graph_sdk,
com modelos imutáveis, builder, relacionamentos e validador. Ele ainda não
está conectado ao CPI-001. Os Sprints 2–6 dependem de Architecture Review,
Medical Validation, ADR e aprovação do Astera Flow.

A revisão também tornou a proveniência do Node explícita e registrou os gates
de catálogo, relacionamentos, cardinalidade, temporalidade, SOAP, FHIR e
Golden Consultation 001.

Foi aberta a Medical Domain Review do Clinical Consultation Graph com oito
perguntas clínicas: Chief Complaint, Review of Systems, Family History, Social
History, Vital Signs, Episode, Evidence e Clinical Identity. O Sprint 2 segue
bloqueado até validação por profissional clínico; nenhuma integração de
pipeline foi autorizada.

O RFC-003 foi registrado como proposta oficial para a fronteira FHIR. A
responsabilidade do Astera fica limitada ao FHIR Mapper/Bundle Builder baseado
no Clinical Graph; validação estrutural, perfis, referências, terminologia e
persistência FHIR ficam delegadas ao HAPI FHIR quando o RFC for aprovado. O
Runtime atual permanece com InMemoryFhirGateway para testes, sem HAPI externo.

## 2026-08-07 17:52:32 -03:00

### Deno Desktop — alinhamento da documentação oficial

Status: 🟢 Completed  
Phase: Product Engineering  
Module: Astera Connect / Astera Workbench technology policy  
Execution Time: 4 min  
Author: Agent Runtime  
Architecture: Astera Flow — official Desktop stack  
Tests: Busca documental e validação de referências concluídas  
Coverage: N/A  
Decision: Approved — Deno Desktop + React + TypeScript

### Correção realizada

A Technology Selection Policy agora declara explicitamente a stack oficial do
Astera Connect / Astera Workbench. O contrato de interface também identifica o
Desktop como Deno Desktop.

Nenhuma outra tecnologia, boundary ou decisão arquitetural foi alterada.

### Arquivos alterados

- docs/astera-flow/technology-selection-policy-v2.md
- docs/astera-flow/api-contracts.js
- docs/astera-flow/development-log.md

### Próximo módulo

Astera Workbench MVP — interface de execução do CPI-001  
Status: READY — continuar somente com Deno Desktop, React e TypeScript.

## 2026-08-07 17:50:10 -03:00

### Architecture Compliance Fix — Astera Workbench

Status: 🟢 Completed  
Phase: Product Engineering  
Module: Astera Connect / Astera Workbench PRD  
Execution Time: 6 min  
Author: Agent Runtime  
Architecture: Astera Flow — official Desktop stack  
Tests: Busca documental e validação de referências concluídas  
Coverage: N/A  
Decision: Approved — Deno Desktop + React + TypeScript

### Correção realizada

O PRD independente do Astera Workbench continha uma escolha indevida de
framework Desktop não aprovado. Essa escolha foi removida. A stack oficial
passa a estar expressa exclusivamente como:

- Deno Desktop;
- React;
- TypeScript.

Também foi removida a referência ao framework não aprovado como alternativa no
catálogo tecnológico do Astera Flow.

### Regra reforçada

Nenhum framework, biblioteca ou tecnologia nova deve ser introduzido por
conveniência. A decisão precisa existir no Astera Flow; caso não exista, deve
ser registrada como pendente e aguardar ADR quando aplicável.

### Arquivos alterados

- /home/carlos-henrique/Documentos/workspace/astera-workbench/README.md
- docs/astera-flow/tech-catalog.js
- docs/astera-flow/development-log.md

### Arquitetura relacionada

- Astera Connect
- Astera Workbench
- Astera Flow
- ADR governance

### Technical Debt

Nenhuma dívida arquitetural criada. Nenhuma outra decisão foi alterada.

### Próximo módulo

Astera Workbench MVP — interface de execução do CPI-001  
Status: READY — implementar somente sobre Deno Desktop, React e TypeScript.

## 2026-08-07 17:31:57 -03:00

### CPI-001 — Primary Care Consultation: pergunta única da sprint

Status: 🟡 In Progress  
Phase: Product Engineering  
Module: Clinical Product Increment / Primary Care Consultation  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: ADR-011 — Platform Complete  
Tests: Verificação documental e de referências; execução clínica ainda pendente  
Coverage: N/A  
Decision: Approved — o CPI será promovido apenas por workflow completo

### Decisão

A sprint CPI-001 responde somente:

> O Astera consegue concluir uma consulta clínica simples do início ao fim?

Providers, modelos, componentes e benchmarks não são o resultado da sprint.
Eles são meios de habilitar o workflow.

### Critério de saída

O caso precisa atravessar Audio, Transcript, Clinical Facts, Context, Reasoning,
Knowledge, SOAP, FHIR, Persistence e Clinical Replay sem copiar dados
manualmente. O médico precisa conseguir revisar a saída e as lacunas devem
permanecer explícitas.

### Estado atual

O resultado ainda não foi emitido. O dashboard registra CPI-001 como In
Progress e a execução real está Blocked até existir áudio autorizado,
persistência real e replay completo.

### Arquivos alterados

- docs/astera-flow/product-backlog.md
- docs/astera-flow/clinical-workflows/README.md
- docs/astera-flow/executive-dashboard.md
- docs/astera-flow/demo-day.md
- docs/astera-flow/construction/README.md
- docs/astera-flow/development-log.md

### Próximo módulo

CPI-001.A — Capturar consulta autorizada  
Status: READY — executar a Golden Consultation 001 e emitir uma decisão Yes,
No ou Blocked baseada no workflow completo.

## 2026-08-07 17:23:06 -03:00

### Product Mode — backlog orientado a Clinical Product Increments

Status: 🟢 Completed  
Phase: Product Engineering  
Module: Product Backlog / Clinical Workflow Dataset / Executive Dashboard  
Execution Time: 20 min  
Author: Agent Runtime  
Architecture: ADR-011 — Platform Complete  
Tests: Verificação documental e de referências; testes de runtime não aplicáveis  
Coverage: N/A  
Decision: Approved — workflow clínico é a unidade oficial de entrega

### O que foi decidido?

O backlog ativo deixa de ser organizado por componentes e passa a ser organizado
por Clinical Product Increments. O primeiro objetivo é concluir a Consulta
Primária, do áudio autorizado até SOAP, FHIR, persistência e replay.

### O que foi atualizado?

- Product Backlog com estados, ordem de execução e fatias do CPI-001.
- Sprints técnicos marcados como fundação histórica, não como backlog ativo.
- Clinical Workflow Dataset com registry, fatos esperados, lacunas e métricas.
- Dashboard com Primary Care Workflow como indicador primário.
- Demo Day com roteiro de dois minutos e formulário de avaliação médica.
- Clinical Workflow Certification com semântica oficial dos estados.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos alterados

- docs/astera-flow/product-backlog.md
- docs/astera-flow/clinical-workflows/README.md
- docs/astera-flow/clinical-workflows/clinical-workflow-dataset.md
- docs/astera-flow/executive-dashboard.md
- docs/astera-flow/demo-day.md
- docs/astera-flow/construction/README.md
- docs/astera-flow/README.md
- docs/astera-flow/development-log.md

### Arquitetura relacionada

- ADR-011 — Platform Complete
- Clinical Workflow Certification
- Cognitive Validation Lab

### Astera Flow

- Aba: Product Engineering / Clinical Product Increments
- Status: CPI-001 em execução; próxima evidência é áudio autorizado
- Versão: Product Mode 2.0

### Technical Debt

Nenhuma dívida arquitetural criada. A gravação autorizada da Golden Consultation
001, o gateway FHIR real e a persistência durável continuam pendentes.

### Próximo módulo

CPI-001.A — Capturar consulta autorizada  
Status: READY — registrar o artefato no Clinical Workflow Dataset antes de
promover qualquer etapa clínica.

## Padrão do Engineering Journal

Toda nova entrada deve responder às mesmas perguntas e usar este cabeçalho:

```text
Status: 🟢 Completed | 🟡 In Progress | 🔴 Blocked
Phase: C
Module: Nome do módulo
Execution Time: duração ou ongoing
Author: Agent Runtime
Architecture: Hexagonal | Modular Monolith | Event Driven | Plugin First
Tests: resultado da suíte
Coverage: percentual ou N/A
Decision: Approved | Pending | Rejected
```

### Impacto arquitetural

```text
Arquitetura impactada
[ ] Runtime
[ ] Kernel
[ ] API
[ ] Desktop
[ ] Plugin System
[ ] Event Bus
[ ] Contracts
[ ] Observability
```

### Evidências obrigatórias

Cada entrada deve terminar com:

- **Arquivos criados**
- **Arquivos alterados**
- **Arquitetura relacionada**: ADRs aplicáveis ou `Nenhuma`
- **Astera Flow**: aba, status e versão atualizada
- **Technical Debt**: item conhecido ou `Nenhum`
- **Próximo módulo** e status `READY`, `IN PROGRESS` ou `BLOCKED`

Entradas históricas anteriores a este padrão mantêm sua narrativa original;
novas entradas e marcos retroativos passam a usar o formato acima.

## 2026-08-07 17:09:41 -03:00

### CPI-001 — Consulta Primária como primeiro incremento de produto

Status: 🟡 In Progress  
Phase: Product Engineering  
Module: Clinical Product Increment / Primary Care Workflow  
Execution Time: 12 min  
Author: Agent Runtime  
Architecture: ADR-011 — Platform Complete  
Tests: Documentação validada; testes de componentes não promovem o CPI  
Coverage: N/A  
Decision: Approved — backlog reorganizado por caso de uso clínico

### O que foi decidido?

O Product Backlog deixa de ser organizado por providers ou componentes e passa a
ser organizado por Clinical Product Increments (CPIs). O primeiro é o
`CPI-001 — Consulta Primária`, cujo aceite é a jornada completa do áudio até a
persistência revisável.

### Por que foi decidido?

O valor do Astera para o médico é documentar uma consulta, não instalar um
provider isolado. Providers, Capabilities e SDKs continuam como mecanismos
internos e só avançam quando contribuem para uma jornada clínica completa.

### O que foi implementado?

- Product Backlog reescrito como roadmap de CPIs.
- `CPI-001 — Consulta Primária` definido com objetivo, jornada e critérios de
  aceite ponta a ponta.
- Clinical Workflow Dataset criado com `Golden Consultation 001` e roteiro de
  gravação em português brasileiro.
- Dashboard atualizado para acompanhar CPIs e não apenas Capabilities.
- Clinical Workflow Certification vinculada ao CPI e ao dataset.

### Como foi validado?

- Nenhum contrato, SDK, Kernel ou abstração arquitetural foi alterado.
- O roteiro não foi tratado como áudio real: gravação autorizada continua
  pendente.
- O dataset proíbe dados clínicos no Git e exige registry com consentimento,
  hashes e localização segura.
- Critérios exigem transcript, Facts, Context, Reasoning, Knowledge, SOAP, FHIR,
  persistência, replay, Medical Validation e CQA no mesmo caso.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/clinical-workflows/clinical-workflow-dataset.md`

### Arquivos alterados

- `docs/astera-flow/product-backlog.md`
- `docs/astera-flow/clinical-workflows/README.md`
- `docs/astera-flow/executive-dashboard.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-011` — Platform Complete
- Clinical Workflow Certification
- Cognitive Validation Lab

### Astera Flow

- Aba: Product Engineering / Clinical Product Increments
- Status: Atualizada — CPI-001 em execução
- Versão: 2.0 — Product Mode

### Technical Debt

Nenhuma dívida arquitetural criada. A gravação autorizada da Golden Consultation
001 e a execução ponta a ponta continuam pendentes.

### Próximo módulo

CPI-001 — Captura de áudio falado autorizado  
Status: READY — executar a jornada completa somente após existir o artefato
autorizado; não promover por roteiro ou áudio sintético.

## 2026-08-07 08:22:50 -03:00

### Diagnóstico inicial

- Repositório confirmado na branch `main`, alinhada com `origin/main`.
- Base identificada no commit `440caca`:
  `Capability → Provider → Plugin` e `TaskOrchestrator`.
- Alterações locais existentes foram preservadas.
- O Astera Flow confirmou que Policy Engine e ExecutionPlan devem aguardar os
  gatilhos definidos no backlog.

### Implementações registradas

- Corrigida a integração do `AsteraKernel` com o `EventBusPort` injetado pelo
  bootstrap.
- Removida a referência inexistente a `apps.runtime.src.infra.nats`.
- Alinhados os métodos de ciclo de vida `startup`/`shutdown` com o bootstrap,
  mantendo aliases `start`/`stop` para compatibilidade.
- Restaurado o acesso do Kernel às interfaces esperadas pelo health adapter:
  `is_ready`, `get_status`, `get_health`, `get_version_info`, `providers` e
  `context`.
- Corrigido o teardown para realmente remover providers dos registries.
- Criada `EventBusNotConnectedError`, usada pelo adapter NATS e exportada pelo
  pacote de exceções.
- Corrigido o `ContextManager` para persistir o `session_id` no contexto criado.
- Adicionados testes unitários sem dependências externas para ciclo de vida,
  contexto e seleção de capabilities.

### Validação

- `python3 -m compileall -q apps packages` passou.
- Importação do `AsteraKernel`, `CapabilityRegistry` e adapter NATS passou.
- Smoke test assíncrono do Kernel passou.
- Testes adicionados aguardam execução após a finalização do registro desta
  entrada.

## 2026-08-07 08:23:21 -03:00

### Dependência de testes

- Adicionado `requirements-dev.txt` com `pytest` como dependência de
  desenvolvimento (`>=8.0,<9.0`).
- Atualizado o Dev Container para instalar automaticamente as dependências de
  desenvolvimento após a criação do ambiente.

## 2026-08-07 08:23:53 -03:00

### Configuração do pytest

- Adicionado `pytest.ini` com `testpaths = apps/runtime/tests`.
- Configurado `pythonpath = .` para permitir os imports do monólito modular a
  partir da raiz do repositório.
- A primeira execução encontrou somente a ausência dessa configuração; nenhum
  teste chegou a ser executado nessa tentativa.

### Próximo passo

Executar a suíte local, corrigir falhas encontradas e continuar a Fase C sem
implementar evoluções cujo gatilho ainda não ocorreu.

### Resultado posterior

Após a configuração do pytest, a suíte foi executada em ambiente virtual
temporário e concluiu com **3 passed**.

## 2026-08-07 08:24:12 -03:00

### Fechamento da etapa de testes

- `pytest -q` executado com sucesso.
- Nenhum serviço externo foi necessário para os testes do núcleo.
- O ambiente virtual usado na validação foi criado fora do repositório em
  `/tmp/astera-pytest-venv`.

## 2026-08-07 08:24:37 -03:00

### Preparação do ambiente

- Adicionado `requirements.txt` com FastAPI, Uvicorn, Pydantic,
  `pydantic-settings` e `nats-py`, alinhados à stack oficial do Runtime.
- O Dev Container agora instala dependências de runtime e desenvolvimento.
- Adicionado `.gitignore` para caches Python, cache do pytest, ambientes
  virtuais e artefatos de empacotamento.

### Validação da preparação

- `pytest -q`: **3 passed**.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

## 2026-08-07 08:24:54 -03:00

### Estado consolidado

O núcleo da Fase C está importável e testável sem serviços externos. As
dependências para executar o Runtime completo agora estão declaradas, mas a
execução da API/NATS depende da instalação do ambiente e dos containers de
infraestrutura oficiais.

## 2026-08-07 08:26:12 -03:00

### Isolamento do roteador HTTP

- Alterado `create_health_router` para criar um `APIRouter` por aplicação.
- Eliminado o estado global de rotas, evitando duplicação ao chamar
  `create_app()` repetidamente em testes ou workers.
- A checagem manual anterior do bootstrap foi ajustada: a versão instalada do
  FastAPI usa inclusão lazy de routers, portanto a presença dos endpoints deve
  ser validada pelo router retornado e pelo dispatch ASGI, não por uma leitura
  direta de `app.routes`.

### Validação

- `pytest -q`: **3 passed**.
- Criação repetida de duas aplicações e dois health routers sem acúmulo de
  rotas.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

## 2026-08-07 08:26:33 -03:00

### Registro da validação do adapter HTTP

O adapter HTTP está isolado por instância de aplicação e mantém exatamente os
cinco endpoints de Kernel definidos no Astera Flow: `/health`, `/live`,
`/ready`, `/status` e `/version`.

## 2026-08-07 08:30:42 -03:00

### Event Bus SDK iniciado

- Criado o contrato compartilhado `packages/shared/events/port.py` com
  `EventPublisher`, `EventSubscriber`, `EventBusPort` e `serialize_event`.
- O contrato não conhece NATS, FastAPI ou qualquer adapter concreto.
- O `EventBusPort` do Runtime passou a reutilizar o contrato compartilhado.
- Adicionados testes para serialização canônica e abstração do port.

### Status do módulo

Implementação concluída. Falta executar a validação final do SDK antes de
avançar para o Configuration SDK.

## 2026-08-07 08:31:38 -03:00

### Fechamento do Event Bus SDK

- Corrigido `BaseEvent.timestamp` para usar `datetime.now(timezone.utc)`.
- Removido o warning de `datetime.utcnow()` durante os testes.
- Validação final: **5 passed**, compilação Python e `git diff --check` sem
  falhas.
- O Event Bus SDK está 100% concluído conforme o escopo atual da Fase C.

## 2026-08-07 08:32:06 -03:00

### Configuration SDK iniciado

- Criado `packages/shared/config` com `ConfigurationLoader` genérico e
  `ConfigurationError`.
- O loader preserva a leitura de ambiente do `BaseSettings`, aceita overrides
  explícitos e converte falhas de validação para erro do SDK.
- `apps/runtime` passou a carregar `AsteraSettings` por meio do loader
  compartilhado.
- Adicionados testes de ambiente, override e validação.

## 2026-08-07 08:33:12 -03:00

### Observability SDK iniciado

- Criado o contrato compartilhado de observabilidade com spans, counters e
  gauges.
- Criado `NoopObservability` para testes e ambientes explicitamente desligados.
- Criado adapter OpenTelemetry com exportação OTLP gRPC opcional.
- Integrado o adapter ao bootstrap e ao ciclo de vida do `AsteraKernel`.
- Declaradas as dependências oficiais OpenTelemetry no Runtime.
- Adicionados testes de no-op, spans e métricas.

### Fechamento da etapa de Observability SDK

- `pytest -q`: **9 passed**.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- O Observability SDK está 100% concluído conforme o escopo atual da Fase C.

## 2026-08-07 08:34:27 -03:00

### Validação dos SDKs compartilhados

Configuration SDK e Observability SDK foram validados juntos no ambiente
virtual com as dependências de runtime instaladas. Nenhum exporter foi
acionado durante os testes; a exportação OTLP permanece configurada para o
endpoint oficial quando o Runtime for iniciado com infraestrutura ativa.

## 2026-08-07 08:27:05 -03:00

### Verificação final da etapa

- Suíte no ambiente com dependências de runtime: **3 passed**.
- Compilação de `apps` e `packages`: passou.
- Verificação de whitespace com `git diff --check`: passou.
- Nenhum commit, push ou alteração no remoto foi realizado.

## 2026-08-07 08:43:04 -03:00

### CI alinhado ao Runtime Python

- Removido o pipeline antigo de Node/npm, que não correspondia ao conteúdo do
  repositório e não possuía `package.json`.
- GitHub Actions agora instala `requirements.txt` e `requirements-dev.txt`.
- O CI executa pytest, compilação de `apps`/`packages` e `git diff --check`.
- A versão de Python do CI foi fixada em 3.11, igual ao Dev Container oficial.

## 2026-08-07 08:43:32 -03:00

### Plugin System completado

- Adicionado `PluginManifest` com nome, versão semântica, descrição e
  capabilities declaradas.
- O `PluginProtocol` passou a exigir manifest versionado.
- `PluginRegistry` agora suporta discovery explícito e visão de health por
  plugin.
- EchoPlugin recebeu manifest oficial.
- Adicionados testes de manifest, discovery e health.

## 2026-08-07 08:45:29 -03:00

### Robustez do lifecycle

- O Kernel agora executa cleanup mesmo quando o startup falha antes de ficar
  `READY`; apenas o estado `STOPPED` impede nova finalização.
- Health síncrono passou a incluir o resumo de plugins.
- O registry passou a tipar explicitamente `PluginManifest`.
- Adicionado teste de desconexão do Event Bus após falha de startup de plugin.

## 2026-08-07 08:45:54 -03:00

### Discovery público de Plugins

- Kernel passou a implementar `list_plugins` e `get_plugin` como inbound port.
- Adicionados `GET /api/v1/plugins` e `GET /api/v1/plugins/{plugin_name}`.
- Respostas de discovery seguem o envelope oficial e expõem manifest, estado e
  health do Plugin Registry.
- Adicionado teste de versionamento das rotas públicas.

### Validação da extensão da API

- `pytest -q`: **19 passed**.
- Compilação de `apps` e `packages`: passou.
- `git diff --check`: passou.

## 2026-08-07 08:46:24 -03:00

### Estado de continuidade

O código continuou seguindo a ordem definida pelo Astera Flow. A próxima
entrega especificada no roadmap é o Google ADK; não é permitido ao Agent criar
critérios próprios para iniciar ou interromper fases.

## 2026-08-07 08:47:01 -03:00

### Validação do entrypoint oficial

- `apps.api.src.bootstrap.main:create_app` importado e criado com sucesso.
- O entrypoint registrou exatamente um plugin inicial (`echo-plugin`).
- Suíte completa: **19 passed**.
- Compilação Python e `git diff --check`: passaram.

## 2026-08-07 08:34:58 -03:00

### Plugin SDK iniciado

- Criado `packages/plugin_sdk` com `PluginProtocol`, `PluginRegistry`,
  `PluginRecord` e `PluginLifecycleError`.
- Implementado lifecycle ordenado `register`, `start`, `stop`, `start_all` e
  `stop_all`.
- O Kernel passou a possuir um `PluginRegistry` dedicado e o encerra antes dos
  providers durante o shutdown.
- O contrato local `application.providers.PluginProtocol` passou a reutilizar o
  contrato oficial do SDK.
- Adicionados testes de lifecycle e registro duplicado.

## 2026-08-07 08:37:57 -03:00

### Fechamento da etapa de Plugin SDK

- O Plugin SDK está implementado conforme o escopo da Fase C.
- Validação final em execução com a suíte completa antes do início da API
  oficial.

## 2026-08-07 08:39:08 -03:00

### Primeiro Plugin — Echo

- Criado `EchoPlugin` em `application/plugins/echo`.
- O plugin registra `PLATFORM_ECHO`, o provider `echo` e o binding no
  `PluginResolver` durante `on_start`.
- O plugin remove todos os registros durante `on_stop`.
- O bootstrap registra o plugin no `PluginRegistry`; o Kernel executa seu
  lifecycle durante startup e shutdown.
- Adicionado teste de integração da cadeia completa até `TaskOrchestrator`.

## 2026-08-07 08:39:56 -03:00

### Fechamento do primeiro Plugin

- Corrigida a implementação para respeitar o contrato estrutural `Protocol`;
  `EchoPlugin` não herda diretamente do Protocol.
- Validação final: **12 passed**, compilação Python e `git diff --check` sem
  falhas.
- O Plugin SDK e o primeiro plugin da Fase C estão 100% concluídos.

## 2026-08-07 08:40:23 -03:00

### API oficial iniciada

- Criado `TaskExecutionPort` como fronteira inbound entre API e Kernel.
- Adicionado endpoint versionado `POST /api/v1/tasks`.
- Criado contrato `ExecuteTaskRequest` com contexto organizacional e clínico.
- Respostas seguem o envelope oficial com `success`, `data`, `error`, `meta`,
  `trace_id` e `timestamp`.
- O `TaskResult` agora inclui `output` nos eventos publicados.
- Criado entrypoint `apps/api` que reutiliza a composição única do Runtime.
- Adicionados testes de contrato e versionamento do endpoint.

## 2026-08-07 08:41:18 -03:00

### Fechamento da API oficial da Fase C

- Validação final: **14 passed**.
- Compilação de `apps` e `packages`: passou.
- `git diff --check`: passou.
- O endpoint de execução e o entrypoint `apps/api` estão concluídos no escopo
  da Fase C.
- O fluxo funcional validado é `API → Kernel → TaskOrchestrator → EchoPlugin`;
  NATS continua sendo o Event Bus interno e não é exposto pela API.

## 2026-08-07 08:42:23 -03:00

### Validação end-to-end da Fase C

- Adicionado teste de bootstrap que registra o EchoPlugin no Kernel, inicia o
  lifecycle e executa uma task pelo `TaskExecutionPort`.
- Adicionado teste do envelope de resposta da API oficial.
- A Fase C possui agora validação do caminho completo:
  `API → Kernel → TaskOrchestrator → Capability → Provider → Plugin`.

### Fechamento da Fase C

- Validação final: **16 passed**.
- Compilação de `apps` e `packages`: passou.
- `git diff --check`: passou.
- A Fase C está 100% concluída no código atual.

## 2026-08-07 11:14:52 -03:00

### Sprint C2 — Google ADK

- Criada a ponte `AdkRuntime` entre o Astera Runtime e o Google ADK.
- Implementados `Agent`, `App`, `Runner` e `InMemorySessionService` através de
  imports isolados no adapter.
- Sessões ADK recebem o `ContextScope` do Astera em `session.state`.
- Implementado fluxo assíncrono `run_text` baseado em `Runner.run_async` e
  eventos streamed.
- Declarada a dependência oficial `google-adk>=2.0.0,<3.0.0`.
- Adicionado teste de agent, app e sessão contextual sem chamada a modelo.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Google ADK  
Execution Time: 6 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 20 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `apps/runtime/src/application/agents/__init__.py`
- `apps/runtime/src/application/agents/adk_runtime.py`
- `apps/runtime/tests/test_adk_runtime.py`

### Arquivos alterados

- `requirements.txt`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Engineering Roadmap / Sprint C2 — Google ADK
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Session service atual: in-memory, conforme escopo de desenvolvimento.

### Próximo módulo

Medical Knowledge Layer  
Status: IN PROGRESS

## 2026-08-07 11:15:29 -03:00

### Correção de governança do desenvolvimento

Status: 🟢 Completed  
Phase: C  
Module: Engineering Journal / Governança do Astera Flow  
Execution Time: 4 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: documentação revisada; suíte de código preservada  
Coverage: N/A  
Decision: Approved

O Agent não cria critérios próprios de bloqueio, início ou término de fases.
As fases, tecnologias e decisões são controladas exclusivamente pelo Astera
Flow. Quando o Astera Flow define a próxima etapa, o desenvolvimento continua
automaticamente nessa ordem.

Arquivos criados

- Nenhum.

Arquivos alterados

- `docs/astera-flow/development-log.md`

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices

Astera Flow

- Aba: Engineering Roadmap / Engineering Journal
- Status: Atualizada
- Versão: 1.1

Technical Debt

Nenhum.

Próximo módulo

Medical Knowledge Layer  
Status: IN PROGRESS

## 2026-08-07 11:20:33 -03:00

### Sprint C3 — Medical Knowledge Layer: fundação provider-neutral

O Astera Flow define como entregáveis do Sprint C3: Knowledge Sources, Parser,
Retriever, Embeddings, Knowledge Store, Ranking e Versionamento. Esta entrega
implementa a fundação de contratos e o pipeline local determinístico para que
os adapters de embeddings e persistência possam ser conectados sem alterar o
Runtime ou o contrato de recuperação.

O que foi decidido?

- O Knowledge Layer permanece desacoplado de LLM, Google ADK e banco vetorial.
- Toda evidência recuperada carrega fonte, documento, versão e chunk de origem.
- A implementação em memória é um adapter de desenvolvimento, não uma decisão
  de persistência definitiva.

Por que foi decidido?

- O Astera Flow exige rastreabilidade, versionamento e substituibilidade dos
  provedores de conhecimento.
- O contrato pode ser validado localmente antes da conexão com infraestrutura
  externa aprovada.

O que foi implementado?

- Modelos `KnowledgeSource`, `KnowledgeDocument`, `KnowledgeChunk`,
  `KnowledgeQuery` e `Evidence`.
- Ports `KnowledgeParser`, `KnowledgeStore`, `KnowledgeRetriever` e `Ranker`.
- `SimpleTextParser` com chunking determinístico por parágrafo.
- `InMemoryKnowledgeStore` com histórico de revisões e consulta da versão atual.
- `KeywordRetriever` com ranking determinístico e filtros por metadados da fonte.
- `KnowledgeService` compondo ingestão e recuperação.

Como foi validado?

- `pytest -q`: **22 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Testes cobrem rastreabilidade da evidência, filtros, ranking e versionamento.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Medical Knowledge Layer  
Execution Time: 5 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Provider Neutral · Event Driven  
Tests: 22 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/medical_knowledge_sdk/__init__.py`
- `packages/medical_knowledge_sdk/models.py`
- `packages/medical_knowledge_sdk/protocol.py`
- `packages/medical_knowledge_sdk/in_memory.py`
- `packages/medical_knowledge_sdk/service.py`
- `apps/runtime/tests/test_medical_knowledge_sdk.py`

### Arquivos alterados

- `requirements.txt`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Engineering Roadmap / Sprint C3 — Medical Knowledge Layer
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Embeddings, reranker e Knowledge Store persistente ainda serão adapters
  posteriores do mesmo contrato.

### Próximo módulo

Open Source AI Modules — Speech  
Status: READY

## 2026-08-07 16:18:03 -03:00

### Era 4 — Astera Provider Lab: Parakeet

Status: 🟢 Lab preparado · 🟡 Runtime não executado  
Phase: Era 4 — Provider Research & Integration  
Module: Astera Provider Lab / Speech / NVIDIA Parakeet  
Execution Time: 5 min  
Author: Agent Runtime  
Architecture: Isolated Provider Research · Astera Core Frozen  
Tests: Compose config, Python compile e shell syntax passaram; runtime NIM não disponível  
Coverage: N/A  
Decision: Aprovado — iniciar Provider Lab isolado antes de qualquer nova integração

### O que foi decidido?

O desenvolvimento do núcleo do Astera fica pausado para abrir a Era 4 — Provider
Research & Integration. O primeiro e único provider em investigação é o NVIDIA
Parakeet NIM. Whisper, Deepgram e demais providers não serão iniciados neste
ciclo.

O Lab é a fronteira de descoberta: runtime, limitações, desempenho, payloads e
requisitos precisam ser comprovados ali antes de um provider entrar no Astera.

### Por que foi decidido?

O ambiente atual não permite provar uma execução real: não há driver NVIDIA
funcional, `NGC_API_KEY` configurada e a porta local 9000 não é um NIM. O check
contra essa porta retornou `InvalidBucketName` do MinIO. Registrar o bloqueio
mantém a evidência honesta e evita fallback silencioso ou integração fictícia.

### O que foi implementado?

- Projeto isolado `labs/provider-lab` sem imports de `apps/` ou `packages/`.
- Compose do NVIDIA Speech NIM com GPU NVIDIA, portas HTTP 9000 e gRPC 50051,
  `NGC_API_KEY` obrigatório e seleção explícita do perfil.
- Probe de readiness para health, models, version, metadata e metrics.
- Probe HTTP batch real e probe WebSocket realtime real, incluindo sessão,
  deltas, resultado completo, timestamps, confidence, diarization e VAD.
- Benchmark repetível com latência e WER/CER somente quando houver transcript
  de referência; métricas ausentes permanecem `null`.
- Provider Capability Matrix separando documentação oficial de evidência de
  runtime.
- Política de dados autorizados sem áudio clínico ou transcript no Git.

### Como foi validado?

- `docker-compose config` passou.
- `python3 -m py_compile labs/provider-lab/speech/parakeet/scripts/*.py` passou.
- `bash -n labs/provider-lab/speech/parakeet/scripts/check_readiness.sh` passou.
- `git diff --check` passou.
- Readiness real falhou de forma explícita: porta 9000 responde MinIO, não
  NVIDIA Speech NIM.
- `nvidia-smi` falhou por ausência de comunicação com o driver NVIDIA.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

O Lab não altera a arquitetura congelada nem cria nova abstração do Astera.

### Arquivos criados

- `labs/provider-lab/README.md`
- `labs/provider-lab/.gitignore`
- `labs/provider-lab/speech/parakeet/.env.example`
- `labs/provider-lab/speech/parakeet/docker-compose.yml`
- `labs/provider-lab/speech/parakeet/README.md`
- `labs/provider-lab/speech/parakeet/requirements.txt`
- `labs/provider-lab/speech/parakeet/capability-matrix.md`
- `labs/provider-lab/speech/parakeet/benchmark-plan.md`
- `labs/provider-lab/speech/parakeet/data/README.md`
- `labs/provider-lab/speech/parakeet/scripts/check_readiness.sh`
- `labs/provider-lab/speech/parakeet/scripts/batch_probe.py`
- `labs/provider-lab/speech/parakeet/scripts/realtime_probe.py`
- `labs/provider-lab/speech/parakeet/scripts/benchmark.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- Nenhuma nova ADR ou RFC foi criada.

### Astera Flow

- Aba: Provider Research & Integration / Astera Provider Lab
- Status: Atualizada — Lab Parakeet aberto; integração com Astera pendente de
  evidências operacionais
- Versão: 1.0 — Era 4

### Technical Debt

Nenhuma dívida de código criada. O bloqueio atual é operacional: GPU/driver,
acesso NGC, runtime NVIDIA e áudio autorizado ainda precisam ser provisionados.

### Próximo módulo

Parakeet Runtime Enablement  
Status: BLOCKED — infraestrutura externa necessária

## 2026-08-07 16:19:55 -03:00

### Parakeet Lab — Runtime Research & Readiness Evidence

Status: 🟢 Research registrada · 🟡 Runtime Integration Blocked  
Phase: Era 4 — Provider Research & Integration  
Module: NVIDIA Parakeet NIM Runtime Research  
Execution Time: 2 min  
Author: Agent Runtime  
Architecture: Provider Lab isolado · sem alteração do Astera  
Tests: Compose config, Python compile, shell syntax e `git diff --check` passaram  
Coverage: N/A  
Decision: Evidence-based — não certificar sem runtime real

### O que foi decidido?

Formalizar no Lab o funcionamento conhecido do NVIDIA Speech NIM: deployment,
batch HTTP, realtime WebSocket, payload rico, VAD, diarization, word boosting,
limites e recovery. Documentação oficial e execução local passam a ser
classificadas separadamente.

### Por que foi decidido?

O primeiro provider real precisa ensinar o padrão de integração. O Lab deve
provar o comportamento do runtime antes que qualquer adapter seja considerado
pronto para consumo pelo Astera. “Vocabulário médico” permanece não comprovado;
`word_boosting` não será usado como sinônimo.

### O que foi implementado?

- `runtime-research.md` com a pesquisa técnica e o mapeamento candidato sem
  alteração de contrato.
- `readiness-report.md` com evidências do ambiente atual e o bloqueio
  operacional reproduzível.
- Registro explícito de que batch, realtime, deltas, timestamps, confidence,
  speaker tags e VAD são capacidades documentadas que ainda exigem execução no
  perfil real escolhido.

### Como foi validado?

- `docker-compose config`: PASS.
- Compilação Python e sintaxe shell: PASS.
- Readiness: BLOCKED — porta 9000 é MinIO, não NIM.
- GPU: BLOCKED — `nvidia-smi` não comunica com o driver.
- Credencial NGC: BLOCKED — ausente no ambiente.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- `labs/provider-lab/speech/parakeet/runtime-research.md`
- `labs/provider-lab/speech/parakeet/readiness-report.md`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- Nenhuma nova ADR ou RFC.

### Astera Flow

- Aba: Provider Research & Integration / Astera Provider Lab
- Status: Atualizada — pesquisa completa; execução operacional pendente
- Versão: 1.0 — Era 4

### Technical Debt

Nenhuma. O gap é infraestrutura externa e dataset autorizado, não débito do
Astera.

### Próximo módulo

Parakeet Runtime Enablement  
Status: BLOCKED — aguarda GPU, NIM, NGC e áudio autorizado

## 2026-08-07 16:25:44 -03:00

### Astera Research — Technology Readiness & Provider Governance

Status: 🟢 Completed  
Phase: Era 4 — Provider Research & Integration  
Module: Astera Research / Provider Maturity  
Execution Time: 7 min  
Author: Agent Runtime  
Architecture: Provider Boundary · Astera Core Frozen  
Tests: Markdown review e `git diff --check`  
Coverage: N/A  
Decision: Approved — Research passa a ser o centro de evidências de providers

### O que foi decidido?

O antigo Provider Lab passa a ser organizado como **Astera Research**. O
Provider Lab permanece como módulo interno de pesquisa de providers, começando
exclusivamente pelo NVIDIA Parakeet.

Foi criada uma escala TRL própria para providers, separando:

`Documentado → Lab criado → Runtime validado → Benchmark → Medical Validation
→ Capability Certification → Clinical Workflow → Pilot → Production`.

### Por que foi decidido?

O produto não deve depender de um vendor; deve depender dos contratos existentes.
O Research depende do vendor e produz evidências. Essa fronteira torna a troca
de providers mensurável e impede que documentação, intenção ou benchmark de
outro ambiente sejam confundidos com certificação.

### O que foi implementado?

- Renomeação organizacional para `labs/astera-research`.
- Módulo `providers/speech/parakeet` mantido como único provider ativo.
- TRL adaptado para maturidade de providers.
- Dashboard executivo de maturidade.
- Decision Log com decisões de escopo, evidência e não-fallback.
- Provider Scorecard sem notas inventadas: dimensões não medidas permanecem
  `Not measured`.
- Registry de Provider Research e regra de retrospectiva antes de iniciar outro
  provider.

### Como foi validado?

- Estrutura de diretórios revisada.
- Links internos do Astera Research revisados.
- `git diff --check` passou.
- Nenhum runtime, contrato, SDK, plugin ou Kernel do Astera foi modificado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- `labs/astera-research/README.md`
- `labs/astera-research/technology-readiness-level.md`
- `labs/astera-research/provider-maturity-dashboard.md`
- `labs/astera-research/decision-log.md`
- `labs/astera-research/provider-scorecard.md`
- `labs/astera-research/providers/README.md`

### Arquivos alterados

- Organização de `labs/provider-lab` para `labs/astera-research`.
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- Provider Boundary existente
- Nenhuma nova ADR ou RFC.

### Astera Flow

- Aba: Provider Research & Integration / Astera Research
- Status: Atualizada — TRL, dashboard, scorecard e decision log ativos
- Versão: 1.0 — Era 4

### Technical Debt

Nenhuma. A maturidade do Parakeet permanece TRL 2; o runtime real continua
bloqueado por infraestrutura e não foi promovido artificialmente.

### Próximo módulo

Parakeet Runtime Enablement  
Status: BLOCKED — GPU, NIM, NGC e áudio autorizado necessários

## 2026-08-07 16:39:54 -03:00

### Development Provider Policy — CPU-first Speech

Status: 🟢 Completed  
Phase: Era 4 — Provider Research & Integration  
Module: Development Provider Policy / faster-whisper  
Execution Time: 14 min  
Author: Agent Runtime  
Architecture: Hexagonal · Provider Boundary preservado  
Tests: 108 passed, 4 warnings  
Coverage: N/A  
Decision: Approved — política normativa aplicada

### O que foi decidido?

O perfil `development` passa a usar `faster-whisper` em CPU/int8 por padrão. O
NVIDIA Parakeet permanece explicitamente selecionável como Benchmark Provider e
continua no Astera Research.

### Por que foi decidido?

O desenvolvimento do Astera não pode depender de GPU, CUDA, NGC, cloud ou API
paga. A separação Development → Benchmark → Production permite pesquisar e
certificar providers de alta performance sem impedir que qualquer desenvolvedor
execute o produto em notebook comum.

### O que foi implementado?

- Política normativa aprovada em `docs/astera-flow/development-provider-policy.md`.
- `FasterWhisperTranscriber` implementando o contrato `SpeechTranscriber`, sem
  alterar SDK, Capability ou Kernel.
- Seleção `ASTERA_SPEECH_PROVIDER`, com `faster-whisper` como default de
  desenvolvimento e `parakeet` como opção explícita de benchmark.
- Configuração CPU/int8, modelo local configurável e threads de CPU.
- `faster-whisper` adicionado às dependências de desenvolvimento.
- Matriz de profiles e dashboard executivo atualizados.
- Decision Log do Astera Research atualizado com a decisão DR-005.

### Como foi validado?

- Testes direcionados do adapter e Parakeet: **7 passed**.
- Suíte completa: **108 passed, 4 warnings**.
- O teste do Development Provider usa modelo injetado; não baixa modelo, não
  usa GPU e não mascara a ausência da dependência real.
- `git diff --check` passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/development-provider-policy.md`
- `apps/runtime/src/adapters/speech/faster_whisper.py`
- `apps/runtime/tests/test_faster_whisper_adapter.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `apps/runtime/src/infrastructure/settings/__init__.py`
- `apps/runtime/src/adapters/speech/__init__.py`
- `requirements-dev.txt`
- `docs/astera-flow/README.md`
- `docs/astera-flow/providers/README.md`
- `docs/astera-flow/capabilities/speech-provider-readiness.md`
- `docs/astera-flow/executive-dashboard.md`
- `labs/astera-research/README.md`
- `labs/astera-research/provider-maturity-dashboard.md`
- `labs/astera-research/decision-log.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- Development Provider Policy — Status APPROVED
- Contrato existente `SpeechTranscriber`
- Nenhuma nova ADR ou RFC.

### Astera Flow

- Aba: Core Platform / Providers / Development Provider Policy
- Status: Atualizada — Development Provider CPU-first aprovado
- Versão: 1.0 — Policy Applied

### Technical Debt

Nenhuma dívida arquitetural criada. A instalação do modelo faster-whisper e a
execução com áudio autorizado permanecem atividades operacionais do próximo
smoke test, não um fallback silencioso.

### Próximo módulo

Development Provider Smoke Run — Speech  
Status: READY

## 2026-08-07 15:17:49 -03:00

### Era 3 — Platform, Capabilities e Providers

Status

🟢 Completed — três frentes permanentes e Benchmark Lab registrados

Phase

Provider Ecosystem

Module

Executive Dashboard · Astera Benchmark Lab · Speech Provider Readiness

Execution Time

8 min

Author

Agent Runtime

Architecture

Platform stable · Capability contracts · Provider adapters

Tests

90 passed (baseline preservado)

Coverage

N/A — benchmarks reais ainda não executados

Decision

Approved — Architecture Freeze mantido; Provider Ecosystem iniciado

### O que foi decidido?

- O Astera Flow passa a ter três frentes permanentes: `Platform`,
  `Capabilities` e `Providers`.
- A Platform evolui lentamente; Capabilities preservam contratos; Providers
  mudam sem tocar no núcleo.
- O Benchmark Lab compara providers com o mesmo contrato e corpus autorizado.
- O dashboard executivo passa a ser o indicador oficial do projeto.
- O adapter Parakeet não será iniciado antes do Speech Provider Readiness
  Checklist atingir `PASS`.

### Por que foi decidido?

A arquitetura já está fechada. O próximo risco é um provider específico forçar
mudanças no Kernel ou ser declarado pronto apenas por passar em testes
determinísticos. A separação torna a Era 3 repetível e auditável.

### O que foi implementado?

- Estrutura documental Platform / Capabilities / Providers.
- Executive Dashboard não técnico.
- Astera Benchmark Lab com especificação de Speech.
- Provider matrix com estado real de cada engine.
- Checklist de readiness do Speech contra Parakeet.
- Identificação objetiva das lacunas atuais: streaming formal, word-level
  timestamps e normalização tipada de erros.

### Como foi validado?

- Speech batch é compatível com `SpeechTranscriber`.
- Timestamps de segmento, confidence opcional, speaker, provider e idioma já
  existem.
- Streaming e error mapping foram marcados como ausentes, não presumidos.
- Providers reais continuam `Pending`; nenhum foi falsamente certificado.
- `git diff --check`: passou.
- Suíte preservada em **90 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — readiness e benchmark documentados  
[x] Observability — métricas de provider definidas como evidência

### Arquivos criados

- `docs/astera-flow/platform/README.md`
- `docs/astera-flow/providers/README.md`
- `docs/astera-flow/benchmarks/README.md`
- `docs/astera-flow/benchmarks/speech/provider-benchmark-spec.md`
- `docs/astera-flow/executive-dashboard.md`
- `docs/astera-flow/capabilities/speech-provider-readiness.md`

### Arquivos alterados

- `docs/astera-flow/README.md`
- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/speech-transcription.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `Capability Certification Contract`
- `Capability Definition — Five Questions`

### Astera Flow

- Aba: `Platform / Capabilities / Providers`
- Status: Atualizada — Era 3 iniciada
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. Speech Provider Readiness precisa fechar
streaming, word-level timestamps e error mapping antes do adapter Parakeet.

### Próximo módulo

Parakeet Provider Adapter  
Status: READY — Speech Plugin streaming binding concluído; retry/idempotência e
provider real ainda pendentes.

## 2026-08-07 15:20:59 -03:00

### Speech SDK Contract Hardening

Status

🟢 Completed — contrato fortalecido; adapter Parakeet ainda não iniciado

Phase

Provider Ecosystem / Speech

Module

Speech SDK Readiness

Execution Time

7 min

Author

Agent Runtime

Architecture

Capability contract · Provider-neutral · Hexagonal boundary

Tests

93 passed · 4 warnings

Coverage

N/A

Decision

Approved — continuar no Speech boundary antes do provider real

### O que foi decidido?

O Speech SDK passa a representar word-level metadata, chunks parciais/finais e
erros provider-neutral sem expor payloads internos do engine.

### Por que foi decidido?

O Parakeet/NVIDIA ASR oferece perfis offline e streaming, timestamps e opções de
diarização; o contrato anterior cobria apenas transcrição batch por segmento.
Fechar essa diferença reduz o risco de adaptar o provider forçando mudanças no
restante da plataforma.

### O que foi implementado?

- `SpeechWord` para timestamps e confidence por palavra.
- `TranscriptSegment.sequence` e `is_final` para semântica de stream.
- `SpeechStreamingTranscriber` como port opcional.
- `SpeechErrorCode`, `SpeechProviderError` e normalização de falhas genéricas.
- Serialização completa dos novos metadados.
- Testes de streaming, word-level metadata e error mapping.

### Como foi validado?

- Testes direcionados: **4 passed**.
- Suíte completa: **93 passed**, com 4 warnings de depreciação existentes.
- `git diff --check`: passou.
- O checklist ainda permanece parcial: binding de streaming no Plugin,
  idempotência/retry e adapter real aguardam implementação.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime — contrato Speech SDK consumido pelo Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System — binding de streaming ainda pendente  
[ ] Event Bus  
[x] Contracts — Speech port ampliado sem nova Capability  
[x] Observability — error codes e metadata auditáveis

### Arquivos criados

- `packages/speech_sdk/errors.py`
- `apps/runtime/tests/test_speech_sdk_contract.py`

### Arquivos alterados

- `packages/speech_sdk/models.py`
- `packages/speech_sdk/protocol.py`
- `packages/speech_sdk/__init__.py`
- `docs/astera-flow/capabilities/speech-provider-readiness.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `Capability Certification Contract`
- `Speech Provider Readiness Checklist`

### Astera Flow

- Aba: `Providers / Speech`
- Status: Atualizada — SDK hardening concluído
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. Faltam binding de streaming no Plugin,
retry/idempotência e implementação do provider real.

### Próximo módulo

Speech Plugin Streaming Binding  
Status: READY

## 2026-08-07 15:23:40 -03:00

### Speech Plugin Streaming Binding

Status

🟢 Completed — streaming capability registrada apenas para providers compatíveis

Phase

Provider Ecosystem / Speech

Module

Speech Plugin Streaming Binding

Execution Time

3 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · streaming boundary

Tests

94 passed · 4 warnings

Coverage

N/A

Decision

Approved — provider batch não é obrigado a declarar streaming

### O que foi decidido?

O Speech Plugin registra `speech.streaming` somente quando o provider injetado
implementa `SpeechStreamingTranscriber`. Providers batch continuam registrando
somente as capabilities que realmente suportam.

### O que foi implementado?

- Binding condicional de `SPEECH_STREAMING` no lifecycle do Speech Plugin.
- `invoke_stream` com chunks provider-neutral, sequence e `is_final`.
- Teste de provider streaming fake e preservação da compatibilidade batch.

### Como foi validado?

- Testes direcionados Speech: **5 passed**.
- Suíte completa: **94 passed**, com 4 warnings existentes.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos alterados

- `apps/runtime/src/application/plugins/speech/plugin.py`
- `apps/runtime/tests/test_speech_plugin.py`
- `docs/astera-flow/capabilities/speech-provider-readiness.md`
- `docs/astera-flow/development-log.md`

### Próximo módulo

Parakeet Provider Adapter  
Status: READY — retry/idempotência, provider real e benchmark permanecem pendentes.

## 2026-08-07 15:27:59 -03:00

### Speech Provider Error Boundary

Status

🟢 Completed — boundary provider-neutral endurecida

Phase

Provider Ecosystem / Speech

Module

Speech Request Identity and Error Mapping

Execution Time

4 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · stable request boundary

Tests

96 passed · 4 warnings

Coverage

N/A

Decision

Approved — o Plugin normaliza falhas externas; o retry executor permanece fora
do contrato

### O que foi decidido?

`AudioRequest.audio_id` é o identificador estável da requisição e fica exposto
como `request_id`. Uma nova tentativa da mesma transcrição deve reutilizar esse
identificador. O Plugin não implementa política de retry; apenas preserva a
identidade e traduz falhas para o vocabulário estável de Speech.

### O que foi implementado?

- `AudioRequest.request_id` como chave provider-neutral de idempotência.
- `SpeechPlugin.invoke` e `invoke_stream` com normalização de falhas externas.
- Mapeamento de `ValueError`, `TypeError` e `KeyError` para `INVALID_AUDIO`.
- `request_id` preservado nos chunks de streaming.
- Testes de identidade de requisição e timeout sem vazamento de payload do
  provider.

### Como foi validado?

- Testes direcionados Speech: **7 passed**.
- Suíte completa: **96 passed**, com 4 warnings de depreciação já existentes.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- Nenhum.

### Arquivos alterados

- `packages/speech_sdk/models.py`
- `packages/speech_sdk/errors.py`
- `apps/runtime/src/application/plugins/speech/plugin.py`
- `apps/runtime/tests/test_speech_sdk_contract.py`
- `apps/runtime/tests/test_speech_plugin.py`
- `docs/astera-flow/capabilities/speech-provider-readiness.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Providers / Speech
- Status: Atualizada — request identity e error boundary concluídos
- Versão: 1.4

### Technical Debt

- Retry executor, adapter real Parakeet e benchmark ainda não implementados.
- `RATE_LIMITED` exige que o adapter real reconheça e emita esse estado.

### Próximo módulo

Parakeet Provider Adapter  
Status: READY — iniciar somente com runtime/provider disponível; depois executar
Benchmark Lab, CQA, Medical Validation e Certification.

## 2026-08-07 15:34:00 -03:00

### Provider Certification and Trace Boundary

Status

🟢 Completed — primeiro contrato de certificação de Provider registrado

Phase

Provider Ecosystem

Module

Provider Trace · ProviderExecutionResult · Provider Certification

Execution Time

7 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · evidence-first boundary

Tests

98 passed · 4 warnings

Coverage

N/A

Decision

Approved — provider real só pode avançar pelos gates explícitos

### O que foi decidido?

O primeiro objetivo não é “integrar Parakeet”, mas certificar o primeiro
Provider Real. A Capability permanece estável; o provider evolui por lifecycle,
benchmark, validação clínica, CQA e certificação.

### O que foi implementado?

- `ProviderTrace` com request, provider, versão, capability, plugin, tempos,
  latência, retries, status, confidence e streaming.
- `ProviderExecutionResult` com output, métricas e diagnósticos.
- `ProviderLifecycleStatus` e `ProviderCertification` com sete gates obrigatórios.
- Speech Plugin emitindo evidência de execução sem alterar o output Transcript.
- Documentação do Provider Certification e da regra de troca sem tocar no Kernel.

### Como foi validado?

- Testes direcionados de Provider e Speech: **9 passed**.
- Suíte completa: **98 passed**, com 4 warnings de depreciação já existentes.
- Falha inicial de contrato corrigida: certificação agora exige todos os gates
  obrigatórios, não apenas os gates fornecidos.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/provider_sdk/__init__.py`
- `packages/provider_sdk/models.py`
- `apps/runtime/tests/test_provider_sdk.py`
- `docs/astera-flow/providers/provider-certification.md`

### Arquivos alterados

- `packages/speech_sdk/__init__.py`
- `apps/runtime/src/application/plugins/speech/plugin.py`
- `apps/runtime/tests/test_speech_plugin.py`
- `docs/astera-flow/providers/README.md`
- `docs/astera-flow/benchmarks/speech/provider-benchmark-spec.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Providers / Provider Certification
- Status: Atualizada — lifecycle, trace e gates registrados
- Versão: 1.4

### Technical Debt

- NVIDIA Parakeet ainda não integrado como adapter real.
- Golden Dataset, Stress Test, Medical Validation e CQA ainda não executados.
- `retries` já faz parte do trace, mas a política de retry permanece no executor.

### Próximo módulo

Parakeet Provider Adapter  
Status: READY — depende apenas de runtime/provider disponível; a troca será
validada pelo mesmo SpeechTranscriber e pelo mesmo Speech Plugin.

## 2026-08-07 15:39:00 -03:00

### Provider Evidence Isolation and Replaceability Metrics

Status

🟢 Completed — evidência operacional isolada do Clinical Domain

Phase

Provider Ecosystem / Evidence

Module

Provider Trace Isolation · Golden Dataset · Replaceability Metrics

Execution Time

5 min

Author

Agent Runtime

Architecture

Infrastructure/Observability separated from Clinical Domain

Tests

99 passed · 4 warnings

Coverage

N/A

Decision

Approved — `ProviderTrace` só circula pelo evidence path

### O que foi decidido?

O Clinical Domain recebe apenas o output clínico provider-neutral. Métricas,
diagnósticos, retries, latência e identidade técnica ficam no caminho explícito
de Benchmark/Observability.

### O que foi implementado?

- `SpeechPlugin.invoke` e `invoke_stream` deixaram de retornar `ProviderTrace`.
- `execute_with_evidence` e `stream_with_evidence` preservam a evidência para
  Benchmark Lab e Observability.
- Métricas de Capability Independence, Replaceability e Health documentadas.
- Golden Clinical Dataset versionado por manifest/hash, sem dados clínicos no
  repositório.
- Compatibility Matrix inicial para Speech registrada sem presumir capacidades
  ainda não benchmarkadas.

### Como foi validado?

- Testes direcionados Speech/Provider: **10 passed**.
- Suíte completa: **99 passed**, com 4 warnings existentes.
- Teste explícito confirma que o trace está disponível na evidência e ausente
  no retorno clínico.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `docs/astera-flow/benchmarks/provider-evidence-metrics.md`

### Arquivos alterados

- `apps/runtime/src/application/plugins/speech/plugin.py`
- `apps/runtime/tests/test_speech_plugin.py`
- `docs/astera-flow/providers/provider-certification.md`
- `docs/astera-flow/benchmarks/README.md`
- `docs/astera-flow/executive-dashboard.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Benchmarks / Provider Evidence
- Status: Atualizada — métricas e isolamento registrados
- Versão: 1.4

### Technical Debt

- Golden Dataset v1.0 ainda precisa de manifest autorizado e execução real.
- Parakeet, Whisper e demais Providers permanecem sem benchmark executado.

### Próximo módulo

Parakeet Provider Adapter  
Status: READY — implementar apenas o adapter; medir independência e iniciar o
pipeline de evidências com o Golden Dataset versionado.

## 2026-08-07 15:53:58 -03:00

### Sprint 1 — NVIDIA Parakeet NIM Adapter

Status

🟡 Engineering Complete — runtime real e certificação pendentes

Phase

Provider Ecosystem / Construction Sprint 1

Module

ParakeetNimTranscriber

Execution Time

12 min

Author

Agent Runtime

Architecture

Existing `SpeechTranscriber` + `SpeechStreamingTranscriber` · no Kernel changes

Tests

105 passed · 4 warnings

Coverage

N/A

Decision

Approved — adapter real implementado sem alterar contratos públicos

### O que foi decidido?

O provider real será o NVIDIA ASR NIM, usando REST para batch e WebSocket
Realtime para streaming. Nenhuma resposta ou tipo específico do NIM atravessa
o boundary do Speech SDK.

### O que foi implementado?

- `ParakeetNimTranscriber` implementando os ports existentes.
- Batch multipart em `/v1/audio/transcriptions`.
- Streaming PCM16 em `/v1/realtime?intent=transcription`.
- Retry com backoff para timeout, indisponibilidade e rate limit.
- Conversão de eventos NIM para `TranscriptSegment` e `SpeechWord`.
- Mapeamento de erros para `SpeechErrorCode`.
- Bootstrap de produção sem `DeterministicTranscriber`; áudio não é mais
  convertido em texto-semente.
- Configuração do NIM via `ASTERA_PARAKEET_*`.

### Como foi validado?

- Testes do adapter: **4 passed** com transportes HTTP/WebSocket simulados.
- Suíte completa: **105 passed**, com 4 warnings de depreciação já existentes.
- `create_app()` inicializado com o adapter real configurado.
- `git diff --check`: passou.
- Verificação operacional: NIM local ausente, GPU indisponível e `NGC_API_KEY`
  ausente; nenhuma execução real foi declarada.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — apenas consumo, sem alteração  
[ ] Observability

### Arquivos criados

- `apps/runtime/src/adapters/speech/__init__.py`
- `apps/runtime/src/adapters/speech/parakeet.py`
- `apps/runtime/tests/test_parakeet_adapter.py`

### Arquivos alterados

- `apps/runtime/src/adapters/http/mvp.py`
- `apps/runtime/src/bootstrap/main.py`
- `apps/runtime/src/infrastructure/settings/__init__.py`
- `apps/runtime/tests/test_mvp_flow.py`
- `requirements.txt`
- `docs/astera-flow/capabilities/speech-provider-readiness.md`
- `docs/astera-flow/providers/README.md`
- `docs/astera-flow/providers/provider-certification.md`
- `docs/astera-flow/providers/parakeet-integration-report.md`
- `docs/astera-flow/providers/parakeet-readiness-report.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Providers / Speech / Sprint 1
- Status: Atualizada — adapter implementado; runtime externo pendente
- Versão: 1.4

### Technical Debt

- NIM Parakeet real não está disponível no workspace para execução.
- Não existe ainda Golden Clinical Dataset autorizado.
- Benchmark, Medical Validation, CQA e Certification não foram executados.

### Próximo módulo

Golden Clinical Dataset v1  
Status: READY — somente iniciar evidência após disponibilizar NIM Parakeet,
áudio autorizado e ambiente de execução compatível.

## 2026-08-07 16:03:50 -03:00

### Sprint 1 — Integration and Readiness Reports

Status

🟢 Completed — documentação oficial e readiness registradas antes do commit

Phase

Provider Ecosystem / Construction Sprint 1

Module

Parakeet Integration Report · Parakeet Readiness Report

Execution Time

6 min

Author

Agent Runtime

Architecture

Provider adapter only · Architecture Freeze preserved

Tests

105 passed · 4 warnings

Coverage

N/A

Decision

Approved — `Runtime Integration` permanece `BLOCKED` até evidência operacional

### O que foi decidido?

O adapter não será promovido por existir código. A promoção exige NIM real,
GPU, credencial/licença, áudio autorizado e execução observável. As limitações
da API batch e a diferença entre REST, WebSocket e gRPC ficam registradas.

### O que foi implementado?

- Integration Report baseado exclusivamente em documentação oficial NVIDIA.
- Readiness Report com Definition of Done, riscos e próximo gate.
- Mapeamento entre NIM e `SpeechTranscriber`/`SpeechStreamingTranscriber`.
- Registro explícito de `Runtime Integration: BLOCKED`.
- Nenhum novo código ou contrato alterado após o adapter.

### Como foi validado?

- Git confirma que o Sprint 1 ainda não foi commitado.
- `git diff --check`: passou.
- Suíte já validada: **105 passed**, com 4 warnings existentes.
- Ambiente verificado: NIM ausente, GPU indisponível, `NGC_API_KEY` ausente e
  nenhum áudio clínico autorizado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/providers/parakeet-integration-report.md`
- `docs/astera-flow/providers/parakeet-readiness-report.md`

### Arquivos alterados

- `docs/astera-flow/providers/README.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Providers / Speech / Sprint 1
- Status: Atualizada — Integration e Readiness Reports aprovados
- Versão: 1.4

### Technical Debt

- Runtime real, benchmark e certification permanecem pendentes por ausência de
  ambiente NVIDIA/NIM e dados autorizados.

### Próximo módulo

Golden Clinical Dataset v1  
Status: BLOCKED operacionalmente — não criar dataset artificial; aguardar corpus
autorizado e runtime real.

## 2026-08-07 16:05:42 -03:00

### Sprint 1 — Streaming Retry Hardening

Status

🟢 Completed — retry de conexão adicionado sem duplicar partials

Phase

Provider Ecosystem / Construction Sprint 1

Module

ParakeetNimTranscriber Streaming Retry

Execution Time

2 min

Author

Agent Runtime

Architecture

Existing `SpeechStreamingTranscriber` · no contract changes

Tests

106 passed · 4 warnings

Coverage

N/A

Decision

Approved — reconectar somente antes do primeiro partial

### O que foi decidido?

Uma falha antes de qualquer resultado parcial pode ser repetida com backoff. Uma
falha depois de um partial não é repetida automaticamente, evitando duplicação
ou inconsistência na jornada clínica.

### O que foi implementado?

- Retry bounded no início da sessão WebSocket.
- Teste de reconexão antes do primeiro partial.
- Limitação registrada no Integration Report.

### Como foi validado?

- Testes direcionados Parakeet: **5 passed**.
- Suíte completa: **106 passed**, com 4 warnings existentes.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- Nenhum.

### Arquivos alterados

- `apps/runtime/src/adapters/speech/parakeet.py`
- `apps/runtime/tests/test_parakeet_adapter.py`
- `docs/astera-flow/providers/parakeet-integration-report.md`
- `docs/astera-flow/providers/parakeet-readiness-report.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Providers / Speech / Sprint 1
- Status: Atualizada — streaming retry hardening concluído
- Versão: 1.4

### Technical Debt

- Retry após partial permanece deliberadamente não automático.
- Runtime NIM real, benchmark e certification continuam pendentes.

### Próximo módulo

Golden Clinical Dataset v1  
Status: BLOCKED operacionalmente — aguardar NIM real, corpus autorizado e
ambiente compatível.

## 2026-08-07 15:45:38 -03:00

### Clinical Journey Executor and Capability Zero

Status

🟢 Completed — jornada clínica executável criada; certificação real ainda não emitida

Phase

Clinical Workflow Certification

Module

Audio → Speech → Facts → Context → Reasoning → Knowledge → SOAP → FHIR → Persistence

Execution Time

8 min

Author

Agent Runtime

Architecture

Clinical Domain workflow · Provider-neutral · Replayable

Tests

101 passed · 4 warnings

Coverage

N/A

Decision

Approved — Capability Zero será medida pela jornada completa, não por módulos isolados

### O que foi decidido?

O próximo KPI é `Real Consultation Success Rate`. A jornada só será considerada
real quando áudio clínico autorizado, provider real e persistência real
percorrerem o fluxo sem transformação manual.

### O que foi implementado?

- `ClinicalJourneyExecutor` compondo o Cognitive Consultation Pipeline com FHIR
  validation, criação e persistência.
- `ClinicalJourney` e `JourneyStep` para replay de oito etapas clínicas.
- `InMemoryClinicalJourneyStore` para validação local do replay.
- Proteção contratual que rejeita `ProviderTrace`, latência, retries, GPU e
  diagnósticos dentro do replay clínico.
- Dashboard executivo atualizado com Clinical Journey e Capability Zero.

### Como foi validado?

- Jornada de contrato percorreu Speech, Facts, Context, Reasoning, Knowledge,
  SOAP, FHIR e Persistence.
- Teste de isolamento rejeitou dados operacionais no replay.
- Suíte completa: **101 passed**, com 4 warnings existentes.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `packages/clinical_journey_sdk/__init__.py`
- `packages/clinical_journey_sdk/models.py`
- `packages/clinical_journey_sdk/in_memory.py`
- `apps/runtime/src/application/clinical/journey.py`
- `apps/runtime/tests/test_clinical_journey.py`
- `docs/astera-flow/clinical-workflows/README.md`

### Arquivos alterados

- `apps/runtime/src/application/clinical/__init__.py`
- `docs/astera-flow/README.md`
- `docs/astera-flow/executive-dashboard.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-004` — Clinical Fact as Atomic Unit
- `ADR-005` — Clinical Context as Cognitive Molecule
- `ADR-006` — Clinical Reasoning Loop
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: Clinical Workflow Certification / Capability Zero
- Status: Atualizada — journey harness implementado; evidência real pendente
- Versão: 1.4

### Technical Debt

- O endpoint atual ainda usa `DeterministicTranscriber` e transforma áudio em
  seed textual; não é elegível para Real Consultation Success Rate.
- FHIR e journey stores ainda são in-memory; persistência durável pendente.
- Não há áudio clínico autorizado nem runtime de provider real disponível neste
  workspace.

### Próximo módulo

Real Consultation Input  
Status: READY — conectar áudio autorizado, provider Speech real e gateway de
persistência sem alterar o ClinicalJourneyExecutor.

## 2026-08-07 15:13:38 -03:00

### Capability Maturity Classification and Technical Cards

Status

🟢 Completed — classificação oficial e fichas técnicas registradas

Phase

Capability-first Product Strategy

Module

Capability Cards · Provider Maturity

Execution Time

5 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · Architecture simple, evidências completas

Tests

90 passed (baseline preservado)

Coverage

N/A

Decision

Approved pelo Astera Flow

### O que foi decidido?

Toda Capability passa a exibir explicitamente:

- `Specification Complete`;
- `Engineering Complete`;
- `Deterministic Provider`;
- `Real Provider Pending`;
- `Capability Certified`;
- `Production Ready`.

Nenhuma ficha pode usar “implementado”, “pronto” ou “concluído” sem qualificar
qual desses níveis foi demonstrado.

### Por que foi decidido?

Contratos, SDKs, plugins e testes locais demonstram maturidade de engenharia,
mas não demonstram que um engine real foi integrado, validado clinicamente ou
certificado para produção. A classificação torna essa diferença visível em uma
única leitura.

### O que foi implementado?

- Capability Cards para Speech, Vision, OCR, Medical NLP, Terminology, FHIR,
  Embeddings, Clinical Facts, Context, Reasoning, Knowledge, Documentation e
  Consultation Core.
- Provider atual e Target Provider explicitados por capability.
- Roadmap atualizado com a classificação oficial.
- Speech qualificado como `Engineering Complete`, `Deterministic Provider` e
  `Real Provider Pending`.
- Linguagem da estratégia ajustada para “Arquitetura simples. Evidências
  completas.”

### Como foi validado?

- Cards conferidos contra os ports, plugins e adapters existentes.
- Providers reais não foram declarados integrados sem adapter correspondente.
- `git diff --check`: passou.
- Suíte de software preservada em **90 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — classificação de maturidade documental  
[x] Observability — estado de evidência operacional explicitado

### Arquivos criados

- `docs/astera-flow/capabilities/capability-cards.md`

### Arquivos alterados

- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/capability-roadmap.md`
- `docs/astera-flow/capabilities/speech-transcription.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `Capability Definition — Five Questions`
- `Capability Certification Contract`

### Astera Flow

- Aba: `Capabilities / Maturity`
- Status: Atualizada — cards oficiais publicados
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. A integração dos providers reais continua
como trabalho de capability, preservando os contratos existentes.

### Próximo módulo

Real Provider Integration — Speech Transcription  
Status: READY — NVIDIA Parakeet permanece target provider; integração ainda não
foi realizada.

## 2026-08-07 15:11:13 -03:00

### Five-question Capability Rule

Status

🟢 Completed — processo de Capability simplificado

Phase

Capability-first Product Strategy

Module

Capability Definition Template · Architecture Freeze

Execution Time

5 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · Freeze v1.0

Tests

90 passed (baseline preservado)

Coverage

N/A

Decision

Approved pelo Astera Flow

### O que foi decidido?

Toda Capability nova deve responder apenas:

1. Qual problema resolve?
2. Qual contrato expõe?
3. Qual provider implementa?
4. Como é validada?
5. Quando pode receber Production Ready?

Certification, benchmark, CQA e Medical Validation são evidências do processo,
não novas camadas conceituais.

### Por que foi decidido?

O processo estava correndo o risco de ficar mais complexo que o produto. A
regra reduz a superfície de decisão sem remover a separação necessária entre
Engineering, validação clínica, CQA e produção.

### O que foi implementado?

- Template normativo de cinco perguntas.
- Capability Roadmap vinculado ao template.
- Certification Contract explicitamente tratado como evidência da quinta
  pergunta.
- Construction marcada como fase histórica concluída; operação futura passa a
  ser Capability-first.
- Speech documentado com transparência: adapters determinísticos existem, mas
  Parakeet/Whisper reais ainda não estão integrados.

### Como foi validado?

- Links e regras Markdown revisados.
- Nenhum novo conceito cognitivo ou ADR criado.
- `git diff --check`: passou.
- Suíte preservada em **90 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — simplificação do processo de Capability  
[x] Observability — gate permanece separado, sem falsa aprovação

### Arquivos criados

- `docs/astera-flow/capabilities/capability-definition-template.md`

### Arquivos alterados

- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/capability-certification.md`
- `docs/astera-flow/capabilities/speech-transcription.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `Capability Certification Contract`
- `Cognitive Validation Lab`

### Astera Flow

- Aba: `Capabilities`
- Status: Atualizada — Five-question Rule ativa
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. A integração de providers reais continua
como execução de capability, não como motivo para criar nova arquitetura.

### Próximo módulo

Real Provider Integration — Speech Transcription  
Status: READY — provider e versão devem ser aprovados pelo Astera Flow.

## 2026-08-07 15:06:47 -03:00

### Speech Transcription CQA Case Selection 001

Status

🟢 Completed — seleção e critérios preparados; CQA ainda não executado

Phase

Capability Certification / Cognitive QA

Module

Capability Zero — Speech Transcription CQA

Execution Time

2 min

Author

Agent Runtime

Architecture

Capability Validation · Cognitive Validation Lab · Freeze v1.0

Tests

90 passed (baseline preservado)

Coverage

N/A — nenhuma sessão clínica executada

Decision

Approved — seleção pronta sem promover casos candidatos

### O que foi decidido?

Separar três trilhas: benchmark acústico de Speech, CQA do modelo cognitivo e
Medical Validation. Casos textuais do registry não serão tratados como corpus
de áudio sem acesso, licença, desidentificação e provenance verificadas.

### Por que foi decidido?

Misturar essas trilhas produziria uma falsa métrica: um caso clínico pode validar
Facts/Context, mas não mede latência ou qualidade de transcrição sem áudio e
referência autorizados.

### O que foi implementado?

- CQA Case Selection 001.
- Critérios de entrada, separação de evidências e saída esperada.
- Referência à sessão de certificação Speech.
- Regra explícita de não armazenar dados clínicos brutos no repositório.

### Como foi validado?

- Seleção vinculada ao Case Registry e à Certification Session 001.
- Nenhum caso promovido e nenhum verdict clínico inventado.
- `git diff --check`: passou.
- Suíte preservada em **90 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — critérios de validação de capability  
[x] Observability — provenance e provider/version exigidos

### Arquivos criados

- `docs/astera-flow/capabilities/sessions/speech-transcription-cqa-selection-001.md`

### Arquivos alterados

- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/sessions/speech-transcription-certification-001.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `Cognitive Validation Lab`
- `Capability Certification Contract`
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: `Capabilities / Certification / CQA`
- Status: Atualizada — CQA Selection 001 READY
- Versão: `1.0`

### Technical Debt

Nenhuma dívida criada. A execução clínica depende de corpus e evidência de
acesso autorizados; a arquitetura permanece intacta.

### Próximo módulo

Speech Transcription CQA Validation Report  
Status: READY — executar somente após entrada autorizada no Case Registry.

## 2026-08-07 15:06:01 -03:00

### Speech Benchmark 001 preparado

Status

🟢 Completed — benchmark pronto para execução com corpus e providers aprovados

Phase

Capability Certification

Module

Capability Zero — Speech Transcription Benchmark

Execution Time

3 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · Evaluation Boundary

Tests

90 passed (baseline preservado)

Coverage

N/A — nenhuma medição de produção executada

Decision

Approved — benchmark preparado; nenhum resultado ou certificação inventado

### O que foi decidido?

O benchmark de Speech será executado somente com providers aprovados, corpus
autorizado, hardware e SLOs definidos pelo Astera Flow.

### Por que foi decidido?

Fixtures determinísticas comprovam contrato, mas não permitem inferir p95,
throughput, taxa de erro ou prontidão de produção. Métrica de performance também
não substitui Medical Validation ou CQA.

### O que foi implementado?

- Benchmark 001 com dimensões de latency, throughput, completude, erro,
  idioma e recursos.
- Regras de comparação e provenance.
- Entradas e saídas exigidas para o relatório reprodutível.

### Como foi validado?

- Documento vinculado à Certification Session 001.
- Nenhuma métrica foi preenchida sem execução real.
- `git diff --check`: passou.
- Suíte de software permanece em **90 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — benchmark e critérios de evidência  
[x] Observability — métricas de produção aguardando execução

### Arquivos criados

- `docs/astera-flow/capabilities/sessions/speech-transcription-benchmark-001.md`

### Arquivos alterados

- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/capability-roadmap.md`
- `docs/astera-flow/capabilities/speech-transcription.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `Capability Certification Contract`
- `EvaluationPlugin`
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: `Capabilities / Certification / Benchmarks`
- Status: Atualizada — Benchmark 001 READY
- Versão: `1.0`

### Technical Debt

Nenhuma dívida criada. A execução depende de provider, corpus, ambiente e SLOs
aprovados; essa dependência operacional não altera a arquitetura.

### Próximo módulo

Speech Transcription CQA Case Selection  
Status: READY

## 2026-08-07 15:05:12 -03:00

### Speech Transcription Certification Session 001

Status

🟡 In Progress — Engineering e Documentation aprovados; demais gates abertos

Phase

Capability Certification

Module

Capability Zero — `speech.transcription`

Execution Time

3 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · Certification Contract

Tests

90 passed (baseline preservado)

Coverage

N/A — sessão de certificação não substitui cobertura de código

Decision

Engineering Complete; Certification e Production Ready não emitidos

### O que foi decidido?

Abrir a sessão `speech-transcription-certification-001` com uma matriz de oito
gates. Apenas Engineering e Documentation possuem evidência suficiente hoje.

### Por que foi decidido?

O ciclo Capability-first precisa começar por um registro auditável. Declarar
Speech como Production Ready sem Medical Validation, CQA, regressão,
performance, segurança e observabilidade específicas confundiria contrato local
com capacidade de produção.

### O que foi implementado?

- Sessão de certificação versionada para Speech Transcription.
- Matriz de gates com evidências e estados `PASS`/`NOT RUN`.
- Próximas evidências explicitadas sem alterar Speech SDK, Kernel ou Plugin.

### Como foi validado?

- Engineering vinculado ao teste do Speech Plugin e aos contratos do SDK.
- Documentation vinculada ao capability record.
- `Production Ready` permanece tecnicamente impedido pelo Certification SDK
  enquanto houver gates ausentes.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — registro de certificação  
[x] Observability — gate aguardando evidência operacional

### Arquivos criados

- `docs/astera-flow/capabilities/sessions/speech-transcription-certification-001.md`

### Arquivos alterados

- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/speech-transcription.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `Capability Certification Contract`
- `Cognitive Validation Lab`

### Astera Flow

- Aba: `Capabilities / Certification`
- Status: Atualizada — Session 001 aberta
- Versão: `1.0`

### Technical Debt

Nenhuma dívida criada. Gaps de certificação são gates ainda não executados, não
alterações arquiteturais necessárias.

### Próximo módulo

Speech Benchmark + CQA Case Selection  
Status: READY

## 2026-08-07 15:04:23 -03:00

### Capability Certification SDK

Status

🟢 Completed — Certification Contract implementado e validado

Phase

Product Capabilities / Capability Zero

Module

Capability Certification Contract

Execution Time

4 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · Governance SDK · Freeze v1.0

Tests

90 passed · 4 warnings

Coverage

N/A

Decision

Approved — nenhum status Production Ready emitido sem evidência completa

### O que foi decidido?

O status `Production Ready` passa a ser protegido pelo contrato de certificação.
Uma capability precisa apresentar oito gates obrigatórios em `PASS`, cada um
com evidência, antes de receber certificação de produção.

### Por que foi decidido?

O Speech Plugin já possui Engineering Complete, mas testes determinísticos não
comprovam Medical Validation, CQA, performance, segurança, observabilidade ou
regressão de produção. O contrato impede que maturidade de engenharia seja
confundida com readiness do produto.

### O que foi implementado?

- `CapabilityGate` com status, reviewer, notas e evidence refs.
- `CapabilityCertification` com os oito gates obrigatórios.
- Regra executável que rejeita `Production Ready` incompleto.
- Serialização de status, gates faltantes e evidências.
- Testes para certificação incompleta, completa e gate sem evidência.

### Como foi validado?

- Testes do Certification SDK: **3 passed**.
- Suíte completa: **90 passed**, com 4 warnings de depreciação já existentes.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — contrato de governança de capability  
[x] Observability — gate definido, sem emitir aprovação automaticamente

### Arquivos criados

- `packages/capability_sdk/models.py`
- `packages/capability_sdk/__init__.py`
- `apps/runtime/tests/test_capability_certification.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `docs/astera-flow/capabilities/capability-certification.md`
- `docs/astera-flow/cognitive-validation-lab/README.md`

### Astera Flow

- Aba: `Capabilities / Certification`
- Status: Atualizada — contrato implementado
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. O primeiro Certification Record real depende
da execução dos gates de Speech Transcription.

### Próximo módulo

Speech Transcription Certification Session  
Status: READY

## 2026-08-07 15:02:51 -03:00

### Capability-first Product Strategy

Status

🟢 Completed — Capability Roadmap e Certification Contract registrados

Phase

Product Capabilities

Module

Capability Zero — Speech Transcription

Execution Time

8 min

Author

Agent Runtime

Architecture

Capability → Provider → Plugin · Architecture Freeze v1.0

Tests

87 passed (software baseline preservado)

Coverage

N/A — gates de capability ainda não possuem métricas quantitativas

Decision

Approved pelo Astera Flow como estratégia de produto

### O que foi decidido?

- A unidade de roadmap passa a ser `Capability`, não Sprint ou módulo interno.
- O ciclo de produto passa a ser `Capability → Engineering → Medical
  Validation → CQA → Regression → Certification → Production`.
- `Speech Transcription` foi escolhido como Capability Zero.
- `Production Ready` não foi emitido: a evidência atual prova Engineering
  Complete, não certificação clínica ou operacional.

### Por que foi decidido?

Usuários consomem capacidades, enquanto Provider e Plugin são mecanismos de
entrega substituíveis. Uma capability certificada demonstra o ciclo completo de
produto e cria um processo repetível para Vision, OCR, Labs, Imaging e demais
capacidades.

### O que foi implementado?

- Capability Roadmap e status board.
- Capability Certification Contract com gates obrigatórios.
- Registro específico de Capability Zero — Speech Transcription.
- Cognitive Validation Lab atualizado para validar capabilities e regression
  baselines de capabilities.
- Board inicial sem percentuais inventados: apenas PASS, NOT RUN, NOT ISSUED e
  NOT READY conforme evidência disponível.

### Como foi validado?

- Speech Engineering: PASS por SDK, plugin lifecycle, provider health e testes.
- Documentação: PASS para o contrato e operação conhecida.
- Medical Validation, CQA, Regression, Performance, Security e Observability
  específica: ainda não executados, portanto certificação não emitida.
- Suíte de software preservada em **87 passed**.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — governança de capability e certificação  
[x] Observability — novo gate de certificação, sem implementação de provider

### Arquivos criados

- `docs/astera-flow/capabilities/README.md`
- `docs/astera-flow/capabilities/capability-roadmap.md`
- `docs/astera-flow/capabilities/capability-certification.md`
- `docs/astera-flow/capabilities/speech-transcription.md`

### Arquivos alterados

- `docs/astera-flow/README.md`
- `docs/astera-flow/cognitive-validation-lab/README.md`
- `docs/astera-flow/cognitive-validation-lab/regression-suite.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `CapabilityType` e Capability Registry
- `Cognitive Validation Lab`

### Astera Flow

- Aba: `Capabilities`
- Status: Atualizada — Capability-first
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. Falta executar os gates de certificação do
Speech com evidências específicas; isso é trabalho planejado, não um bloqueio
arquitetural.

### Próximo módulo

Capability Zero — Speech Transcription Certification Session  
Status: READY

## 2026-08-07 11:22:51 -03:00

### Sprint C4.1 — Speech Plugin

O Astera Flow define Speech como o primeiro módulo de Open Source AI Modules
e mantém Parakeet como tecnologia aprovada para a integração de áudio. A
implementação adiciona a fronteira de capability e o plugin, sem acoplar o
Runtime ao engine de inferência ou exigir GPU no ambiente de testes.

O que foi decidido?

- Speech é exposto ao Kernel exclusivamente através do Plugin SDK.
- O provider de transcrição é injetado pela composição do plugin.
- O transcript é um contrato estruturado com segmentos, timestamps,
  confiança, idioma e provider para manter rastreabilidade.

O que foi implementado?

- `AudioRequest`, `TranscriptSegment` e `Transcript` no Speech SDK.
- Port `SpeechTranscriber` para providers aprovados ou substituíveis.
- `DeterministicTranscriber` para testes locais sem infraestrutura de GPU.
- `SpeechPlugin` com lifecycle, registro de provider e capabilities de
  transcrição/detecção de idioma.
- Conversão da invocação do plugin para o contrato de transcript serializável.

Como foi validado?

- `pytest -q`: **23 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre registro, provider saudável, transcrição, idioma, lifecycle e
  resolução do plugin.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — Speech  
Execution Time: 2 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 23 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/speech_sdk/__init__.py`
- `packages/speech_sdk/models.py`
- `packages/speech_sdk/protocol.py`
- `packages/speech_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/speech/__init__.py`
- `apps/runtime/src/application/plugins/speech/plugin.py`
- `apps/runtime/tests/test_speech_plugin.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / Speech
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Adapter Parakeet real, streaming, diarização e processamento de áudio
  permanecem como extensões do port aprovado.

### Próximo módulo

Open Source AI Modules — Vision  
Status: READY

## 2026-08-07 11:24:19 -03:00

### Sprint C4.2 — Vision Plugin

O Astera Flow define Vision como o segundo módulo de Open Source AI Modules.
O catálogo mantém os modelos de visão em benchmark; por isso esta entrega
fecha o contrato estável do módulo e deixa a escolha do engine atrás de um
provider substituível.

O que foi implementado?

- `ImageRequest` e `VisionResult` como contratos serializáveis.
- Port `ImageAnalyzer` para desacoplar o plugin do modelo escolhido.
- `DeterministicImageAnalyzer` para validação local sem GPU.
- `VisionPlugin` com lifecycle, provider e capability
  `vision.classification` registrados no Kernel.
- Resultado com labels, objects, texto, provider e request id.

Como foi validado?

- `pytest -q`: **24 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre registro, provider saudável, análise, serialização e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — Vision  
Execution Time: 2 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 24 passed  
Coverage: N/A  
Decision: Módulo especificado pelo Astera Flow; engine mantido atrás de port

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/vision_sdk/__init__.py`
- `packages/vision_sdk/models.py`
- `packages/vision_sdk/protocol.py`
- `packages/vision_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/vision/__init__.py`
- `apps/runtime/src/application/plugins/vision/plugin.py`
- `apps/runtime/tests/test_vision_plugin.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / Vision
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Engine de visão aprovado pelo Flow ainda precisa ser conectado quando a
  seleção do catálogo estiver definida.

### Próximo módulo

Open Source AI Modules — OCR  
Status: READY

## 2026-08-07 11:25:39 -03:00

### Sprint C4.3 — OCR Plugin

O Astera Flow define OCR como o terceiro módulo da sequência de Open Source AI
Modules. O catálogo mantém os modelos de OCR em benchmark; o contrato foi
implementado de forma independente do engine para preservar substituibilidade.

O que foi implementado?

- `OcrRequest`, `OcrBlock` e `OcrResult` com texto, página, confiança,
  idioma e provider.
- Port `OcrEngine` para desacoplar a capacidade de extração do modelo.
- `DeterministicOcrEngine` para testes sem dependência externa.
- `OcrPlugin` com lifecycle, provider e capability `vision.ocr` registrados no
  Kernel.
- Serialização de resultado adequada ao transporte do Runtime.

Como foi validado?

- `pytest -q`: **25 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre registro, provider saudável, extração, confiança, serialização
  e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — OCR  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 25 passed  
Coverage: N/A  
Decision: Módulo especificado pelo Astera Flow; engine mantido atrás de port

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/ocr_sdk/__init__.py`
- `packages/ocr_sdk/models.py`
- `packages/ocr_sdk/protocol.py`
- `packages/ocr_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/ocr/__init__.py`
- `apps/runtime/src/application/plugins/ocr/plugin.py`
- `apps/runtime/tests/test_ocr_plugin.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / OCR
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Engine OCR selecionado pelo benchmark ainda precisa ser conectado ao port.

### Próximo módulo

Open Source AI Modules — Medical NLP  
Status: READY

## 2026-08-07 11:27:02 -03:00

### Sprint C4.4 — Medical NLP Plugin

O Astera Flow define Medical NLP como o quarto módulo da sequência. O catálogo
aponta MedSpacy como opção aprovada na arquitetura visual e mantém o conjunto
de engines atrás do benchmark; o plugin permanece provider-neutral.

O que foi implementado?

- `NlpRequest`, `ClinicalEntity` e `NlpResult` com offsets, label, idioma e
  assertion/negação.
- Port `MedicalNlpProcessor` sem acoplamento a spaCy, MedSpacy ou outro engine.
- `DeterministicMedicalNlp` para validação local.
- `MedicalNlpPlugin` com lifecycle, provider e capability
  `nlp.entity_extraction` registrados no Kernel.
- Serialização de entidades para o contrato de transporte do Runtime.

Como foi validado?

- `pytest -q`: **26 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre registro, provider saudável, entidade, assertion, idioma,
  serialização e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — Medical NLP  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 26 passed  
Coverage: N/A  
Decision: Módulo especificado pelo Astera Flow; engine mantido atrás de port

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/medical_nlp_sdk/__init__.py`
- `packages/medical_nlp_sdk/models.py`
- `packages/medical_nlp_sdk/protocol.py`
- `packages/medical_nlp_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/medical_nlp/__init__.py`
- `apps/runtime/src/application/plugins/medical_nlp/plugin.py`
- `apps/runtime/tests/test_medical_nlp_plugin.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / Medical NLP
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Engine Medical NLP selecionado pelo benchmark ainda precisa ser conectado ao
  port; este módulo não executa decisão clínica.

### Próximo módulo

Open Source AI Modules — Terminology  
Status: READY

## 2026-08-07 11:28:36 -03:00

### Sprint C4.5 — Terminology Plugin

O Astera Flow define Terminology como o quinto módulo. Snowstorm e LOINC estão
aprovados no catálogo para a camada de conhecimento; esta entrega fecha o
contrato comum de lookup sem acoplar o Runtime a um servidor específico.

O que foi implementado?

- `TerminologyQuery`, `TerminologyConcept` e `TerminologyResult` com sistema,
  código, display, versão e estado ativo.
- Port `TerminologyService` para Snowstorm, LOINC e providers compatíveis.
- `DeterministicTerminologyService` para testes locais versionados.
- `TerminologyPlugin` com lifecycle, provider e capability
  `medical.terminology` registrados no Kernel.
- Lookup por código ou texto com preservação de versão na resposta.

Como foi validado?

- `pytest -q`: **27 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre registro, provider saudável, lookup versionado, serialização e
  lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — Terminology  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 27 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/terminology_sdk/__init__.py`
- `packages/terminology_sdk/models.py`
- `packages/terminology_sdk/protocol.py`
- `packages/terminology_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/terminology/__init__.py`
- `apps/runtime/src/application/plugins/terminology/plugin.py`
- `apps/runtime/tests/test_terminology_plugin.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / Terminology
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Conectores reais para Snowstorm e demais terminologias ainda precisam ser
  implementados atrás do port aprovado.

### Próximo módulo

Open Source AI Modules — FHIR  
Status: READY

## 2026-08-07 11:34:15 -03:00

### Sprint C4.6 — FHIR Plugin

O Astera Flow define FHIR como o sexto módulo da sequência e aprova HAPI FHIR
como implementação de referência para o Gateway. Esta entrega fecha a
fronteira provider-neutral para interoperabilidade HL7 FHIR.

O que foi implementado?

- `FhirResource` com mapeamento `resourceType`, id e payload interoperável.
- `FhirBundle` para agrupamento de recursos e contagem de entries.
- Port `FhirGateway` com validação, create, read e bundle.
- `InMemoryFhirGateway` para validação local sem servidor externo.
- `FhirPlugin` com lifecycle e capability `medical.fhir` registrados no Kernel.
- Operações do plugin para validar, criar, ler e gerar Bundle.

Como foi validado?

- `pytest -q`: **28 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre resource mapping, validação, create/read, bundle e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — FHIR  
Execution Time: 5 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 28 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/fhir_sdk/__init__.py`
- `packages/fhir_sdk/models.py`
- `packages/fhir_sdk/protocol.py`
- `packages/fhir_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/fhir/__init__.py`
- `apps/runtime/src/application/plugins/fhir/plugin.py`
- `apps/runtime/tests/test_fhir_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / FHIR
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Adapter HAPI FHIR real e validação por perfil ainda precisam ser conectados
  atrás do port aprovado.

### Próximo módulo

Open Source AI Modules — Embeddings  
Status: READY

## 2026-08-07 11:35:42 -03:00

### Sprint C4.7 — Embeddings Plugin

O Astera Flow define Embeddings como o sétimo módulo e aprova BGE-M3 no
catálogo para integração com o Knowledge Layer. Esta entrega cria o contrato
de encoding em lote e mantém o modelo atrás do provider do plugin.

O que foi implementado?

- `EmbeddingRequest`, `EmbeddingVector` e `EmbeddingResult` com modelo,
  dimensão e índices preservados.
- Port `Embedder` para desacoplar BGE-M3 de outros providers.
- `DeterministicEmbedder` com vetores estáveis e normalizados para testes.
- `EmbeddingsPlugin` com lifecycle, provider e capability
  `knowledge.embeddings` registrados no Kernel.
- Encoding em lote e serialização para consumo do Knowledge Layer.

Como foi validado?

- `pytest -q`: **29 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre batch, dimensões, provider, normalização e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — Embeddings  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 29 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/embeddings_sdk/__init__.py`
- `packages/embeddings_sdk/models.py`
- `packages/embeddings_sdk/protocol.py`
- `packages/embeddings_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/embeddings/__init__.py`
- `apps/runtime/src/application/plugins/embeddings/plugin.py`
- `apps/runtime/tests/test_embeddings_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / Embeddings
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Provider BGE-M3 real, batching operacional e persistência vetorial ainda
  precisam ser conectados ao Knowledge Store.

### Próximo módulo

Open Source AI Modules — Evaluation  
Status: READY

## 2026-08-07 11:37:07 -03:00

### Sprint C4.8 — Evaluation Plugin

O Astera Flow define Evaluation como o oitavo e último módulo da sequência de
Open Source AI Modules e aprova DeepEval para a camada de avaliação. Esta
entrega cria o contrato de métricas e deixa o framework externo atrás do
provider do plugin.

O que foi implementado?

- `EvaluationRequest`, `MetricResult` e `EvaluationResult` com score,
  aprovação e justificativa.
- Port `Evaluator` para DeepEval e providers compatíveis.
- `DeterministicEvaluator` com métricas de resposta presente e reference match.
- `EvaluationPlugin` com lifecycle, provider e capability
  `quality.evaluation` registrados no Kernel.
- Resultado serializável para integração com CI/CD e Observability.

Como foi validado?

- `pytest -q`: **30 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre métricas, aprovação, provider e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Open Source AI Modules — Evaluation  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 30 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/evaluation_sdk/__init__.py`
- `packages/evaluation_sdk/models.py`
- `packages/evaluation_sdk/protocol.py`
- `packages/evaluation_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/evaluation/__init__.py`
- `apps/runtime/src/application/plugins/evaluation/plugin.py`
- `apps/runtime/tests/test_evaluation_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Open Source AI Modules / Evaluation
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Integração DeepEval real, métricas de faithfulness/hallucination e execução
  em CI/CD ainda precisam ser conectadas ao port aprovado.

### Próximo módulo

LiteLLM — Model Router  
Status: READY

## 2026-08-07 11:38:46 -03:00

### Sprint C5 — LiteLLM-compatible Model Gateway

O Astera Flow define o Sprint C5 com Model Router, Fallback, Model Selection e
Observability. LiteLLM está aprovado no catálogo como gateway oficial entre o
Google ADK e as APIs de modelos. Esta entrega implementa a fronteira de
roteamento sem acoplar o Runtime ao proxy externo.

O que foi implementado?

- `ChatMessage`, `CompletionRequest` e `CompletionResponse`.
- Ports `LlmProvider` e `LlmRouter` para seleção e execução de modelos.
- `ModelRouter` com ordem explícita de providers e fallback automático.
- `DeterministicLlmProvider` para testes locais.
- `LlmGatewayPlugin` com lifecycle e capability `ai.text_generation`.
- Preservação de provider, modelo, conteúdo, finish reason e usage na resposta.

Como foi validado?

- `pytest -q`: **31 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre seleção, fallback, resposta, provider saudável e lifecycle.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: LiteLLM — Model Router  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Plugin First · Provider Neutral  
Tests: 31 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/llm_sdk/__init__.py`
- `packages/llm_sdk/models.py`
- `packages/llm_sdk/protocol.py`
- `packages/llm_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/llm_gateway/__init__.py`
- `apps/runtime/src/application/plugins/llm_gateway/plugin.py`
- `apps/runtime/tests/test_llm_gateway_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Engineering Roadmap / Sprint C5 — LiteLLM
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Adapter LiteLLM real, observabilidade de chamadas, rate limiting e políticas
  de custo ainda precisam ser conectados ao gateway.

### Próximo módulo

Primeiro agente cognitivo funcionando  
Status: READY

## 2026-08-07 11:45:35 -03:00

### Critério da Fase C — Primeiro Cognitive Agent funcionando

O Astera Flow define como critério da Fase C o primeiro agente cognitivo
funcionando. A composição implementada conecta as entregas anteriores em um
fluxo único e rastreável:

```text
Knowledge Source
  → Parser / Knowledge Store
  → Retriever / Ranking
  → Cognitive Agent
  → LLM Gateway / Fallback
  → Resposta + Evidências versionadas
```

O que foi decidido?

- O agente não acessa fontes diretamente; recebe evidências pelo port do
  Knowledge Layer.
- O gateway de modelos continua substituível e aplica fallback antes de
  devolver uma resposta.
- Toda resposta cognitiva carrega request id, provider, modelo e referências
  de fonte, documento, chunk e versão.

O que foi implementado?

- `CognitiveRequest`, `CognitiveEvidence` e `CognitiveResponse`.
- `CognitiveAgent` com recuperação de evidência, construção de contexto e
  geração pelo `LlmRouter`.
- `CognitiveAgentPlugin` com lifecycle e capability `cognitive.query`.
- Teste end-to-end de fonte médica até resposta fundamentada.

Como foi validado?

- `pytest -q`: **32 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: ingestão → retrieval → contexto → modelo → evidência.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: C  
Module: Primeiro Cognitive Agent  
Execution Time: 7 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 32 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/cognitive_sdk/__init__.py`
- `packages/cognitive_sdk/models.py`
- `apps/runtime/src/application/cognitive/__init__.py`
- `apps/runtime/src/application/cognitive/agent.py`
- `apps/runtime/src/application/plugins/cognitive_agent/__init__.py`
- `apps/runtime/src/application/plugins/cognitive_agent/plugin.py`
- `apps/runtime/tests/test_cognitive_agent.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Engineering Roadmap / Critério da Fase C
- Status: Atualizada — primeiro agente cognitivo validado
- Versão: 1.0

### Technical Debt

- Persistência externa de sessões, observabilidade de tokens e execução real
  dos providers Google ADK/LiteLLM ainda precisam ser conectadas aos adapters
  de infraestrutura.

### Próximo módulo

Evidence Pipeline — Speech → Evidence  
Status: READY

## 2026-08-07 11:47:14 -03:00

### Sprint D1 — Evidence Pipeline

O Astera Flow define o primeiro pipeline clínico como `Speech → Evidence`.
Esta entrega transforma segmentos de transcrição em evidências estruturadas,
sem interpretar, diagnosticar ou substituir a decisão profissional.

O que foi implementado?

- `EvidenceItem` com encounter, origem, tipo, conteúdo, timestamps,
  confiança, speaker e metadata.
- `EvidenceBatch` com integridade de pertencimento ao encounter.
- Port `EvidenceExtractor` para providers de extração substituíveis.
- `TranscriptEvidenceExtractor` preservando a proveniência do Speech Plugin.
- `EvidencePlugin` com lifecycle e capability `cognitive.evidence`.
- Integração de payload de transcript para lote de evidências rastreáveis.

Como foi validado?

- `pytest -q`: **33 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: transcript → evidence batch → origem e timestamps
  preservados.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: D  
Module: Evidence Pipeline — Speech → Evidence  
Execution Time: 2 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 33 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/evidence_sdk/__init__.py`
- `packages/evidence_sdk/models.py`
- `packages/evidence_sdk/protocol.py`
- `packages/evidence_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/evidence/__init__.py`
- `apps/runtime/src/application/plugins/evidence/plugin.py`
- `apps/runtime/tests/test_evidence_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Clinical Platform / Sprint D1 — Evidence Pipeline
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Persistência de evidências, eventos NATS e validação humana ainda serão
  conectados nas próximas etapas clínicas.

### Próximo módulo

Correlation Pipeline — Evidence → Correlation  
Status: READY

## 2026-08-07 11:48:46 -03:00

### Sprint D2 — Correlation Pipeline

O Astera Flow define o segundo pipeline clínico como `Evidence → Correlation`.
Esta entrega identifica relações explícitas entre evidências e preserva a
separação entre correlação, entendimento e decisão clínica.

O que foi implementado?

- `Correlation` com ids de evidências, tipo de relação, rationale, confiança e
  metadata.
- `CorrelationBatch` com integridade de pertencimento ao encounter.
- Port `CorrelationEngine` para engines substituíveis.
- `SharedTermCorrelationEngine` determinístico para correlações por termos
  compartilhados.
- `CorrelationPlugin` com lifecycle e capability `cognitive.correlation`.
- Preservação dos ids de evidência na resposta correlacionada.

Como foi validado?

- `pytest -q`: **34 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: evidence batch → relação explícita → ids e rationale.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: D  
Module: Correlation Pipeline — Evidence → Correlation  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 34 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/correlation_sdk/__init__.py`
- `packages/correlation_sdk/models.py`
- `packages/correlation_sdk/protocol.py`
- `packages/correlation_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/correlation/__init__.py`
- `apps/runtime/src/application/plugins/correlation/plugin.py`
- `apps/runtime/tests/test_correlation_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Clinical Platform / Sprint D2 — Correlation Pipeline
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Correlator clínico contextual, persistência das relações e revisão humana
  ainda serão conectados nas próximas etapas.

### Próximo módulo

Understanding Pipeline — Correlation → Understanding  
Status: READY

## 2026-08-07 11:50:23 -03:00

### Sprint D3 — Understanding Pipeline

O Astera Flow define o terceiro pipeline clínico como
`Correlation → Understanding`. Esta entrega transforma relações explícitas em
um snapshot provisório, revisável e fundamentado, sem emitir diagnóstico ou
conduta clínica.

O que foi implementado?

- `UnderstandingStatement` com texto, evidências, correlações, confiança e
  metadata.
- `UnderstandingSnapshot` com encounter e status `draft`.
- Port `UnderstandingEngine` para engines substituíveis.
- `CorrelationUnderstandingEngine` determinístico para materializar relações
  em afirmações revisáveis.
- `UnderstandingPlugin` com lifecycle e capability `cognitive.understanding`.
- Preservação dos ids de evidências e correlações no snapshot.

Como foi validado?

- `pytest -q`: **35 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: correlation batch → snapshot draft → referências preservadas.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: D  
Module: Understanding Pipeline — Correlation → Understanding  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 35 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/understanding_sdk/__init__.py`
- `packages/understanding_sdk/models.py`
- `packages/understanding_sdk/protocol.py`
- `packages/understanding_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/understanding/__init__.py`
- `apps/runtime/src/application/plugins/understanding/plugin.py`
- `apps/runtime/tests/test_understanding_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Clinical Platform / Sprint D3 — Understanding Pipeline
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Engine contextual com LLM, persistência de snapshots e revisão humana ainda
  serão conectados nas próximas etapas.

### Próximo módulo

Knowledge Pipeline — Understanding → Knowledge  
Status: READY

## 2026-08-07 11:51:53 -03:00

### Sprint D4 — Knowledge Pipeline

O Astera Flow define o quarto pipeline clínico como
`Understanding → Knowledge`. Esta entrega consolida snapshots provisórios em
conhecimento estruturado e versionado, mantendo representação documental fora
desta camada.

O que foi implementado?

- `KnowledgeRecord` com encounter, versão, statements, evidências e
  correlações de origem.
- Port `KnowledgeEngine` para engines de consolidação substituíveis.
- `SnapshotKnowledgeEngine` determinístico para consolidação local.
- `KnowledgePlugin` com lifecycle e capability `cognitive.knowledge`.
- Preservação dos ids de evidência e correlação no conhecimento consolidado.

Como foi validado?

- `pytest -q`: **36 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: understanding snapshot → knowledge record versionado.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: D  
Module: Knowledge Pipeline — Understanding → Knowledge  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 36 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/knowledge_pipeline_sdk/__init__.py`
- `packages/knowledge_pipeline_sdk/models.py`
- `packages/knowledge_pipeline_sdk/protocol.py`
- `packages/knowledge_pipeline_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/knowledge/__init__.py`
- `apps/runtime/src/application/plugins/knowledge/plugin.py`
- `apps/runtime/tests/test_knowledge_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Clinical Platform / Sprint D4 — Knowledge Pipeline
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Persistência do conhecimento, versionamento concorrente e validação
  profissional ainda serão conectados nas próximas etapas.

### Próximo módulo

Representation Pipeline — Knowledge → SOAP → FHIR → Summary  
Status: READY

## 2026-08-07 11:53:24 -03:00

### Sprint D5 — Representation Pipeline

O Astera Flow define o quinto pipeline clínico como
`Knowledge → SOAP → FHIR → Summary`. Esta entrega materializa o mesmo
conhecimento em representações diferentes sem duplicar ou alterar o
`KnowledgeRecord` de origem.

O que foi implementado?

- `RepresentationRequest`, `Representation`, e `RepresentationResult`.
- Port `RepresentationEngine` para renderizadores substituíveis.
- `KnowledgeRepresentationEngine` com SOAP draft, DocumentReference FHIR e
  Summary.
- `RepresentationPlugin` com lifecycle e capability
  `cognitive.representation`.
- Preservação do record id e da versão em todas as representações.

Como foi validado?

- `pytest -q`: **37 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: knowledge record → SOAP/FHIR/Summary com fonte única.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: D  
Module: Representation Pipeline — Knowledge → SOAP → FHIR → Summary  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 37 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/representation_sdk/__init__.py`
- `packages/representation_sdk/models.py`
- `packages/representation_sdk/protocol.py`
- `packages/representation_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/representation/__init__.py`
- `apps/runtime/src/application/plugins/representation/plugin.py`
- `apps/runtime/tests/test_representation_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Clinical Platform / Sprint D5 — Representation Pipeline
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- SOAP clínico semântico, validação FHIR por perfil e revisão profissional
  ainda serão conectados antes de uso clínico real.

### Próximo módulo

Primeira consulta completa  
Status: READY

## 2026-08-07 11:54:46 -03:00

### Critério da Fase D — Primeira consulta completa

O Astera Flow define como critério da Clinical Platform uma consulta completa.
O pipeline agora compõe todas as etapas clínicas especificadas:

```text
Speech
  → Evidence
  → Correlation
  → Understanding
  → Knowledge
  → SOAP / FHIR / Summary
```

O que foi implementado?

- `ConsultationResult` agregando transcript, evidências, correlações,
  entendimento, conhecimento e representações.
- `ConsultationPipeline` compondo os ports dos cinco estágios clínicos.
- Integração end-to-end com transcrição segmentada e proveniência preservada.
- Geração das três representações a partir do mesmo Knowledge Record.

Como foi validado?

- `pytest -q`: **38 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo completo validado: Speech → Evidence → Correlation → Understanding →
  Knowledge → SOAP/FHIR/Summary.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: D  
Module: Primeira consulta completa  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 38 passed  
Coverage: N/A  
Decision: Critério especificado pelo Astera Flow validado

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/clinical_pipeline_sdk/__init__.py`
- `packages/clinical_pipeline_sdk/models.py`
- `apps/runtime/src/application/clinical/__init__.py`
- `apps/runtime/src/application/clinical/consultation.py`
- `apps/runtime/tests/test_consultation_pipeline.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Clinical Platform / Critério da Fase D
- Status: Atualizada — primeira consulta completa validada
- Versão: 1.0

### Technical Debt

- Integração com API oficial, persistência de encounter, autenticação,
  observabilidade distribuída e revisão profissional ainda precisam ser
  conectadas antes de operação clínica.

### Próximo módulo

Experience Layer — Login / Workspace / Encounter  
Status: READY

## 2026-08-07 11:58:08 -03:00

### Fase F — Login / Authentication Foundation

O Astera Flow define Login como a primeira entrega da Experience Layer e
especifica JWT, Refresh Token, RBAC e Permissions. A arquitetura visual aponta
Keycloak como Auth Gateway; o Runtime agora expõe um contrato compatível e
mantém o provider de identidade substituível.

O que foi implementado?

- `LoginCredentials`, `Principal` e `AuthTokens`.
- `AuthService` com hash PBKDF2, JWT HS256, claims de organização/workspaces,
  roles e permissions.
- Refresh token opaco com rotação e invalidação do token anterior.
- Verificação de permissionamento RBAC através de `require_permission`.
- Endpoints versionados `POST /api/v1/auth/login` e
  `POST /api/v1/auth/refresh`.
- Configurações `ASTERA_AUTH_SECRET` e `ASTERA_AUTH_ACCESS_TTL_SECONDS`.
- Router de autenticação conectado ao bootstrap oficial.

Como foi validado?

- `pytest -q`: **42 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Testes cobrem login, claims, RBAC, refresh rotation, rejeição de credenciais
  inválidas e contrato HTTP.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Login  
Execution Time: 6 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Provider Neutral  
Tests: 42 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow; Keycloak preservado atrás do adapter

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/auth_sdk/__init__.py`
- `packages/auth_sdk/models.py`
- `packages/auth_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/auth.py`
- `apps/runtime/tests/test_auth_sdk.py`
- `apps/runtime/tests/test_auth_http.py`

### Arquivos alterados

- `requirements.txt`
- `apps/runtime/src/infrastructure/settings/__init__.py`
- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Login
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Adapter Keycloak, armazenamento persistente de identidades e secrets
  externos ainda precisam substituir o provider em memória antes de produção.

### Próximo módulo

Experience Layer — Workspace  
Status: READY

## 2026-08-07 11:59:21 -03:00

### Fase F — Workspace

O Astera Flow define Workspace como a segunda entrega da Experience Layer.
Esta implementação mantém o isolamento multi-tenant na fronteira da API:
claims de organização e workspaces determinam o que o profissional pode
visualizar.

O que foi implementado?

- `Workspace` como contrato imutável com organização, nome e slug.
- `WorkspaceDirectory` provider-neutral para registro e consulta de memberships.
- Endpoint autenticado `GET /api/v1/workspaces`.
- Integração do Workspace Directory no bootstrap oficial.
- Filtro simultâneo por `organization_id` e `workspace_ids` do principal.

Como foi validado?

- `pytest -q`: **43 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste garante que workspaces de outra organização ou sem membership não são
  retornados.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Workspace  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Multi-tenant  
Tests: 43 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/workspace_sdk/__init__.py`
- `packages/workspace_sdk/models.py`
- `packages/workspace_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/workspaces.py`
- `apps/runtime/tests/test_workspace.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Workspace
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Persistência de workspaces, convites, membership administrativo e adapter
  Keycloak ainda serão conectados.

### Próximo módulo

Experience Layer — Encounter  
Status: READY

## 2026-08-07 12:01:25 -03:00

### Fase F — Encounter

O Astera Flow define Encounter como a terceira entrega da Experience Layer e
o fluxo obrigatório após Login e Workspace. O atendimento agora possui
lifecycle explícito, vínculo com paciente e profissional e isolamento por
organização/workspace.

O que foi implementado?

- `Encounter` com status `planned`, `in_progress` e `completed`.
- `EncounterDirectory` para criação e transições de lifecycle.
- Autorização por organização, workspace e profissional atribuído.
- Endpoints versionados para criar, iniciar e concluir encounters.
- Integração do Encounter Directory no bootstrap oficial.
- Integração com `ContextManager` para anexar encounter à runtime session.

Como foi validado?

- `pytest -q`: **45 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Testes cobrem lifecycle, timestamps, tenant isolation e contexto clínico.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Encounter  
Execution Time: 2 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Multi-tenant  
Tests: 45 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/encounter_sdk/__init__.py`
- `packages/encounter_sdk/models.py`
- `packages/encounter_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/encounters.py`
- `apps/runtime/tests/test_encounter.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Encounter
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Persistência de encounters, Patient Directory, auditoria e integração com
  FHIR Gateway ainda serão conectados.

### Próximo módulo

Experience Layer — Patient  
Status: READY

## 2026-08-07 12:02:33 -03:00

### Fase F — Patient

O Astera Flow define Patient como a quarta entrega da Experience Layer e como
parte do fluxo obrigatório após Login: `Login → Patient → Novo Encounter`.
Esta implementação mantém registros de paciente isolados por organização.

O que foi implementado?

- `Patient` como contrato imutável de identidade e status ativo.
- `PatientDirectory` provider-neutral para criação, consulta e listagem.
- Endpoints autenticados `POST /api/v1/patients` e `GET /api/v1/patients`.
- Integração do Patient Directory no bootstrap oficial.
- Isolamento de pacientes por `organization_id` do principal autenticado.

Como foi validado?

- `pytest -q`: **46 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste garante que profissionais de outra organização não acessam o paciente.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Patient  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Multi-tenant  
Tests: 46 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/patient_sdk/__init__.py`
- `packages/patient_sdk/models.py`
- `packages/patient_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/patients.py`
- `apps/runtime/tests/test_patient.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Patient
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Persistência clínica, identificadores externos, consentimento e auditoria de
  acesso ainda serão conectados antes de uso real.

### Próximo módulo

Experience Layer — Timeline  
Status: READY

## 2026-08-07 12:03:43 -03:00

### Fase F — Timeline

O Astera Flow define Timeline como a quinta entrega da Experience Layer. A
timeline agora representa eventos ordenáveis do paciente, vinculados à
organização e opcionalmente a um encounter.

O que foi implementado?

- `TimelineEvent` com tipo, timestamp, paciente, encounter e payload.
- `TimelineDirectory` append-only para registro e consulta temporal.
- Endpoint autenticado `GET /api/v1/patients/{patient_id}/timeline`.
- Integração do Timeline Directory no bootstrap oficial.
- Isolamento por `organization_id` do principal autenticado.

Como foi validado?

- `pytest -q`: **47 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre ordenação cronológica e exclusão de eventos de outra organização.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Timeline  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Event Driven  
Tests: 47 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/timeline_sdk/__init__.py`
- `packages/timeline_sdk/models.py`
- `packages/timeline_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/timeline.py`
- `apps/runtime/tests/test_timeline.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Timeline
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Event Store persistente, paginação, filtros clínicos e publicação NATS ainda
  serão conectados.

### Próximo módulo

Experience Layer — Dashboard  
Status: READY

## 2026-08-07 12:04:58 -03:00

### Fase F — Dashboard

O Astera Flow define Dashboard como a sexta entrega da Experience Layer. A
visão agora agrega dados dos diretórios existentes sem duplicar ownership e
respeitando organização, workspaces e profissional autenticado.

O que foi implementado?

- `DashboardSnapshot` com pacientes, encounters, encounters ativos e eventos.
- `DashboardService` para agregação tenant-safe.
- Endpoint autenticado `GET /api/v1/dashboard`.
- Integração do Dashboard Service no bootstrap oficial.
- Agregação baseada em Patient Directory, Encounter Directory e Timeline.

Como foi validado?

- `pytest -q`: **48 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre escopo por organização e contagem de encounter ativo/eventos.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Dashboard  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Multi-tenant  
Tests: 48 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/dashboard_sdk/__init__.py`
- `packages/dashboard_sdk/models.py`
- `apps/runtime/src/application/dashboard/__init__.py`
- `apps/runtime/src/application/dashboard/service.py`
- `apps/runtime/src/adapters/http/dashboard.py`
- `apps/runtime/tests/test_dashboard.py`

### Arquivos alterados

- `packages/encounter_sdk/in_memory.py`
- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Dashboard
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Métricas persistentes, paginação, filtros por workspace e observabilidade de
  consultas ainda serão conectados.

### Próximo módulo

Experience Layer — Streaming  
Status: READY

## 2026-08-07 12:06:05 -03:00

### Fase F — Streaming

O Astera Flow define Streaming como a sétima entrega da Experience Layer para
áudio, transcrição, status e representações contínuas. A plataforma agora
possui um broker assíncrono provider-neutral e uma fronteira WebSocket.

O que foi implementado?

- `StreamEvent` com stream id, tipo, sequência, payload e timestamp.
- `InMemoryStreamBroker` com publicação e múltiplos subscribers assíncronos.
- Endpoint WebSocket `/api/v1/streaming/{stream_id}`.
- Integração do broker no bootstrap oficial.
- Teste de ordenação de eventos de transcript delta/completed.

Como foi validado?

- `pytest -q`: **49 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo validado: publisher → subscriber → eventos ordenados.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — Streaming  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Event Driven  
Tests: 49 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/streaming_sdk/__init__.py`
- `packages/streaming_sdk/models.py`
- `packages/streaming_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/streaming.py`
- `apps/runtime/tests/test_streaming.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Streaming
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- NATS-backed broker, autenticação WebSocket, replay, backpressure e
  reconexão ainda serão conectados.

### Próximo módulo

Experience Layer — A2UI  
Status: READY

## 2026-08-07 12:07:20 -03:00

### Fase F — A2UI

O Astera Flow define A2UI como a oitava e última entrega da Experience Layer.
O Runtime agora produz uma árvore declarativa de componentes para o Clinical
Workspace, mantendo o backend independente de React, TypeScript ou Deno.

O que foi implementado?

- `A2UINode` e `A2UIDocument` como contratos declarativos imutáveis.
- `A2UIService` para construir a visão do workspace a partir do Dashboard.
- Componentes `ClinicalWorkspace`, `WorkspaceHeader` e `MetricGrid`.
- Endpoint autenticado `GET /api/v1/a2ui/workspace`.
- Integração do A2UI Service no bootstrap oficial.
- Validação de root node e referências de filhos no documento.

Como foi validado?

- `pytest -q`: **50 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Teste cobre documento declarativo, root, componentes e métricas.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Experience Layer — A2UI  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Renderer Neutral  
Tests: 50 passed  
Coverage: N/A  
Decision: Specified pelo Astera Flow

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[x] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/a2ui_sdk/__init__.py`
- `packages/a2ui_sdk/models.py`
- `apps/runtime/src/application/a2ui/__init__.py`
- `apps/runtime/src/application/a2ui/service.py`
- `apps/runtime/src/adapters/http/a2ui.py`
- `apps/runtime/tests/test_a2ui.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / A2UI
- Status: Atualizada
- Versão: 1.0

### Technical Debt

- Renderer React/TypeScript/Deno, ações interativas e sincronização em tempo
  real ainda serão conectados ao contrato A2UI.

### Próximo módulo

Primeira consulta visual  
Status: READY

## 2026-08-07 12:08:43 -03:00

### Critério da Fase F — Primeira consulta visual

O Astera Flow define como critério da Experience Layer uma primeira consulta
visual. A view declarativa agora compõe o contexto clínico completo em A2UI:

```text
PatientCard
  + EncounterStatus
  + TimelinePanel
  + AudioStream
  + RepresentationPanel
```

O que foi implementado?

- `A2UIService.consultation_view` para composição da consulta.
- Endpoint autenticado `GET /api/v1/a2ui/encounters/{encounter_id}`.
- View declarativa com paciente, encounter, timeline, streaming e formatos de
  representação.
- Validação de vínculo entre principal, encounter, paciente e organização.
- Teste da primeira consulta visual sem acoplamento a renderer.

Como foi validado?

- `pytest -q`: **51 passed**.
- `python -m compileall -q apps packages`: passou.
- `git diff --check`: passou.
- Fluxo visual validado: Login → Workspace → Patient → Encounter → A2UI.

### Cabeçalho da entrada

Status: 🟢 Completed  
Phase: F  
Module: Primeira consulta visual  
Execution Time: 1 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First · Renderer Neutral  
Tests: 51 passed  
Coverage: N/A  
Decision: Critério especificado pelo Astera Flow validado

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[x] Desktop  
[ ] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- Nenhum novo arquivo; composição adicionada aos componentes A2UI existentes.

### Arquivos alterados

- `apps/runtime/src/application/a2ui/service.py`
- `apps/runtime/src/adapters/http/a2ui.py`
- `apps/runtime/src/bootstrap/main.py`
- `apps/runtime/tests/test_a2ui.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Experience Layer / Critério da Fase F
- Status: Atualizada — primeira consulta visual validada
- Versão: 1.0

### Technical Debt

- Renderer real React/TypeScript/Deno, ações do usuário, autenticação
  WebSocket e persistência da view ainda serão conectados.

### Próximo módulo

Enterprise Platform — Observability  
Status: READY

## 2026-08-07 12:14:07 -03:00

### Enterprise Observability

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — Observability  
Execution Time: 6 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven  
Tests: 53 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Implementar o primeiro módulo da Enterprise Platform com um contrato
vendor-neutral para métricas operacionais e eventos estruturados, mantendo o
OpenTelemetry como adapter de exportação e sem expor dados clínicos no
snapshot operacional.

### Por que foi decidido?

O Astera Flow define Observabilidade como o primeiro item da Fase G e exige
que a plataforma tenha telemetria operacional consultável antes do checklist
Enterprise. O contrato separado permite testar e operar o Runtime sem acoplar
o domínio a um fornecedor de observabilidade.

### O que foi implementado?

- Métricas counter e gauge com atributos normalizados e valores atuais.
- Eventos operacionais com severidade, trace id opcional e retenção limitada.
- Snapshot imutável e serializável para ferramentas de operação.
- Endpoint `GET /api/v1/observability` protegido por `observability:read`.
- Registro do evento `runtime.configured` no bootstrap.

### Como foi validado?

- Teste unitário de acumulação, gauge e retenção limitada de eventos.
- Teste do endpoint com autenticação JWT e autorização RBAC.
- `pytest -q`: **53 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/observability_sdk/__init__.py`
- `packages/observability_sdk/models.py`
- `packages/observability_sdk/ports.py`
- `packages/observability_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/observability.py`
- `apps/runtime/tests/test_enterprise_observability.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — Observabilidade concluída; execução segue para Auditoria
- Versão: 1.4

### Technical Debt

- Exportação do snapshot operacional para armazenamento persistente e
  integração do catálogo de métricas com Prometheus/Grafana ainda pendentes.
- A identidade e a retenção definitiva de eventos dependem do módulo Auditoria.

### Próximo módulo

Enterprise Platform — Audit  
Status: READY

## 2026-08-07 12:21:32 -03:00

### Enterprise Audit

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — Audit  
Execution Time: 7 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven  
Tests: 55 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Adicionar uma trilha de auditoria append-only, com identidade do ator,
organização, ação, recurso, resultado e metadados redigidos.

### Por que foi decidido?

Auditoria é o segundo módulo explicitamente ordenado pelo Astera Flow na Fase
G. O escopo por organização evita vazamento entre tenants e a consulta
protegida por RBAC dá aos operadores um contrato HTTP verificável.

### O que foi implementado?

- `AuditEntry` imutável com criação controlada e redaction de segredos.
- `InMemoryAuditLog` append-only com retenção limitada e leitura por tenant.
- Filtro opcional por ação e limite de consulta.
- Endpoint `GET /api/v1/audit` protegido por `audit:read`.
- Evento inicial `runtime.configured` registrado no bootstrap.

### Como foi validado?

- Redaction de password e isolamento por organização.
- Autenticação JWT, RBAC e seleção de tenant no endpoint.
- `pytest -q`: **55 passed**, com 4 warnings de depreciação do Google ADK.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/audit_sdk/__init__.py`
- `packages/audit_sdk/models.py`
- `packages/audit_sdk/ports.py`
- `packages/audit_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/audit.py`
- `apps/runtime/tests/test_audit.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — Auditoria concluída; execução segue para Segurança
- Versão: 1.4

### Technical Debt

- Persistência WORM, assinatura/hash chain, retenção configurável e exportação
  para SIEM ainda serão conectadas na evolução enterprise.

### Próximo módulo

Enterprise Platform — Security  
Status: READY

## 2026-08-07 12:28:41 -03:00

### Enterprise Security

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — Security  
Execution Time: 7 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First  
Tests: 57 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Adicionar uma postura de segurança verificável no bootstrap e headers
defensivos na fronteira HTTP, sem expor valores de segredo no relatório.

### Por que foi decidido?

Segurança é o terceiro item da Fase G. O Runtime já tinha autenticação e RBAC;
este módulo consolida controles mínimos de produção e torna a configuração
auditável por operadores autorizados.

### O que foi implementado?

- Verificação de força e uso do segredo JWT.
- Verificação de debug e documentação interativa em produção.
- `SecurityHeadersMiddleware` com CSP, HSTS condicional, anti-clickjacking,
  MIME sniffing e política de referrer.
- Endpoint `GET /api/v1/security/status` protegido por `security:read`.

### Como foi validado?

- Cenário de produção inseguro detecta três falhas.
- Relatório de segurança acessível apenas com RBAC.
- `pytest -q`: **57 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/security_sdk/__init__.py`
- `packages/security_sdk/models.py`
- `packages/security_sdk/posture.py`
- `packages/security_sdk/headers.py`
- `apps/runtime/src/adapters/http/security.py`
- `apps/runtime/tests/test_security.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — Segurança concluída; execução segue para LGPD
- Versão: 1.4

### Technical Debt

- WAF, rate limiting distribuído, rotação automática de chaves e integração
  com provedor de identidade externo continuam pendentes.

### Próximo módulo

Enterprise Platform — LGPD  
Status: READY

## 2026-08-07 12:36:10 -03:00

### Enterprise LGPD

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — LGPD  
Execution Time: 7 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First  
Tests: 59 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Implementar contratos de consentimento versionado e solicitações de direitos do
titular (acesso, retificação, exclusão e portabilidade), sempre dentro da
organização do principal autenticado.

### Por que foi decidido?

LGPD é o quarto item explícito da Fase G. O Runtime clínico precisa registrar
finalidade e versão de política, além de receber solicitações sem permitir
acesso entre organizações.

### O que foi implementado?

- `ConsentRecord` com finalidade, versão de política e decisão do titular.
- `DataSubjectRequest` com ciclo inicial `received`.
- Serviço em memória com leituras por organização e titular.
- Rotas para registrar consentimento, abrir/listar solicitações e consultar
  consentimentos, protegidas por RBAC.

### Como foi validado?

- Isolamento de consentimentos e solicitações entre organizações.
- Rota de consentimento usa a organização do JWT, não a enviada pelo cliente.
- `pytest -q`: **59 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `packages/privacy_sdk/__init__.py`
- `packages/privacy_sdk/models.py`
- `packages/privacy_sdk/ports.py`
- `packages/privacy_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/privacy.py`
- `apps/runtime/tests/test_privacy.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — LGPD concluída; execução segue para Backup
- Versão: 1.4

### Technical Debt

- Workflow assíncrono de atendimento, validação de identidade do titular,
  anonimização física e integração com armazenamento de consentimento ainda
  serão conectados.

### Próximo módulo

Enterprise Platform — Backup  
Status: READY

## 2026-08-07 12:44:03 -03:00

### Enterprise Backup

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — Backup  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First  
Tests: 61 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Criar um manifesto de backup com tamanho, origem e checksum SHA-256, além de
restauração que verifica integridade antes de devolver o conteúdo.

### Por que foi decidido?

Backup é o quinto item da Fase G. O contrato permite substituir o armazenamento
em memória por object storage sem alterar os consumidores, enquanto o endpoint
expõe somente manifestos para operadores autorizados.

### O que foi implementado?

- `BackupArtifact` imutável.
- `InMemoryBackupStore` com criação, listagem e restauração verificada.
- `BackupIntegrityError` para conteúdo divergente do manifesto.
- Endpoint `GET /api/v1/backups` protegido por `backup:read`.
- Manifesto inicial do Runtime criado no bootstrap.

### Como foi validado?

- Round-trip de payload e verificação de checksum.
- Consulta de manifesto com autenticação e RBAC.
- `pytest -q`: **61 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `packages/backup_sdk/__init__.py`
- `packages/backup_sdk/models.py`
- `packages/backup_sdk/ports.py`
- `packages/backup_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/backups.py`
- `apps/runtime/tests/test_backup.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — Backup concluído; execução segue para Disaster Recovery
- Versão: 1.4

### Technical Debt

- Object storage, criptografia em repouso, agendamento, retenção e backup
  consistente de dados persistidos ainda serão conectados.

### Próximo módulo

Enterprise Platform — Disaster Recovery  
Status: READY

## 2026-08-07 12:52:18 -03:00

### Enterprise Disaster Recovery

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — Disaster Recovery  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Resilience First  
Tests: 63 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Adicionar planos declarativos de recuperação com RTO/RPO, dependências e
registro de drills, permitindo identificar prontidão e atenção necessária.

### Por que foi decidido?

Disaster Recovery é o sexto item da Fase G. O contrato torna explícitos os
objetivos de recuperação antes da integração com infraestrutura externa.

### O que foi implementado?

- `RecoveryPlan` com RTO, RPO e dependências.
- `InMemoryRecoveryCoordinator` para planos e drills.
- Estados `planned`, `verified` e `attention_required`.
- Endpoint `GET /api/v1/disaster-recovery/status` protegido por
  `recovery:read`.
- Plano inicial do Runtime registrado no bootstrap.

### Como foi validado?

- Drill falho marca a plataforma como não pronta; drill aprovado recupera o
  status `verified`.
- Consulta de prontidão com autenticação e RBAC.
- `pytest -q`: **63 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `packages/disaster_recovery_sdk/__init__.py`
- `packages/disaster_recovery_sdk/models.py`
- `packages/disaster_recovery_sdk/ports.py`
- `packages/disaster_recovery_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/disaster_recovery.py`
- `apps/runtime/tests/test_disaster_recovery.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — Disaster Recovery concluído; execução segue para Performance
- Versão: 1.4

### Technical Debt

- Failover automatizado, replicação multi-região, exercícios agendados e
  integração com orquestrador/cloud provider ainda serão conectados.

### Próximo módulo

Enterprise Platform — Performance  
Status: READY

## 2026-08-07 13:01:26 -03:00

### Enterprise Performance

Status: 🟢 Completed  
Phase: G  
Module: Enterprise Platform — Performance  
Execution Time: 9 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · API First  
Tests: 65 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Adicionar monitoramento de latência, taxa de erro e percentis p50/p95 no
Runtime, com labels de operação que não incluem caminhos nem dados clínicos.

### Por que foi decidido?

Performance é o último item de criação da Fase G. A medição no boundary HTTP
produz uma base consistente para o checklist Enterprise sem acoplar o domínio
ao backend de métricas.

### O que foi implementado?

- `InMemoryPerformanceMonitor` com retenção limitada por operação.
- Resumos de amostras, erros, média, p50, p95 e error rate.
- `PerformanceMiddleware` medindo `http.request` com rótulos privacy-safe.
- Endpoint `GET /api/v1/performance/status` protegido por
  `performance:read`.

### Como foi validado?

- Percentis e taxa de erro calculados sobre amostras controladas.
- Consulta de performance com autenticação e RBAC.
- `pytest -q`: **65 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[x] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/performance_sdk/__init__.py`
- `packages/performance_sdk/models.py`
- `packages/performance_sdk/ports.py`
- `packages/performance_sdk/in_memory.py`
- `packages/performance_sdk/middleware.py`
- `apps/runtime/src/adapters/http/performance.py`
- `apps/runtime/tests/test_performance.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Enterprise Platform
- Status: Atualizada — todos os itens técnicos da Fase G concluídos; checklist Enterprise pronto para avaliação do Flow
- Versão: 1.4

### Technical Debt

- Backend de métricas persistente, SLOs por endpoint, tracing distribuído e
  testes de carga ainda serão conectados na evolução de produção.

### Próximo módulo

Production — Kubernetes  
Status: READY

## 2026-08-07 13:09:42 -03:00

### Production Kubernetes

Status: 🟢 Completed  
Phase: H  
Module: Production — Kubernetes  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Cloud Native · Modular Monolith · Resilience First  
Tests: 66 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Preparar o primeiro manifesto Kubernetes do Runtime com rollout gradual,
probes de saúde, identidade mínima e limites de recursos.

### Por que foi decidido?

Kubernetes é o primeiro item da Fase H Production, explicitamente ordenada pelo
Astera Flow após a Enterprise Platform.

### O que foi implementado?

- Namespace e ServiceAccount dedicados.
- Deployment com duas réplicas e `RollingUpdate` (`maxUnavailable: 0`,
  `maxSurge: 1`).
- Readiness `/ready` e liveness `/health`.
- SecretRef para `ASTERA_AUTH_SECRET`, sem segredo no manifesto.
- `runAsNonRoot`, filesystem read-only, capabilities removidas e recursos
  declarados.
- Service interno e PodDisruptionBudget.

### Como foi validado?

- Teste estrutural dos recursos críticos do manifesto.
- `pytest -q`: **66 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/kubernetes/astera-runtime.yaml`
- `apps/runtime/tests/test_kubernetes_manifest.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — Kubernetes concluído; execução segue para Helm
- Versão: 1.4

### Technical Debt

- Image build/publish, Ingress/TLS, NetworkPolicy e external secret provider
  ainda serão conectados nos módulos seguintes.

### Próximo módulo

Production — Helm  
Status: READY

## 2026-08-07 13:17:35 -03:00

### Production Helm

Status: 🟢 Completed  
Phase: H  
Module: Production — Helm  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Cloud Native · Modular Monolith · GitOps Ready  
Tests: 67 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Empacotar o Runtime Kubernetes em um chart Helm parametrizado, sem criar
segredos dentro do chart e preservando a estratégia de rollout seguro.

### Por que foi decidido?

Helm é o segundo item explicitamente ordenado na Fase H Production e fornece
reprodutibilidade entre ambientes sem duplicar manifests manuais.

### O que foi implementado?

- Chart `astera-runtime` v0.1.0.
- Templates para Deployment, ServiceAccount, Service e PodDisruptionBudget.
- Valores parametrizados para imagem, réplicas, probes, recursos e serviço.
- Secret externo via `secretKeyRef`.
- README com comando de instalação/upgrade.

### Como foi validado?

- Teste estrutural de Chart, values e template de Deployment.
- `pytest -q`: **67 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/helm/astera/Chart.yaml`
- `infrastructure/helm/astera/values.yaml`
- `infrastructure/helm/astera/templates/_helpers.tpl`
- `infrastructure/helm/astera/templates/serviceaccount.yaml`
- `infrastructure/helm/astera/templates/deployment.yaml`
- `infrastructure/helm/astera/templates/service.yaml`
- `infrastructure/helm/astera/templates/pdb.yaml`
- `infrastructure/helm/astera/README.md`
- `apps/runtime/tests/test_helm_chart.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — Helm concluído; execução segue para AWS
- Versão: 1.4

### Technical Debt

- Registry real, chart lint/render no CI, Ingress/TLS e external secrets
  provider ainda serão conectados.

### Próximo módulo

Production — AWS  
Status: READY

## 2026-08-07 13:26:44 -03:00

### Production AWS

Status: 🟢 Completed  
Phase: H  
Module: Production — AWS  
Execution Time: 9 min  
Author: Agent Runtime  
Architecture: Cloud Native · Modular Monolith · Private Network First  
Tests: 68 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Criar um blueprint Terraform para EKS com endpoint privado, logs de controle
habilitados e node group gerenciado, recebendo rede e IAM por variáveis.

### Por que foi decidido?

AWS é o terceiro item da Fase H. A separação entre infraestrutura provisionada
e aplicação evita credenciais hardcoded e permite que a conta AWS mantenha seu
próprio estado e governança.

### O que foi implementado?

- Provider AWS versionado e Terraform mínimo `>= 1.6`.
- EKS com endpoint privado e subnets privadas externas.
- Logs `api`, `audit`, `authenticator`, `controllerManager` e `scheduler`.
- Managed node group Runtime com escala 2–6 e update controlado.
- Outputs do cluster e exemplo de variáveis sem credenciais reais.

### Como foi validado?

- Teste estrutural do blueprint, entradas de IAM/rede e ausência de access key.
- `pytest -q`: **68 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/aws/versions.tf`
- `infrastructure/aws/variables.tf`
- `infrastructure/aws/main.tf`
- `infrastructure/aws/outputs.tf`
- `infrastructure/aws/terraform.tfvars.example`
- `infrastructure/aws/README.md`
- `apps/runtime/tests/test_aws_blueprint.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — AWS concluído; execução segue para CI/CD
- Versão: 1.4

### Technical Debt

- VPC, IAM, state backend, KMS, autoscaling avançado e validação com conta AWS
  ainda serão conectados pelo pipeline de infraestrutura.

### Próximo módulo

Production — CI/CD  
Status: READY

## 2026-08-07 13:35:51 -03:00

### Production CI/CD

Status: 🟢 Completed  
Phase: H  
Module: Production — CI/CD  
Execution Time: 9 min  
Author: Agent Runtime  
Architecture: Cloud Native · Modular Monolith · GitHub Actions · GitOps Ready  
Tests: 70 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Criar um pipeline de entrega que bloqueia a construção da imagem e a validação
do chart até que testes, compilação e verificação de diff passem.

### Por que foi decidido?

CI/CD é o quarto item da Fase H. A cadeia de validação precisa ser repetível e
executar a mesma base de qualidade antes de produzir um artefato de Runtime.

### O que foi implementado?

- `Dockerfile` Python 3.12 com usuário não-root e healthcheck.
- `.dockerignore` reduzindo o contexto da imagem.
- Workflow `production.yml` com jobs de validação, build de imagem e Helm lint.
- Build usa cache do GitHub Actions e tag imutável pelo SHA do commit.
- Publicação e deploy permanecem dependentes das credenciais do ambiente.

### Como foi validado?

- Testes estruturais do Dockerfile e workflow.
- `pytest -q`: **70 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `Dockerfile`
- `.dockerignore`
- `.github/workflows/production.yml`
- `apps/runtime/tests/test_delivery_assets.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — CI/CD concluído; execução segue para Rollback
- Versão: 1.4

### Technical Debt

- Registry de imagem, assinatura/SBOM, environment promotion e deploy via OIDC
  ainda serão conectados aos ambientes reais.

### Próximo módulo

Production — Rollback  
Status: READY

## 2026-08-07 13:44:29 -03:00

### Production Rollback

Status: 🟢 Completed  
Phase: H  
Module: Production — Rollback  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Cloud Native · Resilience First · GitOps Ready  
Tests: 72 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Implementar rollback explícito por release e revision Helm, exigindo ambiente,
release e revisão definidos manualmente e aguardando a recuperação dos pods.

### Por que foi decidido?

Rollback é o quinto item da Fase H e precisa ser uma operação deliberada,
auditável e reversível, sem escolher uma revisão automaticamente.

### O que foi implementado?

- Histórico de releases e manager de rollback em `release_sdk`.
- Script `helm rollback --wait --timeout 10m` com variáveis obrigatórias.
- Workflow manual `workflow_dispatch` com ambiente `production`.
- Acesso ao cluster permanece fornecido pelo ambiente de produção.

### Como foi validado?

- Rollback restaura a imagem anterior e registra o estado `rolled_back`.
- Assets operacionais exigem uma revision explícita.
- `pytest -q`: **72 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/release_sdk/__init__.py`
- `packages/release_sdk/models.py`
- `packages/release_sdk/in_memory.py`
- `infrastructure/scripts/rollback.sh`
- `.github/workflows/rollback.yml`
- `apps/runtime/tests/test_rollback.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — Rollback concluído; execução segue para Blue/Green
- Versão: 1.4

### Technical Debt

- Cluster access via OIDC/cloud connector, aprovação de mudança e auditoria do
  operador ainda serão conectados ao ambiente real.

### Próximo módulo

Production — Blue/Green  
Status: READY

## 2026-08-07 13:53:18 -03:00

### Production Blue/Green

Status: 🟢 Completed  
Phase: H  
Module: Production — Blue/Green  
Execution Time: 9 min  
Author: Agent Runtime  
Architecture: Cloud Native · Resilience First · Progressive Delivery  
Tests: 74 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Separar as versões blue e green do Runtime, validar a cor alvo com readiness
antes da promoção e trocar apenas o selector do Service estável.

### Por que foi decidido?

Blue/Green é o sexto e último item listado na Fase H Production. A promoção
manual mantém a versão anterior disponível para rollback imediato.

### O que foi implementado?

- Deployments `astera-runtime-blue` e `astera-runtime-green`.
- Service estável e Service preview com selectors por cor.
- Script de troca que aceita exclusivamente `blue` ou `green`.
- Workflow manual que atualiza a imagem, aguarda rollout e só então promove o
  tráfego.

### Como foi validado?

- Manifesto contém as duas cores e os Services ativo/preview.
- Workflow exige rollout status antes da promoção.
- `pytest -q`: **74 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/kubernetes/blue-green.yaml`
- `infrastructure/scripts/switch-color.sh`
- `.github/workflows/blue-green.yml`
- `apps/runtime/tests/test_blue_green.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — Blue/Green concluído; critério First Deploy especificado como próximo resultado
- Versão: 1.4

### Technical Debt

- Ingress real, análise de tráfego, métricas de promoção e integração do
  cluster access/OIDC ainda serão conectados ao ambiente real.

### Próximo módulo

Production — First Deploy  
Status: READY

## 2026-08-07 14:02:07 -03:00

### Production First Deploy

Status: 🟢 Completed  
Phase: H  
Module: Production — First Deploy  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Cloud Native · GitOps Ready · Progressive Delivery  
Tests: 75 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Preparar o primeiro deploy do Runtime como uma operação explícita, atômica e
aguardada, com tag imutável de imagem e verificação de rollout.

### Por que foi decidido?

Primeiro Deploy é o critério declarado para concluir a Fase H. O pacote de
execução deixa o ambiente de produção responsável por cluster access e
credenciais, sem simular sucesso de uma operação externa não executada aqui.

### O que foi implementado?

- Script `first-deploy.sh` com `helm upgrade --install --atomic --wait`.
- Rollout status e leitura do Service após a instalação.
- Workflow manual com environment `production` e `image_tag` obrigatório.
- Smoke-test operacional reservado ao ingress configurado no ambiente.

### Como foi validado?

- Teste estrutural do runbook e workflow.
- `pytest -q`: **75 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/scripts/first-deploy.sh`
- `.github/workflows/first-deploy.yml`
- `apps/runtime/tests/test_first_deploy.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production
- Status: Atualizada — artefatos do First Deploy concluídos; execução segue para Astera MVP
- Versão: 1.4

### Technical Debt

- Execução contra o cluster AWS real, ingress/TLS e smoke test externo dependem
  do ambiente de produção configurado.

### Próximo módulo

Astera MVP — End-to-End Clinical Flow  
Status: READY

## 2026-08-07 14:15:36 -03:00

### Astera MVP End-to-End Clinical Flow

Status: 🟢 Completed  
Phase: I  
Module: Astera MVP — End-to-End Clinical Flow  
Execution Time: 13 min  
Author: Agent Runtime  
Architecture: Hexagonal · Modular Monolith · Event Driven · Plugin First  
Tests: 76 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Conectar o fluxo clínico obrigatório do Astera Flow em uma operação de Runtime:
autenticação, paciente, encounter, áudio, Speech, Evidence, Knowledge, SOAP e
salvamento.

### Por que foi decidido?

O Astera Flow define a consulta completa funcionando como critério da Fase I.
Todos os componentes necessários já existiam como contratos; o trabalho foi
compor os adapters sem mover regra clínica para a camada HTTP.

### O que foi implementado?

- Rota `POST /api/v1/mvp/consultations` protegida por `consultation:write`.
- Decode de áudio, criação/início/conclusão do Encounter e isolamento por
  organização/workspace.
- Composição Speech → Evidence → Correlation → Understanding → Knowledge →
  Representation.
- Store de consultas salvas e evento `consultation.saved` na Timeline.
- Resposta com transcript, evidence, knowledge e representações SOAP/FHIR/
  summary.

### Como foi validado?

- Teste completo de login, criação de paciente, consulta, áudio, pipeline e
  salvamento.
- Encounter finalizado como `completed` e evento de timeline persistido.
- `pytest -q`: **76 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[x] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `packages/consultation_sdk/__init__.py`
- `packages/consultation_sdk/models.py`
- `packages/consultation_sdk/ports.py`
- `packages/consultation_sdk/in_memory.py`
- `apps/runtime/src/adapters/http/mvp.py`
- `apps/runtime/tests/test_mvp_flow.py`

### Arquivos alterados

- `apps/runtime/src/bootstrap/main.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Astera MVP
- Status: Atualizada — consulta completa funcionando
- Versão: 1.4

### Technical Debt

- Persistência real, Speech provider externo, aprovação clínica, autorização
  fina por ação e ingestão de áudio streaming ainda serão conectados.

### Próximo módulo

Astera MVP — Release Candidate 1.0  
Status: READY

## 2026-08-07 14:23:11 -03:00

### Astera MVP Release Candidate 1.0

Status: 🟢 Completed  
Phase: I  
Module: Astera MVP — Release Candidate 1.0  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Cloud Native · GitOps Ready · Progressive Delivery  
Tests: 77 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Definir o manifesto do Release Candidate 1.0 com imagem imutável, chart,
comandos de validação e estratégias de promoção/rollback.

### Por que foi decidido?

Release Candidate é explicitamente listado pelo Astera Flow na trilha de
Production antes do Astera MVP 1.0. O manifesto mantém a promoção reproduzível
e delega publicação ao registry configurado.

### O que foi implementado?

- Manifesto `astera-runtime-1.0.0-rc.1`.
- Workflow manual de validação e empacotamento Helm.
- Gate de testes, compilação e `git diff --check` antes do package.
- Estratégia Blue/Green e rollback por revisão no metadata do release.

### Como foi validado?

- Teste estrutural do manifesto e workflow.
- `pytest -q`: **77 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/release/astera-runtime-1.0.0-rc.1.yaml`
- `.github/workflows/release-candidate.yml`
- `apps/runtime/tests/test_release_candidate.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Production / Astera MVP
- Status: Atualizada — Release Candidate 1.0 definido; execução segue para MVP 1.0
- Versão: 1.4

### Technical Debt

- Assinatura/proveniência do artefato, publicação no registry, aprovação formal
  e deploy real ainda dependem do ambiente de produção.

### Próximo módulo

Astera MVP — Version 1.0  
Status: READY

## 2026-08-07 14:31:04 -03:00

### Astera MVP 1.0

Status: 🟢 Completed  
Phase: I  
Module: Astera MVP — Version 1.0  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Hexagonal · Cloud Native · Event Driven · Plugin First  
Tests: 78 passed  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Consolidar o Astera Runtime 1.0 com o fluxo clínico obrigatório validado e
artefatos de promoção estável.

### Por que foi decidido?

Astera MVP 1.0 é o último sprint explicitamente listado pelo Astera Flow na
trilha de Production. O manifesto conecta o Release Candidate ao canal stable
sem reimplementar o fluxo clínico.

### O que foi implementado?

- Manifesto estável `astera-runtime-1.0.0`.
- Workflow de promoção do MVP 1.0 usando o runbook de First Deploy.
- Registro explícito das oito etapas: Login, Patient, Encounter, Speech,
  Evidence, Knowledge, SOAP e Save.
- Verificação estrutural de que a promoção usa imagem `1.0.0`.

### Como foi validado?

- Teste do manifesto estável e workflow de promoção.
- Fluxo clínico ponta a ponta já validado pelo teste de integração do MVP.
- `pytest -q`: **78 passed**, com 4 warnings de depreciação do Google ADK.
- `python3 -m compileall -q apps packages`: passou.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[x] API  
[ ] Desktop  
[x] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `infrastructure/release/astera-runtime-1.0.0.yaml`
- `.github/workflows/mvp-1.0.yml`
- `apps/runtime/tests/test_mvp_release.py`

### Arquivos alterados

- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- Nenhuma nova decisão arquitetural criada.

### Astera Flow

- Aba: Astera MVP 1.0
- Status: Atualizada — fluxo clínico completo e release estável definidos
- Versão: 1.4

### Technical Debt

- Promoção contra o cluster real, registry/proveniência, Speech externo,
  persistência clínica e observabilidade distribuída seguem como evolução
  operacional após o MVP.

### 2026-08-07 12:40:04 -03:00 — Correção de integração pós-validação

- Corrigida a exportação pública de `PerformanceMiddleware`, necessária para o
  bootstrap importar o app completo. O smoke import passou após a correção.

### Próximo módulo

Conforme próxima definição do Astera Flow  
Status: READY

## 2026-08-07 16:47:52 -03:00

### Technology Selection Policy v2 — Foundation Model Boundary

Status: 🟢 Completed  
Phase: Era 4 — Provider Research & Integration  
Module: Technology Selection Policy v2 / Google ADK Foundation Models  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Hexagonal · Provider-Oriented · ADR-010 preservada  
Tests: 109 passed, 4 warnings  
Coverage: N/A  
Decision: Approved — v2 aplicada

### O que foi decidido?

A `Technology Selection Policy v2`, aprovada pelo Astera Flow, substitui a
Development Provider Policy v1. A política separa formalmente Capability
Providers do Astera e Foundation Models executados pelo Google ADK.

### Por que foi decidido?

Capability Providers implementam capacidades através de contratos. Foundation
Models executam agentes através do ADK. Misturar as duas categorias criaria
acoplamento de vendor no domínio, nas Capabilities ou no Kernel.

### O que foi implementado?

- Política v2 formalizada em
  `docs/astera-flow/technology-selection-policy-v2.md`.
- Política v1 marcada como `SUPERSEDED`.
- `FoundationModel` protocol criado como boundary interno do runtime.
- `GeminiAdapter` e `LiteLlmAdapter` criados para construir modelos aceitos
  pelo Google ADK.
- `AdkRuntime.from_definition` passou a resolver o modelo através do adapter;
  `model_name` permanece apenas como compatibilidade e é encapsulado no
  `GeminiAdapter`.
- Dashboard, Providers README e Astera Flow README atualizados.

### Como foi validado?

- Testes direcionados de ADK: **2 passed, 4 warnings**.
- Suíte completa: **109 passed, 4 warnings**.
- `git diff --check` passou.
- O teste de adapter confirma que o ADK recebe o modelo produzido pela boundary,
  sem exigir modelo específico no Kernel.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts públicos  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/technology-selection-policy-v2.md`
- `apps/runtime/src/application/agents/foundation_model.py`
- `apps/runtime/tests/test_adk_runtime.py` — cenário de adapter adicionado

### Arquivos alterados

- `docs/astera-flow/development-provider-policy.md`
- `docs/astera-flow/README.md`
- `docs/astera-flow/providers/README.md`
- `docs/astera-flow/executive-dashboard.md`
- `apps/runtime/src/application/agents/__init__.py`
- `apps/runtime/src/application/agents/adk_runtime.py`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- Technology Selection Policy v2 — Status APPROVED
- Google ADK `BaseLlm` boundary
- Nenhuma nova ADR ou RFC.

### Astera Flow

- Aba: Core Platform / Google ADK / Technology Selection
- Status: Atualizada — Capability Providers e Foundation Models separados
- Versão: 2.0 — Policy Applied

### Technical Debt

Nenhuma dívida arquitetural criada. Adapters adicionais para Ollama, vLLM,
Grok, OpenAI ou Claude só serão implementados quando houver uso aprovado; a
boundary já permite substituição sem alterar o Kernel.

### Próximo módulo

Technology Selection Compliance Review  
Status: READY

## 2026-08-07 16:52:31 -03:00

### Tool Adapter & Capability Catalog

Status: 🟢 Completed  
Phase: Era 4 — Provider Research & Integration  
Module: Tool Boundary / Capability Catalog / Foundation Benchmark Governance  
Execution Time: 5 min  
Author: Agent Runtime  
Architecture: Hexagonal · ADK Boundary · Architecture Freeze preservado  
Tests: 111 passed, 4 warnings  
Coverage: N/A  
Decision: Approved — última extensão arquitetural registrada

### O que foi decidido?

Adicionar o terceiro boundary `ToolAdapter`, mantendo o Google ADK independente
de REST, MCP, Local, Workflow, CLI e FHIR tools. Adicionar o `CapabilityCatalog`
como visão de descoberta provider-neutral para ADK e orquestração.

Foundation Model Benchmark e Foundation Model Certification passam a ser
artefatos separados dos benchmarks e certificações de Capability Providers.

### Por que foi decidido?

O ADK deve consumir Tools e Capabilities sem conhecer suas implementações. A
separação permite trocar a origem de uma Tool e comparar Foundation Models sem
alterar o Kernel, o domínio ou os contratos das Capabilities.

### O que foi implementado?

- `ToolAdapter` protocol e `PythonToolAdapter` para Tools locais.
- `AdkRuntime` converte Tool Adapters em Tools compatíveis com ADK.
- `CapabilityCatalog` read-only sobre o registro existente, sem segunda fonte
  de verdade.
- `AsteraKernel.capability_catalog` para descoberta provider-neutral.
- Documentação de Capability Catalog.
- Foundation Model Benchmark e Foundation Model Certification.

### Como foi validado?

- Testes direcionados de ADK e Catalog: **4 passed, 4 warnings**.
- Suíte completa: **111 passed, 4 warnings**.
- `git diff --check` passou.
- Nenhum provider específico foi exposto ao ADK como API de domínio.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel — somente superfície read-only de catalog discovery  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts públicos  
[ ] Observability

### Arquivos criados

- `apps/runtime/src/application/agents/tool_adapter.py`
- `apps/runtime/src/application/capabilities/catalog.py`
- `apps/runtime/tests/test_capability_catalog.py`
- `docs/astera-flow/capability-catalog.md`
- `docs/astera-flow/benchmarks/foundation-model-benchmark.md`
- `docs/astera-flow/benchmarks/foundation-model-certification.md`

### Arquivos alterados

- `apps/runtime/src/application/agents/__init__.py`
- `apps/runtime/src/application/agents/adk_runtime.py`
- `apps/runtime/src/application/capabilities/__init__.py`
- `apps/runtime/src/application/kernel/kernel.py`
- `apps/runtime/tests/test_adk_runtime.py`
- `docs/astera-flow/README.md`
- `docs/astera-flow/benchmarks/README.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- Technology Selection Policy v2 — Status APPROVED
- FoundationModel boundary
- ProviderAdapter boundary
- ToolAdapter boundary

### Astera Flow

- Aba: Cognitive Platform / Tools / Capability Catalog / Foundation Benchmarks
- Status: Atualizada — última extensão arquitetural aprovada implementada
- Versão: 2.0 — Architecture Extension Complete

### Technical Debt

Nenhuma dívida criada. Adapters específicos de FHIR, MCP, REST e outros serão
implementados apenas quando houver uma Capability de produto que os exija.

### Próximo módulo

Provider Integration & Product Capability Delivery  
Status: READY — arquitetura congelada; foco em evidências e produto

## 2026-08-07 16:58:36 -03:00

### ADR-011 — Platform Complete & Product Backlog

Status: 🟢 Completed  
Phase: Product Engineering  
Module: Platform Completion / Product Backlog  
Execution Time: 6 min  
Author: Agent Runtime  
Architecture: Complete · ADR-011 · Architecture Freeze definitivo  
Tests: Documentação validada · suíte anterior preservada em 111 passed  
Coverage: N/A  
Decision: Approved — Agents passam a Product Engineers

### O que foi decidido?

A arquitetura do Astera é considerada completa. `ADR-011 — Platform Complete`
proíbe novas abstrações arquiteturais, salvo evidência concreta de integração
real, limitação do Google ADK ou falha estrutural demonstrada pelo Cognitive
Validation Lab.

O backlog ativo passa a ser exclusivamente o Product Backlog.

### Por que foi decidido?

O valor restante está na entrega de Capabilities utilizáveis, Providers reais,
benchmarks, validações e Clinical Workflow Certification. Continuar criando
arquitetura sem uma limitação comprovada aumentaria o processo sem aumentar o
produto.

### O que foi implementado?

- ADR-011 criada e adicionada ao índice de ADRs.
- Product Backlog criado com sete sprints orientadas a produto:
  faster-whisper, PaddleOCR, Snowstorm, HAPI FHIR, Qdrant, Golden Dataset e
  Clinical Workflow Certification.
- `agent-execution-plan.md` atualizado para o papel Product Engineer.
- Construction vinculada ao Product Backlog após sua conclusão.
- Kernel Evolution Backlog marcado como histórico e encerrado.
- Regra operacional: toda tarefa deve resultar em Capability, Provider,
  evidência ou certificação para o usuário final.

### Como foi validado?

- ADR-011 vinculada no README de ADRs.
- Product Backlog vinculado no Astera Flow.
- Nenhum contrato, SDK, Kernel ou Capability foi alterado.
- Estados dos sprints refletem evidência real; nenhum provider foi declarado
  concluído sem execução.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

- `docs/adrs/ADR-011-platform-complete.md`
- `docs/astera-flow/product-backlog.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/astera-flow/README.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/construction/README.md`
- `docs/astera-flow/kernel-evolution-backlog.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-010` — Architecture Freeze
- `ADR-011` — Platform Complete
- Technology Selection Policy v2

### Astera Flow

- Aba: Product Engineering / Product Backlog
- Status: Atualizada — arquitetura encerrada e backlog de produto ativo
- Versão: 2.0 — Product Mode

### Technical Debt

Nenhuma dívida arquitetural criada. O restante é execução de produto e
evidência operacional.

### Próximo módulo

Sprint 1 — faster-whisper CPU Smoke Run  
Status: READY

## 2026-08-07 17:00:50 -03:00

### Product Engineering Dashboard Alignment

Status: 🟢 Completed  
Phase: Product Engineering  
Module: Executive Dashboard / Construction Governance  
Execution Time: 2 min  
Author: Agent Runtime  
Architecture: ADR-011 — Platform Complete  
Tests: 2 targeted tests passed via `unittest`; full pytest unavailable in shell  
Coverage: N/A  
Decision: Approved — Product Backlog is the active delivery surface

### O que foi decidido?

O dashboard executivo passa a comunicar explicitamente que a plataforma está
completa e que o trabalho ativo é Product Engineering. A Construction mantém seu
papel histórico e aponta a execução atual para o Product Backlog.

### Por que foi decidido?

Para impedir que o estado de arquitetura encerrada seja confundido com o estado
de produto. O indicador oficial agora é a entrega de Capabilities, Providers,
evidências e certificações.

### O que foi implementado?

- Dashboard atualizado com `Platform Complete · ADR-011`.
- Seção `Operating Model` adicionada ao dashboard executivo.
- Versão arquitetural da Construction alinhada à ADR-011.
- Referência da ADR-011 adicionada à documentação da Construction.

### Como foi validado?

- `git diff --check` passou.
- Referências a ADR-011, Product Backlog e Product Engineering conferidas com
  busca no Astera Flow.
- Testes focados do adapter faster-whisper: `2` passaram via `unittest`.
- A suíte completa permanece registrada como `111 passed` na última execução
  disponível; o executável `pytest` não está instalado neste shell atual.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

Nenhum.

### Arquivos alterados

- `docs/astera-flow/executive-dashboard.md`
- `docs/astera-flow/construction/README.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-011` — Platform Complete
- Product Backlog

### Astera Flow

- Aba: Product Engineering / Executive Dashboard
- Status: Atualizada — arquitetura encerrada e foco em produto
- Versão: 2.0 — Product Mode

### Technical Debt

Nenhuma dívida arquitetural criada. A disponibilidade do executável `pytest`
fica registrada como condição do ambiente de validação, não como mudança de
arquitetura.

### Próximo módulo

Sprint 1 — faster-whisper CPU Smoke Run  
Status: READY — executar somente com runtime/modelo local disponível e registrar
evidência real, sem declarar sucesso por testes injetados.

## 2026-08-07 17:04:07 -03:00

### Sprint 1 — faster-whisper Runtime Smoke Evidence

Status: 🟡 Evidence Collected · Product validation pending  
Phase: Product Engineering  
Module: Speech / faster-whisper Development Provider  
Execution Time: 8 min  
Author: Agent Runtime  
Architecture: Provider boundary preserved · ADR-011  
Tests: Runtime smoke executed; targeted adapter tests remain 2 passed  
Coverage: N/A  
Decision: Continue — transcript de áudio falado ainda necessário

### O que foi decidido?

O `faster-whisper` foi executado em um ambiente temporário fora do repositório,
com modelo `tiny`, CPU/int8 e o adapter real. O resultado não promove a
Capability: o áudio usado foi silêncio sintético e não produziu segmentos.

### Por que foi decidido?

Para distinguir claramente disponibilidade do runtime de qualidade de
transcrição. Uma execução sem erro de infraestrutura não é evidência de uma
consulta clínica processada.

### O que foi implementado?

- Dependência `faster-whisper` instalada apenas no ambiente temporário de smoke.
- Modelo `tiny` carregado pelo `FasterWhisperTranscriber` real.
- Entrada WAV de silêncio processada pelo caminho assíncrono do adapter.
- Readiness e Product Backlog atualizados sem alterar contratos ou status de
  certificação.

### Como foi validado?

- `faster-whisper` 1.2.1 carregou e executou em CPU/int8.
- O adapter retornou `TRANSCRIPTION_FAILED` por ausência de fala, comportamento
  esperado para o input usado.
- Tempo total observado: 7,38 s, incluindo carga do modelo.
- Não houve áudio clínico autorizado, transcript falado, benchmark ou CQA.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[ ] Contracts  
[ ] Observability

### Arquivos criados

Nenhum no repositório. O ambiente e o modelo foram mantidos fora do workspace.

### Arquivos alterados

- `docs/astera-flow/capabilities/speech-provider-readiness.md`
- `docs/astera-flow/product-backlog.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-011` — Platform Complete
- Speech Provider Readiness Checklist
- Product Backlog — Sprint 1

### Astera Flow

- Aba: Product Engineering / Capabilities / Speech
- Status: Atualizada — runtime disponível; validação de áudio falado pendente
- Versão: 2.0 — Product Mode

### Technical Debt

Nenhuma dívida arquitetural. Continua pendente a disponibilidade de áudio falado
local/autorizado para completar o smoke de transcript.

### Próximo módulo

Sprint 1 — faster-whisper Speech Sample Smoke  
Status: READY — usar áudio falado autorizado e registrar transcript, idioma,
latência e consumo antes de avançar para PaddleOCR.

## 2026-08-07 14:42:33 -03:00

### Construction ativada — ADR-010, Clinical Facts e Context Builder

Status

🟢 Completed — ADR-010 registrada; Sprints 1, 2 e 3 entregues/validados

Phase

Construction

Module

Architecture Freeze · Speech Plugin · Clinical Facts Plugin · Context Builder

Execution Time

Sessão contínua de implementação

Author

Agent Runtime — Builders

Architecture

Hexagonal · Modular Monolith · Plugin First · Architecture Freeze v1.0

Tests

83 passed · 4 warnings

Coverage

N/A — cobertura quantitativa não configurada no repositório

Decision

Approved pelo Astera Flow; continuar automaticamente na Construction

### O que foi decidido?

- A arquitetura v1.0 está congelada pela `ADR-010 — Architecture Freeze`.
- O Astera entrou na fase Construction com sete sprints oficiais.
- O Speech Plugin existente foi reconhecido como Sprint 1 concluído; não houve
  duplicação de código.
- Clinical Facts e Clinical Context foram implementados como boundaries
  provider-neutral, sem introduzir reasoning, knowledge ou documentação.

### Por que foi decidido?

Os pilares de arquitetura, Cognitive Model e Validation Lab já estão definidos.
O próximo risco era continuar expandindo especificação em vez de executar os
contratos existentes. O freeze preserva o Kernel e desloca a evolução para os
plugins, com `pytest` validando software e o Cognitive Validation Lab validando
o modelo cognitivo.

### O que foi implementado?

- `ADR-010` e a fase `Construction` foram adicionadas ao Astera Flow.
- Sprint 1 foi documentado como entregue com o Speech SDK/Plugin já existente.
- Sprint 2 criou `clinical_facts_sdk` e `ClinicalFactsPlugin`.
- Clinical Facts preservam `subject`, `patient`, `encounter`, provenance,
  confidence, certainty, polarity e status.
- Sprint 3 criou `clinical_context_sdk` e `ClinicalContextPlugin`.
- Context Builder mantém `context_id`, incrementa `context_version`, preserva
  facts anteriores e acrescenta timeline.
- Negação, incerteza e encounter divergente são tratados explicitamente.

### Como foi validado?

- Testes direcionados de Clinical Facts e Clinical Context: **5 passed**.
- Suíte completa: **83 passed**, com 4 warnings de depreciação já existentes.
- `git diff --check`: passou.
- Lifecycle, capability registry, provider health e resolver foram exercitados
  nos testes dos novos plugins.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel — somente registro de capabilities, sem mudança de regra  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[ ] Event Bus — emissão permanece responsabilidade do Runtime  
[x] Contracts  
[x] Observability — lifecycle/health preservados

### Arquivos criados

- `docs/adrs/ADR-010-architecture-freeze.md`
- `docs/astera-flow/construction/README.md`
- `docs/astera-flow/construction/sprint-01-speech-plugin.md`
- `docs/astera-flow/construction/sprint-02-clinical-facts.md`
- `docs/astera-flow/construction/sprint-03-context-builder.md`
- `packages/clinical_facts_sdk/models.py`
- `packages/clinical_facts_sdk/protocol.py`
- `packages/clinical_facts_sdk/in_memory.py`
- `packages/clinical_facts_sdk/__init__.py`
- `packages/clinical_context_sdk/models.py`
- `packages/clinical_context_sdk/protocol.py`
- `packages/clinical_context_sdk/in_memory.py`
- `packages/clinical_context_sdk/__init__.py`
- `apps/runtime/src/application/plugins/clinical_facts/__init__.py`
- `apps/runtime/src/application/plugins/clinical_facts/plugin.py`
- `apps/runtime/src/application/plugins/clinical_context/__init__.py`
- `apps/runtime/src/application/plugins/clinical_context/plugin.py`
- `apps/runtime/tests/test_clinical_facts_plugin.py`
- `apps/runtime/tests/test_clinical_context_plugin.py`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `docs/adrs/README.md`
- `docs/astera-flow/README.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/construction/README.md`
- `docs/astera-flow/construction/sprint-02-clinical-facts.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-004` — Clinical Fact como unidade atômica
- `ADR-005` — Clinical Context como molécula cognitiva
- `ADR-009` — Cognitive Architecture como especificação normativa
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: `Construction`
- Status: Atualizada — Sprints 1 e 2 concluídos; Sprint 3 concluído nesta
  execução
- Versão: `1.0`

### Technical Debt

- Nenhuma dívida arquitetural criada.
- Em aberto para sprints posteriores: emissão persistente no Event Bus e
  adapters de armazenamento, conforme contratos de infraestrutura existentes.

### Próximo módulo

Reasoning Plugin  
Status: PLANNED — seguir a ordem oficial da Construction quando o Astera Flow
marcar o módulo como próximo.

## 2026-08-07 14:50:10 -03:00

### Construction concluída — Sprints 4 a 7

Status

🟢 Completed — todos os sete sprints da Construction implementados

Phase

Construction

Module

Reasoning Plugin · Knowledge Plugin · Documentation Plugin · End-to-End Consultation

Execution Time

Continuidade automática na mesma sessão de desenvolvimento

Author

Agent Runtime — Builders

Architecture

Hexagonal · Modular Monolith · Event Driven · Plugin First · Freeze v1.0

Tests

87 passed · 4 warnings

Coverage

N/A — cobertura quantitativa não configurada no repositório

Decision

Approved pelo Astera Flow; Construction encerrada e modelo pronto para CQA

### O que foi decidido?

- Reasoning Plugin é o único responsável por hipóteses, Information Gaps e
  perguntas rastreáveis.
- Knowledge Plugin mantém consolidação e também atende queries ligadas a
  hipótese/gap com fontes versionadas.
- Documentation Plugin produz projeções não canônicas com provenance do
  Clinical Context.
- A consulta end-to-end passa por todos os boundaries antes da documentação.
- Nenhum novo conceito cognitivo, domínio ou ADR foi criado após a ADR-010.

### Por que foi decidido?

O Astera Flow já definia a ordem dos sete sprints. A implementação precisava
provar a arquitetura congelada em software integrado, mantendo separados os
dois pipelines: `pytest` para software e Cognitive Validation Lab para o modelo
de raciocínio.

### O que foi implementado?

- Sprint 4: `reasoning_sdk` e `ReasoningPlugin`, com hipóteses concorrentes,
  gaps e perguntas.
- Sprint 5: Knowledge Query com `hypothesis_id`, `gap_id`, query type,
  população, jurisdição, data e evidência versionada.
- Sprint 6: provenance de `context_id` e `context_version` nas projeções SOAP,
  FHIR e Summary.
- Sprint 7: `CognitiveConsultationPipeline` compondo Speech, NLP, Clinical
  Facts, Context, Reasoning, Knowledge e Documentation.

### Como foi validado?

- Testes direcionados dos Sprints 4–7 passaram.
- Suíte completa: **87 passed**, com 4 warnings de depreciação já existentes.
- Cenário end-to-end confirmou que Transcript não vira SOAP diretamente.
- `git diff --check`: passou.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[ ] Kernel — somente capabilities já previstas; regras preservadas  
[ ] API  
[ ] Desktop  
[x] Plugin System  
[x] Event Bus — integração permanece desacoplada e Runtime-owned  
[x] Contracts  
[x] Observability — lifecycle/health preservados

### Arquivos criados

- `packages/reasoning_sdk/`
- `apps/runtime/src/application/plugins/reasoning/`
- `apps/runtime/tests/test_reasoning_plugin.py`
- `apps/runtime/src/application/clinical/cognitive_consultation.py`
- `apps/runtime/tests/test_cognitive_consultation_pipeline.py`
- `docs/astera-flow/construction/sprint-04-reasoning-plugin.md`
- `docs/astera-flow/construction/sprint-05-knowledge-plugin.md`
- `docs/astera-flow/construction/sprint-06-documentation-plugin.md`
- `docs/astera-flow/construction/sprint-07-end-to-end-consultation.md`

### Arquivos alterados

- `apps/runtime/src/domain/value_objects/capability_type.py`
- `apps/runtime/src/application/plugins/knowledge/plugin.py`
- `apps/runtime/src/application/plugins/representation/plugin.py`
- `apps/runtime/src/application/clinical/__init__.py`
- `apps/runtime/tests/test_knowledge_plugin.py`
- `apps/runtime/tests/test_representation_plugin.py`
- `packages/medical_knowledge_sdk/models.py`
- `packages/representation_sdk/models.py`
- `packages/representation_sdk/in_memory.py`
- `packages/clinical_pipeline_sdk/models.py`
- `packages/clinical_pipeline_sdk/__init__.py`
- `docs/astera-flow/construction/README.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-004` — Clinical Fact
- `ADR-005` — Clinical Context
- `ADR-006` — Clinical Reasoning Loop
- `ADR-007` — Medical Knowledge Layer
- `ADR-008` — Specialists e Context Enrichment
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: `Construction`
- Status: Atualizada — sete sprints concluídos
- Versão: `1.0`

### Technical Debt

Nenhuma dívida arquitetural criada. Persistência externa, replay/event schema
registry e adapters de produção permanecem extensões operacionais dos contratos
existentes.

### Próximo módulo

Cognitive Validation Lab — Regression Suite  
Status: READY — validar o pipeline construído sem alterar a arquitetura.

## 2026-08-07 14:54:42 -03:00

### Sincronização do baseline cognitivo com o Astera Flow

Status

🟢 Completed

Phase

Architecture Governance → Construction

Module

Cognitive Architecture status synchronization

Execution Time

6 min

Author

Agent Runtime

Architecture

Astera Flow Design Authority · Architecture Freeze v1.0

Tests

87 passed (baseline de código preservado)

Coverage

N/A

Decision

Approved — documentação sincronizada com a decisão do Astera Flow

### O que foi decidido?

RFC-001, documentos normativos 01–09, ADRs 003–009 e reviews concluídos deixam
de apresentar a arquitetura aprovada como `Proposed`. O status canônico passa a
ser `Approved`/`Completed`, mantendo `Proposed` apenas para estados de entidades
ou evoluções ainda não promovidas.

### Por que foi decidido?

Manter o status antigo criava um bloqueio artificial e contradizia a regra de
que o Astera Flow controla exclusivamente a aprovação. A Construction já está
implementada sob a ADR-010; a documentação precisava refletir esse fato.

### O que foi implementado?

- RFC-001 e documentos Clinical Facts, Context, Reasoning, Knowledge,
  Specialists, Contracts, Events e Validation marcados como `Approved`.
- Architecture Review e Clinical Simulation marcados como `Completed`.
- ADRs 003–009 sincronizadas com a decisão do Astera Flow.
- README da Cognitive Architecture atualizado para declarar o baseline v1.0.

### Como foi validado?

- Busca de status antigos nos documentos canônicos: nenhum `Status Proposed`
  remanescente.
- `git diff --check`: passou.
- Suíte de software preservada em **87 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts — apenas sincronização documental  
[ ] Observability

### Arquivos criados

- Nenhum.

### Arquivos alterados

- `docs/astera-flow/cognitive-architecture/README.md`
- `docs/astera-flow/cognitive-architecture/RFC-001-astera-cognitive-architecture.md`
- `docs/astera-flow/cognitive-architecture/01-clinical-facts.md`
- `docs/astera-flow/cognitive-architecture/02-clinical-context.md`
- `docs/astera-flow/cognitive-architecture/03-clinical-reasoning-loop.md`
- `docs/astera-flow/cognitive-architecture/04-medical-knowledge-layer.md`
- `docs/astera-flow/cognitive-architecture/05-specialists-architecture.md`
- `docs/astera-flow/cognitive-architecture/06-cognitive-contracts.md`
- `docs/astera-flow/cognitive-architecture/07-cognitive-events.md`
- `docs/astera-flow/cognitive-architecture/08-validation-scenarios.md`
- `docs/astera-flow/cognitive-architecture/09-adrs.md`
- `docs/astera-flow/cognitive-architecture/10-architecture-review.md`
- `docs/astera-flow/cognitive-architecture/11-clinical-simulation.md`
- `docs/adrs/ADR-003-cognitive-architecture-workshops.md`
- `docs/adrs/ADR-004-clinical-fact-as-atomic-unit.md`
- `docs/adrs/ADR-005-clinical-context-as-cognitive-molecule.md`
- `docs/adrs/ADR-006-clinical-reasoning-loop.md`
- `docs/adrs/ADR-007-medical-knowledge-layer.md`
- `docs/adrs/ADR-008-agent-context-and-clinical-representation.md`
- `docs/adrs/ADR-009-cognitive-architecture-specification.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-009` — Cognitive Architecture como especificação normativa
- `ADR-010` — Architecture Freeze

### Astera Flow

- Aba: `Cognitive Architecture` / `Construction`
- Status: Atualizada — baseline v1.0 aprovado
- Versão: `1.0`

### Technical Debt

Nenhuma dívida criada. Questões abertas de implementação permanecem dentro dos
contratos aprovados e não bloqueiam a Construction.

### Próximo módulo

Cognitive Validation Lab — Regression Suite  
Status: READY

## 2026-08-07 13:59:10 -03:00

### RFC-001 — Astera Cognitive Architecture

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Cognitive Architecture Specification  
Execution Time: 18 min  
Author: Agent Runtime  
Architecture: Design Authority · RFC · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando revisão e decisão do Astera Flow

### O que foi decidido?

Transformar os cinco workshops em uma especificação formal RFC, organizada no
domínio `Cognitive Architecture`, com contratos, eventos, cenários de validação
e ADRs rastreáveis.

### Por que foi decidido?

Conceitos cognitivos não devem saltar diretamente de workshop para código. A
especificação precisa ser revisada por arquitetura, domínio, clínica e
engenharia antes de qualquer implementação.

### O que foi implementado?

- Criado o domínio `docs/astera-flow/cognitive-architecture/`.
- Criada a RFC-001 normativa.
- Criadas as especificações 01–09.
- Criado o Workshop 6 de validação ponta a ponta.
- Definidos Cognitive Architect, Domain Reviewer, Clinical Reviewer,
  Engineering Reviewer e Executor.
- Definidos Cognitive Contracts e Cognitive Events.
- Criada ADR-009 para governança da especificação.
- Astera Flow e ADR-003 vinculados à RFC e ao novo domínio.

### Como foi validado?

- Cada documento contém objetivo, definições, responsabilidades, contratos,
  eventos, diagramas, exemplos, regras, restrições, validação e questões
  abertas.
- O cenário ponta a ponta cobre Context v1 até Context v9 e assinatura clínica.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `docs/astera-flow/cognitive-architecture/README.md`
- `docs/astera-flow/cognitive-architecture/RFC-001-astera-cognitive-architecture.md`
- `docs/astera-flow/cognitive-architecture/01-clinical-facts.md`
- `docs/astera-flow/cognitive-architecture/02-clinical-context.md`
- `docs/astera-flow/cognitive-architecture/03-clinical-reasoning-loop.md`
- `docs/astera-flow/cognitive-architecture/04-medical-knowledge-layer.md`
- `docs/astera-flow/cognitive-architecture/05-specialists-architecture.md`
- `docs/astera-flow/cognitive-architecture/06-cognitive-contracts.md`
- `docs/astera-flow/cognitive-architecture/07-cognitive-events.md`
- `docs/astera-flow/cognitive-architecture/08-validation-scenarios.md`
- `docs/astera-flow/cognitive-architecture/09-adrs.md`
- `docs/adrs/ADR-009-cognitive-architecture-specification.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/adrs/ADR-003-cognitive-architecture-workshops.md`
- `docs/astera-flow/README.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-003` — Workshops de Cognitive Architecture
- `ADR-004` a `ADR-008` — Decisões cognitivas propostas
- `ADR-009` — Cognitive Architecture como especificação normativa

### Astera Flow

- Aba: Cognitive Architecture
- Status: Atualizada — RFC-001 e documentos 01–09 registrados
- Versão: 1.4

### Technical Debt

- Reviews formais, decisão do Flow, schemas físicos, broker e implementação
  permanecem etapas posteriores da governança.

### Próximo módulo

Architecture Review  
Status: READY

## 2026-08-07 14:06:18 -03:00

### Architecture Review — Cognitive Architecture

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Architecture Review + Clinical Simulation  
Execution Time: 22 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Design Authority · Validation  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Conditionally Consistent — Clinical Review READY

### O que foi decidido?

Executar sete revisões conceituais: Consistency, Cognitive Flow, Boundaries,
Responsibilities, Data Flow, Events e Lifecycles, seguidas de uma simulação
clínica ponta a ponta sem código, IA ou ADK.

### Por que foi decidido?

A RFC precisava ser testada contra duplicação, lacunas de fluxo, owners
ambíguos, ciclos, eventos, estados e situações difíceis antes da Fase D.

### O que foi implementado?

- Relatório formal de Architecture Review.
- Matriz de boundaries e responsabilidade única.
- Catálogo de lifecycles revisado.
- Eventos cognitivos normalizados no documento 07.
- Recommendation Contract adicionado ao documento 06.
- Simulação clínica minuto a minuto, incluindo mudança de assunto,
  contradição, nova versão de diretriz e discordância médica.

### Como foi validado?

- Nenhuma contradição estrutural encontrada.
- Divergências de nomes de eventos corrigidas.
- Cenário cobre Context v1 até Context v9 e assinatura clínica.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `docs/astera-flow/cognitive-architecture/10-architecture-review.md`
- `docs/astera-flow/cognitive-architecture/11-clinical-simulation.md`

### Arquivos alterados

- `docs/astera-flow/cognitive-architecture/README.md`
- `docs/astera-flow/cognitive-architecture/06-cognitive-contracts.md`
- `docs/astera-flow/cognitive-architecture/07-cognitive-events.md`
- `docs/astera-flow/cognitive-architecture/02-clinical-context.md`
- `docs/astera-flow/cognitive-architecture/05-specialists-architecture.md`
- `docs/astera-flow/cognitive-architecture/RFC-001-astera-cognitive-architecture.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `RFC-001` — Astera Cognitive Architecture
- `ADR-009` — Cognitive Architecture como especificação normativa

### Astera Flow

- Aba: Cognitive Architecture / Architecture Review
- Status: Atualizada — veredicto `Conditionally Consistent`
- Versão: 1.4

### Technical Debt

- Política clínica de aceitação de Facts, confirmação de Hypotheses e aceitação
  de Recommendations aguardam Reality Review e Medical Validation.

### Próximo módulo

Reality Review  
Status: READY

## 2026-08-07 14:19:31 -03:00

### Reality Review — Real Consultation Validation

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Reality Review + Reality Case Registry  
Execution Time: 14 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Evidence Validation · Design Authority  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — Medical Validation ainda não iniciada

### O que foi decidido?

Inserir Reality Review entre Architecture Review e Medical Validation para
testar o modelo contra dez consultas públicas, desidentificadas ou anonimizadas.

### Por que foi decidido?

A simulação anterior era controlada e sintética. A validação precisa observar
interrupções, retornos, mudanças de assunto, perguntas de alto valor,
contradições e o momento real das Knowledge Queries.

### O que foi implementado?

- Especificação formal da Reality Review.
- Registry com dez casos candidatos de especialidades distintas.
- Política de admissibilidade, acesso, licença e desidentificação.
- Protocolo de anotação cega e matriz de perdas.
- Separação explícita entre Reality Review e Medical Validation.
- Renomeação normativa de Clinical Review para Medical Validation.

### Como foi validado?

- MIMIC, MedDialog e materiais de transcrição foram classificados por tipo de
  evidência e requisito de acesso.
- Consultas reais ainda não foram copiadas para o repositório.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `docs/astera-flow/cognitive-architecture/12-reality-review.md`
- `docs/astera-flow/cognitive-architecture/13-reality-case-registry.md`

### Arquivos alterados

- `docs/astera-flow/README.md`
- `docs/astera-flow/cognitive-architecture/README.md`
- `docs/astera-flow/cognitive-architecture/RFC-001-astera-cognitive-architecture.md`
- `docs/astera-flow/cognitive-architecture/07-cognitive-events.md`
- `docs/astera-flow/cognitive-architecture/08-validation-scenarios.md`
- `docs/astera-flow/cognitive-architecture/09-adrs.md`
- `docs/astera-flow/cognitive-architecture/10-architecture-review.md`
- `docs/astera-flow/cognitive-architecture/11-clinical-simulation.md`
- `docs/adrs/ADR-009-cognitive-architecture-specification.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `RFC-001` — Astera Cognitive Architecture
- `ADR-009` — Cognitive Architecture como especificação normativa

### Astera Flow

- Aba: Cognitive Architecture / Reality Review
- Status: Atualizada — Reality Review registrada; Medical Validation posterior
- Versão: 1.4

### Technical Debt

- Aquisição autorizada, anotação humana, relatórios dos dez casos e decisão de
  Medical Validation ainda pendentes.

### Próximo módulo

Cognitive Validation Lab  
Status: READY

## 2026-08-07 14:24:53 -03:00

### Cognitive Validation Lab — Cognitive QA

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Cognitive Validation Lab  
Execution Time: 12 min  
Author: Agent Runtime  
Architecture: Cognitive QA · Model Validation · Design Authority  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — Medical Validation posterior ao Lab

### O que foi decidido?

Substituir `Reality Case Annotation` por uma área permanente chamada Cognitive
Validation Lab, responsável por validar o modelo cognitivo independentemente
de LLM, Speech provider, RAG ou implementação.

### Por que foi decidido?

Anotar casos é apenas uma atividade. O objetivo real é medir fidelidade de
Facts, Context, Hypotheses, Knowledge Queries, Representations, perdas,
invenções e necessidade de mudança arquitetural.

### O que foi implementado?

- Criado o domínio `docs/astera-flow/cognitive-validation-lab/`.
- Formalizado Cognitive QA (CQA).
- Separados os pipelines de desenvolvimento e validação cognitiva.
- Definidos Case Curator, Cognitive Validator, Gap Detector e Architecture
  Reviewer como agentes pesquisadores sem implementação de código.
- Criados Case Registry, Validation Sessions, Failure Analysis, Edge Cases,
  Regression Suite, Benchmark Results e Medical Validation.
- Modelo `ValidationReport` e nota de caso definidos.
- Registry anterior marcado como histórico/superseded.

### Como foi validado?

- Dez casos candidatos preservados no registry por especialidade e foco CQA.
- Nenhum dado clínico bruto foi copiado para o repositório.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[x] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `docs/astera-flow/cognitive-validation-lab/README.md`
- `docs/astera-flow/cognitive-validation-lab/case-registry.md`
- `docs/astera-flow/cognitive-validation-lab/validation-sessions.md`
- `docs/astera-flow/cognitive-validation-lab/failure-analysis.md`
- `docs/astera-flow/cognitive-validation-lab/edge-cases.md`
- `docs/astera-flow/cognitive-validation-lab/regression-suite.md`
- `docs/astera-flow/cognitive-validation-lab/benchmark-results.md`
- `docs/astera-flow/cognitive-validation-lab/medical-validation.md`

### Arquivos alterados

- `docs/astera-flow/README.md`
- `docs/astera-flow/cognitive-architecture/README.md`
- `docs/astera-flow/cognitive-architecture/12-reality-review.md`
- `docs/astera-flow/cognitive-architecture/13-reality-case-registry.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `RFC-001` — Astera Cognitive Architecture
- `ADR-009` — Cognitive Architecture como especificação normativa
- `12 — Reality Review`

### Astera Flow

- Aba: Cognitive Validation Lab
- Status: Atualizada — CQA registrado como pipeline permanente
- Versão: 1.4

### Technical Debt

- Aquisição autorizada e sessões reais ainda precisam ser executadas; os dez
  registros atuais são candidatos, não resultados validados.

### Próximo módulo

Case Curation  
Status: READY

## 2026-08-07 13:45:36 -03:00

### Workshop 4 — Medical Knowledge Layer

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Workshop 4 — Medical Knowledge Layer  
Execution Time: 12 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Knowledge Governance · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando decisão explícita do Astera Flow

### O que foi decidido?

Separar o Clinical World do Medical World. O estado específico do paciente
contém facts, context, hypotheses, gaps, timeline e encounter; o conhecimento
médico contém guidelines, protocolos, terminologias, literatura e regras
versionadas.

### Por que foi decidido?

O paciente não altera o conhecimento médico. A consulta deve formular uma
`Knowledge Query` a partir de uma hipótese ou Information Gap e receber
`Knowledge Objects` estruturados, em vez de recuperar documentos brutos como
se fossem conhecimento final.

### O que foi implementado?

- Documento do Workshop 4.
- ADR-007 em status `Proposed`.
- Modelo conceitual de `Knowledge Query`.
- Modelo conceitual de `Knowledge Object`.
- Política de snapshots imutáveis e ingestão offline por curadoria.
- Fronteiras iniciais para SNOMED CT, LOINC, RxNorm, CID/ICD e FHIR.
- Papel do ADK definido como mediador entre os dois mundos.
- Glossário e mapa da Fase C.5 atualizados.

### Como foi validado?

- Referências primárias de HL7 FHIR, SNOMED International, LOINC, NLM RxNorm
  e WHO ICD registradas no Workshop 4.
- Links entre Workshop 4, ADR-007, Fase C.5, glossário e índice de ADRs
  revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/workshops/workshop-04-medical-knowledge-layer.md`
- `docs/adrs/ADR-007-medical-knowledge-layer.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/cognitive-architecture-research.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-005` — Clinical Context como molécula cognitiva
- `ADR-006` — Clinical Reasoning Loop
- `ADR-007` — Medical Knowledge Layer (Proposed)

### Astera Flow

- Aba: Architecture Evolution / Fase C.5 / Workshop 4
- Status: Atualizada — Medical Knowledge Layer proposto; aprovação pendente
- Versão: 1.4

### Technical Debt

- Hierarquia de evidência, política de conflitos, curadoria clínica, contratos
  de código e licenciamento por jurisdição ainda são decisões abertas.

### Próximo módulo

Workshop 5 — Modelo de Agentes e Clinical Representation  
Status: READY

## 2026-08-07 13:50:04 -03:00

### Workshop 5 — Specialists e Clinical Representation

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Workshop 5 — Specialists e Clinical Representation  
Execution Time: 10 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Context Enrichment · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando decisão explícita do Astera Flow

### O que foi decidido?

O centro da arquitetura cognitiva é o Clinical Context vivo, não um agente
gigante, o LLM ou o ADK. Specialists de responsabilidade única transformam o
mesmo contexto progressivamente.

### Por que foi decidido?

Specialists não devem conversar diretamente nem produzir estados paralelos.
Cada enriquecimento precisa ser versionado, auditável e recebido pelo próximo
Specialist como uma nova versão do Clinical Context.

### O que foi implementado?

- Documento do Workshop 5 alinhado à proposta de Specialists.
- ADR-008 em status `Proposed`.
- Matriz de responsabilidades de Speech, Facts, Context, Reasoning, Knowledge,
  Gap Detection, Medication e Documentation Specialists.
- Contrato conceitual `Specialist Invocation` e `Context Enrichment`.
- Clinical Context definido como objeto vivo com versões sucessivas.
- ADK limitado à coordenação do contexto, sem conhecer SOAP, FHIR, Timeline,
  PDF ou prontuário.
- Clinical Representations definidas como projeções derivadas com manifesto.

### Como foi validado?

- Links entre Workshop 5, ADR-008, Fase C.5, glossário e índice de ADRs
  revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[x] Runtime  
[x] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/workshops/workshop-05-agent-context-and-clinical-representation.md`
- `docs/adrs/ADR-008-agent-context-and-clinical-representation.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/adrs/ADR-003-cognitive-architecture-workshops.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/cognitive-architecture-research.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-005` — Clinical Context como molécula cognitiva
- `ADR-006` — Clinical Reasoning Loop
- `ADR-007` — Medical Knowledge Layer
- `ADR-008` — Specialists e Clinical Context (Proposed)

### Astera Flow

- Aba: Architecture Evolution / Fase C.5 / Workshop 5
- Status: Atualizada — Specialists propostos; aprovação pendente
- Versão: 1.4

### Technical Debt

- Contrato de código, scheduler do loop, política de merge de enriquecimentos,
  revisão humana e governança de conflitos permanecem decisões abertas.

### Próximo módulo

Conforme próxima definição do Astera Flow  
Status: READY

## 2026-08-07 13:33:24 -03:00

### Fase C.5 — Cognitive Architecture Proposal

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Five Architecture Workshops  
Execution Time: 42 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Knowledge Modeling · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando decisão explícita do Astera Flow

### O que foi decidido?

Registrar uma proposta de Fase C.5 antes da Fase D, sem escrever código, para
modelar o pipeline cognitivo e responder qual é a unidade fundamental de
conhecimento do Astera.

### Por que foi decidido?

O pipeline atual já possui componentes de Speech, Evidence, Knowledge,
Representation e agentes, mas a fronteira conceitual entre Transcript,
Clinical Fact, Evidence, Hypothesis e Medical Knowledge ainda precisa ser
definida antes de novos contratos cognitivos.

### O que foi implementado?

- Documento da Fase C.5 com cinco workshops e entregáveis.
- Research Notes com FHIR Clinical Reasoning, Evidence, EvidenceVariable,
  SNOMED CT, LOINC, RxNorm, OpenMRS e literatura de clinical reasoning.
- ADR-003 em status `Proposed`.
- Fase C.5 registrada no Execution Plan como proposta, sem alterar a Ordem
  Oficial.
- Hipótese de trabalho `Clinical Assertion`, ainda não aprovada.

### Como foi validado?

- Fontes primárias pesquisadas e vinculadas na nota de pesquisa.
- Links relativos entre ADR, workshops, README e Execution Plan revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum arquivo de código foi criado ou alterado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[x] Observability

### Arquivos criados

- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/cognitive-architecture-research.md`
- `docs/adrs/ADR-003-cognitive-architecture-workshops.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/astera-flow/README.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- `ADR-002` — Architecture Evolution Governance
- `ADR-003` — Cognitive Architecture Workshops (Proposed)

### Astera Flow

- Aba: Architecture Evolution / Proposed Phase C.5
- Status: Atualizada — proposta e pesquisa registradas; aprovação pendente do Flow
- Versão: 1.4

### Technical Debt

- Nenhuma dívida de código criada. O vocabulário cognitivo, o modelo de
  evidências e a unidade canônica continuam decisões abertas.

### Próximo módulo

Workshop 1 — O Pipeline Cognitivo  
Status: READY

## 2026-08-07 13:35:36 -03:00

### Workshop 1 — Clinical Facts

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Workshop 1 — O Pipeline Cognitivo  
Execution Time: 18 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Knowledge Modeling · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando decisão explícita do Astera Flow

### O que foi decidido?

Formalizar `Clinical Fact` como a menor unidade de informação clínica
verificável, contextualizada e rastreável do Astera.

### Por que foi decidido?

Transcript e entidade NLP ainda são linguagem/extração. O domínio precisa de
uma unidade que carregue source, provenance, confidence, subject, temporalidade
e status sem depender de SOAP, FHIR, CID, prompt ou LLM.

### O que foi implementado?

- Documento completo do Workshop 1.
- ADR-004 em status `Proposed`.
- Taxonomia inicial de Clinical Facts.
- Lifecycle `Detected → Enriched → Validated → Updated → Resolved → Archived`.
- Separação explícita entre Clinical Fact, Clinical Evidence, Medical Knowledge,
  Clinical Reasoning, Hypothesis e Clinical Recommendation.
- Nenhum rename ou alteração no `evidence_sdk`.

### Como foi validado?

- Provenance, source, confidence, lifecycle e dependências revisados.
- Links entre Workshop, ADR, Fase C.5 e índice de ADRs revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/workshops/workshop-01-clinical-facts.md`
- `docs/adrs/ADR-004-clinical-fact-as-atomic-unit.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-002` — Architecture Evolution Governance
- `ADR-003` — Cognitive Architecture Workshops
- `ADR-004` — Clinical Fact como unidade atômica (Proposed)

### Astera Flow

- Aba: Architecture Evolution / Fase C.5 / Workshop 1
- Status: Atualizada — decisão proposta registrada; aprovação pendente
- Versão: 1.4

### Technical Debt

- O `evidence_sdk` ainda usa nomenclatura anterior por compatibilidade; migração
  só poderá ocorrer após aprovação da ADR-004.
- Polaridade, certainty, contradições, revisão e terminologias canônicas ainda
  são decisões abertas.

### Próximo módulo

Workshop 2 — O que é Clinical Evidence?  
Status: READY

## 2026-08-07 13:37:59 -03:00

### Workshop 2 — Clinical Context

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Workshop 2 — O Modelo Cognitivo  
Execution Time: 14 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Temporal Graph · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando decisão explícita do Astera Flow

### O que foi decidido?

Formalizar `Clinical Context` como a molécula cognitiva do Astera: um estado
temporal e relacional de um paciente durante um Encounter.

### Por que foi decidido?

Clinical Facts isolados não representam o raciocínio médico. O contexto reúne
facts, relationships, timeline, active hypotheses, confidence e metadata, e
evolui por versões sem criar outro paciente, Encounter ou SOAP.

### O que foi implementado?

- Documento do Workshop 2 com modelo temporal e relacional.
- ADR-005 em status `Proposed`.
- Contexto definido como centro de consumo para Agent, Knowledge, Reasoning,
  SOAP, FHIR e Timeline.
- Relações reservadas para o Workshop 3: causa, agrava, melhora com, ocorre
  após, contradiz, confirma, fator de risco e consequência.
- Sequência da C.5 alinhada em cinco workshops.

### Como foi validado?

- Links entre Workshop 2, ADR-005, Fase C.5 e índice de ADRs revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/workshops/workshop-02-clinical-context.md`
- `docs/adrs/ADR-005-clinical-context-as-cognitive-molecule.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-003` — Cognitive Architecture Workshops
- `ADR-004` — Clinical Fact como unidade atômica
- `ADR-005` — Clinical Context como molécula cognitiva (Proposed)

### Astera Flow

- Aba: Architecture Evolution / Fase C.5 / Workshop 2
- Status: Atualizada — Clinical Context proposto; aprovação pendente
- Versão: 1.4

### Technical Debt

- Sem dívida de código. A semântica formal das relações e do grafo temporal
  continua aberta para o Workshop 3.

### Próximo módulo

Workshop 3 — Clinical Relationships e Temporal Graph  
Status: READY

## 2026-08-07 13:40:16 -03:00

### Workshop 3 — Clinical Reasoning Loop

Status: 🟡 In Progress  
Phase: C.5 — Proposed  
Module: Workshop 3 — Clinical Reasoning Model  
Execution Time: 16 min  
Author: Agent Runtime  
Architecture: Cognitive Architecture · Clinical Reasoning Loop · ADR Driven  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Proposed — aguardando decisão explícita do Astera Flow

### O que foi decidido?

Propor o `Clinical Reasoning Loop` como núcleo cognitivo: Observe → Interpret →
Hypothesize → Ask → Observe again → Update Context → Refine Hypotheses.

### Por que foi decidido?

O Astera não deve transformar a primeira conversa diretamente em diagnóstico ou
SOAP. O médico trabalha com hipóteses concorrentes, fatos de suporte, lacunas
de informação e novas perguntas.

### O que foi implementado?

- Documento do Workshop 3.
- ADR-006 em status `Proposed`.
- Modelo conceitual de `Clinical Hypothesis`.
- Modelo conceitual de `Information Gap`.
- Lifecycle de hipóteses concorrentes.
- Papel do ADK definido como coordenação do loop, não como resposta clínica
  direta.
- Sequência C.5 alinhada com Workshop 3 como Clinical Reasoning Model.

### Como foi validado?

- Links entre Workshop 3, ADR-006, Fase C.5 e índice de ADRs revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `docs/astera-flow/workshops/workshop-03-clinical-reasoning-loop.md`
- `docs/adrs/ADR-006-clinical-reasoning-loop.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/adrs/ADR-003-cognitive-architecture-workshops.md`
- `docs/astera-flow/cognitive-architecture-phase.md`
- `docs/astera-flow/agent-execution-plan.md`
- `docs/astera-flow/workshops/workshop-02-clinical-context.md`
- `docs/astera-flow/cognitive-architecture-research.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-004` — Clinical Fact como unidade atômica
- `ADR-005` — Clinical Context como molécula cognitiva
- `ADR-006` — Clinical Reasoning Loop (Proposed)

### Astera Flow

- Aba: Architecture Evolution / Fase C.5 / Workshop 3
- Status: Atualizada — Clinical Reasoning Loop proposto; aprovação pendente
- Versão: 1.4

### Technical Debt

- Calibração de confidence, priorização de Information Gaps, revisão humana,
  contradições e ações possíveis ainda são decisões abertas.

### Próximo módulo

Workshop 4 — Medical Knowledge Layer  
Status: READY

## 2026-08-07 12:49:57 -03:00

### ADR-002 — Architecture Evolution Governance

Status: 🟢 Completed  
Phase: Architecture Governance  
Module: ADR-002 — Architecture Evolution Governance  
Execution Time: 5 min  
Author: Agent Runtime  
Architecture: ADR Driven · Astera Flow Controlled  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Formalizar o ciclo Trigger → ADR → Astera Flow → Implementação → Validação e
as quatro categorias de Architecture Evolution como decisão arquitetural.

### Por que foi decidido?

O backlog passou a classificar mudanças por impacto, mas precisava de uma ADR
que tornasse essa governança rastreável e aplicável às futuras alterações do
Kernel, providers, operações e enterprise.

### O que foi implementado?

- Criada `ADR-002-architecture-evolution-governance.md`.
- Índice de ADRs atualizado.
- Backlog vinculado à ADR-002 e às ADRs específicas futuras.
- Nenhuma evolução de código implementada sem trigger/ADR/Flow.

### Como foi validado?

- Links relativos entre ADR, backlog, README e Journal revisados.
- `git diff --check`: passou.
- Suíte baseline preservada em **78 passed**.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- `docs/adrs/ADR-002-architecture-evolution-governance.md`

### Arquivos alterados

- `docs/adrs/README.md`
- `docs/astera-flow/kernel-evolution-backlog.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- `ADR-002` — Architecture Evolution Governance

### Astera Flow

- Aba: Architecture Evolution
- Status: Atualizada — ADR-002 aprovada e vinculada ao backlog
- Versão: 1.4

### Technical Debt

- ADRs específicas dos seis Approved Evolutions serão criadas somente quando
  os respectivos triggers forem atendidos.

### Próximo módulo

Conforme próxima definição do Astera Flow  
Status: READY

## 2026-08-07 12:44:43 -03:00

### Architecture Evolution Governance

Status: 🟢 Completed  
Phase: Architecture Governance  
Module: Kernel Evolution Backlog  
Execution Time: 4 min  
Author: Agent Runtime  
Architecture: Governance · ADR Driven · Astera Flow Controlled  
Tests: 78 passed (baseline preservado)  
Coverage: N/A  
Decision: Approved pelo Astera Flow

### O que foi decidido?

Classificar o backlog de evoluções em quatro níveis: Core, Provider,
Operational e Enterprise, com estados RFC-like e ciclo obrigatório
Trigger → ADR → Astera Flow → Implementação.

### Por que foi decidido?

A classificação separa mudanças que alteram o Kernel de melhorias de providers,
operação e negócio. Impacto, complexidade, risco, prioridade e custo de
refatoração passam a ser explícitos antes de qualquer implementação.

### O que foi implementado?

- Cabeçalho `Current Architecture`, `Current Version`, `Architecture Debt`,
  `Approved Evolutions` e `Implemented`.
- Matriz dos seis itens aprovados com nível, status, impacto, estrelas de
  complexidade/risco e custo estimado.
- Catálogos Proposed para Operational e Enterprise Evolution.
- Categorias Approved, Proposed, Experimental Ideas e Deprecated Decisions.
- Regra de ADR obrigatória antes de alterar o Kernel.
- Referência adicionada ao README do Astera Flow.

### Como foi validado?

- Estrutura Markdown revisada e `git diff --check` passou.
- Suíte baseline preservada em **78 passed**.
- Nenhum código de Runtime ou Kernel foi alterado.

### Impacto arquitetural

Arquitetura impactada

[ ] Runtime  
[ ] Kernel  
[ ] API  
[ ] Desktop  
[ ] Plugin System  
[ ] Event Bus  
[x] Contracts  
[ ] Observability

### Arquivos criados

- Nenhum.

### Arquivos alterados

- `docs/astera-flow/kernel-evolution-backlog.md`
- `docs/astera-flow/README.md`
- `docs/astera-flow/development-log.md`

### Arquitetura relacionada

- `ADR-001` — Modular Monolith vs Microservices
- ADR específica será obrigatória antes da implementação de cada evolução.

### Astera Flow

- Aba: Architecture Evolution
- Status: Atualizada — governança de evoluções registrada
- Versão: 1.4

### Technical Debt

- Nenhuma dívida de código criada; ADRs específicas dos seis itens ainda serão
  criadas somente quando seus gatilhos forem atendidos.

### Próximo módulo

Conforme próxima definição do Astera Flow  
Status: READY
