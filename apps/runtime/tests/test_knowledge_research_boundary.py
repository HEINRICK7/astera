"""Boundary contracts for the Knowledge & Research inventory milestone."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass
import ast
from pathlib import Path
import unittest

from apps.runtime.src.ports.outbound.knowledge import (
    ClinicalQuestion,
    KnowledgeConcept,
    KnowledgeLookupQuery,
    KnowledgePort,
    KnowledgeResult,
    ResearchFinding,
    ResearchPort,
    ResearchResult,
)
from apps.runtime.src.ports.outbound.clinical_semantics import (
    ClinicalContextResult,
    ClinicalContextPort,
    ClinicalContextBuilderPort,
    TerminologyPort,
)
from packages.clinical_context_sdk import ClinicalContext
from packages.contracts.transcription import TranscriptSegment
from packages.evidence_sdk import EvidenceItem
from packages.terminology_sdk import TerminologyConcept, TerminologyQuery, TerminologyResult


class KnowledgeResearchBoundaryTests(unittest.TestCase):
    def test_ports_are_provider_neutral_runtime_checkable_protocols(self) -> None:
        self.assertTrue(getattr(KnowledgePort, "_is_runtime_protocol", False))
        self.assertTrue(getattr(ResearchPort, "_is_runtime_protocol", False))
        self.assertTrue(getattr(TerminologyPort, "_is_runtime_protocol", False))
        self.assertTrue(getattr(ClinicalContextPort, "_is_runtime_protocol", False))
        self.assertTrue(getattr(ClinicalContextBuilderPort, "_is_runtime_protocol", False))

    def test_terminology_result_and_context_are_immutable_contracts(self) -> None:
        terminology = TerminologyResult(
            query=TerminologyQuery(system="SNOMED-CT", text="losartana"),
            provider="deterministic",
            concepts=(TerminologyConcept("SNOMED-CT", "123", "Losartana"),),
        )
        with self.assertRaises(FrozenInstanceError):
            terminology.provider = "medcat"

        context = ClinicalContext(
            context_id="context-1",
            context_version=1,
            patient_id="patient-1",
            encounter_id="encounter-1",
        )
        with self.assertRaises(FrozenInstanceError):
            context.status = "rewritten"

        assertion_context = ClinicalContextResult(
            negated=True,
            certainty="possible",
            provenance={"provider": "baseline"},
        )
        with self.assertRaises(FrozenInstanceError):
            assertion_context.negated = False
        with self.assertRaises(TypeError):
            assertion_context.provenance["provider"] = "changed"

    def test_knowledge_result_is_derived_and_immutable(self) -> None:
        result = KnowledgeResult(
            query=KnowledgeLookupQuery("losartana", context={"language": "pt-BR"}),
            provider="deterministic-placeholder",
            concepts=(KnowledgeConcept("rxnorm:losartan", "Losartana", "medication"),),
            provenance={"source": "boundary-test"},
        )
        with self.assertRaises(FrozenInstanceError):
            result.provider = "vendor"
        with self.assertRaises(TypeError):
            result.provenance["source"] = "changed"

    def test_research_result_is_derived_and_immutable(self) -> None:
        result = ResearchResult(
            result_id="research-1",
            question=ClinicalQuestion("Qual a evidência para este achado?"),
            provider="local-placeholder",
            findings=(ResearchFinding("finding-1", "Fonte", "Resumo"),),
            provenance={"source": "boundary-test"},
        )
        with self.assertRaises(FrozenInstanceError):
            result.result_id = "changed"
        with self.assertRaises(TypeError):
            result.provenance["source"] = "changed"

    def test_canonical_evidence_contracts_remain_frozen_values(self) -> None:
        segment = TranscriptSegment("segment-1", "texto original", 0, 100)
        evidence = EvidenceItem("evidence-1", "encounter-1", "transcript", "texto original", "segment-1")
        self.assertTrue(is_dataclass(segment))
        with self.assertRaises(FrozenInstanceError):
            segment.segment_id = "changed"
        self.assertTrue(is_dataclass(evidence))
        with self.assertRaises(FrozenInstanceError):
            evidence.content = "changed"

    def test_normalization_has_no_provider_or_vendor_dependency(self) -> None:
        path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "application"
            / "clinical"
            / "normalization.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        forbidden = {"medcat", "quickumls", "medspacy", "httpx", "requests"}
        self.assertFalse(
            any(name.casefold() in {item.casefold() for item in imported} for name in forbidden)
        )


if __name__ == "__main__":
    unittest.main()
