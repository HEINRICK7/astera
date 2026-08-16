"""Inbound port for evidence entering the Clinical Runtime."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from packages.contracts.transcription import TranscriptEvent


@runtime_checkable
class EvidenceIngressPort(Protocol):
    """Clinical input boundary independent of the evidence source."""

    async def ingest(self, event: TranscriptEvent) -> None:
        """Accept one versioned evidence event for clinical processing."""
        ...
