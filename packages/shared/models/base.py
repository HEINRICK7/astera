"""
Astera Shared Models — Base Classes.

AsteraModel: base Pydantic model for all DTOs and API contracts.
AsteraEvent: base model for all domain events published to the Event Bus.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AsteraModel(BaseModel):
    """
    Base Pydantic model for all Astera DTOs and API contracts.

    Provides:
        - Strict mode (no extra fields silently accepted)
        - Immutability by default
        - JSON serialization helpers
    """

    model_config = {
        "frozen": True,             # Immutable by default
        "extra": "forbid",          # No silent extra fields
        "populate_by_name": True,   # Allow alias or field name
        "use_enum_values": True,    # Enums serialize to their .value
    }


class AsteraEvent(BaseModel):
    """
    Base model for all domain events published to the Event Bus (NATS).

    Every event has:
        event_id  — globally unique identifier
        event_type — the subject/topic name (e.g., 'kernel.ready')
        version   — event schema version for compatibility
        timestamp — when the event was created (UTC)
        source    — which platform component emitted the event

    Usage:
        class KernelReadyEvent(AsteraEvent):
            event_type: str = "kernel.ready"
            boot_time_ms: float

        event = KernelReadyEvent(source="astera-kernel", boot_time_ms=250.3)
        await event_bus.publish("astera.kernel.ready", event.model_dump_json().encode())
    """

    model_config = {
        "frozen": True,
        "extra": "forbid",
        "use_enum_values": True,
    }

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally unique event identifier (UUID v4).",
    )
    event_type: str = Field(
        description="Event type / NATS subject. Example: 'kernel.ready'.",
    )
    version: str = Field(
        default="1.0",
        description="Event schema version for forward compatibility.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="Event creation timestamp (UTC).",
    )
    source: str = Field(
        description="Platform component that emitted this event. Example: 'astera-kernel'.",
    )
