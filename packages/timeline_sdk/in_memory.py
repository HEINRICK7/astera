"""Development timeline directory behind the future event-store adapter."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from packages.auth_sdk import Principal

from .models import TimelineEvent


class InMemoryTimelineRepository:
    """Development adapter for append-only patient timeline events."""

    def __init__(self) -> None:
        self._events: list[TimelineEvent] = []

    def append(
        self,
        principal: Principal,
        *,
        patient_id: str,
        event_type: str,
        encounter_id: str | None = None,
        payload: dict[str, object] | None = None,
        occurred_at: datetime | None = None,
    ) -> TimelineEvent:
        event = TimelineEvent(
            event_id=f"event-{uuid4().hex[:12]}",
            organization_id=principal.organization_id,
            patient_id=patient_id,
            event_type=event_type,
            occurred_at=occurred_at or datetime.now(timezone.utc),
            encounter_id=encounter_id,
            payload=payload or {},
        )
        self._events.append(event)
        return event

    def list_for(self, principal: Principal, patient_id: str) -> tuple[TimelineEvent, ...]:
        return tuple(
            sorted(
                (
                    event
                    for event in self._events
                    if event.organization_id == principal.organization_id
                    and event.patient_id == patient_id
                ),
                key=lambda event: event.occurred_at,
            )
        )


# Compatibility name for callers migrating from the original directory API.
TimelineDirectory = InMemoryTimelineRepository
