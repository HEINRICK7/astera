"""
Astera Runtime — Domain Entities.

Entities have identity (an ID field) and are mutable over their lifecycle.

Key entities in the Kernel:
    - Capability: a discrete function offered by a Plugin
    - ContextScope: the organizational/clinical context of a session

Rule: Entities belong to the domain. No framework imports here.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    HealthStatus,
    PluginName,
    PluginVersion,
)


# ── Capability Entity ─────────────────────────────────────────────────────────

@dataclass
class Capability:
    """
    A discrete function offered by a Plugin, registered in the Capability Registry.

    Plugin ≠ Capability. One Plugin can offer multiple Capabilities.

    Example — SpeechPlugin offers:
        Capability(type=SPEECH_TRANSCRIPTION, plugin='speech-v1')
        Capability(type=SPEECH_STREAMING,     plugin='speech-v1')
        Capability(type=SPEECH_DIARIZATION,   plugin='speech-v1')

    When the ADK needs speech transcription, it queries the CapabilityRegistry
    for SPEECH_TRANSCRIPTION and gets routed to the correct plugin — without
    knowing the plugin's implementation.
    """

    capability_type: CapabilityType
    plugin_name: PluginName
    version: PluginVersion
    status: HealthStatus = field(default=HealthStatus.UNKNOWN)
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @property
    def id(self) -> str:
        """Composite identity: capability_type + plugin_name."""
        return f"{self.capability_type.value}::{self.plugin_name}"

    def is_available(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def mark_healthy(self) -> None:
        self.status = HealthStatus.HEALTHY

    def mark_unhealthy(self) -> None:
        self.status = HealthStatus.UNHEALTHY

    def mark_degraded(self) -> None:
        self.status = HealthStatus.DEGRADED

    def __repr__(self) -> str:
        return (
            f"Capability(type={self.capability_type.value!r}, "
            f"plugin={self.plugin_name!s}, "
            f"version={self.version!s}, "
            f"status={self.status.value!r})"
        )


# ── Context Scope Entity ──────────────────────────────────────────────────────

@dataclass
class ContextScope:
    """
    The organizational and clinical context of an active session in the Kernel.

    Hierarchy:
        Organization → Workspace → Encounter → Patient → Session

    At Phase C, this entity is intentionally minimal — just the scaffold.
    The ContextManager will populate and manage these scopes.
    The ADK and all Plugins will receive a ContextScope on every invocation.

    This is what makes Astera multi-tenant from the ground up:
    every capability knows WHICH organization, workspace, and patient it is
    serving — without the capability implementation needing to care about
    multi-tenancy at all.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str | None = None
    workspace_id: str | None = None
    encounter_id: str | None = None
    patient_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def system(cls) -> ContextScope:
        """
        Create a system-level context (no patient, no encounter).
        Used for internal Kernel operations and health checks.
        """
        return cls(
            organization_id="__system__",
            workspace_id="__system__",
            metadata={"context_type": "system"},
        )

    def is_clinical(self) -> bool:
        """True when both patient_id and encounter_id are set."""
        return self.patient_id is not None and self.encounter_id is not None

    def is_system(self) -> bool:
        return self.organization_id == "__system__"

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "organization_id": self.organization_id,
            "workspace_id": self.workspace_id,
            "encounter_id": self.encounter_id,
            "patient_id": self.patient_id,
            "user_id": self.user_id,
            "is_clinical": self.is_clinical(),
            "created_at": self.created_at.isoformat(),
        }
