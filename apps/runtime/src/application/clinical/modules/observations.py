"""Observation extraction and mention lifecycle."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from packages.clinical_facts_sdk import ClinicalMention
from apps.runtime.src.application.clinical.mention_registry import MentionRegistry, RegisteredMention
from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer, NormalizationResult
from apps.runtime.src.application.clinical.transcript_state import ClinicalTranscriptState


class ClinicalObservationModule:
    def __init__(self, normalizer: ClinicalNormalizationLayer) -> None:
        self._normalizer = normalizer
        self._registry = MentionRegistry()

    @property
    def registry(self) -> MentionRegistry:
        return self._registry

    def normalize(
        self,
        state: ClinicalTranscriptState,
        *,
        segment_ids: Iterable[str],
        metadata: Mapping[str, Any],
    ) -> NormalizationResult:
        return self._normalizer.normalize_state(
            state,
            segment_ids=segment_ids,
            metadata=metadata,
        )

    def register(
        self,
        mentions: Iterable[ClinicalMention],
        *,
        encounter_id: str,
        subject_id: str,
    ) -> tuple[RegisteredMention, ...]:
        return tuple(
            self._registry.upsert(mention, encounter_id=encounter_id, subject_id=subject_id)
            for mention in mentions
        )
