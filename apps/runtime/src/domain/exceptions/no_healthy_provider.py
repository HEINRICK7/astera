"""NoHealthyProviderError — raised when all registered providers are unhealthy."""
from __future__ import annotations

from typing import TYPE_CHECKING

from apps.runtime.src.domain.exceptions.base import AsteraError
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType

if TYPE_CHECKING:
    from apps.runtime.src.domain.value_objects.selection_criteria import SelectionCriteria


class NoHealthyProviderError(AsteraError):
    """
    Raised when CapabilityRegistry.select_best() finds no provider that
    satisfies the given SelectionCriteria and is in HEALTHY status.
    """

    def __init__(
        self,
        capability_type: CapabilityType,
        criteria: "SelectionCriteria | None" = None,
    ) -> None:
        detail = f"No healthy provider for capability '{capability_type.value}'"
        if criteria and not criteria.is_empty():
            detail += " with the requested criteria."
        super().__init__(detail, code="NO_HEALTHY_PROVIDER")
        self.capability_type = capability_type
        self.criteria = criteria
