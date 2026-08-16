"""
CapabilityRegistry — index of all registered capabilities in the platform.

WHY separated from CapabilityScorer:
    Registry manages the data structure (register, unregister, query).
    Scorer makes the decision (score, compare, select).
    Registry does not know HOW to score. It delegates to Scorer.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from apps.runtime.src.application.capabilities.scorer import CapabilityScorer
from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.health_status import HealthStatus
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.provider_name import ProviderName
from apps.runtime.src.domain.value_objects.selection_criteria import SelectionCriteria
from apps.runtime.src.domain.exceptions.capability_not_found import CapabilityNotFoundError
from apps.runtime.src.domain.exceptions.no_healthy_provider import NoHealthyProviderError

logger = logging.getLogger("astera.capability_registry")

_HARD_PENALTY_THRESHOLD = -50.0


class CapabilityRegistry:
    """
    Index: CapabilityType → list[CapabilityDescriptor].
    Delegates scoring to CapabilityScorer.
    """

    def __init__(self) -> None:
        self._index: dict[CapabilityType, list[CapabilityDescriptor]] = defaultdict(list)
        self._scorer = CapabilityScorer()

    def register(self, descriptor: CapabilityDescriptor) -> None:
        """Register a CapabilityDescriptor. Idempotent by (type, provider)."""
        self._index[descriptor.capability_type] = [
            d for d in self._index[descriptor.capability_type]
            if d.provider != descriptor.provider
        ]
        descriptor.status = HealthStatus.HEALTHY
        self._index[descriptor.capability_type].append(descriptor)
        logger.info("Capability registered", extra={
            "capability": descriptor.capability_type.value,
            "provider":   str(descriptor.provider),
            "plugin":     str(descriptor.plugin),
        })

    def unregister_plugin(self, plugin: PluginName) -> int:
        """Remove all descriptors for a plugin. Returns count removed."""
        removed = 0
        for cap_type in list(self._index):
            before = len(self._index[cap_type])
            self._index[cap_type] = [
                d for d in self._index[cap_type] if d.plugin != plugin
            ]
            removed += before - len(self._index[cap_type])
        return removed

    def unregister_provider(self, provider: ProviderName) -> int:
        """Remove all descriptors for a provider. Returns count removed."""
        removed = 0
        for cap_type in list(self._index):
            before = len(self._index[cap_type])
            self._index[cap_type] = [
                d for d in self._index[cap_type] if d.provider != provider
            ]
            removed += before - len(self._index[cap_type])
        return removed

    def select_best(
        self,
        capability_type: CapabilityType,
        criteria: SelectionCriteria | None = None,
    ) -> CapabilityDescriptor:
        """Select the highest-scoring healthy provider for the given capability."""
        descriptors = self._index.get(capability_type, [])
        if not descriptors:
            raise CapabilityNotFoundError(capability_type)

        healthy = [d for d in descriptors if d.is_available()]
        if not healthy:
            raise NoHealthyProviderError(capability_type)

        if criteria is None or criteria.is_empty():
            return max(healthy, key=lambda d: (d.accuracy_score or 0.0, -(d.avg_latency_ms or 9999)))

        scored = [(d, self._scorer.score(d, criteria)) for d in healthy]
        viable = [(d, s) for d, s in scored if s > _HARD_PENALTY_THRESHOLD]

        if not viable:
            raise NoHealthyProviderError(capability_type, criteria=criteria)

        best, _ = max(viable, key=lambda ds: (
            ds[1], ds[0].accuracy_score or 0.0, -(ds[0].avg_latency_ms or 9999)
        ))
        return best

    def has_capability(self, capability_type: CapabilityType) -> bool:
        return any(d.is_available() for d in self._index.get(capability_type, []))

    def list_for(self, capability_type: CapabilityType) -> list[CapabilityDescriptor]:
        return list(self._index.get(capability_type, []))

    def list_all(self) -> list[CapabilityDescriptor]:
        return [d for descriptors in self._index.values() for d in descriptors]

    def query(
        self,
        *,
        language: str | None = None,
        requires_streaming: bool = False,
        requires_cpu: bool = False,
        requires_confidence: bool = False,
    ) -> list[CapabilityDescriptor]:
        """ADK discovery: 'give me all capabilities that support pt-BR + streaming'."""
        results = self.list_all()
        if language:
            results = [d for d in results if d.supports_language(language)]
        if requires_streaming:
            results = [d for d in results if d.supports_streaming]
        if requires_cpu:
            results = [d for d in results if not d.requires_gpu]
        if requires_confidence:
            results = [d for d in results if d.confidence_output]
        return results

    def summary(self) -> dict[str, Any]:
        all_d = self.list_all()
        return {
            "total":   len(all_d),
            "healthy": sum(1 for d in all_d if d.is_available()),
            "capabilities": {
                cap_type.value: {
                    "providers": [str(d.provider) for d in descs],
                    "healthy":   sum(1 for d in descs if d.is_available()),
                }
                for cap_type, descs in self._index.items() if descs
            },
        }
