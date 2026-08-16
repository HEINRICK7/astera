"""Typed, deterministic clinical conversational semantics primitives.

This module is deliberately benchmark/lab scoped.  It consumes derived local
mentions and never mutates raw or canonical evidence.  The classes are small
policy objects so that continuity, reference resolution, attribute ownership
and relation projection can be tested independently.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Iterable, Mapping

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextResult

from .clinical_projection import ClinicalRelation, ClinicalRelationCompiler
from .relation_input_signals import (
    RelationInputContractReport,
    ResolvedAttributeSignal,
    ResolvedTransitionSignal,
)


class ResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


CRITICAL_FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "dose", "dose_value", "dose_unit", "frequency", "route", "status",
)


@dataclass(frozen=True, slots=True)
class ClinicalSemanticCandidate:
    """Local semantic output; it is not a final clinical projection."""

    mention_candidate: ContextMention | None
    attribute_candidates: tuple[AttributeEvidence, ...]
    relation_candidates: tuple[ClinicalRelation, ...]
    source_segment_id: str
    candidate_id: str = ""
    candidate_type: str = "mention"
    source_span: tuple[int, int] | None = None
    entity_type: str | None = None
    mention_id: str | None = None
    originating_rule: str = "unknown"
    confidence: float = 1.0
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ResolvedClinicalSemantics:
    """The only input accepted by the authoritative projection writer."""

    resolved_mentions: tuple[ContextMention, ...]
    resolved_attributes: Mapping[str, Any]
    resolved_relations: tuple[ClinicalRelation, ...]
    unresolved: tuple[str, ...]
    provenance: Mapping[str, Any]
    resolution_status: ResolutionStatus = ResolutionStatus.RESOLVED
    relation_input_signals: tuple[ResolvedAttributeSignal, ...] = ()
    transition_input_signals: tuple[ResolvedTransitionSignal, ...] = ()

    def __post_init__(self) -> None:
        owners = [item for item in self.resolved_attributes if item in CRITICAL_FIELDS]
        if len(owners) != len(set(owners)):
            raise ValueError("a resolved clinical attribute can have only one owner")
        relation_keys = [
            (item.relation_type, item.source, item.target, item.value)
            for item in self.resolved_relations
        ]
        if len(relation_keys) != len(set(relation_keys)):
            raise ValueError("resolved clinical relations must be unique")
        if self.resolution_status is ResolutionStatus.RESOLVED:
            report = RelationInputContractReport(
                self.relation_input_signals,
                self.transition_input_signals,
            )
            if report.has_blocking_signal:
                raise ValueError("resolved semantics contains a blocking relation input signal")


@dataclass(slots=True)
class AuthorityDecisionMetrics:
    resolver_decisions_total: int = 0
    resolver_decisions_preserved: int = 0
    resolver_decisions_overwritten: int = 0
    legacy_fallback_count: int = 0
    ambiguous_forced_resolution_count: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "resolver_decisions_total": self.resolver_decisions_total,
            "resolver_decisions_preserved": self.resolver_decisions_preserved,
            "resolver_decisions_overwritten": self.resolver_decisions_overwritten,
            "legacy_fallback_count": self.legacy_fallback_count,
            "ambiguous_forced_resolution_count": self.ambiguous_forced_resolution_count,
        }


@dataclass(frozen=True, slots=True)
class QuestionContext:
    asked_entity: str | None
    asked_attribute: str | None
    experiencer: str | None
    segment_id: str
    expected_answer_type: str
    source_span: tuple[int, int] | None = None
    confidence: float = 1.0

    @classmethod
    def from_segment(cls, segment: SegmentContext) -> "QuestionContext | None":
        text = segment.text.casefold()
        if "?" not in text and not text.lstrip().startswith(("qual", "ainda", "tem", "teve", "usa", "toma")):
            return None
        asked_attribute = None
        expected = "confirmation"
        asked_entity = None
        if any(token in text for token in ("remédio", "medicação", "medicamento", "comprimido", "tratamento")):
            asked_entity = "medication"
        elif any(token in text for token in ("dor", "sintoma", "queimação", "formigamento")):
            asked_entity = "symptom"
        elif any(token in text for token in ("doença", "diagnóstico", "diabetes", "hipertensão")):
            asked_entity = "condition"
        if any(token in text for token in ("dose", "quanto", "quantos", "quantas")):
            asked_attribute, expected = "dose", "dose"
        elif any(token in text for token in ("usa", "toma", "continua", "ainda")):
            asked_attribute, expected = "status", "medication_status"
        elif any(token in text for token in ("lado", "direit", "esquerd", "onde")):
            asked_attribute, expected = "laterality", "laterality"
        elif any(token in text for token in ("quem", "de quem", "qual pessoa")):
            asked_attribute, expected = "experiencer", "experiencer"
        elif any(token in text for token in ("mãe", "pai", "irmã", "irmão", "família", "familiar")):
            expected = "confirmation"
        return cls(
            asked_entity=asked_entity,
            asked_attribute=asked_attribute,
            experiencer="family" if any(token in text for token in ("mãe", "pai", "irmã", "irmão", "família", "familiar")) else "patient",
            segment_id=segment.segment_id,
            expected_answer_type=expected,
            source_span=(0, len(segment.text)),
            confidence=0.8 if asked_attribute else 0.65,
        )


@dataclass(frozen=True, slots=True)
class CandidateTrace:
    local_mentions: tuple[str, ...] = ()
    attribute_candidates: tuple[str, ...] = ()
    antecedent_candidates: tuple[str, ...] = ()
    filtered_candidates: tuple[str, ...] = ()
    ranked_candidates: tuple[str, ...] = ()
    selected_owner: str | None = None
    selected_relation: str | None = None
    rejected_candidates: tuple[str, ...] = ()
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED
    origins: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "local_mentions": list(self.local_mentions),
            "attribute_candidates": list(self.attribute_candidates),
            "antecedent_candidates": list(self.antecedent_candidates),
            "filtered_candidates": list(self.filtered_candidates),
            "ranked_candidates": list(self.ranked_candidates),
            "selected_owner": self.selected_owner,
            "selected_relation": self.selected_relation,
            "rejected_candidates": list(self.rejected_candidates),
            "resolution_status": self.resolution_status.value,
            "origins": {key: dict(value) for key, value in self.origins.items()},
        }


ATTRIBUTE_OWNER_TYPES: Mapping[str, tuple[str, ...]] = {
    "dose": ("medication", "treatment"),
    "dose_value": ("medication", "treatment"),
    "dose_unit": ("medication", "treatment"),
    "frequency": ("medication", "treatment"),
    "route": ("medication", "treatment"),
    "laterality": ("symptom", "condition", "anatomical"),
    "negated": ("mention", "symptom", "condition", "medication", "procedure"),
    "experiencer": ("mention", "symptom", "condition", "medication", "procedure"),
    "status": ("medication", "treatment", "symptom", "condition", "procedure"),
    "temporality": ("mention", "symptom", "condition", "medication", "procedure"),
}


class AuthoritativeProjectionWriter:
    """Materialize only resolved semantics for context-dependent cases."""

    def __init__(self, metrics: AuthorityDecisionMetrics | None = None) -> None:
        self.metrics = metrics or AuthorityDecisionMetrics()

    def materialize(
        self,
        *,
        local_candidate: ClinicalContextResult,
        resolved: ResolvedClinicalSemantics,
    ) -> ClinicalContextResult:
        if resolved.resolution_status in {ResolutionStatus.AMBIGUOUS, ResolutionStatus.UNRESOLVED}:
            provenance = dict(local_candidate.provenance)
            provenance.update({
                "semantic_role": "PROJECTION_WRITER",
                "authoritative_resolution": True,
                "resolution_status": resolved.resolution_status.value,
                "unresolved": list(resolved.unresolved),
                "resolved_provenance": dict(resolved.provenance),
                "authority_metrics": self.metrics.to_dict(),
            })
            return ClinicalContextResult(
                **{field_name: getattr(local_candidate, field_name) for field_name in CRITICAL_FIELDS},
                provenance=provenance,
            )

        values = dict(resolved.resolved_attributes)
        result = local_candidate
        for field_name in CRITICAL_FIELDS:
            if field_name not in values:
                raise ValueError(f"authoritative resolution omitted critical field: {field_name}")
            self.metrics.resolver_decisions_total += 1
            if getattr(local_candidate, field_name) == values[field_name]:
                self.metrics.resolver_decisions_preserved += 1
            else:
                self.metrics.resolver_decisions_overwritten += 1
            result = replace_result_field(result, field_name, values[field_name])

        provenance = dict(result.provenance)
        provenance.update({
            "semantic_role": "PROJECTION_WRITER",
            "authoritative_resolution": True,
            "resolution_status": resolved.resolution_status.value,
            "unresolved": list(resolved.unresolved),
            "resolved_provenance": dict(resolved.provenance),
            "authority_metrics": self.metrics.to_dict(),
        })
        projection = dict(provenance.get("projection", {}))
        relation_set = ClinicalRelationCompiler().compile(resolved)
        projection["relations"] = [
            {
                "relation_id": relation.relation_id,
                "relation_type": relation.relation_type,
                "source": relation.source,
                "target": relation.target,
                "value": relation.value,
                "source_mention_id": relation.source_mention_id or relation.source,
                "target_mention_id": relation.target_mention_id or relation.target,
                "source_segment_ids": list(relation.source_segment_ids),
                "confidence": relation.confidence,
                "provenance": dict(relation.provenance),
            }
            for relation in relation_set
        ]
        provenance["relation_compiler"] = {
            "version": "clinical-relation-compiler-v1",
            "immutable_relation_count": len(relation_set.relations),
            "post_compile_mutation_forbidden": True,
        }
        provenance["projection"] = projection
        return ClinicalContextResult(
            **{field_name: getattr(result, field_name) for field_name in CRITICAL_FIELDS},
            provenance=provenance,
        )


def replace_result_field(result: ClinicalContextResult, field_name: str, value: Any) -> ClinicalContextResult:
    """Small explicit seam so projection writes are centralized and auditable."""
    from dataclasses import replace

    return replace(result, **{field_name: value})


@dataclass(frozen=True, slots=True)
class ContextMention:
    """A candidate mention retained in derived conversational state."""

    mention_id: str
    concept_id: str | None
    entity_type: str
    surface: str
    speaker: str
    experiencer: str
    segment_id: str
    turn_index: int
    status: str | None = None
    recency: int = 0
    confidence: float = 1.0
    source_segment_ids: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mention_id or not self.segment_id or not self.entity_type:
            raise ValueError("context mentions require identity, segment and entity type")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("context mention confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class SegmentContext:
    segment_id: str
    speaker: str
    turn_index: int
    text: str
    topic: str | None = None


@dataclass(frozen=True, slots=True)
class CrossSegmentContextState:
    """Derived state grouped by semantic type, not by one last mention."""

    segments: tuple[SegmentContext, ...] = ()
    medication_context: tuple[ContextMention, ...] = ()
    symptom_context: tuple[ContextMention, ...] = ()
    condition_context: tuple[ContextMention, ...] = ()
    procedure_context: tuple[ContextMention, ...] = ()
    family_context: tuple[ContextMention, ...] = ()
    temporal_context: tuple[ContextMention, ...] = ()
    discourse_context: tuple[ContextMention, ...] = ()
    unresolved_references: tuple[str, ...] = ()
    active_mentions: tuple[ContextMention, ...] = ()
    question_contexts: tuple[QuestionContext, ...] = ()

    @property
    def mentions(self) -> tuple[ContextMention, ...]:
        return tuple(
            item
            for group in (
                self.medication_context,
                self.symptom_context,
                self.condition_context,
                self.procedure_context,
                self.family_context,
                self.temporal_context,
                self.discourse_context,
            )
            for item in group
        )

    @classmethod
    def derive(
        cls,
        segments: Iterable[SegmentContext],
        mentions: Iterable[ContextMention],
    ) -> "CrossSegmentContextState":
        ordered_segments = tuple(sorted(segments, key=lambda item: item.turn_index))
        ordered_mentions = tuple(sorted(mentions, key=lambda item: (item.turn_index, item.recency)))
        groups: dict[str, list[ContextMention]] = {
            "medication": [],
            "symptom": [],
            "condition": [],
            "procedure": [],
            "family": [],
            "temporal": [],
        }
        discourse: list[ContextMention] = []
        for mention in ordered_mentions:
            group = mention.entity_type.casefold()
            if group in groups:
                groups[group].append(mention)
            else:
                discourse.append(mention)
        active = tuple(item for item in ordered_mentions if item.status not in {"resolved", "discontinued"})
        question_contexts = tuple(
            question
            for segment in ordered_segments
            if (question := QuestionContext.from_segment(segment)) is not None
        )
        return cls(
            segments=ordered_segments,
            medication_context=tuple(groups["medication"]),
            symptom_context=tuple(groups["symptom"]),
            condition_context=tuple(groups["condition"]),
            procedure_context=tuple(groups["procedure"]),
            family_context=tuple(groups["family"]),
            temporal_context=tuple(groups["temporal"]),
            discourse_context=tuple(discourse),
            active_mentions=active,
            question_contexts=question_contexts,
        )


@dataclass(frozen=True, slots=True)
class ReferenceCandidate:
    mention_id: str
    entity_type: str
    semantic_compatibility: float
    speaker_compatibility: float
    discourse_distance: int
    recency: float
    clinical_attribute_compatibility: float
    confidence: float
    source_segment_ids: tuple[str, ...]
    entity_type_compatibility: float = 1.0
    explicit_reference_strength: float = 0.0
    topic_continuity: float = 1.0
    stale_context_penalty: float = 0.0

    @property
    def score(self) -> float:
        return round(
            self.semantic_compatibility * 0.25
            + self.entity_type_compatibility * 0.15
            + self.speaker_compatibility * 0.10
            + max(0.0, 1.0 - min(self.discourse_distance, 10) / 10) * 0.15
            + self.recency * 0.10
            + self.clinical_attribute_compatibility * 0.10
            + self.explicit_reference_strength * 0.05
            + self.topic_continuity * 0.05
            + self.confidence * 0.05
            - self.stale_context_penalty * 0.25,
            6,
        )


@dataclass(frozen=True, slots=True)
class ReferenceResolution:
    status: ResolutionStatus
    selected: ReferenceCandidate | None
    candidates: tuple[ReferenceCandidate, ...]
    reason: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AttributeEvidence:
    name: str
    value: Any
    source_segment_ids: tuple[str, ...]
    entity_types: tuple[str, ...] = ()
    mention_id: str | None = None
    confidence: float = 1.0


@dataclass(frozen=True, slots=True)
class ClinicalAttributeCandidate(AttributeEvidence):
    """Typed attribute candidate with explicit ownership possibilities."""

    candidate_id: str = ""
    candidate_owner_ids: tuple[str, ...] = ()
    scope: str = "segment"
    source_span: tuple[int, int] | None = None
    originating_rule: str = "unknown"
    candidate_type: str = "attribute"
    provenance: Mapping[str, Any] = field(default_factory=dict)


class ShortAnswerResolver:
    """Turn a short answer into typed candidates only when a question permits it."""

    _DOSE = re.compile(
        r"\b(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>mg|g|mcg|µg|ml|ui|"
        r"unidades?|comprimidos?|cápsulas?|jatos?|gotas?)\b",
        re.IGNORECASE,
    )
    _LEFT = re.compile(r"\b(?:do\s+lado\s+)?esquer(?:do|da)\b", re.IGNORECASE)
    _RIGHT = re.compile(r"\b(?:do\s+lado\s+)?direit(?:o|a)\b", re.IGNORECASE)
    _STOPPED = re.compile(
        r"\b(?:parei|parou|paramos|suspendi|suspendeu|interrompi|interrompeu|"
        r"deixei\s+de|não\s+(?:uso|usa|tomo|toma)\s+mais)\b",
        re.IGNORECASE,
    )
    _NEGATIVE = re.compile(r"^\s*(?:não|nao|nunca|negativo)\b", re.IGNORECASE)
    _POSITIVE = re.compile(r"^\s*(?:sim|isso|exato|correto)\b", re.IGNORECASE)
    _FAMILY = re.compile(
        r"\b(?:minha|meu|minhas|meus)\s+(?:mãe|pai|irmã|irmão|avó|avô|filho|filha)\b",
        re.IGNORECASE,
    )

    @classmethod
    def resolve(
        cls,
        answer: str,
        *,
        question: QuestionContext | None,
        segment_id: str,
        owner_ids: tuple[str, ...] = (),
    ) -> tuple[ClinicalAttributeCandidate, ...]:
        if question is None:
            return ()
        text = answer.strip()
        if not text:
            return ()
        span = (0, len(answer))
        common = {
            "source_segment_ids": (segment_id,),
            "candidate_owner_ids": owner_ids,
            "scope": "question_answer",
            "source_span": span,
            "confidence": question.confidence,
        }
        if question.asked_attribute == "dose":
            match = cls._DOSE.search(text)
            if not match:
                return ()
            value = match.group("value").replace(",", ".")
            unit = match.group("unit").casefold()
            return (
                ClinicalAttributeCandidate(
                    name="dose",
                    value=f"{match.group('value')} {match.group('unit')}",
                    entity_types=ATTRIBUTE_OWNER_TYPES["dose"],
                    candidate_id=f"{segment_id}:answer:dose",
                    originating_rule="short-answer:dose",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
                ClinicalAttributeCandidate(
                    name="dose_value",
                    value=value,
                    entity_types=ATTRIBUTE_OWNER_TYPES["dose_value"],
                    candidate_id=f"{segment_id}:answer:dose_value",
                    originating_rule="short-answer:dose",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
                ClinicalAttributeCandidate(
                    name="dose_unit",
                    value=unit,
                    entity_types=ATTRIBUTE_OWNER_TYPES["dose_unit"],
                    candidate_id=f"{segment_id}:answer:dose_unit",
                    originating_rule="short-answer:dose",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
            )
        if question.asked_attribute == "laterality":
            match = cls._LEFT.search(text) or cls._RIGHT.search(text)
            if not match:
                return ()
            value = "left" if cls._LEFT.search(text) else "right"
            return (
                ClinicalAttributeCandidate(
                    name="laterality",
                    value=value,
                    entity_types=ATTRIBUTE_OWNER_TYPES["laterality"],
                    candidate_id=f"{segment_id}:answer:laterality",
                    originating_rule="short-answer:laterality",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
            )
        if question.asked_attribute == "status" and cls._STOPPED.search(text):
            return (
                ClinicalAttributeCandidate(
                    name="status",
                    value="discontinued",
                    entity_types=ATTRIBUTE_OWNER_TYPES["status"],
                    candidate_id=f"{segment_id}:answer:status",
                    originating_rule="short-answer:discontinued",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
                ClinicalAttributeCandidate(
                    name="temporality",
                    value="past",
                    entity_types=ATTRIBUTE_OWNER_TYPES["temporality"],
                    candidate_id=f"{segment_id}:answer:temporality",
                    originating_rule="short-answer:discontinued",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
            )
        if question.expected_answer_type == "experiencer" and cls._FAMILY.search(text):
            return (
                ClinicalAttributeCandidate(
                    name="experiencer",
                    value="family",
                    entity_types=ATTRIBUTE_OWNER_TYPES["experiencer"],
                    candidate_id=f"{segment_id}:answer:experiencer",
                    originating_rule="short-answer:experiencer",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
            )
        if question.expected_answer_type == "confirmation":
            value = True if cls._POSITIVE.search(text) else False if cls._NEGATIVE.search(text) else None
            if value is None:
                return ()
            name = "status" if question.experiencer == "family" else "negated"
            rendered = "confirmed" if value else "negated"
            if name == "negated":
                rendered = not value
            return (
                ClinicalAttributeCandidate(
                    name=name,
                    value=rendered,
                    entity_types=ATTRIBUTE_OWNER_TYPES[name],
                    candidate_id=f"{segment_id}:answer:{name}",
                    originating_rule="short-answer:confirmation",
                    provenance={"source_segment_ids": (segment_id,), "source_span": span},
                    **common,
                ),
            )
        return ()


@dataclass(frozen=True, slots=True)
class AttributeAttachment:
    attribute: AttributeEvidence
    status: ResolutionStatus
    target_mention_id: str | None
    provenance: tuple[str, ...]
    candidates: tuple[str, ...] = ()


class ContextLifetimePolicy:
    """Deterministic validity policy based on context compatibility."""

    def eligible(
        self,
        candidate: ContextMention,
        *,
        target_turn_index: int,
        target_speaker: str,
        target_entity_type: str | None = None,
        explicit_reference: bool = False,
        topic_changed: bool = False,
    ) -> bool:
        if candidate.turn_index >= target_turn_index:
            return False
        if target_entity_type and candidate.entity_type != target_entity_type:
            return False
        if topic_changed and not explicit_reference:
            return False
        if candidate.status in {"resolved", "discontinued"} and not explicit_reference:
            return False
        # Speaker changes are normal in clinical dialogue.  They reduce score
        # in the resolver, but do not invalidate a compatible antecedent.
        _ = target_speaker
        return True


class AmbiguityPolicy:
    def __init__(self, minimum_score: float = 0.45, tie_margin: float = 0.08) -> None:
        self.minimum_score = minimum_score
        self.tie_margin = tie_margin

    def decide(self, candidates: tuple[ReferenceCandidate, ...]) -> ResolutionStatus:
        if not candidates or candidates[0].score < self.minimum_score:
            return ResolutionStatus.UNRESOLVED
        if len(candidates) > 1 and candidates[0].score - candidates[1].score < self.tie_margin:
            return ResolutionStatus.AMBIGUOUS
        return ResolutionStatus.RESOLVED


class ClinicalReferenceResolver:
    """Resolve references without concatenating conversational text."""

    def __init__(
        self,
        lifetime_policy: ContextLifetimePolicy | None = None,
        ambiguity_policy: AmbiguityPolicy | None = None,
    ) -> None:
        self.lifetime_policy = lifetime_policy or ContextLifetimePolicy()
        self.ambiguity_policy = ambiguity_policy or AmbiguityPolicy()

    def resolve(
        self,
        *,
        state: CrossSegmentContextState,
        target_turn_index: int,
        target_speaker: str,
        entity_type: str | None = None,
        experiencer: str | None = None,
        attribute_names: Iterable[str] = (),
        explicit_reference: bool = False,
        topic_changed: bool = False,
    ) -> ReferenceResolution:
        requested_attributes = set(attribute_names)
        candidates: list[ReferenceCandidate] = []
        for mention in state.mentions:
            if not self.lifetime_policy.eligible(
                mention,
                target_turn_index=target_turn_index,
                target_speaker=target_speaker,
                target_entity_type=entity_type,
                explicit_reference=explicit_reference,
                topic_changed=topic_changed,
            ):
                continue
            semantic = 1.0 if entity_type is None or mention.entity_type == entity_type else 0.0
            entity_compatibility = 1.0 if entity_type is None or mention.entity_type == entity_type else 0.0
            speaker = 1.0 if mention.speaker == target_speaker else 0.65
            experience = 1.0 if experiencer is None or mention.experiencer == experiencer else 0.35
            compatibility = experience
            if requested_attributes:
                present = requested_attributes.intersection(mention.attributes)
                compatibility = (compatibility + len(present) / len(requested_attributes)) / 2
            distance = target_turn_index - mention.turn_index
            candidates.append(
                ReferenceCandidate(
                    mention_id=mention.mention_id,
                    entity_type=mention.entity_type,
                    semantic_compatibility=semantic,
                    speaker_compatibility=speaker,
                    discourse_distance=distance,
                    recency=1.0 / max(distance, 1),
                    clinical_attribute_compatibility=compatibility,
                    confidence=mention.confidence,
                    source_segment_ids=mention.source_segment_ids or (mention.segment_id,),
                    entity_type_compatibility=entity_compatibility,
                    explicit_reference_strength=1.0 if explicit_reference else 0.0,
                    topic_continuity=0.35 if topic_changed else 1.0,
                    stale_context_penalty=max(0.0, distance - 3) / 10,
                )
            )
        ordered = tuple(sorted(candidates, key=lambda item: (-item.score, item.discourse_distance, item.mention_id)))
        status = self.ambiguity_policy.decide(ordered)
        reason = {
            ResolutionStatus.RESOLVED: (
                "semantic-compatible",
                "entity-type-compatible",
                "discourse-nearest",
                "explicit-reference" if explicit_reference else "implicit-reference",
            ),
            ResolutionStatus.AMBIGUOUS: ("equally-plausible-antecedents", "ownership-not-forced"),
            ResolutionStatus.UNRESOLVED: ("no-compatible-antecedent", "ownership-not-invented"),
        }[status]
        return ReferenceResolution(status, ordered[0] if status is ResolutionStatus.RESOLVED else None, ordered, reason)


class ClinicalAttributeAttachmentResolver:
    """Attach each attribute to one compatible owner with field provenance."""

    def attach(
        self,
        *,
        target: ContextMention,
        evidence: Iterable[AttributeEvidence],
    ) -> tuple[AttributeAttachment, ...]:
        attached: list[AttributeAttachment] = []
        for item in evidence:
            compatible_types = item.entity_types or ATTRIBUTE_OWNER_TYPES.get(item.name, ())
            if compatible_types and target.entity_type not in compatible_types:
                attached.append(
                    AttributeAttachment(
                        item,
                        ResolutionStatus.UNRESOLVED,
                        None,
                        item.source_segment_ids,
                        tuple(getattr(item, "candidate_owner_ids", ())),
                    )
                )
                continue
            owner_ids = getattr(item, "candidate_owner_ids", ())
            if owner_ids and target.mention_id not in owner_ids:
                attached.append(AttributeAttachment(item, ResolutionStatus.UNRESOLVED, None, item.source_segment_ids, tuple(owner_ids)))
                continue
            if item.mention_id and item.mention_id != target.mention_id:
                attached.append(AttributeAttachment(item, ResolutionStatus.UNRESOLVED, None, item.source_segment_ids))
                continue
            attached.append(
                AttributeAttachment(
                    attribute=item,
                    status=ResolutionStatus.RESOLVED,
                    target_mention_id=target.mention_id,
                    provenance=item.source_segment_ids,
                    candidates=(target.mention_id,),
                )
            )
        return tuple(attached)


class ClinicalRelationResolver:
    """Project owned attributes and transitions into the current relation vocabulary."""

    _ATTRIBUTE_RELATIONS = {
        "dose": "HAS_DOSE",
        "frequency": "HAS_FREQUENCY",
        "route": "HAS_ROUTE",
        "laterality": "HAS_LATERALITY",
        "status": "HAS_STATUS",
        "experiencer": "EXPERIENCER_OF",
    }

    def resolve(
        self,
        *,
        source: ContextMention,
        attachments: Iterable[AttributeAttachment],
        changed_from: Iterable[AttributeEvidence] = (),
        refers_to: ContextMention | None = None,
    ) -> tuple[ClinicalRelation, ...]:
        relations: list[ClinicalRelation] = []
        for attachment in attachments:
            if attachment.status is not ResolutionStatus.RESOLVED:
                continue
            relation_type = self._ATTRIBUTE_RELATIONS.get(attachment.attribute.name)
            if relation_type is None:
                continue
            relations.append(
                ClinicalRelation(
                    relation_type=relation_type,
                    source=source.mention_id,
                    target=attachment.attribute.name,
                    value=str(attachment.attribute.value),
                    provenance={"source_segment_ids": attachment.provenance, "status": attachment.status.value},
                    relation_id=f"{source.mention_id}:{relation_type}:{attachment.attribute.name}",
                    source_mention_id=source.mention_id,
                    target_mention_id=attachment.target_mention_id,
                    source_segment_ids=attachment.provenance,
                )
            )
        for item in changed_from:
            relations.append(
                ClinicalRelation(
                    relation_type="CHANGED_FROM",
                    source=source.mention_id,
                    target=item.name,
                    value=str(item.value),
                    provenance={"source_segment_ids": item.source_segment_ids},
                    relation_id=f"{source.mention_id}:CHANGED_FROM:{item.name}:{item.value}",
                    source_mention_id=source.mention_id,
                    source_segment_ids=item.source_segment_ids,
                )
            )
        if refers_to is not None:
            relations.append(
                ClinicalRelation(
                    relation_type="REFERS_TO",
                    source=source.mention_id,
                    target=refers_to.mention_id,
                    value=refers_to.surface,
                    provenance={"source_segment_ids": refers_to.source_segment_ids or (refers_to.segment_id,)},
                    relation_id=f"{source.mention_id}:REFERS_TO:{refers_to.mention_id}",
                    source_mention_id=source.mention_id,
                    target_mention_id=refers_to.mention_id,
                    source_segment_ids=refers_to.source_segment_ids or (refers_to.segment_id,),
                )
            )
        return tuple(relations)


@dataclass(frozen=True, slots=True)
class ConversationalSemanticsTrace:
    input_segment: str
    candidate_mentions: tuple[str, ...] = ()
    candidate_scores: Mapping[str, float] = field(default_factory=dict)
    selected_antecedent: str | None = None
    rejected_candidates: tuple[str, ...] = ()
    attached_attributes: tuple[str, ...] = ()
    generated_relations: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    ambiguity_status: ResolutionStatus = ResolutionStatus.UNRESOLVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_segment": self.input_segment,
            "candidate_mentions": list(self.candidate_mentions),
            "candidate_scores": dict(self.candidate_scores),
            "selected_antecedent": self.selected_antecedent,
            "rejected_candidates": list(self.rejected_candidates),
            "attached_attributes": list(self.attached_attributes),
            "generated_relations": list(self.generated_relations),
            "provenance": dict(self.provenance),
            "ambiguity_status": self.ambiguity_status.value,
        }
