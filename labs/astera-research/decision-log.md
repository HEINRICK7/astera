# Astera Research — Decision Log

Registro das decisões tomadas durante a pesquisa de providers. Decisões sobre
arquitetura do Astera continuam pertencendo ao Astera Flow e às ADRs vigentes.

## 2026-08-07 — DR-001 — Research antes da integração

Status: Approved  
Scope: Todos os providers futuros

**Decisão:** nenhum provider entra no Astera antes de existir um Lab que
documente runtime, limitações, dependências, benchmark, licença e mapeamento
para os contratos existentes.

**Motivo:** separar descoberta tecnológica de integração de produto e evitar
acoplamento prematuro ao vendor.

## 2026-08-07 — DR-002 — Parakeet é o único provider ativo

Status: Approved  
Scope: Speech Transcription

**Decisão:** concluir o ciclo Parakeet antes de iniciar Whisper, Deepgram,
Qwen2.5-VL, Snowstorm ou BGE-M3.

**Motivo:** o primeiro provider deve estabelecer o método repetível de
pesquisa, benchmark e certificação.

## 2026-08-07 — DR-003 — Word boosting não é vocabulário médico

Status: Approved  
Scope: Parakeet realtime

**Decisão:** registrar `word_boosting` como recurso documentado do provider,
mas manter “medical vocabulary” como não comprovado até benchmark clínico
autorizado.

**Motivo:** não transformar uma feature nominal em uma capacidade clínica não
demonstrada.

## 2026-08-07 — DR-004 — Ausência de runtime é bloqueio explícito

Status: Active  
Scope: Parakeet Lab

**Decisão:** sem GPU/driver, NIM, credencial NGC e áudio autorizado, o estado é
`Runtime Integration Blocked`. Não criar fallback, mock ou resultado sintético.

**Motivo:** preservar a cadeia Documentado → Comprovado → Certificado.

## 2026-08-07 — DR-005 — Development Provider não depende de Benchmark Provider

Status: Approved  
Scope: Speech Development

**Decisão:** `faster-whisper` em CPU/int8 é o Development Provider oficial de
Speech. `NVIDIA Parakeet NIM` permanece no Provider Lab como Benchmark Provider.

**Motivo:** desenvolvimento local, testes e CI não podem depender de GPU,
CUDA, NGC ou cloud. A troca para Parakeet ocorre apenas em Benchmark ou após
certificação para Production.
