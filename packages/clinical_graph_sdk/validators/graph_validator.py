"""Structural and provenance validation for Clinical Graphs."""
from __future__ import annotations

from ..models import ClinicalGraph


class ClinicalGraphValidationError(ValueError):
    """Raised when a Clinical Graph violates its domain invariants."""


class GraphValidator:
    def validate(self, graph: ClinicalGraph) -> None:
        node_ids = {node.node_id for node in graph.nodes}
        if len(node_ids) != len(graph.nodes):
            raise ClinicalGraphValidationError("Clinical Graph contains duplicate node ids")
        if len({edge.edge_id for edge in graph.edges}) != len(graph.edges):
            raise ClinicalGraphValidationError("Clinical Graph contains duplicate edge ids")
        if any(node.encounter_id != graph.encounter_id for node in graph.nodes):
            raise ClinicalGraphValidationError("Clinical Graph node encounter does not match graph encounter")
        if any(edge.source_node_id not in node_ids or edge.target_node_id not in node_ids for edge in graph.edges):
            raise ClinicalGraphValidationError("Clinical Graph edge references an unknown node")
        if set(graph.source_fact_ids) != {node.fact_id for node in graph.nodes}:
            raise ClinicalGraphValidationError("Clinical Graph must preserve every source Clinical Fact")
