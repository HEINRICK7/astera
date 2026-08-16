from __future__ import annotations

import unittest
from datetime import datetime, timezone

from apps.runtime.src.adapters.cognitive import KeywordClinicalNlp
from apps.runtime.src.application.clinical.knowledge_layer import ClinicalKnowledgeLayer
from packages.clinical_facts_sdk import DeterministicClinicalFactsExtractor
from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch
from packages.medical_nlp_sdk import NlpRequest


class ClinicalKnowledgeLayerTests(unittest.IsolatedAsyncioTestCase):
    async def test_facts_are_reduced_into_graph_and_card_projection(self):
        result = await KeywordClinicalNlp().process(
            NlpRequest(
                request_id="speech-1",
                text="Estou com dor de cabeça há 5 dias",
                language="pt-BR",
            )
        )
        batch = await DeterministicClinicalFactsExtractor().extract(
            encounter_id="encounter-1",
            subject_id="patient-1",
            patient_id="patient-1",
            result=result,
            observed_at=datetime.now(timezone.utc),
        )
        projection = ClinicalKnowledgeLayer().apply(batch, source="speech")

        self.assertEqual(projection.version, 1)
        self.assertEqual(len(projection.cards), 2)
        self.assertEqual(projection.cards[0]["lifecycle"], "created")
        self.assertIsNotNone(projection.graph)
        self.assertTrue(any(edge["type"] == "HAS_DURATION" for edge in projection.graph["edges"]))
        self.assertEqual(projection.events[0].event_type, "clinical.knowledge.fact.upserted")

    async def test_same_semantic_fact_is_updated_without_duplicate_timeline_card(self):
        now = datetime.now(timezone.utc)
        first = ClinicalFact(
            fact_id="fact-segment-1",
            category="Symptom",
            value="Dor de cabeça",
            subject_id="patient-1",
            encounter_id="encounter-upsert",
            source="speech",
            provenance={"source_ref": "segment-1"},
            code="symptom.headache",
            ontology="ASTERA-CONCEPT",
            observed_at=now,
        )
        second = ClinicalFact(
            fact_id="fact-segment-2",
            category="Symptom",
            value="Dor de cabeça",
            subject_id="patient-1",
            encounter_id="encounter-upsert",
            source="speech",
            provenance={"source_ref": "segment-2"},
            code="symptom.headache",
            ontology="ASTERA-CONCEPT",
            observed_at=now,
        )
        layer = ClinicalKnowledgeLayer()
        layer.apply(ClinicalFactsBatch(encounter_id="encounter-upsert", items=(first,)), source="speech")
        projection = layer.apply(ClinicalFactsBatch(encounter_id="encounter-upsert", items=(second,)), source="speech")

        self.assertEqual(len(projection.facts), 1)
        self.assertEqual(projection.facts[0].fact_id, "fact-segment-1")
        self.assertEqual(len(projection.timeline), 1)
        self.assertEqual(projection.timeline[0]["update_count"], 2)
        self.assertEqual(len(projection.history), 2)


if __name__ == "__main__":
    unittest.main()
