"""Low-latency clinical candidate extraction for live consultation windows."""
from __future__ import annotations

import re

from packages.medical_nlp_sdk import ClinicalEntity, NlpRequest, NlpResult


class KeywordClinicalNlp:
    """Extract only phrases literally present in the received transcript.

    This is a fast candidate stage for live UI latency. It does not diagnose,
    infer synonyms or create facts absent from the speech. The full cognitive
    provider remains responsible for richer asynchronous processing.
    """

    provider = "local-clinical-candidates"

    _patterns = (
        ("dor de cabeça", "Symptom"),
        ("dor no peito", "Symptom"),
        ("falta de ar", "Symptom"),
        ("dor abdominal", "Symptom"),
        ("dor nas costas", "Symptom"),
        ("febre", "Symptom"),
        ("náusea", "Symptom"),
        ("náuseas", "Symptom"),
        ("vômito", "Symptom"),
        ("tosse", "Symptom"),
        ("tontura", "Symptom"),
        ("diabetes", "Condition"),
        ("hipertensão", "Condition"),
        ("alergia", "Allergy"),
        ("losartana", "Medication"),
    )

    async def process(self, request: NlpRequest) -> NlpResult:
        entities: list[ClinicalEntity] = []
        for phrase, label in self._patterns:
            for match in re.finditer(re.escape(phrase), request.text, flags=re.IGNORECASE):
                prefix = request.text[max(0, match.start() - 28):match.start()].casefold()
                negated = bool(re.search(r"\b(?:não|nao)\b", prefix))
                entities.append(
                    ClinicalEntity(
                        text=match.group(0),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        negated=negated,
                        assertion="negative" if negated else "present",
                    )
                )

        for match in re.finditer(r"\b(?:há|ha)\s+\d+\s+(?:dia|dias|hora|horas|semana|semanas)\b", request.text, flags=re.IGNORECASE):
            entities.append(
                ClinicalEntity(
                    text=match.group(0),
                    label="Duration",
                    start=match.start(),
                    end=match.end(),
                )
            )
        for match in re.finditer(r"\b(?:\d{1,2}\s*/\s*10|dez|nove|oito|sete|seis|cinco)\b", request.text, flags=re.IGNORECASE):
            entities.append(
                ClinicalEntity(
                    text=match.group(0),
                    label="Severity",
                    start=match.start(),
                    end=match.end(),
                )
            )

        entities.sort(key=lambda entity: (entity.start, entity.end, entity.label))
        return NlpResult(
            request_id=request.request_id,
            provider=self.provider,
            entities=tuple(entities),
            language=request.language,
        )
