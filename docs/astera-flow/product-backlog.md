---
document_id: astera-product-backlog
title: Astera Product Backlog — Clinical Product Increments
category: Product
status: Official
version: 2.0
owner: Astera Product Engineering
depends_on:
  - AGENTS.md
  - ../adrs/ADR-011-platform-complete.md
  - clinical-workflows/clinical-workflow-dataset.md
used_by:
  - Product Engineering
  - Clinical Validation
  - Demo Day
last_updated: 2026-08-08
---

# Astera Product Backlog — Clinical Product Increments

Status: **Active — Product First**  
Operating Model: **Clinical Product / Product Engineering**  
Architecture: **🟢 Frozen — ADR-011**

O backlog é organizado por jornadas clínicas. Providers, Capabilities e
componentes são meios de implementação; o aceite é definido pelo resultado que
um médico ou paciente consegue vivenciar.

## Regra de priorização

O Astera não planeja a próxima entrega como “implementar faster-whisper” ou
“implementar PaddleOCR”. Planeja como “concluir uma consulta”. Trabalho técnico
só entra no backlog como tarefa filha de um CPI e precisa explicar qual etapa da
jornada clínica habilita.

\`\`\`text
Clinical Product Increment
  ├── Clinical workflow
  ├── Patient value
  ├── Acceptance evidence
  └── Enabling work (provider, adapter, persistence, UI, observability)
\`\`\`

Estados oficiais: Planned → Ready → In Progress → Clinical Validation →
Certified → Released. Uma entrega técnica não promove o estado do CPI sozinha.

## ASTERA PLATFORM — Architecture Frozen

Status: **🟢 ARCHITECTURE FROZEN**

A arquitetura da plataforma está congelada. A partir deste ponto, nenhuma
alteração arquitetural entra no trabalho sem ADR aprovada.

Sem ADR, ficam proibidos:

- novos Managers;
- novos Engines;
- novos States;
- novos Providers como novos conceitos arquiteturais;
- novas abstrações.

Implementações de providers já previstos continuam permitidas quando forem
trabalho habilitador de uma jornada de produto. A pergunta de cada Sprint deixa
de ser “qual abstração falta?” e passa a ser:

> **O que um médico consegue fazer hoje que ontem ainda não conseguia?**

## Product First Rule — permanente

A arquitetura base da experiência clínica está congelada. A partir deste ponto,
nenhuma Sprint deve criar novos Managers, Engines, Coordinators, Containers,
Contexts ou abstrações arquiteturais sem uma ADR aprovada.

Antes de iniciar qualquer Sprint, o backlog deve responder claramente:

1. Qual problema do médico esta Sprint resolve?
2. O que ficará visível na interface ao final da Sprint?
3. Como isso aproxima o Astera da primeira consulta clínica completa?

Uma Sprint que não responda às três perguntas não entra no backlog de produto.
Providers, adapters e tarefas técnicas continuam permitidos apenas como trabalho
habilitador de uma entrega visível e aceita pelo médico.

### Ordem oficial das jornadas

| Fase | Jornada | Pergunta de produto | Entrega observável |
|---:|---|---|---|
| 0 | Vision Demo | Qual experiência estamos construindo? | Filme de referência em 11 cenas |
| 1 ⭐ | Patient Journey | O paciente consegue entrar? | Paciente abre o link no smartphone e entra na sala de espera |
| 2 | Doctor Journey | O médico consegue iniciar? | Médico vê o paciente conectado e inicia a consulta |
| 3 ⭐ | Communication Journey | Os dois conseguem conversar? | Notebook e smartphone trocam áudio e vídeo com conexão estável |
| 4 ⭐⭐⭐ | Consultation Journey | A consulta realmente acontece? | Sessão, participantes, espera, início e encerramento funcionam |
| 5 | Clinical Journey | A consulta começa a ser entendida? | Speech → Facts → Context → Reasoning → Knowledge |
| 6 ⭐⭐⭐⭐⭐ | A2UI Journey | O conhecimento aparece durante a conversa? | Clinical Events viram Knowledge Cards no Canvas |
| 7 | Clinical Review Journey | O médico consegue finalizar? | SOAP, FHIR, revisão, assinatura e aprovação |
| 8 | Deployment Journey | O produto pode ser disponibilizado? | Entrega reproduzível em ambiente autorizado |
| 9 | Operations Journey | A consulta pode ser acompanhada? | Logs, auditoria, persistência, replay e Golden Consultation |

O resultado de cada fase deve poder ser aberto no computador e reconhecido
como uma experiência de produto. Nenhuma fase é promovida por uma evolução
interna que não seja demonstrável ao usuário.

### Fase atual

**Sprint 0 — Vision Demo:** 🟢 concluída como referência de produto.  
**Sprint 1 — Patient Journey:** 🟡 em implementação.

Capability em foco: `CC-001 — Paciente consegue entrar na consulta`.
O fluxo já está implementado no Workbench; a demonstração gravada e a
aprovação profissional ainda são pendências da Definition of Done.

As próximas Sprints não devem antecipar IA, Speech, SOAP ou FHIR. Primeiro o
Astera deve entregar paciente, médico, comunicação e consulta funcionando.

### Gate obrigatório após Communication Journey

Quando a Communication Journey terminar, o trabalho deve parar para uma
demonstração real:

```text
Notebook
   ↓
