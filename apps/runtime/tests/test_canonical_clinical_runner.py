from __future__ import annotations

import unittest

from apps.runtime.src.adapters.cognitive import KeywordClinicalNlp
from apps.runtime.src.adapters.transcription import ExternalTranscriptionAdapter
from apps.runtime.src.adapters.streaming import InMemoryStreamBrokerAdapter
from apps.runtime.src.adapters.persistence import InMemoryClinicalReviewStore
from apps.runtime.src.application.clinical.live_stream import LiveClinicalPipeline
from packages.clinical_context_sdk import DeterministicClinicalContextBuilder
from packages.clinical_facts_sdk import DeterministicClinicalFactsExtractor
from packages.reasoning_sdk import DeterministicClinicalReasoner
from packages.representation_sdk import KnowledgeRepresentationEngine


class CanonicalClinicalRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_runner_accepts_canonical_events_without_speech_engine(self) -> None:
        adapter = ExternalTranscriptionAdapter()
        payloads = (
            {
                "type": "transcript.partial",
                "session_id": "encounter-canonical",
                "segment_id": "segment-1",
                "revision": 0,
                "text": "estou com dor de cabeça",
                "start_ms": 0,
                "end_ms": 900,
                "language": "pt-BR",
                "provider": "external-test",
            },
            {
                "type": "transcript.committed",
                "session_id": "encounter-canonical",
                "segment_id": "segment-1",
                "revision": 1,
                "text": "estou com dor de cabeça há 5 dias",
                "start_ms": 0,
                "end_ms": 1200,
                "language": "pt-BR",
                "provider": "external-test",
            },
        )

        async def events():
            for payload in payloads:
                event = adapter.to_contract(payload)
                assert event is not None
                yield event

        pipeline = LiveClinicalPipeline(
            broker=InMemoryStreamBrokerAdapter(),
            nlp_processor=KeywordClinicalNlp(),
            facts_extractor=DeterministicClinicalFactsExtractor(),
            context_builder=DeterministicClinicalContextBuilder(),
            reasoner=DeterministicClinicalReasoner(),
            representation_engine=KnowledgeRepresentationEngine(),
            review_store=InMemoryClinicalReviewStore(),
        )

        await pipeline.run_canonical_events(
            stream_id="encounter-canonical",
            encounter_id="encounter-canonical",
            patient_id="patient-1",
            language="pt-BR",
            events=events(),
        )

        review = pipeline.review_store.get("encounter-canonical")
        self.assertIsNotNone(review)
        self.assertEqual(review["transcript"]["final_segments"][0]["id"], "segment-1")
        self.assertIn("Dor de cabeça", {item["value"] for item in review["clinical_facts"]["items"]})
