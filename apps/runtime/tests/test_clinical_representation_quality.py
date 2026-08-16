from __future__ import annotations

import base64
import json
import unittest

from packages.clinical_facts_sdk import DeterministicClinicalFactsExtractor
from packages.fhir_sdk import FhirResource, InMemoryFhirGateway
from packages.medical_nlp_sdk import ClinicalEntity, NlpResult
from packages.representation_sdk import KnowledgeRepresentationEngine, RepresentationRequest
from packages.contracts.transcription import Transcript, TranscriptNormalizer, TranscriptSegment


class ClinicalRepresentationQualityTests(unittest.IsolatedAsyncioTestCase):
    def test_transcript_normalizer_keeps_raw_asr_evidence(self) -> None:
        transcript = Transcript(
            request_id="audio-golden-001",
            language="pt-BR",
            provider="test-speech",
            segments=(TranscriptSegment("segment-1", "cansácio e loss artana de 50mg", 0, 1000),),
        )

        normalized = TranscriptNormalizer().normalize(transcript)
        self.assertEqual(normalized.text, "cansaço e losartana de 50 mg")
        self.assertEqual(normalized.raw_text, "cansácio e loss artana de 50mg")
        self.assertEqual(normalized.to_dict()["segments"][0]["raw_text"], "cansácio e loss artana de 50mg")

    async def test_golden_asr_variants_are_normalized_with_raw_provenance(self) -> None:
        result = NlpResult(
            request_id="audio-golden-001",
            provider="test-nlp",
            entities=(
                ClinicalEntity("cansácio", "Symptom", 0, 8),
                ClinicalEntity("na Áusia", "Symptom", 9, 17),
                ClinicalEntity("não vou me ter", "Symptom", 18, 33, negated=True),
                ClinicalEntity("loss artana de 50mg", "Medication", 34, 55),
                ClinicalEntity("alergia a algum medicamento", "Allergy", 56, 85, negated=True),
                ClinicalEntity("Não que eu saiba", "Allergy", 86, 102, negated=True),
            ),
        )

        batch = await DeterministicClinicalFactsExtractor().extract(
            encounter_id="encounter-1",
            subject_id="patient-1",
            patient_id="patient-1",
            result=result,
        )

        facts = {(item.category, item.value, item.polarity): item for item in batch.items}
        self.assertIn(("Fatigue", "cansaço", "positive"), facts)
        self.assertIn(("Nausea", "náusea", "positive"), facts)
        self.assertIn(("Vomiting", "vômito", "negative"), facts)
        self.assertIn(("Medication", "losartana de 50 mg", "positive"), facts)
        self.assertIn(("Allergy", "alergia medicamentosa conhecida", "negative"), facts)
        self.assertEqual(len([item for item in batch.items if item.category == "Allergy"]), 1)
        self.assertEqual(facts[("Fatigue", "cansaço", "positive")].provenance["raw_value"], "cansácio")

    async def test_soap_is_structured_and_fhir_attachment_is_valid(self) -> None:
        facts = (
            {
                "id": "fact-1",
                "category": "Symptom",
                "value": "muita dor de cabeça",
                "polarity": "positive",
                "certainty": "reported",
                "provenance": {"source_ref": "audio-1:0-12"},
            },
            {
                "id": "fact-2",
                "category": "Medication",
                "value": "losartana 50 mg",
                "polarity": "positive",
                "certainty": "reported",
                "provenance": {"source_ref": "audio-1:20-35"},
            },
        )
        request = RepresentationRequest(
            record_id="context-1",
            encounter_id="encounter-1",
            version="1",
            statements=tuple(item["value"] for item in facts),
            formats=("soap", "fhir"),
            context_id="context-1",
            context_version=1,
            patient_id="patient-1",
            facts=facts,
            transcript={"language": "pt-BR", "text": "consulta"},
        )

        result = await KnowledgeRepresentationEngine().render(request)
        by_format = {item.format: item.content for item in result.representations}
        self.assertEqual(by_format["soap"]["subjective"]["chief_complaint"], "muita dor de cabeça")
        self.assertEqual(by_format["soap"]["status"], "draft")

        fhir = by_format["fhir"]
        attachment = fhir["content"][0]["attachment"]
        self.assertIsInstance(attachment["data"], str)
        decoded = json.loads(base64.b64decode(attachment["data"]))
        self.assertEqual(decoded["subjective"]["chief_complaint"], "muita dor de cabeça")

        errors = await InMemoryFhirGateway().validate(
            FhirResource(resource_type="DocumentReference", resource_id="context-1", data=fhir)
        )
        self.assertEqual(errors, ())