Astera Clinical
   ↔ comunicação
Smartphone
```

Duas pessoas devem conseguir conversar de forma fluida por áudio e vídeo. Não
participam dessa demonstração IA, Speech, SOAP ou A2UI. O resultado precisa ser
observado por um médico em uma sessão de aproximadamente 30 minutos, sem
explicação técnica, para identificar onde ele olha, clica, hesita ou se
distrai. Somente após esse gate a Clinical Journey pode começar.

### Communication Platform — fundamento concluído

Antes de escolher ou implementar um provider de produção, a Sprint de
Communication Platform deve responder:

> O médico consegue iniciar e conduzir uma consulta com comunicação segura,
> independentemente do provider utilizado?

O objetivo desta definição não foi implementar Galène. Foi estabilizar a boundary de comunicação
que permite entregar uma consulta real sem acoplar o produto a uma tecnologia
de mídia. A plataforma conhece apenas participantes, mídia, dispositivos,
permissões, qualidade da conexão e eventos de comunicação. Ela não conhece
Runtime, Speech, Clinical Graph, SOAP, FHIR, A2UI, Clinical Cards ou IA.

| Ordem | Entrega | Resultado observável |
|---|---|---|
| ✅ A — Communication Contract | Estado, ciclo de vida, eventos e tipos provider-neutral | Qualquer provider pode obedecer ao mesmo contrato |
| ✅ B — MediaDevices Provider | Adaptador local de áudio e vídeo | Base local disponível para a jornada de consulta |
| → C — Patient Journey | Entrada, espera, consentimento e prontidão | O paciente consegue entrar na consulta |
| → D — Communication Session | Join, leave e transições da sessão | Dois dispositivos conseguem estabelecer a consulta |
| 5 — Galène Provider | Adaptador de produção atrás do contrato | Galène entra sem alterar Session, Canvas ou UI |
| 7 — Golden Consultation Provider | Replay de mídia, timeline e eventos | Golden Consultation pode ser reproduzida e validada |

Os estados `Communication State`, `Clinical State` e `Workspace State` são
projeções independentes da `ConsultationSession` e não devem ser misturados.
Todo novo provider deve implementar exatamente o mesmo contrato público. Após
esta Sprint, novas abstrações arquiteturais ficam proibidas sem ADR; o backlog
volta a ser exclusivamente orientado ao valor visível para o médico.

Esta definição habilita a `CC-003 — Paciente e médico conectam áudio e vídeo`.
Ela só será promovida quando notebook e smartphone estabelecerem comunicação
real, com duas pessoas e observação de um médico. Galène continua sendo apenas
um provider futuro; não é o resultado da Capability.

## Dashboard de Produto — CPI-001

### CPI-001 — Consulta Primária

O dashboard mede a jornada que o médico consegue concluir, não a quantidade de
componentes implementados. Os estados abaixo são o baseline atual e só avançam
com evidência reproduzível da jornada.

| Etapa da consulta | Estado atual | Evidência esperada para avançar |
|---|---:|---|
| Paciente entra | 🟡 | Paciente entra por outro dispositivo e a sessão registra a entrada |
| Consentimento | ⚪ | Consentimento aceito e visível para o médico |
| Áudio | 🟡 | Áudio bidirecional validado em dois dispositivos |
| Vídeo | 🟡 | Vídeo bidirecional validado em dois dispositivos |
| Speech | 🟡 | Transcript completo, segmentado e normalizado |
| Clinical Facts | 🟡 | Fatos clínicos rastreáveis e sem ruído semântico evidente |
| Reasoning | 🟢 | Resultado produzido pelo Runtime e apresentado para revisão |
| SOAP | 🟡 | Nota clínica narrativa revisável pelo médico |
| FHIR | 🔴 | Bundle clínico real validado pelo HAPI FHIR |
| Consulta completa | ❌ | Jornada inteira concluída, aprovada e persistida |

O CPI-001 só passa a **Certified** quando “Consulta completa” estiver verde
mediante validação clínica. Um estágio técnico verde não certifica a consulta.

## Clinical Capability Maturity

O Astera não mede Features, Stories ou Tasks como resultado de produto. Mede
**Clinical Capabilities**: capacidades clínicas que uma pessoa consegue
executar e demonstrar no sistema.

Clinical Capability Maturity substitui percentuais genéricos como “80% pronto”.
Uma capacidade está entregue quando funciona, é demonstrável, observável e
aprovada conforme o [Definition of Done](definition-of-done.md).

| Capability | Capacidade clínica | Status atual |
|---|---|---:|
| CC-001 | Paciente consegue entrar na consulta | 🟡 |
| CC-002 | Paciente concede consentimento | ⚪ |
| CC-003 | Paciente e médico conectam áudio e vídeo | ⚪ |
| CC-004 | Médico inicia a consulta | ⚪ |
| CC-005 | Consulta acontece com sessão ativa | ⚪ |
| CC-006 | Conversa é transcrita | ⚪ |
| CC-007 | Fatos clínicos são identificados | ⚪ |
| CC-008 | Contexto e raciocínio clínico são organizados | ⚪ |
| CC-009 | Conhecimento aparece durante a consulta | ⚪ |
| CC-010 | Médico revisa e aprova o SOAP | ⚪ |
| CC-011 | Resultado clínico é representado em FHIR | ⚪ |
| CC-012 | Consulta é salva e pode ser auditada | ⚪ |

O [Clinical Capability Catalog](clinical-capability-catalog.md) é a fonte
oficial dos detalhes. O [Clinical Capability Map](clinical-capability-map.md)
mostra quem usa cada capacidade e como elas se relacionam.

O status de uma Journey só avança quando as capacidades que a compõem possuem
evidências. O produto não pode declarar maturidade com base na quantidade de
código produzido.

## Regra de demonstrabilidade

Cada Sprint deve terminar com algo que possa ser aberto no computador e
reconhecido como produto:

- Patient Journey: enviar um link e o paciente entrar pelo celular;
- Doctor Journey: o médico ver que o paciente está conectado;
- Communication Journey: notebook e smartphone conversarem por áudio e vídeo;
- Consultation Journey: a sessão ter espera, início, estado ativo e encerramento;
- Clinical Journey: a consulta começar a ser entendida;
- A2UI Journey: o conhecimento aparecer visualmente;
- Clinical Review Journey: o médico revisar e aprovar;
- Deployment Journey: o produto ser disponibilizado de forma reproduzível;
- Operations Journey: a consulta ser salva e reproduzível.

Toda Sprint deve gerar uma demonstração gravada. Os arquivos seguem nomes
previsíveis e ficam associados à evidência da Sprint:

| Sprint | Evidência esperada |
|---|---|
| Patient Journey | `patient-journey-demo.mp4` |
| Doctor Journey | `doctor-journey-demo.mp4` |
| Communication Journey | `communication-journey-demo.mp4` |
| Consultation Journey | `consultation-journey-demo.mp4` |
| Clinical Journey | `clinical-journey-demo.mp4` |
| A2UI Journey | `a2ui-journey-demo.mp4` |
| Clinical Review Journey | `clinical-review-journey-demo.mp4` |
| Deployment Journey | `deployment-journey-demo.mp4` |
| Operations Journey | `operations-journey-demo.mp4` |

O vídeo deve mostrar a capacidade sendo usada, não uma apresentação de código.

O Workbench continua sendo o nome interno do projeto. A experiência de produto
é denominada **Astera Clinical**.

## Regra de UX — Consultório digital brasileiro

Todo texto visível ao usuário deve estar em Português (Brasil), escrito na
linguagem cotidiana da prática clínica. O modo clínico deve parecer um
consultório digital, não uma ferramenta de desenvolvimento traduzida.

Termos técnicos como workspace, runtime, engineering, review mode e knowledge
panel não devem aparecer no modo clínico quando houver uma expressão natural
para o médico. O modo Engenharia pode permanecer bilíngue quando for ativado
explicitamente para depuração.

Regra de prioridade visual:

> Se um médico perceber primeiro o software em vez do paciente, a interface
> falhou.

## Backlog por jornadas

O produto é decomposto em jornadas. Cada jornada possui seus próprios
incrementos de produto; nenhum incremento é nomeado por componente técnico.
Para evitar ambiguidade entre jornadas, os IDs usam o prefixo da jornada.

### Patient Journey

| CPI | Entrega | Resultado para o paciente |
|---|---|---|
| PJ-CPI-001 | Paciente entra | O paciente abre um convite válido e entra na consulta |
| PJ-CPI-002 | Consentimento | O paciente entende e registra sua decisão |
| PJ-CPI-003 | Teste de câmera e microfone | O paciente confirma que pode ser visto e ouvido |
| PJ-CPI-004 | Sala de espera | O paciente aguarda o médico com orientação clara |

### Doctor Journey

| CPI | Entrega | Resultado para o médico |
|---|---|---|
| DJ-CPI-001 | Criar consulta | O médico prepara uma consulta para um paciente |
| DJ-CPI-002 | Paciente conectado | O médico vê que o paciente está pronto |
| DJ-CPI-003 | Iniciar consulta | O médico inicia a conversa sem configuração técnica |

### Communication Journey

| CPI | Entrega | Resultado para os participantes |
|---|---|---|
| CMJ-CPI-001 | Câmera e microfone | Cada pessoa consegue habilitar seus dispositivos |
| CMJ-CPI-002 | Áudio e vídeo | Notebook e smartphone trocam mídia em tempo real |
| CMJ-CPI-003 | Reconexão | A conversa se recupera de uma interrupção previsível |
| CMJ-CPI-004 | Qualidade da conexão | Participantes entendem quando a conexão está degradada |

Esta jornada responde apenas se os participantes conseguem se comunicar. Ela
não inclui Speech, IA, Clinical Facts, SOAP ou FHIR.

### Consultation Journey

| CPI | Entrega | Resultado para o médico |
|---|---|---|
| COJ-CPI-001 | Sessão de consulta | A consulta possui participantes, estado e identidade |
| COJ-CPI-002 | Início e espera | O médico inicia e encerra a consulta com clareza |
| COJ-CPI-003 | Timeline da consulta | O médico acompanha espera, sessão ativa e encerramento |

Communication Journey é o transporte entre as pessoas. Consultation Journey é
a experiência de conduzir a sessão. A segunda só começa depois da primeira.

### Clinical Journey

| CPI | Entrega | Resultado para o médico |
|---|---|---|
| CJ-CPI-001 | Speech | A fala da consulta vira transcript revisável |
| CJ-CPI-002 | Clinical Facts | Fatos clínicos aparecem rastreáveis ao que foi dito |
| CJ-CPI-003 | Reasoning | O médico acompanha a organização do contexto clínico |
| CJ-CPI-004 | SOAP | Um primeiro SOAP narrativo fica disponível para revisão |

### Clinical Review Journey

| CPI | Entrega | Resultado para o médico |
|---|---|---|
| CRJ-CPI-001 | Revisão clínica | O médico inspeciona a documentação gerada |
| CRJ-CPI-002 | Correções | O médico corrige o que for necessário |
| CRJ-CPI-003 | Aprovação | O médico aprova a versão final da consulta |

### Deployment Journey

| CPI | Entrega | Resultado para o produto |
|---|---|---|
| DJP-CPI-001 | Entrega autorizada | O produto pode ser disponibilizado em ambiente aprovado |
| DJP-CPI-002 | Configuração | A experiência é reproduzível no ambiente de destino |

### Operations Journey

| CPI | Entrega | Resultado para o produto |
|---|---|---|
| OPJ-CPI-001 | Persistência | A consulta aprovada é salva com rastreabilidade |
| OPJ-CPI-002 | Auditoria | A história da consulta pode ser investigada |
| OPJ-CPI-003 | Replay e Golden Consultation | A jornada pode ser reproduzida e validada |

O `CPI-001 — Consulta Primária` continua sendo o incremento de integração do
produto: ele só é concluído quando os incrementos necessários das jornadas
formarem uma consulta completa. Ele não substitui os CPIs das jornadas.

## Roadmap de produto

| Incremento | Caso de uso | Estado | Resultado para o usuário |
|---|---|---|---|
| CPI-001 | Primary Care Consultation | 🟡 Em execução | Consulta clínica simples concluída do áudio à persistência |
| CPI-002 | Consulta com Exame | ⚪ Ready | Áudio + imagem/OCR → Knowledge → SOAP/FHIR |
| CPI-003 | Consulta Pediátrica | ⚪ Planned | Jornada pediátrica validada clinicamente |
| CPI-004 | Consulta de Retorno | ⚪ Planned | Contexto longitudinal comparável e documentação de retorno |
| CPI-005 | Consulta de Emergência | ⚪ Planned | Jornada de alta prioridade com rastreabilidade e validação médica |

## Ordem de execução atual

| Ordem | Entrega de produto | Próximo resultado observável |
|---:|---|---|
| 1 | CPI-001 — Primary Care Consultation | Uma consulta autorizada percorre o workflow completo |
| 2 | CPI-002 — Consulta com Exame | Consulta com documento/imagem produz SOAP revisável |
| 3 | CPI-003 — Consulta Pediátrica | Workflow pediátrico validado com linguagem e contexto adequados |
| 4 | CPI-004 — Consulta de Retorno | A consulta atual usa contexto longitudinal sem inventar fatos |
| 5 | CPI-005 — Consulta de Emergência | Caso de alta prioridade possui trilha de segurança e revisão |

## CPI-001 — Primary Care Consultation

### Pergunta da sprint

> **O Astera consegue concluir uma consulta clínica simples do início ao fim?**

Esta é a única pergunta que promove ou bloqueia o CPI-001. O resultado é
Yes, No ou Blocked; não existe percentual de conclusão do CPI baseado em
componentes.

**Objetivo:** permitir que um médico conduza uma consulta primária simples e
receba documentação clínica revisável sem copiar e colar entre componentes.

```text
Áudio real autorizado
  ↓
