# Architecture Snapshot — Clinical Ingress Cutover

**Status:** complete  
**Date:** 2026-08-14  
**Scope:** canonical clinical ingress; speech removal excluded

## Runtime boundary

```text
SpeechEvent legacy ───────┐
                          ▼
                 LegacySpeechTranscriptionAdapter
                          │
Transcriber payload ─────┐│
                          ▼▼
                   EvidenceIngressPort
                          │
                          ▼
                canonical TranscriptEvent
                          │
                          ▼
             facts / cards / review / finalization
```

The `LiveClinicalPipeline` now places both legacy-translated and externally
translated events into the same active `EvidenceIngressPort`. Clinical state
processing consumes `TranscriptPartial`, `TranscriptRevised` and
`TranscriptCommitted`; it does not consume the legacy `SpeechEvent` model.

`occurred_at`, `received_at` and the legacy `published_at` projection remain
distinct. When the canonical event has no origin or publication timestamp,
the corresponding measurements remain unavailable instead of being inferred.

## Verification

```text
Behavioral: 152 passed
Architecture: 6 passed
Legacy vs external parity: 1 passed
Full suite: 158 passed, 4 warnings
Clinical application imports of SpeechEvent: 0
```

Parity compares semantic facts, cards, final transcript state and completed
clinical status for equivalent legacy and external transcript inputs.

## Deliberate non-goals

The pipeline still owns the outer legacy speech engine orchestration, audio
feeding and lifecycle telemetry. This is intentional and remains the scope of
the next `Speech Legacy Removal` milestone. No speech package, STT integration,
external Transcriber repository or persistence implementation was removed.
