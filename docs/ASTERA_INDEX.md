# ASTERA_INDEX.md

> Master Navigation Document
>
> Este documento é o ponto oficial de entrada para qualquer agente de IA ou desenvolvedor.
>
> Nenhum agente deve iniciar a implementação sem seguir esta sequência.

---

# Objetivo

O Astera possui diversos documentos.

Este índice define:

- ordem de leitura;
- prioridade;
- dependências;
- documentos obrigatórios;
- documentos opcionais.

Este documento elimina ambiguidades durante a implementação.

---

# Ordem Oficial de Leitura

1. AGENTS.md
2. ASTERA_INDEX.md
3. DOCUMENT_CONVENTIONS.md
4. GLOSSARY.md
5. README.md
6. Architecture
7. Engineering
8. Knowledge
9. Product
10. ADRs
11. Astera Flow

---

# Documentos Obrigatórios

Todos os agentes devem ler obrigatoriamente:

- AGENTS.md
- ASTERA_INDEX.md
- DOCUMENT_CONVENTIONS.md
- GLOSSARY.md
- README.md
- Astera Flow

---

# Categorias

## Constituição

Define regras permanentes.

- AGENTS.md
- ASTERA_INDEX.md

---

## Arquitetura

Define como a plataforma funciona.

- Architecture
- ADRs

---

## Engenharia

Define como construir.

- Engineering
- Astera Flow

---

## Conhecimento

Define fontes.

- Knowledge

---

## Produto

Define visão.

- Product

---

# Dependências

Antes de implementar um módulo, verificar seus documentos relacionados.

Exemplo:

Plugin

↓

Architecture

↓

Engineering

↓

Astera Flow

---

# Regra

Nunca implementar utilizando apenas conhecimento do modelo.

Sempre utilizar o Astera Flow como fonte principal.

---

# Objetivo Final

Garantir que todos os agentes utilizem exatamente a mesma sequência de leitura e implementação.
