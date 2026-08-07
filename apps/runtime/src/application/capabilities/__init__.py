"""
Astera Kernel — Capability Registry.

The CapabilityRegistry is the intelligence layer between the Kernel and Providers.

The Kernel says:   "I need SPEECH_TRANSCRIPTION in pt-BR with streaming."
The Registry says: "The best provider is Parakeet (score 85.0). Here is its descriptor."

select_best() scoring model:
    Language match          → +30 pts  (hard penalty: -100 if required + no match)
    Streaming match         → +20 pts  (hard penalty: -100 if required + no support)
    Latency within budget   → +15 pts  (penalty: -30 if over budget)
    Accuracy above minimum  → +15 pts  (penalty: -30 if below minimum)
    Confidence output       → +10 pts
    Healthy status          → +10 pts  (dead providers are never selected)
    GPU preference match    → +5 pts   (penalty: -20 if prefer_cpu + provider needs GPU)

The winner is always the descriptor with the highest score.
Ties are broken by accuracy_score, then by avg_latency_ms (lower = better).
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from apps.runtime.src.domain.entities import CapabilityDescriptor
from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    HealthStatus,
    PluginName,
    ProviderName,
    SelectionCriteria,
)
from apps.runtime.src.domain.exceptions import (
    CapabilityNotFoundError,
    NoHealthyProviderError,
)

logger = logging.getLogger("astera.capability_registry")


class CapabilityRegistry:
    """
    Index of all registered capabilities in the platform.

    Data structure:
        _index[CapabilityType] → list[CapabilityDescriptor]

    The Kernel calls:
        registry.register(descriptor)
        registry.select_best(CapabilityType.SPEECH_TRANSCRIPTION, criteria)
        registry.list_for(CapabilityType.SPEECH_TRANSCRIPTION)
        registry.unregister_plugin(plugin_name)
        registry.summary()
    """

    def __init__(self) -> None:
        self._index: dict[CapabilityType, list[CapabilityDescriptor]] = defaultdict(list)

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, descriptor: CapabilityDescriptor) -> None:
        """
        Register a CapabilityDescriptor into the index.

        If a descriptor for the same (capability_type, provider) already exists,
        it is replaced (idempotent re-registration).
        """
        existing = self._index[descriptor.capability_type]

        # Remove stale entry for same provider (re-register is idempotent)
        self._index[descriptor.capability_type] = [
            d for d in existing if d.provider != descriptor.provider
        ]
        descriptor.status = HealthStatus.HEALTHY
        self._index[descriptor.capability_type].append(descriptor)

        logger.info(
            "Capability registered",
            extra={
                "capability": descriptor.capability_type.value,
                "provider":   str(descriptor.provider),
                "plugin":     str(descriptor.plugin),
                "version":    str(descriptor.version),
            },
        )

    def unregister_plugin(self, plugin: PluginName) -> int:
        """
        Remove ALL descriptors belonging to a given Plugin.

        Called during graceful shutdown when a plugin is stopped.
        Returns the number of descriptors removed.
        """
        removed = 0
        for cap_type in list(self._index.keys()):
            before = len(self._index[cap_type])
            self._index[cap_type] = [
                d for d in self._index[cap_type] if d.plugin != plugin
            ]
            removed += before - len(self._index[cap_type])

        if removed:
            logger.info(
                "Capabilities unregistered",
                extra={"plugin": str(plugin), "removed": removed},
            )
        return removed

    def unregister_provider(self, provider: ProviderName) -> int:
        """Remove ALL descriptors belonging to a given Provider."""
        removed = 0
        for cap_type in list(self._index.keys()):
            before = len(self._index[cap_type])
            self._index[cap_type] = [
                d for d in self._index[cap_type] if d.provider != provider
            ]
            removed += before - len(self._index[cap_type])
        return removed

    # ── Selection ─────────────────────────────────────────────────────────────

    def select_best(
        self,
        capability_type: CapabilityType,
        criteria: SelectionCriteria | None = None,
    ) -> CapabilityDescriptor:
        """
        Select the best Provider for the given capability type and criteria.

        The caller NEVER names a Provider. The Registry decides.

        Args:
            capability_type: What the platform needs to do.
            criteria: Declarative constraints (language, streaming, latency…).
                      If None, any healthy provider qualifies.

        Returns:
            The CapabilityDescriptor with the highest score.

        Raises:
            CapabilityNotFoundError: No descriptor registered for this type.
            NoHealthyProviderError:  All registered providers are unhealthy.
        """
        descriptors = self._index.get(capability_type, [])
        if not descriptors:
            raise CapabilityNotFoundError(capability_type)

        healthy = [d for d in descriptors if d.is_available()]
        if not healthy:
            raise NoHealthyProviderError(capability_type)

        if criteria is None or criteria.is_empty():
            # No constraints: return the one with the best accuracy (or first)
            return max(
                healthy,
                key=lambda d: (d.accuracy_score or 0.0, -(d.avg_latency_ms or 9999)),
            )

        # Score all healthy candidates
        scored = [
            (d, self._score(d, criteria))
            for d in healthy
        ]
        # Hard penalties result in negative scores — filter those out
        viable = [(d, s) for d, s in scored if s > -50]

        if not viable:
            raise NoHealthyProviderError(capability_type, criteria=criteria)

        # Winner: highest score; ties broken by accuracy desc, latency asc
        best_descriptor, best_score = max(
            viable,
            key=lambda ds: (ds[1], ds[0].accuracy_score or 0.0, -(ds[0].avg_latency_ms or 9999)),
        )

        logger.debug(
            "Provider selected",
            extra={
                "capability": capability_type.value,
                "provider":   str(best_descriptor.provider),
                "score":      best_score,
            },
        )
        return best_descriptor

    # ── Queries ───────────────────────────────────────────────────────────────

    def has_capability(self, capability_type: CapabilityType) -> bool:
        """True if at least one healthy provider exists for this type."""
        return any(
            d.is_available()
            for d in self._index.get(capability_type, [])
        )

    def list_for(self, capability_type: CapabilityType) -> list[CapabilityDescriptor]:
        """Return all descriptors for a given capability type (healthy or not)."""
        return list(self._index.get(capability_type, []))

    def list_all(self) -> list[CapabilityDescriptor]:
        """Return every registered descriptor in the registry."""
        return [d for descriptors in self._index.values() for d in descriptors]

    def query(
        self,
        *,
        language: str | None = None,
        requires_streaming: bool = False,
        requires_cpu: bool = False,
        requires_confidence: bool = False,
    ) -> list[CapabilityDescriptor]:
        """
        ADK query interface: "Give me all capabilities that support pt-BR + streaming."

        The ADK calls this to discover what the platform can do before
        composing a workflow.
        """
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
        """Compact summary for health reports and /status endpoint."""
        all_descriptors = self.list_all()
        return {
            "total":         len(all_descriptors),
            "healthy":       sum(1 for d in all_descriptors if d.is_available()),
            "capabilities":  {
                cap_type.value: {
                    "providers": [str(d.provider) for d in descriptors],
                    "healthy":   sum(1 for d in descriptors if d.is_available()),
                }
                for cap_type, descriptors in self._index.items()
                if descriptors
            },
        }

    # ── Scoring Engine ────────────────────────────────────────────────────────

    @staticmethod
    def _score(descriptor: CapabilityDescriptor, criteria: SelectionCriteria) -> float:
        """
        Compute a selection score for a CapabilityDescriptor against SelectionCriteria.

        Positive = good fit. Negative = disqualified (hard penalty).
        The descriptor with the highest score wins in select_best().
        """
        score = 0.0

        # ── Language ──────────────────────────────────────────────────────────
        if criteria.language:
            if descriptor.supports_language(criteria.language):
                score += 30.0
            elif descriptor.supported_languages:
                # Provider has language restrictions but does NOT support the requested one
                score -= 100.0  # Hard disqualifier

        # ── Streaming ─────────────────────────────────────────────────────────
        if criteria.requires_streaming:
            if descriptor.supports_streaming:
                score += 20.0
            else:
                score -= 100.0  # Hard disqualifier — streaming is mandatory

        # ── Latency budget ────────────────────────────────────────────────────
        if criteria.max_latency_ms is not None and descriptor.avg_latency_ms is not None:
            if descriptor.avg_latency_ms <= criteria.max_latency_ms:
                score += 15.0
            else:
                score -= 30.0

        # ── Accuracy floor ────────────────────────────────────────────────────
        if criteria.min_accuracy_score is not None and descriptor.accuracy_score is not None:
            if descriptor.accuracy_score >= criteria.min_accuracy_score:
                score += 15.0
            else:
                score -= 30.0

        # ── Confidence output ─────────────────────────────────────────────────
        if criteria.requires_confidence_output:
            if descriptor.confidence_output:
                score += 10.0
            else:
                score -= 20.0

        # ── Hardware preference ───────────────────────────────────────────────
        if criteria.prefer_gpu and not descriptor.requires_gpu:
            score += 5.0  # Soft preference — GPU providers get a bonus
        if criteria.prefer_cpu and descriptor.requires_gpu:
            score -= 20.0  # CPU-only request: GPU provider is suboptimal

        # ── Health bonus ──────────────────────────────────────────────────────
        if descriptor.status == HealthStatus.HEALTHY:
            score += 10.0

        return score
