"""Immutable Clinical Graph models built from Clinical Facts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ClinicalGraphNode:
    node_id: str
    node_type: str
    value: str
    fact_id: str
    subject_id: str
    encounter_id: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (
            self.node_id, self.node_type, self.value, self.fact_id, self.subject_id, self.encounter_id,
        )):
            raise ValueError("Clinical Graph node identity and semantic fields must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.node_id,
            "type": self.node_type,
            "value": self.value,
            "fact_id": self.fact_id,
            "subject": self.subject_id,
            "encounter": self.encounter_id,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ClinicalGraphEdge:
    edge_id: str
    relationship_type: str
    source_node_id: str
    target_node_id: str
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (
            self.edge_id, self.relationship_type, self.source_node_id, self.target_node_id,
        )):
            raise ValueError("Clinical Graph edge identity and relationship fields must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.edge_id,
            "type": self.relationship_type,
            "source": self.source_node_id,
            "target": self.target_node_id,
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True, slots=True)
class ClinicalGraph:
    graph_id: str
    version: int
    patient_id: str
    encounter_id: str
    nodes: tuple[ClinicalGraphNode, ...]
    edges: tuple[ClinicalGraphEdge, ...]
    source_fact_ids: tuple[str, ...]
    provenance: Mapping[str, Any] = field(default_factory=dict)
    status: str = "candidate"

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (
            self.graph_id, self.patient_id, self.encounter_id, self.status,
        )):
            raise ValueError("Clinical Graph identity and status must not be empty")
        if self.version < 1:
            raise ValueError("Clinical Graph version must be at least 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "version": self.version,
            "patient_id": self.patient_id,
            "encounter_id": self.encounter_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "source_fact_ids": list(self.source_fact_ids),
            "provenance": dict(self.provenance),
            "status": self.status,
        }
