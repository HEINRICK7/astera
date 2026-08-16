"""Read-only capability catalog exposed to orchestration and ADK discovery."""
from __future__ import annotations

from typing import Any

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry


class CapabilityCatalog:
    """Describe capabilities without exposing provider-specific APIs."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    def list(self) -> list[dict[str, Any]]:
        """Return the available capability names and healthy providers."""
        summary = self._registry.summary()
        return [
            {
                "capability": capability,
                "providers": tuple(data["providers"]),
                "healthy_providers": data["healthy"],
            }
            for capability, data in sorted(summary["capabilities"].items())
        ]

    def contains(self, capability: str) -> bool:
        return any(item["capability"] == capability for item in self.list())
