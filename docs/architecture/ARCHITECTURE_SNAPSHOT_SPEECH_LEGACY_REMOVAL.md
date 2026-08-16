# Architecture Snapshot — Speech Legacy Removal

Date: 2026-08-14  
Status: complete for the Astera principal repository.

## Final ownership boundary

```text
astera-live-transcriber
        │ external transport payload
        ▼
ExternalTranscriptionAdapter
        │ TranscriptPartial/Revised/Committed
        ▼
EvidenceIngressPort
        ▼
ClinicalTranscriptState
        ▼
Clinical Runtime
```

The Astera principal repository no longer owns audio capture, PCM transport,
VAD, STT provider sessions or provider-specific speech adapters.

## Removed from Astera

- `packages/speech_sdk`
- `apps/runtime/src/adapters/speech`
- `LegacySpeechEnginePort`
- the old `SpeechPlugin`
- xAI/Faster-Whisper/Parakeet provider composition in bootstrap
- speech engine and provider-specific tests
- legacy PCM ingestion from `/api/v1/clinical-stream/{encounter_id}`
- obsolete speech provider settings and the `faster-whisper` development dependency

The deleted provider modules and tests were untracked legacy files in this
workspace, so they are not recoverable through Git history. Their ownership
and replacement are represented by the canonical external adapter tests.

## Boundary counts

The counts below are scoped to implementation and test imports, excluding
historical architecture notes and the separate `labs/astera-research`
provider experiments.

| Check | Result |
| --- | ---: |
| Runtime production imports of `packages.speech_sdk` | 0 |
| Runtime production imports of `adapters.speech` | 0 |
| `LegacySpeechEnginePort` references in production | 0 |
| Clinical Runtime imports of legacy speech | 0 |
| Bootstrap references to speech providers | 0 |
| HTTP audio/STT ingestion references | 0 |
| Tests importing removed speech implementation | 0 |
| `packages/speech_sdk` directory | absent |
| `apps/runtime/src/adapters/speech` directory | absent |

## Validation

```text
Behavioral: 123 passed
Architecture: 8 passed
Full suite: 131 passed
Warnings: 4 existing Google ADK deprecation warnings
```

The shared plugin capability taxonomy may still mention generic capability
names such as `speech.transcription`; these are metadata vocabulary, not an
implementation or ownership dependency in Astera Runtime.

## Next architectural milestone

Do not reopen the speech boundary. The next milestone is
`Persistence Boundary / Production Persistence`.
