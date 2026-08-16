"""Provider — a named implementation that can fulfill one or more capabilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.health_status import HealthStatus
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.provider_name import ProviderName

if TYPE_CHECKING:
    from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor


@dataclass
class Provider:
    """
    A Provider is a named implementation that fulfills one or more CapabilityTypes.

    WHY separate from Plugin:
        A Plugin packages the code.
        A Provider declares what that code CAN do.
        One Plugin can contain multiple Providers for related capabilities.
        The Kernel queries Providers independently from Plugins.

    WHY separate from CapabilityDescriptor:
        A Provider is an entity with identity (its name).
        A CapabilityDescriptor is the detailed metadata for one specific capability.
        One Provider → many CapabilityDescriptors.
    """

    name: ProviderName
    plugin: PluginName
    status: HealthStatus = HealthStatus.UNKNOWN
    capabilities: list["CapabilityDescriptor"] = field(default_factory=list)
    started_at: datetime | None = field(default=None, compare=False)

    def is_active(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def supports_capability(self, capability_type: CapabilityType) -> bool:
        return any(d.capability_type == capability_type for d in self.capabilities)

    def get_descriptor(self, capability_type: CapabilityType) -> "CapabilityDescriptor | None":
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
