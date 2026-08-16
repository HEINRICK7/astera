"""Immutable streaming event contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class StreamEvent:
    stream_id: str
    event_type: str
    sequence: int
    payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: f"event-{uuid4().hex[:12]}")
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.stream_id.strip() or not self.event_type.strip():
            raise ValueError("stream identity fields must not be empty")
        if self.sequence < 0:
            raise ValueError("sequence must be zero or greater")

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "stream_id": self.stream_id,
            "event_type": self.event_type,
            "sequence": self.sequence,
            "payload": dict(self.payload),
            "occurred_at": self.occurred_at.isoformat(),
        }
