"""Adapter from the current astera-live-transcriber wire payloads."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from apps.runtime.src.ports.inbound.evidence import EvidenceIngressPort
from packages.contracts.transcription import (
    EventEnvelope,
    TranscriptCommitted,
    TranscriptEvent,
    TranscriptPartial,
    TranscriptRevised,
    TranscriptSegment,
    TranscriptWord,
)


class ExternalTranscriptionAdapter:
    """Normalize flat WebSocket events without exposing transport details."""

    source = "astera-live-transcriber"
    default_language = "pt-BR"

    def to_contract(
        self,
        payload: Mapping[str, Any],
        *,
        received_at: datetime | None = None,
        session_id: str | None = None,
        language: str | None = None,
        encounter_id: str | None = None,
        patient_id: str | None = None,
        transport: str = "websocket",
    ) -> TranscriptEvent | None:
        """Convert one current wire event; lifecycle events are ignored."""
        event_type = self._required_text(payload.get("type"), "event type")
        if event_type not in {
            "transcript.partial",
            "transcript.revised",
            "transcript.committed",
        }:
            return None

        resolved_session_id = self._required_text(
            payload.get("session_id") or session_id,
            "session id",
        )
        segment_id = self._required_text(payload.get("segment_id"), "segment id")
        revision = int(payload.get("revision", 0))
        text = self._required_text(payload.get("text"), "transcript text")
        start_ms = int(payload.get("start_ms", 0))
        end_ms = int(payload.get("end_ms", start_ms))
        resolved_language = self._required_text(
            payload.get("language") or language or self.default_language,
            "language",
        )
        provider = self._required_text(payload.get("provider") or "unknown", "provider")
        received = received_at or datetime.now(timezone.utc)
        occurred_at = self._parse_datetime(payload.get("occurred_at"))
        source_event_id = self._optional_text(payload.get("event_id"))
        event_id = source_event_id or self._canonical_event_id(
            event_type=event_type,
            session_id=resolved_session_id,
            segment_id=segment_id,
            revision=revision,
        )
        technical = payload.get("technical")
        metadata: dict[str, Any] = {"transport": transport}
        if isinstance(technical, Mapping):
            metadata["technical"] = dict(technical)

        envelope = EventEnvelope(
            event_id=event_id,
            event_type=event_type,
            source=self.source,
            occurred_at=occurred_at,
            received_at=received,
            source_event_id=source_event_id,
            metadata=metadata,
            raw_payload=dict(payload),
        )
        segment = TranscriptSegment(
            segment_id=segment_id,
            text=text,
            raw_text=text,
            projected_text=self._optional_text(payload.get("projected_text")),
            projected_text_clean=self._optional_text(payload.get("projected_text_clean")),
            start_ms=start_ms,
            end_ms=end_ms,
            revision=revision,
            confidence=self._optional_float(payload.get("confidence")),
            speaker=self._optional_text(payload.get("speaker")),
            words=self._words(payload.get("words", ()), start_ms=start_ms, end_ms=end_ms),
        )
        common = {
            "envelope": envelope,
            "session_id": resolved_session_id,
            "language": resolved_language,
            "provider": provider,
            "encounter_id": encounter_id,
            "patient_id": patient_id,
        }
        if event_type == "transcript.partial":
            return TranscriptPartial(**common, segment=segment)
        if event_type == "transcript.revised":
            return TranscriptRevised(**common, segment=segment)
        return TranscriptCommitted(**common, segments=(segment,), text=text)

    async def forward(
        self,
        payload: Mapping[str, Any],
        *,
        ingress: EvidenceIngressPort,
        received_at: datetime | None = None,
        session_id: str | None = None,
        language: str | None = None,
        encounter_id: str | None = None,
        patient_id: str | None = None,
        transport: str = "websocket",
    ) -> TranscriptEvent | None:
        """Normalize and send a transcript event into the clinical port."""
        contract = self.to_contract(
            payload,
            received_at=received_at,
            session_id=session_id,
            language=language,
            encounter_id=encounter_id,
            patient_id=patient_id,
            transport=transport,
        )
        if contract is not None:
            await ingress.ingest(contract)
        return contract

    @staticmethod
    def _canonical_event_id(
        *,
        event_type: str,
        session_id: str,
        segment_id: str,
        revision: int,
    ) -> str:
        return f"{session_id}:{segment_id}:{revision}:{event_type}"

    @staticmethod
    def _required_text(value: Any, name: str) -> str:
        text = ExternalTranscriptionAdapter._optional_text(value)
        if text is None or not text.strip():
            raise ValueError(f"{name} must not be empty")
        return text.strip()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    @staticmethod
    def _words(
        values: Any,
        *,
        start_ms: int,
        end_ms: int,
    ) -> tuple[TranscriptWord, ...]:
        if not isinstance(values, (list, tuple)):
            return ()
        words: list[TranscriptWord] = []
        for value in values:
            if not isinstance(value, Mapping):
                continue
            text = ExternalTranscriptionAdapter._required_text(
                value.get("word") or value.get("text"),
                "word text",
            )
            words.append(
                TranscriptWord(
                    text=text,
                    start_ms=int(value.get("start_ms", start_ms)),
                    end_ms=int(value.get("end_ms", end_ms)),
                    confidence=ExternalTranscriptionAdapter._optional_float(value.get("confidence")),
                )
            )
        return tuple(words)
