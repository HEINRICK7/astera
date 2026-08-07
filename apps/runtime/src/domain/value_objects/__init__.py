"""
Astera Kernel — Domain Value Objects.

Value objects are immutable and identity-free.

Key additions in this revision:
    - ProviderName: typed identity for a Capability provider (Parakeet, Whisper, Azure…)
    - SelectionCriteria: declarative constraints passed to select_best()
      The Kernel selects the best Provider without the caller naming any Provider.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


# ── Base ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AsteraValueObject:
    """Base class for all Astera value objects. Immutable by design."""


# ── Runtime State (Kernel State Machine) ──────────────────────────────────────

class RuntimeState(str, Enum):
    """
    Authoritative state machine for the AsteraKernel.

    Transitions:
        BOOTING  → READY    (bootstrap complete)
        BOOTING  → FAILED   (startup error)
        READY    → DEGRADED (component unhealthy)
        READY    → STOPPING (SIGTERM)
        DEGRADED → READY    (component recovered)
        DEGRADED → STOPPING (SIGTERM)
        STOPPING → STOPPED
        STOPPING → FAILED   (shutdown error)

    Every observability component reads this state:
    Grafana · Langfuse · Kubernetes probes · Health endpoints
    """

    BOOTING  = "booting"
    READY    = "ready"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED  = "stopped"
    FAILED   = "failed"

    def is_operational(self) -> bool:
        return self in {RuntimeState.READY, RuntimeState.DEGRADED}

    def is_healthy(self) -> bool:
        return self == RuntimeState.READY

    def is_terminal(self) -> bool:
        return self in {RuntimeState.STOPPED, RuntimeState.FAILED}

    def is_shutting_down(self) -> bool:
        return self in {RuntimeState.STOPPING, RuntimeState.STOPPED}

    def can_accept_plugins(self) -> bool:
        return self in {RuntimeState.BOOTING, RuntimeState.READY, RuntimeState.DEGRADED}


# ── Health Status ─────────────────────────────────────────────────────────────

class HealthStatus(str, Enum):
    """Health status for any platform component or provider."""

    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN   = "unknown"

    def is_ok(self) -> bool:
        return self == HealthStatus.HEALTHY


# ── Capability Types ──────────────────────────────────────────────────────────

class CapabilityType(str, Enum):
    """
    Catalogue of all Capability types in the platform.

    The Kernel thinks in CapabilityTypes, never in Providers or Plugins.
    When it needs speech transcription, it asks:
        capability_registry.select_best(CapabilityType.SPEECH_TRANSCRIPTION, criteria)
    """

    # Speech
    SPEECH_TRANSCRIPTION      = "speech.transcription"
    SPEECH_STREAMING          = "speech.streaming"
    SPEECH_DIARIZATION        = "speech.diarization"
    SPEECH_LANGUAGE_DETECTION = "speech.language_detection"

    # Vision
    VISION_OCR                = "vision.ocr"
    VISION_CLASSIFICATION     = "vision.classification"

    # NLP
    NLP_ENTITY_EXTRACTION     = "nlp.entity_extraction"
    NLP_SUMMARIZATION         = "nlp.summarization"
    NLP_CLASSIFICATION        = "nlp.classification"

    # Medical (Phase E+)
    MEDICAL_SOAP_GENERATION   = "medical.soap_generation"
    MEDICAL_ICD_CODING        = "medical.icd_coding"
    MEDICAL_DRUG_INTERACTION  = "medical.drug_interaction"
    MEDICAL_TERMINOLOGY       = "medical.terminology"

    # Platform internal
    PLATFORM_ECHO             = "platform.echo"


# ── Provider & Plugin Identity ────────────────────────────────────────────────

@dataclass(frozen=True)
class ProviderName(AsteraValueObject):
    """
    Typed identity for a Capability provider.

    A Provider is the concrete implementation (Parakeet, Whisper, Azure Speech).
    Multiple Providers can implement the same CapabilityType.

    Examples: 'parakeet', 'whisper-large-v3', 'azure-speech', 'deepgram-nova'
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ProviderName cannot be empty.")
        if not all(c.isalnum() or c in "-_." for c in self.value):
            raise ValueError(
                f"ProviderName '{self.value}' must contain only letters, digits, hyphens, underscores, or dots."
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PluginName(AsteraValueObject):
    """
    Typed identity for a Plugin.

    A Plugin HOSTS one or more Providers.
    Example: 'speech-plugin' hosts providers Parakeet and Whisper.
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
    """Semantic version (MAJOR.MINOR.PATCH)."""

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


# ── Selection Criteria ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SelectionCriteria(AsteraValueObject):
    """
    Declarative constraints for select_best() in the CapabilityRegistry.

    The caller declares WHAT they need. The Kernel picks WHO delivers it.
    The caller NEVER names a Provider or Plugin.

    Example:
        criteria = SelectionCriteria(
            language="pt-BR",
            requires_streaming=True,
            prefer_cpu=True,
            max_latency_ms=200.0,
        )
        descriptor = capability_registry.select_best(
            CapabilityType.SPEECH_TRANSCRIPTION,
            criteria,
        )
    """

    language: str | None = None               # e.g. "pt-BR", "en-US"
    requires_streaming: bool = False
    prefer_gpu: bool = False
    prefer_cpu: bool = False
    max_latency_ms: float | None = None
    min_accuracy_score: float | None = None   # 0.0 – 1.0
    requires_confidence_output: bool = False

    def is_empty(self) -> bool:
        """True when no constraints are set — any healthy provider qualifies."""
        return not any([
            self.language,
            self.requires_streaming,
            self.prefer_gpu,
            self.prefer_cpu,
            self.max_latency_ms,
            self.min_accuracy_score,
            self.requires_confidence_output,
        ])
