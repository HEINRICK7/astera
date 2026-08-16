from __future__ import annotations

import unittest

from apps.runtime.src.application.clinical.mention_registry import MentionRegistry
from packages.clinical_facts_sdk import ClinicalMention


class MentionRegistryTests(unittest.TestCase):
    def test_repeated_stream_observations_share_one_stable_identity(self):
        registry = MentionRegistry()
        first = ClinicalMention(
            id="segment-1-mention",
            original_text="dor de cabeça",
            normalized_text="Dor de cabeça",
            concept_id="headache",
            semantic_type="symptom",
            confidence=0.82,
            negated=False,
            temporality="current",
            speaker="patient",
            provenance={"segment_id": "segment-1"},
            segment_id="segment-1",
            code="SNOMED:25064002",
        )
        second = ClinicalMention(
            id="segment-2-mention",
            original_text="cefaleia",
            normalized_text="Dor de cabeça",
            concept_id="headache",
            semantic_type="symptom",
            confidence=0.91,
            negated=False,
            temporality="current",
            speaker="patient",
            provenance={"segment_id": "segment-2"},
            segment_id="segment-2",
            code="SNOMED:25064002",
        )

        created = registry.upsert(first, encounter_id="encounter-1", subject_id="patient-1")
        growing = registry.upsert(second, encounter_id="encounter-1", subject_id="patient-1")

        self.assertEqual(created.lifecycle, "created")
        self.assertEqual(growing.lifecycle, "growing")
        self.assertEqual(created.mention.id, growing.mention.id)
        self.assertEqual(growing.mention.confidence, 0.91)
        self.assertEqual(len(registry.mentions), 1)
        self.assertEqual(growing.update_count, 2)


if __name__ == "__main__":
    unittest.main()
