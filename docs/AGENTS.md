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

---

## O Astera Flow é a Fonte de Verdade

Considere o Astera Flow como equivalente a uma especificação oficial de engenharia.

Em caso de conflito entre:

- código existente;
- conhecimento interno do modelo;
- sugestões de boas práticas;
- documentação externa;

o Astera Flow sempre possui prioridade.

---

## Não Criar Documentação Paralela

Não criar novos arquivos de arquitetura.

Não criar novos arquivos de planejamento.

Não criar novos roadmaps.

Não criar novos documentos de engenharia.

Toda evolução do projeto deverá ocorrer dentro do Astera Flow.

Caso seja necessária uma nova decisão arquitetural, ela deverá ser adicionada como uma nova aba ou seção do Astera Flow, nunca em um documento separado.

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
