"""Thin Clinical Runtime orchestration boundary."""
from __future__ import annotations

from collections.abc import AsyncIterator

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextBuilderPort
from packages.clinical_facts_sdk import ClinicalFactsExtractor
from packages.medical_nlp_sdk import MedicalNlpProcessor
from packages.representation_sdk import RepresentationEngine
from packages.reasoning_sdk import ClinicalReasoner
from packages.contracts.transcription import TranscriptEvent

from apps.runtime.src.ports.inbound.evidence import EvidenceIngressPort
from apps.runtime.src.ports.outbound.persistence import ReviewRepositoryPort
from apps.runtime.src.ports.outbound.streaming import StreamBrokerPort

from .normalization import ClinicalNormalizationLayer
from .runtime_session import RuntimeSession


class ClinicalOrchestrator:
    """Compose a session executor and expose only the Runtime use-case API."""

    def __init__(
        self,
        *,
        broker: StreamBrokerPort,
        nlp_processor: MedicalNlpProcessor,
        facts_extractor: ClinicalFactsExtractor,
        context_builder: ClinicalContextBuilderPort,
        reasoner: ClinicalReasoner,
        representation_engine: RepresentationEngine,
        review_store: ReviewRepositoryPort,
        normalization_layer: ClinicalNormalizationLayer | None = None,
    ) -> None:
        self._session = RuntimeSession(
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
        return self._session.review_store

    def evidence_ingress_for(self, stream_id: str) -> EvidenceIngressPort:
        return self._session.evidence_ingress_for(stream_id)

    async def run_canonical_events(
        self,
        *,
        stream_id: str,
        encounter_id: str,
        patient_id: str,
        language: str,
        events: AsyncIterator[TranscriptEvent],
    ) -> None:
        await self._session.run_canonical_events(
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
        await self._session.run(
            stream_id=stream_id,
            encounter_id=encounter_id,
            patient_id=patient_id,
            language=language,
            canonical_events=canonical_events,
        )
