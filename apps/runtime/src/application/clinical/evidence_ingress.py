"""Application-side evidence ingress implementations."""
from __future__ import annotations

import asyncio

from packages.contracts.transcription import TranscriptEvent

from apps.runtime.src.ports.inbound.evidence import EvidenceIngressPort


class QueueEvidenceIngress(EvidenceIngressPort):
    """Queue canonical evidence for the Clinical Runtime consumer."""

    def __init__(self, queue: asyncio.Queue[TranscriptEvent]) -> None:
        self._queue = queue

    async def ingest(self, event: TranscriptEvent) -> None:
        await self._queue.put(event)
