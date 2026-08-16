"""Stable internal Clinical Runtime module boundaries.

These modules are in-process bounded contexts.  They are not repositories and
are not public contracts; they provide narrow seams for the Runtime
orchestrator and can later become independent components if ownership or
deployment requires it.
"""

from .context import ClinicalContextModule
from .correlation import ClinicalCorrelationModule
from .facts import ClinicalFactsModule
from .ingestion import CanonicalIngestionModule
from .knowledge import ClinicalKnowledgeModule
from .observations import ClinicalObservationModule
from .publication import ClinicalPublicationModule
from .projections import ClinicalProjectionModule
from .processing import ClinicalProcessingModule
from .representation import ClinicalRepresentationModule
from .research import ClinicalResearchModule

__all__ = [
    "CanonicalIngestionModule",
    "ClinicalContextModule",
    "ClinicalCorrelationModule",
    "ClinicalFactsModule",
    "ClinicalKnowledgeModule",
    "ClinicalObservationModule",
    "ClinicalPublicationModule",
    "ClinicalProjectionModule",
    "ClinicalProcessingModule",
    "ClinicalRepresentationModule",
    "ClinicalResearchModule",
]
