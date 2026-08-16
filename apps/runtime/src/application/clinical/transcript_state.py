"""Clinical-only projection of canonical transcription evidence."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from packages.contracts.transcription import TranscriptSegment


class TranscriptSessionStatus(str, Enum):
    STARTING = "starting"
    STREAMING = "streaming"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class TranscriptSessionLifecycle:
    status: TranscriptSessionStatus = TranscriptSessionStatus.STARTING
    transition_count: int = 0

    _allowed: Mapping[TranscriptSessionStatus, frozenset[TranscriptSessionStatus]] = field(
        default_factory=lambda: {
            TranscriptSessionStatus.STARTING: frozenset({TranscriptSessionStatus.STREAMING, TranscriptSessionStatus.STOPPING, TranscriptSessionStatus.ERROR}),
            TranscriptSessionStatus.STREAMING: frozenset({TranscriptSessionStatus.PAUSED, TranscriptSessionStatus.STOPPING, TranscriptSessionStatus.ERROR}),
            TranscriptSessionStatus.PAUSED: frozenset({TranscriptSessionStatus.STREAMING, TranscriptSessionStatus.STOPPING, TranscriptSessionStatus.ERROR}),
            TranscriptSessionStatus.STOPPING: frozenset({TranscriptSessionStatus.COMPLETED, TranscriptSessionStatus.ERROR}),
            TranscriptSessionStatus.COMPLETED: frozenset(),
            TranscriptSessionStatus.ERROR: frozenset(),
        },
        repr=False,
        compare=False,
    )

    def transition(self, status: TranscriptSessionStatus) -> "TranscriptSessionLifecycle":
        if status == self.status:
            return self
        if status not in self._allowed[self.status]:
            raise ValueError(f"invalid transcript session transition: {self.status.value} -> {status.value}")
        return TranscriptSessionLifecycle(status=status, transition_count=self.transition_count + 1)

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status.value, "transition_count": self.transition_count}


@dataclass(frozen=True, slots=True)
class ClinicalTranscriptSegment:
    """Internal segment view with lifecycle state kept outside contracts."""

    contract: TranscriptSegment
    is_final: bool

    def __getattr__(self, name: str) -> Any:
        return getattr(self.contract, name)

    def to_dict(self) -> dict[str, Any]:
        return {**self.contract.to_dict(), "is_final": self.is_final}


@dataclass(frozen=True, slots=True)
class TranscriptSessionSnapshot:
    session_id: str
    language: str
    started_at: datetime
    updated_at: datetime
    partial: str
    final_segments: tuple[ClinicalTranscriptSegment, ...]
    full_transcript: str
    status: TranscriptSessionStatus
    version: int
    metrics: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "language": self.language,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "partial": self.partial,
            "final_segments": [segment.to_dict() for segment in self.final_segments],
            "full_transcript": self.full_transcript,
            "status": self.status.value,
            "version": self.version,
            "metrics": dict(self.metrics),
        }


class ClinicalTranscriptState:
    """Revision-aware state used only by Clinical Runtime use cases."""

    def __init__(self, *, session_id: str, language: str = "") -> None:
        if not session_id or not session_id.strip():
            raise ValueError("session_id must not be empty")
        now = datetime.now(timezone.utc)
        self.session_id = session_id
        self.language = language
        self.started_at = now
        self.updated_at = now
        self.partial = ""
        self._final_segments: list[ClinicalTranscriptSegment] = []
        self._final_segment_ids: set[str] = set()
        self._current_partial: ClinicalTranscriptSegment | None = None
        self.full_transcript = ""
        self.lifecycle = TranscriptSessionLifecycle()
        self.version = 0
        self.metrics: dict[str, Any] = {
            "audio_bytes": 0,
            "audio_duration_ms": 0.0,
            "segments": 0,
            "chunks_received": 0,
            "partial_events": 0,
            "final_events": 0,
            "revisions": 0,
            "provider_latency_ms": 0.0,
            "runtime_latency_ms": 0.0,
            "end_to_end_latency_ms": 0.0,
            "capture_latency_ms": 0.0,
            "publish_latency_ms": 0.0,
            "dropped_frames": 0,
            "reconnects": 0,
            "errors": 0,
            "bytes_received": 0,
            "latency_ms": 0.0,
            "time_to_first_partial_ms": None,
            "time_to_first_final_ms": None,
            "total_silence_ms": 0.0,
            "total_speaking_ms": 0.0,
            "revision_count": 0,
            "segment_count": 0,
            "discarded_segments": 0,
            "asr_corrections": 0,
            "latency_average_ms": 0.0,
            "latency_min_ms": None,
            "latency_max_ms": None,
        }

    def started(self) -> None:
        self.lifecycle = self.lifecycle.transition(TranscriptSessionStatus.STREAMING)
        self._touch()

    def pause(self) -> None:
        self.lifecycle = self.lifecycle.transition(TranscriptSessionStatus.PAUSED)
        self._touch()

    def resume(self) -> None:
        self.lifecycle = self.lifecycle.transition(TranscriptSessionStatus.STREAMING)
        self._touch()

    def stopping(self) -> None:
        self.lifecycle = self.lifecycle.transition(TranscriptSessionStatus.STOPPING)
        self._touch()

    def observe_audio(self, *, bytes_received: int, duration_ms: float = 0.0) -> None:
        if bytes_received < 0 or duration_ms < 0:
            raise ValueError("audio metrics must not be negative")
        self.metrics["chunks_received"] += 1
        self.metrics["bytes_received"] += bytes_received
        self.metrics["audio_bytes"] += bytes_received
        self.metrics["audio_duration_ms"] += duration_ms
        self._touch()

    def observe_voice_activity(self, *, duration_ms: float, speaking: bool) -> None:
        if duration_ms < 0:
            raise ValueError("duration_ms must be zero or greater")
        self.metrics["total_speaking_ms" if speaking else "total_silence_ms"] += duration_ms
        self._touch()

    def mark_latency(self, metric: str) -> None:
        if metric not in {"time_to_first_partial_ms", "time_to_first_final_ms"}:
            raise ValueError(f"unknown transcript latency metric: {metric}")
        if self.metrics[metric] is None:
            self.metrics[metric] = round((self.updated_at - self.started_at).total_seconds() * 1000, 2)

    def completed(self) -> None:
        if self.lifecycle.status != TranscriptSessionStatus.STOPPING:
            self.stopping()
        self.lifecycle = self.lifecycle.transition(TranscriptSessionStatus.COMPLETED)
        self._touch()

    def failed(self) -> None:
        if self.lifecycle.status not in {TranscriptSessionStatus.COMPLETED, TranscriptSessionStatus.ERROR}:
            self.lifecycle = self.lifecycle.transition(TranscriptSessionStatus.ERROR)
        self.metrics["errors"] += 1
        self._touch()

    @property
    def status(self) -> str:
        return self.lifecycle.status.value

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        latency_ms = round((self.updated_at - self.started_at).total_seconds() * 1000, 2)
        self.metrics["latency_ms"] = latency_ms
        self.metrics["runtime_latency_ms"] = latency_ms
        self.metrics["end_to_end_latency_ms"] = latency_ms
        samples = int(self.metrics.get("_latency_samples", 0)) + 1
        total = float(self.metrics.get("_latency_total_ms", 0.0)) + latency_ms
        self.metrics["_latency_samples"] = samples
        self.metrics["_latency_total_ms"] = total
        self.metrics["latency_average_ms"] = round(total / samples, 2)
        self.metrics["latency_min_ms"] = latency_ms if self.metrics["latency_min_ms"] is None else min(self.metrics["latency_min_ms"], latency_ms)
        self.metrics["latency_max_ms"] = latency_ms if self.metrics["latency_max_ms"] is None else max(self.metrics["latency_max_ms"], latency_ms)

    def observe_event_timing(self, *, captured_at: datetime | None, received_at: datetime, processed_at: datetime, published_at: datetime | None) -> None:
        if captured_at is not None:
            self.metrics["capture_latency_ms"] = max(0.0, (received_at - captured_at).total_seconds() * 1000)
        self.metrics["runtime_latency_ms"] = max(0.0, (processed_at - received_at).total_seconds() * 1000)
        if published_at is not None:
            self.metrics["publish_latency_ms"] = max(0.0, (published_at - processed_at).total_seconds() * 1000)
            if captured_at is not None:
                self.metrics["end_to_end_latency_ms"] = max(0.0, (published_at - captured_at).total_seconds() * 1000)

    def apply(self, segment: TranscriptSegment, *, is_final: bool) -> bool:
        segment_id = segment.segment_id or f"segment-{segment.sequence}"
        previous_revision = (
            self._current_partial.revision
            if self._current_partial is not None and self._current_partial.segment_id == segment_id
            else -1
        )
        if segment_id in self._final_segment_ids or (previous_revision >= 0 and segment.revision <= previous_revision):
            self.metrics["discarded_segments"] += 1
            return False
        previous_text = self._current_partial.text if previous_revision >= 0 else None
        revision = max(segment.revision, previous_revision + 1)
        projected = ClinicalTranscriptSegment(
            contract=replace(segment, segment_id=segment_id, revision=revision),
            is_final=is_final,
        )
        if is_final:
            self._final_segment_ids.add(segment_id)
            self._final_segments.append(projected)
            self._final_segments.sort(key=lambda item: (item.start_ms, item.sequence))
            self._current_partial = None
            self.partial = ""
            self.metrics["final_events"] += 1
            self.metrics["segment_count"] = len(self._final_segments)
            self.metrics["segments"] = len(self._final_segments)
            if previous_revision >= 0:
                self.metrics["revision_count"] += 1
                self.metrics["revisions"] += 1
        else:
            self._current_partial = projected
            self.partial = projected.text
            self.metrics["partial_events"] += 1
            if previous_revision >= 0:
                self.metrics["revision_count"] += 1
                self.metrics["revisions"] += 1
                if previous_text != projected.text:
                    self.metrics["asr_corrections"] += 1
        self.version += 1
        self.full_transcript = " ".join(value for value in (" ".join(item.text for item in self._final_segments), self.partial) if value).strip()
        self._touch()
        return True

    @property
    def final_segments(self) -> tuple[ClinicalTranscriptSegment, ...]:
        return tuple(self._final_segments)

    @property
    def current_partial(self) -> ClinicalTranscriptSegment | None:
        return self._current_partial

    @property
    def final_text(self) -> str:
        return " ".join(segment.text for segment in self._final_segments).strip()

    @property
    def current_text(self) -> str:
        return self.partial

    @property
    def text(self) -> str:
        return self.full_transcript

    @property
    def metrics_snapshot(self) -> dict[str, Any]:
        return {key: value for key, value in self.metrics.items() if not key.startswith("_")}

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "language": self.language,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "partial": self.partial,
            "final_segments": [segment.to_dict() for segment in self._final_segments],
            "current_partial": self._current_partial.to_dict() if self._current_partial else None,
            "final_text": self.final_text,
            "current_text": self.current_text,
            "full_transcript": self.full_transcript,
            "text": self.full_transcript,
            "status": self.status,
            "lifecycle": self.lifecycle.to_dict(),
            "version": self.version,
            "metrics": self.metrics_snapshot,
        }

    def freeze(self) -> TranscriptSessionSnapshot:
        return TranscriptSessionSnapshot(
            session_id=self.session_id,
            language=self.language,
            started_at=self.started_at,
            updated_at=self.updated_at,
            partial=self.partial,
            final_segments=self.final_segments,
            full_transcript=self.full_transcript,
            status=self.lifecycle.status,
            version=self.version,
            metrics=MappingProxyType(self.metrics_snapshot),
        )

    def append(self, segment: TranscriptSegment) -> None:
        """Compatibility helper for local transcript-memory callers."""
        self.apply(segment, is_final=bool(getattr(segment, "is_final", True)))

    @property
    def rolling_text(self) -> str:
        return self.full_transcript
