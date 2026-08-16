# AGENTS.md

## Constituição dos Agentes

Este documento define a estrutura de papéis, responsabilidades e critérios de colaboração dos agentes do projeto Astera.

### Objetivo
- Centralizar as regras de atuação dos agentes.
- Padronizar comunicação e tomada de decisão.
- Garantir consistência entre produto, engenharia e arquitetura.

---

## Ajuste de Comportamento do Agent

A partir deste momento, o Astera Flow passa a ser a fonte oficial de verdade do projeto.

Toda implementação deverá ser guiada exclusivamente pelas especificações presentes no Astera Flow.

Você não deve criar arquitetura paralela, documentação paralela ou tomar decisões estruturais sem que elas estejam registradas no Astera Flow.

---

## Nova Forma de Trabalho

Sempre que receber uma tarefa, siga obrigatoriamente este processo.

1. Localize a aba correspondente dentro do Astera Flow.
2. Leia completamente a especificação antes de iniciar qualquer implementação.
3. Considere o Astera Flow como a documentação oficial do projeto.
4. Implemente exatamente o que está especificado.
5. Caso identifique inconsistências, lacunas ou ambiguidades, não improvise.
6. Interrompa a implementação e registre claramente o que precisa ser decidido para que a documentação seja atualizada primeiro.
7. Após concluir a implementação, atualize o progresso na própria aba correspondente do Astera Flow.

## Product First Rule

Antes de iniciar qualquer Sprint, o agente deve responder obrigatoriamente no
Astera Flow:

1. Qual problema do médico esta Sprint resolve?
2. Qual problema do paciente esta Sprint resolve?
3. O que ficará visível na interface ao final da Sprint?
4. Como esta Sprint aproxima o Astera de uma consulta clínica completa?
5. Existe alguma forma mais simples de entregar este valor?

Se qualquer uma dessas perguntas não puder ser respondida com clareza, a
Sprint não começa. O agente deve registrar a lacuna como pendência no Astera
Flow e aguardar a decisão correspondente.

O resultado esperado de toda Sprint é uma capacidade observável pelo médico ou
pelo paciente. Componentes, providers, adapters e tarefas técnicas só podem
entrar como trabalho habilitador dessa capacidade.

O agente deve usar como teste diário a pergunta:

> **O que um médico consegue fazer hoje que ontem ainda não conseguia?**

O produto é denominado **Astera Clinical**. “Workbench” é apenas o nome
interno, quando necessário.

## Regra de capacidade demonstrável

Nenhuma Sprint pode entregar apenas código. Toda Sprint deve entregar uma
capacidade que possa ser demonstrada por um médico utilizando o sistema.

O resultado deve ser descrito como comportamento:

- “o paciente consegue entrar pelo celular”;
- “o paciente e o médico conseguem conversar”;
- “a IA consegue acompanhar a conversa”;
- “o médico consegue revisar rapidamente a consulta”.

Implementar Galène, Speech ou SOAP não é resultado de produto por si só. O
resultado é uma **Clinical Capability** que o usuário consegue executar com o
Astera.

Nenhuma Sprint existe para implementar uma tecnologia. Toda Sprint existe para
entregar uma nova Clinical Capability demonstrável em uma consulta real.

Toda Sprint também deve produzir uma demonstração gravada associada à Journey.
O encerramento segue obrigatoriamente o [Definition of Done](astera-flow/definition-of-done.md),
com os quatro critérios: Funciona, Demonstrável, Observável e Aprovada.

O projeto mede evolução por **Clinical Capability Maturity**, não por
percentual de código pronto. Uma Journey só avança quando suas capacidades são
executáveis, demonstráveis, observáveis e aprovadas.

## Ordem de entrega do produto

Com a arquitetura congelada e a Vision Demo definida, o agente deve seguir
esta ordem:

1. Patient Journey;
2. Doctor Journey;
3. Communication Journey;
4. Consultation Journey;
5. Clinical Journey;
6. A2UI Journey;
7. Clinical Review Journey;
8. Deployment Journey;
9. Operations Journey.

Enquanto Patient Journey, Doctor Journey, Communication Journey e
Consultation Journey não estiverem demonstráveis, não antecipar IA, Speech,
Clinical Facts, Context, Reasoning, Knowledge, SOAP ou FHIR.

Após a Communication Journey, é obrigatório fazer uma demonstração real com um
notebook e um smartphone, com duas pessoas conversando de forma fluida. Até
essa demonstração ser validada, nenhum trabalho de Speech ou IA começa.

---

## Governança

A governança oficial do projeto encontra-se em:

`docs/engineering/`

Todos os agentes devem seguir a Constituição de Engenharia. Em caso de
conflito, seguir a ordem definida no
[ADR-015 — Engineering Governance](adrs/ADR-015-engineering-governance.md).

---

## Não Criar Documentação Paralela

Não criar arquivos paralelos de arquitetura, planejamento ou roadmap.

Novas decisões arquiteturais continuam sendo registradas no Astera Flow e nos
ADRs. Os documentos ASTERA-ENG definem o processo de implementação, auditoria,
validação e release.

---

## Respeitar a Arquitetura Oficial

Toda implementação deve seguir obrigatoriamente:

- Arquitetura Hexagonal
- Modular Monolith
- Event Driven
- Plugin First
- Cloud First
- Open Source First
- Google ADK
- NATS
- Medical Knowledge Layer

Esses princípios já foram definidos e não devem ser rediscutidos.

---

## Antes de Implementar

Sempre verificar:

- Existe uma aba correspondente no Astera Flow?
- Existe uma especificação para este módulo?
- Existe um contrato definido?
- Existe um fluxo definido?

Se a resposta for "não", interrompa a implementação e solicite a atualização do Astera Flow.

---

## Durante a Implementação

Não invente novas arquiteturas.

Não altere a organização do projeto.

Não mude a stack tecnológica.

Não substitua tecnologias já aprovadas.

Não altere contratos públicos.

Não crie módulos fora da estrutura oficial.

---

## Após Implementar

Verifique se:

- O código segue exatamente o Astera Flow.
- Os testes foram criados.
- O módulo está desacoplado.
- A observabilidade foi adicionada.
- Os contratos foram respeitados.
- Os eventos foram implementados corretamente.

Depois disso, atualize o status da implementação na aba correspondente do Astera Flow.

---

## Princípio Fundamental

O Astera Flow não é apenas documentação.

Ele representa a memória permanente do projeto, a especificação oficial da arquitetura e o guia de engenharia da plataforma.

Sua responsabilidade é transformar o conteúdo do Astera Flow em software, preservando integralmente as decisões arquiteturais já tomadas.

Quando houver dúvida, consulte o Astera Flow.

Nunca assuma.

Nunca improvise.

Nunca substitua a documentação por conhecimento próprio.
