"""Deterministic Clinical Facts extractor for contract and integration tests."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import replace
from datetime import datetime
from typing import Any

from packages.medical_nlp_sdk import NlpResult

from .models import ClinicalFact, ClinicalFactsBatch, ClinicalMention


class DeterministicClinicalFactsExtractor:
    """Map Medical NLP entities to traceable, provider-neutral fact candidates.

    This is a normalization boundary, not a diagnosis engine.  It fixes only
    high-confidence transcription variants and keeps every original entity in
    provenance so that a clinician or auditor can trace the change.
    """

    async def extract(
        self,
        *,
        encounter_id: str,
        subject_id: str,
        patient_id: str | None,
        result: NlpResult | None = None,
        mentions: tuple[ClinicalMention, ...] = (),
        observed_at: datetime | None = None,
    ) -> ClinicalFactsBatch:
        if mentions:
            return ClinicalFactsBatch(
                encounter_id=encounter_id,
                items=tuple(
                    self._mention_to_fact(
                        encounter_id=encounter_id,
                        subject_id=subject_id,
                        patient_id=patient_id,
                        mention=mention,
                        observed_at=observed_at,
                    )
                    for mention in mentions
                ),
            )
        if result is None:
            raise ValueError("result or mentions must be provided")
        unique: dict[tuple[str, str, str], ClinicalFact] = {}
        for index, entity in enumerate(result.entities):
            if entity.assertion.strip().casefold() in {"question", "interrogative", "query"}:
                continue
            fact = self._to_fact(
                encounter_id=encounter_id,
                subject_id=subject_id,
                patient_id=patient_id,
                result=result,
                index=index,
                entity=entity,
                observed_at=observed_at,
            )
            key = (fact.category.casefold(), fact.value.casefold(), fact.polarity)
            previous = unique.get(key)
            if previous is None:
                unique[key] = fact
                continue
            source_refs = list(previous.provenance.get("source_refs", (previous.provenance["source_ref"],)))
            source_refs.append(fact.provenance["source_ref"])
            unique[key] = replace(
                previous,
                provenance={**previous.provenance, "source_refs": tuple(source_refs)},
            )
        return ClinicalFactsBatch(encounter_id=encounter_id, items=tuple(unique.values()))

    @staticmethod
    def _mention_to_fact(
        *,
        encounter_id: str,
        subject_id: str,
        patient_id: str | None,
        mention: ClinicalMention,
        observed_at: datetime | None,
    ) -> ClinicalFact:
        category = {
            "condition": "Condition",
            "symptom": "Symptom",
            "medication": "Medication",
            "allergy": "Allergy",
            "lifestyle": "Lifestyle",
            "temporal": "Duration",
            "severity": "Severity",
        }.get(mention.semantic_type, mention.semantic_type.title())
        stable_identity = ":".join(
            (
                encounter_id,
                subject_id,
                mention.code or mention.concept_id,
                "negative" if mention.negated else "positive",
            )
        )
        fact_id = f"fact-{hashlib.sha256(stable_identity.encode()).hexdigest()[:20]}"
        metadata = {
            "temporality": mention.temporality,
            "certainty": mention.certainty,
            "status": mention.status.value if hasattr(mention.status, "value") else mention.status,
            "speaker": mention.speaker,
            "review_required": mention.review_required,
            "concept_id": mention.concept_id,
            "canonical": mention.normalized_text,
            "ontology": mention.ontology,
            "code": mention.code,
        }
        if mention.semantic_value is not None:
            metadata["semantic_value"] = mention.semantic_value
        if mention.semantic_unit:
            metadata["semantic_unit"] = mention.semantic_unit
        return ClinicalFact(
            fact_id=fact_id,
            category=category,
            value=mention.normalized_text,
            subject_id=subject_id,
            patient_id=patient_id,
            encounter_id=encounter_id,
            source="clinical_normalization",
            provenance={
                **dict(mention.provenance),
                "mention_id": mention.id,
                "original_text": mention.original_text,
                "normalized_text": mention.normalized_text,
                "segment_id": mention.segment_id,
                "revision": mention.revision,
            },
            confidence=mention.confidence,
            unit=mention.semantic_unit,
            certainty=mention.certainty,
            polarity="negative" if mention.negated else "positive",
            observed_at=observed_at or mention.created_at,
            status="candidate",
            metadata=metadata,
            canonical=mention.normalized_text,
            ontology=mention.ontology,
            code=mention.code or mention.concept_id,
        )

    @classmethod
    def _to_fact(
        cls,
        *,
        encounter_id: str,
        subject_id: str,
        patient_id: str | None,
        result: NlpResult,
        index: int,
        entity: object,
        observed_at: datetime | None,
    ) -> ClinicalFact:
        digest = hashlib.sha256(
            f"{result.request_id}:{index}:{entity.start}:{entity.end}".encode()
        ).hexdigest()[:16]
        raw_category = entity.label.strip()
        raw_value = entity.text.strip()
        category, value, unit, metadata = cls._normalize(raw_category, raw_value)
        assertion = entity.assertion.strip().lower()
        if entity.negated or assertion in {"absent", "negated", "negative"}:
            polarity = "negative"
            certainty = "reported"
        elif assertion in {"possible", "uncertain", "conditional"}:
            polarity = "positive"
            certainty = "uncertain"
        else:
            polarity = "positive"
            certainty = "reported"

        # A clinician's screening question is not automatically a patient
        # response.  Keep the item auditable, but make the uncertainty visible
        # instead of presenting a false negative in SOAP/FHIR.
        if category == "Symptom" and value.casefold() == "febre" and polarity == "negative":
            polarity = "unknown"
            certainty = "uncertain"
            metadata = {**metadata, "review_required": "screening question had no confirmed answer"}

        provenance: dict[str, Any] = {
            "source_ref": f"{result.request_id}:{entity.start}-{entity.end}",
            "request_id": result.request_id,
            "provider": result.provider,
            "entity_label": raw_category,
            "entity_index": index,
        }
        if raw_value != value or raw_category != category:
            provenance.update(
                {
                    "raw_value": raw_value,
                    "raw_category": raw_category,
                    "normalizer": "clinical-text-normalizer-v1",
                }
            )
        return ClinicalFact(
            fact_id=f"fact-{digest}",
            category=category,
            value=value,
            unit=unit,
            subject_id=subject_id,
            patient_id=patient_id,
            encounter_id=encounter_id,
            source="medical_nlp",
            provenance=provenance,
            confidence=None,
            certainty=certainty,
            polarity=polarity,
            observed_at=observed_at,
            status="candidate",
            metadata=metadata,
            canonical=value,
            ontology="ASTERA-CONCEPT",
            code=f"clinical.{_slug(category)}.{_slug(value)}",
        )

    @staticmethod
    def _normalize(category: str, value: str) -> tuple[str, str, str | None, dict[str, Any]]:
        folded = _fold(value)
        normalized_category = category
        normalized_value = value
        unit: str | None = None
        metadata: dict[str, Any] = {}

        if category.casefold() == "symptom":
            if "cansacio" in folded:
                normalized_category, normalized_value = "Fatigue", "cansaço"
            elif "na ausia" in folded or "nausia" in folded:
                normalized_category, normalized_value = "Nausea", "náusea"
            elif "nao vou me ter" in folded or "nao vomitei" in folded:
                normalized_category, normalized_value = "Vomiting", "vômito"
            elif "visao ficou" in folded and "embassada" in folded:
                normalized_value = "visão um pouco embaçada"
            elif folded == "dormido muito mal":
                normalized_category, normalized_value = "SleepQuality", "sono ruim"
        elif category.casefold() == "medication":
            normalized_value = re.sub(r"\bloss\s*artana\b", "losartana", value, flags=re.IGNORECASE)
            normalized_value = re.sub(r"(\d+)\s*mg\b", r"\1 mg", normalized_value, flags=re.IGNORECASE)
            dose_match = re.search(r"(?P<dose>\d+)\s*mg\b", normalized_value, flags=re.IGNORECASE)
            if dose_match:
                metadata["medication_name"] = normalized_value[: dose_match.start()].strip()
                metadata["dose"] = f"{dose_match.group('dose')} mg"
        elif category.casefold() in {"severity", "intensity"} and _duration_match(value):
            number, duration_unit = _duration_match(value)
            normalized_category, normalized_value, unit = "Duration", f"{number} {duration_unit}", duration_unit
            metadata.update({"semantic_value": number, "semantic_unit": duration_unit, "concept_id": "clinical.duration"})
        elif category.casefold() == "severity" and folded == "oito":
            normalized_value, unit = "8/10", "score_0_10"
        elif category.casefold() == "allergy":
            normalized_value = "alergia medicamentosa conhecida"
        elif category.casefold() == "habit":
            if "nao fumo" in folded:
                normalized_category, normalized_value = "TobaccoUse", "tabagismo"
            elif "bebo apenas socialmente" in folded:
                normalized_category, normalized_value = "AlcoholUse", "consumo social de álcool"
            elif "pula refeicoes" in folded:
                normalized_category, normalized_value = "Nutrition", "pula refeições"

        return normalized_category, normalized_value, unit, metadata


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


def _duration_match(value: str) -> tuple[int, str] | None:
    match = _DURATION_RE.search(_fold(value))
    if not match:
        return None
    raw_number = match.group("number").casefold()
    number = int(raw_number) if raw_number.isdigit() else _NUMBER_WORDS[raw_number]
    unit = match.group("unit").casefold()
    unit = {"mes": "mês", "meses": "meses"}.get(unit, unit)
    return number, unit


def _slug(value: str) -> str:
    folded = _fold(value).replace("/", "-")
    return re.sub(r"[^a-z0-9]+", "-", folded).strip("-") or "unknown"
