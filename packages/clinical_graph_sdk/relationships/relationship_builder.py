"""Deterministic relationships between facts that belong to one encounter."""
from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence

from packages.clinical_facts_sdk import ClinicalFact

from ..models import ClinicalGraphEdge, ClinicalGraphNode


ROOT_TYPES = frozenset({
    "symptom", "condition", "medication", "observation", "allergy", "exam", "procedure", "lifestyle",
})

ATTRIBUTE_TARGETS: dict[str, tuple[str, ...]] = {
    "duration": ("symptom", "condition", "observation"),
    "severity": ("symptom", "observation"),
    "anatomy": ("symptom", "observation"),
    "location": ("symptom", "observation"),
    "aggravating_factor": ("symptom", "condition"),
    "alleviating_factor": ("symptom", "condition"),
    "trigger": ("symptom", "condition"),
    "relief": ("symptom", "condition"),
    "dosage": ("medication",),
    "dose": ("medication",),
    "frequency": ("medication",),
    "route": ("medication",),
    "laterality": ("symptom", "observation"),
}

RELATIONSHIP_TYPES = {
    "duration": "HAS_DURATION",
    "severity": "HAS_SEVERITY",
    "anatomy": "HAS_LOCATION",
    "location": "HAS_LOCATION",
    "aggravating_factor": "HAS_TRIGGER",
    "trigger": "HAS_TRIGGER",
    "alleviating_factor": "HAS_RELIEF",
    "relief": "HAS_RELIEF",
    "dosage": "HAS_DOSAGE",
    "dose": "HAS_DOSAGE",
    "frequency": "HAS_FREQUENCY",
    "route": "HAS_ROUTE",
    "laterality": "HAS_LATERALITY",
}


class RelationshipBuilder:
    """Build explainable edges without changing or enriching Clinical Facts."""

    def build(
        self,
        *,
        facts: Sequence[ClinicalFact],
        nodes: Sequence[ClinicalGraphNode],
    ) -> tuple[ClinicalGraphEdge, ...]:
        node_by_fact = {node.fact_id: node for node in nodes}
        latest_root: dict[str, ClinicalGraphNode] = {}
        edges: list[ClinicalGraphEdge] = []
        for fact in facts:
            node = node_by_fact[fact.fact_id]
            category = normalize_category(fact.category)
            if category in ROOT_TYPES:
                if category == "medication" and "condition" in latest_root:
                    edges.append(self._edge("HAS_MEDICATION", latest_root["condition"], node, fact))
                latest_root[category] = node
                continue
            targets = ATTRIBUTE_TARGETS.get(category, ())
            target = next((latest_root[item] for item in targets if item in latest_root), None)
            if target is not None:
                edges.append(self._edge(RELATIONSHIP_TYPES[category], target, node, fact))
        return tuple(edges)

    @staticmethod
    def _edge(
        relationship_type: str,
        source: ClinicalGraphNode,
        target: ClinicalGraphNode,
        fact: ClinicalFact,
    ) -> ClinicalGraphEdge:
        digest = hashlib.sha256(f"{source.node_id}:{relationship_type}:{target.node_id}".encode()).hexdigest()[:16]
        return ClinicalGraphEdge(
            edge_id=f"edge-{digest}",
            relationship_type=relationship_type,
            source_node_id=source.node_id,
            target_node_id=target.node_id,
            provenance={
                "builder": "relationship-builder",
                "origin": "inferred_from_clinical_facts",
                "source_fact_id": fact.fact_id,
                "source_ref": fact.provenance.get("source_ref"),
                "request_id": fact.provenance.get("request_id"),
                "observed_at": fact.observed_at.isoformat() if fact.observed_at else None,
                "valid_at": fact.valid_at.isoformat() if fact.valid_at else None,
                "confidence": fact.confidence,
            },
        )


def normalize_category(category: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", category.casefold()).strip("_")
    return {
        "behaviour": "lifestyle",
        "behavior": "lifestyle",
        "habit": "lifestyle",
    }.get(normalized, normalized)
