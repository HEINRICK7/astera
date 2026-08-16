"""Clinical language normalization between Speech and Clinical Facts.

This module is deliberately deterministic and framework-independent. It does
not diagnose, infer hypotheses, or rewrite transcript state; it produces
traceable Clinical Mentions for the Clinical Runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import re
import time
import unicodedata
from typing import Any, Iterable, Mapping, Protocol, runtime_checkable

from packages.clinical_facts_sdk import ClinicalMention
from packages.clinical_facts_sdk import ClinicalMentionStatus
from packages.medical_nlp_sdk import ClinicalEntity
from apps.runtime.src.application.clinical.transcript_state import ClinicalTranscriptState


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    mentions: tuple[ClinicalMention, ...]
    metrics: Mapping[str, int | float]


@runtime_checkable
class ClinicalNormalizationPort(Protocol):
    """Semantic boundary between transcript state and Clinical Runtime."""

    def normalize_state(
        self,
        state: ClinicalTranscriptState,
        *,
        segment_ids: Iterable[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> NormalizationResult:
        """Return mentions only; never facts, hypotheses or representations."""


@dataclass(frozen=True, slots=True)
class _Concept:
    concept_id: str
    canonical: str
    semantic_type: str
    aliases: tuple[str, ...]
    confidence: float = 0.9
    ontology: str = "ASTERA-CONCEPT"
    code: str | None = None


_CONCEPTS = (
    _Concept("condition.hypertension", "Hipertensão", "condition", ("pressão vive alta", "pressao vive alta", "pressão alta", "pressao alta", "hipertensão", "hipertensao", "hipertenso", "hipertensa", "has")),
    _Concept("symptom.chest_pain", "Dor torácica", "symptom", ("dor torácica", "dor toracica", "dor no peito", "peito doendo")),
    _Concept("symptom.hematemesis", "Hematêmese", "symptom", ("hematêmese", "hematemese", "ematemese", "vomitando sangue", "vomitar sangue", "vômito com sangue", "vomito com sangue"), 0.82),
    _Concept("symptom.dyspnea", "Dispneia", "symptom", ("falta de ar", "dispneia", "dispnéia")),
    _Concept("medication.losartan", "Losartana", "medication", ("tomo losartana", "uso losartana", "losartana")),
    _Concept("medication.unspecified", "Medicamento", "medication", ("remédio da pressão", "remedio da pressao", "remédio para pressão", "remedio para pressao"), 0.7),
    _Concept("condition.diabetes", "Diabetes Mellitus", "condition", ("diabetes mellitus", "diabetes", "dm")),
    _Concept("condition.upper_gi_bleeding", "Hemorragia Digestiva Alta", "condition", ("hemorragia digestiva alta", "hda"), 0.86),
    _Concept("symptom.headache", "Dor de cabeça", "symptom", ("dor de cabeça", "dor de cabeca")),
    _Concept("symptom.fever", "Febre", "symptom", ("febre",)),
    _Concept("symptom.vomiting", "Vômito", "symptom", ("vômito", "vomito")),
    _Concept("symptom.nausea", "Náusea", "symptom", ("náusea", "nausea", "náuseas", "nauseas")),
    _Concept("lifestyle.smoking", "Tabagismo", "lifestyle", ("fuma", "fumante", "tabagismo", "tabagista")),
    _Concept("condition.stroke", "AVC", "condition", ("avc",)),
    _Concept("condition.pneumonia", "Pneumonia", "condition", ("pneumonia",)),
)

_CONCEPT_BY_LABEL = {
    "symptom": _CONCEPTS[1],
    "condition": _CONCEPTS[0],
    "allergy": _Concept("allergy.unspecified", "Alergia medicamentosa", "allergy", ("alergia",), 0.74),
    "medication": _Concept("medication.unspecified", "Medicamento", "medication", ("medicamento",), 0.7),
    "duration": _Concept("clinical.duration", "Duração", "temporal", ("duração", "duracao"), 0.72),
    "severity": _Concept("clinical.severity", "Intensidade", "severity", ("intensidade",), 0.72),
}


class ClinicalNormalizationLayer:
    """Convert speech text into normalized, provenance-preserving mentions."""

    def normalize(
        self,
        text: str | ClinicalTranscriptState,
        *,
        metadata: Mapping[str, Any] | None = None,
        fast_entities: Iterable[ClinicalEntity] = (),
    ) -> NormalizationResult:
        """Normalize text for compatibility or a transcript state.

        New Runtime code must pass ``ClinicalTranscriptState`` through
        :meth:`normalize_state`. The string form remains only for isolated
        vocabulary tests and legacy callers.
        """
        if isinstance(text, ClinicalTranscriptState):
            return self.normalize_state(text, metadata=metadata, fast_entities=fast_entities)
        return self._normalize_text(text, metadata=metadata, fast_entities=fast_entities)

    def normalize_state(
        self,
        state: ClinicalTranscriptState,
        *,
        segment_ids: Iterable[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
        fast_entities: Iterable[ClinicalEntity] = (),
    ) -> NormalizationResult:
        """Normalize only segment text held by the single Speech state.

        The full transcript is deliberately never read here. A revision of a
        segment keeps its mention identity because the mention ID excludes the
        revision number while the returned object carries the new revision.
        """
        requested = {str(value) for value in segment_ids} if segment_ids is not None else None
        segments = list(state.final_segments)
        if state.current_partial is not None:
            segments.append(state.current_partial)
        selected = [segment for segment in segments if requested is None or str(segment.segment_id) in requested]
        base_metadata = dict(metadata or {})
        results: list[NormalizationResult] = []
        for segment in selected:
            index = segments.index(segment)
            previous_segment = segments[index - 1].text if index > 0 else ""
            next_segment = segments[index + 1].text if index + 1 < len(segments) else ""
            segment_status = (
                ClinicalMentionStatus.FINAL.value
                if segment.is_final
                else ClinicalMentionStatus.REVISED.value
                if segment.revision > 0
                else ClinicalMentionStatus.PARTIAL.value
            )
            results.append(self._normalize_text(
                segment.text,
                metadata={
                    **base_metadata,
                    "session_id": state.session_id,
                    "segment_id": segment.segment_id,
                    "revision": segment.revision,
                    "segment_revision": segment.revision,
                    "status": segment_status,
                    "speaker": segment.speaker or base_metadata.get("speaker", "unknown"),
                    "start_ms": segment.start_ms,
                    "end_ms": segment.end_ms,
                    "segment_before": previous_segment,
                    "segment_current": segment.text,
                    "segment_after": next_segment,
                },
                # NLP offsets are based on a rolling narrative and cannot be
                # safely applied to an individual segment.
                fast_entities=fast_entities if len(selected) == 1 and selected[0].text == segment.text else (),
            ))
        mentions = tuple(mention for result in results for mention in result.mentions)
        metrics = {
            "mentions_detected": sum(int(result.metrics.get("mentions_detected", 0)) for result in results),
            "mentions_normalized": len(mentions),
            "mentions_negated": sum(mention.negated for mention in mentions),
            "mentions_review_required": sum(mention.review_required for mention in mentions),
            "normalization_latency_ms": round(sum(float(result.metrics.get("normalization_latency_ms", 0.0)) for result in results), 3),
            "normalization_errors": sum(int(result.metrics.get("normalization_errors", 0)) for result in results),
        }
        return NormalizationResult(mentions=mentions, metrics=metrics)

    def _normalize_text(
        self,
        text: str,
        *,
        metadata: Mapping[str, Any] | None = None,
        fast_entities: Iterable[ClinicalEntity] = (),
    ) -> NormalizationResult:
        started = time.perf_counter()
        metadata = metadata or {}
        mentions: list[ClinicalMention] = []
        errors = 0
        folded = _fold(text)

        for match in _DURATION_RE.finditer(folded):
            duration = _duration_parts(match.group("number"), match.group("unit"))
            if duration is None:
                continue
            number, unit = duration
            concept = _CONCEPT_BY_LABEL["duration"]
            try:
                mentions.append(self._mention(
                    concept=concept,
                    alias=text[match.start():match.end()],
                    text=text,
                    start=match.start(),
                    end=match.end(),
                    metadata=metadata,
                    confidence=0.94,
                    normalized_text=f"{number} {unit}",
                    semantic_value=number,
                    semantic_unit=unit,
                ))
            except (TypeError, ValueError):
                errors += 1

        for concept, alias in _aliases_by_length():
            alias_folded = _fold(alias)
            for match in re.finditer(rf"(?<!\w){re.escape(alias_folded)}(?!\w)", folded):
                try:
                    mentions.append(self._mention(
                        concept=concept,
                        alias=alias,
                        text=text,
                        start=match.start(),
                        end=match.end(),
                        metadata=metadata,
                        confidence=concept.confidence if alias_folded == _fold(alias) else concept.confidence * 0.9,
                        approximate=alias_folded in {"ematemese", "hematemese"},
                    ))
                except (TypeError, ValueError):
                    errors += 1

        # KeywordClinicalNlp remains a fast detector, but it can only add a
        # reviewable candidate; it is no longer the gate for normalization.
        for entity in fast_entities:
            duration = _duration_parts_from_text(entity.text)
            concept = _CONCEPT_BY_LABEL.get(entity.label.casefold())
            if concept is None:
                continue
            if duration is not None:
                number, unit = duration
                concept = _CONCEPT_BY_LABEL["duration"]
                normalized_text = f"{number} {unit}"
            else:
                normalized_text = entity.text.strip()
            concept = _Concept(
                concept_id=concept.concept_id if duration is not None else f"clinical.{entity.label.casefold()}.{_fold(entity.text).replace(' ', '-')}",
                canonical=concept.canonical if duration is not None else entity.text.strip(),
                semantic_type=concept.semantic_type,
                aliases=(entity.text.strip(),),
                confidence=concept.confidence,
                ontology=concept.ontology,
                code=concept.code or concept.concept_id,
            )
            try:
                mentions.append(self._mention(
                    concept=concept,
                    alias=entity.text,
                    text=text,
                    start=entity.start,
                    end=entity.end,
                    metadata={**metadata, "fast_detector": True},
                    confidence=min(concept.confidence, 0.72),
                    approximate=True,
                    negated=entity.negated,
                    normalized_text=normalized_text,
                    semantic_value=duration[0] if duration is not None else None,
                    semantic_unit=duration[1] if duration is not None else None,
                ))
            except (TypeError, ValueError):
                errors += 1

        mentions.sort(key=lambda item: (item.provenance.get("start", 0), item.normalized_text))
        # Assign stable occurrence ordinals after sorting. The ordinal is
        # derived from the segment, concept and position in that segment, so
        # a revision can change text/confidence without changing mention_id.
        occurrence_by_concept: dict[tuple[str, str], int] = {}
        stable_mentions: list[ClinicalMention] = []
        for mention in mentions:
            key = (mention.segment_id, mention.concept_id)
            occurrence = occurrence_by_concept.get(key, 0)
            occurrence_by_concept[key] = occurrence + 1
            session_id = str(mention.provenance.get("session_id") or mention.provenance.get("request_id") or "clinical")
            stable_id = hashlib.sha256(
                f"{session_id}:{mention.segment_id}:{mention.concept_id}:{occurrence}".encode()
            ).hexdigest()[:20]
            stable_mentions.append(replace(
                mention,
                id=f"mention-{stable_id}",
                provenance={**dict(mention.provenance), "occurrence": occurrence},
            ))
        mentions = stable_mentions
        metrics = {
            "mentions_detected": len(mentions),
            "mentions_normalized": len(mentions),
            "mentions_negated": sum(mention.negated for mention in mentions),
            "mentions_review_required": sum(mention.review_required for mention in mentions),
            "normalization_latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "normalization_errors": errors,
        }
        return NormalizationResult(tuple(mentions), metrics)

    @staticmethod
    def _mention(
        *,
        concept: _Concept,
        alias: str,
        text: str,
        start: int,
        end: int,
        metadata: Mapping[str, Any],
        confidence: float,
        approximate: bool = False,
        negated: bool | None = None,
        normalized_text: str | None = None,
        semantic_value: int | float | str | None = None,
        semantic_unit: str | None = None,
    ) -> ClinicalMention:
        original_text = text[start:end]
        folded_text = _fold(text)
        prefix = folded_text[max(0, start - 48):start]
        context = folded_text[max(0, start - 48):min(len(folded_text), end + 48)]
        is_negated = bool(re.search(r"(?:\bnao\b|\bnunca\b|\bnega\b|\bsem\b)", prefix)) if negated is None else negated
        temporality = _temporality(context)
        certainty = _certainty(context)
        segment_id = str(metadata.get("segment_id") or f"text-{start}-{end}")
        revision = int(metadata.get("revision", 0))
        # Revision is intentionally excluded: a revised segment updates the
        # same mention identity instead of creating a second occurrence.
        mention_id = hashlib.sha256(
            f"{metadata.get('session_id', metadata.get('request_id', 'clinical'))}:"
            f"{concept.concept_id}:{start}:{end}:{segment_id}".encode()
        ).hexdigest()[:20]
        provider = str(metadata.get("provider", "unknown"))
        trace_id = str(metadata.get("trace_id", metadata.get("request_id", "clinical")))
        status = str(metadata.get("status", ClinicalMentionStatus.FINAL.value))
        received_at = _iso_or_value(metadata.get("received_at"))
        processed_at = _iso_or_value(metadata.get("processed_at"))
        return ClinicalMention(
            id=f"mention-{mention_id}",
            original_text=original_text,
            normalized_text=normalized_text or concept.canonical,
            concept_id=concept.concept_id,
            semantic_type=concept.semantic_type,
            confidence=max(0.0, min(1.0, confidence)),
            negated=is_negated,
            reported=not is_negated,
            temporality=temporality,
            speaker=str(metadata.get("speaker", "patient")),
            certainty=certainty,
            provenance={
                "source": "clinical_normalization_layer",
                "request_id": metadata.get("request_id"),
                "session_id": metadata.get("session_id"),
                "source_segment": segment_id,
                "segment_id": segment_id,
                "segment_revision": revision,
                "speaker": metadata.get("speaker", "unknown"),
                "offset": {"start": start, "end": end},
                "offset_start": start,
                "offset_end": end,
                "start": start,
                "end": end,
                "alias": alias,
                "approximate": approximate,
                "provider": provider,
                "revision": revision,
                "trace_id": trace_id,
                "received_at": received_at,
                "processed_at": processed_at,
                "source_text": text,
                "normalized_by": "clinical-normalization-rules-v2",
                "canonical": concept.canonical,
                "ontology": concept.ontology,
                "code": concept.code or concept.concept_id,
            },
            segment_id=segment_id,
            revision=revision,
            status=status,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            review_required=(
                approximate
                or confidence < 0.8
                or certainty in {"possible", "unknown"}
                or concept.concept_id == "medication.unspecified"
            ),
            ontology=concept.ontology,
            code=concept.code or concept.concept_id,
            semantic_value=semantic_value,
            semantic_unit=semantic_unit or "",
            segment_before=str(metadata.get("segment_before", "")),
            segment_current=str(metadata.get("segment_current", text)),
            segment_after=str(metadata.get("segment_after", "")),
        )


def _aliases_by_length() -> tuple[tuple[_Concept, str], ...]:
    values: list[tuple[_Concept, str]] = []
    seen: set[tuple[str, str]] = set()
    for concept in _CONCEPTS:
        for alias in sorted(concept.aliases, key=len, reverse=True):
            key = (concept.concept_id, _fold(alias))
            if key in seen:
                continue
            seen.add(key)
            values.append((concept, alias))
    return tuple(sorted(values, key=lambda item: len(item[1]), reverse=True))


def _fold(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFD", value.casefold())
        if unicodedata.category(character) != "Mn"
    )


_NUMBER_WORDS = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
}
_DURATION_RE = re.compile(
    r"(?P<number>\d+|um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez)\s+"
    r"(?P<unit>dia[s]?|semana[s]?|mes(?:es)?|ano[s]?)",
    re.IGNORECASE,
)


def _duration_parts(number: str, unit: str) -> tuple[int, str] | None:
    raw_number = number.casefold()
    parsed_number = int(raw_number) if raw_number.isdigit() else _NUMBER_WORDS.get(raw_number)
    if parsed_number is None:
        return None
    normalized_unit = unit.casefold()
    normalized_unit = {"mes": "mês", "meses": "meses"}.get(normalized_unit, normalized_unit)
    return parsed_number, normalized_unit


def _duration_parts_from_text(value: str) -> tuple[int, str] | None:
    match = _DURATION_RE.search(_fold(value))
    return _duration_parts(match.group("number"), match.group("unit")) if match else None


def _temporality(prefix: str) -> str:
    if re.search(r"\b(fam[ií]lia|familiar|m[aã]e|pai|irm[aã]o)\b", prefix):
        return "family_history"
    if re.search(r"\b(vai|irei|ir[aá]|futuro|pretende)\b", prefix):
        return "future"
    if re.search(r"\b(j[aá]\s+tive|hist[oó]rico\s+de|antecedente\s+de|quando\s+crian[cç]a|no\s+passado)\b", prefix):
        return "past"
    if re.search(r"\b(n[aã]o\s+sei|incerto|desconhe[cç]o)\b", prefix):
        return "unknown"
    return "current"


def _certainty(prefix: str) -> str:
    if re.search(r"\b(poss[ií]vel|talvez|pode\s+ser)\b", prefix):
        return "possible"
    if re.search(r"\b(suspeita|suspeito|prov[aá]vel)\b", prefix):
        return "suspected"
    if re.search(r"\bacho\s+que\b", prefix):
        return "possible"
    return "reported"


def _iso_or_value(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _overlaps(left_start: int, left_end: int, right_start: int, right_end: int) -> bool:
    return left_start < right_end and left_end > right_start
