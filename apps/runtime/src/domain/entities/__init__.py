"""
Astera Kernel — Domain Entities.

Key Concept: Capability · Provider · Plugin are THREE different things.

    Capability     = WHAT the platform can do  (speech.transcription)
    Provider       = WHO can do it             (Parakeet, Whisper, Azure)
    Plugin         = HOW it is packaged        (speech-plugin-v1)

Relationship:
    CapabilityType     → 1..N CapabilityDescriptors
    CapabilityDescriptor → 1   Provider
    Provider           → 1   Plugin

The Kernel is aware of:
    CapabilityDescriptor — everything it needs to select a Provider
    ContextScope         — the clinical context for the current request

The Kernel is NOT directly aware of:
    Plugins             — the PluginResolver handles that indirection
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.value_objects import (
    AsteraValueObject,
    CapabilityType,
    HealthStatus,
    PluginName,
    PluginVersion,
    ProviderName,
)


# ── CapabilityDescriptor ──────────────────────────────────────────────────────

@dataclass
class CapabilityDescriptor:
    """
    The rich advertisement of what a specific Provider can do.

    This is what plugins register into the CapabilityRegistry.
    The Kernel uses the metadata to run select_best() automatically.

    Example:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
            provider=ProviderName("parakeet"),
            plugin=PluginName("speech-plugin"),
            version=PluginVersion.from_string("1.0.0"),

            # Selection criteria metadata
            supported_languages=["pt-BR", "en-US", "es"],
            supports_streaming=True,
            requires_gpu=False,
            avg_latency_ms=120.0,
            accuracy_score=0.97,
            confidence_output=True,
        )

    Tomorrow:
        descriptor2 = CapabilityDescriptor(
            capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
            provider=ProviderName("whisper-large-v3"),
            ...
            avg_latency_ms=400.0,
            accuracy_score=0.99,
        )
        # Kernel picks the best one automatically based on SelectionCriteria.
    """

    capability_type: CapabilityType
    provider: ProviderName
    plugin: PluginName
    version: PluginVersion

    # ── Metadata for automatic selection ──────────────────────────────────────
    supported_languages: list[str] = field(default_factory=list)
    # e.g. ["pt-BR", "en-US", "es-ES"]

    supports_streaming: bool = False
    # True if this provider can return results incrementally (real-time)

    requires_gpu: bool = False
    # True if provider REQUIRES a GPU. Kernel will skip on CPU-only nodes.

    avg_latency_ms: float | None = None
    # Measured or documented average latency. Used in select_best() scoring.

    accuracy_score: float | None = None
    # 0.0 – 1.0 accuracy benchmark. Used in select_best() scoring.

    confidence_output: bool = False
    # True if provider returns a confidence/probability score per result.

    extra_metadata: dict[str, Any] = field(default_factory=dict)
    # Future-proof bag for domain-specific metadata (e.g., "model_size": "large")

    # ── Runtime state (set by Kernel, not by Plugin) ───────────────────────────
    status: HealthStatus = field(default=HealthStatus.UNKNOWN, compare=False)

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        compare=False,
    )

    def is_available(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def supports_language(self, language: str) -> bool:
        """True if this provider handles the requested language."""
        if not self.supported_languages:
            return True  # No restriction declared → assume universal
        return language in self.supported_languages

    def to_summary(self) -> dict[str, Any]:
        return {
            "capability_type":    self.capability_type.value,
            "provider":           str(self.provider),
            "plugin":             str(self.plugin),
            "version":            str(self.version),
            "status":             self.status.value,
            "supports_streaming": self.supports_streaming,
            "supported_languages": self.supported_languages,
            "requires_gpu":       self.requires_gpu,
            "avg_latency_ms":     self.avg_latency_ms,
            "accuracy_score":     self.accuracy_score,
            "confidence_output":  self.confidence_output,
            "registered_at":      self.registered_at.isoformat(),
        }


# ── Provider ──────────────────────────────────────────────────────────────────

@dataclass
class Provider:
    """
    A Provider is a named implementation that can fulfill one or more capabilities.

    Examples: Parakeet (speech), Whisper (speech+translation), Azure OCR (vision).

    Key rule: A Provider belongs to exactly ONE Plugin.
    A Plugin can host multiple Providers.

    The ProviderRegistry indexes Providers independently from Plugins,
    so the Kernel can query "which providers support pt-BR streaming?"
    without loading any Plugin.
    """

    name: ProviderName
    plugin: PluginName
    status: HealthStatus = HealthStatus.UNKNOWN

    # All descriptors this provider has registered
    capabilities: list[CapabilityDescriptor] = field(default_factory=list)

    started_at: datetime | None = field(default=None, compare=False)

    def is_active(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def supports_capability(self, capability_type: CapabilityType) -> bool:
        return any(d.capability_type == capability_type for d in self.capabilities)

    def get_descriptor(self, capability_type: CapabilityType) -> CapabilityDescriptor | None:
        return next(
            (d for d in self.capabilities if d.capability_type == capability_type),
            None,
        )

    def mark_healthy(self) -> None:
        self.status = HealthStatus.HEALTHY
        self.started_at = datetime.now(tz=timezone.utc)
        for cap in self.capabilities:
            cap.status = HealthStatus.HEALTHY

    def mark_unhealthy(self) -> None:
        self.status = HealthStatus.UNHEALTHY
        for cap in self.capabilities:
            cap.status = HealthStatus.UNHEALTHY

    def to_summary(self) -> dict[str, Any]:
        return {
            "name":         str(self.name),
            "plugin":       str(self.plugin),
            "status":       self.status.value,
            "capabilities": [d.capability_type.value for d in self.capabilities],
            "started_at":   self.started_at.isoformat() if self.started_at else None,
        }


# ── ContextScope ──────────────────────────────────────────────────────────────

@dataclass
class ContextScope:
    """
    The clinical context hierarchy for a single request or session.

    Hierarchy (outer → inner):
        Organization  → the healthcare org (hospital, clinic)
        Workspace     → the unit or department
        Encounter     → the specific patient encounter / appointment
        Patient       → the patient identifier (de-identified where required)
        Session       → the current interaction session

    Every TaskOrchestrator execution receives a ContextScope.
    Every plugin receives it. Every event carries it.
    This enables multi-tenancy and LGPD compliance from Day 1.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str | None = None
    workspace_id: str | None = None
    encounter_id: str | None = None
    patient_id: str | None = None
    session_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def is_clinical(self) -> bool:
        return self.encounter_id is not None or self.patient_id is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id":              self.id,
            "organization_id": self.organization_id,
            "workspace_id":    self.workspace_id,
            "encounter_id":    self.encounter_id,
            "patient_id":      self.patient_id,
            "session_id":      self.session_id,
            "is_clinical":     self.is_clinical(),
        }
