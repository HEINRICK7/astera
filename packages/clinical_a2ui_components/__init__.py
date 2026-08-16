"""Provider-neutral Clinical A2UI component catalog.

The Runtime may declare one of these semantic component names. It must not
choose layout, colors, icons, or a React implementation; those decisions stay
in the client renderer's catalog.
"""
from __future__ import annotations

from typing import Final

CLINICAL_COMPONENT_CATALOG: Final[tuple[str, ...]] = (
    "ObservationCard",
    "SymptomCard",
    "ConditionCard",
    "MedicationCard",
    "AllergyCard",
    "VitalCard",
    "ProcedureCard",
    "ExamCard",
    "QuestionCard",
    "HypothesisCard",
    "EvidenceCard",
    "RelationshipCard",
    "TimelineCard",
    "KnowledgeCard",
    "SummaryCard",
    "SOAPProgressCard",
    "EncounterStatusCard",
    "ClinicalAlertCard",
    "DifferentialDiagnosisCard",
    "ConfidenceIndicator",
    "KnowledgeBadge",
    "ClinicalTag",
    "ClinicalAvatar",
    "StatusIndicator",
)


def component_for_category(category: str) -> str:
    normalized = category.casefold()
    if normalized in {"symptom", "chiefcomplaint"}:
        return "SymptomCard"
    if normalized == "condition":
        return "ConditionCard"
    if normalized == "medication":
        return "MedicationCard"
    if normalized == "allergy":
        return "AllergyCard"
    if normalized in {"vital", "vitalsign", "vital_sign"}:
        return "VitalCard"
    if normalized == "procedure":
        return "ProcedureCard"
    if normalized in {"exam", "lab", "labresult"}:
        return "ExamCard"
    if normalized in {"question", "open_question"}:
        return "QuestionCard"
    if normalized in {"severity", "duration", "location", "intensity"}:
        return "EvidenceCard"
    return "ObservationCard"


__all__ = ["CLINICAL_COMPONENT_CATALOG", "component_for_category"]
