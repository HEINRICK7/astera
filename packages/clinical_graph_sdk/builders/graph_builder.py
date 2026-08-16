"""Build a semantic graph while preserving the original Clinical Facts."""
from __future__ import annotations

import hashlib

from packages.clinical_facts_sdk import ClinicalFactsBatch

from ..models import ClinicalGraph, ClinicalGraphNode
from ..relationships.relationship_builder import ROOT_TYPES, RelationshipBuilder, normalize_category
from ..validators.graph_validator import GraphValidator


class ClinicalGraphBuilder:
    """Convert one Clinical Facts batch into a versioned Clinical Graph."""

    def __init__(self, relationship_builder: RelationshipBuilder | None = None) -> None:
        self._relationships = relationship_builder or RelationshipBuilder()

    def build(self, facts: ClinicalFactsBatch, *, version: int = 1) -> ClinicalGraph:
        if not facts.items:
            raise ValueError("Clinical Graph requires at least one Clinical Fact")
        patient_ids = {fact.patient_id or fact.subject_id for fact in facts.items}
        if len(patient_ids) != 1:
            raise ValueError("Clinical Graph requires one patient subject")
        patient_id = next(iter(patient_ids))
        nodes = tuple(
            ClinicalGraphNode(
                node_id=fact.fact_id,
                node_type=normalize_category(fact.category) if normalize_category(fact.category) in ROOT_TYPES else "attribute",
                value=fact.value,
                fact_id=fact.fact_id,
                subject_id=fact.subject_id,
                encounter_id=fact.encounter_id,
                provenance={
                    "origin": "transcript",
                    "source": fact.source,
                    "source_fact_id": fact.fact_id,
                    "source_ref": fact.provenance.get("source_ref"),
                    "request_id": fact.provenance.get("request_id"),
                    "observed_at": fact.observed_at.isoformat() if fact.observed_at else None,
                    "valid_at": fact.valid_at.isoformat() if fact.valid_at else None,
                    "confidence": fact.confidence,
                },
                metadata={
                    "category": fact.category,
                    "unit": fact.unit,
                    "certainty": fact.certainty,
                    "polarity": fact.polarity,
                    "source": fact.source,
                    "fact_metadata": dict(fact.metadata),
                },
            )
            for fact in facts.items
        )
        graph_id = self._graph_id(facts.encounter_id, version)
        graph = ClinicalGraph(
            graph_id=graph_id,
            version=version,
            patient_id=patient_id,
            encounter_id=facts.encounter_id,
            nodes=nodes,
            edges=self._relationships.build(facts=facts.items, nodes=nodes),
            source_fact_ids=tuple(fact.fact_id for fact in facts.items),
            provenance={"builder": "clinical-graph-builder", "source_encounter": facts.encounter_id},
        )
        GraphValidator().validate(graph)
        return graph

    @staticmethod
    def _graph_id(encounter_id: str, version: int) -> str:
        digest = hashlib.sha256(f"{encounter_id}:{version}".encode()).hexdigest()[:16]
        return f"clinical-graph-{digest}"
