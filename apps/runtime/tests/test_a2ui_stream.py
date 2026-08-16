from __future__ import annotations

import unittest
from datetime import datetime, timezone

from apps.runtime.src.adapters.cognitive import KeywordClinicalNlp
from apps.runtime.src.application.clinical.a2ui_stream import ClinicalA2UIProjector
from apps.runtime.src.application.clinical.knowledge_layer import ClinicalKnowledgeLayer
from apps.runtime.src.application.clinical.presentation_composer import ClinicalPresentationComposer
from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch, DeterministicClinicalFactsExtractor
from packages.medical_nlp_sdk import NlpRequest


class A2UICognitiveStreamTests(unittest.IsolatedAsyncioTestCase):
    async def test_knowledge_changes_are_incremental_cpp_operations(self):
        nlp = await KeywordClinicalNlp().process(
            NlpRequest(request_id="speech-1", text="dor de cabeça", language="pt-BR")
        )
        batch = await DeterministicClinicalFactsExtractor().extract(
            encounter_id="encounter-1",
            subject_id="patient-1",
            patient_id="patient-1",
            result=nlp,
            observed_at=datetime.now(timezone.utc),
        )
        knowledge = ClinicalKnowledgeLayer()
        projection = knowledge.apply(batch, source="speech")
        composer = ClinicalPresentationComposer()
        presentation = composer.compose(projection)
        projector = ClinicalA2UIProjector()

        created = projector.project(presentation)
        patched = projector.project(presentation)
        validated = projector.validate()

        self.assertEqual(created[0]["op"], "state")
        self.assertEqual(patched, ())
        self.assertEqual(validated[0]["op"], "patch")
        self.assertNotIn("component", created[0])
        self.assertEqual(created[0]["state"]["schema"], "astera.clinical-workspace-state/v1")
        self.assertEqual(created[0]["state"]["focus"]["title"], "dor de cabeça")
        self.assertEqual(created[0]["state"]["active_problems"][0]["title"], "dor de cabeça")
        self.assertTrue(any(item["op"] == "create" and item["component"] == "ClinicalProblemCard" for item in created))
        self.assertTrue(any(item["op"] == "create" and item["id"] == "knowledge-timeline" for item in created))

    async def test_entities_are_composed_into_one_clinical_problem_object(self):
        now = datetime.now(timezone.utc)
        facts = tuple(
            ClinicalFact(
                fact_id=f"fact-{index}",
                category=category,
                value=value,
                subject_id="patient-1",
                encounter_id="encounter-2",
                source="speech",
                provenance={"source": "test"},
                observed_at=now,
            )
            for index, (category, value) in enumerate((
                ("symptom", "dor de cabeça"),
                ("duration", "5 dias"),
                ("severity", "8/10"),
                ("location", "frontal"),
            ), start=1)
        )
        projection = ClinicalKnowledgeLayer().apply(ClinicalFactsBatch(encounter_id="encounter-2", items=facts), source="speech")
        presentation = ClinicalPresentationComposer().compose(projection)

        self.assertEqual(len(presentation.objects), 1)
        clinical_problem = presentation.objects[0]
        self.assertEqual(clinical_problem.object_type, "clinical_problem")
        self.assertEqual({attribute["label"] for attribute in clinical_problem.attributes}, {"Duração", "Intensidade", "Localização"})
        operations = ClinicalA2UIProjector().project(presentation)
        state = operations[0]
        self.assertEqual(state["op"], "state")
        self.assertEqual(state["state"]["active_problems"][0]["title"], "dor de cabeça")
        problem = next(item for item in operations if item.get("component") == "ClinicalProblemCard")
        self.assertEqual(problem["props"]["attributes"][0]["value"], "5 dias")

    async def test_composer_keeps_one_focused_object_and_groups_attributes(self):
        now = datetime.now(timezone.utc)
        facts = tuple(
            ClinicalFact(
                fact_id=f"fact-{index}",
                category=category,
                value=value,
                subject_id="patient-1",
                encounter_id="encounter-3",
                source="speech",
                provenance={"source": "test"},
                observed_at=now,
            )
            for index, (category, value) in enumerate((
                ("symptom", "dor de cabeça"),
                ("condition", "hipertensão"),
            ), start=1)
        )
        knowledge = ClinicalKnowledgeLayer()
        composer = ClinicalPresentationComposer()
        projection = knowledge.apply(ClinicalFactsBatch(encounter_id="encounter-3", items=(facts[0],)), source="speech")
        composer.compose(projection)
        projection = knowledge.apply(ClinicalFactsBatch(encounter_id="encounter-3", items=(facts[1],)), source="speech")
        composer.compose(projection)
        composer.compose(projection)
        presentation = composer.compose(projection)

        self.assertEqual(sum(item.lifecycle == "focused" for item in presentation.objects), 1)
        self.assertIn("supporting", {item.lifecycle for item in presentation.objects})
        self.assertEqual({item.group for item in presentation.objects}, {"Problemas principais", "Antecedentes"})
        self.assertTrue(all(item.lifecycle in composer.WIDGET_LIFECYCLES for item in presentation.objects))

    async def test_patch_exposes_the_clinical_change_for_theater(self):
        now = datetime.now(timezone.utc)
        first = ClinicalFact(
            fact_id="fact-confidence-1",
            category="symptom",
            value="dor de cabeça",
            subject_id="patient-1",
            encounter_id="encounter-diff",
            source="speech",
            provenance={"source": "segment-1"},
            code="symptom.headache",
            confidence=0.82,
            observed_at=now,
        )
        second = ClinicalFact(
            fact_id="fact-confidence-2",
            category="symptom",
            value="dor de cabeça",
            subject_id="patient-1",
            encounter_id="encounter-diff",
            source="speech",
            provenance={"source": "segment-2"},
            code="symptom.headache",
            confidence=0.91,
            observed_at=now,
        )
        knowledge = ClinicalKnowledgeLayer()
        composer = ClinicalPresentationComposer()
        projector = ClinicalA2UIProjector()
        projector.project(composer.compose(knowledge.apply(ClinicalFactsBatch(encounter_id="encounter-diff", items=(first,)), source="speech")))
        operations = projector.project(composer.compose(knowledge.apply(ClinicalFactsBatch(encounter_id="encounter-diff", items=(second,)), source="speech")))

        patch = next(item for item in operations if item.get("op") == "patch" and item.get("id", "").startswith("clinical_problem-"))
        self.assertEqual(patch["target"]["title"], "dor de cabeça")
        self.assertEqual(patch["diff"]["confidence"]["from"], 0.82)
        self.assertEqual(patch["diff"]["confidence"]["to"], 0.91)

    async def test_reasoning_and_soap_become_clinical_workspace_objects(self):
        now = datetime.now(timezone.utc)
        fact = ClinicalFact(
            fact_id="fact-headache",
            category="symptom",
            value="dor de cabeça",
            subject_id="patient-1",
            encounter_id="encounter-4",
            source="speech",
            provenance={"source": "test"},
            observed_at=now,
        )
        projection = ClinicalKnowledgeLayer().apply(ClinicalFactsBatch(encounter_id="encounter-4", items=(fact,)), source="speech")
        presentation = ClinicalPresentationComposer().compose(
            projection,
            reasoning={
                "hypotheses": [{"id": "hypothesis-migraine", "name": "Migrânea", "confidence": 0.72, "supporting_facts": ["fact-headache"], "missing_facts": ["fotofobia"]}],
                "questions": [{"id": "question-1", "text": "Há fotofobia?", "hypothesis_id": "hypothesis-migraine", "objective": "Completar a avaliação"}],
            },
            soap={
                "subjective": {"narrative": "Paciente relata cefaleia."},
                "objective": {},
                "assessment": {},
                "plan": {},
            },
        )
        object_types = {item.object_type for item in presentation.objects}
        self.assertTrue({"clinical_problem", "clinical_hypothesis", "clinical_question", "clinical_summary", "soap_progress"}.issubset(object_types))
        operations = ClinicalA2UIProjector().project(presentation)
        self.assertGreater(len(operations), 1)
        self.assertEqual(operations[0]["op"], "state")
        self.assertEqual(len(operations[0]["state"]["hypotheses"]), 1)
        self.assertEqual(len(operations[0]["state"]["pending_questions"]), 1)
        self.assertTrue(any(item["op"] == "create" and item["component"] == "SOAPProgressCard" for item in operations))

        problem = next(item for item in presentation.objects if item.object_type == "clinical_problem")
        hypothesis = next(item for item in presentation.objects if item.object_type == "clinical_hypothesis")
        question = next(item for item in presentation.objects if item.object_type == "clinical_question")
        self.assertTrue(problem.evidence)
        self.assertEqual(hypothesis.evidence, ())
        self.assertEqual(hypothesis.parent_object_id, problem.object_id)
        self.assertEqual(question.parent_object_id, problem.object_id)
        self.assertIn("Hipótese em construção", {entry["title"] for entry in presentation.timeline})
        self.assertIn("Pergunta sugerida", {entry["title"] for entry in presentation.timeline})


if __name__ == "__main__":
    unittest.main()
