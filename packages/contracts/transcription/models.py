"""Provider-neutral, versioned transcription event contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


TRANSCRIPTION_CONTRACT = "astera.transcription"
TRANSCRIPTION_CONTRACT_VERSION = 1


def _required(value: str, name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value.strip()


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Stable metadata shared by every cross-runtime contract event."""

    event_id: str
    event_type: str
    source: str
    schema_version: int = TRANSCRIPTION_CONTRACT_VERSION
    occurred_at: datetime | None = None
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str | None = None
    source_event_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    raw_payload: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        _required(self.event_id, "event id")
        _required(self.event_type, "event type")
        _required(self.source, "event source")
        if self.schema_version < 1:
            raise ValueError("event schema version must be positive")

    @property
    def version(self) -> int:
        """Compatibility alias for callers of the first internal draft."""
        return self.schema_version

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": TRANSCRIPTION_CONTRACT,
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "received_at": self.received_at.isoformat(),
            "trace_id": self.trace_id,
            "source_event_id": self.source_event_id,
            "metadata": dict(self.metadata),
            "raw_payload": dict(self.raw_payload) if self.raw_payload is not None else None,
        }


@dataclass(frozen=True, slots=True)
class TranscriptWord:
    """Optional word-level timing preserved across the boundary."""

    text: str
    start_ms: int
    end_ms: int
    confidence: float | None = None

    def __post_init__(self) -> None:
        _required(self.text, "word text")
        if self.start_ms < 0 or self.end_ms < self.start_ms:
            raise ValueError("word timestamps must be ordered")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("word confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    """Provider-neutral segment identity, timing and revision data."""

    segment_id: str
    text: str
    start_ms: int
    end_ms: int
    sequence: int = 0
    revision: int = 0
    confidence: float | None = None
    speaker: str | None = None
    raw_text: str | None = None
    projected_text: str | None = None
    projected_text_clean: str | None = None
    words: tuple[TranscriptWord, ...] = ()
    def __post_init__(self) -> None:
        _required(self.segment_id, "segment id")
        _required(self.text, "segment text")
        if self.start_ms < 0 or self.end_ms < self.start_ms:
            raise ValueError("segment timestamps must be ordered")
        if self.sequence < 0 or self.revision < 0:
            raise ValueError("segment sequence and revision must be zero or greater")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("segment confidence must be between 0 and 1")
        if any(word.start_ms < self.start_ms or word.end_ms > self.end_ms for word in self.words):
            raise ValueError("word timestamps must fit within segment timestamps")

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "text": self.text,
            "raw_text": self.raw_text,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "sequence": self.sequence,
            "revision": self.revision,
            "confidence": self.confidence,
            "speaker": self.speaker,
            "projected_text": self.projected_text,
            "projected_text_clean": self.projected_text_clean,
            "words": [word.to_dict() for word in self.words],
        }


@dataclass(frozen=True, slots=True)
class Transcript:
    """Provider-neutral transcript document used by evidence adapters."""

    request_id: str
    language: str | None
    provider: str
    segments: tuple[TranscriptSegment, ...]

    def __post_init__(self) -> None:
        _required(self.request_id, "request id")
        _required(self.provider, "provider")

    @property
    def text(self) -> str:
        return " ".join(segment.text for segment in self.segments)

    @property
    def raw_text(self) -> str:
        return " ".join(segment.raw_text or segment.text for segment in self.segments)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "language": self.language,
            "provider": self.provider,
            "text": self.text,
            "raw_text": self.raw_text,
            "segments": [segment.to_dict() for segment in self.segments],
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class TranscriptEvent:
    """Base context shared by partial, revised and committed events."""

    envelope: EventEnvelope
    session_id: str
    language: str
    provider: str
    encounter_id: str | None = None
    patient_id: str | None = None

    def __post_init__(self) -> None:
        _required(self.session_id, "session id")
        _required(self.language, "language")
        _required(self.provider, "provider")

    def _context_dict(self) -> dict[str, Any]:
        return {
            "envelope": self.envelope.to_dict(),
            "session_id": self.session_id,
            "language": self.language,
            "provider": self.provider,
            "encounter_id": self.encounter_id,
            "patient_id": self.patient_id,
        }


@dataclass(frozen=True, slots=True)
class TranscriptPartial(TranscriptEvent):
    """Current non-committed transcript hypothesis."""

    segment: TranscriptSegment

    def __post_init__(self) -> None:
        TranscriptEvent.__post_init__(self)
        if self.envelope.event_type != "transcript.partial":
            raise ValueError("partial events must use transcript.partial")

    def to_dict(self) -> dict[str, Any]:
        return {**self._context_dict(), "segment": self.segment.to_dict()}


@dataclass(frozen=True, slots=True)
class TranscriptRevised(TranscriptEvent):
    """A correction to a previously emitted transcript segment."""

    segment: TranscriptSegment
    replaces_event_id: str | None = None

    def __post_init__(self) -> None:
        TranscriptEvent.__post_init__(self)
        if self.envelope.event_type != "transcript.revised":
            raise ValueError("revised events must use transcript.revised")
        if self.segment.revision < 1:
            raise ValueError("revised segments must have revision greater than zero")

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._context_dict(),
            "segment": self.segment.to_dict(),
            "replaces_event_id": self.replaces_event_id,
        }


@dataclass(frozen=True, slots=True)
class TranscriptCommitted(TranscriptEvent):
    """One or more final segments committed to the transcript."""

    segments: tuple[TranscriptSegment, ...]
    text: str

    def __post_init__(self) -> None:
        TranscriptEvent.__post_init__(self)
        if self.envelope.event_type != "transcript.committed":
            raise ValueError("committed events must use transcript.committed")
        if not self.segments:
            raise ValueError("committed events must contain at least one segment")
        _required(self.text, "committed transcript text")

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._context_dict(),
            "text": self.text,
            "segments": [segment.to_dict() for segment in self.segments],
        }
