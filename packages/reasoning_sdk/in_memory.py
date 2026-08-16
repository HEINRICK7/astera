"""Deterministic reasoning adapter for contract and integration tests."""
from __future__ import annotations

import hashlib

from packages.clinical_context_sdk import ClinicalContext

from .models import ClinicalHypothesis, ClinicalQuestion, ClinicalReasoningResult, InformationGap


class DeterministicClinicalReasoner:
    """Exercise the CRL contract without an LLM or a clinical claim engine."""

    async def reason(self, context: ClinicalContext) -> ClinicalReasoningResult:
        values = " ".join(fact.value.lower() for fact in context.facts)
        fact_ids = tuple(fact.fact_id for fact in context.facts)
        if "dor" in values and ("peito" in values or "torác" in values):
            templates = (
                ("acute-coronary-syndrome", "Síndrome Coronariana Aguda", 0.62),
                ("stable-angina", "Angina Estável", 0.48),
                ("gastroesophageal-reflux", "Refluxo Gastroesofágico", 0.33),
            )
            missing = ("ECG", "troponina")
        else:
            templates = (("clinical-pattern-review", "Revisão do padrão clínico", 0.25),)
            missing = ()

        hypotheses = tuple(
            ClinicalHypothesis(
                hypothesis_id=f"hypothesis-{hypothesis_id}",
                name=name,
                confidence=confidence,
                supporting_facts=fact_ids,
                missing_facts=missing,
                status="candidate",
                provenance={
                    "reasoner": "deterministic",
                    "context_id": context.context_id,
                    "context_version": context.context_version,
                },
            )
            for hypothesis_id, name, confidence in templates
        )
        gaps = tuple(
            InformationGap(
                gap_id=self._id("gap", hypothesis.hypothesis_id, missing_fact),
                hypothesis_id=hypothesis.hypothesis_id,
                missing_fact_type=missing_fact,
                importance="high" if missing_fact in {"ECG", "troponina"} else "medium",
                question=self._question(missing_fact),
                acquisition_method="clinical_question_or_record",
                provenance={"reasoner": "deterministic"},
            )
            for hypothesis in hypotheses
            for missing_fact in hypothesis.missing_facts
        )
        questions = tuple(
            ClinicalQuestion(
                question_id=self._id("question", gap.gap_id),
                text=gap.question,
                gap_id=gap.gap_id,
                hypothesis_id=gap.hypothesis_id,
                objective=f"Obter o fact ausente: {gap.missing_fact_type}",
            )
            for gap in gaps
        )
        return ClinicalReasoningResult(
            encounter_id=context.encounter_id,
            context_id=context.context_id,
            context_version=context.context_version,
            hypotheses=hypotheses,
            information_gaps=gaps,
            questions=questions,
        )

    @staticmethod
    def _id(prefix: str, *parts: str) -> str:
        digest = hashlib.sha256(":".join(parts).encode()).hexdigest()[:16]
        return f"{prefix}-{digest}"

    @staticmethod
    def _question(missing_fact: str) -> str:
        questions = {
            "ECG": "Foi realizado um ECG e qual foi o resultado?",
            "troponina": "Foi realizada troponina e qual foi o resultado?",
        }
        return questions.get(missing_fact, f"É possível obter o dado {missing_fact}?")
