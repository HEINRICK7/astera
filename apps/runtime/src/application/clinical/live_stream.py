"""Compatibility facade for the Clinical Runtime public entry point."""
from __future__ import annotations

from collections.abc import AsyncIterator

from packages.clinical_context_sdk import ClinicalContextBuilder
from packages.clinical_facts_sdk import ClinicalFactsExtractor
from packages.medical_nlp_sdk import MedicalNlpProcessor
from packages.representation_sdk import RepresentationEngine
from packages.reasoning_sdk import ClinicalReasoner
from packages.contracts.transcription import TranscriptEvent

from apps.runtime.src.ports.inbound.evidence import EvidenceIngressPort
from apps.runtime.src.ports.outbound.persistence import ReviewRepositoryPort
from apps.runtime.src.ports.outbound.streaming import StreamBrokerPort

from .normalization import ClinicalNormalizationLayer
from .orchestrator import ClinicalOrchestrator
from .runtime_session import ConversationMemory


class LiveClinicalPipeline:
    """Stable API facade; execution belongs to ``ClinicalOrchestrator``."""

    def __init__(
        self,
        *,
        broker: StreamBrokerPort,
        nlp_processor: MedicalNlpProcessor,
        facts_extractor: ClinicalFactsExtractor,
        context_builder: ClinicalContextBuilder,
        reasoner: ClinicalReasoner,
        representation_engine: RepresentationEngine,
        review_store: ReviewRepositoryPort,
        normalization_layer: ClinicalNormalizationLayer | None = None,
    ) -> None:
        self._orchestrator = ClinicalOrchestrator(
            broker=broker,
            nlp_processor=nlp_processor,
            facts_extractor=facts_extractor,
            context_builder=context_builder,
            reasoner=reasoner,
            representation_engine=representation_engine,
            review_store=review_store,
            normalization_layer=normalization_layer,
        )

    @property
    def review_store(self) -> ReviewRepositoryPort:
        return self._orchestrator.review_store

    def evidence_ingress_for(self, stream_id: str) -> EvidenceIngressPort:
        return self._orchestrator.evidence_ingress_for(stream_id)

    async def run_canonical_events(
        self,
        *,
        stream_id: str,
        encounter_id: str,
        patient_id: str,
        language: str,
        events: AsyncIterator[TranscriptEvent],
    ) -> None:
        await self._orchestrator.run_canonical_events(
            stream_id=stream_id,
            encounter_id=encounter_id,
            patient_id=patient_id,
            language=language,
            events=events,
        )

    async def run(
        self,
        *,
        stream_id: str,
        encounter_id: str,
        patient_id: str,
        language: str,
        canonical_events: AsyncIterator[TranscriptEvent],
    ) -> None:
        await self._orchestrator.run(
            stream_id=stream_id,
            encounter_id=encounter_id,
            patient_id=patient_id,
            language=language,
            canonical_events=canonical_events,
        )


__all__ = ["ConversationMemory", "LiveClinicalPipeline"]
