from __future__ import annotations

import asyncio
import unittest

from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer
from packages.clinical_facts_sdk import DeterministicClinicalFactsExtractor


class ClinicalNormalizationLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layer = ClinicalNormalizationLayer()

    def test_synonyms_and_phonetic_variants_share_canonical_concepts(self) -> None:
        result = self.layer.normalize(
            "Tenho pressão alta, sou hipertenso e tomo losartana. Também estou vomitando sangue e com falta de ar.",
            metadata={"request_id": "normalization-1", "segment_id": "segment-1", "speaker": "patient"},
        )

        self.assertEqual(
            {mention.normalized_text for mention in result.mentions},
            {"Hipertensão", "Losartana", "Hematêmese", "Dispneia"},
        )
        self.assertTrue(all(mention.original_text for mention in result.mentions))
        self.assertTrue(all(mention.provenance["source"] == "clinical_normalization_layer" for mention in result.mentions))

        phonetic = self.layer.normalize("O paciente teve ematemese.", metadata={"request_id": "normalization-2"})
        self.assertEqual([item.normalized_text for item in phonetic.mentions], ["Hematêmese"])
        self.assertTrue(phonetic.mentions[0].review_required)

    def test_abbreviations_negation_temporality_and_speaker_are_preserved(self) -> None:
        result = self.layer.normalize(
            "HAS e DM no prontuário. Já tive AVC. Não fuma.",
            metadata={"request_id": "normalization-3", "speaker": "patient", "segment_id": "segment-3", "revision": 2},
        )

        by_text = {mention.normalized_text: mention for mention in result.mentions}
        self.assertEqual(by_text["Hipertensão"].original_text, "HAS")
        self.assertEqual(by_text["Diabetes Mellitus"].original_text, "DM")
        self.assertEqual(by_text["AVC"].temporality, "past")
        self.assertTrue(by_text["Tabagismo"].negated)
        self.assertFalse(by_text["Tabagismo"].reported)
        self.assertEqual(by_text["Tabagismo"].speaker, "patient")
        self.assertEqual(by_text["Hipertensão"].revision, 2)

    def test_mentions_are_accepted_by_the_existing_fact_boundary(self) -> None:
        result = self.layer.normalize("Dor no peito e pressão vive alta.", metadata={"request_id": "normalization-4"})
        batch = asyncio.run(
            DeterministicClinicalFactsExtractor().extract(
                encounter_id="encounter-normalization",
                subject_id="patient-normalization",
                patient_id="patient-normalization",
                mentions=result.mentions,
            )
        )

        self.assertEqual(
            {fact.value for fact in batch.items},
            {"Dor torácica", "Hipertensão"},
        )
        self.assertTrue(all(fact.source == "clinical_normalization" for fact in batch.items))

    def test_required_clinical_vocabulary_is_normalized(self) -> None:
        cases = {
            "hipertenso": "Hipertensão",
            "losartana": "Losartana",
            "hematêmese": "Hematêmese",
            "vomitando sangue": "Hematêmese",
            "dor torácica": "Dor torácica",
            "dor no peito": "Dor torácica",
            "falta de ar": "Dispneia",
            "dispneia": "Dispneia",
            "HAS": "Hipertensão",
            "DM": "Diabetes Mellitus",
            "HDA": "Hemorragia Digestiva Alta",
        }

        for phrase, expected in cases.items():
            with self.subTest(phrase=phrase):
                result = self.layer.normalize(phrase)
                self.assertEqual([mention.normalized_text for mention in result.mentions], [expected])

    def test_duration_is_semantic_and_mentions_have_stable_ontology_identity(self) -> None:
        result = self.layer.normalize("Dor de cabeça há cinco dias")
        headache = next(item for item in result.mentions if item.concept_id == "symptom.headache")
        duration = next(item for item in result.mentions if item.concept_id == "clinical.duration")

        self.assertEqual((headache.ontology, headache.code), ("ASTERA-CONCEPT", "symptom.headache"))
        self.assertEqual(duration.semantic_type, "temporal")
        self.assertEqual((duration.semantic_value, duration.semantic_unit), (5, "dias"))


if __name__ == "__main__":
    unittest.main()
