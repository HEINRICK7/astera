"""Compose clinical objects from the internal knowledge projection.

The Graph is allowed to contain entities and predicates. This module is the
anti-corruption boundary: A2UI receives only stable, clinician-facing objects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .knowledge_layer import KnowledgeProjection


@dataclass(frozen=True, slots=True)
class ClinicalObject:
    """A stable object of clinical understanding, not an extracted entity."""

    object_id: str
    object_type: str
    title: str
    summary: str
    attributes: tuple[dict[str, Any], ...]
    evidence: tuple[dict[str, Any], ...]
    lifecycle: str
    priority: int
    attention: str
    source: str
    group: str
    problem: str
    parent_object_id: str | None
    narrative: str
    confidence: float | None
    supporting_facts: tuple[dict[str, Any], ...]
    missing_facts: tuple[str, ...]
    questions: tuple[str, ...]
    recommendations: tuple[str, ...]
    children: tuple[dict[str, Any], ...]
    timeline: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "object_type": self.object_type,
            "title": self.title,
            "summary": self.summary,
            "attributes": [dict(attribute) for attribute in self.attributes],
            "evidence": [dict(item) for item in self.evidence],
            "lifecycle": self.lifecycle,
            "priority": self.priority,
            "attention": self.attention,
            "source": self.source,
            "group": self.group,
            "problem": self.problem,
            "parent_object_id": self.parent_object_id,
            "narrative": self.narrative,
            "confidence": self.confidence,
            "supporting_facts": [dict(item) for item in self.supporting_facts],
            "missing_facts": list(self.missing_facts),
            "questions": list(self.questions),
            "recommendations": list(self.recommendations),
            "children": [dict(item) for item in self.children],
            "timeline": [dict(item) for item in self.timeline],
        }


@dataclass(frozen=True, slots=True)
class PresentationModel:
    version: int
    objects: tuple[ClinicalObject, ...]
    timeline: tuple[dict[str, Any], ...]
    layout: dict[str, Any]
    workspace_state: dict[str, Any]

    @property
    def cards(self) -> tuple[ClinicalObject, ...]:
        """Compatibility alias for older callers; new code uses objects."""

        return self.objects


class ClinicalPresentationComposer:
    """Transform graph entities into a small set of growing clinical objects."""

    WIDGET_LIFECYCLES = frozenset({
        "invisible",
        "emerging",
        "active",
        "focused",
        "supporting",
        "resolved",
        "archived",
    })

    _priorities = {
        "symptom": 10,
        "chiefcomplaint": 10,
        "condition": 20,
        "allergy": 25,
        "medication": 30,
        "vital": 35,
        "vitalsign": 35,
        "procedure": 40,
        "exam": 45,
        "question": 50,
        "clinical_hypothesis": 15,
        "clinical_question": 30,
        "clinical_summary": 65,
        "soap_progress": 70,
    }
    _attribute_categories = {"duration", "temporal", "severity", "intensity", "location", "anatomy"}

    _groups = {
        "clinical_problem": "Problemas principais",
        "clinical_history": "Antecedentes",
        "medication_profile": "Tratamentos",
        "allergy_profile": "Alergias",
        "clinical_hypothesis": "Hipóteses",
        "investigation": "Investigação",
        "clinical_summary": "Resumo clínico",
        "clinical_observation": "Observações",
    }

    def __init__(self) -> None:
        self._seen_objects: set[str] = set()
        self._object_ages: dict[str, int] = {}
        self._resolved_objects: set[str] = set()
        self._archived_objects: set[str] = set()
        self._focused_object_id: str | None = None

    def compose(
        self,
        projection: KnowledgeProjection,
        *,
        reasoning: Mapping[str, Any] | None = None,
        soap: Mapping[str, Any] | None = None,
        consultation_complete: bool = False,
    ) -> PresentationModel:
        facts = {fact.fact_id: fact for fact in projection.facts}
        cards = {str(card["card_id"]): card for card in projection.cards}
        graph_edges = (projection.graph or {}).get("edges", [])
        related_by_fact: dict[str, list[dict[str, Any]]] = {fact_id: [] for fact_id in facts}
        for edge in graph_edges:
            source_id = str(edge.get("source", ""))
            target_id = str(edge.get("target", ""))
            if source_id in related_by_fact:
                related_by_fact[source_id].append({"edge": edge, "fact": facts.get(target_id), "lifecycle": cards.get(target_id, {}).get("lifecycle", "created")})
            if target_id in related_by_fact:
                related_by_fact[target_id].append({"edge": edge, "fact": facts.get(source_id), "lifecycle": cards.get(source_id, {}).get("lifecycle", "created")})

        root_fact_ids: set[str] = set()
        for fact in projection.facts:
            if fact.category.casefold() not in self._attribute_categories:
                root_fact_ids.add(fact.fact_id)

        object_id_by_fact: dict[str, str] = {}
        for fact_id in root_fact_ids:
            object_id_by_fact[fact_id] = f"{self._object_type(facts[fact_id].category.casefold())}-{fact_id}"
        for root_id, related in related_by_fact.items():
            object_id = object_id_by_fact.get(root_id)
            if object_id is None:
                continue
            for item in related:
                related_fact = item["fact"]
                if related_fact is not None and related_fact.fact_id not in object_id_by_fact:
                    object_id_by_fact[related_fact.fact_id] = object_id

        latest_event = projection.events[-1] if projection.events else None
        latest_object_id = object_id_by_fact.get(latest_event.fact_id) if latest_event else None
        reasoning_hypotheses = list((reasoning or {}).get("hypotheses", []))
        if reasoning_hypotheses:
            latest_object_id = f"clinical_hypothesis-{self._stable_value(reasoning_hypotheses[0], 'id', 'name')}"
        if latest_object_id:
            self._focused_object_id = latest_object_id
        primary_object_id = self._primary_object_id(projection.facts, object_id_by_fact, soap)

        objects: list[ClinicalObject] = []
        timeline_by_object: dict[str, list[dict[str, Any]]] = {}
        for entry in projection.timeline:
            entry_object_id = object_id_by_fact.get(str(entry.get("fact_id", "")))
            if entry_object_id:
                timeline_by_object.setdefault(entry_object_id, []).append(
                    {
                        "timeline_id": str(entry.get("timeline_id", "")),
                        "title": self._timeline_title(str(entry.get("lifecycle", "created"))),
                        "detail": str(entry.get("value", "Informação clínica recebida")),
                        "occurred_at": entry.get("occurred_at"),
                    }
                )
        for fact in projection.facts:
            category = fact.category.casefold()
            if category in self._attribute_categories:
                continue
            related = related_by_fact.get(fact.fact_id, [])
            attributes = tuple(
                {
                    "attribute_id": str(item["fact"].fact_id),
                    "label": self._relationship_label(str(item["edge"].get("type", "")), str(item["fact"].category)),
                    "value": item["fact"].value,
                    "source": self._source_label(item["fact"].source),
                }
                for item in related
                if item["fact"] is not None and item["fact"].category.casefold() in self._attribute_categories
            )
            object_type = self._object_type(category)
            object_id = object_id_by_fact[fact.fact_id]
            lifecycle = self._widget_lifecycle(object_id, latest_object_id, consultation_complete)
            supporting_facts = tuple(
                {
                    "fact_id": str(item["fact"].fact_id),
                    "label": self._relationship_label(str(item["edge"].get("type", "")), str(item["fact"].category)),
                    "value": item["fact"].value,
                    "source": self._source_label(item["fact"].source),
                }
                for item in related
                if item["fact"] is not None and item["fact"].fact_id != fact.fact_id
            )
            related_objects = tuple(
                {
                    "object_id": object_id_by_fact[item["fact"].fact_id],
                    "object_type": self._object_type(item["fact"].category.casefold()),
                    "title": item["fact"].value,
                    "relation": self._relationship_label(str(item["edge"].get("type", "")), str(item["fact"].category)),
                }
                for item in related
                if item["fact"] is not None
                and item["fact"].category.casefold() not in self._attribute_categories
                and item["fact"].fact_id in object_id_by_fact
                and object_id_by_fact[item["fact"].fact_id] != object_id
            )
            missing_facts, questions = self._missing_information(object_type, attributes)
            recommendations = self._recommendations_for(missing_facts)
            confidence = self._confidence(fact, related)
            narrative = self._summary(object_type, fact.value, lifecycle)
            self._seen_objects.add(object_id)
            self._object_ages[object_id] = self._object_ages.get(object_id, 0) + 1
            if lifecycle == "resolved":
                self._resolved_objects.add(object_id)
            objects.append(
                ClinicalObject(
                    object_id=object_id,
                    object_type=object_type,
                    title=fact.value,
                    summary=self._summary(object_type, fact.value, lifecycle),
                    attributes=attributes,
                    evidence=({"source": self._source_label(fact.source), "statement": fact.value},),
                    lifecycle=lifecycle,
                    priority=self._object_priority(category, object_id, primary_object_id),
                    attention=self._attention_for(object_type, confidence=confidence),
                    source=self._source_label(fact.source),
                    group=self._groups.get(object_type, "Observações"),
                    problem=fact.value,
                    parent_object_id=None,
                    narrative=narrative,
                    confidence=confidence,
                    supporting_facts=supporting_facts,
                    missing_facts=missing_facts,
                    questions=questions,
                    recommendations=recommendations,
                    children=related_objects,
                    timeline=tuple(timeline_by_object.get(object_id, ())),
                )
            )

        objects.extend(self._reasoning_objects(reasoning, facts, object_id_by_fact, latest_object_id, consultation_complete))
        objects.extend(self._soap_objects(soap, latest_object_id, consultation_complete))

        timeline_entries = [self._timeline_entry(entry, index, objects) for index, entry in enumerate(projection.timeline)]
        timeline_entries.extend(self._reasoning_timeline(reasoning))
        if soap:
            timeline_entries.append({
                "timeline_id": "clinical-timeline-soap",
                "object_id": "soap-progress-consultation",
                "title": "Nota clínica disponível",
                "detail": "O conteúdo está sendo preparado para revisão profissional.",
                "occurred_at": None,
            })
        timeline = tuple(timeline_entries)
        layout = {
            "primary": "clinical-workspace-state",
            "hierarchy": ["patient", "focus", "active_problems", "hypotheses", "evidence", "information_gaps", "next_best_action", "artifacts"],
            "grouping": "clinical-understanding",
            "focused_object_id": self._focused_object_id,
            "widget_lifecycle": sorted(self.WIDGET_LIFECYCLES),
        }
        workspace_state = self._workspace_state(
            projection,
            objects,
            timeline,
            reasoning=reasoning,
            soap=soap,
            primary_object_id=primary_object_id,
            consultation_complete=consultation_complete,
        )
        return PresentationModel(
            version=projection.version,
            objects=tuple(sorted(objects, key=lambda item: (0 if item.lifecycle == "focused" else 1, item.priority, item.title.casefold(), item.object_id))),
            timeline=timeline,
            layout=layout,
            workspace_state=workspace_state,
        )

    def archive(self) -> None:
        """Freeze the Composer state after the encounter leaves the workspace."""

        self._archived_objects.update(self._seen_objects)

    def _widget_lifecycle(self, object_id: str, latest_object_id: str | None, consultation_complete: bool) -> str:
        if object_id in self._archived_objects:
            return "archived"
        if consultation_complete:
            return "resolved"
        if object_id not in self._seen_objects:
            return "emerging"
        age = self._object_ages.get(object_id, 0)
        if age <= 1:
            return "active"
        if object_id == latest_object_id:
            return "focused"
        return "supporting"

    def _reasoning_objects(
        self,
        reasoning: Mapping[str, Any] | None,
        facts: dict[str, Any],
        object_id_by_fact: dict[str, str],
        latest_object_id: str | None,
        consultation_complete: bool,
    ) -> list[ClinicalObject]:
        if not reasoning:
            return []
        raw_questions = [item for item in reasoning.get("questions", []) if isinstance(item, Mapping)]
        hypothesis_by_id = {
            self._stable_value(item, "id", "name"): item
            for item in reasoning.get("hypotheses", [])
            if isinstance(item, Mapping)
        }
        objects: list[ClinicalObject] = []
        for raw in reasoning.get("hypotheses", []):
            if not isinstance(raw, Mapping):
                continue
            raw_id = self._stable_value(raw, "id", "name")
            object_id = f"clinical_hypothesis-{raw_id}"
            supporting = tuple(
                {
                    "fact_id": str(fact_id),
                    "object_id": object_id_by_fact.get(str(fact_id)),
                    "label": "Sustentada por",
                    "title": facts[str(fact_id)].value,
                }
                for fact_id in raw.get("supporting_facts", [])
                if str(fact_id) in facts
            )
            missing = tuple(str(item) for item in raw.get("missing_facts", []))
            questions = tuple(
                str(item.get("text", ""))
                for item in raw_questions
                if str(item.get("hypothesis_id", "")) == raw_id and str(item.get("text", ""))
            )
            children = tuple(
                {
                    "object_id": object_id_by_fact[str(fact_id)],
                    "object_type": "clinical_problem",
                    "title": facts[str(fact_id)].value,
                    "relation": "Sustentada por",
                }
                for fact_id in raw.get("supporting_facts", [])
                if str(fact_id) in object_id_by_fact
            )
            lifecycle = self._widget_lifecycle(object_id, latest_object_id, consultation_complete)
            self._seen_objects.add(object_id)
            self._object_ages[object_id] = self._object_ages.get(object_id, 0) + 1
            objects.append(ClinicalObject(
                object_id=object_id,
                object_type="clinical_hypothesis",
                title=str(raw.get("name", "Hipótese clínica")),
                summary="Hipótese clínica em avaliação profissional.",
                attributes=(),
                # Evidências vivem no ClinicalProblem canônico. A hipótese
                # mantém apenas referências para não renderizar o mesmo fato
                # duas vezes.
                evidence=(),
                lifecycle=lifecycle,
                priority=self._reasoning_priority(raw.get("confidence")),
                attention=self._attention_for("clinical_hypothesis", raw.get("confidence")),
                source="Raciocínio clínico",
                group="Hipóteses",
                problem=str(raw.get("name", "Hipótese clínica")),
                parent_object_id=next((object_id_by_fact.get(str(fact_id)) for fact_id in raw.get("supporting_facts", []) if str(fact_id) in object_id_by_fact), None),
                narrative="Hipótese clínica em avaliação profissional.",
                confidence=float(raw["confidence"]) if raw.get("confidence") is not None else None,
                supporting_facts=supporting,
                missing_facts=missing,
                questions=questions,
                recommendations=tuple(str(item) for item in raw.get("recommendations", []) if str(item).strip()),
                children=children,
                timeline=(),
            ))

        for raw in raw_questions:
            question_id = self._stable_value(raw, "id", "text")
            object_id = f"clinical_question-{question_id}"
            question_hypothesis = hypothesis_by_id.get(str(raw.get("hypothesis_id", "")), {})
            question_parent = next(
                (object_id_by_fact.get(str(fact_id)) for fact_id in question_hypothesis.get("supporting_facts", []) if str(fact_id) in object_id_by_fact),
                None,
            )
            lifecycle = self._widget_lifecycle(object_id, latest_object_id, consultation_complete)
            self._seen_objects.add(object_id)
            self._object_ages[object_id] = self._object_ages.get(object_id, 0) + 1
            objects.append(ClinicalObject(
                object_id=object_id,
                object_type="clinical_question",
                title=str(raw.get("text", "Pergunta clínica")),
                summary=str(raw.get("objective", "Informação ainda precisa ser confirmada.")),
                attributes=(),
                evidence=(),
                lifecycle=lifecycle,
                priority=self._importance_priority(raw.get("importance")),
                attention=self._attention_for("clinical_question", raw.get("importance")),
                source="Raciocínio clínico",
                group="Perguntas",
                problem=str(raw.get("text", "Pergunta clínica")),
                parent_object_id=question_parent,
                narrative=str(raw.get("objective", "Informação ainda precisa ser confirmada.")),
                confidence=None,
                supporting_facts=(),
                missing_facts=(),
                questions=(str(raw.get("text", "")),),
                recommendations=(),
                children=(),
                timeline=(),
            ))
        return objects

    def _soap_objects(self, soap: Mapping[str, Any] | None, latest_object_id: str | None, consultation_complete: bool) -> list[ClinicalObject]:
        if not soap:
            return []
        sections = ("subjective", "objective", "assessment", "plan")
        completed = [section for section in sections if isinstance(soap.get(section), Mapping)]
        progress = len(completed) / len(sections)
        object_id = "soap-progress-consultation"
        lifecycle = self._widget_lifecycle(object_id, latest_object_id, consultation_complete)
        self._seen_objects.add(object_id)
        self._object_ages[object_id] = self._object_ages.get(object_id, 0) + 1
        subjective = soap.get("subjective") if isinstance(soap.get("subjective"), Mapping) else {}
        narrative = str(subjective.get("narrative") or "O resumo clínico está sendo construído a partir da consulta.")
        summary_id = "clinical-summary-consultation"
        summary_lifecycle = self._widget_lifecycle(summary_id, latest_object_id, consultation_complete)
        self._seen_objects.add(summary_id)
        self._object_ages[summary_id] = self._object_ages.get(summary_id, 0) + 1
        return [ClinicalObject(
            object_id=summary_id,
            object_type="clinical_summary",
            title="Resumo clínico",
            summary=narrative,
            attributes=(),
            evidence=(),
            lifecycle=summary_lifecycle,
            priority=65,
            source="Consulta",
            group="Resumo clínico",
            problem="Resumo clínico",
            parent_object_id=None,
            narrative=narrative,
            confidence=progress,
            attention="medium",
            supporting_facts=(),
            missing_facts=tuple(section.title() for section in sections if section not in completed),
            questions=(),
            recommendations=(),
            children=(),
            timeline=(),
        ), ClinicalObject(
            object_id=object_id,
            object_type="soap_progress",
            title="Nota clínica",
            summary="A documentação clínica está sendo preparada para revisão.",
            attributes=tuple({"attribute_id": section, "label": section.title(), "value": "Pronto" if section in completed else "Em construção", "source": "Consulta"} for section in sections),
            evidence=(),
            lifecycle=lifecycle,
            priority=70,
            source="Consulta",
            group="Plano clínico",
            problem="Nota clínica",
            parent_object_id=None,
            narrative="A documentação clínica está sendo preparada para revisão.",
            confidence=progress,
            attention="medium",
            supporting_facts=(),
            missing_facts=tuple(section.title() for section in sections if section not in completed),
            questions=(),
            recommendations=(),
            children=(),
            timeline=(),
        )]

    @staticmethod
    def _stable_value(value: Mapping[str, Any], primary: str, fallback: str) -> str:
        return str(value.get(primary) or value.get(fallback) or "clinical-object")

    @staticmethod
    def _primary_object_id(
        facts: tuple[Any, ...],
        object_id_by_fact: dict[str, str],
        soap: Mapping[str, Any] | None,
    ) -> str | None:
        subjective = soap.get("subjective") if isinstance(soap, Mapping) and isinstance(soap.get("subjective"), Mapping) else {}
        chief_complaint = str(subjective.get("chief_complaint", "")).casefold().strip()
        symptoms = [fact for fact in facts if fact.category.casefold() in {"symptom", "chiefcomplaint"}]
        if chief_complaint:
            matching = next((fact for fact in symptoms if fact.value.casefold() in chief_complaint or chief_complaint in fact.value.casefold()), None)
            if matching is not None:
                return object_id_by_fact.get(matching.fact_id)
        return object_id_by_fact.get(symptoms[0].fact_id) if symptoms else None

    def _object_priority(self, category: str, object_id: str, primary_object_id: str | None) -> int:
        if object_id == primary_object_id:
            return 0
        return self._priorities.get(category, 60)

    @staticmethod
    def _reasoning_priority(confidence: float | str | None) -> int:
        try:
            value = float(confidence) if confidence is not None else 0
        except (TypeError, ValueError):
            value = 0
        return 10 if value >= 0.7 else 20 if value >= 0.4 else 30

    @staticmethod
    def _importance_priority(importance: str | None) -> int:
        return {"critical": 0, "high": 10, "medium": 20, "low": 30}.get(str(importance or "").casefold(), 20)

    def _workspace_state(
        self,
        projection: KnowledgeProjection,
        objects: list[ClinicalObject],
        timeline: tuple[dict[str, Any], ...],
        *,
        reasoning: Mapping[str, Any] | None,
        soap: Mapping[str, Any] | None,
        primary_object_id: str | None,
        consultation_complete: bool,
    ) -> dict[str, Any]:
        by_type = lambda object_type: [item for item in objects if item.object_type == object_type]
        primary = next((item for item in objects if item.object_id == primary_object_id), None)
        problems = by_type("clinical_problem")
        hypotheses = by_type("clinical_hypothesis")
        questions = by_type("clinical_question")
        gaps = [dict(item) for item in (reasoning or {}).get("information_gaps", []) if isinstance(item, Mapping)]
        pending_questions = [
            {
                "id": item.object_id,
                "question": item.title,
                "reason": item.summary,
                "priority": item.priority,
                "attention": item.attention,
                "hypothesis_id": str(next((value.get("hypothesis_id") for value in gaps if value.get("question") == item.title), "")),
            }
            for item in questions
        ]
        pending_questions.sort(key=lambda item: (item["priority"], item["question"].casefold()))
        next_decision = pending_questions[0] if pending_questions else None
        recommendations = [
            {
                "id": f"recommendation-{item.object_id}-{index}",
                "object_id": item.object_id,
                "title": recommendation,
                "summary": "Ação sugerida pelo Runtime para reduzir uma lacuna clínica.",
                "priority": item.priority,
                "status": "sugerida",
            }
            for item in objects
            for index, recommendation in enumerate(item.recommendations)
        ]
        confidence = primary.confidence if primary is not None else None
        problem_payload = [
            {
                "id": item.object_id,
                "title": item.title,
                "narrative": item.narrative,
                "summary": item.summary,
                "stage": "investigation" if not consultation_complete else "review",
                "priority": item.priority,
                "confidence": item.confidence,
                "attributes": [dict(value) for value in item.attributes],
                "evidence": [dict(value) for value in item.evidence],
                "supporting_facts": [dict(value) for value in item.supporting_facts],
                "missing_facts": list(item.missing_facts),
                "questions": list(item.questions),
                "related_problems": [dict(value) for value in item.children],
                "timeline": [dict(value) for value in item.timeline],
            }
            for item in problems
        ]
        hypothesis_payload = [
            {
                "id": item.object_id,
                "title": item.title,
                "confidence": item.confidence,
                "priority": item.priority,
                "attention": item.attention,
                "status": "em avaliação" if not consultation_complete else "pronta para revisão",
                "supporting_facts": [dict(value) for value in item.supporting_facts],
                "missing_facts": list(item.missing_facts),
                "conflicting_facts": [],
            }
            for item in hypotheses
        ]
        all_facts = [fact.to_dict() for fact in projection.facts]
        soap_sections = ("subjective", "objective", "assessment", "plan")
        soap_progress = (
            sum(isinstance(soap.get(section), Mapping) for section in soap_sections) / len(soap_sections)
            if isinstance(soap, Mapping)
            else 0
        )
        artifacts = [{
            "type": "soap",
            "status": "ready" if soap else "building",
            "confidence": soap_progress,
        }]
        return {
            "schema": "astera.clinical-workspace-state/v1",
            "version": projection.version,
            "patient": {"id": projection.facts[0].patient_id if projection.facts else None},
            "encounter": {"id": projection.facts[0].encounter_id if projection.facts else None, "status": "completed" if consultation_complete else "in_progress"},
            "focus": {
                "object_id": primary.object_id if primary else None,
                "title": primary.title if primary else None,
                "reason": primary.narrative if primary else "O Runtime está acompanhando o relato.",
                "urgency": primary.attention if primary else "medium",
                "confidence": confidence,
                "stage": "review" if consultation_complete else "investigation",
            },
            "active_problems": problem_payload,
            "story": {"current_moment": f"Investigando {primary.title}" if primary else "Ouvindo o relato", "previous_moments": [dict(item) for item in timeline]},
            "decisions": {"next": next_decision},
            "evidence": all_facts,
            "hypotheses": hypothesis_payload,
            "information_gaps": gaps,
            "pending_questions": pending_questions,
            "next_best_action": next_decision,
            "recommendations": recommendations,
            "confidence": confidence,
            "risk": "attention" if any(item.attention in {"critical", "high"} for item in hypotheses) else "routine",
            "artifacts": artifacts,
            "knowledge_graph": {"relationships": list((projection.graph or {}).get("edges", []))},
        }

    def _timeline_entry(self, entry: dict[str, Any], index: int, objects: list[ClinicalObject]) -> dict[str, Any]:
        category = str(entry.get("category", "")).casefold()
        lifecycle = str(entry.get("lifecycle", "created")).casefold()
        title = self._cognitive_timeline_title(category, lifecycle, index)
        object_id = next((item.object_id for item in objects if item.title.casefold() == str(entry.get("value", "")).casefold()), None)
        return {
            "timeline_id": str(entry.get("timeline_id", f"clinical-timeline-{index}")),
            "object_id": object_id,
            "title": title,
            "detail": str(entry.get("value", "Informação clínica recebida")),
            "role": "attribute" if category in self._attribute_categories else "clinical-object",
            "occurred_at": entry.get("occurred_at"),
        }

    @staticmethod
    def _reasoning_timeline(reasoning: Mapping[str, Any] | None) -> list[dict[str, Any]]:
        if not reasoning:
            return []
        entries: list[dict[str, Any]] = []
        for index, hypothesis in enumerate(reasoning.get("hypotheses", [])):
            if not isinstance(hypothesis, Mapping):
                continue
            entries.append({
                "timeline_id": f"clinical-timeline-hypothesis-{index}",
                "object_id": f"clinical_hypothesis-{ClinicalPresentationComposer._stable_value(hypothesis, 'id', 'name')}",
                "title": "Hipótese em construção",
                "detail": str(hypothesis.get("name", "Hipótese clínica")),
                "occurred_at": None,
            })
        for index, question in enumerate(reasoning.get("questions", [])):
            if not isinstance(question, Mapping):
                continue
            entries.append({
                "timeline_id": f"clinical-timeline-question-{index}",
                "object_id": f"clinical_question-{ClinicalPresentationComposer._stable_value(question, 'id', 'text')}",
                "title": "Pergunta sugerida",
                "detail": str(question.get("text", "Informação a confirmar")),
                "occurred_at": None,
            })
        return entries

    @classmethod
    def _cognitive_timeline_title(cls, category: str, lifecycle: str, index: int) -> str:
        if index == 0 and category not in cls._attribute_categories:
            return "Paciente iniciou o relato"
        if category in {"symptom", "chiefcomplaint"} and lifecycle == "created":
            return "Problema identificado"
        if category in cls._attribute_categories:
            return "Problema enriquecido"
        if category == "condition":
            return "Antecedente encontrado"
        if category == "medication":
            return "Tratamento identificado"
        if category == "allergy":
            return "Alergia identificada"
        if lifecycle in {"validated", "completed"}:
            return "Informação confirmada"
        if lifecycle == "growing":
            return "Informação complementada"
        return "Informação clínica relacionada"

    @staticmethod
    def _attention_for(object_type: str, confidence: float | str | None = None) -> str:
        if object_type == "clinical_question":
            normalized = str(confidence or "").casefold()
            return normalized if normalized in {"critical", "high", "medium", "low"} else "high"
        if object_type == "clinical_hypothesis":
            value = float(confidence) if confidence is not None else 0
            return "high" if value >= 0.7 else "medium" if value >= 0.4 else "low"
        if object_type == "clinical_problem":
            return "high"
        return "medium"

    @staticmethod
    def _timeline_title(lifecycle: str) -> str:
        normalized = lifecycle.casefold()
        if normalized == "growing":
            return "Informação complementar"
        if normalized in {"validated", "completed"}:
            return "Informação confirmada"
        return "Novo achado identificado"

    @staticmethod
    def _confidence(fact: Any, related: list[dict[str, Any]]) -> float | None:
        values = [fact.confidence, *(item["fact"].confidence for item in related if item["fact"] is not None)]
        values = [float(value) for value in values if value is not None]
        return round(sum(values) / len(values), 3) if values else None

    @staticmethod
    def _missing_information(object_type: str, attributes: tuple[dict[str, Any], ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if object_type != "clinical_problem":
            return (), ()
        present = {str(attribute["label"]) for attribute in attributes}
        prompts = {
            "Duração": "Há quanto tempo esse sintoma começou?",
            "Intensidade": "Qual é a intensidade do sintoma?",
            "Localização": "Onde exatamente o sintoma aparece?",
        }
        missing = tuple(label for label in prompts if label not in present)
        return missing, tuple(prompts[label] for label in missing)

    @staticmethod
    def _recommendations_for(missing_facts: tuple[str, ...]) -> tuple[str, ...]:
        actions = {
            "Duração": "Confirmar há quanto tempo o sintoma começou.",
            "Intensidade": "Registrar a intensidade da dor na escala EVA.",
            "Localização": "Confirmar a localização exata do sintoma.",
        }
        return tuple(actions[label] for label in missing_facts if label in actions)

    @staticmethod
    def _object_type(category: str) -> str:
        if category in {"symptom", "chiefcomplaint"}:
            return "clinical_problem"
        if category == "condition":
            return "clinical_history"
        if category == "medication":
            return "medication_profile"
        if category == "allergy":
            return "allergy_profile"
        if category in {"question", "open_question"}:
            return "investigation"
        return "clinical_observation"

    @staticmethod
    def _relationship_label(relationship: str, category: str) -> str:
        normalized = relationship.casefold()
        if "duration" in normalized or category in {"duration", "temporal"}:
            return "Duração"
        if "severity" in normalized or "intens" in normalized or category in {"severity", "intensity"}:
            return "Intensidade"
        if "location" in normalized or "anatom" in normalized or category in {"location", "anatomy"}:
            return "Localização"
        return "Informação relacionada"

    @staticmethod
    def _source_label(source: str) -> str:
        normalized = source.casefold()
        if "speech" in normalized or "audio" in normalized or "patient" in normalized:
            return "Paciente"
        if "clinician" in normalized or "professional" in normalized:
            return "Profissional de saúde"
        return "Consulta"

    @staticmethod
    def _summary(object_type: str, title: str, lifecycle: str) -> str:
        if object_type == "clinical_problem":
            return f"O paciente trouxe {title} durante o relato da consulta."
        if object_type == "clinical_history":
            return "Histórico clínico identificado no relato."
        if object_type == "medication_profile":
            return "Medicação mencionada durante a consulta."
        if object_type == "allergy_profile":
            return "Alergia mencionada durante a consulta."
        return "Informação clínica identificada durante a consulta."
