"""CapabilityNotFoundError — raised when no provider is registered for a capability."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType


class CapabilityNotFoundError(AsteraError):
    """Raised when no CapabilityDescriptor exists for the requested type."""

    def __init__(self, capability_type: CapabilityType) -> None:
        super().__init__(
            f"No provider registered for capability '{capability_type.value}'.",
            code="CAPABILITY_NOT_FOUND",
        )
        self.capability_type = capability_type
