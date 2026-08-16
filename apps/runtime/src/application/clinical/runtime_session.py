"""Live clinical pipeline fed by canonical transcription evidence."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import suppress
from datetime import datetime, timezone
import logging
from time import perf_counter
from typing import Any

from packages.clinical_context_sdk import ClinicalContext
from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsExtractor
from packages.medical_nlp_sdk import MedicalNlpProcessor, NlpRequest
from packages.representation_sdk import RepresentationEngine
from packages.reasoning_sdk import ClinicalReasoner
from packages.contracts.transcription import TranscriptEvent
from apps.runtime.src.ports.inbound.evidence import EvidenceIngressPort
from apps.runtime.src.ports.outbound.persistence import ReviewRepositoryPort
from apps.runtime.src.ports.outbound.streaming import StreamBrokerPort
from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextBuilderPort

from .normalization import ClinicalNormalizationLayer
from .transcript_state import ClinicalTranscriptState
from .modules import (
    CanonicalIngestionModule,
    ClinicalContextModule,
    ClinicalCorrelationModule,
    ClinicalFactsModule,
    ClinicalKnowledgeModule,
    ClinicalObservationModule,
    ClinicalProcessingModule,
    ClinicalPublicationModule,
    ClinicalProjectionModule,
    ClinicalRepresentationModule,
    ClinicalResearchModule,
)

logger = logging.getLogger("astera.clinical_stream")


def _live_metrics() -> dict[str, Any]:
    return {
        "partial_events": 0,
        "done_events": 0,
        "error_events": 0,
        "first_partial_latency_ms": None,
        "time_to_first_partial_ms": None,
        "time_to_first_final_ms": None,
        "time_to_first_clinical_object_ms": None,
        "time_to_first_hypothesis_ms": None,
        "time_to_soap_ms": None,
        "clinical_objects": 0,
        "knowledge_updates": 0,
        "workspace_updates": 0,
        "mentions_detected": 0,
        "mentions_normalized": 0,
        "mentions_negated": 0,
        "mentions_review_required": 0,
        "normalization_latency_ms": 0.0,
        "normalization_errors": 0,
    }


class ConversationMemory(ClinicalTranscriptState):
    """Accumulated narrative state used by the live clinical pipeline."""

    def __init__(
        self,
        *,
        session_id: str = "compatibility-session",
        language: str = "",
        rolling_window_seconds: float = 30.0,
    ) -> None:
        if rolling_window_seconds <= 0:
            raise ValueError("rolling_window_seconds must be positive")
        self._rolling_window_ms = round(rolling_window_seconds * 1000)
        super().__init__(session_id=session_id, language=language)

    @property
    def rolling_text(self) -> str:
        segments = self.final_segments + ((self.current_partial,) if self.current_partial else ())
        if not segments:
            return ""
        latest_end = max(segment.end_ms for segment in segments)
        cutoff = max(0, latest_end - self._rolling_window_ms)
        return " ".join(
            segment.text
            for segment in segments
            if segment.end_ms >= cutoff
        ).strip()


class RuntimeSession:
    """Execute one session using the injected Clinical Runtime modules."""

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
        self._broker = broker
        self._nlp_processor = nlp_processor
        self._facts_extractor = facts_extractor
        self._context_builder = context_builder
        self._reasoner = reasoner
        self._representation_engine = representation_engine
        self._review_store = review_store
        self._normalization_layer = normalization_layer or ClinicalNormalizationLayer()
        self._active_evidence_ingresses: dict[str, EvidenceIngressPort] = {}

    @property
    def review_store(self) -> ReviewRepositoryPort:
        return self._review_store

    def evidence_ingress_for(self, stream_id: str) -> EvidenceIngressPort:
        """Return the canonical ingress for an active clinical stream."""
        try:
            return self._active_evidence_ingresses[stream_id]
        except KeyError as error:
            raise RuntimeError(f"clinical stream is not active: {stream_id}") from error

    async def run_canonical_events(
        self,
        *,
        stream_id: str,
        encounter_id: str,
        patient_id: str,
        language: str,
        events: AsyncIterator[TranscriptEvent],
    ) -> None:
        """Run the Clinical Runtime from canonical evidence only."""
        await self.run(
            stream_id=stream_id,
            encounter_id=encounter_id,
            patient_id=patient_id,
            language=language,
            canonical_events=events,
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
        context: ClinicalContext | None = None
        latest_projection: Any = None
        latest_reasoning: Any = None
        latest_soap: Any = None
        transcript_state = ConversationMemory(session_id=stream_id, language=language)
        ingestion_module = CanonicalIngestionModule()
        observation_module = ClinicalObservationModule(self._normalization_layer)
        facts_module = ClinicalFactsModule(self._facts_extractor)
        correlation_module = ClinicalCorrelationModule()
        knowledge_module = ClinicalKnowledgeModule(correlation_module)
        context_module = ClinicalContextModule(self._context_builder)
        research_module = ClinicalResearchModule(self._reasoner)
        representation_module = ClinicalRepresentationModule(self._representation_engine)
        projection_module = ClinicalProjectionModule()
        a2ui_projector = projection_module.a2ui
        deep_queue: asyncio.Queue[tuple[ClinicalFact, ...]] = asyncio.Queue()
        session_started_at = perf_counter()
        first_partial_at: float | None = None
        clinical_latency: dict[str, float | None] = {
            "time_to_first_clinical_object_ms": None,
            "time_to_first_hypothesis_ms": None,
            "time_to_soap_ms": None,
        }

        def mark_clinical_latency(metric: str) -> None:
            if clinical_latency[metric] is None:
                clinical_latency[metric] = round((perf_counter() - session_started_at) * 1000, 2)

        self._review_store.begin(encounter_id, patient_id)
        publication_module = ClinicalPublicationModule(
            broker=self._broker,
            review_store=self._review_store,
            stream_id=stream_id,
        )
        await publication_module.start()
        publish = publication_module.publish
        publish_a2ui = publication_module.publish_a2ui

        processing_module = ClinicalProcessingModule(
            observations=observation_module,
            facts=facts_module,
            knowledge=knowledge_module,
            context=context_module,
            research=research_module,
            representation=representation_module,
            projections=projection_module,
            review_store=self._review_store,
            encounter_id=encounter_id,
            patient_id=patient_id,
            stream_id=stream_id,
            language=language,
            publish=publish,
            publish_a2ui=publish_a2ui,
            mark_latency=mark_clinical_latency,
        )

        async def publish_transcript_state() -> None:
            final_segments = tuple(
                {
                    "sequence": segment.sequence,
                    "text": segment.text,
                    "start_ms": segment.start_ms,
                    "end_ms": segment.end_ms,
                    "id": segment.segment_id,
                    "revision": segment.revision,
                }
                for segment in transcript_state.final_segments
            )
            await publish_a2ui(
                a2ui_projector.transcript(
                    text=transcript_state.full_transcript,
                    partial=transcript_state.partial,
                    final_segments=final_segments,
                )
            )

        transcript_state.started()
        await publish(
            "clinical.session.started",
            {
                "type": "clinical.session.started",
                "id": f"{stream_id}:started",
                "sessionId": stream_id,
                "sequence": 0,
                "provider": "clinical-runtime",
                "language": language,
                "traceId": stream_id,
                "session": stream_id,
                "lifecycle": transcript_state.lifecycle.to_dict(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        await publish(
            "consultation.pipeline.started",
            {
                "encounter_id": encounter_id,
                "patient_id": patient_id,
                "stages": ["communication", "clinical", "knowledge", "a2ui"],
            },
        )
        async def deep_worker() -> None:
            nonlocal context, latest_reasoning, latest_soap
            while True:
                snapshot = await deep_queue.get()
                try:
                    while True:
                        try:
                            newer_snapshot = deep_queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                        deep_queue.task_done()
                        snapshot = newer_snapshot
                    context, latest_reasoning, latest_soap = await processing_module.process_deep(
                        facts=snapshot,
                        previous_context=context,
                        latest_projection=latest_projection,
                        latest_reasoning=latest_reasoning,
                        latest_soap=latest_soap,
                    )
                except Exception as error:
                    logger.exception(
                        "clinical.deep failed stream_id=%s code=%s",
                        stream_id,
                        type(error).__name__,
                    )
                    await publish(
                        "clinical.deep.error",
                        {"event_class": "deep", "code": type(error).__name__, "message": str(error)},
                    )
                finally:
                    deep_queue.task_done()

        deep_task = asyncio.create_task(deep_worker())

        evidence_ingress, evidence_events = ingestion_module.open()
        self._active_evidence_ingresses[stream_id] = evidence_ingress

        canonical_end = object()

        async def feed_canonical_events() -> None:
            if canonical_events is None:
                return
            async for event in canonical_events:
                await evidence_ingress.ingest(event)
            await evidence_events.put(canonical_end)

        canonical_task: asyncio.Task[None] | None = None
        evidence_event_task: asyncio.Task[TranscriptEvent | object] | None = None
        try:
            canonical_task = asyncio.create_task(feed_canonical_events())
            evidence_event_task = asyncio.create_task(evidence_events.get())
            while True:
                canonical_event = await evidence_event_task
                evidence_event_task = asyncio.create_task(evidence_events.get())
                if canonical_event is canonical_end:
                    evidence_event_task.cancel()
                    evidence_event_task = None
                    break

                # Canonical events from either adapter are processed below.
                segment, is_final = ingestion_module.segment(canonical_event)
                canonical_segment = canonical_event.segments[0] if is_final else canonical_event.segment
                transcript_state.observe_event_timing(
                    captured_at=canonical_event.envelope.occurred_at,
                    received_at=canonical_event.envelope.received_at,
                    processed_at=canonical_event.envelope.received_at,
                    published_at=None,
                )
                nonlocal_first_partial = False
                if not transcript_state.apply(segment, is_final=is_final):
                    continue
                if is_final:
                    segment = next(
                        item for item in transcript_state.final_segments
                        if item.segment_id == canonical_segment.segment_id
                    )
                else:
                    segment = transcript_state.current_partial or segment
                if not segment.is_final and first_partial_at is None:
                    first_partial_at = perf_counter()
                    nonlocal_first_partial = True
                    transcript_state.mark_latency("time_to_first_partial_ms")
                if segment.is_final:
                    transcript_state.mark_latency("time_to_first_final_ms")
                transcript_event_type = ingestion_module.event_kind(canonical_event, is_final=segment.is_final)
                transcript_payload = {
                    "type": transcript_event_type,
                    "session": stream_id,
                    "sequence": segment.sequence,
                    "text": segment.text,
                    "transcript": transcript_state.full_transcript,
                    "partial": transcript_state.partial,
                    "id": segment.segment_id,
                    "revision": segment.revision,
                    "confidence": segment.confidence,
                    "provider": canonical_event.provider,
                    "version": transcript_state.version,
                    "start_ms": segment.start_ms,
                    "end_ms": segment.end_ms,
                    "is_final": segment.is_final,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await publish(
                    transcript_event_type,
                    transcript_payload,
                )
                await publish_transcript_state()
                if nonlocal_first_partial:
                    await publish(
                        "clinical.runtime.metrics",
                        {
                            "event_class": "runtime",
                            "first_partial_latency_ms": round((first_partial_at - session_started_at) * 1000, 2),
                            "time_to_first_partial_ms": transcript_state.metrics["time_to_first_partial_ms"],
                        },
                    )
                if not segment.is_final:
                    await publish("clinical.runtime.status", {"status": "processing"})

                projection, extracted_facts = await processing_module.process_fast(
                    state=transcript_state,
                    event=canonical_event,
                    segment=segment,
                    source_segment=canonical_segment,
                )
                latest_projection = projection
                if not projection.facts:
                    await publish("clinical.runtime.status", {"status": "processing" if not segment.is_final else "listening", "facts": 0, "pipeline": "fast"})
                    continue
                await publish(
                    "clinical.runtime.status",
                    {"status": "processing" if not segment.is_final else "listening", "facts": len(projection.facts), "pipeline": "fast"},
                )
                if extracted_facts and segment.is_final:
                    await deep_queue.put(projection.facts)
            await deep_queue.join()
            transcript_state.completed()
            await publish(
                "clinical.session.completed",
                {
                    "type": "clinical.session.completed",
                    "session": stream_id,
                    "status": transcript_state.status,
                    "lifecycle": transcript_state.lifecycle.to_dict(),
                    "metrics": transcript_state.metrics_snapshot,
                    "snapshot": transcript_state.freeze().to_dict(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            await publish(
                "consultation.pipeline.completed",
                {"encounter_id": encounter_id, "facts": len(knowledge_module.facts), "context_version": context.context_version if context else 0},
            )
        except Exception as error:
            transcript_state.failed()
            logger.exception(
                "clinical.stream failed stream_id=%s code=%s",
                stream_id,
                type(error).__name__,
            )
            await publish(
                "consultation.pipeline.error",
                {"stage": "clinical", "code": type(error).__name__, "message": str(error)},
            )
            await publish(
                "clinical.session.completed",
                {
                    "type": "clinical.session.completed",
                    "session": stream_id,
                    "status": transcript_state.status,
                    "lifecycle": transcript_state.lifecycle.to_dict(),
                    "metrics": transcript_state.metrics_snapshot,
                    "snapshot": transcript_state.freeze().to_dict(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            raise
        finally:
            for task in (evidence_event_task, canonical_task):
                if task is not None and not task.done():
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task
            await publication_module.close()
            deep_task.cancel()
            with suppress(asyncio.CancelledError):
                await deep_task
            self._active_evidence_ingresses.pop(stream_id, None)
