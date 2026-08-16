"""SelectionCriteria — declarative constraints for select_best()."""
from __future__ import annotations

from dataclasses import dataclass

from apps.runtime.src.domain.value_objects.base import AsteraValueObject


@dataclass(frozen=True)
class SelectionCriteria(AsteraValueObject):
    """
    Declarative constraints for CapabilityRegistry.select_best().

    The caller declares WHAT they need.
    The Registry decides WHO delivers it.
    The caller NEVER names a Provider or Plugin.

    Example:
        criteria = SelectionCriteria(
            language="pt-BR",
            requires_streaming=True,
            prefer_cpu=True,
            max_latency_ms=200.0,
        )
        descriptor = capability_registry.select_best(
            CapabilityType.SPEECH_TRANSCRIPTION,
            criteria,
        )
    """

    language: str | None = None
    requires_streaming: bool = False
    prefer_gpu: bool = False
    prefer_cpu: bool = False
    max_latency_ms: float | None = None
    min_accuracy_score: float | None = None   # 0.0 – 1.0
    requires_confidence_output: bool = False

    def is_empty(self) -> bool:
        """True when no constraints are set — any healthy provider qualifies."""
        return not any([
            self.language,
            self.requires_streaming,
            self.prefer_gpu,
            self.prefer_cpu,
            self.max_latency_ms,
            self.min_accuracy_score,
            self.requires_confidence_output,
        ])
