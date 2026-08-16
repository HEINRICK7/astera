# Astera Flow — Engineering Standards

> **Objetivo**
>
> Este documento define os padrões obrigatórios de organização de código da plataforma Astera.
> Seu objetivo é garantir que todos os módulos permaneçam pequenos, desacoplados, legíveis, reutilizáveis e fáceis de evoluir.
>
> **Estas regras são obrigatórias para todos os Agentes de IA e desenvolvedores.**

---

## Filosofia

A complexidade nunca deve crescer dentro de um arquivo.
Ela deve crescer através da **composição de pequenos componentes**.

> Sempre preferir **10 arquivos de 80 linhas** ao invés de **1 arquivo de 800 linhas**.

---

## Regra Principal

Nenhum arquivo deverá crescer indefinidamente.
Sempre que um componente começar a assumir mais de uma responsabilidade, ele deverá ser dividido.

---

## Limites Oficiais

| Artefato | Recomendado | Máximo | Acima disso |
|---|---|---|---|
| Arquivo | 150 linhas | 250 linhas | Refatoração obrigatória |
| Classe | 150 linhas | 250 linhas | Refatoração obrigatória |
| Função/Método | 20 linhas | 40 linhas | Refatoração obrigatória |
| Arquivo de Configuração | — | 300 linhas | — |
| Enum | — | 100 linhas | — |
| Interface | — | 150 linhas | — |

---

## Responsabilidade

Cada arquivo deverá possuir **apenas uma responsabilidade**.

✔ `runtime_state.py`
✔ `capability_registry.py`
✔ `context_manager.py`

✘ `RuntimeHelpersUtilsManager.py`

---

## Estrutura

**Nunca misturar** Domain, Infrastructure, Application, Adapters no mesmo arquivo.

---

## Imports

- Máximo recomendado: **15 imports**
- Acima disso: verificar acoplamento

---

## Dependências

**Nunca criar dependências circulares.**

---

## Regras por Artefato

| Artefato | Regra |
|---|---|
| Classes | Uma classe. Uma responsabilidade. |
| Interfaces | Uma interface. Um contrato. |
| Eventos | Um evento por arquivo. |
| Value Objects | Um Value Object por arquivo. |
| Entities | Uma Entity por arquivo. |
| Exceptions | Uma Exception por arquivo. |
| DTOs | Preferencialmente 1 DTO por arquivo. |
| Adapters | Cada Adapter implementa apenas uma Port. |
| Ports | Cada Port representa apenas um contrato. |
| Plugins | Cada Plugin possui estrutura própria. Nunca compartilhar implementação. |

---

## Casos de Uso

Cada caso de uso deverá representar **uma única ação**.

✔ `CreateEncounter` · `CloseEncounter` · `RegisterCapability` · `GenerateSOAP`
✘ `EncounterService`

---

## Organização

Sempre preferir:

```
speech/
    transcriber.py
    streaming.py
    language.py
    confidence.py
    events.py
```

Ao invés de `speech.py` com 900 linhas.

---

## Refatoração Obrigatória

O Agent deverá **interromper a implementação e refatorar** quando detectar:

- Arquivos muito grandes
- Classes muito grandes
- Funções muito grandes
- Excesso de responsabilidades
- Duplicação
- Acoplamento excessivo

---

## Complexidade

Evitar: `if` dentro de `if` · switches gigantes · funções enormes

---

## Reutilização

Antes de criar código novo, pesquisar:

- Existe implementação semelhante?
- Existe SDK?
- Existe componente compartilhado?

---

## Comentários

Comentários devem explicar **POR QUÊ**. Nunca **O QUÊ**.

---

## Testes

Cada módulo deverá possuir:

- `test_unit.py`
- `test_integration.py`
- `test_e2e.py` (quando aplicável)

A estrutura de testes deve **espelhar exatamente** a estrutura do código.

---

## Nomeação

| Artefato | Convenção |
|---|---|
| Arquivos | `snake_case` |
| Classes | `PascalCase` |
| Métodos | `snake_case` |
| Constantes | `UPPER_CASE` |

---

## Definition of Done

Um módulo somente estará concluído quando:

- [ ] Respeita todos os limites de linhas
- [ ] Não possui responsabilidades múltiplas
- [ ] Possui testes
- [ ] Possui documentação
- [ ] Possui observabilidade
- [ ] Segue Arquitetura Hexagonal
- [ ] Segue Modular Monolith

---

## Regra Final

Sempre que existir dúvida entre **criar mais um arquivo** ou **aumentar um arquivo existente**:

> **Escolha criar mais um arquivo.**

A modularização possui prioridade sobre a concentração de código.
O objetivo da plataforma Astera é **permanecer simples por muitos anos**, independentemente do seu crescimento.
