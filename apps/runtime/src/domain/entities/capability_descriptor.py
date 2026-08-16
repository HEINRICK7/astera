"""CapabilityDescriptor — rich advertisement of what a Provider can do."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.health_status import HealthStatus
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.plugin_version import PluginVersion
from apps.runtime.src.domain.value_objects.provider_name import ProviderName


@dataclass
class CapabilityDescriptor:
    """
    The rich advertisement of what a specific Provider can do.

    Plugins register this into the CapabilityRegistry.
    The Kernel uses this metadata to run select_best() automatically.

    WHY metadata fields matter:
        supported_languages → Kernel picks Portuguese-capable providers
        supports_streaming  → real-time vs. batch selection
        requires_gpu        → skip on CPU-only deployment nodes
        avg_latency_ms      → latency-budget enforcement
        accuracy_score      → minimum accuracy enforcement
        confidence_output   → Kernel can filter for confidence-aware results
    """

    capability_type: CapabilityType
    provider: ProviderName
    plugin: PluginName
    version: PluginVersion

    supported_languages: list[str] = field(default_factory=list)
    supports_streaming: bool = False
    requires_gpu: bool = False
    avg_latency_ms: float | None = None
    accuracy_score: float | None = None       # 0.0 – 1.0
    confidence_output: bool = False
    extra_metadata: dict[str, Any] = field(default_factory=dict)

    # Set by Kernel at registration time, not by the Plugin
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
