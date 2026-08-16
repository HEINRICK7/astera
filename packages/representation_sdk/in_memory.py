"""Deterministic knowledge representation adapter.

The adapter deliberately remains provider-neutral.  It turns structured
Clinical Facts into reviewable documents, while keeping the original facts
and their provenance available to downstream consumers.
"""
from __future__ import annotations

import base64
import json
from collections import defaultdict
from typing import Any, Mapping

from .models import Representation, RepresentationRequest, RepresentationResult


class KnowledgeRepresentationEngine:
    """Render the same knowledge record into SOAP, FHIR, and summary forms."""

    async def render(self, request: RepresentationRequest) -> RepresentationResult:
        representations = tuple(
            self._render_one(request, format_name) for format_name in request.formats
        )
        return RepresentationResult(record_id=request.record_id, representations=representations)

    def _render_one(self, request: RepresentationRequest, format_name: str) -> Representation:
        if format_name == "soap":
            content = self._build_soap(request)
        elif format_name == "fhir":
            content = self._build_fhir(request)
        else:
            content = self._build_summary(request)
        return Representation(
            format=format_name,
            content=content,
            source_record_id=request.record_id,
            version=request.version,
            context_id=request.context_id,
            context_version=request.context_version,
            provenance=request.provenance,
        )

    def _build_soap(self, request: RepresentationRequest) -> dict[str, Any]:
        facts = tuple(request.facts)
        grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for fact in facts:
            grouped[str(fact.get("category", "Other")).casefold()].append(fact)

        symptom_facts = self._facts_for(grouped, "symptom", "chiefcomplaint")
        location_facts = self._facts_for(grouped, "location")
        temporal_facts = self._facts_for(grouped, "temporal", "duration")
        medication_facts = self._facts_for(grouped, "medication")
        condition_facts = self._facts_for(grouped, "condition")
        allergy_facts = self._facts_for(grouped, "allergy")
        objective_facts = self._facts_for(grouped, "vitalsign", "vital_sign", "observation")

        chief_complaint = self._first_value(
            symptom_facts,
            contains=("dor de cabeça", "cefaleia", "dor"),
        ) or self._first_value(symptom_facts)
        subjective_findings = [self._fact_projection(fact) for fact in facts]

        subjective: dict[str, Any] = {
            "chief_complaint": chief_complaint,
            "history_of_present_illness": {
                "symptoms": [self._fact_projection(fact) for fact in symptom_facts],
                "locations": [self._fact_projection(fact) for fact in location_facts],
                "temporal_features": [self._fact_projection(fact) for fact in temporal_facts],
            },
            "medical_history": [self._fact_projection(fact) for fact in condition_facts],
            "medications": [self._fact_projection(fact) for fact in medication_facts],
            "allergies": self._allergy_summary(allergy_facts),
            "reported_findings": subjective_findings,
            "narrative": self._subjective_narrative(
                chief_complaint=chief_complaint,
                facts=facts,
            ),
        }

        objective: dict[str, Any] = {
            "status": "documented" if objective_facts else "not_documented",
            "findings": [self._fact_projection(fact) for fact in objective_facts],
            "narrative": (
                "Dados objetivos disponíveis no contexto clínico."
                if objective_facts
                else "Nenhum sinal vital, exame físico ou resultado objetivo foi documentado."
            ),
        }

        hypotheses = list((request.reasoning or {}).get("hypotheses", []))
        gaps = list((request.reasoning or {}).get("information_gaps", []))
        assessment: dict[str, Any] = {
            "status": "pending_clinician_review",
            "candidate_hypotheses": hypotheses,
            "narrative": (
                "Há hipóteses candidatas para revisão clínica; nenhum diagnóstico definitivo foi gerado."
                if hypotheses
                else "Nenhuma hipótese clínica foi retornada pelo Runtime."
            ),
        }
        plan: dict[str, Any] = {
            "status": "pending_clinician_review",
            "documented_next_steps": self._documented_next_steps(request),
            "open_questions": gaps,
            "narrative": (
                "Revisar os dados, completar o exame clínico e definir a conduta."
                if not self._documented_next_steps(request)
                else "Executar os próximos passos documentados e concluir a revisão clínica."
            ),
        }

        return {
            "subjective": subjective,
            "objective": objective,
            "assessment": assessment,
            "plan": plan,
            "status": "draft",
            "provenance": {
                "source_record_id": request.record_id,
                "context_id": request.context_id,
                "context_version": request.context_version,
                "facts_are_candidates": True,
            },
        }

    def _build_fhir(self, request: RepresentationRequest) -> dict[str, Any]:
        """Build the CPI-001 interim DocumentReference wrapper.

        RFC-003 reserves the full Clinical Graph -> FHIR Bundle mapper for a
        later approved increment.  Until then, the SOAP draft is embedded as
        valid base64 JSON in a DocumentReference attachment.
        """
        soap = self._build_soap(request)
        encoded_soap = base64.b64encode(
            json.dumps(soap, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")
        content: dict[str, Any] = {
            "resourceType": "DocumentReference",
            "id": request.record_id,
            "status": "current",
            "type": {"text": "Clinical consultation note"},
            "description": "Astera SOAP draft derived from Clinical Context.",
            "content": [
                {
                    "attachment": {
                        "contentType": "application/json",
                        "language": (request.transcript or {}).get("language", "pt-BR"),
                        "title": "Astera SOAP Draft",
                        "data": encoded_soap,
                    }
                }
            ],
        }
        if request.patient_id:
            content["subject"] = {"reference": f"Patient/{request.patient_id}"}
        if request.encounter_id:
            content["context"] = {
                "encounter": [{"reference": f"Encounter/{request.encounter_id}"}]
            }
        return content

    def _build_summary(self, request: RepresentationRequest) -> str:
        if request.facts:
            values = [str(fact.get("value", "")).strip() for fact in request.facts]
            values = [value for value in values if value]
            chief = self._first_value(request.facts, contains=("dor de cabeça", "cefaleia", "dor"))
            prefix = f"Queixa principal: {chief}. " if chief else ""
            return prefix + "Fatos relatados: " + "; ".join(values)
        return " ".join(request.statements)

    @staticmethod
    def _facts_for(grouped: Mapping[str, list[Mapping[str, Any]]], *categories: str) -> list[Mapping[str, Any]]:
        result: list[Mapping[str, Any]] = []
        for category in categories:
            result.extend(grouped.get(category.casefold(), []))
        return result

    @staticmethod
    def _first_value(
        facts: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
        contains: tuple[str, ...] = (),
    ) -> str | None:
        for fact in facts:
            value = str(fact.get("value", "")).strip()
            if value and (not contains or any(term in value.casefold() for term in contains)):
                return value
        return None

    @staticmethod
    def _fact_projection(fact: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "id": fact.get("id"),
            "category": fact.get("category"),
            "value": fact.get("value"),
            "polarity": fact.get("polarity", "positive"),
            "certainty": fact.get("certainty", "reported"),
            "provenance": dict(fact.get("provenance", {})),
        }

    @classmethod
    def _allergy_summary(cls, facts: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        if not facts:
            return []
        if all(fact.get("polarity") == "negative" for fact in facts):
            return [{"status": "no_known_allergy_reported", "evidence": [cls._fact_projection(fact) for fact in facts]}]
        return [cls._fact_projection(fact) for fact in facts]

    @staticmethod
    def _subjective_narrative(*, chief_complaint: str | None, facts: tuple[Mapping[str, Any], ...]) -> str:
        if not facts:
            return "Nenhum fato clínico estruturado foi retornado."
        prefix = f"Paciente relata {chief_complaint}." if chief_complaint else "Paciente relata os achados abaixo."
        return prefix + " Os demais fatos permanecem vinculados à sua evidência e aguardam revisão clínica."

    @staticmethod
    def _documented_next_steps(request: RepresentationRequest) -> list[str]:
        text = str((request.transcript or {}).get("text", "")).casefold()
        steps: list[str] = []
        if "exame físico" in text or "exame" in text:
            steps.append("Realizar ou registrar o exame físico.")
        if "pressão" in text or "pressao" in text:
            steps.append("Aferir e registrar a pressão arterial.")
        return steps
