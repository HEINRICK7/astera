# Platform

| Campo | Valor |
|---|---|
| **Status** | Stable |
| **Version** | 1.0 |
| **Evolution policy** | Slow, evidence-driven, ADR-010 protected |

## Escopo

Kernel, Event Bus, SDKs, Observability, Security, Configuration e Plugin System.

A Platform fornece os contratos e as boundaries. Ela não escolhe provider e
não deve mudar para acomodar um provider específico.

## Regra

Uma mudança na Platform só ocorre por limitação concreta demonstrada no
Cognitive Validation Lab, falha operacional ou decisão explícita do Astera
Flow. Integração de provider deve acontecer dentro da Capability existente.
