"""Clinician-facing projection boundary; no clinical inference lives here."""
from __future__ import annotations

from typing import Any, Mapping

from apps.runtime.src.application.clinical.a2ui_stream import ClinicalA2UIProjector
from apps.runtime.src.application.clinical.presentation_composer import ClinicalPresentationComposer, PresentationModel
from apps.runtime.src.application.clinical.knowledge_layer import KnowledgeProjection


class ClinicalProjectionModule:
    def __init__(self) -> None:
        self.a2ui = ClinicalA2UIProjector()
        self.presentation = ClinicalPresentationComposer()

    def compose(
        self,
        projection: KnowledgeProjection,
        *,
        reasoning: Mapping[str, Any] | None = None,
        soap: Mapping[str, Any] | None = None,
        consultation_complete: bool = False,
    ) -> PresentationModel:
        return self.presentation.compose(
            projection,
            reasoning=reasoning,
            soap=soap,
            consultation_complete=consultation_complete,
        )
