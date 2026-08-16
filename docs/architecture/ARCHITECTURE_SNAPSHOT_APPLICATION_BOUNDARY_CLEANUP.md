# Architecture Snapshot — Application Boundary Cleanup

**Status:** complete  
**Date:** 2026-08-14  
**Scope:** application boundary only

## Verified result

The Runtime application no longer imports concrete in-memory implementations or
framework/vendor SDKs directly.

```text
application ───────▶ ports/outbound ◀────── adapters
                                               ▲
                                               │
                                           bootstrap
```

Streaming now follows:

```text
LiveClinicalPipeline ─▶ StreamBrokerPort ◀─ InMemoryStreamBrokerAdapter
```

Agent execution now follows:

```text
application services ─▶ AgentRuntimePort ◀─ Google ADK adapter
```

The Google ADK adapter owns provider-specific concerns, including the temporary
`build_adk_model()` compatibility fallback. The application-facing contract is
`build_model()`.

## Fitness gate

```text
Behavioral: 140 passed
Architecture: 6 passed, 0 failed
Full suite: 146 passed, 4 warnings
```

The warnings come from a deprecation inside the installed Google ADK package;
they are not architecture or behavioral failures.

## Deliberate non-goals

This snapshot does not claim that the whole Astera architecture is complete.
The following remain known work:

- AsteraKernel still has composition-root responsibilities;
- real persistence adapters are not connected;
- legacy speech remains in the Astera Runtime;
- `LiveClinicalPipeline` is still broad;
- transcription contracts are not stabilized;
- the six fitness tests cover only the rules currently encoded in the Constitution.

No speech/transcriber or PostgreSQL changes were included in this milestone.
