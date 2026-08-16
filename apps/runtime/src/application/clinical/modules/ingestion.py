"""Canonical evidence ingestion boundary."""
from __future__ import annotations

import asyncio
from typing import Any

from packages.contracts.transcription import TranscriptCommitted, TranscriptEvent, TranscriptSegment
from apps.runtime.src.application.clinical.evidence_ingress import QueueEvidenceIngress


class CanonicalIngestionModule:
    """Accept canonical evidence and expose only runtime-ready observations."""

    def open(self) -> tuple[QueueEvidenceIngress, asyncio.Queue[TranscriptEvent | object]]:
        queue: asyncio.Queue[TranscriptEvent | object] = asyncio.Queue()
        return QueueEvidenceIngress(queue), queue

    @staticmethod
    def segment(event: TranscriptEvent) -> tuple[TranscriptSegment, bool]:
        source = event.segments[0] if isinstance(event, TranscriptCommitted) else event.segment
        return (
            TranscriptSegment(
                text=source.text,
                start_ms=source.start_ms,
                end_ms=source.end_ms,
                confidence=source.confidence,
                speaker=source.speaker,
                sequence=source.sequence,
                segment_id=source.segment_id,
                revision=source.revision,
            ),
            isinstance(event, TranscriptCommitted),
        )

    @staticmethod
    def event_kind(event: TranscriptEvent, *, is_final: bool) -> str:
        if is_final:
            return "transcript.done"
        return "transcript.revised" if event.__class__.__name__ == "TranscriptRevised" else "transcript.partial"