Transcript
  ↓
Clinical Facts
  ↓
Clinical Context
  ↓
Clinical Reasoning Loop
  ↓
Medical Knowledge
  ↓
SOAP
  ↓
FHIR
  ↓
Persistência durável
```

### Critérios de aceite

- áudio falado autorizado processado por provider real;
- transcript preserva idioma, segmentos, timestamps e request_id;
- Clinical Facts são rastreáveis ao transcript;
- Clinical Context e hipóteses são gerados pelo pipeline existente;
- SOAP é derivado do contexto e revisável pelo médico;
- FHIR é gerado sem alterar o domínio clínico;
- resultado é persistido de forma durável;
- Clinical Replay reconstrói a jornada completa;
- observabilidade e ProviderTrace ficam fora do domínio clínico;
- Medical Validation, CQA e Cognitive Regression registram evidências;
- nenhuma intervenção manual ou adapter determinístico participa da execução.

### Critério de saída da sprint

O CPI-001 responde **Yes** somente quando uma Golden Consultation autorizada:

1. começa com áudio de uma consulta simples;
2. gera transcript;
3. extrai Clinical Facts rastreáveis;
4. constrói Clinical Context;
5. executa Reasoning e Knowledge;
6. gera SOAP revisável;
7. gera FHIR;
8. persiste os artefatos;
9. permite recuperar o Clinical Replay completo.

Além disso, o caso precisa ser executado sem transcrição, fatos, SOAP ou FHIR
copiados manualmente por um operador. O médico deve conseguir revisar o
resultado e as lacunas devem permanecer explícitas.

### O que não decide o resultado

Não são critérios de conclusão desta sprint:

- qual Speech Provider foi usado;
- qual modelo de NLP, terminologia ou FHIR foi usado;
- número de componentes implementados;
- cobertura de testes isolados;
- benchmark entre providers;
- performance de produção;
- suporte a exames, pediatria, retorno ou emergência.

Esses itens só entram no backlog quando habilitam ou ampliam um CPI posterior.

### Componentes internos previstos

| Necessidade do CPI | Implementação interna | Estado |
|---|---|---|
| Speech | faster-whisper Development Provider | Runtime smoke executado; áudio falado pendente |
| Clinical Facts/Context | Pipeline cognitivo existente | Harness validado |
| Reasoning/Knowledge | Pipeline cognitivo existente | Harness validado; workflow real pendente |
| SOAP/FHIR | Representations existentes | FHIR durável pendente |
| Persistência | Gateway atual + destino durável | Pendente |

### Próximas fatias de entrega

Estas são as próximas entregas do CPI-001. O nome da fatia descreve o resultado
clínico; a implementação interna pode usar mais de um provider ou componente.

| Fatia | Resultado verificável | Estado |
|---|---|---|
| CPI-001.A — Capturar consulta | Áudio autorizado de uma consulta real disponível no registry | Ready |
| CPI-001.B — Organizar consulta | Transcript, Facts e Context navegáveis no mesmo replay | In Progress |
| CPI-001.C — Documentar consulta | SOAP revisável, com origem nos fatos e lacunas explícitas | In Progress |
| CPI-001.D — Fechar consulta | FHIR persistido, replay recuperável e aceite médico registrado | Planned |

## Próximos Clinical Product Increments

### CPI-002 — Consulta com Exame

**Objetivo:** combinar fala e documento ou imagem clínica sem perder a
proveniência de cada evidência.

**Aceite:** o médico identifica o conteúdo extraído do exame, distingue dado
observado de interpretação, revisa o SOAP e recupera a representação FHIR do
encontro.

### CPI-003 — Consulta Pediátrica

**Objetivo:** documentar uma consulta pediátrica com distinção entre paciente,
responsável e relato do acompanhante.

**Aceite:** idade, peso, queixa, histórico e relato do responsável permanecem
atribuídos corretamente; o sistema não inventa medidas ou achados ausentes.

### CPI-004 — Consulta de Retorno

**Objetivo:** documentar a evolução desde o encontro anterior, preservando
continuidade sem misturar fatos históricos com fatos do encontro atual.

**Aceite:** o médico consegue revisar mudanças, medicações, resultados e plano
atual, com cada item ligado à consulta de origem.

### CPI-005 — Consulta de Emergência

**Objetivo:** reduzir o trabalho de documentação em uma jornada de alta
prioridade com destaque para lacunas e sinais de risco.

**Aceite:** o resultado é explicitamente revisável, não produz diagnóstico
automático conclusivo e mantém uma trilha de evidência adequada ao caso.

## Dataset do produto

O dataset oficial passa a ser um **Clinical Workflow Dataset**, não um conjunto
isolado por provider. A primeira entrada é [Golden Consultation 001](clinical-workflows/clinical-workflow-dataset.md).

## Regras de execução

- Não alterar Kernel, SDKs ou contratos públicos para avançar um CPI.
- Não declarar CPI concluído por testes de componentes isolados.
- Um CPI só é concluído quando o caso percorre a jornada clínica completa.
- Providers podem ser trocados, mas o resultado clínico e os contratos permanecem
  provider-neutral.
- Toda entrega registra data/hora e evidências no [Engineering Journal](development-log.md).

## Definition of Done de produto

O contrato normativo está em [Definition of Done — Clinical Journeys](definition-of-done.md).
Um CPI ou Journey só é concluído quando atende simultaneamente:

- **Funciona** — jornada ponta a ponta executada;
- **Demonstrável** — pode ser mostrada ao vivo sem explicação técnica;
- **Observável** — possui eventos, logs ou métricas verificáveis;
- **Aprovada** — passou por revisão de UX e validação profissional.

Vídeo da demonstração, evidências de cada etapa, persistência e registro no
Development Log fazem parte do aceite quando aplicáveis ao escopo.

## O que não conta como entrega de produto

- instalar ou trocar um provider sem executar um workflow;
- aumentar a cobertura de testes de um componente isolado;
- publicar um percentual sem dataset, método e evidência;
- gerar SOAP a partir de texto copiado manualmente;
- marcar Production porque o harness determinístico passou.
