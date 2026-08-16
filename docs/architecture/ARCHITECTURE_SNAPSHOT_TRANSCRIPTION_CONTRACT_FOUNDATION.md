# Architecture Snapshot — Transcription Contract Foundation

**Status:** external adapter complete; runtime integration pending  
**Date:** 2026-08-14  
**Scope:** public transcription boundary and legacy compatibility

## Established boundary

```text
legacy SpeechEvent ───────────────┐
        │                         │
        ▼                         │
LegacySpeechTranscriptionAdapter  │
        │                         │
        └─────────────────────────┤
                                  │
external Transcriber payload ────┘
                                  ▼
                 canonical contracts
                                  │
                                  ▼
                        EvidenceIngressPort
```

The public contracts live in `packages/contracts/transcription` and do not
depend on `speech_sdk` or Runtime application code. Every event carries an
`EventEnvelope` with contract name, `schema_version`, source, event identity,
provenance and receipt metadata.

When the external producer does not provide origin metadata:

```text
event_id        = canonical Astera ID
source_event_id = None
occurred_at     = None
received_at     = Astera receipt time
raw_payload     = original transport payload
```

`raw_payload` stays inside the envelope/provenance boundary and is not a
clinical reasoning API.

`TranscriptSegment` preserves stable identity, sequence, revision, timestamps,
confidence, speaker and optional word timing. The compatibility adapter maps
legacy `transcript.partial` and `transcript.done` events into the new contract,
while `ExternalTranscriptionAdapter` handles the current flat WebSocket events
`transcript.partial`, `transcript.revised` and `transcript.committed`.

## Verification

```text
Transcription contract tests: 11 passed
Behavioral suite: 151 passed
Architecture suite: 6 passed
Full suite: 157 passed, 4 warnings
```

The warnings are existing Google ADK deprecation warnings and are unrelated to
the transcription boundary.

## Explicit boundary of this milestone

The adapters can forward translated events through `EvidenceIngressPort`, and
the live pipeline now consumes canonical events from that ingress. The
pipeline still owns legacy speech-engine orchestration and lifecycle telemetry;
removing that outer speech boundary is the next milestone.

Therefore this milestone does **not** claim that speech has been removed from
Astera. It also does not change persistence, the external Transcriber service,
or clinical processing semantics.
