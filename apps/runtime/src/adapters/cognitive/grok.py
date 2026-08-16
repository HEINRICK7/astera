"""Grok adapter for structured clinical extraction and reasoning."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

import httpx

from packages.clinical_context_sdk import ClinicalContext
from packages.reasoning_sdk import (
    ClinicalHypothesis,
    ClinicalQuestion,
    ClinicalReasoningResult,
    InformationGap,
)


class GrokProviderError(RuntimeError):
    """Raised when Grok cannot return a valid provider-neutral result."""


class GrokClient:
    def __init__(self, *, api_key: str | None, base_url: str, model: str, timeout_seconds: float) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("ASTERA_XAI_API_KEY is required when cognitive_provider=grok")
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema_name: str,
        schema: Mapping[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "model": self._model,
            "temperature": 0,
            "reasoning_effort": "low",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "strict": True, "schema": schema},
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
            content = body["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("Grok response must be a JSON object")
            return result
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GrokProviderError("Grok did not return a valid structured clinical response") from exc


class GrokClinicalReasoner:
    provider = "grok"

    def __init__(self, client: GrokClient) -> None:
        self._client = client

    async def reason(self, context: ClinicalContext) -> ClinicalReasoningResult:
        result = await self._client.complete_json(
            system=(
                "Você é um reasoner clínico assistivo. Gere hipóteses candidatas, nunca diagnóstico final. "
                "Use apenas os fatos fornecidos, indique lacunas e perguntas verificáveis."
            ),
            user=json.dumps(context.to_dict(), ensure_ascii=False),
            schema_name="clinical_reasoning",
            schema={
                "type": "object", "additionalProperties": False,
                "properties": {
                    "hypotheses": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
                        "id": {"type": "string"}, "name": {"type": "string"}, "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "supporting_facts": {"type": "array", "items": {"type": "string"}}, "missing_facts": {"type": "array", "items": {"type": "string"}},
                        "conflicting_facts": {"type": "array", "items": {"type": "string"}}, "status": {"type": "string"},
                    }, "required": ["id", "name", "confidence", "supporting_facts", "missing_facts", "conflicting_facts", "status"]}},
                    "information_gaps": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
                        "id": {"type": "string"}, "hypothesis_id": {"type": "string"}, "missing_fact_type": {"type": "string"}, "importance": {"type": "string"},
                        "question": {"type": "string"}, "acquisition_method": {"type": "string"},
                    }, "required": ["id", "hypothesis_id", "missing_fact_type", "importance", "question", "acquisition_method"]}},
                },
                "required": ["hypotheses", "information_gaps"],
            },
        )
        raw_hypotheses = result.get("hypotheses", [])
        hypothesis_ids: dict[str, str] = {}
        hypotheses: list[ClinicalHypothesis] = []
        for item in raw_hypotheses:
            raw_id = str(item["id"])
            hypothesis_id = self._stable_id("hypothesis", context.context_id, raw_id)
            hypothesis_ids[raw_id] = hypothesis_id
            hypotheses.append(ClinicalHypothesis(
                hypothesis_id=hypothesis_id,
                name=str(item["name"]),
                confidence=float(item["confidence"]),
                supporting_facts=tuple(str(value) for value in item["supporting_facts"]),
                missing_facts=tuple(str(value) for value in item["missing_facts"]),
                conflicting_facts=tuple(str(value) for value in item["conflicting_facts"]),
                status=str(item["status"]),
                provenance={"reasoner": self.provider, "context_id": context.context_id},
            ))
        gaps: list[InformationGap] = []
        questions: list[ClinicalQuestion] = []
        for item in result.get("information_gaps", []):
            gap_id = self._stable_id("gap", context.context_id, str(item["id"]))
            hypothesis_id = hypothesis_ids.get(str(item["hypothesis_id"]), str(item["hypothesis_id"]))
            questions.append(ClinicalQuestion(
                question_id=self._stable_id("question", gap_id), text=str(item["question"]), gap_id=gap_id,
                hypothesis_id=hypothesis_id, objective=f"Obter o fact ausente: {item['missing_fact_type']}",
            ))
            gaps.append(InformationGap(
                gap_id=gap_id, hypothesis_id=hypothesis_id, missing_fact_type=str(item["missing_fact_type"]),
                importance=str(item["importance"]), question=str(item["question"]),
                acquisition_method=str(item["acquisition_method"]), provenance={"reasoner": self.provider},
            ))
        return ClinicalReasoningResult(
            encounter_id=context.encounter_id, context_id=context.context_id, context_version=context.context_version,
            hypotheses=tuple(hypotheses), information_gaps=tuple(gaps), questions=tuple(questions),
        )

    @staticmethod
    def _stable_id(prefix: str, *parts: str) -> str:
        digest = hashlib.sha256(":".join(parts).encode()).hexdigest()[:16]
        return f"{prefix}-{digest}"
