"""
Astera Runtime — Domain Value Objects.

Value objects are immutable and identity-free.
Equality is determined by value, not reference.

RuntimeState is the authoritative source of truth for the Kernel's lifecycle.
Every observability component (Grafana, Langfuse, Health) reads from it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ── Base ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AsteraValueObject:
    """Base class for all Astera value objects. Immutable by design."""


# ── Runtime State (Kernel State Machine) ──────────────────────────────────────

class RuntimeState(str, Enum):
    """
    Authoritative state machine for the Astera Kernel.

    Transitions:
        BOOTING → READY
        BOOTING → FAILED          (startup error)
        READY   → DEGRADED        (component becomes unhealthy)
        READY   → STOPPING        (graceful shutdown signal)
        DEGRADED → READY          (component recovered)
        DEGRADED → STOPPING       (graceful shutdown signal)
        STOPPING → STOPPED
        STOPPING → FAILED         (shutdown error)

    Grafana, Langfuse, and Health endpoints all observe this state.
    """

    BOOTING  = "booting"   # Kernel is executing the bootstrap sequence
    READY    = "ready"     # Kernel is fully operational — accepts all traffic
    DEGRADED = "degraded"  # Kernel is running but some component is unhealthy
    STOPPING = "stopping"  # Kernel received shutdown signal — draining
    STOPPED  = "stopped"   # Kernel has stopped cleanly
    FAILED   = "failed"    # Kernel encountered an unrecoverable error

    # ── Predicates ────────────────────────────────────────────────────────────

    def is_operational(self) -> bool:
        """True when the Kernel can accept platform requests."""
        return self in {RuntimeState.READY, RuntimeState.DEGRADED}

    def is_healthy(self) -> bool:
        """True only when fully healthy (no degraded components)."""
        return self == RuntimeState.READY

    def is_terminal(self) -> bool:
        """True when the Kernel will not transition further."""
        return self in {RuntimeState.STOPPED, RuntimeState.FAILED}

    def is_shutting_down(self) -> bool:
        return self in {RuntimeState.STOPPING, RuntimeState.STOPPED}

    def can_accept_plugins(self) -> bool:
        """True when the Plugin Registry can accept new registrations."""
        return self in {RuntimeState.BOOTING, RuntimeState.READY, RuntimeState.DEGRADED}


# ── Health Status ─────────────────────────────────────────────────────────────

class HealthStatus(str, Enum):
    """Health status for any individual component in the platform."""

    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN   = "unknown"

    def is_ok(self) -> bool:
        return self == HealthStatus.HEALTHY


# ── Capability Types ──────────────────────────────────────────────────────────

class CapabilityType(str, Enum):
    """
    Catalogue of known Capability types in the Astera platform.

    A Plugin offers one or more Capabilities from this catalogue.
    The CapabilityRegistry indexes plugins by CapabilityType.

    Example:
        SpeechPlugin registers:
            - CapabilityType.SPEECH_TRANSCRIPTION
            - CapabilityType.SPEECH_STREAMING
            - CapabilityType.SPEECH_DIARIZATION
            - CapabilityType.SPEECH_LANGUAGE_DETECTION
    """

    # Speech
    SPEECH_TRANSCRIPTION       = "speech.transcription"
    SPEECH_STREAMING           = "speech.streaming"
    SPEECH_DIARIZATION         = "speech.diarization"
    SPEECH_LANGUAGE_DETECTION  = "speech.language_detection"

    # Vision
    VISION_OCR                 = "vision.ocr"
    VISION_CLASSIFICATION      = "vision.classification"

    # NLP
    NLP_ENTITY_EXTRACTION      = "nlp.entity_extraction"
    NLP_SUMMARIZATION          = "nlp.summarization"
    NLP_CLASSIFICATION         = "nlp.classification"

    # Medical (Phase E)
    MEDICAL_SOAP_GENERATION    = "medical.soap_generation"
    MEDICAL_ICD_CODING         = "medical.icd_coding"
    MEDICAL_DRUG_INTERACTION   = "medical.drug_interaction"
    MEDICAL_TERMINOLOGY        = "medical.terminology"

    # Platform
    PLATFORM_ECHO              = "platform.echo"   # Used for integration testing


# ── Plugin Identity ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PluginName(AsteraValueObject):
    """
    Unique identifier for a plugin.
    Allowed: lowercase letters, digits, hyphens.
    Example: 'echo-plugin', 'speech-v1'.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("PluginName cannot be empty.")
        if not all(c.isalnum() or c == "-" for c in self.value):
            raise ValueError(
                f"PluginName '{self.value}' must contain only lowercase letters, digits, and hyphens."
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PluginVersion(AsteraValueObject):
    """Semantic version (MAJOR.MINOR.PATCH) for a Plugin or Capability."""

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version: str) -> PluginVersion:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version: '{version}'. Expected MAJOR.MINOR.PATCH.")
        try:
            return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))
        except ValueError:
            raise ValueError(f"Version components must be integers. Got: '{version}'.")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
