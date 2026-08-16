from __future__ import annotations

import unittest

from apps.runtime.src.application.clinical.normalization import (
    ClinicalNormalizationLayer,
    ClinicalNormalizationPort,
)
from apps.runtime.src.application.clinical.transcript_state import ClinicalTranscriptState
from packages.contracts.transcription import TranscriptSegment


class ClinicalNormalizationSprint002Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.layer = ClinicalNormalizationLayer()

    def test_layer_implements_explicit_port_and_does_not_deduplicate_occurrences(self) -> None:
        self.assertIsInstance(self.layer, ClinicalNormalizationPort)

        result = self.layer.normalize(
            "pressão alta e pressão alta",
            metadata={"session_id": "session-1", "segment_id": "segment-1"},
        )

        self.assertEqual(len(result.mentions), 2)
        self.assertNotEqual(result.mentions[0].mention_id, result.mentions[1].mention_id)

    def test_state_input_keeps_mention_id_across_segment_revisions(self) -> None:
        state = ClinicalTranscriptState(session_id="session-2", language="pt-BR")
        state.started()
        state.apply(TranscriptSegment(
            text="press",
            start_ms=0,
            end_ms=300,
            segment_id="segment-15",
            revision=0,
            speaker="patient",
        ), is_final=False)
        partial = self.layer.normalize_state(state, metadata={"trace_id": "trace-2"})
        self.assertEqual(partial.mentions, ())

        state.apply(TranscriptSegment(
            text="pressão alta",
            start_ms=0,
            end_ms=700,
            segment_id="segment-15",
            revision=1,
            speaker="patient",
        ), is_final=False)
        revised = self.layer.normalize_state(state, metadata={"trace_id": "trace-2"})
        self.assertEqual(len(revised.mentions), 1)
        mention_id = revised.mentions[0].mention_id
        self.assertEqual(revised.mentions[0].status, "REVISED")
        self.assertEqual(revised.mentions[0].revision, 1)

        state.apply(TranscriptSegment(
            text="pressão alta",
            start_ms=0,
            end_ms=700,
            segment_id="segment-15",
            revision=2,
            speaker="patient",
        ), is_final=True)
        final = self.layer.normalize_state(state, metadata={"trace_id": "trace-2"})
        self.assertEqual(final.mentions[0].mention_id, mention_id)
        self.assertEqual(final.mentions[0].status, "FINAL")
        self.assertEqual(final.mentions[0].revision, 2)

    def test_semantic_assertion_fields_and_rich_provenance_are_preserved(self) -> None:
        result = self.layer.normalize(
            "Acho que tenho pressão alta, não tenho diabetes, tive pneumonia quando criança e uso remédio da pressão.",
            metadata={
                "session_id": "session-3",
                "segment_id": "segment-3",
                "revision": 4,
                "provider": "xai-stt",
                "trace_id": "trace-3",
                "speaker": "patient",
                "received_at": "2026-08-11T12:00:00Z",
                "processed_at": "2026-08-11T12:00:01Z",
            },
        )
        by_concept = {mention.concept_id: mention for mention in result.mentions}

        self.assertEqual(by_concept["condition.hypertension"].certainty, "possible")
        self.assertTrue(by_concept["condition.diabetes"].negated)
        self.assertEqual(by_concept["condition.pneumonia"].temporality, "past")
        self.assertEqual(by_concept["medication.unspecified"].status, "FINAL")
        self.assertTrue(by_concept["medication.unspecified"].review_required)

        payload = by_concept["condition.hypertension"].to_dict()
        self.assertIn("mention_id", payload)
        self.assertEqual(payload["mention_id"], payload["id"])
        self.assertEqual(payload["updated_at"], by_concept["condition.hypertension"].updated_at.isoformat())
        provenance = payload["provenance"]
        for field in (
            "trace_id",
            "session_id",
            "segment_id",
            "segment_revision",
            "provider",
            "speaker",
            "offset_start",
            "offset_end",
            "received_at",
            "processed_at",
            "source_text",
            "normalized_by",
        ):
            self.assertIn(field, provenance)


if __name__ == "__main__":
    unittest.main()
