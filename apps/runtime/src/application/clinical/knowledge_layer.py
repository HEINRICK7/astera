"""Clinical Knowledge Layer: graph and derived cards from stable evidence."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch
from packages.clinical_graph_sdk import ClinicalGraphBuilder

from .evidence_store import EvidenceProjection, EvidenceStore


@dataclass(frozen=True, slots=True)
class KnowledgeEvent:
    """Provider-neutral change emitted after evidence enters the graph."""

    event_id: str
    encounter_id: str
    source: str
    event_type: str
    fact_id: str
    category: str
    value: str
    lifecycle: str
    occurred_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "encounter_id": self.encounter_id,
            "source": self.source,
            "event_type": self.event_type,
            "fact_id": self.fact_id,
            "category": self.category,
            "value": self.value,
            "lifecycle": self.lifecycle,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class KnowledgeProjection:
    version: int
    facts: tuple[ClinicalFact, ...]
    graph: dict[str, Any] | None
    cards: tuple[dict[str, Any], ...]
    events: tuple[KnowledgeEvent, ...]
    timeline: tuple[dict[str, Any], ...]
    history: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "facts": [fact.to_dict() for fact in self.facts],
            "graph": self.graph,
            "cards": [dict(card) for card in self.cards],
            "events": [event.to_dict() for event in self.events],
            "timeline": [dict(entry) for entry in self.timeline],
            "history": [dict(entry) for entry in self.history],
        }


class ClinicalKnowledgeLayer:
    """Build a clinical graph from the deduplicated Evidence Store."""

    def __init__(self) -> None:
        self._evidence_store = EvidenceStore()
        self._graph_builder = ClinicalGraphBuilder()

    @property
    def facts(self) -> tuple[ClinicalFact, ...]:
        return self._evidence_store.facts

    def apply(self, batch: ClinicalFactsBatch, *, source: str) -> KnowledgeProjection:
        evidence = self._evidence_store.apply(batch, source=source)
        events = tuple(
            KnowledgeEvent(
                event_id=event.event_id.replace("evidence-", "knowledge-", 1),
                encounter_id=event.encounter_id,
                source=event.source,
                event_type="clinical.knowledge.fact.upserted",
                fact_id=event.fact_id,
                category=event.category,
                value=event.value,
                lifecycle=event.lifecycle,
                occurred_at=event.occurred_at,
            )
            for event in evidence.events
        )
        return self._projection(batch.encounter_id, evidence, events)

    def _projection(
        self,
        encounter_id: str,
        evidence: EvidenceProjection,
        events: tuple[KnowledgeEvent, ...],
    ) -> KnowledgeProjection:
        graph = None
        if evidence.facts:
            graph = self._graph_builder.build(
                ClinicalFactsBatch(encounter_id=encounter_id, items=evidence.facts),
                version=max(1, evidence.version),
            ).to_dict()

        edges_by_node: dict[str, list[str]] = {fact.fact_id: [] for fact in evidence.facts}
        if graph:
            fact_values = {fact.fact_id: fact.value for fact in evidence.facts}
            for edge in graph["edges"]:
                source_value = fact_values.get(edge["source"])
                target_value = fact_values.get(edge["target"])
                if source_value and target_value:
                    edges_by_node[edge["source"]].append(f"{edge['type']}: {target_value}")
                    edges_by_node[edge["target"]].append(f"{edge['type']}: {source_value}")

        cards = tuple(
            {
                "card_id": fact.fact_id,
                "graph_node_id": fact.fact_id,
                "lifecycle": evidence.lifecycles.get(fact.fact_id, "created"),
                "fact": fact.to_dict(),
                "metadata": edges_by_node.get(fact.fact_id, []),
            }
            for fact in evidence.facts
        )
        return KnowledgeProjection(
            version=evidence.version,
            facts=evidence.facts,
            graph=graph,
            cards=cards,
            events=events,
            timeline=evidence.timeline,
            history=evidence.history,
        )
