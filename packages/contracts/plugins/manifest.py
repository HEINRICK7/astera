"""Versioned plugin manifest contract."""
from __future__ import annotations

from dataclasses import dataclass

from .types import CapabilityType, PluginName, PluginVersion


@dataclass(frozen=True)
class PluginManifest:
    """Metadata that can be exchanged without importing the Runtime."""

    name: PluginName
    version: PluginVersion
    description: str
    capabilities: tuple[CapabilityType, ...] = ()

    def to_summary(self) -> dict[str, object]:
        return {
            "name": str(self.name),
            "version": str(self.version),
            "description": self.description,
            "capabilities": [capability.value for capability in self.capabilities],
        }
