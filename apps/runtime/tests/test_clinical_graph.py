from __future__ import annotations

import unittest

from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch
from packages.clinical_graph_sdk import ClinicalGraphBuilder


class ClinicalGraphTests(unittest.TestCase):
    def test_groups_symptom_attributes_and_condition_treatment(self) -> None:
        encounter = "encounter-graph-1"
        patient = "patient-1"

        def fact(fact_id: str, category: str, value: str) -> ClinicalFact:
            return ClinicalFact(
                fact_id=fact_id,
                category=category,
                value=value,
                subject_id=patient,
                patient_id=patient,
                encounter_id=encounter,
                source="grok",
                provenance={"request_id": "graph-test"},
            )

        graph = ClinicalGraphBuilder().build(ClinicalFactsBatch(encounter, (
            fact("f-symptom", "symptom", "dor de cabeça"),
            fact("f-duration", "duration", "cinco dias"),
            fact("f-severity", "severity", "8/10"),
            fact("f-location", "anatomy", "testa"),
            fact("f-condition", "condition", "hipertensão"),
            fact("f-medication", "medication", "Losartana"),
            fact("f-dose", "dosage", "50 mg"),
            fact("f-frequency", "frequency", "todos os dias"),
        )))

        relationships = {(edge.relationship_type, edge.source_node_id, edge.target_node_id) for edge in graph.edges}
        self.assertEqual(len(graph.nodes), 8)
        self.assertIn(("HAS_DURATION", "f-symptom", "f-duration"), relationships)
        self.assertIn(("HAS_SEVERITY", "f-symptom", "f-severity"), relationships)
        self.assertIn(("HAS_LOCATION", "f-symptom", "f-location"), relationships)
        self.assertIn(("HAS_MEDICATION", "f-condition", "f-medication"), relationships)
        self.assertIn(("HAS_DOSAGE", "f-medication", "f-dose"), relationships)
        self.assertIn(("HAS_FREQUENCY", "f-medication", "f-frequency"), relationships)
        self.assertEqual(graph.nodes[0].provenance["origin"], "transcript")
        self.assertEqual(graph.nodes[0].provenance["source_fact_id"], "f-symptom")
        self.assertTrue(all(edge.provenance["source_fact_id"] for edge in graph.edges))

    def test_preserves_all_source_facts(self) -> None:
        fact = ClinicalFact(
            fact_id="f-1", category="allergy", value="penicilina", subject_id="patient-1",
            patient_id="patient-1", encounter_id="encounter-1", source="grok", provenance={"source": "test"},
        )
        graph = ClinicalGraphBuilder().build(ClinicalFactsBatch("encounter-1", (fact,)))
        self.assertEqual(graph.source_fact_ids, ("f-1",))
        self.assertEqual(graph.nodes[0].node_type, "allergy")

    def test_graph_identity_does_not_depend_on_raw_transcript(self) -> None:
        fact = ClinicalFact(
            fact_id="f-symptom", category="symptom", value="dor", subject_id="patient-1",
            patient_id="patient-1", encounter_id="encounter-1", source="grok",
            provenance={"source_ref": "audio-1:0-3", "request_id": "audio-1"},
        )
        graph = ClinicalGraphBuilder().build(ClinicalFactsBatch("encounter-1", (fact,)))
        serialized = graph.to_dict()
        self.assertNotIn("transcript", serialized)
        self.assertEqual(serialized["nodes"][0]["value"], "dor")
        self.assertEqual(serialized["source_fact_ids"], ["f-symptom"])
