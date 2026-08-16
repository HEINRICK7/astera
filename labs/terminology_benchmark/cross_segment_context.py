"""General cross-segment context resolution for the clinical semantics lab.

This module keeps canonical text untouched.  It builds an immutable derived
state from ordered segments, asks the existing local adapter for segment-local
semantics, and applies only general continuity relations to the result.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from apps.runtime.src.ports.outbound.clinical_semantics import (
    ClinicalContextPort,
    ClinicalContextQuery,
    ClinicalContextResult,
)

from .models import BenchmarkCase, ConversationSegment
from .clinical_projection import ClinicalRelation
from .clinical_conversational_semantics import (
    AttributeAttachment,
    AttributeEvidence,
    ClinicalAttributeAttachmentResolver,
    ClinicalRelationResolver,
    ClinicalReferenceResolver,
    ClinicalSemanticCandidate,
    ConversationalSemanticsTrace,
    ContextLifetimePolicy,
    AmbiguityPolicy,
    ContextMention as TypedContextMention,
    CrossSegmentContextState as TypedCrossSegmentContextState,
    CandidateTrace,
    ClinicalAttributeCandidate,
    ResolutionStatus,
    ResolvedClinicalSemantics,
    AuthoritativeProjectionWriter,
    AuthorityDecisionMetrics,
    QuestionContext,
    ShortAnswerResolver,
    SegmentContext as TypedSegmentContext,
)
from .relation_input_signals import (
    RelationInputContractReport,
    ResolvedAttributeSignal,
    ResolvedTransitionSignal,
    SignalState,
)


_FAMILY_CUE = re.compile(
    r"\b(?:mãe|pai|genitora|genitor|irmã|irmão|avó|avô|família|familiar|filho|filha)\b",
    re.IGNORECASE,
)
_PAST_CUE = re.compile(
    r"\b(?:teve|tinha|teve aos|histórico|história|parei|parou|suspendeu|interrompeu|"
    r"mês passado|semana passada|ontem|há\s+\w+\s+anos?)\b",
    re.IGNORECASE,
)
_DISCONTINUED_CUE = re.compile(
    r"\b(?:parei|parou|paramos|suspendeu|suspendi|interrompeu|interrompi|"
    r"não\s+(?:usa|uso|toma|tomo)\s+mais|deixou\s+de)\b",
    re.IGNORECASE,
)
_RESOLVED_CUE = re.compile(
    r"\b(?:não\s+sinto\s+mais|não\s+tem\s+mais|melhorou|sumiu|resolveu|passou)\b",
    re.IGNORECASE,
)
_ACTIVE_CUE = re.compile(
    r"\b(?:voltou|retomou|retomei|recomeçou|recomecei|passou\s+a\s+usar|"
    r"passei\s+(?:a\s+usar|de|para)|ajustei\s+para|aumentei|aumentou|reduzi|reduziu|mudou\s+para|"
    r"passou\s+para|usa|toma|usando|tomando)\b",
    re.IGNORECASE,
)
_NEGATION_CUE = re.compile(
    r"\b(?:não|nega|sem|nunca)\b|não\s+sinto\s+mais",
    re.IGNORECASE,
)
_NEGATION_BEFORE_TARGET = re.compile(
    r"\b(?:nega|sem|não\s+(?:tive|tem|tenho|teve|usa|toma|sente|sinto|refere|relata|"
    r"apresenta|apresento|está|estou|houve))\b",
    re.IGNORECASE,
)
_LATERALITY_CUE = re.compile(
    r"\b(?:lado\s+)?(esquerdo|esquerda|direito|direita)\b",
    re.IGNORECASE,
)
_DOSE_CUE = re.compile(
    r"\b(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>mg|g|mcg|µg|ml|mL|UI|"
    r"unidades?|comprimidos?|cápsulas?|jatos?|gotas?)\b",
    re.IGNORECASE,
)
_IMPLICIT_DOSE_CUE = re.compile(r"\b(?:para|de)\s+(?P<value>\d+(?:[.,]\d+)?)\b", re.IGNORECASE)
_FREQUENCY_CUE = re.compile(
    r"\b(?:\d+x\s*(?:ao\s+dia|/\s*dia)|duas vezes ao dia|três vezes ao dia|"
    r"uma dose|toda noite|antes de dormir|antes do café|pela manhã|ao acordar|à noite|à tarde|"
    r"se\s+(?:a\s+)?dor(?:\s+apertar)?|"
    r"de manhã|no (?:almoço|jantar)|após\s+(?:o\s+)?(?:almoço|jantar)|depois do (?:almoço|jantar|café)|"
    r"a cada\s+(?:\d+|oito)\s+horas?|de oito em oito horas?|em jejum)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class SegmentContext:
    segment_id: str
    speaker: str
    text: str
    index: int


@dataclass(frozen=True, slots=True)
class CrossSegmentContextState:
    """Derived continuity state; it is never written back to evidence."""

    segments: tuple[SegmentContext, ...]
    active_mentions: tuple[str, ...] = ()
    unresolved_references: tuple[str, ...] = ()
    medication_context: Mapping[str, str] = ()
    family_context: Mapping[str, str] = ()
    temporal_context: Mapping[str, str] = ()
    speaker_context: Mapping[str, str] = ()
    segment_provenance: Mapping[str, tuple[str, ...]] = ()
    typed_state: TypedCrossSegmentContextState | None = None


class CrossSegmentContextResolver:
    """Resolve continuity from ordered segments using provider-neutral cues."""

    def __init__(self, local_adapter: ClinicalContextPort) -> None:
        self._local = local_adapter
        self._authority_metrics = AuthorityDecisionMetrics()
        self._projection_writer = AuthoritativeProjectionWriter(self._authority_metrics)

    async def resolve(self, query: ClinicalContextQuery, case: BenchmarkCase) -> ClinicalContextResult:
        contexts = _segment_contexts(case)
        if not contexts:
            return await self._local.analyze(query)

        target_index = _target_segment_index(case.text, query.start, contexts)
        target = contexts[target_index]
        local = await self._local_result(query, target, "context")
        prior = contexts[:target_index]
        following = contexts[target_index + 1 :]
        state = self._build_state(prior, following)
        candidate = self._apply_continuity(local, state, target, query)
        return self._materialize_authoritative(local, candidate, target, query, state)

    @property
    def authority_metrics(self) -> AuthorityDecisionMetrics:
        return self._authority_metrics

    def _materialize_authoritative(
        self,
        local: ClinicalContextResult,
        candidate_result: ClinicalContextResult,
        target: SegmentContext,
        query: ClinicalContextQuery,
        state: CrossSegmentContextState,
    ) -> ClinicalContextResult:
        candidate_relations = tuple(
            ClinicalRelation(
                relation_type=item.get("relation_type", ""),
                source=item.get("source", ""),
                target=item.get("target", ""),
                value=str(item.get("value", "")),
                provenance=item.get("provenance", {}),
                relation_id=item.get("relation_id"),
                source_mention_id=item.get("source_mention_id"),
                target_mention_id=item.get("target_mention_id"),
                source_segment_ids=tuple(item.get("source_segment_ids", ())),
                confidence=float(item.get("confidence", 1.0)),
            )
            for item in candidate_result.provenance.get("relation_signals", ())
            if isinstance(item, dict) and item.get("relation_type")
        )
        owner_type = _owner_type(query.concept_id) or _owner_type_from_context(
            candidate_result.provenance, target.text, candidate_result
        )
        attributes = {
            field_name: getattr(candidate_result, field_name)
            for field_name in (
                "negated", "certainty", "temporality", "experiencer", "laterality",
                "dose", "dose_value", "dose_unit", "frequency", "route", "status",
            )
        }
        mention = TypedContextMention(
            mention_id=f"context:{target.segment_id}",
            concept_id=None,
            entity_type="clinical",
            surface="mention",
            speaker=target.speaker,
            experiencer=candidate_result.experiencer,
            segment_id=target.segment_id,
            turn_index=target.index,
            source_segment_ids=(target.segment_id,),
            attributes=attributes,
        )
        semantic_candidate = ClinicalSemanticCandidate(
            mention_candidate=mention,
            attribute_candidates=tuple(
                AttributeEvidence(field_name, value, (target.segment_id,))
                for field_name, value in attributes.items()
            ),
            relation_candidates=candidate_relations,
            source_segment_id=target.segment_id,
            provenance={"source_segment_ids": (target.segment_id,)},
        )
        resolved_provenance = {
            "source_segment_ids": (target.segment_id,),
            "candidate_source": semantic_candidate.source_segment_id,
            "owner_type": owner_type,
            "owner_mention_id": mention.mention_id,
            "attribute_provenance": dict(candidate_result.provenance.get("segment_provenance", {})),
            "attribute_ownership": {
                field_name: {
                    "owner_mention_id": mention.mention_id,
                    "owner_segment_id": target.segment_id,
                    "owner_type": owner_type,
                    "source_segment_ids": tuple(candidate_result.provenance.get("segment_provenance", {}).get(field_name, (target.segment_id,))),
                }
                for field_name, value in attributes.items()
                if value is not None
            },
            "transition_evidence": [
                {
                    "relation_type": relation.relation_type,
                    "source": relation.source,
                    "target": relation.target,
                    "value": relation.value,
                    "relation_id": relation.relation_id,
                    "source_mention_id": relation.source_mention_id,
                    "target_mention_id": relation.target_mention_id,
                    "source_segment_ids": list(relation.source_segment_ids),
                    "provenance": dict(relation.provenance),
                }
                for relation in candidate_relations
                if relation.relation_type in {"CHANGED_FROM", "CHANGED_TO", "REFERS_TO"}
            ],
        }
        attribute_signals = tuple(
            _build_attribute_signal(
                field_name=field_name,
                value=value,
                owner_mention_id=mention.mention_id,
                owner_type=owner_type,
                state=_signal_state(
                    field_name,
                    candidate_result.temporality,
                    value,
                ),
                source_segment_ids=tuple(
                    candidate_result.provenance.get("segment_provenance", {}).get(
                        field_name, (target.segment_id,)
                    )
                ),
                candidate_result=candidate_result,
            )
            for field_name, value in attributes.items()
            if field_name in {"dose", "frequency", "route", "laterality", "status"}
            and value is not None
        )
        transition_signals = tuple(
            _build_transition_signal(
                relation=relation,
                owner_mention_id=mention.mention_id,
                owner_type=owner_type,
                current_attributes=attributes,
                transition_ownership=candidate_result.provenance.get(
                    "transition_attribute_ownership", {}
                ),
                event_temporality=candidate_result.provenance.get(
                    "event_temporality", {}
                ),
            )
            for relation in candidate_relations
            if relation.relation_type in {"CHANGED_FROM", "CHANGED_TO"}
        )
        input_report = RelationInputContractReport(attribute_signals, transition_signals)
        compiler_attributes = dict(attributes)
        historical_attributes = {
            signal.attribute_type: signal.value
            for signal in attribute_signals
            if signal.state is SignalState.HISTORICAL
        }
        for field_name in historical_attributes:
            compiler_attributes[field_name] = None
        resolved_provenance["historical_attributes"] = historical_attributes
        resolved_provenance["relation_input_signals"] = [
            signal.to_dict() for signal in attribute_signals
        ]
        resolved_provenance["transition_input_signals"] = [
            signal.to_dict() for signal in transition_signals
        ]
        resolved_provenance["relation_input_contract"] = input_report.to_dict()
        unresolved = [
            f"{signal.status.value}:{getattr(signal, 'attribute_type', 'transition')}"
            for signal in input_report.all_signals
            if not signal.relation_ready
        ]
        for provenance_key in ("transition_attribute_ownership", "event_temporality"):
            if provenance_key in candidate_result.provenance:
                resolved_provenance[provenance_key] = candidate_result.provenance[
                    provenance_key
                ]
        resolved = ResolvedClinicalSemantics(
            resolved_mentions=(semantic_candidate.mention_candidate,),
            resolved_attributes=compiler_attributes,
            resolved_relations=(),
            unresolved=tuple(unresolved),
            provenance=resolved_provenance,
            resolution_status=(
                ResolutionStatus.UNRESOLVED
                if input_report.has_blocking_signal
                else ResolutionStatus.RESOLVED
            ),
            relation_input_signals=attribute_signals,
            transition_input_signals=transition_signals,
        )
        materialized = self._projection_writer.materialize(
            local_candidate=local,
            resolved=resolved,
        )
        materialized_provenance = dict(materialized.provenance)
        materialized_provenance.update({
            "source_text": query.text,
            "source_scope": "conversation",
            "target_segment_id": target.segment_id,
            "conversation_segment_ids": list(
                candidate_result.provenance.get("context_state", {}).get(
                    "resolved_from_segments", (target.segment_id,)
                )
            ),
        })
        if "event_temporality" in candidate_result.provenance:
            materialized_provenance["event_temporality"] = candidate_result.provenance[
                "event_temporality"
            ]
        return replace(materialized, provenance=materialized_provenance)

    async def _local_result(
        self,
        query: ClinicalContextQuery,
        target: SegmentContext,
        evidence_id: str,
    ) -> ClinicalContextResult:
        target_start = _relative_span(query.text, query.start, query.end, target.text)
        if target_start is None:
            return await self._local.analyze(query)
        start, end = target_start
        return await self._local.analyze(
            ClinicalContextQuery(
                text=target.text,
                language=query.language,
                start=start,
                end=end,
                concept_id=query.concept_id,
                evidence_id=f"{evidence_id}:{target.segment_id}",
                semantic_policy=query.semantic_policy,
            )
        )

    def _build_state(
        self,
        prior: Sequence[SegmentContext],
        following: Sequence[SegmentContext],
    ) -> CrossSegmentContextState:
        ordered = tuple(prior) + tuple(following)
        family = {segment.segment_id: "family" for segment in ordered if _FAMILY_CUE.search(segment.text)}
        temporal = {segment.segment_id: "past" for segment in ordered if _PAST_CUE.search(segment.text)}
        speaker = {segment.segment_id: segment.speaker for segment in ordered}
        typed_state = _derive_typed_state(ordered)
        return CrossSegmentContextState(
            segments=ordered,
            active_mentions=tuple(
                segment.segment_id for segment in ordered if _ACTIVE_CUE.search(segment.text)
            ),
            unresolved_references=tuple(
                segment.segment_id for segment in following if not _mentions_named_entity(segment.text)
            ),
            medication_context={segment.segment_id: "medication" for segment in ordered if _MEDICATION_CUE.search(segment.text)},
            family_context=family,
            temporal_context=temporal,
            speaker_context=speaker,
            segment_provenance={
                field: tuple(segment.segment_id for segment in ordered)
                for field in ("temporality", "status", "negated", "experiencer", "laterality", "dose", "frequency")
            },
            typed_state=typed_state,
        )

    def _apply_continuity(
        self,
        local: ClinicalContextResult,
        state: CrossSegmentContextState,
        target: SegmentContext,
        query: ClinicalContextQuery,
    ) -> ClinicalContextResult:
        following_text = " ".join(segment.text for segment in state.segments if segment.index > target.index)
        prior_text = " ".join(segment.text for segment in state.segments if segment.index < target.index)
        combined = f"{prior_text} {target.text} {following_text}".strip()
        provenance = dict(local.provenance)
        fields: dict[str, tuple[str, ...]] = {}

        result = local
        target_surface = query.text[query.start : query.end or query.start]
        target_offset = target.text.casefold().find(target_surface.casefold())
        target_before = target.text[:target_offset] if target_offset >= 0 else ""
        last_negation = max(
            (match.start() for match in _NEGATION_BEFORE_TARGET.finditer(target_before)),
            default=-1,
        )
        scope_break = target_before.casefold().rfind("só")
        negation_tail = target_before[last_negation:] if last_negation >= 0 else ""
        negation_is_local = last_negation >= 0 and not re.search(
            r"\b(?:mas|porém|contudo|embora|apesar\s+de)\b|[;:]",
            negation_tail,
            re.IGNORECASE,
        )
        if negation_is_local and scope_break <= last_negation:
            result = replace(result, negated=True)
            fields["negated"] = (target.segment_id,)
        if _PAST_CUE.search(target_surface):
            result = replace(result, temporality="past")
            fields["temporality"] = (target.segment_id,)
        if (
            result.status is None
            and _MEDICATION_CUE.search(target.text)
            and re.search(r"\b(?:usa|usa\s+mais|toma|tomando|usando|está\s+tomando)\b", target_before, re.IGNORECASE)
        ):
            result = replace(result, status="active")
            fields["status"] = (target.segment_id,)

        if following_text and _DISCONTINUED_CUE.search(following_text):
            result = replace(result, status="discontinued", temporality="past")
            fields.update(status=(state.segments[-1].segment_id,), temporality=(state.segments[-1].segment_id,))
        elif following_text and _RESOLVED_CUE.search(following_text):
            result = replace(result, status="resolved", negated=True)
            fields.update(status=(state.segments[-1].segment_id,), negated=(state.segments[-1].segment_id,))
        elif following_text and _ACTIVE_CUE.search(following_text):
            result = replace(result, status="active", temporality="current")
            fields.update(status=(state.segments[-1].segment_id,), temporality=(state.segments[-1].segment_id,))

        if (
            following_text
            and _NEGATION_CUE.search(following_text)
            and not _DISCONTINUED_CUE.search(following_text)
            and (
                not _mentions_named_entity(following_text)
                or _LEADING_GENERIC_NEGATION.search(following_text)
            )
        ):
            result = replace(result, negated=True)
            fields["negated"] = (state.segments[-1].segment_id,)

        if following_text and _FAMILY_CUE.search(prior_text + " " + target.text):
            result = replace(result, experiencer="family")
            fields["experiencer"] = tuple(
                segment.segment_id
                for segment in state.segments
                if _FAMILY_CUE.search(segment.text)
            ) or (target.segment_id,)

        if following_text:
            lateral = _last_laterality(following_text)
            if (
                lateral
                and not _LATERALITY_CUE.search(target_surface)
                and not _mentions_named_entity(following_text)
            ):
                result = replace(result, laterality=lateral)
                fields["laterality"] = (state.segments[-1].segment_id,)

            dose = _last_dose(following_text)
            if dose and result.dose is None:
                value, unit, rendered = dose
                result = replace(result, dose=rendered, dose_value=value, dose_unit=unit)
                fields.update(dose=(state.segments[-1].segment_id,), dose_value=(state.segments[-1].segment_id,), dose_unit=(state.segments[-1].segment_id,))
            elif result.dose is None:
                implicit_dose = _last_implicit_dose(following_text)
                if implicit_dose:
                    value = implicit_dose
                    result = replace(result, dose=value, dose_value=value)
                    fields.update(dose=(state.segments[-1].segment_id,), dose_value=(state.segments[-1].segment_id,))

            frequency = _last_frequency(following_text)
            if frequency and result.frequency is None:
                result = replace(result, frequency=frequency)
                fields["frequency"] = (state.segments[-1].segment_id,)

            if _PAST_CUE.search(following_text) and result.temporality == "current":
                temporal_sources = (state.segments[-1].segment_id,)
                if _ACTIVE_CUE.search(following_text) and (
                    result.status == "active" or _MEDICATION_CUE.search(target.text)
                ):
                    provenance["event_temporality"] = {
                        "value": "past",
                        "owner": "dose_change_event",
                        "source_segment_ids": temporal_sources,
                    }
                else:
                    result = replace(result, temporality="past")
                    fields["temporality"] = temporal_sources

        answer_candidates = _question_answer_candidates(state, target)
        for candidate in answer_candidates:
            if not _answer_candidate_belongs_to_target(candidate, state, query):
                continue
            if candidate.name == "dose" and result.dose is None:
                result = replace(result, dose=str(candidate.value))
                fields["dose"] = (target.segment_id,)
            elif candidate.name == "dose_value" and result.dose_value is None:
                result = replace(result, dose_value=str(candidate.value))
                fields["dose_value"] = (target.segment_id,)
            elif candidate.name == "dose_unit" and result.dose_unit is None:
                result = replace(result, dose_unit=str(candidate.value))
                fields["dose_unit"] = (target.segment_id,)
            elif candidate.name == "status" and result.status is None:
                result = replace(result, status=str(candidate.value))
                fields["status"] = (target.segment_id,)
            elif candidate.name == "temporality" and result.temporality == "current":
                result = replace(result, temporality=str(candidate.value))
                fields["temporality"] = (target.segment_id,)
            elif candidate.name == "laterality" and result.laterality is None:
                result = replace(result, laterality=str(candidate.value))
                fields["laterality"] = (target.segment_id,)
            elif candidate.name == "negated" and result.negated is False:
                result = replace(result, negated=bool(candidate.value))
                fields["negated"] = (target.segment_id,)

        if result.frequency is None:
            local_frequency = _last_frequency(target.text)
            if local_frequency:
                result = replace(result, frequency=local_frequency)
                fields["frequency"] = (target.segment_id,)

        provenance["cross_segment"] = True
        provenance["context_state"] = {
            "target_segment": target.segment_id,
            "resolved_from_segments": [segment.segment_id for segment in state.segments],
            "active_mentions": list(state.active_mentions),
            "unresolved_references": list(state.unresolved_references),
            "question_contexts": [
                {
                    "segment_id": item.segment_id,
                    "asked_entity": item.asked_entity,
                    "asked_attribute": item.asked_attribute,
                    "expected_answer_type": item.expected_answer_type,
                }
                for item in (state.typed_state.question_contexts if state.typed_state else ())
            ],
        }
        if state.typed_state is not None:
            provenance["typed_context_state"] = {
                "medication_context": [item.mention_id for item in state.typed_state.medication_context],
                "symptom_context": [item.mention_id for item in state.typed_state.symptom_context],
                "condition_context": [item.mention_id for item in state.typed_state.condition_context],
                "active_mentions": [item.mention_id for item in state.typed_state.active_mentions],
            }
        provenance["segment_provenance"] = {
            field: list(sources) for field, sources in fields.items()
        }
        _augment_transition_relations(result, provenance, query, target, state)
        reference = _resolve_reference_for_trace(state, target, query, result)
        candidate_trace = CandidateTrace(
            local_mentions=tuple(item.mention_id for item in (state.typed_state.mentions if state.typed_state else ())),
            attribute_candidates=tuple(item.candidate_id for item in answer_candidates),
            antecedent_candidates=tuple(item.mention_id for item in reference.candidates),
            filtered_candidates=tuple(item.mention_id for item in reference.candidates),
            ranked_candidates=tuple(item.mention_id for item in reference.candidates),
            selected_owner=reference.selected.mention_id if reference.selected else None,
            selected_relation=None,
            rejected_candidates=tuple(item.mention_id for item in reference.candidates[1:]),
            resolution_status=reference.status,
            origins={
                item.candidate_id: {
                    "candidate_type": item.candidate_type,
                    "source_segment_id": item.source_segment_ids[0] if item.source_segment_ids else target.segment_id,
                    "source_span": item.source_span,
                    "entity_type": item.entity_types,
                    "originating_rule": item.originating_rule,
                    "confidence": item.confidence,
                    "provenance": dict(item.provenance),
                }
                for item in answer_candidates
            },
        )
        provenance["candidate_trace"] = candidate_trace.to_dict()
        provenance["conversation_trace"] = ConversationalSemanticsTrace(
            input_segment=target.segment_id,
            candidate_mentions=tuple(item.mention_id for item in reference.candidates),
            candidate_scores={item.mention_id: item.score for item in reference.candidates},
            selected_antecedent=reference.selected.mention_id if reference.selected else None,
            rejected_candidates=tuple(item.mention_id for item in reference.candidates[1:]),
            attached_attributes=tuple(fields),
            generated_relations=tuple(
                item.get("relation_type")
                for item in provenance.get("relation_signals", ())
                if isinstance(item, dict) and item.get("relation_type")
            ),
            provenance={"source_segment_ids": tuple(fields.get("temporality", ()))},
            ambiguity_status=reference.status,
        ).to_dict()
        provenance["source_text"] = query.text
        return replace(result, provenance=provenance)


def _owner_type(concept_id: str | None) -> str | None:
    """Map a concept namespace to the owner vocabulary used by relations."""

    if not concept_id or "." not in concept_id:
        return None
    prefix = concept_id.split(".", 1)[0].casefold()
    return prefix if prefix in {"medication", "treatment", "symptom", "condition", "anatomical"} else None


def _signal_state(
    attribute_type: str,
    temporality: str | None,
    value: object = None,
) -> SignalState:
    # Lifecycle status is a current state. The time of a discontinuation event
    # belongs to transition/event provenance and must not turn the status into
    # a historical entity attribute.
    if attribute_type == "status" and value in {"active", "discontinued", "resolved", "ongoing"}:
        return SignalState.CURRENT
    if temporality == "past":
        return SignalState.HISTORICAL
    if temporality == "current":
        return SignalState.CURRENT
    return SignalState.UNRESOLVED


def _build_attribute_signal(
    *,
    field_name: str,
    value: object,
    owner_mention_id: str,
    owner_type: str | None,
    state: SignalState,
    source_segment_ids: tuple[str, ...],
    candidate_result: ClinicalContextResult,
) -> ResolvedAttributeSignal:
    return ResolvedAttributeSignal(
        attribute_type=field_name,
        value=value,
        owner_mention_id=owner_mention_id,
        owner_type=owner_type,
        state=state,
        provenance={
            "source_segment_ids": source_segment_ids,
            "evidence_id": candidate_result.provenance.get("source_evidence_id"),
            "semantic_policy": candidate_result.provenance.get("semantic_policy"),
        },
        evidence=tuple(source_segment_ids),
    )


def _build_transition_signal(
    *,
    relation: ClinicalRelation,
    owner_mention_id: str,
    owner_type: str | None,
    current_attributes: Mapping[str, object],
    transition_ownership: Mapping[str, object],
    event_temporality: Mapping[str, object],
) -> ResolvedTransitionSignal:
    ownership = transition_ownership.get(relation.target, {})
    if not isinstance(ownership, Mapping):
        ownership = {}
    provenance = dict(relation.provenance)
    source_segment_ids = tuple(relation.source_segment_ids) or tuple(
        provenance.get("source_segment_ids", ())
    )
    provenance["source_segment_ids"] = source_segment_ids
    return ResolvedTransitionSignal(
        attribute_type=relation.target,
        owner_mention_id=owner_mention_id,
        owner_type=owner_type,
        previous_value=ownership.get("previous", relation.value),
        current_value=ownership.get("current", current_attributes.get(relation.target)),
        transition_type=relation.relation_type,
        temporal_anchor=event_temporality.get("value") if isinstance(event_temporality, Mapping) else None,
        provenance=provenance,
        state=_signal_state(
            relation.target,
            (event_temporality.get("value") or "current")
            if isinstance(event_temporality, Mapping)
            else "current"
        ),
        confidence=relation.confidence,
    )


def _owner_type_from_context(
    provenance: Mapping[str, object],
    target_text: str,
    result: ClinicalContextResult,
) -> str | None:
    """Use already-recorded question context when a query has no concept id."""

    questions = provenance.get("context_state", {}).get("question_contexts", ()) if isinstance(provenance.get("context_state", {}), Mapping) else ()
    for question in questions:
        if not isinstance(question, Mapping):
            continue
        entity = question.get("asked_entity")
        if entity in {"medication", "symptom", "condition"}:
            return str(entity)
    if result.dose or result.frequency or result.route or result.status:
        if _MEDICATION_CUE.search(target_text):
            return "medication"
    if result.laterality and re.search(r"\b(?:dor|queimação|sintoma|tremor|formigamento|náusea|tontura)\b", target_text, re.IGNORECASE):
        return "symptom"
    return None


class CrossSegmentContextAdapter:
    """Adapter applying continuity only to cases with ordered segments."""

    provider = "niede-pt-br-cross-segment-context"

    def __init__(self, local_adapter: ClinicalContextPort, cases: Sequence[BenchmarkCase]) -> None:
        self._cases = {case.case_id: case for case in cases}
        self._resolver = CrossSegmentContextResolver(local_adapter)

    def authority_metrics(self) -> dict[str, int]:
        return self._resolver.authority_metrics.to_dict()

    async def analyze(self, query: ClinicalContextQuery) -> ClinicalContextResult:
        case = self._cases.get(query.evidence_id or "")
        if case is None:
            return await self._resolver._local.analyze(query)
        if not case.segments:
            # A one-turn benchmark case still needs the authoritative
            # projection boundary.  Treat it as a local conversation rather
            # than returning relation signals without materializing them.
            local_case = replace(
                case,
                segments=(ConversationSegment("local", "patient", case.text),),
            )
            return await self._resolver.resolve(query, local_case)
        return await self._resolver.resolve(query, case)


def _segment_contexts(case: BenchmarkCase) -> tuple[SegmentContext, ...]:
    return tuple(
        SegmentContext(segment.segment_id, segment.speaker, segment.text, index)
        for index, segment in enumerate(case.segments)
    )


def _derive_typed_state(segments: Sequence[SegmentContext]) -> TypedCrossSegmentContextState:
    """Derive typed candidates from local normalized mentions only.

    This is intentionally a one-way projection.  It never writes to the case,
    transcript, raw evidence or canonical evidence, and it keeps the existing
    safety adapter as the source of assertion attributes.
    """
    from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer

    normalizer = ClinicalNormalizationLayer()
    typed_segments = tuple(
        TypedSegmentContext(item.segment_id, item.speaker, item.index, item.text)
        for item in segments
    )
    mentions: list[TypedContextMention] = []
    for segment in segments:
        normalized = normalizer.normalize(
            segment.text,
            metadata={
                "session_id": "clinical-conversational-semantics-lab",
                "segment_id": segment.segment_id,
                "speaker": segment.speaker,
            },
        )
        family = bool(_FAMILY_CUE.search(segment.text))
        for index, item in enumerate(normalized.mentions):
            mentions.append(
                TypedContextMention(
                    mention_id=item.mention_id,
                    concept_id=item.concept_id,
                    entity_type=item.semantic_type,
                    surface=item.original_text,
                    speaker=segment.speaker,
                    experiencer="family" if family else "patient",
                    segment_id=segment.segment_id,
                    turn_index=segment.index,
                    status=None,
                    recency=index,
                    confidence=item.confidence,
                    source_segment_ids=(segment.segment_id,),
                    attributes={
                        "temporality": item.temporality,
                        "negated": item.negated,
                    },
                )
            )
    return TypedCrossSegmentContextState.derive(typed_segments, mentions)


def _resolve_reference_for_trace(
    state: CrossSegmentContextState,
    target: SegmentContext,
    query: ClinicalContextQuery,
    result: ClinicalContextResult,
):
    from .clinical_conversational_semantics import ReferenceResolution

    typed_state = state.typed_state or TypedCrossSegmentContextState()
    entity_type = "medication" if result.dose or result.status else None
    attributes = tuple(
        field
        for field in ("dose", "frequency", "laterality", "status")
        if getattr(result, field) is not None
    )
    if target.index <= 0 or not typed_state.mentions:
        return ReferenceResolution(
            status=ResolutionStatus.UNRESOLVED,
            selected=None,
            candidates=(),
            reason=("no-prior-context",),
        )
    return ClinicalReferenceResolver(
        lifetime_policy=ContextLifetimePolicy(),
        ambiguity_policy=AmbiguityPolicy(),
    ).resolve(
        state=typed_state,
        target_turn_index=target.index,
        target_speaker=target.speaker,
        entity_type=entity_type,
        experiencer=result.experiencer,
        attribute_names=attributes,
        explicit_reference=False,
        topic_changed=False,
    )


def _question_answer_candidates(
    state: CrossSegmentContextState,
    target: SegmentContext,
) -> tuple[ClinicalAttributeCandidate, ...]:
    """Bind a short answer to the nearest preceding question context."""
    typed_state = state.typed_state
    if typed_state is None or not typed_state.question_contexts:
        return ()
    preceding = tuple(
        item for item in typed_state.question_contexts
        if item.segment_id != target.segment_id
        and next((segment.index for segment in state.segments if segment.segment_id == item.segment_id), -1) < target.index
    )
    if not preceding:
        return ()
    question = max(
        preceding,
        key=lambda item: next(
            (segment.index for segment in state.segments if segment.segment_id == item.segment_id),
            -1,
        ),
    )
    if "?" in target.text or target.text.casefold().lstrip().startswith(("qual", "ainda", "tem", "usa", "toma")):
        return ()
    owner_ids = tuple(
        mention.mention_id
        for mention in typed_state.mentions
        if mention.turn_index < target.index
        and (question.asked_entity is None or mention.entity_type == question.asked_entity)
    )
    return ShortAnswerResolver.resolve(
        target.text,
        question=question,
        segment_id=target.segment_id,
        owner_ids=owner_ids,
    )


def _answer_candidate_belongs_to_target(
    candidate: ClinicalAttributeCandidate,
    state: CrossSegmentContextState,
    query: ClinicalContextQuery,
) -> bool:
    """Do not apply an answer about one owner to a sibling target mention."""
    owner_ids = set(candidate.candidate_owner_ids)
    if not owner_ids:
        return True
    target_surface = query.text[query.start : query.end or query.start].casefold().strip()
    target_ids = {
        mention.mention_id
        for mention in (state.typed_state.mentions if state.typed_state else ())
        if mention.surface.casefold() in target_surface
        or target_surface in mention.surface.casefold()
    }
    return bool(owner_ids.intersection(target_ids))


def _relative_span(
    full_text: str,
    start: int,
    end: int | None,
    segment_text: str,
) -> tuple[int, int] | None:
    if start < 0 or start >= len(full_text):
        return None
    segment_start = full_text.find(segment_text)
    segment_end = segment_start + len(segment_text)
    absolute_end = end if end is not None else start
    if segment_start < 0 or not (segment_start <= start <= segment_end):
        return None
    if absolute_end > segment_end:
        return None
    relative_start = start - segment_start
    return relative_start, absolute_end - segment_start


def _target_segment_index(full_text: str, start: int, contexts: Sequence[SegmentContext]) -> int:
    cursor = 0
    for context in contexts:
        segment_start = full_text.find(context.text, cursor)
        if segment_start >= 0 and segment_start <= start <= segment_start + len(context.text):
            return context.index
        if segment_start >= 0:
            cursor = segment_start + len(context.text)
    return 0


def _mentions_named_entity(text: str) -> bool:
    return bool(re.search(r"\b(?:losartana|enalapril|metformina|câncer|diabetes|dor|tontura|"
                          r"formigamento|tosse|hipertensão|AVC|bombinha|chiado)\b", text, re.IGNORECASE))


_MEDICATION_CUE = re.compile(
    r"\b(?:losartana|enalapril|metformina|sertralina|atenolol|ibuprofeno|"
    r"prednisona|amlodipino|levotiroxina|dipirona|medicação|remédio|bombinha)\b",
    re.IGNORECASE,
)
_LEADING_GENERIC_NEGATION = re.compile(r"^\s*(?:não|não,|sim,\s*não)\b", re.IGNORECASE)


def _last_laterality(text: str) -> str | None:
    matches = list(_LATERALITY_CUE.finditer(text))
    if not matches:
        return None
    return "left" if matches[-1].group(1).casefold().startswith("esquer") else "right"


def _last_dose(text: str) -> tuple[str, str, str] | None:
    matches = list(_DOSE_CUE.finditer(text))
    if not matches:
        return None
    match = matches[-1]
    value = match.group("value").replace(",", ".")
    unit = match.group("unit").casefold()
    return value, unit, f"{match.group('value')} {match.group('unit')}"


def _last_implicit_dose(text: str) -> str | None:
    matches = list(_IMPLICIT_DOSE_CUE.finditer(text))
    return matches[-1].group("value") if matches else None


def _last_frequency(text: str) -> str | None:
    matches = list(_FREQUENCY_CUE.finditer(text))
    return matches[-1].group(0).casefold() if matches else None


def _augment_transition_relations(
    result: ClinicalContextResult,
    provenance: dict[str, object],
    query: ClinicalContextQuery,
    target: SegmentContext,
    state: CrossSegmentContextState,
) -> None:
    """Project explainable dose/frequency transitions without changing attributes."""
    if not result.dose and not result.frequency and not result.status:
        return
    ordered_segments = tuple(sorted((*state.segments, target), key=lambda segment: segment.index))
    text = " ".join(segment.text for segment in ordered_segments)
    if not re.search(r"\b(?:passou|passei|mudou|mudou-se|aumentou|aumentei|reduziu|reduzi|virou|agora|ficou)\b", text, re.IGNORECASE):
        return

    source = TypedContextMention(
        mention_id=f"context:{target.segment_id}:{query.start}:{query.end or query.start}",
        concept_id=query.concept_id,
        entity_type="medication",
        surface=query.text[query.start : query.end or query.start],
        speaker=target.speaker,
        experiencer=result.experiencer,
        segment_id=target.segment_id,
        turn_index=target.index,
        source_segment_ids=(target.segment_id,),
    )
    current_evidence_items: list[AttributeEvidence] = []
    if result.dose:
        current_evidence_items.append(AttributeEvidence(
            name="dose",
            value=result.dose,
            source_segment_ids=(target.segment_id,),
            entity_types=("medication",),
            mention_id=source.mention_id,
        ))
    if result.frequency:
        current_evidence_items.append(AttributeEvidence(
            name="frequency",
            value=result.frequency,
            source_segment_ids=(target.segment_id,),
            entity_types=("medication",),
            mention_id=source.mention_id,
        ))

    changed_from: list[AttributeEvidence] = []
    transition_ownership: dict[str, object] = {}
    dose_values = list(_DOSE_CUE.finditer(text))
    if len(dose_values) >= 2:
        old_match, new_match = dose_values[-2], dose_values[-1]
        old_value = old_match.group("value").replace(",", ".")
        new_value = new_match.group("value").replace(",", ".")
        if old_value != new_value:
            old_rendered = f"{old_match.group('value')} {old_match.group('unit')}"
            changed_from.append(AttributeEvidence(
                name="dose",
                value=old_rendered,
                source_segment_ids=(target.segment_id,),
                entity_types=("medication",),
            ))
            transition_ownership["dose"] = {
                "current": result.dose,
                "previous": old_rendered,
                "owner_mention_id": source.mention_id,
                "source_segment_ids": (target.segment_id,),
            }
    elif result.dose:
        implicit = list(re.finditer(r"\b(?:de|para|a)\s+(\d+(?:[.,]\d+)?)\b", text, re.IGNORECASE))
        if len(implicit) >= 2 and implicit[-2].group(1) != implicit[-1].group(1):
            previous = implicit[-2].group(1)
            changed_from.append(AttributeEvidence(
                name="dose",
                value=previous,
                source_segment_ids=(target.segment_id,),
                entity_types=("medication",),
            ))
            transition_ownership["dose"] = {
                "current": result.dose,
                "previous": previous,
                "owner_mention_id": source.mention_id,
                "source_segment_ids": (target.segment_id,),
            }

    frequencies = list(_FREQUENCY_CUE.finditer(text))
    if len(frequencies) >= 2 and frequencies[-2].group(0).casefold() != frequencies[-1].group(0).casefold():
        previous_frequency = frequencies[-2].group(0).casefold()
        changed_from.append(AttributeEvidence(
            name="frequency",
            value=previous_frequency,
            source_segment_ids=(target.segment_id,),
            entity_types=("medication",),
        ))
        transition_ownership["frequency"] = {
            "current": result.frequency,
            "previous": previous_frequency,
            "owner_mention_id": source.mention_id,
            "source_segment_ids": (target.segment_id,),
        }
    if not current_evidence_items and not changed_from:
        return

    attachments = ClinicalAttributeAttachmentResolver().attach(
        target=source,
        evidence=tuple(current_evidence_items),
    )
    provenance["transition_attribute_ownership"] = transition_ownership
    relations = ClinicalRelationResolver().resolve(
        source=source,
        attachments=attachments,
        changed_from=tuple(changed_from),
    )
    relation_signals = list(provenance.get("relation_signals", ()))
    existing_keys = {
        (item.get("relation_type"), item.get("target"), item.get("value"))
        for item in relation_signals
        if isinstance(item, dict)
    }
    for relation in relations:
        key = (relation.relation_type, relation.target, relation.value)
        if key in existing_keys:
            continue
        relation_signals.append(
            {
                "relation_id": relation.relation_id,
                "relation_type": relation.relation_type,
                "source": relation.source,
                "target": relation.target,
                "value": relation.value,
                "source_mention_id": relation.source_mention_id,
                "target_mention_id": relation.target_mention_id,
                "source_segment_ids": list(relation.source_segment_ids),
                "confidence": relation.confidence,
                "provenance": dict(relation.provenance),
            }
        )
    provenance["relation_signals"] = relation_signals
