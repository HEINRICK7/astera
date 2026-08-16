# Speech Legacy Removal — dependency inventory

Status: complete. See [Speech Legacy Removal Snapshot](ARCHITECTURE_SNAPSHOT_SPEECH_LEGACY_REMOVAL.md).

## Target boundary

```text
astera-live-transcriber
        │ transport payload
        ▼
ExternalTranscriptionAdapter
        │ canonical TranscriptPartial/Revised/Committed
        ▼
EvidenceIngressPort
        ▼
ClinicalTranscriptState (Runtime-internal projection)
        ▼
Clinical Runtime
```

The Runtime-internal projection is intentionally not part of
`packages/contracts`. Only interoperable transcription evidence remains in
that package: `EventEnvelope`, `TranscriptSegment`, `TranscriptPartial`,
`TranscriptRevised` and `TranscriptCommitted`.

## Current consumers

| Consumer | Current dependency | Decision |
| --- | --- | --- |
| `application/clinical/live_stream.py` | canonical `TranscriptEvent` runner | no speech implementation dependency |
| `application/clinical/normalization.py` | `ClinicalTranscriptState` | migrated; no `speech_sdk` import |
| `application/plugins/evidence` | transcript document/segments | migrated to `packages.contracts.transcription` |
| `packages/evidence_sdk` | transcript document | migrated to `packages.contracts.transcription` |
| `application/plugins/speech` | audio request and provider transcriber protocols | retired and absent |
| `bootstrap/main.py` | provider registry, xAI/Faster-Whisper and legacy adapter | absent from composition |
| `adapters/speech/*` | provider implementations and legacy event bridge | retired and absent |
| `/api/v1/clinical-stream/*` | PCM ingestion and speech lifecycle | changed to read-only clinical projection |

## Remaining references

There are no implementation or import references to the removed speech
surface in `apps/runtime/src`, `packages` or current behavioral tests.
Historical engineering notes and the separate provider experiments under
`labs/astera-research` remain as archival material and are outside the
Astera Runtime ownership boundary.
