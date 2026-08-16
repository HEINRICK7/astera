"""Deterministic Speech-to-Evidence adapter."""
from __future__ import annotations

from hashlib import sha256

from packages.contracts.transcription import Transcript

from .models import EvidenceBatch, EvidenceItem


class TranscriptEvidenceExtractor:
    """Turn transcript segments into evidence while preserving provenance."""

    async def extract(self, *, encounter_id: str, transcript: Transcript) -> EvidenceBatch:
        items = tuple(
            EvidenceItem(
                evidence_id=sha256(
                    f"{encounter_id}:{transcript.request_id}:{index}:{segment.text}".encode()
                ).hexdigest()[:16],
                encounter_id=encounter_id,
                source_type="speech",
                content=segment.text,
                origin_id=transcript.request_id,
                start_ms=segment.start_ms,
                end_ms=segment.end_ms,
                confidence=segment.confidence,
                speaker=segment.speaker,
                metadata={"language": transcript.language, "provider": transcript.provider},
            )
            for index, segment in enumerate(transcript.segments)
        )
        return EvidenceBatch(encounter_id=encounter_id, items=items)
