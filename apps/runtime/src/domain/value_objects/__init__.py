"""
Astera Runtime — Domain Value Objects.

Value objects are immutable and have no identity (no ID field).
Equality is determined by value, not by reference.

All value objects inherit from AsteraValueObject.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ── Base ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AsteraValueObject:
    """Base class for all Astera value objects. Immutable by design."""


# ── Runtime State ─────────────────────────────────────────────────────────────

class RuntimeStatus(str, Enum):
    """Represents the lifecycle state of the Astera Runtime."""

    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"

    def is_healthy(self) -> bool:
        return self == RuntimeStatus.RUNNING

    def is_terminal(self) -> bool:
        return self in {RuntimeStatus.STOPPED}

    def can_accept_requests(self) -> bool:
        return self in {RuntimeStatus.RUNNING, RuntimeStatus.DEGRADED}


class HealthStatus(str, Enum):
    """Health status for any component in the platform."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# ── Plugin Identity ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PluginName(AsteraValueObject):
    """
    Unique identifier for a plugin.

    Must follow the pattern: lowercase letters, digits, and hyphens.
    Example: 'echo-plugin', 'speech-v1', 'medical-nlp'.
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
    """
    Semantic version of a plugin.

    Format: MAJOR.MINOR.PATCH (e.g., '1.0.0').
    """

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version: str) -> PluginVersion:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: '{version}'. Expected MAJOR.MINOR.PATCH.")
        try:
            return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))
        except ValueError:
            raise ValueError(f"Version components must be integers. Got: '{version}'.")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
