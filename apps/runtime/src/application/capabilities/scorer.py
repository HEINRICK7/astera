"""
CapabilityScorer — scoring engine for Provider selection.

WHY separated from CapabilityRegistry:
    CapabilityRegistry manages the index (register, unregister, query).
    CapabilityScorer makes the selection decision (score, compare).
    Single Responsibility: the registry does not know how to score.
    The scoring algorithm can evolve independently (A/B testing, ML weights).
"""
from __future__ import annotations

from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor
from apps.runtime.src.domain.value_objects.health_status import HealthStatus
from apps.runtime.src.domain.value_objects.selection_criteria import SelectionCriteria

# Score weights — changing these changes the Kernel's provider selection behavior.
# WHY constants: makes the scoring policy explicit and easy to tune.
_LANGUAGE_MATCH        = 30.0
_LANGUAGE_MISMATCH     = -100.0  # Hard disqualifier
_STREAMING_MATCH       = 20.0
_STREAMING_MISMATCH    = -100.0  # Hard disqualifier
_LATENCY_WITHIN_BUDGET = 15.0
_LATENCY_OVER_BUDGET   = -30.0
_ACCURACY_ABOVE_MIN    = 15.0
_ACCURACY_BELOW_MIN    = -30.0
_CONFIDENCE_MATCH      = 10.0
_CONFIDENCE_MISMATCH   = -20.0
_GPU_SOFT_BONUS        = 5.0
_CPU_OVER_GPU_PENALTY  = -20.0
_HEALTH_BONUS          = 10.0


class CapabilityScorer:
    """
    Stateless scoring engine.

    Computes a float score for a CapabilityDescriptor against SelectionCriteria.
    Positive = good fit. Negative = disqualified (hard penalty).
    Higher score wins in select_best().
    """

    def score(
        self,
        descriptor: CapabilityDescriptor,
        criteria: SelectionCriteria,
    ) -> float:
        """Return a selection score. Call for each candidate; pick the highest."""
        score = 0.0
        score += self._language_score(descriptor, criteria)
        score += self._streaming_score(descriptor, criteria)
        score += self._latency_score(descriptor, criteria)
        score += self._accuracy_score(descriptor, criteria)
        score += self._confidence_score(descriptor, criteria)
        score += self._hardware_score(descriptor, criteria)
        score += self._health_score(descriptor)
        return score

    @staticmethod
    def _language_score(d: CapabilityDescriptor, c: SelectionCriteria) -> float:
        if not c.language:
            return 0.0
        if d.supports_language(c.language):
            return _LANGUAGE_MATCH
        if d.supported_languages:
            return _LANGUAGE_MISMATCH  # Has restrictions but not the one we need
        return 0.0

    @staticmethod
    def _streaming_score(d: CapabilityDescriptor, c: SelectionCriteria) -> float:
        if not c.requires_streaming:
            return 0.0
        return _STREAMING_MATCH if d.supports_streaming else _STREAMING_MISMATCH

    @staticmethod
    def _latency_score(d: CapabilityDescriptor, c: SelectionCriteria) -> float:
        if c.max_latency_ms is None or d.avg_latency_ms is None:
            return 0.0
        return (
            _LATENCY_WITHIN_BUDGET
            if d.avg_latency_ms <= c.max_latency_ms
            else _LATENCY_OVER_BUDGET
        )

    @staticmethod
    def _accuracy_score(d: CapabilityDescriptor, c: SelectionCriteria) -> float:
        if c.min_accuracy_score is None or d.accuracy_score is None:
            return 0.0
        return (
            _ACCURACY_ABOVE_MIN
            if d.accuracy_score >= c.min_accuracy_score
            else _ACCURACY_BELOW_MIN
        )

    @staticmethod
    def _confidence_score(d: CapabilityDescriptor, c: SelectionCriteria) -> float:
        if not c.requires_confidence_output:
            return 0.0
        return _CONFIDENCE_MATCH if d.confidence_output else _CONFIDENCE_MISMATCH

    @staticmethod
    def _hardware_score(d: CapabilityDescriptor, c: SelectionCriteria) -> float:
        if c.prefer_gpu:
            return _GPU_SOFT_BONUS
        if c.prefer_cpu and d.requires_gpu:
            return _CPU_OVER_GPU_PENALTY
        return 0.0

    @staticmethod
    def _health_score(d: CapabilityDescriptor) -> float:
        return _HEALTH_BONUS if d.status == HealthStatus.HEALTHY else 0.0
