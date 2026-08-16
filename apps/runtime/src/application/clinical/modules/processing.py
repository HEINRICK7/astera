"""Clinical processing stages invoked by the runtime session coordinator."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
import logging
from typing import Any

from packages.clinical_context_sdk import ClinicalContext
from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch
from packages.contracts.transcription import TranscriptEvent
from packages.representation_sdk import RepresentationRequest

from apps.runtime.src.application.clinical.knowledge_layer import KnowledgeProjection
from apps.runtime.src.application.clinical.normalization import NormalizationResult
from apps.runtime.src.application.clinical.transcript_state import ClinicalTranscriptState
from apps.runtime.src.ports.outbound.persistence import ReviewRepositoryPort

from .context import ClinicalContextModule
from .correlation import ClinicalCorrelationModule
from .facts import ClinicalFactsModule
from .knowledge import ClinicalKnowledgeModule
from .observations import ClinicalObservationModule
from .projections import ClinicalProjectionModule
from .representation import ClinicalRepresentationModule
from .research import ClinicalResearchModule

logger = logging.getLogger("astera.clinical.processing")
Publish = Callable[[str, dict[str, Any]], Awaitable[None]]
PublishA2UI = Callable[[tuple[dict[str, Any], ...]], Awaitable[None]]
MarkLatency = Callable[[str], None]


class ClinicalProcessingModule:
    """Own semantic processing; RuntimeSession owns execution mechanics."""

    def __init__(
        self,
        *,
        observations: ClinicalObservationModule,
        facts: ClinicalFactsModule,
        knowledge: ClinicalKnowledgeModule,
        context: ClinicalContextModule,
        research: ClinicalResearchModule,
        representation: ClinicalRepresentationModule,
        projections: ClinicalProjectionModule,
        review_store: ReviewRepositoryPort,
        encounter_id: str,
        patient_id: str,
        stream_id: str,
        language: str,
        publish: Publish,
        publish_a2ui: PublishA2UI,
        mark_latency: MarkLatency,
    ) -> None:
        self._observations = observations
        self._facts = facts
        self._knowledge = knowledge
        self._context = context
        self._research = research
        self._representation = representation
        self._projections = projections
        self._review_store = review_store
        self._encounter_id = encounter_id
        self._patient_id = patient_id
        self._stream_id = stream_id
        self._language = language
        self._publish = publish
        self._publish_a2ui = publish_a2ui
        self._mark_latency = mark_latency

    async def process_fast(
        self,
        *,
        state: ClinicalTranscriptState,
        event: TranscriptEvent,
        segment: Any,
        source_segment: Any,
    ) -> tuple[KnowledgeProjection, bool]:
        """Normalize one event and update the fast clinical projection."""
        try:
            normalization = self._observations.normalize(
                state,
                segment_ids=(segment.segment_id or f"segment-{segment.sequence}",),
                metadata={
                    "request_id": f"{self._stream_id}:clinical:{segment.sequence}",
                    "session_id": self._stream_id,
                    "provider": event.provider,
                    "trace_id": event.envelope.trace_id,
                    "speaker": source_segment.speaker or "unknown",
                    "received_at": event.envelope.received_at,
                    "processed_at": event.envelope.received_at,
                },
            )
        except Exception:
            logger.exception(
                "clinical normalization failed stream_id=%s segment=%s",
                self._stream_id,
                segment.sequence,
            )
            normalization = NormalizationResult(
                mentions=(),
                metrics={
                    "mentions_detected": 0,
                    "mentions_normalized": 0,
                    "mentions_negated": 0,
                    "mentions_review_required": 0,
                    "normalization_latency_ms": 0.0,
                    "normalization_errors": 1,
                },
            )

        await self._publish("clinical.runtime.metrics", {"event_class": "runtime", **normalization.metrics})
        registered = self._observations.register(
            normalization.mentions,
            encounter_id=self._encounter_id,
            subject_id=self._patient_id,
        )
        for item in registered:
            await self._publish(
                "clinical.mention.detected",
                {
                    "event_class": "clinical",
                    "mention": item.mention.to_dict(),
                    "lifecycle": item.lifecycle,
                    "update_count": item.update_count,
                    "registry_size": len(self._observations.registry.mentions),
                },
            )

        mentions = tuple(item.mention for item in registered)
        batch = (
            await self._facts.extract(
                encounter_id=self._encounter_id,
                subject_id=self._patient_id,
                patient_id=self._patient_id,
                mentions=mentions,
                observed_at=datetime.now(timezone.utc),
            )
            if mentions
            else self._facts.empty(self._encounter_id)
        )

        projections: list[KnowledgeProjection] = []
        if batch.items:
            for fact in batch.items:
                projections.append(
                    self._knowledge.apply(
                        ClinicalFactsBatch(encounter_id=self._encounter_id, items=(fact,)),
                        source="transcription",
                    )
                )
        else:
            projections.append(self._knowledge.apply(batch, source="transcription"))

        projection = projections[-1]
        for extracted, incremental in zip(batch.items, projections):
            fact = next(
                item
                for item in incremental.facts
                if (item.category.casefold(), item.value.casefold(), item.polarity)
                == (extracted.category.casefold(), extracted.value.casefold(), extracted.polarity)
            )
            lifecycle = next(
                (item.lifecycle for item in incremental.events if item.fact_id == fact.fact_id),
                "created",
            )
            event_category = self._event_category(fact.category)
            payload = {
                "event_class": "fast",
                "event_name": f"clinical.fast.{event_category}.detected",
                "fact": fact.to_dict(),
                "lifecycle": lifecycle,
            }
            await self._publish(f"clinical.fast.{event_category}.detected", payload)
            await self._publish("clinical.fact.detected", payload)
            if incremental.events:
                for knowledge_event in incremental.events:
                    await self._publish(
                        "clinical.knowledge.event",
                        {"event_class": "fast", "event": knowledge_event.to_dict()},
                    )
                await self._publish(
                    "clinical.knowledge.updated",
                    {"event_class": "fast", "knowledge": incremental.to_dict()},
                )
                presentation = self._projections.compose(incremental)
                await self._publish_a2ui(self._projections.a2ui.project(presentation))
                await self._publish(
                    "clinical.runtime.metrics",
                    {
                        "event_class": "runtime",
                        "clinical_objects": len(incremental.cards),
                        "knowledge_updates": len(incremental.events),
                    },
                )
                self._mark_latency("time_to_first_clinical_object_ms")
        return projection, bool(batch.items)

    async def process_deep(
        self,
        *,
        facts: tuple[ClinicalFact, ...],
        previous_context: ClinicalContext | None,
        latest_projection: KnowledgeProjection | None,
        latest_reasoning: dict[str, Any] | None,
        latest_soap: Any,
    ) -> tuple[ClinicalContext, dict[str, Any], Any]:
        """Build context, research it, and render clinician representations."""
        context = await self._context.build(
            facts=facts,
            encounter_id=self._encounter_id,
            previous=previous_context,
            occurred_at=datetime.now(timezone.utc),
        )
        await self._publish(
            "clinical.deep.context.updated",
            {"event_class": "deep", "context": context.to_dict()},
        )
        await self._publish(
            "clinical.deep.reasoning.started",
            {"event_class": "deep", "context_version": context.context_version},
        )
        reasoning = await self._research.reason(context)
        self._mark_latency("time_to_first_hypothesis_ms")
        reasoning_dict = reasoning.to_dict()
        await self._publish(
            "clinical.deep.reasoning.updated",
            {"event_class": "deep", "reasoning": reasoning_dict},
        )
        if latest_projection is not None:
            presentation = self._projections.compose(latest_projection, reasoning=reasoning_dict)
            await self._publish_a2ui(self._projections.a2ui.project(presentation))

        representation = await self._representation.render(
            RepresentationRequest(
                record_id=context.context_id,
                encounter_id=self._encounter_id,
                version=str(context.context_version),
                statements=tuple(fact.value for fact in context.facts),
                formats=("soap", "fhir", "summary"),
                context_id=context.context_id,
                context_version=context.context_version,
                patient_id=self._patient_id,
                facts=tuple(fact.to_dict() for fact in context.facts),
                transcript={"language": self._language, "is_final": True},
                reasoning=reasoning_dict,
                provenance={"source": "live_deep_pipeline", "encounter_id": self._encounter_id},
            )
        )
        soap = next((item.content for item in representation.representations if item.format == "soap"), None)
        self._mark_latency("time_to_soap_ms")
        for item in representation.representations:
            self._review_store.set_representation(self._encounter_id, item.format, item.content)
            await self._publish(
                "clinical.representation.updated",
                {
                    "event_class": "presentation",
                    "format": item.format,
                    "content": item.content,
                    "context_version": context.context_version,
                },
            )
            if item.format == "fhir":
                await self._publish(
                    "clinical.fhir.updated",
                    {
                        "event_class": "presentation",
                        "fhir": item.content,
                        "context_version": context.context_version,
                    },
                )
        await self._publish(
            "clinical.deep.soap.updated",
            {"event_class": "deep", "soap": soap, "context_version": context.context_version},
        )
        if latest_projection is not None:
            presentation = self._projections.compose(
                latest_projection,
                reasoning=reasoning_dict,
                soap=soap,
            )
            await self._publish_a2ui(self._projections.a2ui.project(presentation))
            complete = self._projections.compose(
                latest_projection,
                reasoning=reasoning_dict,
                soap=soap,
                consultation_complete=True,
            )
            await self._publish_a2ui(self._projections.a2ui.project(complete))
            self._projections.presentation.archive()
            archived = self._projections.compose(
                latest_projection,
                reasoning=reasoning_dict,
                soap=soap,
            )
            await self._publish_a2ui(self._projections.a2ui.project(archived))
        await self._publish(
            "clinical.soap.updated",
            {"event_class": "deep", "soap": soap, "context_version": context.context_version},
        )
        await self._publish(
            "clinical.deep.completed",
            {"event_class": "deep", "context_version": context.context_version},
        )
        return context, reasoning_dict, soap

    @staticmethod
    def _event_category(category: str) -> str:
        normalized = category.casefold()
        if normalized in {"symptom", "chiefcomplaint"}:
            return "symptom"
        if normalized == "medication":
            return "medication"
        if normalized == "allergy":
            return "allergy"
        if normalized in {"duration", "temporal"}:
            return "duration"
        if normalized == "location":
            return "location"
        if normalized in {"severity", "intensity"}:
            return "severity"
        return "context"
